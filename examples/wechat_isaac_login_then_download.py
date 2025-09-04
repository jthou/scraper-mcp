#!/usr/bin/env python3
"""
微信：先登录/验证，检测登录成功后，再只搜索“Isaac Sim”并逐篇下载（无限等待验证）。
"""

import asyncio
import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform


async def wait_until_logged_in(toolkit: ScraperToolkit):
    """无限等待，直到验证码完成并进入正常搜索结果页；不触发任何下载或搜索。"""
    print('等待你在浏览器中完成登录/验证码（无限等待），完成后我才会继续...')
    page = toolkit.wechat_scraper.page
    # 仅打开搜索页，不开始提取
    await page.goto('https://weixin.sogou.com/weixin?type=2&query=Isaac%20Sim')
    await page.wait_for_load_state('networkidle')

    # 循环探测是否还在验证码/反爬页面；若是则调用无限等待
    while True:
        captcha = await toolkit.wechat_scraper._check_captcha()
        if captcha.get('has_captcha'):
            print('检测到验证码页，开始无限等待，完成后自动继续...')
            _ = await toolkit.wechat_scraper.wait_for_manual_verification(timeout=None)
            print('检测到验证完成，继续探测...')
        else:
            # 简单检查是否出现搜索结果容器
            try:
                box = await page.query_selector('.news-box, .news-list, .results')
                if box:
                    break
            except Exception:
                pass
            await page.wait_for_timeout(1000)

    # 自动继续（取消交互式 input）
    print('检测到搜索结果已可见，自动继续执行...')


def load_downloaded_urls(out_dir: Path):
    """从 file_mapping.json 读取已下载URL集合，用于跳过。"""
    mapping_file = out_dir / 'file_mapping.json'
    urls = set()
    if mapping_file.exists():
        try:
            data = json.loads(mapping_file.read_text(encoding='utf-8'))
            for _, v in (data or {}).items():
                u = v.get('url')
                if u:
                    urls.add(u)
        except Exception:
            pass
    return urls


async def run():
    # 指定输出目录：使用 p10 目录以便复用已有下载
    out_dir = Path('data/wechat_isaac_p10')
    out_dir.mkdir(parents=True, exist_ok=True)

    tk = ScraperToolkit(ScrapingConfig(
        platform=Platform.WECHAT,
        headless=False,
        max_pages=0,
        output_dir=out_dir,
        wait_for_verification=True,
    ))
    try:
        print('1) 设置浏览器...')
        await tk.setup_browser(Platform.WECHAT)

        print('2) 等待登录/验证成功...')
        await wait_until_logged_in(tk)

        print('3) 仅搜索 "Isaac Sim"（前9页）...')
        res = await tk.search(Platform.WECHAT, 'Isaac Sim', max_pages=9)
        links = res.get('all_links') or [i.get('link') for i in (res.get('results') or []) if i.get('link')]
        links = [l for l in links if l]
        print(f'   获得 {len(links)} 篇文章链接（不去重，按顺序下载）')

        # 读取已下载URL集合（基于 file_mapping.json）
        downloaded_urls = load_downloaded_urls(out_dir)
        if downloaded_urls:
            print(f'   发现已下载 {len(downloaded_urls)} 篇（基于 file_mapping.json），将自动跳过匹配链接')

        print('4) 逐篇下载，遇验证码继续等待...')
        ok = 0
        fail = 0
        for i, link in enumerate(links, 1):
            # 基于已记录URL跳过（注意：若历史是 mp.weixin 链接而当前是搜狗跳转链接，可能无法完全匹配；此处做最小可行跳过）
            if link in downloaded_urls:
                print(f'  [{i}/{len(links)}] 跳过（已下载记录匹配）: {link}')
                continue

            print(f'  [{i}/{len(links)}] 下载: {link}')
            r = await tk.download_content(Platform.WECHAT, link, out_dir)
            if r.get('status') == 'success':
                files = r.get('files', {})
                print('     ✅ 成功')
                print(f"       PDF: {files.get('pdf')}")
                print(f"       MD : {files.get('markdown')}")
                ok += 1
            else:
                print(f"     ❌ 失败: {r.get('message')}")
                fail += 1

        print('\n完成：')
        print(f'  成功: {ok} 失败: {fail} 总计: {len(links)}')

    finally:
        await tk.cleanup()


if __name__ == '__main__':
    asyncio.run(run())



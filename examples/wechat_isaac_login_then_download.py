#!/usr/bin/env python3
"""
微信：先登录/验证，检测登录成功后，再只搜索“Isaac Sim”并逐篇下载（无限等待验证）。
"""

import asyncio
import sys
from pathlib import Path

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

    # 双重保险：由用户手动确认
    input('请确认已完成登录/验证且能正常看到搜索结果后，按回车继续... ')


async def run():
    out_dir = Path('data/wechat_isaac_login')
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

        print('3) 仅搜索 "Isaac Sim"（全量）...')
        res = await tk.search(Platform.WECHAT, 'Isaac Sim', max_pages=0)
        links = res.get('all_links') or [i.get('link') for i in (res.get('results') or []) if i.get('link')]
        links = [l for l in links if l]
        print(f'   获得 {len(links)} 篇文章链接（不去重，按顺序下载）')

        print('4) 逐篇下载，遇验证码继续等待...')
        ok = 0
        fail = 0
        for i, link in enumerate(links, 1):
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



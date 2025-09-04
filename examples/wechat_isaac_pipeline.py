#!/usr/bin/env python3
"""
微信 Isaac Sim 全量抓取流水线（断点续跑）

功能：
- 多关键词全量搜索 → 合并去重 → 串行逐个下载
- 断点续跑：links.json 保存链接、state.json 保存进度（completed/failed/index）
- 下载过程中如遇验证码，等待人工验证完成后继续

运行：
  python examples/wechat_isaac_pipeline.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform


QUERIES: List[str] = [
    'Isaac Sim',
    'NVIDIA Isaac Sim',
    '英伟达 Isaac Sim',
    'Isaac 仿真',
    '英伟达 仿真 平台 Isaac',
]

OUTPUT_DIR = Path('data/wechat_isaac_all')
LINKS_JSON = OUTPUT_DIR / 'links.json'
STATE_JSON = OUTPUT_DIR / 'state.json'


def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return default
    return default


def save_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


async def collect_all_links(toolkit: ScraperToolkit) -> List[str]:
    print('2) 收集链接（全量，多关键词）...')
    all_links: List[str] = []
    for q in QUERIES:
        print(f'  - 搜索: {q}')
        res = await toolkit.search(Platform.WECHAT, q, max_pages=0)
        links = res.get('all_links') or [item.get('link') for item in (res.get('results') or []) if item.get('link')]
        links = [l for l in links if l]
        print(f'    取得 {len(links)} 条链接')
        all_links.extend(links)
    unique_links = list(dict.fromkeys(all_links))
    print(f'  收集合计 {len(all_links)} 条，去重后 {len(unique_links)} 条')
    return unique_links


async def run_pipeline():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    config = ScrapingConfig(
        platform=Platform.WECHAT,
        headless=False,
        max_pages=0,  # 全部页面
        output_dir=OUTPUT_DIR,
        wait_for_verification=True,
    )
    toolkit = ScraperToolkit(config)

    try:
        print('1) 设置浏览器...')
        await toolkit.setup_browser(Platform.WECHAT)

        # 读取或生成链接清单
        if LINKS_JSON.exists():
            print('2) 发现 links.json，直接读取...')
            links: List[str] = load_json(LINKS_JSON, [])
        else:
            links = await collect_all_links(toolkit)
            save_json(LINKS_JSON, links)
            print(f'  已保存链接清单：{LINKS_JSON}')

        # 读取或初始化状态
        state = load_json(STATE_JSON, {
            'completed': [],
            'failed': [],
            'index': 0,
            'total': len(links),
        })
        print(f"3) 读取进度：index={state.get('index',0)}/{state.get('total',len(links))}, completed={len(state.get('completed',[]))}, failed={len(state.get('failed',[]))}")

        # 串行下载（断点续跑）
        print('4) 串行下载，遇到验证码将等待人工验证...')
        for i in range(state.get('index', 0), len(links)):
            link = links[i]
            if link in state.get('completed', []):
                print(f'  [{i+1}/{len(links)}] 跳过（已完成）: {link}')
                continue

            print(f'  [{i+1}/{len(links)}] 下载: {link}')
            try:
                r = await toolkit.download_content(Platform.WECHAT, link, OUTPUT_DIR)
                if r.get('status') == 'success':
                    files = r.get('files', {})
                    print('     ✅ 成功')
                    print(f"       PDF: {files.get('pdf')}")
                    print(f"       MD : {files.get('markdown')}")
                    state.setdefault('completed', []).append(link)
                else:
                    print(f"     ❌ 失败: {r.get('message')}")
                    state.setdefault('failed', []).append({'link': link, 'message': r.get('message')})
                # 更新索引并保存状态
                state['index'] = i + 1
                save_json(STATE_JSON, state)
            except Exception as e:
                print(f'     💥 异常: {e}')
                state.setdefault('failed', []).append({'link': link, 'error': str(e)})
                state['index'] = i + 1
                save_json(STATE_JSON, state)

        print('\n5) 完成统计：')
        print(f"  成功: {len(state.get('completed', []))}")
        print(f"  失败: {len(state.get('failed', []))}")
        print(f"  总数: {len(links)}")
        print(f"  链接清单: {LINKS_JSON}")
        print(f"  进度文件: {STATE_JSON}")

    finally:
        await toolkit.cleanup()


if __name__ == '__main__':
    asyncio.run(run_pipeline())



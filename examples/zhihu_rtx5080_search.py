#!/usr/bin/env python3
"""
NVIDIA RTX 5080 显卡问题和避坑指南搜索脚本

搜索知乎上关于 NVIDIA RTX 5080 显卡的相关问题和使用注意事项
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

# 输出目录
OUTPUT_DIR = Path('data/rtx5080')
LINKS_JSON = OUTPUT_DIR / 'links.json'
STATE_JSON = OUTPUT_DIR / 'state.json'


async def wait_until_zhihu_logged_in(toolkit: ScraperToolkit):
    """等待知乎登录完成"""
    print('等待你在浏览器中完成知乎登录（无限等待），完成后我才会继续...')
    
    # 打开知乎首页
    page = toolkit.web_scraper.zhihu_page
    await page.goto('https://www.zhihu.com')
    await page.wait_for_load_state('networkidle')
    
    # 循环检查登录状态
    while True:
        try:
            # 检查是否在登录页面
            current_url = page.url
            if "login" in current_url.lower() or "signin" in current_url.lower():
                print('检测到登录页面，请完成登录...')
                await page.wait_for_timeout(3000)  # 等待3秒
                continue
            
            # 检查是否有登录按钮（未登录状态）
            login_button = await page.query_selector('button:has-text("登录"), .SignFlow-tab, [data-testid*="login"]')
            if login_button:
                print('检测到登录按钮，请完成登录...')
                await page.wait_for_timeout(3000)
                continue
            
            # 检查是否有用户头像或用户名（已登录状态）
            user_avatar = await page.query_selector('.AppHeader-userInfo, .UserAvatar, [data-testid*="user"]')
            if user_avatar:
                print('检测到用户信息，登录成功！')
                break
            
            # 检查是否有搜索框（登录后的页面特征）
            search_box = await page.query_selector('.SearchBar-input, input[placeholder*="搜索"]')
            if search_box:
                print('检测到搜索功能，登录成功！')
                break
                
            print('等待登录完成...')
            await page.wait_for_timeout(2000)  # 等待2秒后再次检查
            
        except Exception as e:
            print(f'检查登录状态时出错: {e}')
            await page.wait_for_timeout(2000)
    
    print('知乎登录检测完成，开始搜索...')


async def collect_all_links(toolkit: ScraperToolkit) -> List[str]:
    """收集所有关于RTX 5080的链接"""
    print('2) 收集关于NVIDIA RTX 5080的相关链接...')
    all_links: List[str] = []
    
    # 搜索关键词
    queries = [
        "NVIDIA RTX 5080 问题",
        "RTX 5080 使用技巧",
        "RTX 5080 避坑",
        "RTX 5080 故障",
        "RTX 5080 兼容性",
        "RTX 5080 性能问题",
        "RTX 5080 游戏问题"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f'  [{i}/{len(queries)}] 搜索: {query}')
        try:
            res = await toolkit.search(Platform.ZHIHU, query, max_pages=3)  # 每个关键词搜索3页
            if res.get('status') == 'success':
                links = res.get('all_links') or [item.get('url') for item in (res.get('results') or []) if item.get('url')]
                links = [l for l in links if l]
                print(f'    取得 {len(links)} 条链接')
                all_links.extend(links)
            else:
                print(f'    搜索失败: {res.get("message", "未知错误")}')
        except Exception as e:
            print(f'    搜索异常: {e}')
        
        # 搜索间隔，避免请求过快
        await asyncio.sleep(2)
    
    # 去重
    unique_links = list(dict.fromkeys(all_links))
    print(f'  收集合计 {len(all_links)} 条，去重后 {len(unique_links)} 条')
    return unique_links


def load_json(path: Path, default):
    """加载JSON文件"""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return default
    return default


def save_json(path: Path, data: Any):
    """保存JSON文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def load_downloaded_urls(output_dir: Path) -> set:
    """从已有的下载文件中提取URL"""
    downloaded = set()
    if output_dir.exists():
        for json_file in output_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding='utf-8'))
                if 'url' in data:
                    downloaded.add(data['url'])
            except Exception:
                pass
    return downloaded


async def run_zhihu_rtx5080_search():
    """运行知乎RTX 5080相关内容搜索和下载"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    config = ScrapingConfig(
        platform=Platform.ZHIHU,
        headless=False,
        max_pages=3,
        output_dir=OUTPUT_DIR,
        wait_for_verification=True,
    )
    toolkit = ScraperToolkit(config)
    
    try:
        print('1) 设置浏览器并登录知乎...')
        # 使用ScraperToolkit的setup_browser方法来正确初始化浏览器
        setup_result = await toolkit.setup_browser(Platform.ZHIHU, headless=False)
        if setup_result["status"] != "success":
            print(f"❌ 浏览器设置失败: {setup_result.get('message', '未知错误')}")
            return
        print("✅ 浏览器设置成功")
        
        print('2) 等待知乎登录完成...')
        await wait_until_zhihu_logged_in(toolkit)
        
        # 读取或生成链接清单
        if LINKS_JSON.exists():
            print('3) 发现 links.json，直接读取...')
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
        print(f"4) 读取进度：index={state.get('index',0)}/{state.get('total',len(links))}, completed={len(state.get('completed',[]))}, failed={len(state.get('failed',[]))}")
        
        # 读取已下载URL集合
        downloaded_urls = load_downloaded_urls(OUTPUT_DIR)
        if downloaded_urls:
            print(f'   发现已下载 {len(downloaded_urls)} 篇，将自动跳过匹配链接')
        
        # 串行下载
        print('5) 串行下载RTX 5080相关文章...')
        for i in range(state.get('index', 0), len(links)):
            link = links[i]
            
            # 跳过已下载的链接
            if link in downloaded_urls or link in state.get('completed', []):
                print(f'  [{i+1}/{len(links)}] 跳过（已下载）: {link}')
                continue
            
            print(f'  [{i+1}/{len(links)}] 下载: {link}')
            try:
                r = await toolkit.download_content(Platform.ZHIHU, link, OUTPUT_DIR)
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
                
                # 下载间隔
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f'     💥 异常: {e}')
                state.setdefault('failed', []).append({'link': link, 'error': str(e)})
                state['index'] = i + 1
                save_json(STATE_JSON, state)
        
        print('\n6) 完成统计：')
        print(f"  成功: {len(state.get('completed', []))}")
        print(f"  失败: {len(state.get('failed', []))}")
        print(f"  总数: {len(links)}")
        print(f"  链接清单: {LINKS_JSON}")
        print(f"  进度文件: {STATE_JSON}")
        print(f"  输出目录: {OUTPUT_DIR}")
        
    finally:
        await toolkit.cleanup()


async def main():
    """主函数"""
    try:
        await run_zhihu_rtx5080_search()
    except KeyboardInterrupt:
        print("\n⏹️ 任务被用户中断")
    except Exception as e:
        print(f"\n💥 执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
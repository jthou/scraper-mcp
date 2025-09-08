#!/usr/bin/env python3
"""
知乎AI编程文章批量下载脚本
仿照微信登录策略：打开登录页面，间隔检查登录状态，登录成功后进行批量下载
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

# AI编程相关搜索关键词
AI_CODING_QUERIES = [
    "AI编程",
    "人工智能编程", 
    "AI开发",
    "智能编程",
    "AI编程助手",
    "Claude Code",
    "ChatGPT编程",
    "GitHub Copilot",
    "AI代码生成",
    "自动编程",
    "Python AI编程",
    "JavaScript AI",
    "AI工具开发",
    "机器学习编程",
    "深度学习编程",
    "AI调试",
    "AI重构",
    "AI测试",
    "AI编程工具",
    "AI开发环境",
    "AI编程范式",
    "智能代码分析",
    "AI代码审查",
    "AI编程最佳实践",
    "AI辅助开发"
]

OUTPUT_DIR = Path('K-Vault/AI-Coding/zhihu')
LINKS_JSON = OUTPUT_DIR / 'links.json'
STATE_JSON = OUTPUT_DIR / 'state.json'


async def wait_until_zhihu_logged_in(toolkit: ScraperToolkit):
    """等待知乎登录完成，仿照微信登录策略"""
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


def load_downloaded_urls(out_dir: Path):
    """从 file_mapping.json 读取已下载URL集合，用于跳过"""
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


async def collect_all_links(toolkit: ScraperToolkit) -> List[str]:
    """收集所有AI编程相关链接"""
    print('2) 收集AI编程相关链接（多关键词搜索）...')
    all_links: List[str] = []
    
    for i, query in enumerate(AI_CODING_QUERIES, 1):
        print(f'  [{i}/{len(AI_CODING_QUERIES)}] 搜索: {query}')
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


async def run_zhihu_ai_coding_download():
    """运行知乎AI编程文章批量下载"""
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
        print('1) 设置浏览器...')
        await toolkit.setup_browser(Platform.ZHIHU)
        
        print('2) 等待知乎登录...')
        await wait_until_zhihu_logged_in(toolkit)
        
        # 确保登录状态正确设置
        print('3) 确认登录状态...')
        login_result = await toolkit.web_scraper.login_zhihu()
        if login_result["status"] != "success":
            print(f"❌ 登录确认失败: {login_result.get('message', '未知错误')}")
            return
        print("✅ 登录状态确认成功")
        
        # 读取或生成链接清单
        if LINKS_JSON.exists():
            print('4) 发现 links.json，直接读取...')
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
        print(f"5) 读取进度：index={state.get('index',0)}/{state.get('total',len(links))}, completed={len(state.get('completed',[]))}, failed={len(state.get('failed',[]))}")
        
        # 读取已下载URL集合
        downloaded_urls = load_downloaded_urls(OUTPUT_DIR)
        if downloaded_urls:
            print(f'   发现已下载 {len(downloaded_urls)} 篇，将自动跳过匹配链接')
        
        # 串行下载
        print('6) 串行下载AI编程文章...')
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
        
        print('\n7) 完成统计：')
        print(f"  成功: {len(state.get('completed', []))}")
        print(f"  失败: {len(state.get('failed', []))}")
        print(f"  总数: {len(links)}")
        print(f"  链接清单: {LINKS_JSON}")
        print(f"  进度文件: {STATE_JSON}")
        print(f"  输出目录: {OUTPUT_DIR}")
        
    finally:
        await toolkit.cleanup()


if __name__ == '__main__':
    print("🚀 知乎AI编程文章批量下载")
    print("=" * 50)
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"🔍 搜索关键词: {len(AI_CODING_QUERIES)} 个")
    print("⏰ 预计时间: 30-60分钟")
    print("=" * 50)
    
    try:
        asyncio.run(run_zhihu_ai_coding_download())
    except KeyboardInterrupt:
        print("\n⏹️ 下载被用户中断")
    except Exception as e:
        print(f"\n💥 下载过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

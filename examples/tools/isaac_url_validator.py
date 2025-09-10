#!/usr/bin/env python3
"""
Isaac Sim URL验证器
检查哪些链接实际有效
"""

import asyncio
import json
import aiohttp
from pathlib import Path
from urllib.parse import urljoin

async def check_url(session, url, timeout=10):
    """检查单个URL是否有效"""
    try:
        async with session.head(url, timeout=timeout) as response:
            return {
                'url': url,
                'status': response.status,
                'valid': 200 <= response.status < 400,
                'content_type': response.headers.get('content-type', '')
            }
    except Exception as e:
        return {
            'url': url,
            'status': 'error',
            'valid': False,
            'error': str(e)
        }

async def discover_isaac_pages():
    """发现有效的Isaac Lab页面"""
    
    base_urls = [
        "https://isaac-sim.github.io/IsaacLab/",
        "https://isaac-sim.github.io/IsaacLab/main/",
        "https://docs.omniverse.nvidia.com/isaacsim/latest/",
    ]
    
    # 常见页面路径
    common_paths = [
        "index.html",
        "installation.html",
        "tutorial_intro.html",
        "features/overview.html",
        "getting_started.html",
        "api/index.html",
        "guides/index.html",
        "tutorials/index.html",
        "source/index.html",
        # Isaac Lab specific
        "source/setup/index.html",
        "source/features/index.html", 
        "source/tutorials/index.html",
        "source/api/index.html",
        # Documentation sections
        "setup/installation/index.html",
        "setup/sample.html",
        "features/actuators.html",
        "features/sensors.html",
        "features/environments.html",
        "tutorials/intro.html",
        "tutorials/core.html",
        "api/lab/index.html",
    ]
    
    all_urls_to_check = []
    
    # 生成所有URL组合
    for base_url in base_urls:
        all_urls_to_check.append(base_url)
        for path in common_paths:
            full_url = urljoin(base_url, path)
            all_urls_to_check.append(full_url)
    
    print(f"🔍 检查 {len(all_urls_to_check)} 个可能的URL...")
    
    # 并发检查URL
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [check_url(session, url) for url in all_urls_to_check]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 过滤有效结果
    valid_urls = []
    invalid_urls = []
    
    for result in results:
        if isinstance(result, dict):
            if result['valid']:
                valid_urls.append(result)
            else:
                invalid_urls.append(result)
    
    # 排序并显示结果
    valid_urls.sort(key=lambda x: x['url'])
    
    print(f"\n✅ 找到 {len(valid_urls)} 个有效URL:")
    for i, result in enumerate(valid_urls[:20], 1):  # 显示前20个
        print(f"  {i}. {result['url']} (状态: {result['status']})")
    
    if len(valid_urls) > 20:
        print(f"  ... 还有 {len(valid_urls) - 20} 个")
    
    print(f"\n❌ 无效URL: {len(invalid_urls)} 个")
    
    # 保存结果
    output_dir = Path("isaac_url_validation")
    output_dir.mkdir(exist_ok=True)
    
    # 保存有效URL
    valid_file = output_dir / "valid_urls.json"
    with open(valid_file, 'w', encoding='utf-8') as f:
        json.dump(valid_urls, f, ensure_ascii=False, indent=2)
    
    # 保存无效URL
    invalid_file = output_dir / "invalid_urls.json" 
    with open(invalid_file, 'w', encoding='utf-8') as f:
        json.dump(invalid_urls, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 结果已保存:")
    print(f"  有效URL: {valid_file}")
    print(f"  无效URL: {invalid_file}")
    
    return valid_urls

async def main():
    """主函数"""
    valid_urls = await discover_isaac_pages()
    
    if valid_urls:
        print(f"\n🎯 建议下载这些有效页面:")
        for url_info in valid_urls[:10]:
            print(f"  {url_info['url']}")

if __name__ == "__main__":
    asyncio.run(main())

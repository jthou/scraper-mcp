#!/usr/bin/env python3
"""
找到Isaac Sim真正的文档URL
通过爬取实际可访问的页面来发现正确的链接
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import re

async def discover_real_isaac_docs():
    """发现真正可访问的Isaac文档"""
    
    print("🔍 寻找Isaac Sim真正的文档结构...")
    
    # 尝试从已知可访问的页面开始
    entry_points = [
        "https://docs.omniverse.nvidia.com/",
        "https://docs.omniverse.nvidia.com/isaacsim/",
        "https://isaac-sim.github.io/IsaacLab/",
        "https://developer.nvidia.com/isaac-sim"
    ]
    
    valid_links = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        for entry_point in entry_points:
            try:
                print(f"🌐 检查入口: {entry_point}")
                response = await page.goto(entry_point, timeout=15000)
                
                if response and response.status < 400:
                    print(f"✅ 可访问: {entry_point}")
                    
                    # 获取页面内容
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 查找所有链接
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        href = link['href']
                        full_url = urljoin(entry_point, href)
                        
                        # 过滤Isaac相关的链接
                        if any(keyword in full_url.lower() for keyword in [
                            'isaac', 'simulation', 'robot', 'omniverse', 
                            'install', 'tutorial', 'guide', 'api', 'doc'
                        ]):
                            valid_links.add(full_url)
                            
                    print(f"  📋 发现 {len([l for l in valid_links if entry_point in l])} 个相关链接")
                
                else:
                    print(f"❌ 无法访问: {entry_point}")
                    
            except Exception as e:
                print(f"❌ 错误 {entry_point}: {e}")
        
        await browser.close()
    
    # 过滤和清理链接
    isaac_links = []
    for link in valid_links:
        # 排除不相关的链接
        if any(exclude in link for exclude in [
            'javascript:', 'mailto:', '#', 'github.com/NVIDIA', 
            '.zip', '.tar.gz', 'download'
        ]):
            continue
            
        # 只保留文档类链接
        if any(keyword in link.lower() for keyword in [
            'doc', 'tutorial', 'guide', 'api', 'install', 'setup'
        ]):
            isaac_links.append(link)
    
    print(f"\n📊 总共发现 {len(isaac_links)} 个潜在的Isaac文档链接")
    
    # 按域名分组
    by_domain = {}
    for link in isaac_links:
        domain = urlparse(link).netloc
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(link)
    
    print(f"\n🌐 按域名分组:")
    for domain, links in by_domain.items():
        print(f"  📍 {domain}: {len(links)} 个链接")
        for link in links[:3]:  # 显示前3个
            print(f"    - {link}")
        if len(links) > 3:
            print(f"    ... 还有 {len(links) - 3} 个")
    
    # 保存发现的链接
    discovery_report = {
        "发现时间": "2025-09-09",
        "总链接数": len(isaac_links),
        "按域名分组": by_domain,
        "所有链接": isaac_links
    }
    
    with open("isaac_real_docs_discovery.json", 'w', encoding='utf-8') as f:
        json.dump(discovery_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 发现报告保存至: isaac_real_docs_discovery.json")
    
    return isaac_links

async def verify_discovered_links(isaac_links):
    """验证发现的链接是否真的可访问"""
    
    print(f"\n🧪 验证 {len(isaac_links)} 个发现的链接...")
    
    async def check_link(session, url):
        try:
            async with session.head(url, timeout=10, allow_redirects=True) as response:
                return {
                    "url": url,
                    "status": response.status,
                    "valid": 200 <= response.status < 400
                }
        except:
            return {"url": url, "status": "error", "valid": False}
    
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [check_link(session, url) for url in isaac_links[:50]]  # 只验证前50个
        results = await asyncio.gather(*tasks)
    
    valid_urls = [r for r in results if r["valid"]]
    invalid_urls = [r for r in results if not r["valid"]]
    
    print(f"✅ 有效链接: {len(valid_urls)}")
    print(f"❌ 无效链接: {len(invalid_urls)}")
    
    # 显示有效链接
    print(f"\n📋 有效的Isaac文档链接:")
    for result in valid_urls:
        print(f"  ✅ {result['url']}")
    
    return [r["url"] for r in valid_urls]

async def main():
    # 1. 发现真实的Isaac文档链接
    isaac_links = await discover_real_isaac_docs()
    
    # 2. 验证链接有效性
    if isaac_links:
        valid_urls = await verify_discovered_links(isaac_links)
        
        print(f"\n🎯 建议:")
        print(f"  1. 使用这 {len(valid_urls)} 个验证过的URL")
        print(f"  2. Isaac Sim可能已经迁移了文档结构")
        print(f"  3. 重点关注Isaac Lab和Isaac ROS文档")
        
        return valid_urls
    else:
        print("❌ 未发现有效的Isaac文档链接")
        return []

if __name__ == "__main__":
    asyncio.run(main())

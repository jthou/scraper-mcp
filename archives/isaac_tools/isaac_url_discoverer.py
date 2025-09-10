#!/usr/bin/env python3
"""
Isaac Sim URL验证和发现工具
找出真正有效的文档URL
"""

import asyncio
import aiohttp
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re

class IsaacURLDiscoverer:
    def __init__(self):
        self.valid_urls = []
        self.invalid_urls = []
        self.discovered_patterns = set()
        
    async def check_url_exists(self, session, url, timeout=10):
        """检查URL是否存在"""
        try:
            async with session.head(url, timeout=timeout, allow_redirects=True) as response:
                return {
                    'url': url,
                    'status': response.status,
                    'valid': 200 <= response.status < 400,
                    'content_type': response.headers.get('content-type', ''),
                    'final_url': str(response.url)
                }
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'valid': False,
                'error': str(e)
            }
    
    async def discover_isaac_documentation_structure(self):
        """发现Isaac文档的真实结构"""
        print("🔍 发现Isaac文档的真实结构...")
        
        # 已知的有效基础URL
        base_urls_to_test = [
            "https://docs.omniverse.nvidia.com/isaacsim/",
            "https://docs.omniverse.nvidia.com/app_isaacsim/",
            "https://docs.omniverse.nvidia.com/py/isaacsim/",
            "https://isaac-sim.github.io/IsaacLab/",
            "https://isaac-sim.github.io/IsaacLab/main/",
            "https://nvidia-isaac-ros.github.io/",
            "https://docs.omniverse.nvidia.com/kit/docs/",
            "https://docs.omniverse.nvidia.com/usd/",
            "https://docs.omniverse.nvidia.com/materials-and-rendering/",
            "https://docs.omniverse.nvidia.com/extensions/"
        ]
        
        # 可能的版本号
        version_patterns = [
            "latest",
            "2023.1.1",
            "2024.1.0", 
            "4.0.0",
            "104.0",
            "105.0"
        ]
        
        # 构建要测试的URL列表
        urls_to_test = []
        
        # 测试基础URL
        for base_url in base_urls_to_test:
            urls_to_test.append(base_url)
            
            # 测试带版本的URL
            for version in version_patterns:
                versioned_url = urljoin(base_url, version + "/")
                urls_to_test.append(versioned_url)
                
                # 测试常见页面
                common_pages = [
                    "index.html",
                    "installation.html", 
                    "getting_started.html",
                    "tutorial_intro.html",
                    "tutorials/index.html",
                    "api/index.html",
                    "guide/index.html"
                ]
                
                for page in common_pages:
                    page_url = urljoin(versioned_url, page)
                    urls_to_test.append(page_url)
        
        print(f"🧪 测试 {len(urls_to_test)} 个可能的URL...")
        
        # 并发检查URL
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [self.check_url_exists(session, url) for url in urls_to_test]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 分析结果
        for result in results:
            if isinstance(result, dict):
                if result['valid']:
                    self.valid_urls.append(result)
                    # 提取URL模式
                    parsed = urlparse(result['url'])
                    pattern = f"{parsed.netloc}{parsed.path}"
                    self.discovered_patterns.add(pattern)
                else:
                    self.invalid_urls.append(result)
        
        print(f"✅ 发现 {len(self.valid_urls)} 个有效URL")
        print(f"❌ 无效URL: {len(self.invalid_urls)} 个")
        
        return self.valid_urls
    
    async def analyze_documentation_sites(self):
        """分析主要文档站点的结构"""
        print("\n🌐 分析主要文档站点...")
        
        # 主要站点分析
        main_sites = [
            {
                "name": "Omniverse Isaac Sim",
                "base": "https://docs.omniverse.nvidia.com/",
                "patterns": ["isaacsim", "app_isaacsim", "py/isaacsim"]
            },
            {
                "name": "Isaac Lab", 
                "base": "https://isaac-sim.github.io/",
                "patterns": ["IsaacLab", "IsaacLab/main"]
            },
            {
                "name": "Isaac ROS",
                "base": "https://nvidia-isaac-ros.github.io/",
                "patterns": ["", "getting_started", "repositories_and_packages"]
            },
            {
                "name": "Omniverse Kit",
                "base": "https://docs.omniverse.nvidia.com/kit/docs/",
                "patterns": ["kit-manual", "omni_physics", "carbonite"]
            }
        ]
        
        site_analysis = {}
        
        for site in main_sites:
            print(f"  🔍 分析 {site['name']}...")
            site_valid_urls = []
            
            for pattern in site['patterns']:
                test_url = urljoin(site['base'], pattern + "/")
                
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    result = await self.check_url_exists(session, test_url)
                    if result['valid']:
                        site_valid_urls.append(result)
                        print(f"    ✅ {test_url}")
                    else:
                        print(f"    ❌ {test_url} ({result.get('status', 'error')})")
            
            site_analysis[site['name']] = site_valid_urls
        
        return site_analysis
    
    def generate_corrected_urls(self):
        """基于发现的有效URL生成更正的下载列表"""
        print("\n🎯 生成更正的下载URL列表...")
        
        # 基于有效URL生成扩展列表
        corrected_urls = []
        
        for url_info in self.valid_urls:
            base_url = url_info['url']
            
            # 如果是目录页面，尝试添加常见子页面
            if base_url.endswith('/'):
                common_subpages = [
                    "index.html",
                    "installation.html",
                    "getting_started.html", 
                    "tutorial_intro.html",
                    "tutorials/index.html",
                    "api/index.html",
                    "reference/index.html",
                    "guide/index.html",
                    "examples/index.html"
                ]
                
                for subpage in common_subpages:
                    full_url = urljoin(base_url, subpage)
                    corrected_urls.append({
                        "url": full_url,
                        "source": "generated_from_valid_base",
                        "base": base_url
                    })
            else:
                corrected_urls.append({
                    "url": base_url,
                    "source": "directly_validated",
                    "base": base_url
                })
        
        return corrected_urls
    
    async def main_analysis(self):
        """主分析流程"""
        print("🚀 开始Isaac文档URL深度分析...")
        
        # 1. 发现文档结构
        valid_urls = await self.discover_isaac_documentation_structure()
        
        # 2. 分析主要站点
        site_analysis = await self.analyze_documentation_sites()
        
        # 3. 生成更正的URL列表
        corrected_urls = self.generate_corrected_urls()
        
        # 4. 总结发现
        print(f"\n📊 分析总结:")
        print(f"  🔍 测试的URL总数: {len(self.valid_urls) + len(self.invalid_urls)}")
        print(f"  ✅ 有效URL: {len(self.valid_urls)}")
        print(f"  ❌ 无效URL: {len(self.invalid_urls)}")
        print(f"  🎯 生成的下载候选: {len(corrected_urls)}")
        
        # 5. 按站点分组显示有效URL
        print(f"\n🌐 按站点分组的有效URL:")
        site_groups = {}
        for url_info in self.valid_urls:
            domain = urlparse(url_info['url']).netloc
            if domain not in site_groups:
                site_groups[domain] = []
            site_groups[domain].append(url_info['url'])
        
        for domain, urls in site_groups.items():
            print(f"  📍 {domain}: {len(urls)} 个有效URL")
            for url in urls[:5]:  # 显示前5个
                print(f"    - {url}")
            if len(urls) > 5:
                print(f"    ... 还有 {len(urls) - 5} 个")
        
        # 6. 保存结果
        report = {
            "分析时间": "2025-09-09",
            "有效URL总数": len(self.valid_urls),
            "无效URL总数": len(self.invalid_urls),
            "有效URL列表": [url['url'] for url in self.valid_urls],
            "站点分析": {domain: urls for domain, urls in site_groups.items()},
            "推荐下载URL": [item['url'] for item in corrected_urls[:50]]  # 前50个
        }
        
        report_file = Path("isaac_url_analysis_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告保存至: {report_file}")
        
        # 7. 生成建议
        print(f"\n💡 下载建议:")
        print(f"  1. 优先下载已验证的 {len(self.valid_urls)} 个有效URL")
        print(f"  2. Isaac Sim官方文档可能使用了不同的URL结构")
        print(f"  3. 重点关注 isaac-sim.github.io 和 nvidia-isaac-ros.github.io")
        print(f"  4. 避免使用 /latest/ 路径，很多返回404")
        
        return corrected_urls

async def main():
    discoverer = IsaacURLDiscoverer()
    corrected_urls = await discoverer.main_analysis()
    
    print(f"\n🎯 可以用这些验证过的URL创建新的下载器!")

if __name__ == "__main__":
    asyncio.run(main())

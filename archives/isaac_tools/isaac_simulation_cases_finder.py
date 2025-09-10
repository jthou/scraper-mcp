#!/usr/bin/env python3
"""
Isaac Sim 仿真案例文档专项搜索器
专门寻找和下载Isaac Sim的仿真案例、教程和示例文档
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from pathlib import Path
import hashlib
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup

class IsaacSimCasesFinder:
    def __init__(self, output_dir="isaac_simulation_cases"):
        self.output_dir = Path(output_dir)
        self.pdf_dir = self.output_dir / "pdfs" 
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        
        self.found_urls = set()
        self.downloaded_files = []
        self.errors = []
        self.success_count = 0
        self.error_count = 0
        
    async def search_isaac_simulation_cases(self):
        """搜索Isaac Sim仿真案例的多种来源"""
        
        print("🔍 专项搜索Isaac Sim仿真案例文档...")
        
        # 多种搜索策略
        search_strategies = [
            self.search_github_docs(),
            self.search_nvidia_developer(),
            self.search_isaac_lab_examples(),
            self.search_omniverse_tutorials(),
            self.search_isaac_ros_examples()
        ]
        
        # 并行执行所有搜索策略
        await asyncio.gather(*search_strategies, return_exceptions=True)
        
        print(f"🎯 总共发现 {len(self.found_urls)} 个仿真案例相关URL")
        return list(self.found_urls)
    
    async def search_github_docs(self):
        """搜索GitHub上的Isaac文档"""
        print("📚 搜索GitHub文档...")
        
        github_sources = [
            "https://isaac-sim.github.io/IsaacLab/",
            "https://isaac-sim.github.io/IsaacLab/main/",
            "https://nvidia-isaac-ros.github.io/"
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            
            for source in github_sources:
                try:
                    page = await browser.new_page()
                    print(f"  🔍 检查: {source}")
                    
                    response = await page.goto(source, timeout=20000, wait_until="networkidle")
                    if response and response.status < 400:
                        await self.extract_simulation_links(page, source)
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"  ❌ GitHub搜索错误 {source}: {e}")
            
            await browser.close()
    
    async def search_nvidia_developer(self):
        """搜索NVIDIA开发者网站"""
        print("🏢 搜索NVIDIA开发者网站...")
        
        nvidia_urls = [
            "https://developer.nvidia.com/isaac-sim",
            "https://docs.omniverse.nvidia.com/",
            "https://docs.omniverse.nvidia.com/isaacsim/",
            "https://docs.omniverse.nvidia.com/extensions/",
            "https://docs.omniverse.nvidia.com/kit/"
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            
            for url in nvidia_urls:
                try:
                    page = await browser.new_page()
                    print(f"  🔍 检查: {url}")
                    
                    # 设置更长的超时时间
                    response = await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    if response and response.status < 400:
                        await asyncio.sleep(3)  # 等待动态内容加载
                        await self.extract_simulation_links(page, url)
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"  ❌ NVIDIA搜索错误 {url}: {e}")
            
            await browser.close()
    
    async def search_isaac_lab_examples(self):
        """深度搜索Isaac Lab的示例"""
        print("🧪 深度搜索Isaac Lab示例...")
        
        lab_paths = [
            "source/tutorials/",
            "source/tutorials/00_sim/",
            "source/tutorials/01_assets/", 
            "source/tutorials/02_scene/",
            "source/tutorials/03_envs/",
            "source/tutorials/04_sensors/",
            "source/tutorials/05_controllers/",
            "source/api/lab/envs/",
            "source/api/lab/sim/",
            "source/api/lab/assets/",
            "source/how-to/",
            "source/deployment/"
        ]
        
        base_url = "https://isaac-sim.github.io/IsaacLab/main/"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            
            for path in lab_paths:
                try:
                    full_url = urljoin(base_url, path)
                    page = await browser.new_page()
                    print(f"  🔍 检查Lab路径: {path}")
                    
                    response = await page.goto(full_url, timeout=15000)
                    if response and response.status < 400:
                        await self.extract_simulation_links(page, full_url)
                        self.found_urls.add(full_url)
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"  ❌ Lab路径错误 {path}: {e}")
            
            await browser.close()
    
    async def search_omniverse_tutorials(self):
        """搜索Omniverse教程"""
        print("🎓 搜索Omniverse教程...")
        
        tutorial_paths = [
            "app_isaacsim/app_isaacsim/tutorial_intro.html",
            "app_isaacsim/app_isaacsim/tutorial_gui_basics.html", 
            "app_isaacsim/app_isaacsim/tutorial_simple_objects.html",
            "app_isaacsim/app_isaacsim/tutorial_required_interface.html",
            "app_isaacsim/app_isaacsim/tutorial_core_api.html",
            "app_isaacsim/app_isaacsim/advanced_tutorials.html",
            "py/isaacsim/",
            "extensions/omni.isaac.sim/",
            "extensions/omni.isaac.core/"
        ]
        
        base_url = "https://docs.omniverse.nvidia.com/"
        
        # 直接验证这些URL
        async with aiohttp.ClientSession() as session:
            for path in tutorial_paths:
                try:
                    full_url = urljoin(base_url, path)
                    async with session.head(full_url, timeout=10) as response:
                        if 200 <= response.status < 400:
                            self.found_urls.add(full_url)
                            print(f"  ✅ 找到: {path}")
                        else:
                            print(f"  ❌ 无效: {path} ({response.status})")
                except:
                    print(f"  ❌ 错误: {path}")
    
    async def search_isaac_ros_examples(self):
        """搜索Isaac ROS示例"""
        print("🤖 搜索Isaac ROS示例...")
        
        ros_paths = [
            "tutorials/",
            "concepts/",
            "performance/",
            "getting_started/",
            "repositories_and_packages/isaac_ros_apriltag/",
            "repositories_and_packages/isaac_ros_visual_slam/",
            "repositories_and_packages/isaac_ros_nvblox/",
            "repositories_and_packages/isaac_ros_image_pipeline/",
            "repositories_and_packages/isaac_ros_common/"
        ]
        
        base_url = "https://nvidia-isaac-ros.github.io/"
        
        for path in ros_paths:
            full_url = urljoin(base_url, path)
            self.found_urls.add(full_url)
    
    async def extract_simulation_links(self, page, base_url):
        """从页面中提取仿真相关的链接"""
        try:
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找所有链接
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                link_text = link.get_text().lower()
                
                # 过滤仿真案例相关的链接
                simulation_keywords = [
                    'tutorial', 'example', 'demo', 'case', 'simulation', 'sim',
                    'robot', 'manipulation', 'navigation', 'sensor', 'camera',
                    'physics', 'collision', 'dynamics', 'control', 'rl', 
                    'reinforcement', 'learning', 'training', 'environment',
                    'scene', 'asset', 'urdf', 'articulation', 'joint'
                ]
                
                if any(keyword in link_text for keyword in simulation_keywords) or \
                   any(keyword in href.lower() for keyword in simulation_keywords):
                    
                    full_url = urljoin(base_url, href)
                    
                    # 过滤掉不相关的链接
                    if not any(exclude in full_url for exclude in [
                        'github.com', 'youtube.com', 'twitter.com', 'facebook.com',
                        'mailto:', 'javascript:', '#', '.zip', '.tar.gz'
                    ]):
                        self.found_urls.add(full_url)
                        
        except Exception as e:
            print(f"  ⚠️ 链接提取错误: {e}")
    
    async def download_simulation_docs(self, urls):
        """下载仿真文档"""
        print(f"🚀 开始下载 {len(urls)} 个仿真案例文档...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            
            for i, url in enumerate(urls, 1):
                try:
                    print(f"\n📄 进度: {i}/{len(urls)}")
                    print(f"📥 下载: {url}")
                    
                    page = await browser.new_page()
                    
                    # 设置页面
                    await page.set_viewport_size({"width": 1920, "height": 1080})
                    await page.set_extra_http_headers({
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                    })
                    
                    # 导航到页面
                    response = await page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    if not response or response.status >= 400:
                        raise Exception(f"HTTP错误: {response.status if response else 'No response'}")
                    
                    # 等待页面完全加载
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2)
                    
                    # 生成文件名
                    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                    parsed_url = urlparse(url)
                    path_part = parsed_url.path.strip('/').replace('/', '_').replace('.html', '')
                    if not path_part:
                        path_part = "index"
                    
                    filename = f"sim_case_{path_part}_{url_hash}.pdf"
                    pdf_path = self.pdf_dir / filename
                    
                    # 生成PDF
                    await page.pdf(
                        path=str(pdf_path),
                        format="A4",
                        print_background=True,
                        margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
                    )
                    
                    await page.close()
                    
                    # 检查文件
                    file_size = pdf_path.stat().st_size
                    if file_size < 1000:
                        pdf_path.unlink()
                        raise Exception("PDF文件过小")
                    
                    file_info = {
                        "url": url,
                        "filename": filename,
                        "size": file_size,
                        "category": self.categorize_url(url),
                        "download_time": datetime.now().isoformat()
                    }
                    
                    self.downloaded_files.append(file_info)
                    self.success_count += 1
                    
                    size_mb = file_size / (1024 * 1024)
                    print(f"✅ 成功: {filename} ({size_mb:.1f} MB)")
                    
                    # 进度报告
                    if i % 10 == 0:
                        total_size = sum(f["size"] for f in self.downloaded_files) / (1024 * 1024)
                        print(f"📊 进度报告: 成功 {self.success_count}, 失败 {self.error_count}")
                        print(f"💾 当前大小: {total_size:.1f} MB")
                    
                    # 延迟避免过载
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    error_info = {
                        "url": url,
                        "error": str(e),
                        "error_time": datetime.now().isoformat()
                    }
                    
                    self.errors.append(error_info)
                    self.error_count += 1
                    print(f"❌ 失败: {url} - {str(e)}")
            
            await browser.close()
    
    def categorize_url(self, url):
        """根据URL分类文档类型"""
        url_lower = url.lower()
        
        if 'tutorial' in url_lower:
            return "教程"
        elif 'example' in url_lower or 'demo' in url_lower:
            return "示例"
        elif 'api' in url_lower:
            return "API文档"
        elif 'isaac-ros' in url_lower:
            return "Isaac ROS"
        elif 'isaaclab' in url_lower:
            return "Isaac Lab"
        elif 'omniverse' in url_lower:
            return "Omniverse"
        else:
            return "其他"
    
    async def generate_report(self):
        """生成下载报告"""
        total_size = sum(f["size"] for f in self.downloaded_files)
        total_size_mb = total_size / (1024 * 1024)
        
        # 按类别统计
        category_stats = {}
        for file_info in self.downloaded_files:
            category = file_info["category"]
            if category not in category_stats:
                category_stats[category] = {"count": 0, "size": 0}
            category_stats[category]["count"] += 1
            category_stats[category]["size"] += file_info["size"]
        
        report = {
            "搜索时间": datetime.now().isoformat(),
            "发现URL总数": len(self.found_urls),
            "成功下载": self.success_count,
            "失败数量": self.error_count,
            "成功率": f"{self.success_count / max(len(self.found_urls), 1) * 100:.1f}%",
            "总大小MB": f"{total_size_mb:.1f}",
            "按类别统计": {
                cat: {
                    "文件数": stats["count"], 
                    "大小MB": f"{stats['size'] / (1024 * 1024):.1f}"
                }
                for cat, stats in category_stats.items()
            },
            "发现的URL": list(self.found_urls),
            "下载文件": self.downloaded_files,
            "错误列表": self.errors
        }
        
        report_file = self.output_dir / "simulation_cases_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 仿真案例搜索下载完成!")
        print(f"📊 成功: {self.success_count}, 失败: {self.error_count}")
        print(f"💾 总大小: {total_size_mb:.1f} MB")
        print(f"📁 文件位置: {self.pdf_dir}")
        print(f"📋 详细报告: {report_file}")
        
        if category_stats:
            print(f"\n📊 按类别统计:")
            for category, stats in category_stats.items():
                size_mb = stats["size"] / (1024 * 1024)
                print(f"  📂 {category}: {stats['count']} 个文件, {size_mb:.1f} MB")

async def main():
    finder = IsaacSimCasesFinder()
    
    # 1. 搜索仿真案例URLs
    urls = await finder.search_isaac_simulation_cases()
    
    if urls:
        print(f"\n🎯 找到 {len(urls)} 个仿真案例相关URL，开始下载...")
        # 2. 下载文档
        await finder.download_simulation_docs(urls)
        # 3. 生成报告
        await finder.generate_report()
    else:
        print("❌ 未找到仿真案例相关URL")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Isaac Sim 无限制完整下载器
下载所有可能找到的Isaac Sim相关文档，不设限制
"""

import asyncio
import json
import aiohttp
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import time
import hashlib
import re
from datetime import datetime

class IsaacUnlimitedDownloader:
    def __init__(self, output_dir="isaac_unlimited_downloads"):
        self.output_dir = Path(output_dir)
        self.pdfs_dir = self.output_dir / "pdfs"
        self.logs_dir = self.output_dir / "logs"
        
        # 创建输出目录
        for dir_path in [self.pdfs_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 状态追踪
        self.discovered_urls = set()
        self.visited_urls = set()
        self.downloaded_urls = set()
        self.failed_urls = set()
        
        # 统计信息
        self.stats = {
            '发现': 0,
            '访问': 0,
            '成功': 0,
            '失败': 0,
            '跳过': 0
        }
        
        # 所有可能的Isaac相关域名和路径
        self.isaac_domains = [
            'isaac-sim.github.io',
            'docs.omniverse.nvidia.com',
            'docs.nvidia.com',
            'developer.nvidia.com'
        ]
        
        # 种子URL - 扩展版本
        self.seed_urls = [
            # Isaac Lab
            "https://isaac-sim.github.io/IsaacLab/",
            "https://isaac-sim.github.io/IsaacLab/main/",
            "https://isaac-sim.github.io/IsaacLab/main/source/api/index.html",
            "https://isaac-sim.github.io/IsaacLab/main/source/tutorials/index.html",
            "https://isaac-sim.github.io/IsaacLab/main/source/setup/index.html",
            "https://isaac-sim.github.io/IsaacLab/main/source/features/index.html",
            
            # Omniverse Isaac Sim
            "https://docs.omniverse.nvidia.com/isaacsim/latest/",
            "https://docs.omniverse.nvidia.com/isaacsim/latest/installation/",
            "https://docs.omniverse.nvidia.com/isaacsim/latest/tutorial_intro.html",
            "https://docs.omniverse.nvidia.com/isaacsim/latest/features/",
            "https://docs.omniverse.nvidia.com/isaacsim/latest/api/",
            
            # NVIDIA Developer
            "https://developer.nvidia.com/isaac-sim",
            "https://docs.nvidia.com/isaac/",
        ]
        
        # 并发控制 - 更积极的设置
        self.discovery_semaphore = asyncio.Semaphore(10)  # 发现链接的并发数
        self.download_semaphore = asyncio.Semaphore(3)    # 下载的并发数
        
        self.start_time = time.time()
        
    def is_isaac_related_url(self, url):
        """检查URL是否与Isaac相关"""
        parsed = urlparse(url)
        
        # 必须在相关域名内
        if parsed.netloc not in self.isaac_domains:
            return False
        
        # Isaac相关关键词
        isaac_keywords = [
            'isaac', 'omniverse', 'simulation', 'robot', 'physics',
            'isaacsim', 'isaaclab', 'gym', 'rl', 'reinforcement'
        ]
        
        url_lower = url.lower()
        if not any(keyword in url_lower for keyword in isaac_keywords):
            return False
        
        # 排除不需要的文件类型
        exclude_patterns = [
            r'\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|ttf|eot)(\?|$)',
            r'\.(zip|tar|gz|pdf|mp4|mov|avi)(\?|$)',
            r'/_static/',
            r'/_sources/',
            r'/genindex',
            r'/search',
            r'#',
            'mailto:',
            'javascript:',
            'tel:',
            'ftp:',
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url):
                return False
        
        return True
    
    async def discover_links_from_url(self, session, url):
        """从URL发现新链接"""
        async with self.discovery_semaphore:
            if url in self.visited_urls:
                return []
            
            try:
                print(f"🔍 探索: {url}")
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    discovered = []
                    
                    # 查找所有链接
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        absolute_url = urljoin(url, href)
                        
                        if (self.is_isaac_related_url(absolute_url) and 
                            absolute_url not in self.discovered_urls):
                            discovered.append(absolute_url)
                            self.discovered_urls.add(absolute_url)
                    
                    # 查找可能的API或文档结构
                    for link in soup.find_all(['link', 'script'], src=True):
                        src = link.get('src', '')
                        if src:
                            absolute_url = urljoin(url, src)
                            if (self.is_isaac_related_url(absolute_url) and 
                                absolute_url not in self.discovered_urls):
                                discovered.append(absolute_url)
                                self.discovered_urls.add(absolute_url)
                    
                    self.visited_urls.add(url)
                    self.stats['访问'] += 1
                    self.stats['发现'] += len(discovered)
                    
                    if discovered:
                        print(f"📎 发现 {len(discovered)} 个新链接")
                    
                    return discovered
                    
            except Exception as e:
                print(f"❌ 探索失败 {url}: {e}")
                return []
    
    async def download_page_to_pdf(self, browser, url):
        """将页面下载为PDF"""
        async with self.download_semaphore:
            if url in self.downloaded_urls:
                self.stats['跳过'] += 1
                return {"status": "跳过", "url": url}
            
            try:
                # 生成唯一文件名
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                parsed = urlparse(url)
                
                # 从URL路径生成有意义的文件名
                path_parts = [p for p in parsed.path.split('/') if p and p != 'index.html']
                if path_parts:
                    name_part = '_'.join(path_parts[-3:])[:80]  # 取最后3个路径部分
                else:
                    name_part = parsed.netloc.replace('.', '_')
                
                # 清理文件名
                safe_name = re.sub(r'[^\w\-_]', '_', name_part)
                filename = f"isaac_{safe_name}_{url_hash}.pdf"
                pdf_path = self.pdfs_dir / filename
                
                # 检查文件是否已存在
                if pdf_path.exists():
                    self.downloaded_urls.add(url)
                    self.stats['跳过'] += 1
                    return {"status": "跳过", "url": url, "path": pdf_path}
                
                print(f"📥 下载: {url}")
                
                # 创建新页面
                page = await browser.new_page()
                
                # 设置更好的用户代理和头信息
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                })
                
                # 设置视口大小
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                # 导航到页面
                response = await page.goto(url, timeout=90000, wait_until='domcontentloaded')
                
                if not response or response.status >= 400:
                    raise Exception(f"HTTP错误: {response.status}")
                
                # 等待页面加载完成
                await page.wait_for_timeout(5000)
                
                # 尝试等待主要内容
                try:
                    await page.wait_for_selector('body', timeout=10000)
                    # 等待可能的动态内容
                    await page.wait_for_timeout(3000)
                except:
                    pass
                
                # 生成高质量PDF
                await page.pdf(
                    path=str(pdf_path),
                    format='A4',
                    print_background=True,
                    prefer_css_page_size=False,
                    margin={
                        'top': '20px',
                        'right': '20px', 
                        'bottom': '20px',
                        'left': '20px'
                    },
                    display_header_footer=False
                )
                
                await page.close()
                
                # 验证PDF文件
                if not pdf_path.exists() or pdf_path.stat().st_size < 2000:
                    if pdf_path.exists():
                        pdf_path.unlink()
                    raise Exception("PDF文件太小或生成失败")
                
                self.downloaded_urls.add(url)
                self.stats['成功'] += 1
                
                print(f"✅ 成功下载: {filename} ({pdf_path.stat().st_size / 1024:.1f} KB)")
                
                return {
                    "status": "成功",
                    "url": url,
                    "filename": filename,
                    "path": str(pdf_path),
                    "size": pdf_path.stat().st_size,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                if 'pdf_path' in locals() and pdf_path.exists():
                    pdf_path.unlink()
                
                self.failed_urls.add(url)
                self.stats['失败'] += 1
                
                print(f"❌ 下载失败: {url} - {str(e)[:100]}")
                
                return {
                    "status": "失败",
                    "url": url,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
    
    async def unlimited_crawl_and_download(self):
        """无限制爬取和下载"""
        print(f"🚀 开始无限制Isaac文档下载!")
        print(f"📋 种子URL: {len(self.seed_urls)} 个")
        
        # 初始化队列
        discovery_queue = list(self.seed_urls)
        download_queue = list(self.seed_urls)
        self.discovered_urls.update(self.seed_urls)
        
        # 启动浏览器
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-extensions'
                ]
            )
            
            # 启动HTTP会话
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                
                try:
                    round_number = 1
                    
                    while discovery_queue or download_queue:
                        print(f"\n🔄 第 {round_number} 轮处理")
                        print(f"📊 状态: 发现 {len(self.discovered_urls)}, 访问 {len(self.visited_urls)}, 下载 {len(self.downloaded_urls)}")
                        
                        # 阶段1: 并发发现新链接
                        if discovery_queue:
                            print(f"🔍 发现阶段: 处理 {len(discovery_queue)} 个URL")
                            current_discovery = discovery_queue[:20]  # 每轮处理20个
                            discovery_queue = discovery_queue[20:]
                            
                            discovery_tasks = [
                                self.discover_links_from_url(session, url)
                                for url in current_discovery
                            ]
                            
                            discovery_results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
                            
                            # 收集新发现的链接
                            for result in discovery_results:
                                if isinstance(result, list):
                                    discovery_queue.extend(result)
                                    download_queue.extend(result)
                        
                        # 阶段2: 并发下载页面
                        if download_queue:
                            print(f"📥 下载阶段: 处理 {min(10, len(download_queue))} 个URL")
                            current_downloads = download_queue[:10]  # 每轮下载10个
                            download_queue = download_queue[10:]
                            
                            download_tasks = [
                                self.download_page_to_pdf(browser, url)
                                for url in current_downloads
                            ]
                            
                            download_results = await asyncio.gather(*download_tasks, return_exceptions=True)
                            
                            # 显示下载结果
                            for result in download_results:
                                if isinstance(result, dict) and result.get('status') == '成功':
                                    print(f"📄 已下载: {result['filename']}")
                        
                        # 每10轮显示详细统计
                        if round_number % 10 == 0:
                            self.print_detailed_stats()
                        
                        round_number += 1
                        
                        # 短暂休息
                        await asyncio.sleep(2)
                        
                        # 安全检查：避免无限循环
                        if round_number > 1000:
                            print("⚠️  达到最大轮数限制，停止处理")
                            break
                
                finally:
                    await browser.close()
        
        # 生成最终报告
        self.generate_final_report()
    
    def print_detailed_stats(self):
        """打印详细统计信息"""
        total_size = 0
        total_files = 0
        
        if self.pdfs_dir.exists():
            for pdf in self.pdfs_dir.glob("*.pdf"):
                total_size += pdf.stat().st_size
                total_files += 1
        
        elapsed = time.time() - self.start_time
        
        print(f"\n📊 详细统计 (运行时间: {elapsed/60:.1f} 分钟):")
        print(f"  🔗 发现URL: {len(self.discovered_urls)} 个")
        print(f"  👁️  访问URL: {len(self.visited_urls)} 个")
        print(f"  ✅ 成功下载: {self.stats['成功']} 个")
        print(f"  ❌ 下载失败: {self.stats['失败']} 个")
        print(f"  ⏭️  跳过重复: {self.stats['跳过']} 个")
        print(f"  📁 PDF文件: {total_files} 个")
        print(f"  💾 总大小: {total_size / 1024 / 1024:.1f} MB")
        print(f"  📈 下载速度: {self.stats['成功'] / max(elapsed/60, 1):.1f} 文件/分钟")
    
    def generate_final_report(self):
        """生成最终报告"""
        total_size = 0
        total_files = 0
        
        if self.pdfs_dir.exists():
            for pdf in self.pdfs_dir.glob("*.pdf"):
                total_size += pdf.stat().st_size
                total_files += 1
        
        elapsed = time.time() - self.start_time
        
        report = {
            "无限制下载总结": {
                "运行时间分钟": f"{elapsed/60:.1f}",
                "发现URL总数": len(self.discovered_urls),
                "访问URL总数": len(self.visited_urls),
                "成功下载": self.stats['成功'],
                "下载失败": self.stats['失败'],
                "跳过重复": self.stats['跳过'],
                "PDF文件数": total_files,
                "总大小MB": f"{total_size / 1024 / 1024:.1f}",
                "下载速度": f"{self.stats['成功'] / max(elapsed/60, 1):.1f} 文件/分钟"
            },
            "文件位置": {
                "PDF目录": str(self.pdfs_dir),
                "日志目录": str(self.logs_dir)
            },
            "完成时间": datetime.now().isoformat(),
            "种子URLs": self.seed_urls,
            "统计详情": self.stats
        }
        
        # 保存报告
        report_file = self.output_dir / "unlimited_download_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存URL列表
        urls_file = self.output_dir / "all_discovered_urls.json"
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump({
                "discovered": list(self.discovered_urls),
                "visited": list(self.visited_urls),
                "downloaded": list(self.downloaded_urls),
                "failed": list(self.failed_urls)
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 无限制下载完成!")
        self.print_detailed_stats()
        print(f"📋 详细报告: {report_file}")
        print(f"🔗 URL列表: {urls_file}")

async def main():
    """主函数"""
    downloader = IsaacUnlimitedDownloader()
    await downloader.unlimited_crawl_and_download()

if __name__ == "__main__":
    asyncio.run(main())

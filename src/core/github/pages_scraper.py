"""重构后的GitHub Pages抓取器 - 基于新的模块化结构"""
import asyncio
import re
import json
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import html2text

from .config import GitHubConfig, default_config
from .utils import GitHubUtils, AsyncRateLimiter, ContentExtractor


class GitHubPagesScraper:
    """GitHub Pages文档站点专用抓取器 - 重构版本"""
    
    def __init__(self, config: GitHubConfig = None):
        """
        初始化GitHub Pages抓取器
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or default_config
        self.session: Optional[aiohttp.ClientSession] = None
        self.visited_urls: Set[str] = set()
        self.extracted_content: List[Dict[str, Any]] = []
        self.rate_limiter = AsyncRateLimiter(100, 3600)  # 每小时100请求
        
        # HTML到Markdown转换器配置
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = not self.config.extract_links
        self.h2t.ignore_images = not self.config.extract_images
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # 不换行
        
        # 创建输出目录
        self.output_dir = self.config.output_base_dir / "Pages"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 常见的文档生成器特征
        self.doc_generators = {
            "jekyll": {
                "indicators": ["jekyll", "_config.yml", ".jekyll-cache", "_site"],
                "meta_pattern": r'generator["\s]*content["\s]*=["\s]*jekyll'
            },
            "docusaurus": {
                "indicators": ["docusaurus", ".docusaurus"],
                "meta_pattern": r'generator["\s]*content["\s]*=["\s]*docusaurus'
            },
            "gatsby": {
                "indicators": ["gatsby", "___gatsby"],
                "meta_pattern": r'generator["\s]*content["\s]*=["\s]*gatsby'
            },
            "next": {
                "indicators": ["next.js", "_next"],
                "meta_pattern": r'generator["\s]*content["\s]*=["\s]*next'
            },
            "vuepress": {
                "indicators": ["vuepress"],
                "meta_pattern": r'generator["\s]*content["\s]*=["\s]*vuepress'
            },
            "gitbook": {
                "indicators": ["gitbook"],
                "meta_pattern": r'generator["\s]*content["\s]*=["\s]*gitbook'
            },
            "mkdocs": {
                "indicators": ["mkdocs"],
                "meta_pattern": r'generator["\s]*content["\s]*=["\s]*mkdocs'
            }
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers=self.config.request_headers,
            timeout=aiohttp.ClientTimeout(total=self.config.pages_timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def discover_github_pages(self, owner: str, repo: str = None) -> List[Dict[str, Any]]:
        """
        发现GitHub Pages站点
        
        Args:
            owner: GitHub用户名或组织名
            repo: 仓库名，如果为None则发现用户的主Pages站点
            
        Returns:
            发现的站点信息列表
        """
        print(f"🔍 发现GitHub Pages: {owner}/{repo if repo else 'main-site'}")
        
        if repo:
            sites = await self._discover_single_repo_pages(owner, repo)
        else:
            sites = await self._discover_user_pages(owner)
        
        print(f"📋 发现 {len(sites)} 个站点")
        return sites
    
    async def _discover_single_repo_pages(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """发现单个仓库的Pages站点"""
        # 生成可能的URL列表
        possible_urls = [
            f"https://{owner}.github.io/{repo}/",
            f"https://{owner}.github.io/" if repo == f"{owner}.github.io" else None,
            f"https://{repo}.netlify.app/",
            f"https://{repo}.vercel.app/",
            f"https://{repo}.surge.sh/"
        ]
        
        # 过滤None值
        possible_urls = [url for url in possible_urls if url]
        
        # 检查自定义域名
        try:
            cname_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/CNAME"
            async with self.session.get(cname_url) as response:
                if response.status == 200:
                    cname = (await response.text()).strip()
                    if cname:
                        possible_urls.append(f"https://{cname}/")
        except Exception:
            # 如果获取CNAME失败，继续其他检查
            pass
        
        # 并发验证所有可能的URL
        tasks = [
            self._validate_pages_site(url, owner, repo) 
            for url in possible_urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤有效结果
        valid_sites = []
        for result in results:
            if isinstance(result, dict) and result.get("status") == "active":
                valid_sites.append(result)
        
        return valid_sites
    
    async def _discover_user_pages(self, owner: str) -> List[Dict[str, Any]]:
        """发现用户/组织的主Pages站点"""
        main_site_url = f"https://{owner}.github.io/"
        site_info = await self._validate_pages_site(main_site_url, owner, None)
        
        return [site_info] if site_info else []
    
    async def _validate_pages_site(self, url: str, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """验证Pages站点是否存在并获取基本信息"""
        try:
            await self.rate_limiter.acquire()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # 检测文档生成器类型
                    generator = self._detect_generator(content, dict(response.headers))
                    
                    # 提取基本信息
                    title = self._extract_title(content)
                    description = self._extract_description(content)
                    
                    # 检查内容质量
                    text_content = ContentExtractor.extract_text_content(content)
                    
                    return {
                        "url": url,
                        "owner": owner,
                        "repo": repo,
                        "status": "active",
                        "generator": generator,
                        "title": title,
                        "description": description,
                        "content_length": len(text_content),
                        "discovered_at": datetime.now().isoformat(),
                        "response_headers": dict(response.headers)
                    }
                elif response.status == 404:
                    return {
                        "url": url,
                        "owner": owner,
                        "repo": repo,
                        "status": "not_found",
                        "discovered_at": datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"⚠️ 验证站点失败 {url}: {e}")
            return {
                "url": url,
                "owner": owner,
                "repo": repo,
                "status": "error",
                "error": str(e),
                "discovered_at": datetime.now().isoformat()
            }
        
        return None
    
    def _detect_generator(self, content: str, headers: Dict[str, str]) -> str:
        """检测文档生成器类型"""
        content_lower = content.lower()
        
        # 首先检查meta标签
        for generator, config in self.doc_generators.items():
            if re.search(config["meta_pattern"], content_lower, re.IGNORECASE):
                return generator.title()
        
        # 然后检查内容特征
        for generator, config in self.doc_generators.items():
            for indicator in config["indicators"]:
                if indicator.lower() in content_lower:
                    return generator.title()
        
        # 检查服务器头部
        server = headers.get('server', '').lower()
        x_served_by = headers.get('x-served-by', '').lower()
        
        if 'github.com' in server or 'github-pages' in server:
            return "GitHub Pages"
        elif 'netlify' in server or 'netlify' in x_served_by:
            return "Netlify"
        elif 'vercel' in server or 'vercel' in x_served_by:
            return "Vercel"
        elif 'surge' in server:
            return "Surge"
        
        return "Unknown"
    
    def _extract_title(self, content: str) -> str:
        """提取页面标题"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # 优先查找title标签
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title:
                return title
        
        # 备选：查找h1标签
        h1_tag = soup.find('h1')
        if h1_tag:
            h1_text = h1_tag.get_text().strip()
            if h1_text:
                return h1_text
        
        # 备选：查找og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        return "Untitled"
    
    def _extract_description(self, content: str) -> str:
        """提取页面描述"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
            if desc:
                return desc[:200] + "..." if len(desc) > 200 else desc
        
        # 备选：查找og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            desc = og_desc['content'].strip()
            if desc:
                return desc[:200] + "..." if len(desc) > 200 else desc
        
        # 备选：查找第一个p标签
        p_tag = soup.find('p')
        if p_tag:
            text = p_tag.get_text().strip()
            if text:
                return text[:200] + "..." if len(text) > 200 else text
        
        return ""
    
    async def scrape_documentation_site(self, base_url: str, max_pages: int = None) -> Dict[str, Any]:
        """
        抓取完整的文档站点
        
        Args:
            base_url: 站点基础URL
            max_pages: 最大抓取页面数，如果为None则使用配置中的值
            
        Returns:
            抓取结果字典
        """
        max_pages = max_pages or self.config.pages_max_pages
        
        print(f"🕷️ 开始抓取文档站点: {base_url}")
        print(f"📊 最大页面数: {max_pages}")
        
        # 重置状态
        self.visited_urls.clear()
        self.extracted_content.clear()
        
        # 创建输出目录
        domain = GitHubUtils.get_url_domain(base_url)
        site_dir = self.output_dir / domain
        site_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 使用Playwright进行深度抓取
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config.pages_headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                page = await browser.new_page()
                
                # 设置用户代理和头部
                await page.set_extra_http_headers(self.config.request_headers)
                
                try:
                    # 首先发现站点地图
                    sitemap_urls = await self._discover_sitemap(page, base_url)
                    
                    if sitemap_urls:
                        print(f"📋 发现站点地图，包含 {len(sitemap_urls)} 个页面")
                        urls_to_crawl = sitemap_urls[:max_pages]
                    else:
                        print("🔍 未发现站点地图，使用智能爬取")
                        urls_to_crawl = await self._intelligent_crawl(page, base_url, max_pages)
                    
                    print(f"📝 开始抓取 {len(urls_to_crawl)} 个页面")
                    
                    # 抓取每个页面的内容
                    for i, url in enumerate(urls_to_crawl, 1):
                        if url not in self.visited_urls:
                            print(f"📄 抓取页面 {i}/{len(urls_to_crawl)}: {url}")
                            
                            await self._scrape_single_page(page, url)
                            self.visited_urls.add(url)
                            
                            # 页面间延迟
                            if self.config.pages_delay > 0:
                                await asyncio.sleep(self.config.pages_delay)
                    
                    await browser.close()
                    
                    # 组织和保存内容
                    result = await self._organize_scraped_content(base_url)
                    
                    if self.config.save_metadata:
                        await self._save_scraped_content(result, site_dir)
                    
                    return result
                    
                except Exception as e:
                    await browser.close()
                    raise e
                    
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "base_url": base_url,
                "scraped_at": datetime.now().isoformat()
            }
    
    async def _discover_sitemap(self, page, base_url: str) -> List[str]:
        """发现站点地图"""
        sitemap_urls = [
            urljoin(base_url, "sitemap.xml"),
            urljoin(base_url, "sitemap_index.xml"),
            urljoin(base_url, "robots.txt")
        ]
        
        all_urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = await page.goto(sitemap_url, timeout=self.config.pages_timeout * 1000)
                if response and response.status == 200:
                    content = await page.content()
                    
                    if sitemap_url.endswith('.xml'):
                        # 解析XML sitemap
                        urls = self._parse_xml_sitemap(content)
                        all_urls.extend(urls)
                    elif sitemap_url.endswith('robots.txt'):
                        # 从robots.txt中提取sitemap引用
                        sitemap_refs = self._extract_sitemaps_from_robots(content)
                        for sitemap_ref in sitemap_refs:
                            referenced_urls = await self._get_urls_from_sitemap(page, sitemap_ref)
                            all_urls.extend(referenced_urls)
                        
            except Exception as e:
                print(f"⚠️ 获取sitemap失败 {sitemap_url}: {e}")
        
        # 去重并过滤相关URL
        unique_urls = list(set(all_urls))
        filtered_urls = GitHubUtils.filter_urls(unique_urls, base_url)
        
        return filtered_urls
    
    def _parse_xml_sitemap(self, xml_content: str) -> List[str]:
        """解析XML格式的sitemap"""
        soup = BeautifulSoup(xml_content, 'xml')
        urls = []
        
        # 解析standard sitemap
        for url_tag in soup.find_all('url'):
            loc_tag = url_tag.find('loc')
            if loc_tag:
                urls.append(loc_tag.get_text().strip())
        
        # 解析sitemap index
        for sitemap_tag in soup.find_all('sitemap'):
            loc_tag = sitemap_tag.find('loc')
            if loc_tag:
                urls.append(loc_tag.get_text().strip())
        
        return urls
    
    def _extract_sitemaps_from_robots(self, robots_content: str) -> List[str]:
        """从robots.txt中提取sitemap引用"""
        sitemaps = []
        for line in robots_content.splitlines():
            line = line.strip()
            if line.lower().startswith('sitemap:'):
                sitemap_url = line.split(':', 1)[1].strip()
                sitemaps.append(sitemap_url)
        return sitemaps
    
    async def _get_urls_from_sitemap(self, page, sitemap_url: str) -> List[str]:
        """从引用的sitemap获取URL列表"""
        try:
            response = await page.goto(sitemap_url, timeout=self.config.pages_timeout * 1000)
            if response and response.status == 200:
                content = await page.content()
                return self._parse_xml_sitemap(content)
        except Exception as e:
            print(f"⚠️ 获取引用sitemap失败 {sitemap_url}: {e}")
        
        return []
    
    async def _intelligent_crawl(self, page, base_url: str, max_pages: int) -> List[str]:
        """智能爬取（当没有sitemap时）"""
        urls_to_crawl = [base_url]
        discovered_urls = set([base_url])
        
        await page.goto(base_url, timeout=self.config.pages_timeout * 1000)
        await page.wait_for_load_state("networkidle")
        
        # 分析页面结构，查找导航链接
        navigation_links = await self._extract_navigation_links(page, base_url)
        
        for link in navigation_links:
            if link not in discovered_urls and len(discovered_urls) < max_pages:
                discovered_urls.add(link)
                urls_to_crawl.append(link)
        
        return urls_to_crawl
    
    async def _extract_navigation_links(self, page, base_url: str) -> List[str]:
        """提取导航链接"""
        links = []
        
        # 常见的导航选择器
        nav_selectors = [
            'nav a[href]',
            '.sidebar a[href]',
            '.navigation a[href]',
            '.menu a[href]',
            '.toc a[href]',
            '.table-of-contents a[href]',
            '[role="navigation"] a[href]',
            '.docs-navigation a[href]',
            '.site-nav a[href]'
        ]
        
        for selector in nav_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    href = await element.get_attribute('href')
                    if href:
                        # 转换为绝对URL
                        if href.startswith('/'):
                            full_url = urljoin(base_url, href)
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        # 检查是否为相关URL
                        if GitHubUtils.get_url_domain(full_url) == GitHubUtils.get_url_domain(base_url):
                            links.append(full_url)
                            
            except Exception as e:
                print(f"⚠️ 提取导航链接失败 {selector}: {e}")
        
        return list(set(links))
    
    async def _scrape_single_page(self, page, url: str) -> Dict[str, Any]:
        """抓取单个页面内容"""
        try:
            response = await page.goto(url, 
                                     wait_until="networkidle", 
                                     timeout=self.config.pages_timeout * 1000)
            
            if not response or response.status != 200:
                error_data = {
                    "status": "error", 
                    "url": url, 
                    "error": f"HTTP {response.status if response else 'No response'}",
                    "extracted_at": datetime.now().isoformat()
                }
                self.extracted_content.append(error_data)
                return error_data
            
            # 等待页面完全加载
            await page.wait_for_load_state("networkidle")
            
            # 提取页面内容
            content_data = await self._extract_page_content(page, url)
            self.extracted_content.append(content_data)
            
            return content_data
            
        except Exception as e:
            error_data = {
                "status": "error", 
                "url": url, 
                "error": str(e),
                "extracted_at": datetime.now().isoformat()
            }
            self.extracted_content.append(error_data)
            return error_data
    
    async def _extract_page_content(self, page, url: str) -> Dict[str, Any]:
        """提取页面的核心内容"""
        try:
            # 获取页面基本信息
            title = await page.title()
            
            # 智能选择内容区域
            content_html = await self._extract_main_content(page)
            
            # 转换为Markdown
            if self.config.convert_to_markdown:
                markdown_content = self.h2t.handle(content_html)
            else:
                markdown_content = content_html
            
            # 提取元数据
            metadata = await self._extract_page_metadata(page)
            
            # 提取链接和图片
            page_url = page.url
            if self.config.extract_links:
                links = ContentExtractor.extract_links(content_html, page_url)
                metadata['links'] = links[:20]  # 限制数量
            
            if self.config.extract_images:
                images = ContentExtractor.extract_images(content_html, page_url)
                metadata['images'] = images[:10]  # 限制数量
            
            return {
                "status": "success",
                "url": url,
                "title": title,
                "content": markdown_content,
                "metadata": metadata,
                "extracted_at": datetime.now().isoformat(),
                "content_length": len(markdown_content),
                "word_count": len(markdown_content.split()) if markdown_content else 0
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "url": url, 
                "error": str(e),
                "extracted_at": datetime.now().isoformat()
            }
    
    async def _extract_main_content(self, page) -> str:
        """智能提取页面主要内容"""
        # 常见的内容选择器，按优先级排序
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '.page-content',
            '.documentation',
            '.docs-content',
            '.markdown-body',
            '#content',
            '.container .content',
            '.container main',
            'body'  # 最后的备选方案
        ]
        
        for selector in content_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    # 移除导航、侧边栏、页脚等无关内容
                    await self._clean_content_element(page, element)
                    content_html = await element.inner_html()
                    
                    # 检查内容质量
                    if self._is_quality_content(content_html):
                        return content_html
            except Exception:
                continue
        
        # 如果所有选择器都失败，返回空内容
        return ""
    
    async def _clean_content_element(self, page, element):
        """清理内容元素，移除无关部分"""
        # 要移除的选择器
        remove_selectors = [
            'nav', '.navigation', '.navbar', '.nav',
            '.sidebar', '.side-nav', '.menu',
            'header', 'footer', '.header', '.footer',
            '.advertisement', '.ads', '.ad',
            '.social-share', '.social-sharing',
            '.comments', '.comment', '.disqus',
            'script', 'style', 'noscript',
            '.breadcrumb', '.breadcrumbs',
            '.edit-page', '.edit-link',
            '.prev-next', '.pagination'
        ]
        
        for selector in remove_selectors:
            try:
                elements = await element.query_selector_all(selector)
                for el in elements:
                    await el.evaluate('el => el.remove()')
            except Exception:
                continue
    
    def _is_quality_content(self, html_content: str) -> bool:
        """判断内容质量"""
        if not html_content or len(html_content.strip()) < 100:
            return False
        
        # 转换为文本检查
        text_content = ContentExtractor.extract_text_content(html_content)
        
        # 基本质量检查
        if len(text_content) < 50:  # 太短
            return False
        
        # 检查是否有实际内容
        words = text_content.split()
        if len(words) < 10:  # 词语太少
            return False
        
        return True
    
    async def _extract_page_metadata(self, page) -> Dict[str, Any]:
        """提取页面元数据"""
        metadata = {}
        
        try:
            # 提取meta标签
            meta_tags = await page.query_selector_all('meta')
            for meta in meta_tags:
                name = await meta.get_attribute('name')
                property_attr = await meta.get_attribute('property')
                content = await meta.get_attribute('content')
                
                if (name or property_attr) and content:
                    key = name or property_attr
                    metadata[key] = content
            
            # 提取标题层次结构
            headings = []
            for i in range(1, 7):  # h1-h6
                heading_elements = await page.query_selector_all(f'h{i}')
                for heading in heading_elements[:10]:  # 限制数量
                    text = await heading.inner_text()
                    if text.strip():
                        headings.append({
                            "level": i,
                            "text": text.strip()
                        })
            
            metadata['headings'] = headings
            
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _organize_scraped_content(self, base_url: str) -> Dict[str, Any]:
        """组织抓取的内容"""
        successful_pages = [page for page in self.extracted_content if page.get("status") == "success"]
        failed_pages = [page for page in self.extracted_content if page.get("status") == "error"]
        
        # 统计信息
        total_words = sum(page.get("word_count", 0) for page in successful_pages)
        total_pages = len(successful_pages)
        
        # 构建内容层次结构
        content_structure = self._build_content_structure(successful_pages, base_url)
        
        return {
            "status": "success",
            "base_url": base_url,
            "scrape_summary": {
                "total_pages_found": len(self.extracted_content),
                "successful_pages": total_pages,
                "failed_pages": len(failed_pages),
                "total_words": total_words,
                "scraped_at": datetime.now().isoformat(),
                "config_used": self.config.to_dict()
            },
            "content_structure": content_structure,
            "pages": successful_pages,
            "errors": failed_pages if self.config.save_errors else []
        }
    
    def _build_content_structure(self, pages: List[Dict], base_url: str) -> Dict[str, Any]:
        """构建内容层次结构"""
        structure = {"pages": []}
        
        for page in pages:
            url = page["url"]
            relative_path = url.replace(base_url, "").strip("/")
            
            structure["pages"].append({
                "path": relative_path,
                "title": page["title"],
                "url": url,
                "word_count": page.get("word_count", 0),
                "content_length": page.get("content_length", 0)
            })
        
        # 按路径排序
        structure["pages"].sort(key=lambda x: x["path"])
        
        return structure
    
    async def _save_scraped_content(self, result: Dict[str, Any], site_dir: Path):
        """保存抓取的内容"""
        # 保存元数据
        metadata_file = site_dir / "metadata.json"
        GitHubUtils.save_json({
            "base_url": result["base_url"],
            "scrape_summary": result["scrape_summary"],
            "content_structure": result["content_structure"]
        }, metadata_file)
        
        # 保存每个页面的内容
        pages_dir = site_dir / "pages"
        pages_dir.mkdir(exist_ok=True)
        
        for i, page in enumerate(result["pages"]):
            if page.get("status") == "success":
                # 生成安全的文件名
                safe_title = GitHubUtils.sanitize_filename(page["title"], 50)
                filename = f"{i+1:03d}_{safe_title}.md"
                
                page_file = pages_dir / filename
                
                # 构建页面内容
                page_content = f"# {page['title']}\n\n"
                page_content += f"**URL**: {page['url']}\n"
                page_content += f"**抓取时间**: {page['extracted_at']}\n"
                page_content += f"**字数**: {page.get('word_count', 0)}\n\n"
                page_content += "---\n\n"
                page_content += page["content"]
                
                # 保存页面内容
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(page_content)
        
        # 保存错误报告
        if result.get("errors") and self.config.save_errors:
            errors_file = site_dir / "errors.json"
            GitHubUtils.save_json(result["errors"], errors_file)
        
        # 生成总结报告
        self._generate_summary_report(result, site_dir)
        
        print(f"📁 内容已保存到: {site_dir}")
        
        return {"status": "success", "output_dir": str(site_dir)}
    
    def _generate_summary_report(self, result: Dict[str, Any], site_dir: Path):
        """生成总结报告"""
        summary_file = site_dir / "README.md"
        
        base_url = result["base_url"]
        domain = GitHubUtils.get_url_domain(base_url)
        summary = result["scrape_summary"]
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {domain} 文档抓取报告\n\n")
            f.write(f"**站点URL**: {base_url}\n")
            f.write(f"**抓取时间**: {summary['scraped_at']}\n")
            f.write(f"**成功页面**: {summary['successful_pages']}\n")
            f.write(f"**失败页面**: {summary['failed_pages']}\n")
            f.write(f"**总字数**: {summary['total_words']:,}\n\n")
            
            f.write("## 配置信息\n\n")
            config = summary.get('config_used', {})
            f.write(f"- 最大页面数: {config.get('pages_max_pages', 'N/A')}\n")
            f.write(f"- 页面延迟: {config.get('pages_delay', 'N/A')}秒\n")
            f.write(f"- 转换为Markdown: {config.get('convert_to_markdown', 'N/A')}\n")
            f.write(f"- 提取链接: {config.get('extract_links', 'N/A')}\n")
            f.write(f"- 提取图片: {config.get('extract_images', 'N/A')}\n\n")
            
            f.write("## 页面列表\n\n")
            for page_info in result["content_structure"]["pages"]:
                f.write(f"- [{page_info['title']}]({page_info['url']}) ({page_info['word_count']} words)\n")
            
            if result.get("errors"):
                f.write(f"\n## 错误页面\n\n")
                f.write(f"共 {len(result['errors'])} 个页面抓取失败，详细信息请查看 `errors.json`\n")


# 便捷函数
async def scrape_github_pages(url: str, max_pages: int = 100, config: GitHubConfig = None) -> Dict[str, Any]:
    """
    便捷函数：抓取GitHub Pages站点
    
    Args:
        url: 站点URL
        max_pages: 最大抓取页面数
        config: 配置对象
        
    Returns:
        抓取结果
    """
    async with GitHubPagesScraper(config) as scraper:
        return await scraper.scrape_documentation_site(url, max_pages)


async def discover_github_pages(owner: str, repo: str = None, config: GitHubConfig = None) -> List[Dict[str, Any]]:
    """
    便捷函数：发现GitHub Pages站点
    
    Args:
        owner: GitHub用户名或组织名
        repo: 仓库名
        config: 配置对象
        
    Returns:
        发现的站点列表
    """
    async with GitHubPagesScraper(config) as scraper:
        return await scraper.discover_github_pages(owner, repo)

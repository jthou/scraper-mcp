"""GitHub Pages 文档站点抓取器"""
import asyncio
import re
import json
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import html2text


class GitHubPagesScraper:
    """GitHub Pages文档站点专用抓取器"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("K-Vault/GitHub-Pages")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = None
        self.visited_urls: Set[str] = set()
        self.extracted_content: List[Dict[str, Any]] = []
        
        # HTML到Markdown转换器配置
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # 不换行
        
        # 常见的文档生成器特征
        self.doc_generators = {
            "jekyll": ["_config.yml", ".jekyll-cache", "_site"],
            "docusaurus": ["docusaurus.config.js", ".docusaurus"],
            "gitbook": ["book.json", "_book"],
            "vuepress": [".vuepress", "vuepress.config.js"],
            "mkdocs": ["mkdocs.yml", "site"],
            "gatsby": ["gatsby-config.js", ".gatsby"],
            "next": ["next.config.js", ".next"],
            "nuxt": ["nuxt.config.js", ".nuxt"]
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def discover_github_pages(self, owner: str, repo: str = None) -> List[Dict[str, Any]]:
        """发现GitHub Pages站点"""
        discovered_sites = []
        
        if repo:
            # 单个仓库的Pages
            sites = await self._discover_single_repo_pages(owner, repo)
            discovered_sites.extend(sites)
        else:
            # 用户/组织的所有Pages
            sites = await self._discover_user_pages(owner)
            discovered_sites.extend(sites)
        
        return discovered_sites
    
    async def _discover_single_repo_pages(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """发现单个仓库的Pages站点"""
        possible_urls = [
            f"https://{owner}.github.io/{repo}/",
            f"https://{owner}.github.io/",  # 如果repo名是username.github.io
            f"https://{repo}.netlify.app/",
            f"https://{repo}.vercel.app/",
            f"https://{repo}.surge.sh/"
        ]
        
        # 检查自定义域名
        try:
            cname_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/CNAME"
            async with self.session.get(cname_url) as response:
                if response.status == 200:
                    cname = (await response.text()).strip()
                    possible_urls.append(f"https://{cname}/")
        except:
            pass
        
        valid_sites = []
        for url in possible_urls:
            site_info = await self._validate_pages_site(url, owner, repo)
            if site_info:
                valid_sites.append(site_info)
        
        return valid_sites
    
    async def _discover_user_pages(self, owner: str) -> List[Dict[str, Any]]:
        """发现用户/组织的所有Pages站点"""
        # 通过GitHub API获取用户的仓库列表
        # 这里先实现基础版本，后续可以集成GitHub API
        main_site_url = f"https://{owner}.github.io/"
        site_info = await self._validate_pages_site(main_site_url, owner, None)
        
        return [site_info] if site_info else []
    
    async def _validate_pages_site(self, url: str, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """验证Pages站点是否存在并获取基本信息"""
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # 检测文档生成器类型
                    generator = self._detect_generator(content, response.headers)
                    
                    return {
                        "url": url,
                        "owner": owner,
                        "repo": repo,
                        "status": "active",
                        "generator": generator,
                        "title": self._extract_title(content),
                        "description": self._extract_description(content),
                        "discovered_at": datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"验证站点失败 {url}: {e}")
        
        return None
    
    def _detect_generator(self, content: str, headers: Dict) -> str:
        """检测文档生成器类型"""
        content_lower = content.lower()
        
        # 通过meta标签检测
        if 'generator" content="jekyll' in content_lower:
            return "Jekyll"
        elif 'docusaurus' in content_lower:
            return "Docusaurus"
        elif 'gitbook' in content_lower:
            return "GitBook"
        elif 'vuepress' in content_lower:
            return "VuePress"
        elif 'mkdocs' in content_lower:
            return "MkDocs"
        elif 'gatsby' in content_lower:
            return "Gatsby"
        elif 'next.js' in content_lower or 'nextjs' in content_lower:
            return "Next.js"
        elif 'nuxt' in content_lower:
            return "Nuxt.js"
        
        # 通过服务器头部检测
        server = headers.get('server', '').lower()
        if 'github.com' in server:
            return "GitHub Pages"
        elif 'netlify' in server:
            return "Netlify"
        elif 'vercel' in server:
            return "Vercel"
        
        return "Unknown"
    
    def _extract_title(self, content: str) -> str:
        """提取页面标题"""
        soup = BeautifulSoup(content, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # 备选方案：查找h1标签
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Untitled"
    
    def _extract_description(self, content: str) -> str:
        """提取页面描述"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # 备选方案：查找第一个p标签
        p_tag = soup.find('p')
        if p_tag:
            text = p_tag.get_text().strip()
            return text[:200] + "..." if len(text) > 200 else text
        
        return ""
    
    async def scrape_documentation_site(self, base_url: str, max_pages: int = 100) -> Dict[str, Any]:
        """抓取完整的文档站点"""
        print(f"🕷️ 开始抓取文档站点: {base_url}")
        
        self.visited_urls.clear()
        self.extracted_content.clear()
        
        # 使用Playwright进行深度抓取
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 设置用户代理
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            try:
                # 首先发现站点地图
                sitemap_urls = await self._discover_sitemap(page, base_url)
                
                if sitemap_urls:
                    print(f"📋 发现站点地图，包含 {len(sitemap_urls)} 个页面")
                    urls_to_crawl = sitemap_urls[:max_pages]
                else:
                    print("🔍 未发现站点地图，使用智能爬取")
                    urls_to_crawl = await self._intelligent_crawl(page, base_url, max_pages)
                
                # 抓取每个页面的内容
                for i, url in enumerate(urls_to_crawl, 1):
                    if url not in self.visited_urls:
                        print(f"📄 抓取页面 {i}/{len(urls_to_crawl)}: {url}")
                        await self._scrape_single_page(page, url)
                        self.visited_urls.add(url)
                        
                        # 避免过快请求
                        await asyncio.sleep(0.5)
                
                await browser.close()
                
                # 组织和保存内容
                result = await self._organize_scraped_content(base_url)
                await self._save_scraped_content(result)
                
                return result
                
            except Exception as e:
                await browser.close()
                print(f"❌ 抓取失败: {e}")
                return {"status": "error", "error": str(e)}
    
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
                response = await page.goto(sitemap_url)
                if response and response.status == 200:
                    content = await page.content()
                    
                    if sitemap_url.endswith('.xml'):
                        # 解析XML sitemap
                        urls = self._parse_xml_sitemap(content)
                        all_urls.extend(urls)
                    elif sitemap_url.endswith('robots.txt'):
                        # 从robots.txt中提取sitemap
                        lines = content.split('\n')
                        for line in lines:
                            if line.lower().startswith('sitemap:'):
                                sitemap_ref = line.split(':', 1)[1].strip()
                                # 递归获取引用的sitemap
                                referenced_urls = await self._get_urls_from_sitemap(page, sitemap_ref)
                                all_urls.extend(referenced_urls)
                        
            except Exception as e:
                print(f"获取sitemap失败 {sitemap_url}: {e}")
        
        # 去重并过滤相关URL
        unique_urls = list(set(all_urls))
        filtered_urls = [url for url in unique_urls if self._is_relevant_url(url, base_url)]
        
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
    
    async def _get_urls_from_sitemap(self, page, sitemap_url: str) -> List[str]:
        """从引用的sitemap获取URL列表"""
        try:
            response = await page.goto(sitemap_url)
            if response and response.status == 200:
                content = await page.content()
                return self._parse_xml_sitemap(content)
        except Exception as e:
            print(f"获取引用sitemap失败 {sitemap_url}: {e}")
        
        return []
    
    def _is_relevant_url(self, url: str, base_url: str) -> bool:
        """判断URL是否与文档相关"""
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        
        # 必须是同一域名
        if base_domain != url_domain:
            return False
        
        # 排除非文档URL
        excluded_patterns = [
            r'/api/v\d+/',  # API endpoints
            r'\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf)$',  # 静态资源
            r'/admin/',     # 管理页面
            r'/login',      # 登录页面
            r'/logout',     # 登出页面
            r'#',           # 锚点链接
        ]
        
        for pattern in excluded_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    async def _intelligent_crawl(self, page, base_url: str, max_pages: int) -> List[str]:
        """智能爬取（当没有sitemap时）"""
        urls_to_crawl = [base_url]
        discovered_urls = set([base_url])
        
        await page.goto(base_url)
        
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
            'nav a',
            '.sidebar a',
            '.navigation a',
            '.menu a',
            '.toc a',
            '.table-of-contents a',
            '[role="navigation"] a'
        ]
        
        for selector in nav_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    href = await element.get_attribute('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if self._is_relevant_url(full_url, base_url):
                            links.append(full_url)
            except Exception as e:
                print(f"提取导航链接失败 {selector}: {e}")
        
        return list(set(links))
    
    async def _scrape_single_page(self, page, url: str) -> Dict[str, Any]:
        """抓取单个页面内容"""
        try:
            response = await page.goto(url, wait_until="networkidle")
            if not response or response.status != 200:
                return {"status": "error", "url": url, "error": f"HTTP {response.status if response else 'No response'}"}
            
            # 等待页面完全加载
            await page.wait_for_load_state("networkidle")
            
            # 提取页面内容
            content_data = await self._extract_page_content(page, url)
            self.extracted_content.append(content_data)
            
            return content_data
            
        except Exception as e:
            error_data = {"status": "error", "url": url, "error": str(e)}
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
            markdown_content = self.h2t.handle(content_html)
            
            # 提取元数据
            metadata = await self._extract_page_metadata(page)
            
            return {
                "status": "success",
                "url": url,
                "title": title,
                "content": markdown_content,
                "metadata": metadata,
                "extracted_at": datetime.now().isoformat(),
                "content_length": len(markdown_content),
                "word_count": len(markdown_content.split())
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
            '#content',
            '.container .row .col',  # Bootstrap布局
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
        
        # 如果所有选择器都失败，返回body内容
        try:
            body = await page.query_selector('body')
            if body:
                await self._clean_content_element(page, body)
                return await body.inner_html()
        except Exception:
            pass
        
        return ""
    
    async def _clean_content_element(self, page, element):
        """清理内容元素，移除无关部分"""
        # 要移除的选择器
        remove_selectors = [
            'nav',
            '.navigation',
            '.navbar',
            '.sidebar',
            '.menu',
            'header',
            'footer',
            '.header',
            '.footer',
            '.advertisement',
            '.ads',
            '.social-share',
            '.comments',
            '.comment',
            'script',
            'style',
            '.breadcrumb'
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
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text().strip()
        
        # 基本质量检查
        if len(text) < 50:  # 太短
            return False
        
        # 检查是否有实际内容
        words = text.split()
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
                
                if name and content:
                    metadata[name] = content
                elif property_attr and content:
                    metadata[property_attr] = content
            
            # 提取标题层次结构
            headings = []
            for i in range(1, 7):  # h1-h6
                heading_elements = await page.query_selector_all(f'h{i}')
                for heading in heading_elements:
                    text = await heading.inner_text()
                    if text.strip():
                        headings.append({
                            "level": i,
                            "text": text.strip()
                        })
            
            metadata['headings'] = headings
            
            # 提取链接信息
            links = []
            link_elements = await page.query_selector_all('a[href]')
            for link in link_elements[:20]:  # 限制数量
                href = await link.get_attribute('href')
                text = await link.inner_text()
                if href and text.strip():
                    links.append({
                        "href": href,
                        "text": text.strip()
                    })
            
            metadata['links'] = links
            
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
            "base_url": base_url,
            "scrape_summary": {
                "total_pages_found": len(self.extracted_content),
                "successful_pages": total_pages,
                "failed_pages": len(failed_pages),
                "total_words": total_words,
                "scraped_at": datetime.now().isoformat()
            },
            "content_structure": content_structure,
            "pages": successful_pages,
            "errors": failed_pages
        }
    
    def _build_content_structure(self, pages: List[Dict], base_url: str) -> Dict[str, Any]:
        """构建内容层次结构"""
        # 简单的URL-based结构
        structure = {"pages": []}
        
        for page in pages:
            url = page["url"]
            relative_path = url.replace(base_url, "").strip("/")
            
            structure["pages"].append({
                "path": relative_path,
                "title": page["title"],
                "url": url,
                "word_count": page.get("word_count", 0)
            })
        
        # 按路径排序
        structure["pages"].sort(key=lambda x: x["path"])
        
        return structure
    
    async def _save_scraped_content(self, result: Dict[str, Any]):
        """保存抓取的内容"""
        base_url = result["base_url"]
        domain = urlparse(base_url).netloc
        
        # 创建输出目录
        site_dir = self.output_dir / domain
        site_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存元数据
        metadata_file = site_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "base_url": result["base_url"],
                "scrape_summary": result["scrape_summary"],
                "content_structure": result["content_structure"]
            }, f, indent=2, ensure_ascii=False)
        
        # 保存每个页面的内容
        pages_dir = site_dir / "pages"
        pages_dir.mkdir(exist_ok=True)
        
        for i, page in enumerate(result["pages"]):
            if page.get("status") == "success":
                # 生成安全的文件名
                safe_title = re.sub(r'[^\w\s-]', '', page["title"])[:50]
                filename = f"{i+1:03d}_{safe_title}.md"
                
                page_file = pages_dir / filename
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {page['title']}\n\n")
                    f.write(f"**URL**: {page['url']}\n")
                    f.write(f"**抓取时间**: {page['extracted_at']}\n")
                    f.write(f"**字数**: {page.get('word_count', 0)}\n\n")
                    f.write("---\n\n")
                    f.write(page["content"])
        
        # 保存错误报告
        if result.get("errors"):
            errors_file = site_dir / "errors.json"
            with open(errors_file, 'w', encoding='utf-8') as f:
                json.dump(result["errors"], f, indent=2, ensure_ascii=False)
        
        # 生成总结报告
        summary_file = site_dir / "README.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {domain} 文档抓取报告\n\n")
            f.write(f"**站点URL**: {base_url}\n")
            f.write(f"**抓取时间**: {result['scrape_summary']['scraped_at']}\n")
            f.write(f"**成功页面**: {result['scrape_summary']['successful_pages']}\n")
            f.write(f"**失败页面**: {result['scrape_summary']['failed_pages']}\n")
            f.write(f"**总字数**: {result['scrape_summary']['total_words']:,}\n\n")
            
            f.write("## 页面列表\n\n")
            for page_info in result["content_structure"]["pages"]:
                f.write(f"- [{page_info['title']}]({page_info['url']}) ({page_info['word_count']} words)\n")
        
        print(f"📁 内容已保存到: {site_dir}")
        
        return {"status": "success", "output_dir": str(site_dir)}


# 使用示例和测试函数
async def test_github_pages_scraper():
    """测试GitHubPagesScraper"""
    async with GitHubPagesScraper() as scraper:
        # 测试发现GitHub Pages
        print("🔍 测试发现GitHub Pages...")
        sites = await scraper.discover_github_pages("facebook", "react")
        print(f"发现的站点: {sites}")
        
        # 测试抓取文档站点
        if sites:
            print(f"📚 测试抓取文档站点...")
            result = await scraper.scrape_documentation_site(sites[0]["url"], max_pages=5)
            print(f"抓取结果: {result['scrape_summary']}")


if __name__ == "__main__":
    asyncio.run(test_github_pages_scraper())

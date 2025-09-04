"""网页抓取模块"""
import asyncio
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright 未安装，正在自动安装...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.async_api import async_playwright


class WebScraper:
    """最基础的网页抓取类"""
    
    def __init__(self):
        self.name = "WebScraper"
        self.playwright = None
        self.zhihu_context = None
        self.zhihu_page = None
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接方法 - 最基础的功能"""
        return {
            "status": "success",
            "message": f"{self.name} 模块已初始化",
            "module": self.name
        }
    
    async def setup_browser(self, headless: bool = False, persistent: bool = False) -> Dict[str, Any]:
        """设置浏览器环境"""
        try:
            self.playwright = await async_playwright().start()
            
            # 使用系统Chrome浏览器
            browser = await self.playwright.chromium.launch(
                channel="chrome",  # 使用系统Chrome
                headless=headless,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            )
            
            if persistent:
                # 持久化模式：创建持久化上下文
                self.zhihu_context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                self.zhihu_page = await self.zhihu_context.new_page()
            else:
                # 非持久化模式：创建临时上下文
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                self.zhihu_page = await context.new_page()
            
            return {
                "status": "success",
                "message": "浏览器设置成功",
                "headless": headless,
                "persistent": persistent
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"浏览器设置失败: {str(e)}"
            }
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.zhihu_page:
                await self.zhihu_page.close()
            if self.zhihu_context:
                await self.zhihu_context.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"资源清理失败: {e}")
    
    async def get_page_info(self, url: str) -> Dict[str, Any]:
        """获取页面信息 - 最基础的功能"""
        return {
            "url": url,
            "status": "not_implemented",
            "message": "基础功能，待实现"
        }
    
    async def open_webpage(self, url: str, headless: bool = False) -> Dict[str, Any]:
        """使用系统Chrome打开指定网页"""
        try:
            async with async_playwright() as p:
                # 使用系统Chrome浏览器
                browser = await p.chromium.launch(
                    channel="chrome",  # 使用系统Chrome
                    headless=headless,  # 可配置是否显示窗口
                    args=[
                        "--start-maximized",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
                
                # 创建新页面
                page = await browser.new_page()
                
                # 设置视口大小
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                # 访问指定网页
                await page.goto(url)
                
                # 等待页面加载完成
                await page.wait_for_load_state("networkidle")
                
                # 返回成功结果
                return {
                    "status": "success",
                    "message": f"成功打开网页: {url}",
                    "url": url,
                    "browser_type": "system_chrome",
                    "headless": headless
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"打开网页失败: {str(e)}",
                "url": url,
                "error": str(e)
            }
    
    async def login_zhihu(self, headless: bool = False) -> Dict[str, Any]:
        """登录知乎网站，保持登录状态"""
        try:
            from pathlib import Path
            
            # 创建用户数据目录保存登录状态
            user_data_dir = Path(__file__).parent.parent.parent / "data" / "browser_data" / "zhihu_stealth"
            user_data_dir.mkdir(parents=True, exist_ok=True)
            
            # 如果还没有playwright实例，创建一个
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            # 使用launch_persistent_context保存登录状态，添加完整的反爬虫参数
            self.zhihu_context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                channel="chrome",
                headless=headless,
                timeout=60000,  # 增加超时时间到60秒
                args=[
                    "--start-maximized",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-ipc-flooding-protection",
                    "--disable-renderer-backgrounding",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-client-side-phishing-detection",
                    "--disable-sync",
                    "--disable-default-apps",
                    "--disable-extensions",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                    "--disable-background-timer-throttling",
                    "--disable-background-networking",
                    "--disable-breakpad",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-domain-reliability",
                    "--disable-features=TranslateUI",
                    "--disable-hang-monitor",
                    "--disable-prompt-on-repost",
                    "--disable-sync-preferences",
                    "--disable-web-resources",
                    "--enable-features=NetworkService,NetworkServiceLogging",
                    "--force-color-profile=srgb",
                    "--metrics-recording-only",
                    "--safebrowsing-disable-auto-update",
                    "--enable-automation",
                    "--password-store=basic",
                    "--use-mock-keychain"
                ]
            )
            
            self.zhihu_page = self.zhihu_context.pages[0] if self.zhihu_context.pages else await self.zhihu_context.new_page()
            
            # 设置真实的用户代理和完整的HTTP头
            await self.zhihu_page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            })
            
            # 设置视口大小
            await self.zhihu_page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 访问知乎，增加超时时间
            await self.zhihu_page.goto("https://www.zhihu.com", timeout=60000)
            await self.zhihu_page.wait_for_load_state("networkidle", timeout=60000)
            
            # 模拟人类行为 - 随机等待
            import random
            await self.zhihu_page.wait_for_timeout(random.randint(1000, 3000))
            
            # 检测登录状态
            login_status = await self._detect_zhihu_login_status(self.zhihu_page)
            
            if login_status == "logged_in":
                # 保持浏览器打开
                return {
                    "status": "success",
                    "message": "知乎已登录",
                    "login_status": login_status,
                    "user_data_dir": str(user_data_dir)
                }
            elif login_status == "waiting_for_login":
                # 保持浏览器打开，等待用户登录
                return {
                    "status": "waiting",
                    "message": "请在浏览器中手动扫码登录",
                    "login_status": login_status,
                    "user_data_dir": str(user_data_dir)
                }
            else:
                await self.zhihu_context.close()
                return {
                    "status": "error",
                    "message": f"登录状态异常: {login_status}",
                    "login_status": login_status,
                    "user_data_dir": str(user_data_dir)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"知乎登录失败: {str(e)}",
                "error": str(e)
            }
    
    async def _detect_zhihu_login_status(self, page) -> str:
        """检测知乎登录状态"""
        try:
            # 等待页面加载
            await page.wait_for_load_state("networkidle")
            
            # 等待一下让页面完全加载
            await page.wait_for_timeout(5000)
            
            # 检查是否已登录
            if await self._is_zhihu_logged_in(page):
                return "logged_in"
            
            # 检查是否在登录页面
            if await self._is_on_zhihu_login_page(page):
                return "on_login_page"
            
            # 检查是否有扫码登录
            if await self._has_zhihu_qr_login(page):
                return "waiting_for_login"
            
            # 如果都没有检测到，可能是需要手动登录
            return "waiting_for_login"
            
        except Exception as e:
            self.logger.error(f"检测知乎登录状态失败: {e}")
            return "error"
    
    async def _is_zhihu_logged_in(self, page) -> bool:
        """检查知乎是否已登录"""
        try:
            # 等待页面加载
            await page.wait_for_load_state("networkidle")
            
            # 检查多种登录标识
            # 1. 检查用户头像
            avatar = await page.query_selector('img[alt*="头像"], img[alt*="avatar"], .Avatar')
            if avatar:
                return True
            
            # 2. 检查用户名链接
            username = await page.query_selector('a[href*="/people/"], .UserLink, .AppHeader-userInfo')
            if username:
                return True
            
            # 3. 检查登录按钮是否存在（如果存在说明未登录）
            login_button = await page.query_selector('button:has-text("登录"), .SignFlow-tab:has-text("登录")')
            if login_button:
                return False
            
            # 4. 检查是否有用户菜单
            user_menu = await page.query_selector('.AppHeader-userInfo, .UserAvatar')
            if user_menu:
                return True
            
            # 5. 检查页面标题是否包含登录信息
            title = await page.title()
            if "登录" in title or "login" in title.lower():
                return False
            
            return False
        except Exception as e:
            self.logger.error(f"检查登录状态时出错: {e}")
            return False
    
    async def _is_on_zhihu_login_page(self, page) -> bool:
        """检查是否在知乎登录页面"""
        try:
            title = await page.title()
            url = page.url
            
            if "登录" in title or "login" in title.lower() or "/login" in url:
                return True
            return False
        except:
            return False
    
    async def _has_zhihu_qr_login(self, page) -> bool:
        """检查知乎是否有扫码登录选项"""
        try:
            qr_button = await page.query_selector('button:has-text("扫码登录"), .qr-login, [data-testid*="qr"]')
            if qr_button:
                return True
            return False
        except:
            return False
    

    
    async def read_zhihu_page(self, url: str = "https://www.zhihu.com") -> Dict[str, Any]:
        """读取知乎网页内容（需要已登录）- 使用PDF转Markdown方法"""
        try:
            # 检查是否有已打开的知乎浏览器
            if not self.zhihu_context or not self.zhihu_page:
                return {
                    "status": "error",
                    "message": "知乎未登录，请先登录"
                }
            
            # 使用已打开的浏览器访问指定页面
            await self.zhihu_page.goto(url)
            await self.zhihu_page.wait_for_load_state("networkidle")
            
            # 模拟人类行为 - 随机等待
            import random
            await self.zhihu_page.wait_for_timeout(random.randint(2000, 5000))
            
            # 模拟鼠标移动
            await self.zhihu_page.mouse.move(random.randint(100, 800), random.randint(100, 600))
            
            # 再次等待
            await self.zhihu_page.wait_for_timeout(random.randint(1000, 2000))
            
            # 简化登录状态检测 - 如果页面能正常加载，就认为已登录
            current_url = self.zhihu_page.url
            if "login" in current_url.lower() or "signin" in current_url.lower():
                return {
                    "status": "error",
                    "message": "知乎未登录，请先登录"
                }
            
            # 获取页面标题
            title = await self.zhihu_page.title()
            
            # 使用PDF转Markdown方法
            pdf_result = await self.print_page_to_pdf(url)
            if pdf_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"PDF打印失败: {pdf_result['message']}",
                    "url": url
                }
            
            markdown_result = await self.pdf_to_markdown(pdf_result['pdf_path'])
            if markdown_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"PDF转Markdown失败: {markdown_result['message']}",
                    "url": url,
                    "pdf_path": pdf_result['pdf_path']
                }
            
            return {
                "status": "success",
                "message": "成功读取知乎页面内容",
                "url": url,
                "title": title,
                "method_used": "pdf_to_markdown",
                "text_content": markdown_result['markdown_content'],
                "pdf_path": pdf_result['pdf_path'],
                "text_length": markdown_result['text_length']
            }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"读取知乎页面失败: {str(e)}",
                "error": str(e)
            }
    

    
    async def print_page_to_pdf(self, url: str = "https://www.zhihu.com", output_path: str = None) -> Dict[str, Any]:
        """将知乎页面打印成PDF"""
        try:
            # 检查是否有已打开的知乎浏览器
            if not self.zhihu_context or not self.zhihu_page:
                return {
                    "status": "error",
                    "message": "知乎未登录，请先登录"
                }
            
            # 使用已打开的浏览器访问指定页面
            await self.zhihu_page.goto(url)
            await self.zhihu_page.wait_for_load_state("networkidle")
            
            # 模拟人类行为 - 随机等待
            import random
            await self.zhihu_page.wait_for_timeout(random.randint(2000, 5000))
            
            # 生成PDF文件路径
            from pathlib import Path
            if output_path:
                pdf_path = Path(output_path)
            else:
                pdf_path = Path(__file__).parent.parent.parent / "data" / "pdfs" / f"zhihu_{int(asyncio.get_event_loop().time())}.pdf"
            
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用浏览器打印功能生成PDF
            await self.zhihu_page.pdf(
                path=str(pdf_path),
                format='A4',
                print_background=True,
                margin={
                    'top': '1cm',
                    'right': '1cm',
                    'bottom': '1cm',
                    'left': '1cm'
                }
            )
            
            return {
                "status": "success",
                "message": "成功将页面打印成PDF",
                "url": url,
                "pdf_path": str(pdf_path)
            }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"PDF打印失败: {str(e)}",
                "error": str(e)
            }
    
    async def pdf_to_markdown(self, pdf_path: str) -> Dict[str, Any]:
        """将PDF转换为Markdown"""
        try:
            import PyPDF2
            import re
            
            # 读取PDF文件
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 提取所有页面的文本
                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
            
            if not text_content.strip():
                return {
                    "status": "error",
                    "message": "PDF中没有提取到文字内容"
                }
            
            # 清理和格式化文本
            lines = text_content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 移除多余的空白字符
                line = re.sub(r'\s+', ' ', line)
                
                # 检测可能的标题（通常是大写字母开头或包含特定关键词）
                if (len(line) > 10 and 
                    (line[0].isupper() or 
                     '：' in line or ':' in line or
                     '问题' in line or '回答' in line or
                     '作者' in line or '时间' in line)):
                    cleaned_lines.append(f"## {line}")
                else:
                    cleaned_lines.append(line)
            
            # 生成Markdown内容
            markdown_content = "\n\n".join(cleaned_lines)
            
            return {
                "status": "success",
                "message": "成功将PDF转换为Markdown",
                "pdf_path": pdf_path,
                "text_length": len(text_content),
                "markdown_content": markdown_content
            }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"PDF转Markdown失败: {str(e)}",
                "error": str(e)
            }
    
    async def search_zhihu(self, query: str, max_pages: int = 3, min_relevance: float = 0.5) -> Dict[str, Any]:
        """搜索知乎内容"""
        try:
            # 检查是否已登录
            if not self.zhihu_context or not self.zhihu_page:
                return {
                    "status": "error",
                    "message": "知乎未登录，请先登录"
                }
            
            # 构建搜索URL
            search_url = f"https://www.zhihu.com/search?q={query}&type=content"
            
            # 访问搜索页面，增加超时时间
            await self.zhihu_page.goto(search_url, timeout=90000)
            await self.zhihu_page.wait_for_load_state("networkidle", timeout=90000)
            
            # 等待搜索结果加载
            await self.zhihu_page.wait_for_timeout(3000)
            
            # 获取搜索结果
            results = await self._extract_search_results()
            
            # 自动翻页获取更多结果
            all_results = results.copy()
            for page in range(2, max_pages + 1):
                next_page_results = await self._get_next_page_results(page)
                if next_page_results:
                    all_results.extend(next_page_results)
                else:
                    break
            
            # 评判相关性
            filtered_results = await self._filter_by_relevance(all_results, query, min_relevance)
            
            # 提取所有符合条件的页面链接
            qualified_links = [result["url"] for result in filtered_results if result["url"]]
            
            return {
                "status": "success",
                "message": f"搜索完成，共找到{len(all_results)}个结果，过滤后{len(filtered_results)}个符合要求",
                "query": query,
                "total_results": len(all_results),
                "filtered_results": len(filtered_results),
                "qualified_links": qualified_links,
                "results": filtered_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索失败: {str(e)}",
                "error": str(e)
            }
    
    async def _extract_search_results(self) -> List[Dict[str, Any]]:
        """提取搜索结果"""
        try:
            # 首先滚动页面多次，确保所有内容加载
            for _ in range(5):  # 滚动5次
                await self.zhihu_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.zhihu_page.wait_for_timeout(1000)  # 等待内容加载
            
            # 等待搜索结果加载 - 尝试多种可能的选择器
            selectors_to_try = [
                ".SearchResult-item",
                ".List-item",
                ".ContentItem",
                "[data-za-detail-view-element_name='SearchResult']",
                ".SearchResult"
            ]
            
            result_items = []
            for selector in selectors_to_try:
                try:
                    await self.zhihu_page.wait_for_selector(selector, timeout=5000)
                    result_items = await self.zhihu_page.query_selector_all(selector)
                    if result_items:
                        break
                except:
                    continue
            
            if not result_items:
                return []
            
            results = []
            for item in result_items:
                try:
                    # 提取标题和链接 - 尝试多种可能的选择器
                    title_element = None
                    title_selectors = [
                        ".ContentItem-title a",
                        "h2 a",
                        ".title a",
                        "a[href*='/question/']",
                        "a[href*='/p/']"
                    ]
                    
                    for selector in title_selectors:
                        title_element = await item.query_selector(selector)
                        if title_element:
                            break
                    
                    if not title_element:
                        continue
                    
                    title = await title_element.inner_text()
                    href = await title_element.get_attribute("href")
                    
                    # 处理相对链接
                    if href and not href.startswith("http"):
                        if href.startswith("//"):
                            href = f"https:{href}"
                        elif href.startswith("/"):
                            href = f"https://www.zhihu.com{href}"
                        else:
                            href = f"https://www.zhihu.com/{href}"
                    
                    # 提取摘要 - 尝试多种可能的选择器
                    summary_element = None
                    summary_selectors = [
                        ".RichText",
                        ".content",
                        ".summary",
                        ".excerpt"
                    ]
                    
                    for selector in summary_selectors:
                        summary_element = await item.query_selector(selector)
                        if summary_element:
                            break
                    
                    summary = ""
                    if summary_element:
                        summary = await summary_element.inner_text()
                        summary = summary.strip()[:200] + "..." if len(summary) > 200 else summary
                    
                    # 提取作者信息 - 尝试多种可能的选择器
                    author_element = None
                    author_selectors = [
                        ".AuthorInfo-name",
                        ".author",
                        ".user-name",
                        ".username"
                    ]
                    
                    for selector in author_selectors:
                        author_element = await item.query_selector(selector)
                        if author_element:
                            break
                    
                    author = ""
                    if author_element:
                        author = await author_element.inner_text()
                    
                    # 提取点赞数 - 尝试多种可能的选择器
                    vote_element = None
                    vote_selectors = [
                        ".VoteButton--up",
                        ".vote-count",
                        ".like-count",
                        ".upvote"
                    ]
                    
                    for selector in vote_selectors:
                        vote_element = await item.query_selector(selector)
                        if vote_element:
                            break
                    
                    vote_count = 0
                    if vote_element:
                        vote_text = await vote_element.inner_text()
                        vote_count = self._extract_number(vote_text)
                    
                    result = {
                        "title": title.strip(),
                        "url": href,
                        "summary": summary,
                        "author": author.strip(),
                        "vote_count": vote_count,
                        "relevance_score": 0.0  # 初始相关性分数
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            return []
    
    async def _get_next_page_results(self, page: int) -> List[Dict[str, Any]]:
        """获取下一页结果"""
        try:
            # 多次滚动页面，确保所有内容加载完全
            for _ in range(5):
                await self.zhihu_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.zhihu_page.wait_for_timeout(1000)
            
            # 查找并点击"下一页"按钮
            next_buttons = await self.zhihu_page.query_selector_all(".PaginationButton")
            for button in next_buttons:
                text = await button.inner_text()
                if str(page) == text.strip():
                    # 点击对应页码的按钮
                    await button.click()
                    await self.zhihu_page.wait_for_timeout(3000)
                    
                    # 再次滚动新页面
                    for _ in range(5):
                        await self.zhihu_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await self.zhihu_page.wait_for_timeout(1000)
                    
                    # 提取新加载的结果
                    return await self._extract_search_results()
            
            # 如果没有找到页码按钮，尝试"下一页"按钮
            next_button = await self.zhihu_page.query_selector(".Pagination-next:not(.Pagination-disabled)")
            if next_button:
                await next_button.click()
                await self.zhihu_page.wait_for_timeout(3000)
                
                # 再次滚动新页面
                for _ in range(5):
                    await self.zhihu_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await self.zhihu_page.wait_for_timeout(1000)
                
                return await self._extract_search_results()
            
            # 尝试"加载更多"按钮
            load_more_button = await self.zhihu_page.query_selector(".List-item button")
            if load_more_button:
                await load_more_button.click()
                await self.zhihu_page.wait_for_timeout(3000)
                return await self._extract_search_results()
            
            return []
            
        except Exception as e:
            print(f"获取下一页结果失败: {e}")
            return []
    
    async def _filter_by_relevance(self, results: List[Dict[str, Any]], query: str, min_relevance: float = 0.5) -> List[Dict[str, Any]]:
        """根据相关性过滤结果"""
        try:
            import re
            query_words = set(re.findall(r'\w+', query.lower()))
            
            for result in results:
                # 计算相关性分数
                relevance_score = self._calculate_relevance(result, query_words)
                result["relevance_score"] = relevance_score
            
            # 按相关性分数排序
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # 过滤相关性低于阈值的结果
            filtered_results = [r for r in results if r["relevance_score"] >= min_relevance]
            
            return filtered_results
            
        except Exception as e:
            return results
    
    def _calculate_relevance(self, result: Dict[str, Any], query_words: set) -> float:
        """计算相关性分数"""
        try:
            import re
            title = result.get("title", "").lower()
            summary = result.get("summary", "").lower()
            author = result.get("author", "").lower()
            
            # 计算标题匹配度
            title_words = set(re.findall(r'\w+', title))
            title_match = len(query_words.intersection(title_words)) / len(query_words) if query_words else 0
            
            # 计算摘要匹配度
            summary_words = set(re.findall(r'\w+', summary))
            summary_match = len(query_words.intersection(summary_words)) / len(query_words) if query_words else 0
            
            # 计算作者匹配度（权重较低）
            author_words = set(re.findall(r'\w+', author))
            author_match = len(query_words.intersection(author_words)) / len(query_words) if query_words else 0
            
            # 综合评分（标题权重最高，摘要次之，作者最低）
            relevance_score = (
                title_match * 0.6 +      # 标题匹配权重60%
                summary_match * 0.3 +    # 摘要匹配权重30%
                author_match * 0.1       # 作者匹配权重10%
            )
            
            return min(relevance_score, 1.0)  # 确保分数不超过1.0
            
        except Exception as e:
            return 0.0
    
    def _extract_number(self, text: str) -> int:
        """从文本中提取数字"""
        try:
            import re
            # 处理中文数字单位
            text = text.replace("万", "0000").replace("千", "000")
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 0
        except:
            return 0

    def clean_filename(self, title: str) -> str:
        """清理文件名，移除不合法字符并处理长度限制"""
        if not title:
            return "untitled"
        
        # 1. 移除特殊字符: < > : " / \ | ? *
        title = re.sub(r'[<>:"/\\|?*]', '_', title)
        
        # 2. 替换多个空格为单个下划线
        title = re.sub(r'\s+', '_', title)
        
        # 3. 移除中文标点符号并替换为下划线
        title = re.sub(r'[，。！？；：""''【】《》（）]', '_', title)
        
        # 4. 移除连续的下划线
        title = re.sub(r'_+', '_', title)
        
        # 5. 移除首尾的下划线和点
        title = title.strip('_.')
        
        # 6. 限制文件名长度 (≤100字符)
        if len(title) > 100:
            title = title[:97] + "..."
        
        # 7. 如果清理后为空，使用默认名称
        if not title:
            title = "untitled"
            
        return title
    
    def _generate_unique_filename(self, base_name: str, extension: str, output_dir: Path) -> str:
        """生成唯一的文件名，处理重复文件名"""
        file_path = output_dir / f"{base_name}{extension}"
        
        if not file_path.exists():
            return f"{base_name}{extension}"
        
        # 如果文件已存在，添加序号
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}{extension}"
            new_path = output_dir / new_name
            if not new_path.exists():
                return new_name
            counter += 1
    
    async def download_and_save_content(self, url: str, output_dir: Path, title: Optional[str] = None) -> Dict[str, Any]:
        """下载知乎内容并保存为PDF和Markdown文件"""
        try:
            # 1. 确保输出目录存在
            pdf_dir = output_dir / "pdfs"
            markdown_dir = output_dir / "markdown"
            pdf_dir.mkdir(parents=True, exist_ok=True)
            markdown_dir.mkdir(parents=True, exist_ok=True)
            
            # 2. 直接生成PDF到目标位置
            # 先确定文件名
            page_result = await self.read_zhihu_page(url)
            page_title = ""
            if page_result["status"] == "success":
                page_title = page_result.get("title", "")
            
            # 使用提供的标题或页面标题
            final_title = title if title else page_title
            if not final_title:
                final_title = f"zhihu_content_{int(datetime.now().timestamp())}"
            
            # 清理文件名
            clean_title = self.clean_filename(final_title)
            
            # 生成唯一文件名
            pdf_filename = self._generate_unique_filename(clean_title, ".pdf", pdf_dir)
            markdown_filename = self._generate_unique_filename(clean_title, ".md", markdown_dir)
            
            # 确保PDF和Markdown使用相同的基础名称
            base_name = pdf_filename.replace(".pdf", "")
            markdown_filename = f"{base_name}.md"
            
            # 直接生成PDF到目标位置
            target_pdf_path = pdf_dir / pdf_filename
            pdf_result = await self.print_page_to_pdf(url, str(target_pdf_path))
            if pdf_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"PDF生成失败: {pdf_result['message']}"
                }
            
            # 验证PDF文件是否真正创建
            if not target_pdf_path.exists():
                return {
                    "status": "error",
                    "message": f"PDF文件创建失败: {target_pdf_path}"
                }
            
            # 使用生成的PDF转换为Markdown
            markdown_result = await self.pdf_to_markdown(str(target_pdf_path))
            if markdown_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"内容提取失败: {markdown_result['message']}"
                }
            
            # 保存Markdown文件
            markdown_content = f"""# {final_title}

**来源**: {url}
**保存时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{markdown_result['markdown_content']}
"""
            
            markdown_path = markdown_dir / markdown_filename
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # 更新文件映射
            mapping_file = output_dir / "file_mapping.json"
            mapping_data = {}
            
            if mapping_file.exists():
                try:
                    with open(mapping_file, 'r', encoding='utf-8') as f:
                        mapping_data = json.load(f)
                except:
                    mapping_data = {}
            
            mapping_data[base_name] = {
                "original_title": final_title,
                "clean_title": clean_title,
                "url": url,
                "pdf_file": f"pdfs/{pdf_filename}",
                "markdown_file": f"markdown/{markdown_filename}",
                "download_time": datetime.now().isoformat()
            }
            
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "message": f"内容保存成功: {final_title}",
                "clean_title": clean_title,
                "base_name": base_name,
                "files": {
                    "pdf": str(target_pdf_path),
                    "markdown": str(markdown_path),
                    "mapping": str(mapping_file)
                },
                "url": url,
                "original_title": final_title
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"保存内容失败: {str(e)}",
                "url": url,
                "error": str(e)
            }
    
    async def batch_download_content(self, query: str, output_dir: Path, max_pages: int = 3, min_relevance: float = 0.5) -> Dict[str, Any]:
        """批量下载知乎搜索结果"""
        try:
            # 1. 搜索内容
            search_result = await self.search_zhihu(query, max_pages, min_relevance)
            
            if search_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"搜索失败: {search_result['message']}"
                }
            
            results = search_result.get("results", [])
            if not results:
                return {
                    "status": "error",
                    "message": "没有找到符合条件的结果"
                }
            
            # 2. 批量下载
            success_count = 0
            failed_count = 0
            download_results = []
            
            for i, article in enumerate(results, 1):
                url = article.get("url", "")
                title = article.get("title", "")
                
                if not url:
                    failed_count += 1
                    continue
                
                print(f"下载第 {i}/{len(results)} 篇: {title}")
                
                # 下载单篇文章
                download_result = await self.download_and_save_content(url, output_dir, title)
                
                if download_result["status"] == "success":
                    success_count += 1
                    download_results.append({
                        "title": title,
                        "url": url,
                        "status": "success",
                        "files": download_result["files"]
                    })
                else:
                    failed_count += 1
                    download_results.append({
                        "title": title,
                        "url": url,
                        "status": "failed",
                        "error": download_result.get("message", "未知错误")
                    })
                
                # 等待一下，避免请求过快
                await asyncio.sleep(1)
            
            # 3. 生成批量下载总结
            summary = {
                "query": query,
                "download_time": datetime.now().isoformat(),
                "total_found": len(results),
                "success_count": success_count,
                "failed_count": failed_count,
                "output_directory": str(output_dir),
                "results": download_results
            }
            
            summary_file = output_dir / f"batch_download_summary_{query}_{int(datetime.now().timestamp())}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "message": f"批量下载完成: 成功{success_count}篇，失败{failed_count}篇",
                "query": query,
                "total_found": len(results),
                "success_count": success_count,
                "failed_count": failed_count,
                "output_dir": str(output_dir),
                "summary_file": str(summary_file),
                "results": download_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"批量下载失败: {str(e)}",
                "error": str(e)
            }

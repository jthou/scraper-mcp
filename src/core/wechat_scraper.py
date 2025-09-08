#!/usr/bin/env python3
"""
微信内容抓取模块

基于搜狗微信搜索的微信内容抓取功能
支持搜索、下载、批量处理等操作
"""

import asyncio
import re
import json
import time
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
import random

from src.utils.logger import Logger
from src.core.advanced_stealth import AdvancedStealth


class WeChatScraper:
    """微信内容抓取类"""
    
    def __init__(self):
        self.logger = Logger("WeChatScraper")
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.base_url = "https://weixin.sogou.com"
        self.user_data_dir = None
        self.stealth = AdvancedStealth()
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接方法"""
        return {
            "status": "success",
            "message": f"{self.__class__.__name__} 模块已初始化",
            "module": self.__class__.__name__
        }
    
    async def setup_browser(self, headless: bool = False, persistent: bool = False) -> Dict[str, Any]:
        """设置高级隐身浏览器环境"""
        try:
            self.playwright = await async_playwright().start()
            
            # 使用高级隐身参数
            stealth_args = self.stealth.get_stealth_args()
            
            if persistent:
                # 使用持久化上下文保存登录状态
                self.user_data_dir = Path(__file__).parent.parent.parent / "data" / "browser_data" / "wechat_stealth"
                self.user_data_dir.mkdir(parents=True, exist_ok=True)
                
                self.context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=str(self.user_data_dir),
                    channel="chrome",
                    headless=headless,
                    args=stealth_args
                )
                
                self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            else:
                # 使用临时浏览器
                self.browser = await self.playwright.chromium.launch(
                    channel="chrome",
                    headless=headless,
                    args=stealth_args
                )
                
                # 使用高级隐身上下文
                self.context = await self.stealth.setup_stealth_context(self.browser, headless)
                self.page = await self.stealth.setup_stealth_page(self.context)
            
            # 设置随机延迟
            await self.stealth.random_delay(1000, 3000)
            
            # 模拟人类行为
            await self.stealth.simulate_human_behavior(self.page, duration=3)
            
            return {
                "status": "success",
                "message": "高级隐身微信搜索浏览器环境设置完成",
                "persistent": persistent,
                "user_data_dir": str(self.user_data_dir) if persistent else None,
                "stealth_enabled": True
            }
            
        except Exception as e:
            self.logger.error(f"浏览器设置失败: {e}")
            return {
                "status": "error",
                "message": f"浏览器设置失败: {str(e)}",
                "error": str(e)
            }
    
    async def search_wechat(self, query: str, max_pages: int = 3) -> Dict[str, Any]:
        """搜索微信内容 - 使用高级反爬虫策略"""
        try:
            if not self.page:
                return {
                    "status": "error",
                    "message": "浏览器未初始化，请先调用setup_browser"
                }
            
            self.logger.info(f"开始搜索微信内容: {query}")
            
            # 构建搜索URL
            search_url = f"{self.base_url}/weixin?type=2&query={query}"
            
            # 访问搜索页面前先模拟人类行为
            await self.stealth.simulate_human_behavior(self.page, duration=2)
            
            # 访问搜索页面
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            
            # 高级反爬虫等待策略
            await self.stealth.random_delay(3000, 6000)
            
            # 模拟人类浏览行为
            await self.stealth.simulate_human_behavior(self.page, duration=5)
            
            # 检查是否需要验证码
            captcha_result = await self._check_captcha()
            if captcha_result["has_captcha"]:
                # 等待人工验证完成
                self.logger.info("检测到验证码，等待人工验证完成...")
                verification_result = await self.wait_for_manual_verification(timeout=None)
                
                if not verification_result["success"]:
                    return {
                        "status": "error",
                        "message": "等待人工验证超时",
                        "captcha_type": captcha_result["type"],
                        "url": search_url,
                        "suggestion": "请手动完成验证码后重试",
                        "verification_result": verification_result
                    }
                else:
                    self.logger.info(f"人工验证完成: {verification_result['message']}")
            
            # 提取搜索结果
            all_results = []
            pages_searched = 0

            if max_pages is None:
                # 抓取全部页面：直到没有下一页
                page_num = 1
                while True:
                    self.logger.info(f"提取第 {page_num} 页结果（全量模式）...")
                    page_results = await self._extract_page_results()
                    all_results.extend(page_results)
                    pages_searched += 1

                    # 尝试翻页
                    next_page_success = await self._go_to_next_page(page_num + 1)
                    if not next_page_success:
                        self.logger.warning(f"无法翻页到第 {page_num + 1} 页，停止搜索")
                        break

                    page_num += 1
                    await self.stealth.random_delay(5000, 10000)
                    await self.stealth.simulate_human_behavior(self.page, duration=3)
            else:
                # 抓取指定页数
                for page_num in range(1, max_pages + 1):
                    self.logger.info(f"提取第 {page_num} 页结果...")
                    page_results = await self._extract_page_results()
                    all_results.extend(page_results)
                    pages_searched = page_num

                    if page_num < max_pages:
                        next_page_success = await self._go_to_next_page(page_num + 1)
                        if not next_page_success:
                            self.logger.warning(f"无法翻页到第 {page_num + 1} 页，停止搜索")
                            break

                    await self.stealth.random_delay(5000, 10000)
                    await self.stealth.simulate_human_behavior(self.page, duration=3)

            # 去重和排序
            unique_results = self._deduplicate_results(all_results)
            
            # 提取所有链接
            all_links = [result["link"] for result in unique_results if result.get("link")]
            
            return {
                "status": "success",
                "message": f"搜索完成，共找到 {len(unique_results)} 个结果",
                "query": query,
                "total_results": len(unique_results),
                "unique_links": len(all_links),
                "pages_searched": pages_searched,
                "url": search_url,
                "all_links": all_links,
                "results": unique_results
            }
            
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return {
                "status": "error",
                "message": f"搜索失败: {str(e)}",
                "query": query,
                "error": str(e)
            }
    
    async def _check_captcha(self) -> Dict[str, Any]:
        """检查是否需要验证码"""
        try:
            # 检查各种验证码类型
            captcha_selectors = [
                (".captcha", "图片验证码"),
                (".verify-code", "验证码"),
                (".slider", "滑块验证码"),
                (".geetest", "极验验证码"),
                (".nc-container", "阿里云验证码"),
                ("#captcha", "验证码"),
                (".captcha-container", "验证码容器"),
                (".sogou-captcha", "搜狗验证码"),
                (".sogou-verify", "搜狗验证"),
                ("[class*='captcha']", "验证码相关元素"),
                ("[class*='verify']", "验证相关元素")
            ]
            
            for selector, captcha_type in captcha_selectors:
                captcha_element = await self.page.query_selector(selector)
                if captcha_element:
                    return {
                        "has_captcha": True,
                        "type": captcha_type,
                        "selector": selector
                    }
            
            # 检查页面标题是否包含验证码相关文字
            title = await self.page.title()
            if any(keyword in title for keyword in ["验证码", "captcha", "验证", "安全验证", "搜狗搜索"]):
                return {
                    "has_captcha": True,
                    "type": "页面标题检测",
                    "title": title
                }
            
            # 检查页面内容是否包含验证码相关文字
            content = await self.page.content()
            if any(keyword in content for keyword in ["验证码", "captcha", "请依次点击", "安全验证"]):
                return {
                    "has_captcha": True,
                    "type": "页面内容检测",
                    "content_keywords": [kw for kw in ["验证码", "captcha", "请依次点击", "安全验证"] if kw in content]
                }
            
            return {"has_captcha": False}
            
        except Exception as e:
            self.logger.warning(f"检查验证码失败: {e}")
            return {"has_captcha": False}
    
    async def _try_bypass_captcha(self) -> Dict[str, Any]:
        """尝试绕过验证码"""
        try:
            self.logger.info("尝试绕过验证码...")
            
            # 等待一段时间让页面完全加载
            await self.stealth.random_delay(3000, 5000)
            
            # 模拟人类行为
            await self.stealth.simulate_human_behavior(self.page, duration=5)
            
            # 尝试刷新页面
            await self.page.reload()
            await self.page.wait_for_load_state("networkidle")
            
            # 再次检查验证码
            captcha_result = await self._check_captcha()
            if not captcha_result["has_captcha"]:
                self.logger.info("验证码绕过成功")
                return {"success": True, "method": "page_reload"}
            
            # 尝试等待更长时间
            await self.stealth.random_delay(10000, 15000)
            await self.stealth.simulate_human_behavior(self.page, duration=10)
            
            # 再次检查
            captcha_result = await self._check_captcha()
            if not captcha_result["has_captcha"]:
                self.logger.info("验证码绕过成功（等待策略）")
                return {"success": True, "method": "wait_strategy"}
            
            self.logger.warning("验证码绕过失败")
            return {"success": False, "reason": "无法自动绕过验证码"}
            
        except Exception as e:
            self.logger.error(f"验证码绕过失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def wait_for_manual_verification(self, timeout: int = None) -> Dict[str, Any]:
        """等待人工验证完成"""
        try:
            if timeout is None:
                self.logger.info("等待人工验证完成，无超时限制，将一直等待直到验证完成...")
            else:
                self.logger.info(f"等待人工验证完成，超时时间: {timeout}秒")
            
            start_time = time.time()
            verification_completed = False
            
            while timeout is None or time.time() - start_time < timeout:
                # 检查当前页面状态
                current_url = self.page.url
                title = await self.page.title()
                content = await self.page.content()
                
                # 检查是否还在验证页面
                if "antispider" in current_url or "验证码" in title or "captcha" in content.lower():
                    self.logger.info(f"仍在验证页面，等待用户完成验证... (已等待 {int(time.time() - start_time)}秒)")
                    
                    # 模拟人类行为，让用户看到我们在等待
                    await self.stealth.simulate_human_behavior(self.page, duration=2)
                    
                    # 等待一段时间后重试
                    await asyncio.sleep(5)
                    continue
                
                # 检查是否重定向到微信文章
                if "mp.weixin.qq.com" in current_url:
                    self.logger.info("检测到重定向到微信文章，验证可能成功")
                    verification_completed = True
                    break
                
                # 检查是否重定向到搜狗搜索结果
                if "weixin.sogou.com/weixin" in current_url and "antispider" not in current_url:
                    self.logger.info("检测到重定向到搜狗搜索结果，验证可能成功")
                    verification_completed = True
                    break
                
                # 检查页面内容是否包含文章内容
                if any(keyword in content for keyword in [
                    "微信公众平台", "文章内容", "作者", "发布时间", "阅读量"
                ]):
                    self.logger.info("检测到文章内容，验证可能成功")
                    verification_completed = True
                    break
                
                # 等待一段时间后重试
                await asyncio.sleep(3)
            
            if verification_completed:
                return {
                    "success": True,
                    "message": "人工验证完成",
                    "current_url": current_url,
                    "title": title,
                    "wait_time": int(time.time() - start_time)
                }
            else:
                return {
                    "success": False,
                    "message": f"等待人工验证超时 ({timeout}秒)",
                    "current_url": current_url,
                    "title": title,
                    "wait_time": int(time.time() - start_time)
                }
                
        except Exception as e:
            self.logger.error(f"等待人工验证失败: {e}")
            return {
                "success": False, 
                "error": str(e),
                "wait_time": int(time.time() - start_time) if 'start_time' in locals() else 0
            }
    
    async def _extract_page_results(self) -> List[Dict[str, Any]]:
        """提取当前页的搜索结果"""
        try:
            results = []
            
            # 等待搜索结果加载
            await self.page.wait_for_selector(".txt-box", timeout=10000)
            
            # 获取所有结果项
            result_items = await self.page.query_selector_all(".txt-box")
            
            for item in result_items:
                try:
                    result = await self._extract_single_result(item)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.warning(f"提取单个结果失败: {e}")
                    continue
            
            self.logger.info(f"成功提取 {len(results)} 个结果")
            return results
            
        except Exception as e:
            self.logger.error(f"提取页面结果失败: {e}")
            return []
    
    async def _extract_single_result(self, item) -> Optional[Dict[str, Any]]:
        """提取单个搜索结果"""
        try:
            # 提取标题和链接
            title_element = await item.query_selector("h3 a")
            if not title_element:
                return None
            
            title = await title_element.inner_text()
            link = await title_element.get_attribute("href")
            
            # 处理相对链接
            if link and not link.startswith("http"):
                if link.startswith("//"):
                    link = f"https:{link}"
                elif link.startswith("/"):
                    link = f"{self.base_url}{link}"
                else:
                    link = f"{self.base_url}/{link}"
            
            # 提取摘要
            summary_element = await item.query_selector(".txt-info")
            summary = ""
            if summary_element:
                summary = await summary_element.inner_text()
                # 清理摘要文本
                summary = re.sub(r'\s+', ' ', summary).strip()
            
            # 提取作者
            author_element = await item.query_selector(".s-p .account")
            author = ""
            if author_element:
                author = await author_element.inner_text()
            
            # 提取发布时间
            time_element = await item.query_selector(".s-p .s2")
            publish_time = ""
            if time_element:
                publish_time = await time_element.inner_text()
            
            # 提取阅读数
            read_count_element = await item.query_selector(".s-p .s3")
            read_count = ""
            if read_count_element:
                read_count = await read_count_element.inner_text()
            
            # 提取公众号名称
            account_element = await item.query_selector(".s-p .account")
            account_name = ""
            if account_element:
                account_name = await account_element.inner_text()
            
            return {
                "title": title.strip(),
                "link": link,
                "summary": summary,
                "author": author.strip(),
                "account_name": account_name.strip(),
                "publish_time": publish_time.strip(),
                "read_count": read_count.strip(),
                "source": "sogou_wechat",
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"提取单个结果失败: {e}")
            return None
    
    async def _go_to_next_page(self, page_num: int) -> bool:
        """翻页到指定页面"""
        try:
            # 尝试多种翻页方式
            next_page_selectors = [
                f".pagination a[href*='page={page_num}']",
                f".pagination a:has-text('{page_num}')",
                ".pagination .next:not(.disabled)",
                ".pagination .next-page",
                ".pagination .page-next"
            ]
            
            for selector in next_page_selectors:
                try:
                    next_button = await self.page.query_selector(selector)
                    if next_button:
                        # 滚动到按钮位置
                        await next_button.scroll_into_view_if_needed()
                        await self.page.wait_for_timeout(1000)
                        
                        # 点击按钮
                        await next_button.click()
                        
                        # 等待页面加载
                        await self.page.wait_for_load_state("networkidle")
                        await self.page.wait_for_timeout(2000)
                        
                        self.logger.info(f"成功翻页到第 {page_num} 页")
                        return True
                except Exception as e:
                    continue
            
            # 如果找不到翻页按钮，尝试直接访问URL
            try:
                current_url = self.page.url
                if "page=" in current_url:
                    new_url = re.sub(r'page=\d+', f'page={page_num}', current_url)
                else:
                    new_url = f"{current_url}&page={page_num}"
                
                await self.page.goto(new_url)
                await self.page.wait_for_load_state("networkidle")
                await self.page.wait_for_timeout(2000)
                
                self.logger.info(f"通过URL直接访问第 {page_num} 页")
                return True
                
            except Exception as e:
                self.logger.warning(f"直接访问第 {page_num} 页失败: {e}")
                return False
            
        except Exception as e:
            self.logger.error(f"翻页失败: {e}")
            return False
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重搜索结果"""
        try:
            seen_links = set()
            unique_results = []
            
            for result in results:
                link = result.get("link", "")
                if link and link not in seen_links:
                    seen_links.add(link)
                    unique_results.append(result)
            
            self.logger.info(f"去重前: {len(results)} 个结果，去重后: {len(unique_results)} 个结果")
            return unique_results
            
        except Exception as e:
            self.logger.error(f"去重失败: {e}")
            return results
    
    async def read_wechat_page(self, url: str) -> Dict[str, Any]:
        """读取微信页面内容"""
        try:
            if not self.page:
                return {
                    "status": "error",
                    "message": "浏览器未初始化，请先调用setup_browser"
                }
            
            # 处理搜狗重定向链接
            if "weixin.sogou.com/link?" in url:
                self.logger.info(f"处理搜狗重定向链接: {url}")
                
                # 先模拟人类行为
                await self.stealth.simulate_human_behavior(self.page, duration=2)
                
                # 先访问搜狗链接，等待重定向
                await self.page.goto(url)
                await self.page.wait_for_load_state("networkidle")
                
                # 高级等待策略
                await self.stealth.random_delay(5000, 8000)
                
                # 模拟人类浏览行为
                await self.stealth.simulate_human_behavior(self.page, duration=3)
                
                # 检查是否重定向到了真正的微信文章
                current_url = self.page.url
                if "mp.weixin.qq.com" in current_url:
                    # 成功重定向到微信文章
                    url = current_url
                    self.logger.info(f"成功重定向到微信文章: {url}")
                else:
                    # 可能遇到了验证码或其他问题
                    title = await self.page.title()
                    if "搜狗搜索" in title or "验证码" in title:
                        # 等待人工验证完成
                        self.logger.info("检测到验证码，等待人工验证完成...")
                        verification_result = await self.wait_for_manual_verification(timeout=None)
                        
                        if verification_result["success"]:
                            current_url = self.page.url
                            if "mp.weixin.qq.com" in current_url:
                                url = current_url
                                self.logger.info(f"人工验证后成功重定向到微信文章: {url}")
                            else:
                                return {
                                    "status": "error",
                                    "message": f"人工验证后仍无法访问微信文章，当前URL: {current_url}",
                                    "has_captcha": True,
                                    "current_url": current_url,
                                    "title": title,
                                    "verification_result": verification_result
                                }
                        else:
                            return {
                                "status": "error",
                                "message": f"等待人工验证超时，当前URL: {current_url}",
                                "has_captcha": True,
                                "current_url": current_url,
                                "title": title,
                                "verification_result": verification_result
                            }
                    else:
                        return {
                            "status": "error",
                            "message": f"重定向失败，当前URL: {current_url}",
                            "current_url": current_url
                        }
            else:
                # 直接访问微信文章
                await self.page.goto(url)
                await self.page.wait_for_load_state("networkidle")
            
            # 高级反爬虫等待策略
            await self.stealth.random_delay(3000, 6000)
            
            # 模拟人类行为
            await self.stealth.simulate_human_behavior(self.page, duration=4)
            
            # 获取页面标题
            title = await self.page.title()
            
            # 检查是否是微信文章页面
            if "搜狗搜索" in title or "验证码" in title:
                return {
                    "status": "error",
                    "message": "页面被重定向到验证码页面，可能需要人工验证",
                    "title": title,
                    "url": url
                }
            
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
                "message": "成功读取微信页面内容",
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
                "message": f"读取微信页面失败: {str(e)}",
                "error": str(e)
            }
    
    async def print_page_to_pdf(self, url: str, output_path: str = None) -> Dict[str, Any]:
        """将微信页面打印成PDF - 使用高级反爬虫策略"""
        try:
            if not self.page:
                return {
                    "status": "error",
                    "message": "浏览器未初始化，请先调用setup_browser"
                }
            
            # 访问页面前先模拟人类行为
            await self.stealth.simulate_human_behavior(self.page, duration=2)
            
            # 访问页面
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            
            # 高级反爬虫等待策略
            await self.stealth.random_delay(3000, 6000)
            
            # 模拟人类行为
            await self.stealth.simulate_human_behavior(self.page, duration=4)
            
            # 额外等待页面完全加载
            await asyncio.sleep(5)
            
            # 模拟用户滚动页面，触发懒加载
            await self.page.evaluate("window.scrollBy(0, 300)")
            await asyncio.sleep(1)
            await self.page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(1)
            await self.page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(2)
            
            # 生成PDF文件路径
            if output_path:
                pdf_path = Path(output_path)
            else:
                pdf_path = Path(__file__).parent.parent.parent / "data" / "pdfs" / f"wechat_{int(asyncio.get_event_loop().time())}.pdf"
            
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 设置更长的超时时间
            self.page.set_default_timeout(120000)  # 120秒超时
            self.page.set_default_navigation_timeout(120000)  # 120秒导航超时
            
            # 等待页面完全加载
            await asyncio.sleep(5)
            
            # 使用浏览器打印功能生成PDF，增加错误处理
            try:
                self.logger.info(f"开始生成PDF: {pdf_path}")
                await self.page.pdf(
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
                self.logger.info(f"PDF生成完成: {pdf_path}")
            except Exception as pdf_error:
                # 如果PDF生成失败，尝试使用不同的参数
                self.logger.warning(f"PDF生成失败，尝试备用参数: {pdf_error}")
                try:
                    await self.page.pdf(
                        path=str(pdf_path),
                        format='A4',
                        print_background=True,
                        margin={
                            'top': '0.5cm',
                            'right': '0.5cm',
                            'bottom': '0.5cm',
                            'left': '0.5cm'
                        }
                    )
                except Exception as pdf_error2:
                    # 如果仍然失败，尝试使用更简单的参数
                    self.logger.warning(f"PDF生成再次失败，尝试简化参数: {pdf_error2}")
                    await self.page.pdf(
                        path=str(pdf_path),
                        format='A4'
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
                
                # 检测可能的标题
                if (len(line) > 10 and 
                    (line[0].isupper() or 
                     '：' in line or ':' in line or
                     '文章' in line or '内容' in line or
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
        """下载微信内容并保存为PDF和Markdown文件"""
        try:
            # 1. 确保输出目录存在
            pdf_dir = output_dir / "pdfs"
            markdown_dir = output_dir / "markdown"
            pdf_dir.mkdir(parents=True, exist_ok=True)
            markdown_dir.mkdir(parents=True, exist_ok=True)
            
            # 2. 先确定文件名
            page_result = await self.read_wechat_page(url)
            page_title = ""
            if page_result["status"] == "success":
                page_title = page_result.get("title", "")
            
            # 使用提供的标题或页面标题
            final_title = title if title else page_title
            if not final_title:
                final_title = f"wechat_content_{int(datetime.now().timestamp())}"
            
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
**来源平台**: 搜狗微信搜索

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
                "download_time": datetime.now().isoformat(),
                "source": "wechat"
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
    
    async def batch_download_content(self, query: str, output_dir: Path, max_pages: int = 3) -> Dict[str, Any]:
        """批量下载微信搜索结果"""
        try:
            # 1. 搜索内容
            search_result = await self.search_wechat(query, max_pages)
            
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
                url = article.get("link", "")
                title = article.get("title", "")
                
                if not url:
                    failed_count += 1
                    continue
                
                self.logger.info(f"下载第 {i}/{len(results)} 篇: {title}")
                
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
            
            summary_file = output_dir / f"wechat_batch_download_summary_{query}_{int(datetime.now().timestamp())}.json"
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
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                await self.browser.close()
            if self.context and not self.user_data_dir:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("资源清理完成")
        except Exception as e:
            self.logger.error(f"资源清理失败: {e}")

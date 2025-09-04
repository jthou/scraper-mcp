#!/usr/bin/env python3
"""
搜狗微信搜索专用模块

搜狗微信搜索的优势：
1. 无需登录微信账号
2. 搜索结果相对完整
3. 支持关键词搜索
4. 相对稳定

技术挑战：
1. 经常出现验证码
2. 反爬虫机制严格
3. 搜索结果可能不完整
4. 需要处理动态加载
"""

import asyncio
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from playwright.async_api import async_playwright
from src.utils.logger import Logger


class SogouWeChatSearch:
    """搜狗微信搜索专用类"""
    
    def __init__(self):
        self.logger = Logger("SogouWeChatSearch")
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.base_url = "https://weixin.sogou.com"
    
    async def setup_browser(self, headless: bool = False) -> bool:
        """设置浏览器环境，专门针对搜狗搜索优化"""
        try:
            self.playwright = await async_playwright().start()
            
            # 针对搜狗搜索优化的浏览器参数
            self.browser = await self.playwright.chromium.launch(
                channel="chrome",
                headless=headless,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-sync",
                    "--disable-extensions",
                    "--disable-default-apps",
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
                    "--use-mock-keychain",
                    "--disable-dev-shm-usage",
                    "--no-sandbox"
                ]
            )
            
            # 创建浏览器上下文
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            self.page = await self.context.new_page()
            
            # 设置额外的HTTP头，模拟真实用户
            await self.page.set_extra_http_headers({
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
            
            # 设置超时时间
            self.page.set_default_timeout(30000)
            
            self.logger.info("搜狗微信搜索浏览器环境设置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"浏览器设置失败: {e}")
            return False
    
    async def search(self, query: str, max_pages: int = 3) -> Dict[str, Any]:
        """搜索微信公众号内容"""
        try:
            self.logger.info(f"开始搜索: {query}")
            
            # 构建搜索URL
            search_url = f"{self.base_url}/weixin?type=2&query={query}"
            
            # 访问搜索页面
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            
            # 模拟人类行为 - 随机等待
            await self.page.wait_for_timeout(random.randint(2000, 4000))
            
            # 检查是否需要验证码
            captcha_result = await self._check_captcha()
            if captcha_result["has_captcha"]:
                return {
                    "status": "error",
                    "message": "需要验证码，无法自动搜索",
                    "captcha_type": captcha_result["type"],
                    "url": search_url,
                    "suggestion": "请手动访问页面完成验证码后重试"
                }
            
            # 提取搜索结果
            all_results = []
            
            for page_num in range(1, max_pages + 1):
                self.logger.info(f"提取第 {page_num} 页结果...")
                
                # 提取当前页结果
                page_results = await self._extract_page_results()
                all_results.extend(page_results)
                
                # 如果不是最后一页，尝试翻页
                if page_num < max_pages:
                    next_page_success = await self._go_to_next_page(page_num + 1)
                    if not next_page_success:
                        self.logger.warning(f"无法翻页到第 {page_num + 1} 页，停止搜索")
                        break
                
                # 页面间等待
                await self.page.wait_for_timeout(random.randint(3000, 5000))
            
            # 去重和排序
            unique_results = self._deduplicate_results(all_results)
            
            return {
                "status": "success",
                "message": f"搜索完成，共找到 {len(unique_results)} 个结果",
                "query": query,
                "total_results": len(unique_results),
                "pages_searched": min(page_num, max_pages),
                "url": search_url,
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
                (".captcha-container", "验证码容器")
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
            if any(keyword in title for keyword in ["验证码", "captcha", "验证", "安全验证"]):
                return {
                    "has_captcha": True,
                    "type": "页面标题检测",
                    "title": title
                }
            
            return {"has_captcha": False}
            
        except Exception as e:
            self.logger.warning(f"检查验证码失败: {e}")
            return {"has_captcha": False}
    
    async def _extract_page_results(self) -> List[Dict[str, Any]]:
        """提取当前页的搜索结果"""
        try:
            results = []
            
            # 等待搜索结果加载
            await self.page.wait_for_selector(".results .result", timeout=10000)
            
            # 获取所有结果项
            result_items = await self.page.query_selector_all(".results .result")
            
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
            title_element = await item.query_selector(".txt-box h3 a")
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
            summary_element = await item.query_selector(".txt-box .txt-info")
            summary = ""
            if summary_element:
                summary = await summary_element.inner_text()
                # 清理摘要文本
                summary = re.sub(r'\s+', ' ', summary).strip()
            
            # 提取作者
            author_element = await item.query_selector(".txt-box .s-p .account")
            author = ""
            if author_element:
                author = await author_element.inner_text()
            
            # 提取发布时间
            time_element = await item.query_selector(".txt-box .s-p .s2")
            publish_time = ""
            if time_element:
                publish_time = await time_element.inner_text()
            
            # 提取阅读数
            read_count_element = await item.query_selector(".txt-box .s-p .s3")
            read_count = ""
            if read_count_element:
                read_count = await read_count_element.inner_text()
            
            # 提取公众号名称
            account_element = await item.query_selector(".txt-box .s-p .account")
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
    
    async def search_with_retry(self, query: str, max_pages: int = 3, max_retries: int = 3) -> Dict[str, Any]:
        """带重试的搜索功能"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"搜索尝试 {attempt + 1}/{max_retries}: {query}")
                
                result = await self.search(query, max_pages)
                
                if result["status"] == "success":
                    return result
                elif result["status"] == "error" and "验证码" in result.get("message", ""):
                    self.logger.warning(f"遇到验证码，等待 {5 * (attempt + 1)} 秒后重试...")
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                else:
                    return result
                    
            except Exception as e:
                self.logger.error(f"搜索尝试 {attempt + 1} 失败: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(3 * (attempt + 1))
                    continue
                else:
                    return {
                        "status": "error",
                        "message": f"搜索失败，已重试 {max_retries} 次",
                        "error": str(e)
                    }
        
        return {
            "status": "error",
            "message": "搜索失败，已达到最大重试次数"
        }
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("资源清理完成")
        except Exception as e:
            self.logger.error(f"资源清理失败: {e}")


async def main():
    """主函数 - 测试搜狗微信搜索"""
    print("🔍 搜狗微信搜索测试")
    print("=" * 40)
    
    # 创建搜索实例
    searcher = SogouWeChatSearch()
    
    try:
        # 设置浏览器
        if not await searcher.setup_browser(headless=False):
            print("❌ 浏览器设置失败")
            return
        
        # 测试查询
        test_queries = [
            "Python编程",
            "机器学习算法",
            "人工智能应用"
        ]
        
        for query in test_queries:
            print(f"\n🔍 搜索: {query}")
            print("-" * 30)
            
            # 执行搜索
            result = await searcher.search_with_retry(query, max_pages=2)
            
            if result["status"] == "success":
                print(f"✅ {result['message']}")
                print(f"📊 总结果数: {result['total_results']}")
                print(f"📄 搜索页数: {result['pages_searched']}")
                
                # 显示前3个结果
                for i, item in enumerate(result.get('results', [])[:3], 1):
                    print(f"\n{i}. {item['title']}")
                    print(f"   作者: {item['author']}")
                    print(f"   公众号: {item['account_name']}")
                    print(f"   时间: {item['publish_time']}")
                    print(f"   阅读: {item['read_count']}")
                    print(f"   摘要: {item['summary'][:100]}...")
                    print(f"   链接: {item['link']}")
            else:
                print(f"❌ {result['message']}")
                if result.get('suggestion'):
                    print(f"💡 建议: {result['suggestion']}")
            
            # 保存结果
            if result["status"] == "success":
                output_file = Path(__file__).parent / f"sogou_search_{query}_{int(datetime.now().timestamp())}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"📁 结果已保存到: {output_file}")
            
            # 等待用户确认
            input("\n按回车键继续下一个搜索...")
    
    except KeyboardInterrupt:
        print("\n⏹️ 搜索被用户中断")
    except Exception as e:
        print(f"\n💥 搜索过程中发生错误: {e}")
    finally:
        await searcher.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

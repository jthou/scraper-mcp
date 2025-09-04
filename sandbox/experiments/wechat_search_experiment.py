#!/usr/bin/env python3
"""
微信公众号内容搜索实验

微信公众号搜索的挑战：
1. 微信没有公开的搜索API
2. 需要登录微信账号
3. 搜索接口经常变化
4. 反爬虫机制严格

本实验探索几种可能的搜索方法：
1. 通过搜狗微信搜索
2. 通过微信PC版搜索
3. 通过第三方聚合平台
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from playwright.async_api import async_playwright
from src.utils.logger import Logger


class WeChatSearchExperiment:
    """微信公众号搜索实验类"""
    
    def __init__(self):
        self.logger = Logger("WeChatSearchExperiment")
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def setup_browser(self, headless: bool = False):
        """设置浏览器环境"""
        try:
            self.playwright = await async_playwright().start()
            
            # 使用Chrome浏览器，添加反检测参数
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
                    "--use-mock-keychain"
                ]
            )
            
            # 创建浏览器上下文
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            self.page = await self.context.new_page()
            
            # 设置额外的HTTP头
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
            
            self.logger.info("浏览器环境设置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"浏览器设置失败: {e}")
            return False
    
    async def method1_sogou_wechat_search(self, query: str) -> Dict[str, Any]:
        """方法1: 通过搜狗微信搜索"""
        try:
            self.logger.info(f"尝试方法1: 搜狗微信搜索 - {query}")
            
            # 搜狗微信搜索URL
            search_url = f"https://weixin.sogou.com/weixin?type=2&query={query}"
            
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            
            # 等待搜索结果加载
            await self.page.wait_for_timeout(3000)
            
            # 检查是否需要验证码
            captcha = await self.page.query_selector(".captcha, .verify-code, .slider")
            if captcha:
                return {
                    "status": "error",
                    "message": "需要验证码，无法自动搜索",
                    "method": "sogou_wechat",
                    "url": search_url
                }
            
            # 提取搜索结果
            results = await self._extract_sogou_results()
            
            return {
                "status": "success",
                "message": f"搜狗微信搜索完成，找到{len(results)}个结果",
                "method": "sogou_wechat",
                "query": query,
                "url": search_url,
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜狗微信搜索失败: {str(e)}",
                "method": "sogou_wechat",
                "error": str(e)
            }
    
    async def method2_wechat_pc_search(self, query: str) -> Dict[str, Any]:
        """方法2: 通过微信PC版搜索（需要登录）"""
        try:
            self.logger.info(f"尝试方法2: 微信PC版搜索 - {query}")
            
            # 微信PC版搜索URL
            search_url = "https://wx.qq.com/"
            
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            
            # 等待页面加载
            await self.page.wait_for_timeout(5000)
            
            # 检查是否需要登录
            login_required = await self.page.query_selector(".login, .qr-login, .login-container")
            if login_required:
                return {
                    "status": "waiting",
                    "message": "需要登录微信账号才能搜索",
                    "method": "wechat_pc",
                    "url": search_url,
                    "action_required": "请手动登录微信"
                }
            
            # 尝试找到搜索框
            search_box = await self.page.query_selector("input[placeholder*='搜索'], input[type='search'], .search-input")
            if not search_box:
                return {
                    "status": "error",
                    "message": "未找到搜索框",
                    "method": "wechat_pc",
                    "url": search_url
                }
            
            # 输入搜索关键词
            await search_box.fill(query)
            await search_box.press("Enter")
            
            # 等待搜索结果
            await self.page.wait_for_timeout(3000)
            
            # 提取搜索结果
            results = await self._extract_wechat_pc_results()
            
            return {
                "status": "success",
                "message": f"微信PC版搜索完成，找到{len(results)}个结果",
                "method": "wechat_pc",
                "query": query,
                "url": search_url,
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"微信PC版搜索失败: {str(e)}",
                "method": "wechat_pc",
                "error": str(e)
            }
    
    async def method3_third_party_search(self, query: str) -> Dict[str, Any]:
        """方法3: 通过第三方聚合平台搜索"""
        try:
            self.logger.info(f"尝试方法3: 第三方平台搜索 - {query}")
            
            # 尝试几个第三方微信搜索平台
            platforms = [
                {
                    "name": "微信文章搜索",
                    "url": f"https://weixin.sogou.com/weixin?type=2&query={query}",
                    "selectors": {
                        "results": ".results .result",
                        "title": ".txt-box h3 a",
                        "link": ".txt-box h3 a",
                        "summary": ".txt-box .txt-info",
                        "author": ".txt-box .s-p .account"
                    }
                },
                {
                    "name": "微信搜索助手",
                    "url": f"https://weixin.sogou.com/weixin?type=2&query={query}",
                    "selectors": {
                        "results": ".results .result",
                        "title": ".txt-box h3 a",
                        "link": ".txt-box h3 a",
                        "summary": ".txt-box .txt-info",
                        "author": ".txt-box .s-p .account"
                    }
                }
            ]
            
            all_results = []
            
            for platform in platforms:
                try:
                    await self.page.goto(platform["url"])
                    await self.page.wait_for_load_state("networkidle")
                    await self.page.wait_for_timeout(2000)
                    
                    # 提取结果
                    results = await self._extract_results_with_selectors(platform["selectors"])
                    all_results.extend(results)
                    
                except Exception as e:
                    self.logger.warning(f"平台 {platform['name']} 搜索失败: {e}")
                    continue
            
            return {
                "status": "success",
                "message": f"第三方平台搜索完成，找到{len(all_results)}个结果",
                "method": "third_party",
                "query": query,
                "results": all_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"第三方平台搜索失败: {str(e)}",
                "method": "third_party",
                "error": str(e)
            }
    
    async def _extract_sogou_results(self) -> List[Dict[str, Any]]:
        """提取搜狗搜索结果"""
        try:
            results = []
            
            # 等待搜索结果加载
            await self.page.wait_for_selector(".results .result", timeout=10000)
            
            # 获取所有结果项
            result_items = await self.page.query_selector_all(".results .result")
            
            for item in result_items:
                try:
                    # 提取标题和链接
                    title_element = await item.query_selector(".txt-box h3 a")
                    if not title_element:
                        continue
                    
                    title = await title_element.inner_text()
                    link = await title_element.get_attribute("href")
                    
                    # 提取摘要
                    summary_element = await item.query_selector(".txt-box .txt-info")
                    summary = ""
                    if summary_element:
                        summary = await summary_element.inner_text()
                    
                    # 提取作者
                    author_element = await item.query_selector(".txt-box .s-p .account")
                    author = ""
                    if author_element:
                        author = await author_element.inner_text()
                    
                    # 提取时间
                    time_element = await item.query_selector(".txt-box .s-p .s2")
                    publish_time = ""
                    if time_element:
                        publish_time = await time_element.inner_text()
                    
                    result = {
                        "title": title.strip(),
                        "link": link,
                        "summary": summary.strip(),
                        "author": author.strip(),
                        "publish_time": publish_time.strip(),
                        "source": "sogou_wechat"
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"提取单个结果失败: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"提取搜狗搜索结果失败: {e}")
            return []
    
    async def _extract_wechat_pc_results(self) -> List[Dict[str, Any]]:
        """提取微信PC版搜索结果"""
        try:
            results = []
            
            # 微信PC版的搜索结果选择器可能不同
            # 这里需要根据实际页面结构调整
            result_items = await self.page.query_selector_all(".message-item, .chat-item, .search-result")
            
            for item in result_items:
                try:
                    # 提取标题
                    title_element = await item.query_selector(".title, .message-title, h3")
                    title = ""
                    if title_element:
                        title = await title_element.inner_text()
                    
                    # 提取链接
                    link_element = await item.query_selector("a")
                    link = ""
                    if link_element:
                        link = await link_element.get_attribute("href")
                    
                    # 提取摘要
                    summary_element = await item.query_selector(".summary, .message-content, .preview")
                    summary = ""
                    if summary_element:
                        summary = await summary_element.inner_text()
                    
                    result = {
                        "title": title.strip(),
                        "link": link,
                        "summary": summary.strip(),
                        "author": "",
                        "publish_time": "",
                        "source": "wechat_pc"
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"提取微信PC结果失败: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"提取微信PC搜索结果失败: {e}")
            return []
    
    async def _extract_results_with_selectors(self, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """使用指定选择器提取搜索结果"""
        try:
            results = []
            
            # 等待结果加载
            await self.page.wait_for_selector(selectors["results"], timeout=10000)
            
            result_items = await self.page.query_selector_all(selectors["results"])
            
            for item in result_items:
                try:
                    # 提取标题和链接
                    title_element = await item.query_selector(selectors["title"])
                    if not title_element:
                        continue
                    
                    title = await title_element.inner_text()
                    link = await title_element.get_attribute("href")
                    
                    # 提取摘要
                    summary_element = await item.query_selector(selectors["summary"])
                    summary = ""
                    if summary_element:
                        summary = await summary_element.inner_text()
                    
                    # 提取作者
                    author_element = await item.query_selector(selectors["author"])
                    author = ""
                    if author_element:
                        author = await author_element.inner_text()
                    
                    result = {
                        "title": title.strip(),
                        "link": link,
                        "summary": summary.strip(),
                        "author": author.strip(),
                        "publish_time": "",
                        "source": "third_party"
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"提取结果失败: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"使用选择器提取结果失败: {e}")
            return []
    
    async def run_experiment(self, query: str, headless: bool = False) -> Dict[str, Any]:
        """运行完整的搜索实验"""
        try:
            self.logger.info(f"开始微信公众号搜索实验: {query}")
            
            # 设置浏览器
            if not await self.setup_browser(headless):
                return {
                    "status": "error",
                    "message": "浏览器设置失败"
                }
            
            # 尝试不同的搜索方法
            methods = [
                ("搜狗微信搜索", self.method1_sogou_wechat_search),
                ("微信PC版搜索", self.method2_wechat_pc_search),
                ("第三方平台搜索", self.method3_third_party_search)
            ]
            
            results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "methods": {}
            }
            
            for method_name, method_func in methods:
                try:
                    self.logger.info(f"尝试方法: {method_name}")
                    result = await method_func(query)
                    results["methods"][method_name] = result
                    
                    # 如果成功找到结果，可以提前结束
                    if result["status"] == "success" and result.get("results"):
                        self.logger.info(f"方法 {method_name} 成功找到 {len(result['results'])} 个结果")
                    
                except Exception as e:
                    self.logger.error(f"方法 {method_name} 执行失败: {e}")
                    results["methods"][method_name] = {
                        "status": "error",
                        "message": f"执行失败: {str(e)}"
                    }
            
            # 统计总结果
            total_results = 0
            successful_methods = 0
            
            for method_name, method_result in results["methods"].items():
                if method_result["status"] == "success":
                    successful_methods += 1
                    if "results" in method_result:
                        total_results += len(method_result["results"])
            
            results["summary"] = {
                "total_results": total_results,
                "successful_methods": successful_methods,
                "total_methods": len(methods)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"实验执行失败: {e}")
            return {
                "status": "error",
                "message": f"实验执行失败: {str(e)}",
                "error": str(e)
            }
        
        finally:
            # 清理资源
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()


async def main():
    """主函数"""
    print("🔬 微信公众号搜索实验")
    print("=" * 50)
    
    # 创建实验实例
    experiment = WeChatSearchExperiment()
    
    # 测试查询
    test_queries = [
        "Python编程",
        "机器学习",
        "人工智能"
    ]
    
    for query in test_queries:
        print(f"\n🔍 测试查询: {query}")
        print("-" * 30)
        
        # 运行实验
        result = await experiment.run_experiment(query, headless=False)
        
        # 显示结果
        if result.get("summary"):
            summary = result["summary"]
            print(f"✅ 成功方法数: {summary['successful_methods']}/{summary['total_methods']}")
            print(f"📊 总结果数: {summary['total_results']}")
        
        # 显示各方法结果
        for method_name, method_result in result.get("methods", {}).items():
            status = method_result["status"]
            message = method_result["message"]
            
            if status == "success":
                results_count = len(method_result.get("results", []))
                print(f"  ✅ {method_name}: {message} ({results_count}个结果)")
            elif status == "waiting":
                print(f"  ⏳ {method_name}: {message}")
            else:
                print(f"  ❌ {method_name}: {message}")
        
        # 保存结果到文件
        output_file = Path(__file__).parent / f"wechat_search_result_{query}_{int(datetime.now().timestamp())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📁 结果已保存到: {output_file}")
        
        # 等待用户确认
        input("\n按回车键继续下一个测试...")


if __name__ == "__main__":
    asyncio.run(main())

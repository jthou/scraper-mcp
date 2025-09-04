#!/usr/bin/env python3
"""
搜狗微信搜索简化版

这是一个简化的搜狗微信搜索实现，用于快速验证和测试
"""

import asyncio
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from playwright.async_api import async_playwright


class SimpleSogouSearch:
    """简化的搜狗微信搜索类"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def setup(self, headless: bool = True):
        """设置浏览器环境"""
        try:
            self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                channel="chrome",
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--disable-sync"
                ]
            )
            
            self.page = await self.browser.new_page()
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            return True
            
        except Exception as e:
            print(f"❌ 浏览器设置失败: {e}")
            return False
    
    async def search(self, query: str, max_pages: int = 3) -> Dict[str, Any]:
        """执行搜索，支持多页翻页"""
        try:
            print(f"🔍 搜索: {query} (最多{max_pages}页)")
            
            # 构建搜索URL
            search_url = f"https://weixin.sogou.com/weixin?type=2&query={query}"
            
            # 访问搜索页面
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            
            # 等待结果加载
            await self.page.wait_for_timeout(3000)
            
            # 检查验证码
            captcha = await self.page.query_selector(".captcha, .verify-code, .slider")
            if captcha:
                return {
                    "status": "error",
                    "message": "需要验证码，无法自动搜索",
                    "url": search_url
                }
            
            # 收集所有页面的结果
            all_results = []
            all_links = []
            
            for page_num in range(1, max_pages + 1):
                print(f"  📄 正在搜索第 {page_num} 页...")
                
                # 提取当前页结果
                page_results = await self._extract_page_results()
                all_results.extend(page_results)
                
                # 记录当前页的链接
                page_links = [result['link'] for result in page_results if result.get('link')]
                all_links.extend(page_links)
                
                print(f"  ✅ 第 {page_num} 页找到 {len(page_results)} 个结果")
                
                # 如果不是最后一页，尝试翻页
                if page_num < max_pages:
                    next_page_success = await self._go_to_next_page(page_num + 1)
                    if not next_page_success:
                        print(f"  ⚠️ 无法翻页到第 {page_num + 1} 页，停止搜索")
                        break
                    
                    # 页面间等待
                    await self.page.wait_for_timeout(2000)
            
            # 去重链接
            unique_links = list(set(all_links))
            
            print(f"📊 搜索完成: 共找到 {len(all_results)} 个结果，{len(unique_links)} 个唯一链接")
            
            return {
                "status": "success",
                "message": f"找到 {len(all_results)} 个结果，{len(unique_links)} 个唯一链接",
                "query": query,
                "url": search_url,
                "total_results": len(all_results),
                "unique_links": len(unique_links),
                "pages_searched": min(page_num, max_pages),
                "all_links": unique_links,  # 记录所有唯一链接
                "results": all_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索失败: {str(e)}",
                "query": query
            }
    
    async def _extract_page_results(self) -> List[Dict[str, Any]]:
        """提取当前页的搜索结果"""
        try:
            results = []
            
            # 等待页面加载
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(2000)
            
            # 调试：检查页面内容
            page_title = await self.page.title()
            print(f"  🔍 页面标题: {page_title}")
            
            # 检查是否有验证码
            captcha_elements = await self.page.query_selector_all(".captcha, .verify-code, .slider, .geetest")
            if captcha_elements:
                print(f"  ⚠️ 检测到验证码元素: {len(captcha_elements)}个")
                return []
            
            # 使用调试发现的有效选择器
            result_items = await self.page.query_selector_all(".txt-box")
            print(f"  ✅ 使用选择器 '.txt-box' 找到 {len(result_items)} 个结果")
            
            if not result_items:
                print(f"  ❌ 未找到任何结果元素")
                # 保存页面截图用于调试
                screenshot_path = Path(__file__).parent / f"debug_screenshot_{int(datetime.now().timestamp())}.png"
                await self.page.screenshot(path=str(screenshot_path))
                print(f"  📸 已保存调试截图: {screenshot_path}")
                return []
            
            for item in result_items:
                try:
                    result = await self._extract_single_result(item)
                    if result:
                        results.append(result)
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            print(f"  ❌ 提取页面结果失败: {e}")
            return []
    
    async def _extract_single_result(self, item) -> Optional[Dict[str, Any]]:
        """提取单个搜索结果"""
        try:
            # 在 .txt-box 内部查找标题和链接
            title_element = await item.query_selector("h3 a")
            if not title_element:
                return None
            
            title = await title_element.inner_text()
            link = await title_element.get_attribute("href")
            
            # 处理搜狗的重定向链接
            if link and link.startswith("/link?"):
                # 这是搜狗的重定向链接，需要进一步处理
                # 暂时保持原样，实际使用时需要解析重定向
                link = f"https://weixin.sogou.com{link}"
            
            # 提取摘要 - 在 .txt-box 内部查找
            summary_element = await item.query_selector(".txt-info")
            summary = ""
            if summary_element:
                summary = await summary_element.inner_text()
            
            # 提取作者信息
            author_element = await item.query_selector(".s-p .account")
            author = ""
            if author_element:
                author = await author_element.inner_text()
            
            # 提取发布时间
            time_element = await item.query_selector(".s-p .s2")
            publish_time = ""
            if time_element:
                publish_time = await time_element.inner_text()
            
            # 提取公众号名称
            account_element = await item.query_selector(".s-p .account")
            account_name = ""
            if account_element:
                account_name = await account_element.inner_text()
            
            # 提取阅读数
            read_element = await item.query_selector(".s-p .s3")
            read_count = ""
            if read_element:
                read_count = await read_element.inner_text()
            
            return {
                "title": title.strip(),
                "link": link,
                "summary": summary.strip()[:200] + "..." if len(summary.strip()) > 200 else summary.strip(),
                "author": author.strip(),
                "account_name": account_name.strip(),
                "publish_time": publish_time.strip(),
                "read_count": read_count.strip()
            }
            
        except Exception as e:
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
                        
                        return True
                except Exception:
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
                
                return True
                
            except Exception:
                return False
            
        except Exception as e:
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"清理资源失败: {e}")


async def main():
    """主函数"""
    print("🔍 搜狗微信搜索简化版测试")
    print("=" * 40)
    
    # 创建搜索实例
    searcher = SimpleSogouSearch()
    
    try:
        # 设置浏览器
        if not await searcher.setup(headless=False):
            print("❌ 浏览器设置失败")
            return
        
        # 测试查询
        test_queries = [
            "Python编程",
            "机器学习",
            "人工智能"
        ]
        
        all_results = {
            "timestamp": datetime.now().isoformat(),
            "queries": {},
            "all_links_summary": {}
        }
        
        for query in test_queries:
            print(f"\n🔍 搜索: {query}")
            print("-" * 30)
            
            # 执行搜索（支持多页）
            result = await searcher.search(query, max_pages=2)
            all_results["queries"][query] = result
            
            # 显示结果
            if result["status"] == "success":
                print(f"✅ {result['message']}")
                print(f"🔗 搜索URL: {result['url']}")
                print(f"📊 总结果数: {result['total_results']}")
                print(f"🔗 唯一链接数: {result['unique_links']}")
                print(f"📄 搜索页数: {result['pages_searched']}")
                
                # 显示所有链接
                if result.get('all_links'):
                    print(f"\n📋 所有搜索到的链接 ({len(result['all_links'])}个):")
                    for i, link in enumerate(result['all_links'], 1):
                        print(f"  {i}. {link}")
                
                # 显示前3个详细结果
                print(f"\n📄 前3个详细结果:")
                for i, item in enumerate(result.get('results', [])[:3], 1):
                    print(f"\n{i}. {item['title']}")
                    print(f"   作者: {item['author']}")
                    print(f"   时间: {item['publish_time']}")
                    print(f"   摘要: {item['summary']}")
                    print(f"   链接: {item['link']}")
                
                # 记录链接摘要
                all_results["all_links_summary"][query] = {
                    "total_links": len(result['all_links']),
                    "links": result['all_links']
                }
            else:
                print(f"❌ {result['message']}")
            
            # 等待用户确认
            input("\n按回车键继续下一个搜索...")
        
        # 保存所有结果
        output_file = Path(__file__).parent / f"sogou_search_simple_results_{int(datetime.now().timestamp())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 所有结果已保存到: {output_file}")
        print("🎉 测试完成！")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
    finally:
        await searcher.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

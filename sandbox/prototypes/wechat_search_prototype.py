#!/usr/bin/env python3
"""
微信公众号搜索原型

这是一个简化的原型实现，用于快速验证微信公众号搜索的可行性
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from playwright.async_api import async_playwright


class WeChatSearchPrototype:
    """微信公众号搜索原型类"""
    
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
    
    async def search_sogou(self, query: str) -> Dict[str, Any]:
        """搜狗微信搜索原型"""
        try:
            print(f"🔍 搜索: {query}")
            
            # 构建搜索URL
            search_url = f"https://weixin.sogou.com/weixin?type=2&query={query}"
            
            # 访问搜索页面
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            
            # 等待结果加载
            await self.page.wait_for_timeout(3000)
            
            # 检查是否需要验证码
            captcha = await self.page.query_selector(".captcha, .verify-code")
            if captcha:
                return {
                    "status": "error",
                    "message": "需要验证码",
                    "url": search_url
                }
            
            # 提取搜索结果
            results = []
            result_items = await self.page.query_selector_all(".results .result")
            
            for item in result_items[:5]:  # 只取前5个结果
                try:
                    title_element = await item.query_selector(".txt-box h3 a")
                    if not title_element:
                        continue
                    
                    title = await title_element.inner_text()
                    link = await title_element.get_attribute("href")
                    
                    summary_element = await item.query_selector(".txt-box .txt-info")
                    summary = ""
                    if summary_element:
                        summary = await summary_element.inner_text()
                    
                    author_element = await item.query_selector(".txt-box .s-p .account")
                    author = ""
                    if author_element:
                        author = await author_element.inner_text()
                    
                    results.append({
                        "title": title.strip(),
                        "link": link,
                        "summary": summary.strip()[:100] + "..." if len(summary.strip()) > 100 else summary.strip(),
                        "author": author.strip()
                    })
                    
                except Exception as e:
                    continue
            
            return {
                "status": "success",
                "message": f"找到 {len(results)} 个结果",
                "query": query,
                "url": search_url,
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索失败: {str(e)}",
                "query": query
            }
    
    async def test_search(self, query: str) -> Dict[str, Any]:
        """测试搜索功能"""
        try:
            # 设置浏览器
            if not await self.setup(headless=False):
                return {"status": "error", "message": "浏览器设置失败"}
            
            # 执行搜索
            result = await self.search_sogou(query)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"测试失败: {str(e)}"
            }
        
        finally:
            # 清理资源
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """保存搜索结果"""
        if not filename:
            filename = f"wechat_search_results_{int(asyncio.get_event_loop().time())}.json"
        
        output_path = Path(__file__).parent / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 结果已保存到: {output_path}")
        return str(output_path)


async def main():
    """主函数"""
    print("🚀 微信公众号搜索原型测试")
    print("=" * 40)
    
    # 创建原型实例
    prototype = WeChatSearchPrototype()
    
    # 测试查询
    test_queries = [
        "Python编程",
        "机器学习",
        "人工智能"
    ]
    
    all_results = {
        "timestamp": asyncio.get_event_loop().time(),
        "queries": {}
    }
    
    for query in test_queries:
        print(f"\n🔍 测试查询: {query}")
        print("-" * 30)
        
        # 执行搜索
        result = await prototype.test_search(query)
        all_results["queries"][query] = result
        
        # 显示结果
        if result["status"] == "success":
            print(f"✅ {result['message']}")
            print(f"🔗 搜索URL: {result['url']}")
            
            # 显示前3个结果
            for i, item in enumerate(result.get('results', [])[:3], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   作者: {item['author']}")
                print(f"   摘要: {item['summary']}")
                print(f"   链接: {item['link']}")
        else:
            print(f"❌ {result['message']}")
        
        # 等待用户确认
        input("\n按回车键继续下一个测试...")
    
    # 保存所有结果
    prototype.save_results(all_results, "wechat_search_prototype_results.json")
    
    print("\n🎉 原型测试完成！")


if __name__ == "__main__":
    asyncio.run(main())

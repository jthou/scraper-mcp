#!/usr/bin/env python3
"""
搜狗微信搜索调试版

专门用于调试搜狗搜索的页面结构和选择器
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


class SogouSearchDebug:
    """搜狗搜索调试类"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def setup(self, headless: bool = False):
        """设置浏览器环境"""
        try:
            self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                channel="chrome",
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--disable-sync",
                    "--disable-web-security"
                ]
            )
            
            self.page = await self.browser.new_page()
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            return True
            
        except Exception as e:
            print(f"❌ 浏览器设置失败: {e}")
            return False
    
    async def debug_page_structure(self, query: str):
        """调试页面结构"""
        try:
            print(f"🔍 调试搜索: {query}")
            
            # 构建搜索URL
            search_url = f"https://weixin.sogou.com/weixin?type=2&query={query}"
            
            # 访问搜索页面
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(5000)
            
            # 获取页面基本信息
            page_title = await self.page.title()
            page_url = self.page.url
            
            print(f"📄 页面标题: {page_title}")
            print(f"🔗 当前URL: {page_url}")
            
            # 检查页面内容
            page_content = await self.page.content()
            print(f"📏 页面内容长度: {len(page_content)} 字符")
            
            # 检查是否有验证码
            captcha_selectors = [
                ".captcha", ".verify-code", ".slider", ".geetest", 
                ".nc-container", "#captcha", ".captcha-container"
            ]
            
            for selector in captcha_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    print(f"⚠️ 发现验证码元素: {selector} ({len(elements)}个)")
            
            # 尝试多种可能的选择器
            possible_selectors = [
                # 搜狗微信搜索的可能选择器
                ".results .result",
                ".result",
                ".search-result",
                ".wx-article",
                ".article-item",
                ".txt-box",
                ".sogou-result",
                ".weixin-result",
                ".content-item",
                ".list-item",
                ".item",
                # 更通用的选择器
                "article",
                ".article",
                "[data-testid*='result']",
                "[class*='result']",
                "[class*='article']",
                "[class*='item']",
                "h3 a",
                ".title a",
                "a[href*='mp.weixin.qq.com']"
            ]
            
            print(f"\n🔍 尝试 {len(possible_selectors)} 个选择器:")
            found_selectors = []
            
            for selector in possible_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        print(f"  ✅ {selector}: {len(elements)} 个元素")
                        found_selectors.append((selector, len(elements)))
                    else:
                        print(f"  ❌ {selector}: 0 个元素")
                except Exception as e:
                    print(f"  💥 {selector}: 错误 - {e}")
            
            # 如果找到元素，尝试提取内容
            if found_selectors:
                print(f"\n📋 找到 {len(found_selectors)} 个有效的选择器:")
                for selector, count in found_selectors:
                    print(f"  - {selector}: {count} 个元素")
                    
                    # 尝试提取前3个元素的内容
                    try:
                        elements = await self.page.query_selector_all(selector)
                        for i, element in enumerate(elements[:3]):
                            try:
                                text = await element.inner_text()
                                href = await element.get_attribute("href")
                                print(f"    元素 {i+1}:")
                                print(f"      文本: {text[:100]}...")
                                print(f"      链接: {href}")
                            except Exception as e:
                                print(f"      提取失败: {e}")
                    except Exception as e:
                        print(f"    提取内容失败: {e}")
            
            # 保存页面截图
            screenshot_path = Path(__file__).parent / f"debug_screenshot_{query}_{int(datetime.now().timestamp())}.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"\n📸 已保存完整页面截图: {screenshot_path}")
            
            # 保存页面HTML
            html_path = Path(__file__).parent / f"debug_html_{query}_{int(datetime.now().timestamp())}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            print(f"📄 已保存页面HTML: {html_path}")
            
            return {
                "status": "success",
                "page_title": page_title,
                "page_url": page_url,
                "content_length": len(page_content),
                "found_selectors": found_selectors,
                "screenshot": str(screenshot_path),
                "html_file": str(html_path)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"调试失败: {str(e)}",
                "error": str(e)
            }
    
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
    print("🔍 搜狗微信搜索调试版")
    print("=" * 40)
    
    # 创建调试实例
    debugger = SogouSearchDebug()
    
    try:
        # 设置浏览器
        if not await debugger.setup(headless=False):
            print("❌ 浏览器设置失败")
            return
        
        # 调试查询
        test_queries = [
            "Python编程",
            "机器学习"
        ]
        
        all_debug_results = {
            "timestamp": datetime.now().isoformat(),
            "debug_results": {}
        }
        
        for query in test_queries:
            print(f"\n🔍 调试查询: {query}")
            print("-" * 30)
            
            # 执行调试
            result = await debugger.debug_page_structure(query)
            all_debug_results["debug_results"][query] = result
            
            if result["status"] == "success":
                print(f"✅ 调试完成")
                print(f"📊 找到 {len(result['found_selectors'])} 个有效选择器")
            else:
                print(f"❌ 调试失败: {result['message']}")
            
            # 等待用户确认
            input("\n按回车键继续下一个调试...")
        
        # 保存调试结果
        output_file = Path(__file__).parent / f"sogou_search_debug_results_{int(datetime.now().timestamp())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_debug_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 调试结果已保存到: {output_file}")
        print("🎉 调试完成！")
        
    except KeyboardInterrupt:
        print("\n⏹️ 调试被用户中断")
    except Exception as e:
        print(f"\n💥 调试过程中发生错误: {e}")
    finally:
        await debugger.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

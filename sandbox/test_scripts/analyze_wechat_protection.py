#!/usr/bin/env python3
"""
微信反爬虫机制分析

分析微信在PDF转换和内容抓取方面的保护机制
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.wechat_scraper import WeChatScraper


async def analyze_wechat_protection():
    """分析微信的反爬虫机制"""
    print("🔍 微信反爬虫机制分析")
    print("=" * 50)
    
    scraper = WeChatScraper()
    
    try:
        # 设置浏览器
        print("\n1. 设置浏览器...")
        setup_result = await scraper.setup_browser(headless=False, persistent=False)
        print(f"   结果: {setup_result}")
        
        if setup_result["status"] != "success":
            print("❌ 浏览器设置失败，无法继续测试")
            return
        
        # 测试不同的网站
        test_sites = [
            {
                "name": "百度",
                "url": "https://www.baidu.com",
                "expected": "正常网站，应该能正常生成PDF"
            },
            {
                "name": "知乎",
                "url": "https://www.zhihu.com",
                "expected": "知乎可能有反爬虫，但应该能生成PDF"
            },
            {
                "name": "搜狗微信搜索",
                "url": "https://weixin.sogou.com",
                "expected": "搜狗可能有反爬虫机制"
            }
        ]
        
        for site in test_sites:
            print(f"\n2. 测试 {site['name']}...")
            print(f"   URL: {site['url']}")
            print(f"   预期: {site['expected']}")
            
            try:
                # 访问页面
                await scraper.page.goto(site['url'])
                await scraper.page.wait_for_load_state("networkidle")
                
                # 等待页面加载
                await asyncio.sleep(3)
                
                # 获取页面信息
                title = await scraper.page.title()
                url = scraper.page.url
                
                print(f"   页面标题: {title}")
                print(f"   当前URL: {url}")
                
                # 检查是否有反爬虫机制
                content = await scraper.page.content()
                
                # 检查常见的反爬虫关键词
                anti_crawl_keywords = [
                    "验证码", "captcha", "安全验证", "请依次点击",
                    "检测到异常访问", "访问过于频繁", "需要验证",
                    "robot", "bot", "自动化", "爬虫"
                ]
                
                found_keywords = [kw for kw in anti_crawl_keywords if kw in content]
                if found_keywords:
                    print(f"   ⚠️ 检测到反爬虫关键词: {found_keywords}")
                else:
                    print(f"   ✅ 未检测到明显的反爬虫机制")
                
                # 尝试生成PDF
                print(f"   尝试生成PDF...")
                pdf_result = await scraper.print_page_to_pdf(site['url'])
                
                if pdf_result["status"] == "success":
                    print(f"   ✅ PDF生成成功")
                    print(f"   📁 文件路径: {pdf_result['pdf_path']}")
                    
                    # 检查PDF文件
                    pdf_path = Path(pdf_result['pdf_path'])
                    if pdf_path.exists():
                        file_size = pdf_path.stat().st_size
                        print(f"   📊 文件大小: {file_size} 字节")
                        
                        # 如果文件太小，可能是验证码页面
                        if file_size < 50000:  # 小于50KB
                            print(f"   ⚠️ 文件较小，可能是验证码页面")
                else:
                    print(f"   ❌ PDF生成失败: {pdf_result['message']}")
                
                print(f"   {'='*40}")
                
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        
        # 专门测试微信文章链接
        print(f"\n3. 测试微信文章链接...")
        
        # 使用一个真实的微信文章链接进行测试
        wechat_test_urls = [
            "https://mp.weixin.qq.com/s/example1",  # 示例链接
        ]
        
        for url in wechat_test_urls:
            print(f"   测试URL: {url}")
            try:
                # 访问微信文章
                await scraper.page.goto(url)
                await scraper.page.wait_for_load_state("networkidle")
                
                # 等待页面加载
                await asyncio.sleep(5)
                
                # 获取页面信息
                title = await scraper.page.title()
                current_url = scraper.page.url
                
                print(f"   页面标题: {title}")
                print(f"   当前URL: {current_url}")
                
                # 检查是否被重定向到验证页面
                if "验证" in title or "captcha" in title.lower():
                    print(f"   ⚠️ 页面被重定向到验证页面")
                
                # 检查页面内容
                content = await scraper.page.content()
                
                # 检查微信特有的保护机制
                wechat_protection_keywords = [
                    "请在微信客户端打开", "请在微信中打开",
                    "微信安全验证", "微信访问验证",
                    "请在微信中查看", "微信客户端"
                ]
                
                found_protection = [kw for kw in wechat_protection_keywords if kw in content]
                if found_protection:
                    print(f"   ⚠️ 检测到微信保护机制: {found_protection}")
                
                # 尝试生成PDF
                print(f"   尝试生成PDF...")
                pdf_result = await scraper.print_page_to_pdf(url)
                
                if pdf_result["status"] == "success":
                    print(f"   ✅ PDF生成成功")
                    print(f"   📁 文件路径: {pdf_result['pdf_path']}")
                    
                    # 检查PDF文件
                    pdf_path = Path(pdf_result['pdf_path'])
                    if pdf_path.exists():
                        file_size = pdf_path.stat().st_size
                        print(f"   📊 文件大小: {file_size} 字节")
                else:
                    print(f"   ❌ PDF生成失败: {pdf_result['message']}")
                
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        
        # 分析总结
        print(f"\n4. 分析总结:")
        print(f"   🔍 微信可能的反爬虫机制:")
        print(f"   - 1. 重定向到验证码页面")
        print(f"   - 2. 检测自动化访问特征")
        print(f"   - 3. 要求微信客户端打开")
        print(f"   - 4. 动态加载内容，PDF生成时内容为空")
        print(f"   - 5. 使用JavaScript渲染，需要等待时间")
        print(f"   - 6. 检测浏览器指纹和用户代理")
        
        print(f"\n   💡 可能的解决方案:")
        print(f"   - 1. 使用更真实的浏览器环境")
        print(f"   - 2. 模拟微信客户端的请求头")
        print(f"   - 3. 使用代理IP轮换")
        print(f"   - 4. 增加更长的等待时间")
        print(f"   - 5. 使用无头浏览器但模拟真实用户行为")
        print(f"   - 6. 直接使用微信API（如果有权限）")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("\n5. 清理资源...")
        try:
            await scraper.cleanup()
            print("   ✅ 资源清理完成")
        except Exception as e:
            print(f"   ⚠️ 资源清理警告: {e}")
    
    print("\n🎉 微信反爬虫机制分析完成！")


async def main():
    """主函数"""
    try:
        await analyze_wechat_protection()
    except KeyboardInterrupt:
        print("\n⏹️ 分析被用户中断")
    except Exception as e:
        print(f"\n💥 分析过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

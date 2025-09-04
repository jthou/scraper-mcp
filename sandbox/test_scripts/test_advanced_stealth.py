#!/usr/bin/env python3
"""
高级反爬虫策略测试

测试改进后的反爬虫技术
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.wechat_scraper import WeChatScraper


async def test_advanced_stealth():
    """测试高级反爬虫策略"""
    print("🕵️ 高级反爬虫策略测试")
    print("=" * 50)
    
    scraper = WeChatScraper()
    
    try:
        # 设置高级隐身浏览器
        print("\n1. 设置高级隐身浏览器...")
        setup_result = await scraper.setup_browser(headless=False, persistent=False)
        print(f"   结果: {setup_result}")
        
        if setup_result["status"] != "success":
            print("❌ 浏览器设置失败，无法继续测试")
            return
        
        # 创建输出目录
        output_dir = Path(__file__).parent / "advanced_stealth_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 测试搜索功能
        print("\n3. 测试高级反爬虫搜索...")
        search_result = await scraper.search_wechat("Python编程", max_pages=1)
        
        print(f"\n4. 搜索结果:")
        print(f"   状态: {search_result['status']}")
        print(f"   消息: {search_result['message']}")
        
        if search_result["status"] == "success":
            print(f"   ✅ 搜索成功!")
            print(f"   总结果数: {search_result['total_results']}")
            print(f"   搜索页面数: {search_result['pages_searched']}")
            print(f"   唯一链接数: {search_result['unique_links']}")
            
            # 显示前3个结果
            results = search_result.get('results', [])
            if results:
                print(f"\n5. 前3个搜索结果:")
                for i, item in enumerate(results[:3], 1):
                    print(f"   {i}. {item['title']}")
                    print(f"      作者: {item['author']}")
                    print(f"      公众号: {item['account_name']}")
                    print(f"      链接: {item['link'][:80]}...")
                    print()
                
                # 尝试下载第一个结果
                if results:
                    first_result = results[0]
                    print(f"6. 尝试下载第一个结果...")
                    print(f"   标题: {first_result['title']}")
                    
                    download_result = await scraper.download_and_save_content(
                        first_result['link'], 
                        output_dir, 
                        first_result['title']
                    )
                    
                    print(f"\n7. 下载结果:")
                    print(f"   状态: {download_result['status']}")
                    print(f"   消息: {download_result['message']}")
                    
                    if download_result["status"] == "success":
                        print(f"   ✅ 下载成功!")
                        print(f"   📁 PDF: {download_result['files']['pdf']}")
                        print(f"   📄 Markdown: {download_result['files']['markdown']}")
                        
                        # 显示下载目录结构
                        print(f"\n8. 下载目录结构:")
                        print(f"   📁 {output_dir}")
                        if output_dir.exists():
                            for item in output_dir.rglob("*"):
                                if item.is_file():
                                    print(f"      📄 {item.relative_to(output_dir)}")
                    else:
                        print(f"   ❌ 下载失败: {download_result['message']}")
                        
                        # 分析失败原因
                        if "验证码" in download_result.get('message', ''):
                            print(f"\n💡 分析:")
                            print(f"   - 搜狗检测到自动化访问")
                            print(f"   - 需要更高级的反爬虫策略")
                            print(f"   - 建议使用代理或更长的等待时间")
                        elif "重定向" in download_result.get('message', ''):
                            print(f"\n💡 分析:")
                            print(f"   - 重定向链接处理需要改进")
                            print(f"   - 可能需要手动处理验证码")
            else:
                print(f"   ❌ 没有找到搜索结果")
        else:
            print(f"   ❌ 搜索失败: {search_result['message']}")
            
            # 分析失败原因
            if "验证码" in search_result.get('message', ''):
                print(f"\n💡 分析:")
                print(f"   - 搜狗检测到自动化访问")
                print(f"   - 需要更高级的反爬虫策略")
                print(f"   - 建议使用代理或更长的等待时间")
            elif "bypass_attempted" in search_result:
                print(f"\n💡 分析:")
                print(f"   - 已尝试绕过验证码")
                print(f"   - 可能需要人工干预")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("\n9. 清理资源...")
        try:
            await scraper.cleanup()
            print("   ✅ 资源清理完成")
        except Exception as e:
            print(f"   ⚠️ 资源清理警告: {e}")
    
    print("\n🎉 高级反爬虫策略测试完成！")


async def main():
    """主函数"""
    try:
        await test_advanced_stealth()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

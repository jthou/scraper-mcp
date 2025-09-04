#!/usr/bin/env python3
"""
微信内容搜索示例

演示如何使用ScraperToolkit搜索微信内容（需要人工验证）
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform


async def search_wechat_content():
    """搜索微信内容示例"""
    print("🔍 微信内容搜索示例")
    print("=" * 40)
    
    # 创建配置
    config = ScrapingConfig(
        platform=Platform.WECHAT,
        headless=False,  # 必须显示浏览器窗口，因为需要人工验证
        persistent=False,
        max_pages=1,
        output_dir=Path("data/wechat"),
        wait_for_verification=True  # 等待人工验证
    )
    
    # 创建工具包实例
    toolkit = ScraperToolkit(config)
    
    try:
        # 1. 设置浏览器
        print("\n1. 设置浏览器...")
        setup_result = await toolkit.setup_browser(Platform.WECHAT)
        print(f"   结果: {setup_result}")
        
        if setup_result["status"] != "success":
            print("❌ 浏览器设置失败，无法继续")
            return
        
        # 2. 搜索内容
        query = "Python编程"
        print(f"\n2. 搜索微信内容: {query}")
        print("   ⚠️ 注意：微信搜索需要人工验证码验证")
        print("   💡 请在浏览器中完成验证码验证")
        
        search_result = await toolkit.search(Platform.WECHAT, query, max_pages=1)
        
        if search_result["status"] == "success":
            print(f"   ✅ 搜索成功!")
            print(f"   总结果数: {search_result['total_results']}")
            print(f"   搜索页面数: {search_result['pages_searched']}")
            
            # 显示前3个结果
            results = search_result.get('results', [])
            if results:
                print(f"\n3. 前3个搜索结果:")
                for i, item in enumerate(results[:3], 1):
                    print(f"   {i}. {item['title']}")
                    print(f"      作者: {item['author']}")
                    print(f"      公众号: {item['account_name']}")
                    print(f"      链接: {item['link']}")
                    print(f"      摘要: {item['summary'][:100]}...")
                    print()
                
                # 3. 下载第一个结果
                if results:
                    first_result = results[0]
                    print(f"4. 下载第一个结果...")
                    print(f"   标题: {first_result['title']}")
                    print("   ⚠️ 注意：下载过程可能需要再次验证")
                    
                    download_result = await toolkit.download_content(
                        Platform.WECHAT,
                        first_result['link'],
                        Path("data/wechat"),
                        first_result['title']
                    )
                    
                    if download_result["status"] == "success":
                        print(f"   ✅ 下载成功!")
                        print(f"   📁 PDF: {download_result['files']['pdf']}")
                        print(f"   📄 Markdown: {download_result['files']['markdown']}")
                    else:
                        print(f"   ❌ 下载失败: {download_result['message']}")
            else:
                print(f"   ❌ 没有找到搜索结果")
        else:
            print(f"   ❌ 搜索失败: {search_result['message']}")
    
    except Exception as e:
        print(f"❌ 示例执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("\n5. 清理资源...")
        await toolkit.cleanup()
        print("   ✅ 资源清理完成")
    
    print("\n🎉 微信内容搜索示例完成！")


async def main():
    """主函数"""
    try:
        await search_wechat_content()
    except KeyboardInterrupt:
        print("\n⏹️ 示例被用户中断")
    except Exception as e:
        print(f"\n💥 示例执行过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

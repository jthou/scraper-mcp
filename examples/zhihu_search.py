#!/usr/bin/env python3
"""
知乎内容搜索示例

演示如何使用ScraperToolkit搜索知乎内容
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform


async def search_zhihu_content():
    """搜索知乎内容示例"""
    print("🔍 知乎内容搜索示例")
    print("=" * 40)
    
    # 创建配置
    config = ScrapingConfig(
        platform=Platform.ZHIHU,
        headless=False,  # 显示浏览器窗口
        persistent=False,
        max_pages=2,
        output_dir=Path("data/zhihu")
    )
    
    # 创建工具包实例
    toolkit = ScraperToolkit(config)
    
    try:
        # 1. 设置浏览器
        print("\n1. 设置浏览器...")
        setup_result = await toolkit.setup_browser(Platform.ZHIHU)
        print(f"   结果: {setup_result}")
        
        if setup_result["status"] != "success":
            print("❌ 浏览器设置失败，无法继续")
            return
        
        # 2. 搜索内容
        query = "RTX 5080"
        print(f"\n2. 搜索知乎内容: {query}")
        search_result = await toolkit.search(Platform.ZHIHU, query, max_pages=2)
        
        if search_result["status"] == "success":
            print(f"   ✅ 搜索成功!")
            print(f"   总结果数: {search_result['total_results']}")
            
            # 显示前3个结果
            results = search_result.get('results', [])
            if results:
                print(f"\n3. 前3个搜索结果:")
                for i, item in enumerate(results[:3], 1):
                    print(f"   {i}. {item['title']}")
                    print(f"      作者: {item['author']}")
                    print(f"      链接: {item['url']}")
                    print(f"      摘要: {item['summary'][:100]}...")
                    print()
                
                # 3. 下载第一个结果
                if results:
                    first_result = results[0]
                    print(f"4. 下载第一个结果...")
                    print(f"   标题: {first_result['title']}")
                    
                    download_result = await toolkit.download_content(
                        Platform.ZHIHU,
                        first_result['url'],
                        Path("data/zhihu"),
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
    
    print("\n🎉 知乎内容搜索示例完成！")


async def main():
    """主函数"""
    try:
        await search_zhihu_content()
    except KeyboardInterrupt:
        print("\n⏹️ 示例被用户中断")
    except Exception as e:
        print(f"\n💥 示例执行过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

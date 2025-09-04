#!/usr/bin/env python3
"""
快速使用示例

演示如何使用便捷函数快速进行搜索和下载
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.scraper_toolkit import quick_search, quick_download, quick_batch_download


async def quick_examples():
    """快速使用示例"""
    print("⚡ 快速使用示例")
    print("=" * 40)
    
    # 1. 快速搜索知乎内容
    print("\n1. 快速搜索知乎内容...")
    try:
        result = await quick_search("zhihu", "Python编程", max_pages=1, headless=False)
        print(f"   搜索结果: {result}")
        
        # 如果有结果，下载第一个
        if result.get("status") == "success" and result.get("results"):
            first_result = result["results"][0]
            print(f"\n2. 快速下载第一个结果...")
            print(f"   标题: {first_result['title']}")
            
            download_result = await quick_download(
                "zhihu",
                first_result["url"],
                "data/quick_zhihu",
                headless=False
            )
            print(f"   下载结果: {download_result}")
    except Exception as e:
        print(f"   ❌ 知乎搜索失败: {e}")
    
    # 2. 快速搜索微信内容
    print(f"\n3. 快速搜索微信内容...")
    try:
        result = await quick_search("wechat", "人工智能", max_pages=1, headless=False)
        print(f"   搜索结果: {result}")
        
        # 如果有结果，下载第一个
        if result.get("status") == "success" and result.get("results"):
            first_result = result["results"][0]
            print(f"\n4. 快速下载第一个结果...")
            print(f"   标题: {first_result['title']}")
            
            download_result = await quick_download(
                "wechat",
                first_result["link"],
                "data/quick_wechat",
                headless=False
            )
            print(f"   下载结果: {download_result}")
    except Exception as e:
        print(f"   ❌ 微信搜索失败: {e}")
    
    # 3. 快速批量下载
    print(f"\n5. 快速批量下载知乎内容...")
    try:
        result = await quick_batch_download(
            "zhihu",
            "机器学习",
            "data/quick_batch",
            max_pages=1,
            headless=False
        )
        print(f"   批量下载结果: {result}")
    except Exception as e:
        print(f"   ❌ 批量下载失败: {e}")
    
    print("\n🎉 快速使用示例完成！")


async def main():
    """主函数"""
    try:
        await quick_examples()
    except KeyboardInterrupt:
        print("\n⏹️ 示例被用户中断")
    except Exception as e:
        print(f"\n💥 示例执行过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

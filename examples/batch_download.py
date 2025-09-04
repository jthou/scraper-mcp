#!/usr/bin/env python3
"""
批量下载示例

演示如何使用ScraperToolkit批量下载搜索结果
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform


async def batch_download_zhihu():
    """批量下载知乎内容示例"""
    print("📥 知乎批量下载示例")
    print("=" * 40)
    
    # 创建配置
    config = ScrapingConfig(
        platform=Platform.ZHIHU,
        headless=False,
        persistent=False,
        max_pages=2,
        output_dir=Path("data/zhihu_batch")
    )
    
    # 创建工具包实例
    toolkit = ScraperToolkit(config)
    
    try:
        # 批量下载
        query = "机器学习"
        print(f"\n1. 批量下载知乎内容: {query}")
        print(f"   输出目录: {config.output_dir}")
        print(f"   最大页数: {config.max_pages}")
        
        result = await toolkit.batch_download(
            Platform.ZHIHU,
            query,
            config.output_dir,
            config.max_pages
        )
        
        if result["status"] == "success":
            print(f"   ✅ 批量下载成功!")
            print(f"   下载文件数: {result['downloaded_files']}")
            print(f"   成功文件数: {result['successful_downloads']}")
            print(f"   失败文件数: {result['failed_downloads']}")
            
            # 显示下载的文件
            if result.get('files'):
                print(f"\n2. 下载的文件:")
                for file_info in result['files']:
                    print(f"   📄 {file_info['title']}")
                    print(f"      PDF: {file_info['pdf_file']}")
                    print(f"      Markdown: {file_info['markdown_file']}")
                    print()
        else:
            print(f"   ❌ 批量下载失败: {result['message']}")
    
    except Exception as e:
        print(f"❌ 示例执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("\n3. 清理资源...")
        await toolkit.cleanup()
        print("   ✅ 资源清理完成")
    
    print("\n🎉 知乎批量下载示例完成！")


async def batch_download_wechat():
    """批量下载微信内容示例"""
    print("📥 微信批量下载示例")
    print("=" * 40)
    
    # 创建配置
    config = ScrapingConfig(
        platform=Platform.WECHAT,
        headless=False,  # 必须显示浏览器窗口
        persistent=False,
        max_pages=1,  # 微信搜索限制较多，只下载1页
        output_dir=Path("data/wechat_batch"),
        wait_for_verification=True
    )
    
    # 创建工具包实例
    toolkit = ScraperToolkit(config)
    
    try:
        # 批量下载
        query = "人工智能"
        print(f"\n1. 批量下载微信内容: {query}")
        print(f"   输出目录: {config.output_dir}")
        print(f"   最大页数: {config.max_pages}")
        print("   ⚠️ 注意：微信搜索需要人工验证码验证")
        
        result = await toolkit.batch_download(
            Platform.WECHAT,
            query,
            config.output_dir,
            config.max_pages
        )
        
        if result["status"] == "success":
            print(f"   ✅ 批量下载成功!")
            print(f"   下载文件数: {result['downloaded_files']}")
            print(f"   成功文件数: {result['successful_downloads']}")
            print(f"   失败文件数: {result['failed_downloads']}")
            
            # 显示下载的文件
            if result.get('files'):
                print(f"\n2. 下载的文件:")
                for file_info in result['files']:
                    print(f"   📄 {file_info['title']}")
                    print(f"      PDF: {file_info['pdf_file']}")
                    print(f"      Markdown: {file_info['markdown_file']}")
                    print()
        else:
            print(f"   ❌ 批量下载失败: {result['message']}")
    
    except Exception as e:
        print(f"❌ 示例执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("\n3. 清理资源...")
        await toolkit.cleanup()
        print("   ✅ 资源清理完成")
    
    print("\n🎉 微信批量下载示例完成！")


async def main():
    """主函数"""
    print("选择要运行的示例:")
    print("1. 知乎批量下载")
    print("2. 微信批量下载")
    print("3. 两个都运行")
    
    choice = input("\n请输入选择 (1-3): ").strip()
    
    try:
        if choice == "1":
            await batch_download_zhihu()
        elif choice == "2":
            await batch_download_wechat()
        elif choice == "3":
            await batch_download_zhihu()
            print("\n" + "="*60 + "\n")
            await batch_download_wechat()
        else:
            print("无效选择，运行知乎批量下载示例...")
            await batch_download_zhihu()
    except KeyboardInterrupt:
        print("\n⏹️ 示例被用户中断")
    except Exception as e:
        print(f"\n💥 示例执行过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

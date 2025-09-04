#!/usr/bin/env python3
"""
微信内容下载测试

演示微信内容的搜索和下载功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.wechat_scraper import WeChatScraper


async def test_wechat_download():
    """测试微信内容下载"""
    print("📥 微信内容下载测试")
    print("=" * 40)
    
    scraper = WeChatScraper()
    
    try:
        # 设置浏览器
        print("\n1. 设置浏览器...")
        setup_result = await scraper.setup_browser(headless=False, persistent=False)
        print(f"   结果: {setup_result}")
        
        if setup_result["status"] != "success":
            print("❌ 浏览器设置失败，无法继续测试")
            return
        
        # 创建输出目录
        output_dir = Path(__file__).parent / "wechat_download_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 搜索微信内容
        print("\n3. 搜索微信内容...")
        search_result = await scraper.search_wechat("Python编程", max_pages=1)
        print(f"   结果: {search_result['status']}")
        
        if search_result["status"] == "success":
            print(f"   ✅ 找到 {search_result['total_results']} 个结果")
            
            # 下载前3个结果
            results = search_result.get('results', [])
            for i, item in enumerate(results[:3], 1):
                print(f"\n4.{i} 下载第 {i} 个结果...")
                print(f"   标题: {item['title']}")
                print(f"   链接: {item['link']}")
                
                # 下载单个内容
                download_result = await scraper.download_and_save_content(
                    item['link'], 
                    output_dir, 
                    item['title']
                )
                
                if download_result["status"] == "success":
                    print(f"   ✅ 下载成功: {download_result['base_name']}")
                    print(f"   📁 PDF: {download_result['files']['pdf']}")
                    print(f"   📄 Markdown: {download_result['files']['markdown']}")
                else:
                    print(f"   ❌ 下载失败: {download_result['message']}")
                
                # 等待一下避免请求过快
                await asyncio.sleep(2)
            
            # 显示下载目录结构
            print(f"\n5. 下载目录结构:")
            print(f"   📁 {output_dir}")
            if output_dir.exists():
                for item in output_dir.rglob("*"):
                    if item.is_file():
                        print(f"      📄 {item.relative_to(output_dir)}")
            
        else:
            print(f"   ❌ 搜索失败: {search_result['message']}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理资源
        print("\n6. 清理资源...")
        try:
            await scraper.cleanup()
            print("   ✅ 资源清理完成")
        except Exception as e:
            print(f"   ⚠️ 资源清理警告: {e}")
    
    print("\n🎉 微信内容下载测试完成！")


async def main():
    """主函数"""
    try:
        await test_wechat_download()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

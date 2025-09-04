#!/usr/bin/env python3
"""
微信内容真实下载测试

使用真实的微信文章链接进行下载测试
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.wechat_scraper import WeChatScraper


async def test_wechat_real_download():
    """测试微信内容真实下载"""
    print("📥 微信内容真实下载测试")
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
        output_dir = Path(__file__).parent / "wechat_real_download_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 使用一个真实的微信文章链接进行测试
        # 这是一个公开的微信文章链接示例
        test_urls = [
            "https://mp.weixin.qq.com/s/example1",  # 示例链接1
            "https://mp.weixin.qq.com/s/example2",  # 示例链接2
        ]
        
        # 如果用户有真实的微信文章链接，可以在这里替换
        print("\n3. 注意：由于搜狗微信搜索的反爬虫机制，")
        print("   建议使用真实的微信文章链接进行测试")
        print("   或者手动从微信中复制文章链接")
        
        # 先测试搜狗搜索，看看能否找到真实链接
        print("\n4. 尝试搜索微信内容...")
        search_result = await scraper.search_wechat("Python编程", max_pages=1)
        
        if search_result["status"] == "success":
            print(f"   ✅ 搜索成功，找到 {search_result['total_results']} 个结果")
            
            # 尝试下载第一个结果
            results = search_result.get('results', [])
            if results:
                first_result = results[0]
                print(f"\n5. 尝试下载第一个结果...")
                print(f"   标题: {first_result['title']}")
                print(f"   链接: {first_result['link']}")
                
                # 下载单个内容
                download_result = await scraper.download_and_save_content(
                    first_result['link'], 
                    output_dir, 
                    first_result['title']
                )
                
                print(f"\n6. 下载结果:")
                print(f"   状态: {download_result['status']}")
                print(f"   消息: {download_result['message']}")
                
                if download_result["status"] == "success":
                    print(f"   ✅ 下载成功!")
                    print(f"   📁 PDF: {download_result['files']['pdf']}")
                    print(f"   📄 Markdown: {download_result['files']['markdown']}")
                    
                    # 显示下载目录结构
                    print(f"\n7. 下载目录结构:")
                    print(f"   📁 {output_dir}")
                    if output_dir.exists():
                        for item in output_dir.rglob("*"):
                            if item.is_file():
                                print(f"      📄 {item.relative_to(output_dir)}")
                else:
                    print(f"   ❌ 下载失败: {download_result['message']}")
                    
                    # 如果是验证码问题，提供解决建议
                    if "验证码" in download_result.get('message', ''):
                        print(f"\n💡 解决建议:")
                        print(f"   1. 搜狗微信搜索检测到自动化访问")
                        print(f"   2. 建议使用真实的微信文章链接")
                        print(f"   3. 或者手动完成验证码验证")
            else:
                print(f"   ❌ 没有找到搜索结果")
        else:
            print(f"   ❌ 搜索失败: {search_result['message']}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("\n8. 清理资源...")
        try:
            await scraper.cleanup()
            print("   ✅ 资源清理完成")
        except Exception as e:
            print(f"   ⚠️ 资源清理警告: {e}")
    
    print("\n🎉 微信内容真实下载测试完成！")


async def main():
    """主函数"""
    try:
        await test_wechat_real_download()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

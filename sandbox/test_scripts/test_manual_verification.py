#!/usr/bin/env python3
"""
人工验证等待测试

测试搜狗微信搜索的人工验证等待功能
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.wechat_scraper import WeChatScraper


async def test_manual_verification():
    """测试人工验证等待功能"""
    print("🔐 人工验证等待测试")
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
        output_dir = Path(__file__).parent / "manual_verification_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 使用搜狗微信搜索链接
        test_url = "https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS-RU6ljlTvJpOQfAfK4l7_65z41o-wcdAVqXa8Fplpd9952kvnRUuUGmJJKhudQ35mGjx4ciicfy_t6uMaCgkDBcJat_Dw3Ktt9Z3CebSf58m4l0myOsAm_R-JrxCE85wcX0SQNdi8xJjoL3tZWFVb"
        
        print(f"\n3. 测试链接:")
        print(f"   {test_url}")
        
        # 访问链接
        print(f"\n4. 访问链接...")
        await scraper.page.goto(test_url)
        await scraper.page.wait_for_load_state("networkidle")
        
        # 等待页面加载
        await asyncio.sleep(3)
        
        # 获取初始页面信息
        title = await scraper.page.title()
        current_url = scraper.page.url
        content = await scraper.page.content()
        
        print(f"   初始页面标题: {title}")
        print(f"   初始URL: {current_url}")
        print(f"   内容长度: {len(content)}")
        
        # 检查是否需要验证
        if "antispider" in current_url or "验证码" in title or "captcha" in content.lower():
            print(f"\n5. 检测到验证码，开始等待人工验证...")
            print(f"   ⚠️ 请在浏览器中完成验证码验证")
            print(f"   ⏳ 程序将一直等待直到验证完成...")
            
            # 等待人工验证完成
            verification_result = await scraper.wait_for_manual_verification(timeout=None)
            
            if verification_result["success"]:
                print(f"   ✅ 人工验证完成!")
                print(f"   等待时间: {verification_result['wait_time']}秒")
                print(f"   最终URL: {verification_result['current_url']}")
                print(f"   最终标题: {verification_result['title']}")
                
                # 验证完成后，尝试下载内容
                print(f"\n6. 验证完成，尝试下载内容...")
                
                # 检查是否重定向到微信文章
                if "mp.weixin.qq.com" in verification_result['current_url']:
                    print(f"   ✅ 成功重定向到微信文章")
                    
                    # 尝试下载内容
                    download_result = await scraper.download_and_save_content(
                        verification_result['current_url'],
                        output_dir,
                        "微信文章"
                    )
                    
                    if download_result["status"] == "success":
                        print(f"   ✅ 内容下载成功!")
                        print(f"   📁 PDF: {download_result['files']['pdf']}")
                        print(f"   📄 Markdown: {download_result['files']['markdown']}")
                    else:
                        print(f"   ❌ 内容下载失败: {download_result['message']}")
                else:
                    print(f"   ⚠️ 未重定向到微信文章，当前URL: {verification_result['current_url']}")
                    
                    # 尝试生成PDF
                    pdf_result = await scraper.print_page_to_pdf(verification_result['current_url'])
                    if pdf_result["status"] == "success":
                        print(f"   ✅ PDF生成成功")
                        print(f"   📁 文件路径: {pdf_result['pdf_path']}")
                        
                        # 检查PDF文件
                        pdf_path = Path(pdf_result['pdf_path'])
                        if pdf_path.exists():
                            file_size = pdf_path.stat().st_size
                            print(f"   📊 文件大小: {file_size} 字节")
                            
                            if file_size > 50000:
                                print(f"   ✅ PDF文件大小正常，可能包含真实内容")
                            else:
                                print(f"   ⚠️ PDF文件较小，可能是验证页面")
                    else:
                        print(f"   ❌ PDF生成失败: {pdf_result['message']}")
            else:
                print(f"   ❌ 等待人工验证超时")
                print(f"   等待时间: {verification_result['wait_time']}秒")
                print(f"   最终URL: {verification_result['current_url']}")
                print(f"   最终标题: {verification_result['title']}")
        else:
            print(f"\n5. 未检测到验证码，直接尝试下载...")
            
            # 直接尝试下载
            download_result = await scraper.download_and_save_content(
                test_url,
                output_dir,
                "微信文章"
            )
            
            if download_result["status"] == "success":
                print(f"   ✅ 内容下载成功!")
                print(f"   📁 PDF: {download_result['files']['pdf']}")
                print(f"   📄 Markdown: {download_result['files']['markdown']}")
            else:
                print(f"   ❌ 内容下载失败: {download_result['message']}")
        
        # 显示生成的文件
        print(f"\n7. 生成的文件:")
        if output_dir.exists():
            for item in output_dir.rglob("*"):
                if item.is_file():
                    print(f"   📄 {item.relative_to(output_dir)}")
        
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
    
    print("\n🎉 人工验证等待测试完成！")


async def main():
    """主函数"""
    try:
        await test_manual_verification()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

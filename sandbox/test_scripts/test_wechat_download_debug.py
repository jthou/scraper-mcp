#!/usr/bin/env python3
"""
微信内容下载调试测试

专门用于调试下载过程中的问题
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.wechat_scraper import WeChatScraper


async def test_wechat_download_debug():
    """调试微信内容下载"""
    print("🔍 微信内容下载调试测试")
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
        output_dir = Path(__file__).parent / "wechat_debug_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 测试单个链接的访问
        test_url = "https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS-RU6ljlTvJpOQfAfK4l7_65z41o-wcdAVqXa8Fplpd9952kvnRUuUGmJJKhudQ35mGjx4ciicfy_t6uMaCgkDBcJat_Dw3Ktt9Z3CebSf58m4l0myOsAm_R-JrxCE85wcX0SQNdi8xJjoL3tZWFVb"
        
        print(f"\n3. 测试访问链接...")
        print(f"   链接: {test_url}")
        
        # 先测试页面读取
        print("\n4. 测试页面读取...")
        page_result = await scraper.read_wechat_page(test_url)
        print(f"   页面读取结果: {page_result}")
        
        if page_result["status"] == "success":
            print(f"   ✅ 页面读取成功")
            print(f"   标题: {page_result.get('title', 'N/A')}")
            print(f"   内容长度: {len(page_result.get('content', ''))}")
        else:
            print(f"   ❌ 页面读取失败: {page_result['message']}")
            return
        
        # 测试PDF生成
        print("\n5. 测试PDF生成...")
        pdf_result = await scraper.print_page_to_pdf(test_url)
        print(f"   PDF生成结果: {pdf_result}")
        
        if pdf_result["status"] == "success":
            print(f"   ✅ PDF生成成功")
            print(f"   PDF路径: {pdf_result['pdf_path']}")
            
            # 检查PDF文件是否存在
            pdf_path = Path(pdf_result['pdf_path'])
            if pdf_path.exists():
                print(f"   ✅ PDF文件确实存在，大小: {pdf_path.stat().st_size} 字节")
                
                # 测试PDF转Markdown
                print("\n6. 测试PDF转Markdown...")
                markdown_result = await scraper.pdf_to_markdown(str(pdf_path))
                print(f"   Markdown转换结果: {markdown_result}")
                
                if markdown_result["status"] == "success":
                    print(f"   ✅ Markdown转换成功")
                    print(f"   内容长度: {len(markdown_result.get('markdown_content', ''))}")
                    print(f"   内容预览: {markdown_result.get('markdown_content', '')[:200]}...")
                else:
                    print(f"   ❌ Markdown转换失败: {markdown_result['message']}")
            else:
                print(f"   ❌ PDF文件不存在: {pdf_path}")
        else:
            print(f"   ❌ PDF生成失败: {pdf_result['message']}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("\n7. 清理资源...")
        try:
            await scraper.cleanup()
            print("   ✅ 资源清理完成")
        except Exception as e:
            print(f"   ⚠️ 资源清理警告: {e}")
    
    print("\n🎉 微信内容下载调试测试完成！")


async def main():
    """主函数"""
    try:
        await test_wechat_download_debug()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

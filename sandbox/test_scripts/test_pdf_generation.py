#!/usr/bin/env python3
"""
PDF生成功能测试

专门测试PDF生成功能，使用简单的网页
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.wechat_scraper import WeChatScraper


async def test_pdf_generation():
    """测试PDF生成功能"""
    print("📄 PDF生成功能测试")
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
        output_dir = Path(__file__).parent / "pdf_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 测试简单的网页PDF生成
        test_urls = [
            "https://www.baidu.com",
            "https://www.zhihu.com",
            "https://www.github.com"
        ]
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n3.{i} 测试PDF生成: {url}")
            
            try:
                # 直接测试PDF生成
                pdf_result = await scraper.print_page_to_pdf(url)
                print(f"   PDF生成结果: {pdf_result}")
                
                if pdf_result["status"] == "success":
                    print(f"   ✅ PDF生成成功")
                    print(f"   📁 文件路径: {pdf_result['pdf_path']}")
                    
                    # 检查文件是否存在
                    pdf_path = Path(pdf_result['pdf_path'])
                    if pdf_path.exists():
                        file_size = pdf_path.stat().st_size
                        print(f"   📊 文件大小: {file_size} 字节")
                    else:
                        print(f"   ❌ PDF文件不存在")
                else:
                    print(f"   ❌ PDF生成失败: {pdf_result['message']}")
                
                # 等待一下避免请求过快
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        
        # 显示生成的PDF文件
        print(f"\n4. 生成的PDF文件:")
        pdf_dir = Path(__file__).parent.parent.parent / "data" / "pdfs"
        if pdf_dir.exists():
            pdf_files = list(pdf_dir.glob("wechat_*.pdf"))
            for pdf_file in pdf_files[-5:]:  # 显示最近5个文件
                print(f"   📄 {pdf_file.name} ({pdf_file.stat().st_size} 字节)")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
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
    
    print("\n🎉 PDF生成功能测试完成！")


async def main():
    """主函数"""
    try:
        await test_pdf_generation()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

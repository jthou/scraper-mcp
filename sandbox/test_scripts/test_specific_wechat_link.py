#!/usr/bin/env python3
"""
测试特定微信文章链接

使用真实的搜狗微信文章链接进行测试
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


async def test_specific_wechat_link():
    """测试特定的微信文章链接"""
    print("🔗 测试特定微信文章链接")
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
        output_dir = Path(__file__).parent / "specific_wechat_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 这里是一个真实的搜狗微信文章链接示例
        # 你可以替换成任何你想测试的链接
        test_url = "https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS-RU6ljlTvJpOQfAfK4l7_65z41o-wcdAVqXa8Fplpd9952kvnRUuUGmJJKhudQ35mGjx4ciicfy_t6uMaCgkDBcJat_Dw3Ktt9Z3CebSf58m4l0myOsAm_R-JrxCE85wcX0SQNdi8xJjoL3tZWFVb"
        
        print(f"\n3. 测试链接:")
        print(f"   {test_url}")
        
        # 访问链接
        print(f"\n4. 访问链接...")
        await scraper.page.goto(test_url)
        await scraper.page.wait_for_load_state("networkidle")
        
        # 等待页面加载
        await asyncio.sleep(5)
        
        # 获取页面信息
        title = await scraper.page.title()
        current_url = scraper.page.url
        content = await scraper.page.content()
        
        print(f"   页面标题: {title}")
        print(f"   当前URL: {current_url}")
        print(f"   内容长度: {len(content)}")
        
        # 检查页面状态
        if "搜狗搜索" in title:
            print(f"   ⚠️ 页面被重定向到搜狗搜索")
        elif "验证码" in content or "captcha" in content.lower():
            print(f"   ⚠️ 页面包含验证码")
        elif "请在微信中打开" in content:
            print(f"   ⚠️ 页面要求微信客户端打开")
        elif "mp.weixin.qq.com" in current_url:
            print(f"   ✅ 成功重定向到微信文章")
        else:
            print(f"   ❓ 页面状态未知")
        
        # 显示页面内容预览
        print(f"\n5. 页面内容预览:")
        content_preview = content[:500] if len(content) > 500 else content
        print(f"   {content_preview}...")
        
        # 尝试生成PDF
        print(f"\n6. 尝试生成PDF...")
        pdf_result = await scraper.print_page_to_pdf(test_url)
        
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
                    
                    # 尝试转换为Markdown
                    print(f"   📝 尝试转换为Markdown...")
                    markdown_result = await scraper.pdf_to_markdown(str(pdf_path))
                    
                    if markdown_result["status"] == "success":
                        print(f"   ✅ Markdown转换成功")
                        print(f"   📄 内容长度: {len(markdown_result['markdown_content'])}")
                        
                        # 显示内容预览
                        print(f"\n7. 内容预览:")
                        content_preview = markdown_result['markdown_content'][:300]
                        print(f"   {content_preview}...")
                        
                        # 保存文件
                        pdf_dir = output_dir / "pdfs"
                        markdown_dir = output_dir / "markdown"
                        pdf_dir.mkdir(exist_ok=True)
                        markdown_dir.mkdir(exist_ok=True)
                        
                        # 复制PDF文件
                        import shutil
                        target_pdf = pdf_dir / "wechat_article.pdf"
                        shutil.copy2(pdf_path, target_pdf)
                        
                        # 保存Markdown文件
                        markdown_content = f"""# 微信文章测试

**来源**: {test_url}
**保存时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**来源平台**: 搜狗微信搜索

---

{markdown_result['markdown_content']}
"""
                        
                        markdown_file = markdown_dir / "wechat_article.md"
                        with open(markdown_file, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
                        
                        print(f"   ✅ 文件保存成功")
                        print(f"   📁 PDF: {target_pdf}")
                        print(f"   📄 Markdown: {markdown_file}")
                    else:
                        print(f"   ❌ Markdown转换失败: {markdown_result['message']}")
                else:
                    print(f"   ⚠️ PDF文件较小，可能是验证页面")
            else:
                print(f"   ❌ PDF文件不存在")
        else:
            print(f"   ❌ PDF生成失败: {pdf_result['message']}")
        
        # 显示生成的文件
        print(f"\n8. 生成的文件:")
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
        print("\n9. 清理资源...")
        try:
            await scraper.cleanup()
            print("   ✅ 资源清理完成")
        except Exception as e:
            print(f"   ⚠️ 资源清理警告: {e}")
    
    print("\n🎉 特定微信文章链接测试完成！")


async def main():
    """主函数"""
    try:
        await test_specific_wechat_link()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

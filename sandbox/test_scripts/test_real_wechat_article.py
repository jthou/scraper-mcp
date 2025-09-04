#!/usr/bin/env python3
"""
真实微信文章测试

使用真实的微信文章链接进行测试
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


async def test_real_wechat_article():
    """测试真实微信文章"""
    print("📰 真实微信文章测试")
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
        output_dir = Path(__file__).parent / "real_wechat_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 使用一些公开的微信文章链接进行测试
        test_articles = [
            {
                "title": "测试文章1",
                "url": "https://mp.weixin.qq.com/s/example1",
                "description": "这是一个示例链接"
            },
            {
                "title": "测试文章2", 
                "url": "https://mp.weixin.qq.com/s/example2",
                "description": "这是另一个示例链接"
            }
        ]
        
        print(f"\n3. 注意：由于微信的保护机制，建议使用真实的微信文章链接")
        print(f"   你可以从微信中复制文章链接来替换下面的示例链接")
        
        for i, article in enumerate(test_articles, 1):
            print(f"\n4.{i} 测试文章: {article['title']}")
            print(f"   URL: {article['url']}")
            print(f"   描述: {article['description']}")
            
            try:
                # 访问文章
                print(f"   🌐 访问文章...")
                await scraper.page.goto(article['url'])
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
                if "请在微信中打开" in content:
                    print(f"   ⚠️ 页面要求微信客户端打开")
                elif "验证码" in content or "captcha" in content.lower():
                    print(f"   ⚠️ 页面包含验证码")
                elif "微信公众平台" in title:
                    print(f"   ⚠️ 页面被重定向到微信公众平台")
                else:
                    print(f"   ✅ 页面可能包含真实内容")
                
                # 尝试生成PDF
                print(f"   📄 尝试生成PDF...")
                pdf_result = await scraper.print_page_to_pdf(article['url'])
                
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
                                
                                # 保存文件
                                pdf_dir = output_dir / "pdfs"
                                markdown_dir = output_dir / "markdown"
                                pdf_dir.mkdir(exist_ok=True)
                                markdown_dir.mkdir(exist_ok=True)
                                
                                # 复制PDF文件
                                import shutil
                                target_pdf = pdf_dir / f"{article['title']}.pdf"
                                shutil.copy2(pdf_path, target_pdf)
                                
                                # 保存Markdown文件
                                markdown_content = f"""# {article['title']}

**来源**: {article['url']}
**保存时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**来源平台**: 微信公众平台

---

{markdown_result['markdown_content']}
"""
                                
                                markdown_file = markdown_dir / f"{article['title']}.md"
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
                
                # 等待一下避免请求过快
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        
        # 显示生成的文件
        print(f"\n5. 生成的文件:")
        if output_dir.exists():
            for item in output_dir.rglob("*"):
                if item.is_file():
                    print(f"   📄 {item.relative_to(output_dir)}")
        
        # 提供使用建议
        print(f"\n6. 使用建议:")
        print(f"   💡 要测试真实的微信文章，请:")
        print(f"   1. 在微信中打开一篇文章")
        print(f"   2. 点击右上角的三个点")
        print(f"   3. 选择'复制链接'")
        print(f"   4. 将链接替换到上面的test_articles中")
        print(f"   5. 重新运行测试")
        
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
    
    print("\n🎉 真实微信文章测试完成！")


async def main():
    """主函数"""
    try:
        await test_real_wechat_article()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

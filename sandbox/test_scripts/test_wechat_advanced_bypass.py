#!/usr/bin/env python3
"""
微信高级绕过测试

使用多种策略尝试绕过微信的反爬虫机制
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


async def test_wechat_advanced_bypass():
    """测试微信高级绕过策略"""
    print("🚀 微信高级绕过测试")
    print("=" * 50)
    
    scraper = WeChatScraper()
    
    try:
        # 设置浏览器
        print("\n1. 设置高级隐身浏览器...")
        setup_result = await scraper.setup_browser(headless=False, persistent=False)
        print(f"   结果: {setup_result}")
        
        if setup_result["status"] != "success":
            print("❌ 浏览器设置失败，无法继续测试")
            return
        
        # 创建输出目录
        output_dir = Path(__file__).parent / "wechat_advanced_test"
        output_dir.mkdir(exist_ok=True)
        print(f"\n2. 输出目录: {output_dir}")
        
        # 策略1: 直接搜索并尝试下载
        print("\n3. 策略1: 直接搜索并尝试下载")
        search_result = await scraper.search_wechat("Python编程", max_pages=1)
        
        if search_result["status"] == "success":
            print(f"   ✅ 搜索成功，找到 {search_result['total_results']} 个结果")
            
            results = search_result.get('results', [])
            if results:
                # 尝试下载第一个结果
                first_result = results[0]
                print(f"\n4. 尝试下载第一个结果...")
                print(f"   标题: {first_result['title']}")
                print(f"   链接: {first_result['link']}")
                
                # 使用高级策略下载
                download_result = await advanced_download(scraper, first_result['link'], output_dir, first_result['title'])
                
                if download_result["status"] == "success":
                    print(f"   ✅ 下载成功!")
                    print(f"   📁 PDF: {download_result['files']['pdf']}")
                    print(f"   📄 Markdown: {download_result['files']['markdown']}")
                else:
                    print(f"   ❌ 下载失败: {download_result['message']}")
                    
                    # 尝试其他策略
                    print(f"\n5. 尝试其他策略...")
                    await try_alternative_strategies(scraper, first_result['link'], output_dir)
        else:
            print(f"   ❌ 搜索失败: {search_result['message']}")
            
            # 尝试直接访问搜狗微信搜索
            print(f"\n6. 尝试直接访问搜狗微信搜索...")
            await try_direct_sogou_access(scraper, output_dir)
        
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
    
    print("\n🎉 微信高级绕过测试完成！")


async def advanced_download(scraper, url, output_dir, title):
    """高级下载策略"""
    try:
        print(f"   🔄 使用高级策略下载...")
        
        # 策略1: 增加更长的等待时间
        print(f"   ⏳ 策略1: 增加等待时间...")
        await asyncio.sleep(10)  # 等待10秒
        
        # 策略2: 模拟人类行为
        print(f"   🎭 策略2: 模拟人类行为...")
        await scraper.stealth.simulate_human_behavior(scraper.page, duration=10)
        
        # 策略3: 尝试访问页面
        print(f"   🌐 策略3: 访问页面...")
        await scraper.page.goto(url)
        await scraper.page.wait_for_load_state("networkidle")
        
        # 策略4: 等待更长时间让内容加载
        print(f"   ⏰ 策略4: 等待内容加载...")
        await asyncio.sleep(15)
        
        # 策略5: 再次模拟人类行为
        print(f"   🎭 策略5: 再次模拟人类行为...")
        await scraper.stealth.simulate_human_behavior(scraper.page, duration=8)
        
        # 策略6: 检查页面内容
        print(f"   🔍 策略6: 检查页面内容...")
        content = await scraper.page.content()
        title_text = await scraper.page.title()
        
        print(f"   页面标题: {title_text}")
        print(f"   内容长度: {len(content)}")
        
        # 检查是否遇到验证码
        if "验证码" in content or "captcha" in content.lower():
            print(f"   ⚠️ 检测到验证码，尝试绕过...")
            
            # 尝试刷新页面
            await scraper.page.reload()
            await scraper.page.wait_for_load_state("networkidle")
            await asyncio.sleep(10)
            
            # 再次检查
            content = await scraper.page.content()
            if "验证码" in content or "captcha" in content.lower():
                return {
                    "status": "error",
                    "message": "无法绕过验证码",
                    "content_preview": content[:200]
                }
        
        # 策略7: 尝试生成PDF
        print(f"   📄 策略7: 生成PDF...")
        pdf_result = await scraper.print_page_to_pdf(url)
        
        if pdf_result["status"] == "success":
            print(f"   ✅ PDF生成成功")
            
            # 检查PDF文件
            pdf_path = Path(pdf_result['pdf_path'])
            if pdf_path.exists():
                file_size = pdf_path.stat().st_size
                print(f"   📊 PDF文件大小: {file_size} 字节")
                
                if file_size > 50000:  # 大于50KB，可能是真实内容
                    print(f"   ✅ PDF文件大小正常，可能包含真实内容")
                    
                    # 尝试转换为Markdown
                    markdown_result = await scraper.pdf_to_markdown(str(pdf_path))
                    if markdown_result["status"] == "success":
                        print(f"   ✅ Markdown转换成功")
                        
                        # 保存文件
                        pdf_dir = output_dir / "pdfs"
                        markdown_dir = output_dir / "markdown"
                        pdf_dir.mkdir(exist_ok=True)
                        markdown_dir.mkdir(exist_ok=True)
                        
                        # 复制PDF文件
                        import shutil
                        target_pdf = pdf_dir / f"{title}.pdf"
                        shutil.copy2(pdf_path, target_pdf)
                        
                        # 保存Markdown文件
                        markdown_content = f"""# {title}

**来源**: {url}
**保存时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**来源平台**: 搜狗微信搜索

---

{markdown_result['markdown_content']}
"""
                        
                        markdown_file = markdown_dir / f"{title}.md"
                        with open(markdown_file, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
                        
                        return {
                            "status": "success",
                            "message": "高级策略下载成功",
                            "files": {
                                "pdf": str(target_pdf),
                                "markdown": str(markdown_file)
                            }
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"Markdown转换失败: {markdown_result['message']}"
                        }
                else:
                    return {
                        "status": "error",
                        "message": f"PDF文件太小({file_size}字节)，可能是验证码页面"
                    }
            else:
                return {
                    "status": "error",
                    "message": "PDF文件不存在"
                }
        else:
            return {
                "status": "error",
                "message": f"PDF生成失败: {pdf_result['message']}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"高级下载失败: {str(e)}"
        }


async def try_alternative_strategies(scraper, url, output_dir):
    """尝试替代策略"""
    print(f"   🔄 尝试替代策略...")
    
    # 策略1: 使用不同的用户代理
    print(f"   🎭 策略1: 更换用户代理...")
    try:
        await scraper.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000029) NetType/WIFI Language/zh_CN"
        })
        
        await scraper.page.goto(url)
        await scraper.page.wait_for_load_state("networkidle")
        await asyncio.sleep(10)
        
        content = await scraper.page.content()
        if "验证码" not in content and "captcha" not in content.lower():
            print(f"   ✅ 用户代理策略成功")
            return True
        else:
            print(f"   ❌ 用户代理策略失败")
    except Exception as e:
        print(f"   ❌ 用户代理策略失败: {e}")
    
    # 策略2: 使用无头模式
    print(f"   👻 策略2: 尝试无头模式...")
    try:
        await scraper.cleanup()
        setup_result = await scraper.setup_browser(headless=True, persistent=False)
        if setup_result["status"] == "success":
            await scraper.page.goto(url)
            await scraper.page.wait_for_load_state("networkidle")
            await asyncio.sleep(10)
            
            content = await scraper.page.content()
            if "验证码" not in content and "captcha" not in content.lower():
                print(f"   ✅ 无头模式策略成功")
                return True
            else:
                print(f"   ❌ 无头模式策略失败")
    except Exception as e:
        print(f"   ❌ 无头模式策略失败: {e}")
    
    return False


async def try_direct_sogou_access(scraper, output_dir):
    """尝试直接访问搜狗微信搜索"""
    print(f"   🔍 尝试直接访问搜狗微信搜索...")
    
    try:
        # 直接访问搜狗微信搜索首页
        await scraper.page.goto("https://weixin.sogou.com")
        await scraper.page.wait_for_load_state("networkidle")
        
        # 等待页面加载
        await asyncio.sleep(10)
        
        # 模拟人类行为
        await scraper.stealth.simulate_human_behavior(scraper.page, duration=5)
        
        # 检查页面内容
        content = await scraper.page.content()
        title = await scraper.page.title()
        
        print(f"   页面标题: {title}")
        print(f"   内容长度: {len(content)}")
        
        if "验证码" in content or "captcha" in content.lower():
            print(f"   ⚠️ 搜狗微信搜索需要验证码")
        else:
            print(f"   ✅ 搜狗微信搜索访问成功")
            
            # 尝试搜索
            search_box = await scraper.page.query_selector("input[name='query']")
            if search_box:
                await search_box.fill("Python编程")
                await search_box.press("Enter")
                await scraper.page.wait_for_load_state("networkidle")
                await asyncio.sleep(5)
                
                print(f"   ✅ 搜索功能可用")
            else:
                print(f"   ❌ 未找到搜索框")
        
    except Exception as e:
        print(f"   ❌ 直接访问失败: {e}")


async def main():
    """主函数"""
    try:
        await test_wechat_advanced_bypass()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

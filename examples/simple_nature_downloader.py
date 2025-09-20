#!/usr/bin/env python3
"""
简化版Nature文章下载器
使用更简单的策略下载Nature文章

功能:
- 下载Nature文章为PDF和Markdown格式
- 使用更宽松的超时设置
- 自动处理网络问题

使用方法:
    python simple_nature_downloader.py

作者: AI Assistant
日期: 2025年9月20日
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import re
from urllib.parse import unquote


def clean_filename(filename: str) -> str:
    """清理文件名，确保适合作为文件名"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace('\n', ' ').replace('\r', ' ')
    filename = re.sub(r'\s+', ' ', filename).strip()
    
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename or "nature_article"


async def download_nature_article_simple(url: str, output_dir: str = "nature"):
    """简化版Nature文章下载"""
    print("🌐 启动浏览器...")
    
    # 创建输出目录
    output_path = Path(output_dir)
    pdf_dir = output_path / "pdfs"
    markdown_dir = output_path / "markdown"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        try:
            # 启动浏览器，使用更宽松的设置
            browser = await p.chromium.launch(
                channel="chrome",
                headless=False,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )
            
            # 创建新的浏览器上下文
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # 设置更长的超时时间
            page.set_default_timeout(120000)  # 120秒超时
            
            print(f"📄 访问Nature文章: {url}")
            
            # 尝试访问页面，使用更宽松的等待条件
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=120000)
                print("✅ 页面加载成功")
            except Exception as e:
                print(f"⚠️ 页面加载超时，尝试继续: {e}")
                # 即使超时也继续尝试
            
            print("⏱️ 等待页面内容加载...")
            await page.wait_for_timeout(10000)  # 等待10秒
            
            # 尝试获取页面标题
            try:
                title = await page.title()
                print(f"📊 页面标题: {title}")
            except Exception as e:
                print(f"⚠️ 获取标题失败: {e}")
                title = "Nature Article"
            
            # 如果标题为空或默认值，尝试从页面内容获取
            if not title or title == "Nature":
                try:
                    title_element = await page.query_selector("h1")
                    if title_element:
                        title = await title_element.inner_text()
                        title = title.strip()
                        print(f"📊 从h1获取标题: {title}")
                except:
                    pass
            
            # 生成文件名
            clean_title = clean_filename(title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 尝试生成PDF
            print("📄 生成PDF...")
            pdf_filename = f"{clean_title}_{timestamp}.pdf"
            pdf_path = pdf_dir / pdf_filename
            
            try:
                await page.pdf(
                    path=str(pdf_path),
                    format="A4",
                    print_background=True,
                    margin={
                        'top': '20px',
                        'bottom': '20px',
                        'left': '20px',
                        'right': '20px'
                    }
                )
                print(f"✅ PDF生成成功: {pdf_path}")
            except Exception as e:
                print(f"⚠️ PDF生成失败: {e}")
                pdf_path = None
            
            # 提取文章内容
            print("📝 提取文章内容...")
            try:
                # 尝试多种选择器获取内容
                content_selectors = [
                    "article",
                    "[data-testid='article-content']",
                    ".c-article-body",
                    ".article-content",
                    "main",
                    ".content"
                ]
                
                content = None
                for selector in content_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            content = await element.inner_text()
                            if content and len(content.strip()) > 100:  # 确保内容足够长
                                print(f"✅ 使用选择器 '{selector}' 提取内容")
                                break
                    except:
                        continue
                
                # 如果上述选择器都失败，使用body
                if not content:
                    content = await page.inner_text("body")
                    print("⚠️ 使用body标签提取内容")
                
            except Exception as e:
                print(f"⚠️ 内容提取失败: {e}")
                content = "内容提取失败"
            
            # 保存Markdown
            markdown_filename = f"{clean_title}_{timestamp}.md"
            markdown_path = markdown_dir / markdown_filename
            
            markdown_content = f"""# {title}

**来源**: [Nature]({url})
**保存时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**文件类型**: Nature杂志文章

---

{content}
"""
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✅ Markdown保存成功: {markdown_path}")
            
            # 创建文件映射
            mapping = {
                "title": title,
                "url": url,
                "pdf_path": str(pdf_path.relative_to(output_path)) if pdf_path else None,
                "markdown_path": str(markdown_path.relative_to(output_path)),
                "timestamp": timestamp,
                "download_time": datetime.now().isoformat()
            }
            
            mapping_file = output_path / "file_mapping.json"
            import json
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
            else:
                mappings = []
            
            mappings.append(mapping)
            
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 文件映射已更新: {mapping_file}")
            print("🎉 Nature文章下载完成！")
            
            return {
                "status": "success",
                "title": title,
                "pdf_path": str(pdf_path) if pdf_path else None,
                "markdown_path": str(markdown_path),
                "url": url
            }
            
        except Exception as e:
            print(f"💥 下载失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": str(e)
            }
        finally:
            print("🧹 关闭浏览器...")
            await browser.close()


async def main():
    """主函数"""
    print("📚 简化版Nature文章下载器")
    print("=" * 50)
    
    # 目标URL - DeepSeek文章
    url = "https://www.nature.com/articles/d41586-025-03015-6"
    
    print(f"🎯 目标文章: {url}")
    print("📁 保存目录: nature/")
    print()
    
    # 执行下载
    result = await download_nature_article_simple(url, "nature")
    
    if result["status"] == "success":
        print("\n🎉 下载成功！")
        if result["pdf_path"]:
            print(f"📄 PDF: {result['pdf_path']}")
        print(f"📝 Markdown: {result['markdown_path']}")
    else:
        print(f"\n❌ 下载失败: {result['message']}")


if __name__ == "__main__":
    asyncio.run(main())

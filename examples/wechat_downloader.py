#!/usr/bin/env python3
"""
微信文章下载器
简单高效的微信公众号文章PDF和Markdown下载工具

功能:
- 下载微信文章为PDF格式 (保留原始排版)
- 提取文章文本内容并保存为Markdown格式
- 自动清理文件名，支持中文标题
- 自动翻页到底部，确保所有内容加载完成
- 保存到 K-Vault/Wechat 目录下

使用方法:
    python wechat_downloader.py

作者: AI Assistant
日期: 2025年9月10日
"""

import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import re


def clean_filename(filename: str) -> str:
    """清理文件名"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace('\n', ' ').replace('\r', ' ')
    filename = re.sub(r'\s+', ' ', filename).strip()
    if len(filename) > 100:
        filename = filename[:100]
    return filename or "wechat_article"


async def download_wechat_article(url: str, output_dir: str):
    """下载微信文章"""
    
    # 创建输出目录
    output_path = Path(output_dir)
    pdf_dir = output_path / "pdfs"
    markdown_dir = output_path / "markdown"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        print("🌐 启动Chrome浏览器...")
        
        # 启动浏览器 - 在macOS上使用默认Chromium
        try:
            browser = await p.chromium.launch(
                headless=False,
                channel="chrome"  # 尝试使用系统Chrome
            )
        except Exception as e:
            print(f"⚠️ 无法使用Chrome，尝试使用Chromium: {e}")
            browser = await p.chromium.launch(
                headless=False  # 使用Playwright自带的Chromium
            )
        
        try:
            context = await browser.new_context()
            page = await context.new_page()
            
            print("📄 访问页面...")
            # 直接访问，不等待太多
            await page.goto(url, wait_until="domcontentloaded")
            
            print("⏱️ 等待页面初始加载...")
            await page.wait_for_timeout(3000)
            
            # 自动翻页到底部
            print("📜 正在自动翻页到底部...")
            previous_height = 0
            current_height = await page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            max_attempts = 20  # 最多尝试20次翻页
            
            while previous_height != current_height and scroll_attempts < max_attempts:
                previous_height = current_height
                scroll_attempts += 1
                
                # 滚动到底部
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                print(f"📍 第{scroll_attempts}次翻页，页面高度: {current_height}px")
                
                # 等待新内容加载
                await page.wait_for_timeout(2000)
                
                # 获取新高度
                current_height = await page.evaluate("document.body.scrollHeight")
            
            print(f"✅ 已滚动到页面底部，共翻页{scroll_attempts}次，最终页面高度: {current_height}px")
            
            # 等待一下确保所有内容都加载完成
            await page.wait_for_timeout(2000)
            
            # 获取标题
            try:
                title = await page.title()
                print(f"📊 页面标题: {title}")
            except:
                title = "微信文章"
            
            # 生成文件名
            clean_title = clean_filename(title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 生成PDF - 这是关键步骤
            print("📄 生成PDF...")
            pdf_filename = f"{clean_title}_{timestamp}.pdf"
            pdf_path = pdf_dir / pdf_filename
            
            # 直接生成PDF，不要复杂的参数
            await page.pdf(
                path=str(pdf_path),
                format="A4"
            )
            
            print(f"✅ PDF生成成功: {pdf_path}")
            
            # 获取页面文本内容
            print("📝 提取文本内容...")
            try:
                # 尝试获取文章内容
                content = await page.inner_text("body")
            except:
                content = "内容提取失败"
            
            # 保存Markdown
            markdown_filename = f"{clean_title}_{timestamp}.md"
            markdown_path = markdown_dir / markdown_filename
            
            markdown_content = f"""# {title}

**来源**: {url}
**保存时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{content}
"""
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✅ Markdown保存成功: {markdown_path}")
            
            return {
                "status": "success",
                "pdf_path": str(pdf_path),
                "markdown_path": str(markdown_path),
                "title": title
            }
            
        finally:
            print("🧹 关闭浏览器...")
            await browser.close()


async def main():
    """主函数"""
    wechat_url = "https://mp.weixin.qq.com/s?__biz=MzI0MjMwMTgyMw==&mid=2247484315&idx=1&sn=63ff4a96e9273e0fcb314e41a4327c53&chksm=e97f2d8bde08a49d12c42358b6d7a456fbc8869f0e55358d6f7e78d44f0f7e818faac8ce8831&cur_album_id=3857758147984932871&scene=189#wechat_redirect"
    output_directory = "K-Vault/Wechat"
    
    print("📚 微信文章下载器 (自动翻页版)")
    print("=" * 60)
    
    try:
        result = await download_wechat_article(wechat_url, output_directory)
        
        if result["status"] == "success":
            print("\n🎉 任务完成！")
            print(f"📄 PDF: {result['pdf_path']}")
            print(f"📝 Markdown: {result['markdown_path']}")
            print(f"📊 标题: {result['title']}")
        else:
            print(f"\n❌ 任务失败")
            
    except Exception as e:
        print(f"\n💥 出错: {e}")


if __name__ == "__main__":
    print("🚀 开始运行微信文章下载器...")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 运行出错: {e}")
        import traceback
        traceback.print_exc()

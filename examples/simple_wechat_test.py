#!/usr/bin/env python3
"""
测试版微信文章下载器
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


async def download_wechat_article():
    """下载微信文章"""
    url = "https://mp.weixin.qq.com/s/NGtutmLuicBZkl3xJWMErA"
    output_dir = "K-Vault/Wechat"
    
    # 创建输出目录
    output_path = Path(output_dir)
    pdf_dir = output_path / "pdfs"
    markdown_dir = output_path / "markdown"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        print("🌐 启动浏览器...")
        
        try:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            print("📄 访问页面...")
            await page.goto(url, wait_until="domcontentloaded")
            
            print("⏱️ 等待页面初始加载...")
            await page.wait_for_timeout(3000)
            
            # 自动翻页到底部
            print("📜 正在自动翻页到底部...")
            previous_height = 0
            current_height = await page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            max_attempts = 20
            
            while previous_height != current_height and scroll_attempts < max_attempts:
                previous_height = current_height
                scroll_attempts += 1
                
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                print(f"📍 第{scroll_attempts}次翻页，页面高度: {current_height}px")
                
                await page.wait_for_timeout(2000)
                current_height = await page.evaluate("document.body.scrollHeight")
            
            print(f"✅ 已滚动到页面底部，共翻页{scroll_attempts}次，最终页面高度: {current_height}px")
            
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
            
            # 生成PDF
            print("📄 生成PDF...")
            pdf_filename = f"{clean_title}_{timestamp}.pdf"
            pdf_path = pdf_dir / pdf_filename
            
            await page.pdf(path=str(pdf_path), format="A4")
            print(f"✅ PDF生成成功: {pdf_path}")
            
            # 获取页面文本内容
            print("📝 提取文本内容...")
            try:
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
            print("🎉 任务完成！")
            
        except Exception as e:
            print(f"💥 出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("🧹 关闭浏览器...")
            await browser.close()


def main():
    print("📚 微信文章下载器 (自动翻页版)")
    print("=" * 60)
    asyncio.run(download_wechat_article())


if __name__ == "__main__":
    main()

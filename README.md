# 网页内容抓取工具包

一个独立的Python工具包，提供网页内容抓取、下载、转换等功能。支持知乎、微信等平台的内容抓取。

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd scraper-mcp

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器（会自动安装）
python -c "import playwright; playwright.install()"
```

## 使用方法

### 1. 快速使用

```python
import asyncio
from src.core.scraper_toolkit import quick_search, quick_download

async def main():
    # 搜索知乎内容
    result = await quick_search("zhihu", "Python编程", max_pages=2)
    print(result)
    
    # 下载页面
    result = await quick_download("zhihu", "https://www.zhihu.com/question/123456")
    print(result)

asyncio.run(main())
```

### 2. 使用工具包类

```python
import asyncio
from pathlib import Path
from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform

async def main():
    # 创建配置
    config = ScrapingConfig(
        platform=Platform.ZHIHU,
        headless=False,
        max_pages=3,
        output_dir=Path("data")
    )
    
    # 创建工具包实例
    toolkit = ScraperToolkit(config)
    
    try:
        # 搜索内容
        result = await toolkit.search(Platform.ZHIHU, "机器学习", 3)
        print(f"搜索结果: {result}")
        
        # 下载内容
        if result["status"] == "success" and result["results"]:
            first_result = result["results"][0]
            download_result = await toolkit.download_content(
                Platform.ZHIHU,
                first_result["url"],
                Path("data"),
                first_result["title"]
            )
            print(f"下载结果: {download_result}")
    
    finally:
        await toolkit.cleanup()

asyncio.run(main())
```

### 3. 命令行工具

```bash
# 搜索知乎内容
python -m src.cli search zhihu "Python编程" --max-pages 2

# 下载单个页面
python -m src.cli download zhihu "https://www.zhihu.com/question/123456"

# 批量下载
python -m src.cli batch zhihu "机器学习" --max-pages 3 --output data/ml
```

## 示例

### 微信Isaac Sim文章下载

```python
# examples/wechat_isaac_login_then_download.py
import asyncio
from pathlib import Path
from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform

async def download_isaac_articles():
    config = ScrapingConfig(
        platform=Platform.WECHAT,
        headless=False,
        max_pages=9,  # 只搜索前9页
        output_dir=Path("data/wechat_isaac_p10"),
        wait_for_verification=True
    )
    
    toolkit = ScraperToolkit(config)
    
    try:
        # 等待登录验证
        await toolkit.setup_browser(Platform.WECHAT)
        
        # 搜索Isaac Sim相关文章
        result = await toolkit.search(Platform.WECHAT, "Isaac Sim", 9)
        
        if result["status"] == "success":
            print(f"找到 {len(result['results'])} 篇文章")
            
            # 下载文章
            for i, article in enumerate(result["results"], 1):
                print(f"下载第 {i} 篇: {article['title']}")
                download_result = await toolkit.download_content(
                    Platform.WECHAT,
                    article["link"],
                    Path("data/wechat_isaac_p10"),
                    article["title"]
                )
                print(f"结果: {download_result['status']}")
    
    finally:
        await toolkit.cleanup()

asyncio.run(download_isaac_articles())
```

## 支持的平台

- **知乎 (zhihu)**: 搜索、登录、页面读取、内容下载
- **微信 (wechat)**: 搜索、页面读取、内容下载（需要人工验证）

## 注意事项

1. **微信平台**：需要人工验证码验证，必须显示浏览器窗口
2. **浏览器要求**：需要Chrome浏览器，Playwright会自动安装
3. **网络要求**：需要稳定的网络连接
4. **资源清理**：使用完毕后记得调用`cleanup()`方法

## 项目结构

```
scraper-mcp/
├── src/
│   ├── core/                    # 核心模块
│   │   ├── scraper_toolkit.py   # 主工具包
│   │   ├── web_scraper.py       # 知乎抓取器
│   │   └── wechat_scraper.py    # 微信抓取器
│   └── cli.py                   # 命令行接口
├── examples/                    # 使用示例
├── data/                        # 输出目录
└── requirements.txt             # 依赖文件
```

## 许可证

MIT License
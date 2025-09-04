# 网页内容抓取工具包

一个独立的Python工具包，提供网页内容抓取、下载、转换等功能。支持知乎、微信等平台的内容抓取。

## 特性

- 🚀 **多平台支持**：支持知乎、微信等平台
- 🔍 **智能搜索**：支持关键词搜索和结果提取
- 📥 **内容下载**：自动下载并转换为PDF和Markdown格式
- 🎭 **人工验证支持**：支持需要人工验证的平台（如微信）
- ⚡ **便捷函数**：提供快速使用的便捷函数
- 🖥️ **命令行接口**：提供完整的命令行工具
- 📚 **示例丰富**：提供多种使用示例

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd scraper-toolkit

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

## 快速开始

### 1. 使用便捷函数

```python
import asyncio
from src.core.scraper_toolkit import quick_search, quick_download

async def main():
    # 快速搜索知乎内容
    result = await quick_search("zhihu", "Python编程", max_pages=2)
    print(result)
    
    # 快速下载页面
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

### 3. 使用命令行工具

```bash
# 搜索知乎内容
python -m src.cli search zhihu "Python编程" --max-pages 2

# 下载单个页面
python -m src.cli download zhihu "https://www.zhihu.com/question/123456"

# 批量下载
python -m src.cli batch zhihu "机器学习" --max-pages 3 --output data/ml

# 快速搜索
python -m src.cli quick-search zhihu "深度学习"

# 查看平台信息
python -m src.cli info zhihu
```

## 支持的平台

### 知乎 (zhihu)
- ✅ 搜索功能
- ✅ 登录功能
- ✅ 页面读取
- ✅ 内容下载
- ❌ 不需要人工验证

### 微信 (wechat)
- ✅ 搜索功能（通过搜狗搜索）
- ✅ 页面读取
- ✅ 内容下载
- ⚠️ 需要人工验证码验证

## 使用示例

### 知乎内容搜索

```python
# examples/zhihu_search.py
import asyncio
from pathlib import Path
from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform

async def search_zhihu():
    config = ScrapingConfig(
        platform=Platform.ZHIHU,
        headless=False,
        max_pages=2,
        output_dir=Path("data/zhihu")
    )
    
    toolkit = ScraperToolkit(config)
    
    try:
        # 搜索内容
        result = await toolkit.search(Platform.ZHIHU, "Python编程", 2)
        print(f"搜索结果: {result}")
        
        # 下载第一个结果
        if result["status"] == "success" and result["results"]:
            first_result = result["results"][0]
            download_result = await toolkit.download_content(
                Platform.ZHIHU,
                first_result["url"],
                Path("data/zhihu"),
                first_result["title"]
            )
            print(f"下载结果: {download_result}")
    
    finally:
        await toolkit.cleanup()

asyncio.run(search_zhihu())
```

### 微信内容搜索

```python
# examples/wechat_search.py
import asyncio
from pathlib import Path
from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform

async def search_wechat():
    config = ScrapingConfig(
        platform=Platform.WECHAT,
        headless=False,  # 必须显示浏览器窗口
        max_pages=1,
        output_dir=Path("data/wechat"),
        wait_for_verification=True  # 等待人工验证
    )
    
    toolkit = ScraperToolkit(config)
    
    try:
        # 搜索内容（需要人工验证）
        result = await toolkit.search(Platform.WECHAT, "人工智能", 1)
        print(f"搜索结果: {result}")
        
        # 下载第一个结果
        if result["status"] == "success" and result["results"]:
            first_result = result["results"][0]
            download_result = await toolkit.download_content(
                Platform.WECHAT,
                first_result["link"],
                Path("data/wechat"),
                first_result["title"]
            )
            print(f"下载结果: {download_result}")
    
    finally:
        await toolkit.cleanup()

asyncio.run(search_wechat())
```

### 批量下载

```python
# examples/batch_download.py
import asyncio
from pathlib import Path
from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform

async def batch_download():
    config = ScrapingConfig(
        platform=Platform.ZHIHU,
        headless=False,
        max_pages=3,
        output_dir=Path("data/batch")
    )
    
    toolkit = ScraperToolkit(config)
    
    try:
        # 批量下载
        result = await toolkit.batch_download(
            Platform.ZHIHU,
            "机器学习",
            Path("data/batch"),
            3
        )
        print(f"批量下载结果: {result}")
    
    finally:
        await toolkit.cleanup()

asyncio.run(batch_download())
```

## 命令行工具

### 基本用法

```bash
# 查看帮助
python -m src.cli --help

# 查看平台信息
python -m src.cli info

# 查看特定平台信息
python -m src.cli info zhihu
```

### 搜索命令

```bash
# 搜索知乎内容
python -m src.cli search zhihu "Python编程" --max-pages 2

# 搜索微信内容（需要人工验证）
python -m src.cli search wechat "人工智能" --max-pages 1
```

### 下载命令

```bash
# 下载知乎页面
python -m src.cli download zhihu "https://www.zhihu.com/question/123456"

# 下载微信页面（需要人工验证）
python -m src.cli download wechat "https://weixin.sogou.com/link?url=..."
```

### 批量下载命令

```bash
# 批量下载知乎内容
python -m src.cli batch zhihu "机器学习" --max-pages 3 --output data/ml

# 批量下载微信内容（需要人工验证）
python -m src.cli batch wechat "深度学习" --max-pages 1 --output data/dl
```

### 快速命令

```bash
# 快速搜索
python -m src.cli quick-search zhihu "Python编程"

# 快速下载
python -m src.cli quick-download zhihu "https://www.zhihu.com/question/123456"
```

## 配置选项

### ScrapingConfig 参数

- `platform`: 平台类型（Platform.ZHIHU, Platform.WECHAT）
- `headless`: 是否无头模式（默认False）
- `persistent`: 是否使用持久化浏览器上下文（默认False）
- `max_pages`: 最大搜索页数（默认3）
- `output_dir`: 输出目录（默认"data"）
- `timeout`: 超时时间（默认300秒）
- `wait_for_verification`: 是否等待人工验证（默认True）

## 注意事项

### 微信平台特殊说明

1. **需要人工验证**：微信搜索通过搜狗搜索，需要完成验证码验证
2. **必须显示浏览器**：不能使用无头模式，因为需要用户交互
3. **等待时间**：程序会等待用户完成验证，不会超时
4. **验证提示**：程序会显示清晰的验证提示信息

### 通用注意事项

1. **浏览器要求**：需要安装Chrome浏览器
2. **网络要求**：需要稳定的网络连接
3. **反爬虫**：某些平台可能有反爬虫机制，需要人工处理
4. **资源清理**：使用完毕后记得调用`cleanup()`方法清理资源

## 项目结构

```
scraper-toolkit/
├── src/
│   ├── core/
│   │   ├── scraper_toolkit.py    # 主工具包
│   │   ├── web_scraper.py        # 知乎抓取器
│   │   ├── wechat_scraper.py     # 微信抓取器
│   │   └── advanced_stealth.py   # 高级反爬虫技术
│   ├── cli.py                    # 命令行接口
│   └── utils/
│       └── logger.py             # 日志工具
├── examples/
│   ├── zhihu_search.py           # 知乎搜索示例
│   ├── wechat_search.py          # 微信搜索示例
│   ├── batch_download.py         # 批量下载示例
│   └── quick_usage.py            # 快速使用示例
├── data/                         # 默认输出目录
├── requirements.txt              # 依赖文件
└── README.md                     # 说明文档
```

## 开发说明

### 添加新平台

1. 在`Platform`枚举中添加新平台
2. 在`ScraperToolkit`中添加平台特定的处理方法
3. 在`get_platform_info`中添加平台信息
4. 更新命令行工具支持新平台

### 扩展功能

1. 在`ScraperToolkit`类中添加新方法
2. 在命令行工具中添加对应的命令
3. 在examples中添加使用示例
4. 更新文档说明

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持知乎和微信平台
- 提供完整的命令行工具
- 支持人工验证等待
- 提供丰富的使用示例
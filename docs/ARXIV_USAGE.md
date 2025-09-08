# ArXiv 文献搜索下载功能

本功能集成到现有项目架构中，提供强大的ArXiv学术文献搜索和自动下载功能。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip3 install --break-system-packages aiohttp feedparser
```

### 2. 快速使用工具
```bash
python3 arxiv_quick_tool.py
```

### 3. 编程接口使用
```python
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from core.arxiv_searcher import ArxivSearcher

async def example():
    searcher = ArxivSearcher()
    
    # 搜索并下载
    result = await searcher.search_and_download(
        query="machine learning",
        max_results=10,
        auto_download=True
    )
    print(result)

asyncio.run(example())
```

## 🆕 最新功能：智能Markdown转换

### � 支持的转换器

系统内置多个PDF转Markdown转换器，按质量排序：

1. **PyMuPDF4LLM** (推荐) - 现代化转换，支持表格、图片
2. **pdfplumber** - 轻量级，适合简单文档，支持表格提取
3. **pypandoc** - 传统工具，基础转换功能
4. **marker** (实验性) - 专为学术论文设计，最高质量

### 🔧 转换方法

#### 方法1：快速工具
```bash
python3 arxiv_quick_tool.py
# 按提示选择：是否转换为Markdown? (y/n)
# 选择转换方法：pymupdf4llm/pdfplumber/pypandoc
```

#### 方法2：编程接口
```python
# 自动选择最佳转换器
result = await searcher.download_and_convert_to_markdown(
    paper, 
    convert_method="pdf"  # 或 "tex" 或 "both"
)

# 指定转换器
result = searcher.convert_pdf_to_markdown(
    pdf_path, 
    converter="pymupdf4llm"  # 或其他转换器
)

# 批量转换
result = await searcher.batch_convert_to_markdown(
    papers,
    convert_method="pdf"
)
```

### 📊 转换质量对比

| 转换器 | 速度 | 质量 | 表格支持 | 数学公式 | 图片处理 |
|--------|------|------|----------|----------|----------|
| PyMuPDF4LLM | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐ | ✅ |
| pdfplumber | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ | ❌ | ❌ |
| pypandoc | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ❌ |
| marker | ⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ | ✅ |

### 🗂️ 输出文件

转换后的文件按转换器分类命名：
```
K-Vault/ArXiv/markdown/
├── paper_name_pymupdf.md     # PyMuPDF4LLM转换
├── paper_name_pdfplumber.md  # pdfplumber转换
├── paper_name_pandoc.md      # pypandoc转换
└── paper_name_marker.md      # marker转换 (如可用)
```

### 核心类：ArxivSearcher

位置：`src/core/arxiv_searcher.py`

#### 主要方法：

1. **`search_arxiv()`** - 搜索文献
   - 支持关键词搜索
   - 类别筛选（cs.AI, cs.LG等）
   - 日期范围筛选
   - 排序选项

2. **`download_paper()`** - 下载单篇文献
   - 自动获取PDF
   - 保存元数据
   - 智能文件命名

3. **`batch_download()`** - 批量下载
   - 并发控制
   - 进度跟踪
   - 错误处理

4. **`search_and_download()`** - 一站式服务
   - 搜索 + 下载一体化
   - 可选择仅搜索不下载

### 收集器：ArxivContentCollector

位置：`collect_arxiv_content.py`

预定义的收集模式：
- `collect_ai_papers()` - AI相关论文
- `collect_robotics_papers()` - 机器人学论文
- `collect_recent_papers()` - 最近论文
- `collect_by_query()` - 自定义查询

## 🛠️ 使用示例

### 基础搜索
```python
result = await searcher.search_arxiv(
    query="deep learning",
    max_results=20
)
```

### 分类搜索
```python
result = await searcher.search_arxiv(
    query="neural networks",
    categories=["cs.AI", "cs.LG", "cs.NE"],
    max_results=50
)
```

### 日期筛选
```python
result = await searcher.search_arxiv(
    query="transformer",
    start_date="2020-01-01",
    end_date="2023-12-31",
    max_results=30
)
```

### 搜索并下载
```python
result = await searcher.search_and_download(
    query="computer vision",
    max_results=10,
    auto_download=True
)
```

### 仅搜索不下载
```python
result = await searcher.search_and_download(
    query="natural language processing",
    max_results=50,
    auto_download=False
)
```

## 📁 文件结构

```
output/arxiv/
├── metadata/           # 元数据JSON文件
│   ├── cs.AI/         # 按类别组织
│   ├── cs.LG/
│   └── ...
├── pdfs/              # PDF文件
│   ├── cs.AI/
│   ├── cs.LG/
│   └── ...
├── progress.json      # 下载进度
└── search_cache.json  # 搜索缓存
```

## 🔧 配置选项

### ArxivSearcher 初始化参数
```python
searcher = ArxivSearcher(
    output_dir="./output/arxiv",  # 输出目录
    max_concurrent=5,             # 最大并发数
    delay_between_requests=1.0    # 请求间隔
)
```

### 搜索参数
- `query`: 搜索关键词
- `max_results`: 最大结果数 (默认100)
- `sort_by`: 排序方式 ("relevance", "lastUpdatedDate", "submittedDate")
- `sort_order`: 排序顺序 ("ascending", "descending")
- `categories`: 类别筛选列表
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

### 常用类别代码
- `cs.AI` - 人工智能
- `cs.LG` - 机器学习
- `cs.CV` - 计算机视觉
- `cs.CL` - 计算语言学
- `cs.RO` - 机器人学
- `cs.NE` - 神经与进化计算
- `stat.ML` - 统计机器学习

## 📊 返回结果格式

### 搜索结果
```json
{
  "status": "success",
  "message": "搜索完成",
  "query": "machine learning",
  "results": [
    {
      "title": "论文标题",
      "arxiv_id": "1234.5678v1",
      "authors": ["作者1", "作者2"],
      "summary": "摘要内容",
      "published": "2023-01-15",
      "updated": "2023-01-20",
      "categories": ["cs.LG"],
      "pdf_url": "https://arxiv.org/pdf/1234.5678v1.pdf",
      "arxiv_url": "https://arxiv.org/abs/1234.5678v1"
    }
  ],
  "total_results": 150
}
```

### 下载统计
```json
{
  "status": "success",
  "download_summary": {
    "total_papers": 10,
    "successful_downloads": 8,
    "skipped_papers": 1,
    "failed_downloads": 1,
    "success_rate": 80.0
  }
}
```

## 🚨 注意事项

1. **API限制**: ArXiv API有速率限制，建议合理设置请求间隔
2. **文件大小**: PDF文件可能较大，注意磁盘空间
3. **网络稳定**: 需要稳定的网络连接进行下载
4. **macOS用户**: 需要使用 `--break-system-packages` 标志安装依赖

## 🔄 与现有项目集成

本功能完全遵循项目现有架构：
- 使用统一的Logger系统
- 遵循相同的文件组织模式
- 采用异步编程模式
- 集成进度跟踪机制

可以轻松与现有的爬虫和数据收集功能协同工作。

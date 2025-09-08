🔬 ArXiv 文献搜索下载 - 快速参考卡
==================================================

📋 核心命令
--------------------------------------------------
# 快速交互式工具 (包含Markdown转换)
python3 arxiv_quick_tool.py

# 预定义收集器
python3 collect_arxiv_content.py

# 示例脚本
python3 examples/arxiv_search_example.py

# 转换器对比测试
python3 test_converter_comparison.py

📋 Markdown转换功能 🆕
--------------------------------------------------
# 支持的转换器（按推荐顺序）
1. pymupdf4llm - 现代化，快速，质量好
2. pdfplumber  - 轻量级，支持表格
3. pypandoc    - 传统工具，基础功能
4. marker      - 实验性，最高质量

# 转换方法选择
convert_method = "pdf"     # PDF转换（推荐）
convert_method = "tex"     # TeX源码转换
convert_method = "both"    # 两种都试

📋 编程接口
--------------------------------------------------
from core.arxiv_searcher import ArxivSearcher

# 创建搜索器
searcher = ArxivSearcher()

# 搜索并转换为Markdown（一站式）
result = await searcher.download_and_convert_to_markdown(
    paper,
    convert_method="pdf"  # pdf/tex/both
)

# 批量转换
result = await searcher.batch_convert_to_markdown(
    papers, 
    convert_method="pdf"
)

# 指定转换器
result = searcher.convert_pdf_to_markdown(
    pdf_path,
    converter="pymupdf4llm"  # 或 pdfplumber/pypandoc
)

📋 常用参数
--------------------------------------------------
类别代码:
- cs.AI    - 人工智能
- cs.LG    - 机器学习  
- cs.CV    - 计算机视觉
- cs.CL    - 计算语言学
- cs.RO    - 机器人学
- cs.NE    - 神经网络
- stat.ML  - 统计机器学习

排序方式:
- relevance        - 相关性（默认）
- lastUpdatedDate  - 最后更新日期
- submittedDate    - 提交日期

排序顺序:
- descending - 降序（默认）
- ascending  - 升序

📋 目录结构
--------------------------------------------------
K-Vault/ArXiv/
├── pdfs/              # PDF文件
├── metadata/          # 元数据JSON
├── markdown/          # 🆕 Markdown转换文件
│   ├── *_pymupdf.md   # PyMuPDF4LLM转换
│   ├── *_pdfplumber.md # pdfplumber转换
│   └── *_pandoc.md    # pypandoc转换
├── tex_sources/       # 🆕 TeX源码文件
├── progress.json      # 下载进度
├── search_cache.json  # 搜索缓存
└── download_summary.json

📋 快速示例
--------------------------------------------------
# 基础搜索
await searcher.search_arxiv("transformer")

# 分类搜索
await searcher.search_arxiv(
    "neural networks", 
    categories=["cs.AI", "cs.LG"]
)

# 日期筛选
await searcher.search_arxiv(
    "reinforcement learning",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# 搜索+下载
await searcher.search_and_download(
    "computer vision",
    max_results=5,
    auto_download=True
)

📋 故障排除
--------------------------------------------------
# 依赖安装（macOS）
pip3 install --break-system-packages aiohttp feedparser

# 权限问题
chmod +x arxiv_quick_tool.py

# 网络问题
- 检查网络连接
- 考虑降低并发数：max_concurrent=3
- 增加请求间隔：delay_between_requests=2.0

📋 配置调优
--------------------------------------------------
# 搜索器配置
searcher = ArxivSearcher(
    output_dir="./custom_output",  # 自定义输出目录
    max_concurrent=5,              # 并发数（默认5）
    delay_between_requests=1.0     # 请求间隔秒数
)

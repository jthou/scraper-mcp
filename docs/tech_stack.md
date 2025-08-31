# 技术栈和依赖库详细说明

## 核心技术栈

### 1. 编程语言
- **Python 3.8+** - 主要开发语言
- **类型提示** - 使用 `typing` 模块提高代码质量
- **异步编程** - 使用 `asyncio` 支持并发处理

### 2. Web自动化和截图
- **Playwright** - 现代化的浏览器自动化工具
  - 支持 Chromium, Firefox, WebKit
  - 内置截图功能
  - 支持JavaScript渲染
  - 跨平台兼容性好

### 3. OCR文字识别
- **飞桨OCR 3.0** - 百度开源的OCR引擎
  - 支持多语言识别
  - 识别精度高
  - 支持表格、公式等复杂内容
  - 本地部署，隐私安全

### 4. PDF处理
- **PyPDF2** - PDF文件读写和操作
- **weasyprint** - HTML转PDF，质量高
- **reportlab** - PDF生成和打印支持

### 5. MCP协议实现
- **mcp** - 官方MCP Python库
- **fastapi** - 可选，用于HTTP API接口

## 详细依赖库列表

### 核心依赖 (requirements.txt)

```txt
# Web自动化和截图
playwright>=1.40.0
asyncio

# OCR引擎
paddlepaddle>=2.5.0
paddleocr>=3.0.0
opencv-python>=4.8.0
pillow>=10.0.0

# PDF处理
PyPDF2>=3.0.0
weasyprint>=60.0
reportlab>=4.0.0

# MCP协议
mcp>=0.1.0

# 数据处理
beautifulsoup4>=4.12.0
lxml>=4.9.0
markdown>=3.5.0

# 配置和日志
pyyaml>=6.0
python-dotenv>=1.0.0
loguru>=0.7.0

# 异步支持
aiofiles>=23.0.0
httpx>=0.25.0

# 开发工具
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
flake8>=6.0.0
```

### 可选依赖

```txt
# HTTP API支持
fastapi>=0.104.0
uvicorn>=0.24.0

# 数据库支持
sqlite3  # 内置
# 或
sqlalchemy>=2.0.0

# 任务队列
celery>=5.3.0
redis>=5.0.0

# 监控和性能
psutil>=5.9.0
memory-profiler>=0.61.0
```

## 版本兼容性

### Python版本要求
- **最低版本**: Python 3.8
- **推荐版本**: Python 3.9+
- **原因**: 支持类型提示、异步编程等现代特性

### 操作系统支持
- **Windows**: 10/11 (64位)
- **macOS**: 10.15+ (Intel/Apple Silicon)
- **Linux**: Ubuntu 18.04+, CentOS 7+, RHEL 7+

### 浏览器引擎
- **Chromium**: 内置，无需安装
- **Firefox**: 可选，需要系统安装
- **WebKit**: 可选，macOS内置

## 性能考虑

### 内存使用
- OCR模型加载: ~500MB-1GB
- 截图缓存: 可配置，默认100MB
- PDF处理: 根据页面复杂度，通常<100MB

### 并发支持
- 支持同时处理多个网页
- 建议并发数: 2-4个（避免资源竞争）
- 异步I/O，不会阻塞主线程

### 存储空间
- OCR模型: ~500MB
- 临时文件: 可配置清理策略
- 输出文件: 根据内容大小而定

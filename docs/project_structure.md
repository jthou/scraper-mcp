# 项目目录结构设计

```scraper-mcp/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── web_scraper.py       # 网页抓取模块
│   │   ├── screenshot.py         # 截图模块
│   │   ├── ocr_engine.py         # OCR识别模块
│   │   ├── pdf_generator.py      # PDF生成模块
│   │   └── markdown_converter.py # Markdown转换模块
│   ├── mcp/                      # MCP Server相关
│   │   ├── __init__.py
│   │   ├── server.py             # MCP Server主类
│   │   ├── tools.py              # 工具函数注册
│   │   └── schemas.py            # 数据模型定义
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── config.py             # 配置管理
│   │   ├── logger.py             # 日志管理
│   │   └── file_manager.py       # 文件管理
│   └── cli.py                    # 命令行接口
├── config/                       # 配置文件目录
│   ├── config.yaml              # 主配置文件
│   └── logging.yaml             # 日志配置
├── data/                        # 数据目录
│   ├── screenshots/             # 截图存储
│   ├── pdfs/                    # PDF文件存储
│   ├── markdown/                # Markdown文件存储
│   └── temp/                    # 临时文件
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── test_core/               # 核心模块测试
│   └── test_mcp/                # MCP模块测试
├── docs/                        # 文档目录
│   ├── README.md
│   ├── API.md
│   └── examples/                # 使用示例
├── requirements.txt              # Python依赖
├── setup.py                     # 安装配置
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git忽略文件
└── main.py                      # 主程序入口
```

## 设计原则

1. **模块化设计**: 每个功能模块独立，便于维护和测试
2. **分层架构**: core(核心) -> mcp(协议) -> cli(接口)
3. **配置分离**: 配置文件和代码分离，便于部署
4. **数据管理**: 不同类型的数据分别存储，便于管理
5. **测试友好**: 独立的测试目录，便于单元测试

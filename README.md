# MCP Server 部署指南

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Chrome浏览器（已安装）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动MCP服务器
```bash
python main.py
```

## 📋 可用工具

启动后，MCP服务器提供以下工具：

- **`open_webpage`** - 使用系统Chrome浏览器打开指定网页
- **`get_page_info`** - 获取网页基本信息
- **`login_zhihu`** - 登录知乎网站，保持登录状态
- **`read_zhihu_page`** - 读取知乎网页内容（需要已登录）
- **`search_zhihu`** - 搜索知乎内容，获取符合要求的所有页面链接

## 🔧 配置说明

### 浏览器配置
- 默认使用系统Chrome浏览器
- 支持无头模式（headless）和可视化模式
- 自动处理反爬虫策略

### 数据存储
- 所有输出文件存储在`data/`目录
- 截图、PDF、Markdown文件自动分类存储
- 支持自定义输出路径

## 🧪 测试

运行测试脚本验证功能：
```bash
python -m pytest tests/
```

## 📁 项目结构

```
scraper-mcp/
├── main.py              # MCP服务器入口
├── src/                 # 核心源代码
│   ├── core/           # 核心功能模块
│   └── utils/          # 工具函数
├── tests/              # 测试文件
├── config/             # 配置文件
└── requirements.txt    # Python依赖
```

## ⚠️ 注意事项

- 首次使用知乎功能需要手动扫码登录
- 浏览器数据存储在`data/browser_data/`目录
- 确保Chrome浏览器版本兼容
- 建议在虚拟环境中运行

## 🔗 相关链接

- [MCP协议规范](https://modelcontextprotocol.io/)
- [Playwright文档](https://playwright.dev/)
- [PaddleOCR文档](https://github.com/PaddlePaddle/PaddleOCR)

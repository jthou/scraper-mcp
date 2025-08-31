# 部署和测试步骤指南

## 概述

本文档详细说明了网页内容抓取工具的部署步骤和测试方法。按照小步迭代的原则，确保每个步骤都可以独立验证。

## 环境要求

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python版本**: Python 3.8+ (推荐 3.9+)
- **内存**: 至少 2GB RAM
- **存储**: 至少 1GB 可用空间

### Python环境
```bash
# 检查Python版本
python --version

# 检查pip版本
pip --version
```

## 部署步骤

### 1. 克隆项目
```bash
# 克隆项目到本地
git clone <repository-url>
cd scraper-mcp
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 安装依赖
```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 4. 创建必要目录
```bash
# 创建数据目录
mkdir -p data/screenshots data/pdfs data/markdown data/temp

# 创建日志目录
mkdir -p logs
```

## 测试步骤

### 1. 基础功能测试

#### 1.1 测试主程序
```bash
# 运行主程序
python main.py

# 预期输出: 启动成功，所有模块初始化成功
```

#### 1.2 测试核心模块
```bash
# 测试网页抓取模块
python tests/test_core/test_web_scraper.py

# 测试MCP Server模块
python tests/test_mcp/test_server.py
```

### 2. 使用pytest进行自动化测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_core/test_web_scraper.py
pytest tests/test_mcp/test_server.py
```

## 故障排除

### 常见问题

#### 1. 模块导入错误
- 确保在项目根目录运行
- 检查src目录是否存在

#### 2. 依赖安装失败
- 升级pip: `pip install --upgrade pip`
- 清理缓存: `pip cache purge`
- 重新安装: `pip install -r requirements.txt --force-reinstall`

#### 3. 权限问题
```bash
# Linux/macOS权限问题
sudo chown -R $USER:$USER data/ logs/
chmod 755 data/ logs/
```

## 部署检查清单

### 部署前检查
- [ ] Python版本 >= 3.8
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已安装
- [ ] 配置文件已创建
- [ ] 必要目录已创建

### 部署后验证
- [ ] 主程序可以运行 (`python main.py`)
- [ ] 所有测试通过 (`pytest`)
- [ ] 配置文件可以加载
- [ ] 日志可以正常写入
- [ ] 数据目录可以访问

## 下一步

完成基础框架的部署和测试后，可以开始实现具体的功能模块。

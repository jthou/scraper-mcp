# GitHub Token 快速配置指南

## 方案1: 使用 `.env` 文件 (推荐)

### 1. 快速设置
```bash
python simple_setup.py
```

### 2. 手动创建 `.env` 文件
```bash
# 复制示例文件
cp .env.example .env

# 编辑文件，填入你的Token
vim .env
```

### 3. 测试配置
```bash
python simple_test.py
```

## 方案2: 环境变量
```bash
export GITHUB_TOKEN=your_token_here
```

## GitHub Token 创建步骤

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 填写描述（如：Scraper Tool）
4. 选择权限：
   - ✅ `repo` - 访问仓库
   - ✅ `read:user` - 读取用户信息
   - ✅ `read:org` - 读取组织信息
5. 点击 "Generate token"
6. 复制Token（只显示一次！）

## 使用示例

```python
from src.core.github.simple_config import GitHubConfig

# 自动加载配置
config = GitHubConfig()

# 检查配置
if config.is_configured:
    print(f"Token: {config.github_token[:10]}...")
    print(f"Headers: {config.headers}")
else:
    print("请配置GitHub Token")
```

## 文件说明

- `.env.example` - 配置模板
- `simple_setup.py` - 快速设置脚本  
- `simple_test.py` - 配置测试脚本
- `src/core/github/simple_config.py` - 简化配置类

## 安全提醒

- ✅ 使用 `.env` 文件（已在 .gitignore 中）
- ❌ 不要在代码中硬编码Token
- ❌ 不要提交Token到Git

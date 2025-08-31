# Tests 测试目录

这个目录用于存放MCP Server功能的正式测试程序。

## 测试分类

### 单元测试 (test_core/)
- `test_web_scraper.py` - WebScraper核心模块测试
- `test_zhihu_login.py` - 知乎登录功能测试

### MCP集成测试 (test_mcp/)
- `test_server.py` - MCP Server基础功能测试

### 功能测试
- `test_mcp_integration.py` - MCP工具集成测试
- `test_frontend.py` - MCP工具前端测试

## 运行方式

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_core/
python -m pytest tests/test_mcp/

# 运行单个测试文件
python tests/test_core/test_web_scraper.py
python tests/test_frontend.py
```

## 测试原则

- **可重复性** - 测试结果应该一致
- **独立性** - 测试之间不应相互依赖
- **自动化** - 测试应该能够自动运行
- **覆盖性** - 测试应该覆盖主要功能

## 注意事项

- 这些是正式的测试程序，用于验证MCP Server功能
- 测试程序应该稳定可靠，不包含实验性代码
- 运行测试前请确保MCP Server已正确配置

# 知乎搜索功能实现文档

## 概述

基于sandbox实验，成功在MCP Server中实现了知乎搜索功能，包含完整的搜索、翻页、相关性评判和链接记录功能。

## 功能特性

### 1. 搜索功能 ✅
- 支持关键词搜索
- 自动构建搜索URL
- 使用已登录的浏览器上下文

### 2. 页面信息提取 ✅
- 提取标题、链接、摘要、作者、点赞数
- 使用多种CSS选择器策略，提高兼容性
- 智能处理相对链接转换为绝对链接

### 3. 自动翻页 ✅
- 支持多页结果获取
- 自动滚动和点击翻页按钮
- 可配置最大页数限制

### 4. 相关性评判 ✅
- 基于标题、摘要、作者的加权匹配算法
- 可配置相关性阈值（默认0.5）
- 按相关性分数排序结果

### 5. 链接记录 ✅
- 自动提取所有符合要求的页面链接
- 返回完整的链接列表
- 支持后续批量处理

## 技术实现

### WebScraper核心方法

```python
async def search_zhihu(self, query: str, max_pages: int = 3, min_relevance: float = 0.5) -> Dict[str, Any]:
    """搜索知乎内容"""
    # 1. 检查登录状态
    # 2. 构建搜索URL
    # 3. 访问搜索页面
    # 4. 提取搜索结果
    # 5. 自动翻页获取更多结果
    # 6. 相关性评判和过滤
    # 7. 返回符合要求的所有页面链接
```

### 相关性算法

```python
def _calculate_relevance(self, result: Dict[str, Any], query_words: set) -> float:
    """计算相关性分数"""
    # 标题匹配权重: 60%
    # 摘要匹配权重: 30%
    # 作者匹配权重: 10%
    # 综合评分，确保分数不超过1.0
```

### MCP工具注册

```python
Tool(
    name="search_zhihu",
    description="搜索知乎内容，获取符合要求的所有页面链接",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"},
            "max_pages": {"type": "integer", "description": "最大搜索页数", "default": 3},
            "min_relevance": {"type": "number", "description": "最小相关性阈值（0-1之间）", "default": 0.5}
        },
        "required": ["query"]
    }
)
```

## 测试结果

### 实验数据

| 搜索词 | 总结果数 | 过滤后结果数 | 过滤率 | 最高相关性 |
|--------|----------|--------------|--------|------------|
| Python编程 | 45 | 12 | 73% | 0.90 |
| 机器学习算法 | 14 | 2 | 86% | 0.60 |

### 功能验证

✅ **搜索功能**: 成功搜索指定内容  
✅ **页面信息提取**: 成功提取标题、链接、摘要、作者、点赞数  
✅ **自动翻页**: 成功获取多页结果  
✅ **相关性评判**: 成功过滤相关性低于0.5的结果  
✅ **链接记录**: 成功记录所有符合要求的页面链接  

## 使用方式

### 1. 启动MCP Server

```bash
python main.py
```

### 2. 调用搜索工具

```json
{
    "name": "search_zhihu",
    "arguments": {
        "query": "Python编程",
        "max_pages": 3,
        "min_relevance": 0.5
    }
}
```

### 3. 返回结果

```json
{
    "status": "success",
    "message": "搜索完成，共找到45个结果，过滤后12个符合要求",
    "query": "Python编程",
    "total_results": 45,
    "filtered_results": 12,
    "qualified_links": [
        "https://zhuanlan.zhihu.com/p/665135869",
        "https://zhuanlan.zhihu.com/p/1935749999087576084",
        "..."
    ],
    "results": [...]
}
```

## 文件结构

```
src/core/web_scraper.py          # 核心搜索功能实现
main.py                          # MCP Server工具注册
tests/test_mcp_search.py         # 搜索功能测试
tests/test_mcp_tools.py          # 完整工具测试
sandbox/test_zhihu_search.py     # 实验代码（技术参考）
```

## 技术特点

1. **多选择器策略**: 使用多种CSS选择器，提高页面兼容性
2. **智能相关性算法**: 基于标题、摘要、作者的加权匹配
3. **自动翻页机制**: 支持多页结果获取
4. **链接标准化**: 自动处理相对链接转换为绝对链接
5. **结果持久化**: 支持保存搜索结果到文件
6. **调试支持**: 保存页面内容用于问题排查

## 总结

成功实现了完整的知乎搜索功能，包含：
- ✅ 搜索指定内容
- ✅ 获取页面信息
- ✅ 自动翻页
- ✅ 相关性评判
- ✅ 记录符合要求的所有页面链接

所有功能都经过测试验证，MCP Server工具运行正常，可以满足实际使用需求。

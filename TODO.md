# 网页内容抓取工具开发任务清单

## ⚠️ 重要提示
**每个任务开始前，都要先读一遍开发总则！**

## 开发总则
- **小步迭代**: 每个任务都要分解成小的、可验证的子任务
- **最小可行产品**: 先实现最基础的功能，再逐步完善
- **测试驱动**: 每个模块都要有对应的测试，确保功能正确
- **可运行优先**: 优先保证基础框架能跑，再考虑功能完善

## 项目概述
创建一个全面的网页内容抓取MCP Server工具，包含网页抓取、截图、OCR识别、PDF生成、Markdown转换等功能。

## 核心功能模块设计
1. **网页抓取模块** - 负责访问和获取网页内容
2. **截图模块** - 负责生成网页截图
3. **OCR模块** - 负责图片文字识别
4. **PDF模块** - 负责生成和打印PDF
5. **Markdown模块** - 负责格式转换
6. **MCP Server模块** - 负责协议实现和工具注册

## 技术栈选择
- **语言**: Python 3.8+
- **Web自动化**: Playwright
- **OCR引擎**: 飞桨OCR 3.0
- **PDF处理**: PyPDF2 + weasyprint
- **MCP框架**: mcp库

## 任务1: 设计合理的项目框架 ✅
- [x] 1.1 分析需求，确定核心功能模块
- [x] 1.2 设计项目目录结构
- [x] 1.3 设计各模块之间的接口和依赖关系
- [x] 1.4 确定技术栈和依赖库
- [x] 1.5 设计数据流和错误处理机制

## 任务2: 生成基本的程序框架 ✅
- [x] 2.1 创建项目目录结构
- [x] 2.2 创建最基础的配置文件 (config.yaml)
- [x] 2.3 创建核心模块的基础类 (每个模块一个最简单的类)
- [x] 2.4 创建MCP Server基础框架
- [x] 2.5 创建自动启动脚本 (main.py)
- [x] 2.6 创建第一个回归测试 (覆盖每个模块的基础功能)
- [x] 2.7 验证基础框架可以运行

### 任务2设计原则
- **小步迭代**: 每个组件只实现最基础的功能
- **可测试**: 每个模块都要有对应的测试
- **最小化**: 不添加任何高级功能，只保证基础框架能跑
- **回归测试**: 测试要覆盖到每个模块的基本功能

## 任务3: 实现网页打开功能 ✅
- [x] 3.1 在WebScraper模块中添加打开网页功能
- [x] 3.2 集成系统Chrome浏览器支持
- [x] 3.3 在MCP Server中注册网页打开工具
- [x] 3.4 创建对应的测试用例
- [x] 3.5 验证MCP工具可以正常调用

### 任务3设计原则
- **最小化实现**: 只实现打开指定网页的功能
- **系统集成**: 使用系统Chrome，不使用Playwright内置浏览器
- **MCP工具化**: 作为MCP Server的一个工具函数
- **可测试**: 确保新功能有对应的测试

## 任务4: 实现知乎登录工具 ✅
- [x] 4.1 在WebScraper模块中添加知乎登录状态检测功能
- [x] 4.2 实现登录状态持久化，避免重复登录
- [x] 4.3 在MCP Server中注册"登录知乎"工具
- [x] 4.4 添加知乎网页内容读取功能
- [x] 4.5 创建对应的测试用例
- [x] 4.6 验证登录状态保持和网页读取功能

### 任务4设计原则
- **状态持久化**: 使用浏览器用户数据目录保存登录状态
- **智能检测**: 自动检测登录状态，避免重复登录
- **持续读取**: 登录后能够持续读取知乎网页内容
- **错误处理**: 完整的登录失败和状态异常处理

### 任务4验证方法
1. **首次登录**: 运行工具，手动扫码登录，验证登录成功
2. **状态保持**: 关闭后重新运行，验证自动识别已登录状态
3. **网页读取**: 登录后读取知乎首页内容，验证内容获取
4. **异常处理**: 测试网络异常、登录失败等情况

## 任务5: 完善内容下载和文件管理功能 ✅
- [x] 5.1 扩展WebScraper，支持自定义文件保存路径
- [x] 5.2 实现基于知乎标题的智能文件命名系统
- [x] 5.3 在MCP Server中添加PDF生成和保存工具
- [x] 5.4 在MCP Server中添加Markdown生成和保存工具
- [x] 5.5 实现PDF和Markdown文件的一一对应机制
- [x] 5.6 创建批量下载工具，支持指定目录保存
- [x] 5.7 添加文件名冲突处理和去重机制
- [x] 5.8 创建对应的测试用例
- [x] 5.9 验证完整的下载和保存流程

### 任务5设计原则
- **路径可配置**: 支持自定义保存目录，不再固定在data/目录
- **文件名智能**: 使用知乎标题作为文件名，处理特殊字符和长度限制
- **格式对应**: 确保PDF和Markdown文件名完全一致，便于管理
- **工具集成**: 作为MCP Server的新工具，便于外部调用
- **错误处理**: 完整的文件保存失败和路径异常处理

### 任务5执行步骤

#### 5.1 扩展WebScraper文件保存功能
```python
# 在WebScraper类中添加方法：
async def download_and_save_content(self, url: str, output_dir: Path, title: str = None)
    # 1. 读取网页内容
    # 2. 清理和生成文件名
    # 3. 保存到指定目录
    # 4. 返回保存结果
```

#### 5.2 实现智能文件命名系统
```python
def clean_filename(self, title: str) -> str:
    # 1. 移除特殊字符: < > : " / \ | ? *
    # 2. 替换空格为下划线
    # 3. 限制文件名长度 (≤100字符)
    # 4. 处理重复文件名 (添加序号)
```

#### 5.3 添加MCP工具: download_zhihu_content
```python
Tool(
    name="download_zhihu_content",
    description="下载知乎内容并保存为PDF和Markdown",
    inputSchema={
        "url": "知乎页面URL",
        "output_dir": "保存目录路径",
        "title": "自定义文件名(可选)"
    }
)
```

#### 5.4 添加MCP工具: batch_download_zhihu
```python
Tool(
    name="batch_download_zhihu",
    description="批量下载知乎搜索结果",
    inputSchema={
        "query": "搜索关键词", 
        "output_dir": "保存目录路径",
        "max_pages": "最大搜索页数",
        "min_relevance": "最小相关性阈值"
    }
)
```

#### 5.5 实现PDF和Markdown对应机制
- PDF文件名: `{clean_title}.pdf`
- Markdown文件名: `{clean_title}.md`  
- 映射文件: `{output_dir}/file_mapping.json`
- 包含: 原始标题、清理后文件名、URL、保存时间

#### 5.6 创建完整的保存流程
1. **内容获取**: 使用现有的read_zhihu_page功能
2. **文件名生成**: 基于标题的智能命名
3. **PDF生成**: 将HTML内容转换为PDF
4. **Markdown生成**: 提取和格式化文本内容
5. **文件保存**: 保存到指定目录
6. **映射记录**: 更新file_mapping.json

### 任务5验证方法

#### 验证5.1: 单个文件下载
```bash
# 测试单个URL下载
python -c "
import asyncio
from src.core.web_scraper import WebScraper
from pathlib import Path

async def test():
    scraper = WebScraper()
    await scraper.login_zhihu()
    result = await scraper.download_and_save_content(
        url='https://zhuanlan.zhihu.com/p/123456', 
        output_dir=Path('test_output'),
        title='测试文章标题'
    )
    print(result)

asyncio.run(test())
"
```

#### 验证5.2: 文件名处理
```python
# 测试特殊字符处理
test_titles = [
    "Gazebo仿真教程：从入门到精通",
    "ROS+Gazebo机器人开发指南 | 完整教程",
    "【深度解析】Gazebo物理引擎的工作原理",
    "这是一个非常非常长的标题需要测试长度限制功能的处理能力和效果展示"
]

for title in test_titles:
    clean_name = scraper.clean_filename(title)
    print(f"原标题: {title}")
    print(f"文件名: {clean_name}")
```

#### 验证5.3: 批量下载功能
```bash
# 测试批量下载
# 1. 搜索"Gazebo教程"
# 2. 下载到K-Vault/Gazebo目录
# 3. 验证PDF和Markdown文件对应
# 4. 检查文件映射记录
```

#### 验证5.4: MCP工具集成
```bash
# 启动MCP Server
python main.py

# 调用新工具
# download_zhihu_content: 下载单个内容
# batch_download_zhihu: 批量下载搜索结果
```

#### 验证5.5: 文件完整性检查
```python
# 检查输出目录结构
output_dir/
├── pdfs/
│   ├── Gazebo仿真教程_从入门到精通.pdf
│   └── ROS_Gazebo机器人开发指南_完整教程.pdf
├── markdown/
│   ├── Gazebo仿真教程_从入门到精通.md
│   └── ROS_Gazebo机器人开发指南_完整教程.md
└── file_mapping.json

# 验证文件映射
{
  "Gazebo仿真教程_从入门到精通": {
    "original_title": "Gazebo仿真教程：从入门到精通",
    "url": "https://zhuanlan.zhihu.com/p/123456",
    "pdf_file": "pdfs/Gazebo仿真教程_从入门到精通.pdf",
    "markdown_file": "markdown/Gazebo仿真教程_从入门到精通.md",
    "download_time": "2025-09-01T14:30:00"
  }
}
```

### 任务5成功标准
1. ✅ 可以指定任意目录保存下载内容
2. ✅ 文件名基于知乎标题，特殊字符正确处理
3. ✅ PDF和Markdown文件名完全对应
4. ✅ 支持单个和批量下载模式
5. ✅ 完整的文件映射和管理机制
6. ✅ MCP工具正确集成和调用
7. ✅ 所有功能都有对应测试覆盖

## 下一步
完成任务5后，项目将具备完整的内容下载和管理能力，可以正式用于生产环境的内容收集工作。

## 当前状态
✅ **任务1**: 设计合理的项目框架 - 已完成
✅ **任务2**: 生成基本的程序框架 - 已完成  
✅ **任务3**: 实现网页打开功能 - 已完成
✅ **任务4**: 实现知乎登录工具 - 已完成
✅ **任务5**: 完善内容下载和文件管理功能 - 已完成

现在有了一个完整的、可工作的MCP Server基础！项目已具备生产级的内容下载功能。

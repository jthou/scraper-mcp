# 持久化浏览器使用指南

## 概述

持久化浏览器功能解决了scraper-mcp项目中浏览器无法记住历史信息、登录状态和Cookie的问题。通过使用Playwright的`launch_persistent_context`功能，可以实现跨会话的状态保持。

## 核心特性

### 🔄 状态持久化
- **Cookie保存**: 自动保存和恢复所有Cookie
- **Local Storage**: 保持本地存储数据
- **Session Storage**: 保持会话存储数据
- **用户数据目录**: 完整的浏览器用户数据持久化

### 🚀 智能管理
- **自动保存**: 可配置的自动状态保存间隔
- **跨平台支持**: 不同平台独立的状态管理
- **登录状态检测**: 智能检测各平台登录状态
- **资源清理**: 自动清理和资源管理

## 快速开始

### 1. 基础使用

```python
import asyncio
from src.core.enhanced_scraper_toolkit import EnhancedScraperToolkit, Platform, EnhancedScrapingConfig

async def basic_usage():
    # 创建配置
    config = EnhancedScrapingConfig(
        platform=Platform.ZHIHU,
        persistent=True,  # 启用持久化
        auto_save_state=True  # 自动保存状态
    )
    
    # 创建工具包
    toolkit = EnhancedScraperToolkit(config)
    
    # 设置持久化浏览器
    await toolkit.setup_persistent_browser(Platform.ZHIHU)
    
    # 检查登录状态
    login_status = await toolkit.check_login_status(Platform.ZHIHU)
    print(f"登录状态: {login_status['message']}")
    
    # 执行搜索
    results = await toolkit.search(Platform.ZHIHU, "人工智能", max_pages=2)
    
    # 清理资源
    await toolkit.cleanup()
```

### 2. 跨平台使用

```python
async def cross_platform_usage():
    # 知乎平台
    zhihu_toolkit = EnhancedScraperToolkit(
        EnhancedScrapingConfig(platform=Platform.ZHIHU, persistent=True)
    )
    await zhihu_toolkit.setup_persistent_browser(Platform.ZHIHU)
    
    # 微信平台
    wechat_toolkit = EnhancedScraperToolkit(
        EnhancedScrapingConfig(platform=Platform.WECHAT, persistent=True)
    )
    await wechat_toolkit.setup_persistent_browser(Platform.WECHAT)
    
    # 各平台独立管理状态
    zhihu_status = await zhihu_toolkit.check_login_status(Platform.ZHIHU)
    wechat_status = await wechat_toolkit.check_login_status(Platform.WECHAT)
```

## 配置选项

### EnhancedScrapingConfig

```python
@dataclass
class EnhancedScrapingConfig:
    platform: Platform                    # 目标平台
    headless: bool = False               # 是否无头模式
    persistent: bool = True              # 是否启用持久化
    max_pages: int = 3                   # 最大搜索页数
    output_dir: Path = Path("data")      # 输出目录
    timeout: int = 300                   # 超时时间（秒）
    wait_for_verification: bool = True   # 等待人工验证
    auto_save_state: bool = True         # 自动保存状态
    state_save_interval: int = 30        # 状态保存间隔（秒）
```

## 核心方法

### 浏览器管理

```python
# 设置持久化浏览器
await toolkit.setup_persistent_browser(Platform.ZHIHU, site="zhihu.com")

# 获取页面实例
page = await toolkit.get_page(Platform.ZHIHU)

# 获取上下文实例
context = await toolkit.get_context(Platform.ZHIHU)

# 导航到URL
await toolkit.navigate_to("https://www.zhihu.com", Platform.ZHIHU)
```

### 状态管理

```python
# 检查登录状态
login_status = await toolkit.check_login_status(Platform.ZHIHU)

# 手动保存状态
await toolkit.browser_manager.save_browser_state(Platform.ZHIHU.value)

# 列出所有保存的状态
states = await toolkit.list_saved_states()

# 清除平台状态
await toolkit.clear_platform_state(Platform.ZHIHU)
```

### 内容操作

```python
# 搜索内容
results = await toolkit.search(Platform.ZHIHU, "查询词", max_pages=3)

# 下载内容
download_result = await toolkit.download_content(
    Platform.ZHIHU, 
    "https://example.com", 
    Path("output"),
    "标题"
)
```

## 状态文件结构

```
data/browser_data/
├── zhihu_abc123/           # 知乎用户数据目录
│   ├── Default/            # Chrome用户数据
│   ├── Local State
│   └── ...
├── wechat_def456/          # 微信用户数据目录
│   └── ...
├── zhihu_abc123_state.json # 知乎状态文件
└── wechat_def456_state.json # 微信状态文件
```

### 状态文件内容

```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123",
      "domain": ".zhihu.com",
      "path": "/",
      "expires": 1234567890
    }
  ],
  "local_storage": {
    "user_preference": "dark_mode",
    "last_search": "人工智能"
  },
  "session_storage": {
    "temp_data": "value"
  },
  "saved_at": "2025-09-20T10:30:00",
  "platform": "zhihu",
  "site": null
}
```

## 最佳实践

### 1. 资源管理

```python
async def proper_cleanup():
    toolkit = EnhancedScraperToolkit(config)
    try:
        # 使用工具包
        await toolkit.setup_persistent_browser(Platform.ZHIHU)
        # ... 执行操作
    finally:
        # 确保清理资源
        await toolkit.cleanup()
```

### 2. 错误处理

```python
async def error_handling():
    toolkit = EnhancedScraperToolkit(config)
    try:
        result = await toolkit.setup_persistent_browser(Platform.ZHIHU)
        if result["status"] != "success":
            print(f"设置失败: {result['message']}")
            return
        
        # 继续操作...
        
    except Exception as e:
        print(f"操作异常: {e}")
    finally:
        await toolkit.cleanup()
```

### 3. 状态检查

```python
async def check_and_login():
    toolkit = EnhancedScraperToolkit(config)
    await toolkit.setup_persistent_browser(Platform.ZHIHU)
    
    # 检查登录状态
    login_status = await toolkit.check_login_status(Platform.ZHIHU)
    
    if not login_status.get("logged_in", False):
        print("需要登录，请手动完成登录操作...")
        # 等待用户登录
        await asyncio.sleep(60)
        
        # 再次检查
        login_status = await toolkit.check_login_status(Platform.ZHIHU)
        if login_status.get("logged_in", False):
            print("登录成功！")
        else:
            print("登录失败")
```

## 故障排除

### 常见问题

1. **状态未保存**
   - 检查`persistent=True`是否设置
   - 确认`auto_save_state=True`
   - 检查文件权限

2. **登录状态丢失**
   - 检查Cookie是否过期
   - 确认用户数据目录存在
   - 重新登录并保存状态

3. **跨平台冲突**
   - 使用不同的`site`参数
   - 检查状态文件是否独立
   - 清理冲突的状态

### 调试技巧

```python
# 列出所有状态
states = await toolkit.list_saved_states()
for state in states:
    print(f"平台: {state['platform']}")
    print(f"Cookies: {state['cookies_count']}")
    print(f"保存时间: {state['saved_at']}")

# 检查特定平台状态
login_status = await toolkit.check_login_status(Platform.ZHIHU)
print(f"登录状态: {login_status}")
```

## 性能优化

### 1. 状态保存频率

```python
# 降低保存频率以减少I/O
config = EnhancedScrapingConfig(
    state_save_interval=60  # 每60秒保存一次
)
```

### 2. 内存管理

```python
# 定期清理不需要的状态
await toolkit.clear_platform_state(Platform.OLD_PLATFORM)
```

### 3. 并发控制

```python
# 避免同时操作同一平台
async def safe_operation():
    async with asyncio.Lock():
        await toolkit.setup_persistent_browser(Platform.ZHIHU)
        # 执行操作
```

## 迁移指南

### 从旧版本迁移

1. **替换导入**
   ```python
   # 旧版本
   from src.core.scraper_toolkit import ScraperToolkit
   
   # 新版本
   from src.core.enhanced_scraper_toolkit import EnhancedScraperToolkit
   ```

2. **更新配置**
   ```python
   # 旧版本
   config = ScrapingConfig(platform=Platform.ZHIHU)
   
   # 新版本
   config = EnhancedScrapingConfig(
       platform=Platform.ZHIHU,
       persistent=True,
       auto_save_state=True
   )
   ```

3. **添加清理代码**
   ```python
   # 确保在finally块中调用cleanup
   try:
       # 使用工具包
       pass
   finally:
       await toolkit.cleanup()
   ```

## 示例项目

查看 `examples/persistent_browser_demo.py` 获取完整的使用示例。

## 技术支持

如有问题，请检查：
1. Playwright是否正确安装
2. 用户数据目录权限
3. 网络连接状态
4. 平台特定的登录要求

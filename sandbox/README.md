# Sandbox 实验目录

这个目录用于存放实验性代码、测试脚本和开发过程中的临时文件。

## 目录结构

```
sandbox/
├── README.md                    # 本说明文件
├── experiments/                 # 实验性代码
│   ├── wechat_search_experiment.py    # 微信公众号搜索实验
│   └── wechat_search_analysis.md      # 搜索技术分析文档
├── test_scripts/               # 测试脚本
│   └── test_wechat_search.py          # 微信搜索测试脚本
├── prototypes/                 # 原型代码
│   └── wechat_search_prototype.py     # 微信搜索原型
└── temp/                       # 临时文件
```

## 当前实验项目

### 搜狗微信搜索实验 ⭐

#### 实验目标
专门优化搜狗微信搜索功能，这是目前最可行的微信公众号搜索方案。

#### 搜狗搜索优势
- **无需登录**: 不需要微信账号，降低使用门槛
- **搜索结果完整**: 覆盖大部分微信公众号内容
- **支持关键词搜索**: 可以精确搜索特定内容
- **相对稳定**: 相比其他方法，搜狗搜索相对稳定

#### 技术挑战
- 验证码问题（图片、滑块、极验等）
- 反爬虫机制严格
- 动态加载内容
- 翻页机制复杂

#### 文件说明

**experiments/sogou_wechat_search.py** ⭐
- 搜狗微信搜索专用模块
- 完整的反爬虫对策
- 智能验证码检测
- 多页搜索和结果去重

**experiments/sogou_search_optimization.md**
- 搜狗搜索优化策略
- 性能优化建议
- 数据质量提升
- 监控和日志方案

**test_scripts/test_sogou_search.py**
- 搜狗搜索专项测试
- 基础搜索、翻页、验证码处理测试
- 数据质量分析
- 重试机制测试

**prototypes/sogou_search_simple.py**
- 搜狗搜索简化版
- 快速验证和测试
- 适合初学者使用

### 微信公众号搜索实验

#### 实验目标
探索多种微信公众号搜索方法，包括搜狗、微信PC版、第三方平台等。

#### 实验方法
1. **搜狗微信搜索** - 通过搜狗搜索引擎的微信搜索功能 ⭐
2. **微信PC版搜索** - 通过微信PC版客户端搜索（需要登录）
3. **第三方平台搜索** - 通过其他聚合平台搜索

#### 文件说明

**experiments/wechat_search_experiment.py**
- 完整的实验实现
- 支持多种搜索方法
- 包含反爬虫对策
- 结果保存和分析

**experiments/wechat_search_analysis.md**
- 技术分析文档
- 法律合规建议
- 实施策略
- 风险控制

**test_scripts/test_wechat_search.py**
- 自动化测试脚本
- 测试各种搜索方法
- 结果验证和统计

**prototypes/wechat_search_prototype.py**
- 简化的原型实现
- 快速验证可行性
- 适合快速测试

## 使用说明

### 运行实验
```bash
# 搜狗微信搜索（推荐）⭐
python sandbox/experiments/sogou_wechat_search.py
python sandbox/test_scripts/test_sogou_search.py
python sandbox/prototypes/sogou_search_simple.py

# 完整微信搜索实验
python sandbox/experiments/wechat_search_experiment.py
python sandbox/test_scripts/test_wechat_search.py
python sandbox/prototypes/wechat_search_prototype.py
```

### 注意事项
- 实验代码可能不稳定，仅供开发参考
- 不要在生产环境中使用sandbox中的代码
- 遵守相关法律法规，仅用于合法用途
- 定期清理不需要的临时文件

## 文件命名规范

- 实验文件: `exp_功能名_日期.py`
- 测试文件: `test_功能名.py`
- 原型文件: `proto_功能名.py`
- 临时文件: `temp_描述.扩展名`

## 法律声明

本sandbox目录中的代码仅用于学习和研究目的，请遵守相关法律法规：

1. **仅用于个人学习** - 不得用于商业用途
2. **遵守使用条款** - 遵守相关平台的使用条款
3. **尊重版权** - 不侵犯他人版权
4. **合理使用** - 控制请求频率，避免对服务器造成压力

## 下一步计划

1. 完善微信公众号搜索功能
2. 添加更多搜索平台支持
3. 实现搜索结果去重和合并
4. 添加法律合规检查
5. 优化反爬虫对策
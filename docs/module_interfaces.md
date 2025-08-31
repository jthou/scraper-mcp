# 模块接口和依赖关系设计

## 模块依赖图

```
CLI (命令行接口)
    ↓
MCP Server (协议层)
    ↓
Core Modules (核心功能)
    ↓
Utils (工具层)
```

## 详细接口设计

### 1. 核心模块接口 (core/)

#### WebScraper 类
```python
class WebScraper:
    async def scrape_url(self, url: str, wait_time: int = 0) -> ScrapedContent
    async def get_page_content(self, url: str) -> str
    async def get_page_metadata(self, url: str) -> PageMetadata
```

#### Screenshot 类
```python
class Screenshot:
    async def capture_full_page(self, url: str, output_path: str) -> str
    async def capture_element(self, url: str, selector: str, output_path: str) -> str
    async def capture_viewport(self, url: str, output_path: str) -> str
```

#### OCREngine 类
```python
class OCREngine:
    async def recognize_text(self, image_path: str) -> RecognizedText
    async def recognize_text_batch(self, image_paths: List[str]) -> List[RecognizedText]
    async def preprocess_image(self, image_path: str) -> str
```

#### PDFGenerator 类
```python
class PDFGenerator:
    async def html_to_pdf(self, html_content: str, output_path: str) -> str
    async def print_to_pdf(self, url: str, output_path: str) -> str
    async def merge_pdfs(self, pdf_paths: List[str], output_path: str) -> str
```

#### MarkdownConverter 类
```python
class MarkdownConverter:
    async def html_to_markdown(self, html_content: str) -> str
    async def pdf_to_markdown(self, pdf_path: str) -> str
    async def optimize_markdown(self, markdown_content: str) -> str
```

### 2. MCP Server 接口 (mcp/)

#### MCPServer 类
```python
class MCPServer:
    def __init__(self, config: Config)
    async def start(self) -> None
    async def stop(self) -> None
    def register_tools(self) -> None
```

#### 工具函数注册
```python
# 在 tools.py 中注册以下工具
TOOLS = {
    "scrape_webpage": scrape_webpage_tool,
    "capture_screenshot": capture_screenshot_tool,
    "ocr_image": ocr_image_tool,
    "generate_pdf": generate_pdf_tool,
    "convert_to_markdown": convert_to_markdown_tool,
    "batch_process": batch_process_tool
}
```

### 3. 数据模型 (schemas.py)

```python
@dataclass
class ScrapedContent:
    url: str
    html_content: str
    text_content: str
    metadata: PageMetadata
    timestamp: datetime

@dataclass
class PageMetadata:
    title: str
    description: str
    keywords: List[str]
    language: str
    encoding: str

@dataclass
class RecognizedText:
    text: str
    confidence: float
    bounding_boxes: List[BoundingBox]
    language: str

@dataclass
class ProcessingResult:
    success: bool
    data: Any
    error_message: Optional[str]
    processing_time: float
```

## 依赖关系说明

1. **CLI** 依赖 **MCP Server** 和 **Utils**
2. **MCP Server** 依赖 **Core Modules** 和 **Utils**
3. **Core Modules** 相互独立，但都依赖 **Utils**
4. **Utils** 是最底层，不依赖其他业务模块

## 异步设计

所有主要操作都使用 `async/await` 模式，支持并发处理多个任务。

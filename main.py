#!/usr/bin/env python3
"""网页内容抓取工具MCP Server"""
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent
)
from src.core.web_scraper import WebScraper
from src.utils.logger import Logger


class ScraperMCPServer:
    """网页内容抓取MCP Server"""
    
    def __init__(self):
        self.logger = Logger()
        self.web_scraper = WebScraper()
        self.tools = [
            Tool(
                name="open_webpage",
                description="使用系统Chrome浏览器打开指定网页",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要打开的网页URL"
                        },
                        "headless": {
                            "type": "boolean",
                            "description": "是否无头模式（不显示浏览器窗口）",
                            "default": False
                        }
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="get_page_info",
                description="获取网页基本信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "网页URL"
                        }
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="login_zhihu",
                description="登录知乎网站，保持登录状态",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "headless": {
                            "type": "boolean",
                            "description": "是否无头模式（不显示浏览器窗口）",
                            "default": False
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="read_zhihu_page",
                description="读取知乎网页内容（需要已登录）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要读取的知乎页面URL",
                            "default": "https://www.zhihu.com"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="search_zhihu",
                description="搜索知乎内容，获取符合要求的所有页面链接",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "max_pages": {
                            "type": "integer",
                            "description": "最大搜索页数",
                            "default": 3
                        },
                        "min_relevance": {
                            "type": "number",
                            "description": "最小相关性阈值（0-1之间）",
                            "default": 0.5
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="download_zhihu_content",
                description="下载知乎内容并保存为PDF和Markdown文件",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "知乎页面URL"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "保存目录路径"
                        },
                        "title": {
                            "type": "string",
                            "description": "自定义文件名(可选)"
                        }
                    },
                    "required": ["url", "output_dir"]
                }
            ),
            Tool(
                name="batch_download_zhihu",
                description="批量下载知乎搜索结果并保存",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "保存目录路径"
                        },
                        "max_pages": {
                            "type": "integer",
                            "description": "最大搜索页数",
                            "default": 3
                        },
                        "min_relevance": {
                            "type": "number",
                            "description": "最小相关性阈值（0-1之间）",
                            "default": 0.5
                        }
                    },
                    "required": ["query", "output_dir"]
                }
            )
        ]
    
    async def handle_list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """处理工具列表请求"""
        self.logger.info(f"收到工具列表请求: {request}")
        return ListToolsResult(tools=self.tools)
    
    async def handle_call_tool(self, request: CallToolRequest) -> CallToolResult:
        """处理工具调用请求"""
        self.logger.info(f"收到工具调用请求: {request}")
        
        try:
            # 从params中获取工具名称和参数
            tool_name = request.params.name
            arguments = request.params.arguments
            
            if tool_name == "open_webpage":
                url = arguments.get("url")
                headless = arguments.get("headless", False)
                
                if not url:
                    return CallToolResult(
                        content=[TextContent(type="text", text="错误：缺少URL参数")],
                        isError=True
                    )
                
                result = await self.web_scraper.open_webpage(url, headless)
                
                if result["status"] == "success":
                    return CallToolResult(
                        content=[TextContent(
                            type="text", 
                            text=f"✅ 成功打开网页: {url}\n浏览器类型: {result['browser_type']}\n无头模式: {result['headless']}"
                        )]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ 打开网页失败: {result['message']}")],
                        isError=True
                    )
            
            elif tool_name == "get_page_info":
                url = arguments.get("url")
                
                if not url:
                    return CallToolResult(
                        content=[TextContent(type="text", text="错误：缺少URL参数")],
                        isError=True
                    )
                
                result = await self.web_scraper.get_page_info(url)
                return CallToolResult(
                    content=[TextContent(
                        type="text", 
                        text=f"网页信息: {result['message']}"
                    )]
                )
            
            elif tool_name == "login_zhihu":
                headless = arguments.get("headless", False)
                
                result = await self.web_scraper.login_zhihu(headless)
                
                if result["status"] == "success":
                    return CallToolResult(
                        content=[TextContent(
                            type="text", 
                            text=f"✅ {result['message']}\n登录状态: {result['login_status']}\n用户数据目录: {result['user_data_dir']}"
                        )]
                    )
                elif result["status"] == "waiting":
                    return CallToolResult(
                        content=[TextContent(
                            type="text", 
                            text=f"⏳ {result['message']}\n请手动扫码登录\n用户数据目录: {result['user_data_dir']}"
                        )]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ {result['message']}")],
                        isError=True
                    )
            
            elif tool_name == "read_zhihu_page":
                url = arguments.get("url", "https://www.zhihu.com")
                
                result = await self.web_scraper.read_zhihu_page(url)
                
                if result["status"] == "success":
                    return CallToolResult(
                        content=[TextContent(
                            type="text", 
                            text=f"✅ {result['message']}\n页面标题: {result['title']}\n内容长度: {result['content_length']} 字符\n文本内容: {result['text_content']}"
                        )]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ {result['message']}")],
                        isError=True
                    )
            
            elif tool_name == "search_zhihu":
                query = arguments.get("query")
                max_pages = arguments.get("max_pages", 3)
                min_relevance = arguments.get("min_relevance", 0.5)
                
                if not query:
                    return CallToolResult(
                        content=[TextContent(type="text", text="错误：缺少搜索关键词参数")],
                        isError=True
                    )
                
                result = await self.web_scraper.search_zhihu(query, max_pages, min_relevance)
                
                if result["status"] == "success":
                    # 格式化输出结果
                    qualified_links = result.get("qualified_links", [])
                    results = result.get("results", [])
                    
                    # 构建输出文本
                    output_text = f"✅ {result['message']}\n"
                    output_text += f"搜索关键词: {result['query']}\n"
                    output_text += f"总结果数: {result['total_results']}\n"
                    output_text += f"符合要求的结果数: {result['filtered_results']}\n\n"
                    
                    if qualified_links:
                        output_text += "📋 符合要求的所有页面链接:\n"
                        for i, link in enumerate(qualified_links, 1):
                            output_text += f"{i}. {link}\n"
                        
                        output_text += "\n📊 详细结果信息:\n"
                        for i, item in enumerate(results[:10], 1):  # 只显示前10个结果
                            output_text += f"\n{i}. {item['title']}\n"
                            output_text += f"   作者: {item['author']}\n"
                            output_text += f"   点赞: {item['vote_count']}\n"
                            output_text += f"   相关性: {item['relevance_score']:.2f}\n"
                            output_text += f"   链接: {item['url']}\n"
                            if item['summary']:
                                output_text += f"   摘要: {item['summary'][:100]}...\n"
                    else:
                        output_text += "❌ 没有找到符合要求的结果"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=output_text)]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ {result['message']}")],
                        isError=True
                    )
            
            elif tool_name == "download_zhihu_content":
                url = arguments.get("url")
                output_dir = arguments.get("output_dir")
                title = arguments.get("title")
                
                if not url or not output_dir:
                    return CallToolResult(
                        content=[TextContent(type="text", text="错误：缺少URL或输出目录参数")],
                        isError=True
                    )
                
                from pathlib import Path
                output_path = Path(output_dir)
                
                result = await self.web_scraper.download_and_save_content(url, output_path, title)
                
                if result["status"] == "success":
                    return CallToolResult(
                        content=[TextContent(
                            type="text", 
                            text=f"✅ {result['message']}\n文件名: {result['base_name']}\n保存目录: {result['files']['markdown']}\nPDF: {result['files']['pdf']}\n原始标题: {result['original_title']}"
                        )]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ {result['message']}")],
                        isError=True
                    )
            
            elif tool_name == "batch_download_zhihu":
                query = arguments.get("query")
                output_dir = arguments.get("output_dir")
                max_pages = arguments.get("max_pages", 3)
                min_relevance = arguments.get("min_relevance", 0.5)
                
                if not query or not output_dir:
                    return CallToolResult(
                        content=[TextContent(type="text", text="错误：缺少搜索关键词或输出目录参数")],
                        isError=True
                    )
                
                from pathlib import Path
                output_path = Path(output_dir)
                
                result = await self.web_scraper.batch_download_content(query, output_path, max_pages, min_relevance)
                
                if result["status"] == "success":
                    return CallToolResult(
                        content=[TextContent(
                            type="text", 
                            text=f"✅ {result['message']}\n搜索关键词: {result['query']}\n总计发现: {result['total_found']} 篇\n成功下载: {result['success_count']} 篇\n失败: {result['failed_count']} 篇\n保存目录: {result['output_dir']}\n总结文件: {result['summary_file']}"
                        )]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ {result['message']}")],
                        isError=True
                    )
            
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"未知工具: {tool_name}")],
                    isError=True
                )
                
        except Exception as e:
            self.logger.error(f"工具调用失败: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"工具调用失败: {str(e)}")],
                isError=True
            )


async def main():
    """主函数"""
    logger = Logger()
    logger.info("启动网页内容抓取MCP Server...")
    
    try:
        # 创建MCP Server实例
        server = ScraperMCPServer()
        
        # 创建MCP Server
        mcp_server = Server("scraper-mcp")
        
        # 注册工具列表处理器
        mcp_server.list_tools()(server.handle_list_tools)
        
        # 注册工具调用处理器
        mcp_server.call_tool()(server.handle_call_tool)
        
        logger.info("MCP Server已启动，等待客户端连接...")
        logger.info("可用工具:")
        for tool in server.tools:
            logger.info(f"  - {tool.name}: {tool.description}")
        
        # MCP Server已准备就绪，等待客户端连接
        logger.info("MCP Server已准备就绪，等待客户端连接...")
        
        # 启动stdio server，持续运行
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )
            
    except KeyboardInterrupt:
        logger.info("MCP Server被用户中断")
    except Exception as e:
        logger.error(f"MCP Server运行失败: {e}")
        return False
    
    logger.info("MCP Server已停止")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

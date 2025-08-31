#!/usr/bin/env python3
"""MCP工具集成测试"""
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp.types import CallToolRequest
from src.core.web_scraper import WebScraper
from src.utils.logger import Logger


class TestMCPIntegration:
    """MCP集成测试类"""
    
    def __init__(self):
        self.logger = Logger()
        self.web_scraper = WebScraper()
    
    async def test_open_webpage_tool(self):
        """测试网页打开工具"""
        self.logger.info("测试网页打开工具...")
        
        # 测试1: 打开知乎网页
        self.logger.info("测试1: 打开知乎网页...")
        result1 = await self.web_scraper.open_webpage("https://www.zhihu.com", headless=False)
        self.logger.info(f"知乎网页结果: {result1}")
        
        # 等待用户确认
        input("知乎网页已打开，按回车键继续测试...")
        
        # 测试2: 打开百度网页
        self.logger.info("测试2: 打开百度网页...")
        result2 = await self.web_scraper.open_webpage("https://www.baidu.com", headless=False)
        self.logger.info(f"百度网页结果: {result2}")
        
        # 等待用户确认
        input("百度网页已打开，按回车键继续测试...")
        
        return result1["status"] == "success" and result2["status"] == "success"
    
    async def test_get_page_info_tool(self):
        """测试页面信息工具"""
        self.logger.info("测试页面信息工具...")
        
        result = await self.web_scraper.get_page_info("https://example.com")
        self.logger.info(f"页面信息结果: {result}")
        
        return result["status"] == "not_implemented"  # 这是预期的状态
    
    async def test_mcp_request_format(self):
        """测试MCP请求格式"""
        self.logger.info("测试MCP请求格式...")
        
        # 模拟MCP请求
        test_request = CallToolRequest(
            method="tools/call",
            params={
                "name": "open_webpage",
                "arguments": {"url": "https://example.com", "headless": True}
            }
        )
        
        self.logger.info(f"MCP请求格式: {test_request}")
        return True


async def run_integration_tests():
    """运行集成测试"""
    logger = Logger()
    logger.info("开始MCP集成测试...")
    
    tester = TestMCPIntegration()
    
    try:
        # 测试MCP请求格式
        format_ok = await tester.test_mcp_request_format()
        if not format_ok:
            logger.error("MCP请求格式测试失败")
            return False
        
        # 测试页面信息工具
        info_ok = await tester.test_get_page_info_tool()
        if not info_ok:
            logger.error("页面信息工具测试失败")
            return False
        
        # 测试网页打开工具
        open_ok = await tester.test_open_webpage_tool()
        if not open_ok:
            logger.error("网页打开工具测试失败")
            return False
        
        logger.info("✅ 所有MCP集成测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"集成测试失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)

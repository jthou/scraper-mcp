#!/usr/bin/env python3
"""网页内容抓取工具主程序"""
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp.server import MCPServer
from src.utils.logger import Logger


async def main():
    """主函数"""
    logger = Logger()
    logger.info("启动网页内容抓取工具...")
    
    try:
        # 创建MCP Server实例
        server = MCPServer()
        
        # 启动服务器
        start_result = await server.start()
        logger.info(f"服务器启动结果: {start_result}")
        
        # 测试所有模块
        test_result = await server.test_all_modules()
        logger.info(f"模块测试结果: {test_result}")
        
        # 停止服务器
        stop_result = await server.stop()
        logger.info(f"服务器停止结果: {stop_result}")
        
        logger.info("程序执行完成")
        return True
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return False


if __name__ == "__main__":
    # 运行主函数
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

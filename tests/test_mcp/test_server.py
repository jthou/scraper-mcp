"""MCP Server测试"""
import pytest
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp.server import MCPServer


class TestMCPServer:
    """MCP Server测试类"""
    
    def test_init(self):
        """测试初始化"""
        server = MCPServer()
        assert server.name == "MCPServer"
        assert not server.is_running
        assert len(server.modules) == 5  # 5个核心模块
    
    @pytest.mark.asyncio
    async def test_start(self):
        """测试启动方法"""
        server = MCPServer()
        result = await server.start()
        
        assert result["status"] == "success"
        assert server.is_running
        assert "已启动" in result["message"]
        assert "modules" in result
    
    @pytest.mark.asyncio
    async def test_stop(self):
        """测试停止方法"""
        server = MCPServer()
        server.is_running = True  # 先设置为运行状态
        
        result = await server.stop()
        
        assert result["status"] == "success"
        assert not server.is_running
        assert "已停止" in result["message"]
    
    @pytest.mark.asyncio
    async def test_all_modules(self):
        """测试所有模块"""
        server = MCPServer()
        result = await server.test_all_modules()
        
        assert result["status"] == "success"
        assert "所有模块测试完成" in result["message"]
        assert "results" in result
        assert len(result["results"]) == 5  # 5个模块的测试结果


if __name__ == "__main__":
    # 直接运行测试
    server = MCPServer()
    
    async def run_tests():
        print("测试初始化...")
        assert server.name == "MCPServer"
        assert len(server.modules) == 5
        print("✅ 初始化测试通过")
        
        print("测试启动方法...")
        result = await server.start()
        assert result["status"] == "success"
        print("✅ 启动测试通过")
        
        print("测试所有模块...")
        result = await server.test_all_modules()
        assert result["status"] == "success"
        print("✅ 模块测试通过")
        
        print("测试停止方法...")
        result = await server.stop()
        assert result["status"] == "success"
        print("✅ 停止测试通过")
        
        print("所有测试通过！")
    
    asyncio.run(run_tests())

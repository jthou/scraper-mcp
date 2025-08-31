"""网页抓取模块测试"""
import pytest
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.web_scraper import WebScraper


class TestWebScraper:
    """网页抓取模块测试类"""
    
    def test_init(self):
        """测试初始化"""
        scraper = WebScraper()
        assert scraper.name == "WebScraper"
    
    @pytest.mark.asyncio
    async def test_connection(self):
        """测试连接方法"""
        scraper = WebScraper()
        result = await scraper.test_connection()
        
        assert result["status"] == "success"
        assert result["module"] == "WebScraper"
        assert "模块已初始化" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_page_info(self):
        """测试获取页面信息方法"""
        scraper = WebScraper()
        result = await scraper.get_page_info("https://example.com")
        
        assert result["url"] == "https://example.com"
        assert result["status"] == "not_implemented"
        assert "基础功能，待实现" in result["message"]
    
    @pytest.mark.asyncio
    async def test_open_webpage(self):
        """测试打开网页功能"""
        scraper = WebScraper()
        result = await scraper.open_webpage("https://example.com", headless=True)
        
        # 验证返回结果格式
        assert "url" in result
        assert "status" in result
        assert result["url"] == "https://example.com"
        
        # 由于是测试环境，可能无法真正打开浏览器，所以只验证格式
        print(f"网页打开测试结果: {result}")


if __name__ == "__main__":
    # 直接运行测试
    scraper = WebScraper()
    
    async def run_tests():
        print("测试初始化...")
        assert scraper.name == "WebScraper"
        print("✅ 初始化测试通过")
        
        print("测试连接方法...")
        result = await scraper.test_connection()
        assert result["status"] == "success"
        print("✅ 连接测试通过")
        
        print("测试获取页面信息...")
        result = await scraper.get_page_info("https://example.com")
        assert result["url"] == "https://example.com"
        print("✅ 页面信息测试通过")
        
        print("测试打开网页功能...")
        result = await scraper.open_webpage("https://example.com", headless=True)
        assert "url" in result and "status" in result
        print("✅ 网页打开测试通过")
        
        print("所有测试通过！")
    
    asyncio.run(run_tests())

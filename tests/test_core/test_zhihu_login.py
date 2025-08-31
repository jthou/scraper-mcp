"""知乎登录功能测试"""
import pytest
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.web_scraper import WebScraper


class TestZhihuLogin:
    """知乎登录功能测试类"""
    
    def test_init(self):
        """测试初始化"""
        scraper = WebScraper()
        assert scraper.name == "WebScraper"
    
    @pytest.mark.asyncio
    async def test_zhihu_login_status_detection(self):
        """测试知乎登录状态检测"""
        scraper = WebScraper()
        
        # 测试登录状态检测方法（模拟）
        # 由于需要真实浏览器，这里只测试方法存在性
        assert hasattr(scraper, '_detect_zhihu_login_status')
        assert hasattr(scraper, '_is_zhihu_logged_in')
        assert hasattr(scraper, '_is_on_zhihu_login_page')
        assert hasattr(scraper, '_has_zhihu_qr_login')
    
    @pytest.mark.asyncio
    async def test_zhihu_login_method(self):
        """测试知乎登录方法"""
        scraper = WebScraper()
        
        # 测试登录方法存在性
        assert hasattr(scraper, 'login_zhihu')
        assert hasattr(scraper, 'read_zhihu_page')
    
    @pytest.mark.asyncio
    async def test_zhihu_page_reading(self):
        """测试知乎页面读取方法"""
        scraper = WebScraper()
        
        # 测试页面读取方法存在性
        assert hasattr(scraper, 'read_zhihu_page')


if __name__ == "__main__":
    # 直接运行测试
    scraper = WebScraper()
    
    async def run_tests():
        print("测试初始化...")
        assert scraper.name == "WebScraper"
        print("✅ 初始化测试通过")
        
        print("测试知乎登录状态检测方法...")
        assert hasattr(scraper, '_detect_zhihu_login_status')
        assert hasattr(scraper, '_is_zhihu_logged_in')
        print("✅ 登录状态检测方法测试通过")
        
        print("测试知乎登录方法...")
        assert hasattr(scraper, 'login_zhihu')
        print("✅ 登录方法测试通过")
        
        print("测试知乎页面读取方法...")
        assert hasattr(scraper, 'read_zhihu_page')
        print("✅ 页面读取方法测试通过")
        
        print("所有测试通过！")
    
    asyncio.run(run_tests())

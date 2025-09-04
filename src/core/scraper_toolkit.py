#!/usr/bin/env python3
"""
网页内容抓取工具包

一个独立的工具库，提供网页内容抓取、下载、转换等功能
支持知乎、微信等平台的内容抓取
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.web_scraper import WebScraper
from src.core.wechat_scraper import WeChatScraper
from src.utils.logger import Logger


class Platform(Enum):
    """支持的平台"""
    ZHIHU = "zhihu"
    WECHAT = "wechat"
    GENERAL = "general"


@dataclass
class ScrapingConfig:
    """抓取配置"""
    platform: Platform
    headless: bool = False
    persistent: bool = False
    max_pages: int = 3
    output_dir: Path = Path("data")
    timeout: int = 300
    wait_for_verification: bool = True


class ScraperToolkit:
    """网页内容抓取工具包"""
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        self.logger = Logger("ScraperToolkit")
        self.config = config or ScrapingConfig(platform=Platform.GENERAL)
        self.web_scraper = WebScraper()
        self.wechat_scraper = WeChatScraper()
        self._browser_initialized = False
    
    async def setup_browser(self, platform: Platform, headless: bool = None, persistent: bool = None) -> Dict[str, Any]:
        """设置浏览器环境"""
        headless = headless if headless is not None else self.config.headless
        persistent = persistent if persistent is not None else self.config.persistent
        
        if platform == Platform.ZHIHU:
            result = await self.web_scraper.setup_browser(headless, persistent)
        elif platform == Platform.WECHAT:
            result = await self.wechat_scraper.setup_browser(headless, persistent)
        else:
            result = await self.web_scraper.setup_browser(headless, persistent)
        
        if result["status"] == "success":
            self._browser_initialized = True
        
        return result
    
    async def login(self, platform: Platform, username: str, password: str) -> Dict[str, Any]:
        """登录平台"""
        if not self._browser_initialized:
            await self.setup_browser(platform)
        
        if platform == Platform.ZHIHU:
            return await self.web_scraper.login_zhihu(username, password)
        else:
            return {
                "status": "error",
                "message": f"平台 {platform.value} 不支持登录功能"
            }
    
    async def search(self, platform: Platform, query: str, max_pages: int = None) -> Dict[str, Any]:
        """搜索内容"""
        if not self._browser_initialized:
            await self.setup_browser(platform)
        
        # 支持 0 表示抓取全部页面（直到没有“下一页”）
        if max_pages == 0:
            max_pages = None
        else:
            max_pages = max_pages or self.config.max_pages
        
        if platform == Platform.ZHIHU:
            return await self.web_scraper.search_zhihu(query, max_pages)
        elif platform == Platform.WECHAT:
            return await self.wechat_scraper.search_wechat(query, max_pages)
        else:
            return {
                "status": "error",
                "message": f"平台 {platform.value} 不支持搜索功能"
            }
    
    async def read_page(self, platform: Platform, url: str) -> Dict[str, Any]:
        """读取页面内容"""
        if not self._browser_initialized:
            await self.setup_browser(platform)
        
        if platform == Platform.ZHIHU:
            return await self.web_scraper.read_zhihu_page(url)
        elif platform == Platform.WECHAT:
            return await self.wechat_scraper.read_wechat_page(url)
        else:
            return {
                "status": "error",
                "message": f"平台 {platform.value} 不支持页面读取功能"
            }
    
    async def download_content(self, platform: Platform, url: str, output_dir: Path = None, title: str = None) -> Dict[str, Any]:
        """下载内容并保存为PDF和Markdown"""
        if not self._browser_initialized:
            await self.setup_browser(platform)
        
        output_dir = output_dir or self.config.output_dir
        
        if platform == Platform.ZHIHU:
            return await self.web_scraper.download_and_save_content(url, output_dir, title)
        elif platform == Platform.WECHAT:
            return await self.wechat_scraper.download_and_save_content(url, output_dir, title)
        else:
            return {
                "status": "error",
                "message": f"平台 {platform.value} 不支持内容下载功能"
            }
    
    async def batch_download(self, platform: Platform, query: str, output_dir: Path = None, max_pages: int = None) -> Dict[str, Any]:
        """批量下载搜索结果"""
        if not self._browser_initialized:
            await self.setup_browser(platform)
        
        output_dir = output_dir or self.config.output_dir
        # 支持 0 表示抓取全部页面
        if max_pages == 0:
            max_pages = None
        else:
            max_pages = max_pages or self.config.max_pages
        
        if platform == Platform.ZHIHU:
            return await self.web_scraper.batch_download_content(query, output_dir, max_pages)
        elif platform == Platform.WECHAT:
            return await self.wechat_scraper.batch_download_content(query, output_dir, max_pages)
        else:
            return {
                "status": "error",
                "message": f"平台 {platform.value} 不支持批量下载功能"
            }
    
    async def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self.web_scraper, 'cleanup'):
                await self.web_scraper.cleanup()
            if hasattr(self.wechat_scraper, 'cleanup'):
                await self.wechat_scraper.cleanup()
            self.logger.info("资源清理完成")
        except Exception as e:
            self.logger.error(f"资源清理失败: {e}")
    
    def get_supported_platforms(self) -> List[str]:
        """获取支持的平台列表"""
        return [platform.value for platform in Platform]
    
    def get_platform_info(self, platform: Platform) -> Dict[str, Any]:
        """获取平台信息"""
        info = {
            Platform.ZHIHU: {
                "name": "知乎",
                "description": "知乎问答平台内容抓取",
                "features": ["搜索", "登录", "页面读取", "内容下载"],
                "requires_verification": False
            },
            Platform.WECHAT: {
                "name": "微信",
                "description": "微信公众号内容抓取（通过搜狗搜索）",
                "features": ["搜索", "页面读取", "内容下载"],
                "requires_verification": True
            },
            Platform.GENERAL: {
                "name": "通用",
                "description": "通用网页内容抓取",
                "features": ["页面读取", "内容下载"],
                "requires_verification": False
            }
        }
        return info.get(platform, {})


# 便捷函数
async def quick_search(platform: str, query: str, max_pages: int = 3, headless: bool = False) -> Dict[str, Any]:
    """快速搜索功能"""
    platform_enum = Platform(platform)
    config = ScrapingConfig(platform=platform_enum, headless=headless, max_pages=max_pages)
    toolkit = ScraperToolkit(config)
    
    try:
        result = await toolkit.search(platform_enum, query, max_pages)
        return result
    finally:
        await toolkit.cleanup()


async def quick_download(platform: str, url: str, output_dir: str = "data", headless: bool = False) -> Dict[str, Any]:
    """快速下载功能"""
    platform_enum = Platform(platform)
    config = ScrapingConfig(platform=platform_enum, headless=headless, output_dir=Path(output_dir))
    toolkit = ScraperToolkit(config)
    
    try:
        result = await toolkit.download_content(platform_enum, url, Path(output_dir))
        return result
    finally:
        await toolkit.cleanup()


async def quick_batch_download(platform: str, query: str, output_dir: str = "data", max_pages: int = 3, headless: bool = False) -> Dict[str, Any]:
    """快速批量下载功能"""
    platform_enum = Platform(platform)
    config = ScrapingConfig(platform=platform_enum, headless=headless, max_pages=max_pages, output_dir=Path(output_dir))
    toolkit = ScraperToolkit(config)
    
    try:
        result = await toolkit.batch_download(platform_enum, query, Path(output_dir), max_pages)
        return result
    finally:
        await toolkit.cleanup()


if __name__ == "__main__":
    # 示例用法
    async def main():
        # 创建工具包实例
        config = ScrapingConfig(
            platform=Platform.ZHIHU,
            headless=False,
            max_pages=2,
            output_dir=Path("data")
        )
        toolkit = ScraperToolkit(config)
        
        try:
            # 搜索知乎内容
            print("搜索知乎内容...")
            result = await toolkit.search(Platform.ZHIHU, "Python编程", 2)
            print(f"搜索结果: {result}")
            
            # 如果有结果，下载第一个
            if result.get("status") == "success" and result.get("results"):
                first_result = result["results"][0]
                print(f"下载第一个结果: {first_result['title']}")
                download_result = await toolkit.download_content(
                    Platform.ZHIHU, 
                    first_result["url"], 
                    Path("data"),
                    first_result["title"]
                )
                print(f"下载结果: {download_result}")
        
        finally:
            await toolkit.cleanup()
    
    asyncio.run(main())

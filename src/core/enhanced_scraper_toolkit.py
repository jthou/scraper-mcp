#!/usr/bin/env python3
"""
增强版网页内容抓取工具包

集成持久化浏览器管理，支持：
- 自动状态保存和恢复
- Cookie和会话持久化
- 跨平台状态共享
- 智能登录状态检测

作者: AI Assistant
日期: 2025年9月20日
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
from src.core.persistent_browser import PersistentBrowserManager, get_persistent_browser_manager
from src.utils.logger import Logger


class Platform(Enum):
    """支持的平台"""
    ZHIHU = "zhihu"
    WECHAT = "wechat"
    GENERAL = "general"
    NATURE = "nature"
    ARXIV = "arxiv"


@dataclass
class EnhancedScrapingConfig:
    """增强版抓取配置"""
    platform: Platform
    headless: bool = False
    persistent: bool = True  # 默认启用持久化
    max_pages: int = 3
    output_dir: Path = Path("data")
    timeout: int = 300
    wait_for_verification: bool = True
    auto_save_state: bool = True  # 自动保存状态
    state_save_interval: int = 30  # 状态保存间隔（秒）


class EnhancedScraperToolkit:
    """增强版网页内容抓取工具包"""
    
    def __init__(self, config: Optional[EnhancedScrapingConfig] = None):
        self.logger = Logger("EnhancedScraperToolkit")
        self.config = config or EnhancedScrapingConfig(platform=Platform.GENERAL)
        
        # 初始化组件
        self.web_scraper = WebScraper()
        self.wechat_scraper = WeChatScraper()
        self.browser_manager = get_persistent_browser_manager()
        
        # 状态管理
        self._browser_initialized = False
        self._current_platform = None
        self._state_save_task = None
    
    async def setup_persistent_browser(self, platform: Platform, site: str = None, 
                                     headless: bool = None) -> Dict[str, Any]:
        """设置持久化浏览器环境"""
        headless = headless if headless is not None else self.config.headless
        
        # 创建持久化浏览器
        result = await self.browser_manager.create_persistent_browser(
            platform.value, site, headless
        )
        
        if result["status"] == "success":
            self._browser_initialized = True
            self._current_platform = platform
            
            # 启动自动状态保存
            if self.config.auto_save_state:
                await self._start_auto_save_state(platform, site)
        
        return result
    
    async def _start_auto_save_state(self, platform: Platform, site: str = None):
        """启动自动状态保存"""
        if self._state_save_task:
            self._state_save_task.cancel()
        
        async def auto_save_loop():
            while True:
                try:
                    await asyncio.sleep(self.config.state_save_interval)
                    await self.browser_manager.save_browser_state(platform.value, site)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"自动保存状态失败: {e}")
        
        self._state_save_task = asyncio.create_task(auto_save_loop())
    
    async def get_page(self, platform: Platform = None, site: str = None) -> Optional[Any]:
        """获取页面实例"""
        platform = platform or self._current_platform
        if not platform:
            return None
        
        return await self.browser_manager.get_page(platform.value, site)
    
    async def get_context(self, platform: Platform = None, site: str = None) -> Optional[Any]:
        """获取上下文实例"""
        platform = platform or self._current_platform
        if not platform:
            return None
        
        return await self.browser_manager.get_context(platform.value, site)
    
    async def navigate_to(self, url: str, platform: Platform = None, site: str = None) -> Dict[str, Any]:
        """导航到指定URL"""
        try:
            page = await self.get_page(platform, site)
            if not page:
                return {
                    "status": "error",
                    "message": "页面实例不存在，请先设置浏览器"
                }
            
            await page.goto(url, wait_until="networkidle", timeout=self.config.timeout * 1000)
            
            return {
                "status": "success",
                "message": f"成功导航到: {url}",
                "url": url
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"导航失败: {str(e)}",
                "url": url,
                "error": str(e)
            }
    
    async def check_login_status(self, platform: Platform, site: str = None) -> Dict[str, Any]:
        """检查登录状态"""
        try:
            page = await self.get_page(platform, site)
            if not page:
                return {
                    "status": "error",
                    "message": "页面实例不存在"
                }
            
            # 根据平台检查登录状态
            if platform == Platform.ZHIHU:
                # 检查知乎登录状态
                try:
                    # 检查是否有用户头像或登录相关元素
                    user_avatar = await page.query_selector('[data-za-detail-view-id="1001"]')
                    if user_avatar:
                        return {
                            "status": "success",
                            "logged_in": True,
                            "message": "已登录知乎"
                        }
                    else:
                        return {
                            "status": "success",
                            "logged_in": False,
                            "message": "未登录知乎"
                        }
                except:
                    return {
                        "status": "success",
                        "logged_in": False,
                        "message": "无法检测登录状态"
                    }
            
            elif platform == Platform.WECHAT:
                # 检查微信登录状态
                try:
                    # 检查是否有验证码或登录相关元素
                    verification = await page.query_selector('.verify-code')
                    if verification:
                        return {
                            "status": "success",
                            "logged_in": False,
                            "message": "需要验证码验证"
                        }
                    else:
                        return {
                            "status": "success",
                            "logged_in": True,
                            "message": "微信搜索可用"
                        }
                except:
                    return {
                        "status": "success",
                        "logged_in": True,
                        "message": "微信搜索可用"
                    }
            
            else:
                return {
                    "status": "success",
                    "logged_in": True,
                    "message": "通用平台，无需登录检查"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查登录状态失败: {str(e)}",
                "error": str(e)
            }
    
    async def search(self, platform: Platform, query: str, max_pages: int = None, 
                    site: str = None) -> Dict[str, Any]:
        """搜索内容（增强版）"""
        try:
            # 确保浏览器已初始化
            if not self._browser_initialized:
                await self.setup_persistent_browser(platform, site)
            
            # 检查登录状态
            login_status = await self.check_login_status(platform, site)
            if login_status["status"] == "error":
                return login_status
            
            # 根据平台执行搜索
            if platform == Platform.ZHIHU:
                return await self._search_zhihu(query, max_pages, site)
            elif platform == Platform.WECHAT:
                return await self._search_wechat(query, max_pages, site)
            else:
                return await self._search_general(query, max_pages, site)
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索失败: {str(e)}",
                "error": str(e)
            }
    
    async def _search_zhihu(self, query: str, max_pages: int, site: str = None) -> Dict[str, Any]:
        """知乎搜索"""
        try:
            page = await self.get_page(Platform.ZHIHU, site)
            if not page:
                return {"status": "error", "message": "页面实例不存在"}
            
            # 导航到知乎搜索页面
            search_url = f"https://www.zhihu.com/search?q={query}&type=content"
            await page.goto(search_url, wait_until="networkidle")
            
            # 等待搜索结果加载
            await page.wait_for_timeout(3000)
            
            # 提取搜索结果
            results = []
            for i in range(max_pages or 3):
                # 提取当前页面的结果
                items = await page.query_selector_all('.Card')
                for item in items:
                    try:
                        title_elem = await item.query_selector('h2 a')
                        if title_elem:
                            title = await title_elem.inner_text()
                            link = await title_elem.get_attribute('href')
                            if link and not link.startswith('http'):
                                link = f"https://www.zhihu.com{link}"
                            
                            results.append({
                                "title": title.strip(),
                                "url": link,
                                "platform": "zhihu"
                            })
                    except:
                        continue
                
                # 尝试翻页
                try:
                    next_button = await page.query_selector('.Pagination button:last-child')
                    if next_button and await next_button.is_enabled():
                        await next_button.click()
                        await page.wait_for_timeout(3000)
                    else:
                        break
                except:
                    break
            
            return {
                "status": "success",
                "results": results,
                "total": len(results),
                "platform": "zhihu"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"知乎搜索失败: {str(e)}",
                "error": str(e)
            }
    
    async def _search_wechat(self, query: str, max_pages: int, site: str = None) -> Dict[str, Any]:
        """微信搜索"""
        try:
            page = await self.get_page(Platform.WECHAT, site)
            if not page:
                return {"status": "error", "message": "页面实例不存在"}
            
            # 导航到搜狗微信搜索
            search_url = f"https://weixin.sogou.com/weixin?type=2&query={query}"
            await page.goto(search_url, wait_until="networkidle")
            
            # 等待搜索结果加载
            await page.wait_for_timeout(3000)
            
            # 提取搜索结果
            results = []
            for i in range(max_pages or 3):
                # 提取当前页面的结果
                items = await page.query_selector_all('.txt-box')
                for item in items:
                    try:
                        title_elem = await item.query_selector('h3 a')
                        if title_elem:
                            title = await title_elem.inner_text()
                            link = await title_elem.get_attribute('href')
                            
                            results.append({
                                "title": title.strip(),
                                "url": link,
                                "platform": "wechat"
                            })
                    except:
                        continue
                
                # 尝试翻页
                try:
                    next_button = await page.query_selector('#sogou_next')
                    if next_button and await next_button.is_enabled():
                        await next_button.click()
                        await page.wait_for_timeout(3000)
                    else:
                        break
                except:
                    break
            
            return {
                "status": "success",
                "results": results,
                "total": len(results),
                "platform": "wechat"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"微信搜索失败: {str(e)}",
                "error": str(e)
            }
    
    async def _search_general(self, query: str, max_pages: int, site: str = None) -> Dict[str, Any]:
        """通用搜索"""
        return {
            "status": "success",
            "results": [],
            "total": 0,
            "platform": "general",
            "message": "通用搜索功能待实现"
        }
    
    async def download_content(self, platform: Platform, url: str, output_dir: Path, 
                             title: str = None, site: str = None) -> Dict[str, Any]:
        """下载内容（增强版）"""
        try:
            page = await self.get_page(platform, site)
            if not page:
                return {"status": "error", "message": "页面实例不存在"}
            
            # 导航到目标URL
            await page.goto(url, wait_until="networkidle")
            
            # 获取页面标题
            if not title:
                title = await page.title()
            
            # 生成文件名
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_title = title.replace('/', '_').replace('\\', '_')[:50]
            
            # 创建输出目录
            pdf_dir = output_dir / "pdfs"
            markdown_dir = output_dir / "markdown"
            pdf_dir.mkdir(parents=True, exist_ok=True)
            markdown_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成PDF
            pdf_filename = f"{clean_title}_{timestamp}.pdf"
            pdf_path = pdf_dir / pdf_filename
            
            await page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={'top': '20px', 'bottom': '20px', 'left': '20px', 'right': '20px'}
            )
            
            # 提取内容并保存Markdown
            content = await page.inner_text("body")
            markdown_filename = f"{clean_title}_{timestamp}.md"
            markdown_path = markdown_dir / markdown_filename
            
            markdown_content = f"""# {title}

**来源**: [{platform.value}]({url})
**保存时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**文件类型**: {platform.value}内容

---

{content}
"""
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return {
                "status": "success",
                "title": title,
                "pdf_path": str(pdf_path),
                "markdown_path": str(markdown_path),
                "url": url
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"下载内容失败: {str(e)}",
                "error": str(e)
            }
    
    async def list_saved_states(self) -> List[Dict[str, Any]]:
        """列出所有保存的状态"""
        return await self.browser_manager.list_saved_states()
    
    async def clear_platform_state(self, platform: Platform, site: str = None):
        """清除指定平台的状态"""
        await self.browser_manager.clear_browser_state(platform.value, site)
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 停止自动保存任务
            if self._state_save_task:
                self._state_save_task.cancel()
            
            # 保存当前状态
            if self._current_platform:
                await self.browser_manager.save_browser_state(
                    self._current_platform.value
                )
            
            # 清理浏览器管理器
            await self.browser_manager.cleanup()
            
            print("✅ 增强版工具包资源已清理")
            
        except Exception as e:
            print(f"⚠️ 清理资源失败: {e}")


# 便捷函数
async def quick_setup(platform: Platform, headless: bool = False, 
                     persistent: bool = True) -> EnhancedScraperToolkit:
    """快速设置增强版工具包"""
    config = EnhancedScrapingConfig(
        platform=platform,
        headless=headless,
        persistent=persistent
    )
    
    toolkit = EnhancedScraperToolkit(config)
    await toolkit.setup_persistent_browser(platform)
    
    return toolkit

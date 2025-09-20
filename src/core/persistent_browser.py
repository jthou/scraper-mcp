#!/usr/bin/env python3
"""
持久化浏览器管理模块

提供统一的浏览器状态管理，支持：
- Cookie和会话持久化
- 登录状态保持
- 用户数据目录管理
- 跨平台状态共享

作者: AI Assistant
日期: 2025年9月20日
"""

import asyncio
import json
import pickle
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import hashlib
import os


class PersistentBrowserManager:
    """持久化浏览器管理器"""
    
    def __init__(self, base_data_dir: Path = None):
        self.base_data_dir = base_data_dir or Path(__file__).parent.parent.parent / "data" / "browser_data"
        self.base_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 浏览器实例管理
        self.playwright = None
        self.browsers: Dict[str, Browser] = {}
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        
        # 状态管理
        self.cookies: Dict[str, List[Dict]] = {}
        self.local_storage: Dict[str, Dict[str, str]] = {}
        self.session_storage: Dict[str, Dict[str, str]] = {}
        
        # 配置
        self.stealth_args = [
            "--start-maximized",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-sync",
            "--disable-default-apps",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-background-timer-throttling",
            "--disable-background-networking",
            "--disable-breakpad",
            "--disable-component-extensions-with-background-pages",
            "--disable-domain-reliability",
            "--disable-features=TranslateUI",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-sync-preferences",
            "--disable-web-resources",
            "--enable-features=NetworkService,NetworkServiceLogging",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--safebrowsing-disable-auto-update",
            "--enable-automation",
            "--password-store=basic",
            "--use-mock-keychain"
        ]
    
    def _get_platform_hash(self, platform: str, site: str = None) -> str:
        """生成平台唯一标识"""
        identifier = f"{platform}_{site}" if site else platform
        return hashlib.md5(identifier.encode()).hexdigest()[:8]
    
    def _get_user_data_dir(self, platform: str, site: str = None) -> Path:
        """获取用户数据目录"""
        platform_hash = self._get_platform_hash(platform, site)
        return self.base_data_dir / f"{platform}_{platform_hash}"
    
    def _get_state_file(self, platform: str, site: str = None) -> Path:
        """获取状态文件路径"""
        platform_hash = self._get_platform_hash(platform, site)
        return self.base_data_dir / f"{platform}_{platform_hash}_state.json"
    
    async def initialize_playwright(self):
        """初始化Playwright"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
    
    async def create_persistent_browser(self, platform: str, site: str = None, 
                                      headless: bool = False) -> Dict[str, Any]:
        """创建持久化浏览器实例"""
        try:
            await self.initialize_playwright()
            
            # 获取用户数据目录
            user_data_dir = self._get_user_data_dir(platform, site)
            user_data_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建持久化上下文
            context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                channel="chrome",
                headless=headless,
                timeout=60000,
                args=self.stealth_args
            )
            
            # 生成唯一标识
            context_id = f"{platform}_{site}" if site else platform
            
            # 保存上下文
            self.contexts[context_id] = context
            
            # 创建或获取页面
            if context.pages:
                page = context.pages[0]
            else:
                page = await context.new_page()
            
            self.pages[context_id] = page
            
            # 设置用户代理和HTTP头
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            })
            
            # 加载保存的状态
            await self._load_browser_state(context_id, platform, site)
            
            return {
                "status": "success",
                "message": f"持久化浏览器创建成功: {platform}",
                "context_id": context_id,
                "user_data_dir": str(user_data_dir),
                "persistent": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"创建持久化浏览器失败: {str(e)}",
                "error": str(e)
            }
    
    async def get_page(self, platform: str, site: str = None) -> Optional[Page]:
        """获取页面实例"""
        context_id = f"{platform}_{site}" if site else platform
        return self.pages.get(context_id)
    
    async def get_context(self, platform: str, site: str = None) -> Optional[BrowserContext]:
        """获取上下文实例"""
        context_id = f"{platform}_{site}" if site else platform
        return self.contexts.get(context_id)
    
    async def save_browser_state(self, platform: str, site: str = None):
        """保存浏览器状态"""
        try:
            context_id = f"{platform}_{site}" if site else platform
            page = self.pages.get(context_id)
            context = self.contexts.get(context_id)
            
            if not page or not context:
                return
            
            # 保存Cookies
            cookies = await context.cookies()
            self.cookies[context_id] = cookies
            
            # 保存Local Storage
            try:
                local_storage = await page.evaluate("() => { return {...localStorage}; }")
                self.local_storage[context_id] = local_storage
            except:
                pass
            
            # 保存Session Storage
            try:
                session_storage = await page.evaluate("() => { return {...sessionStorage}; }")
                self.session_storage[context_id] = session_storage
            except:
                pass
            
            # 保存到文件
            state_file = self._get_state_file(platform, site)
            state_data = {
                "cookies": self.cookies.get(context_id, []),
                "local_storage": self.local_storage.get(context_id, {}),
                "session_storage": self.session_storage.get(context_id, {}),
                "saved_at": datetime.now().isoformat(),
                "platform": platform,
                "site": site
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 浏览器状态已保存: {state_file}")
            
        except Exception as e:
            print(f"⚠️ 保存浏览器状态失败: {e}")
    
    async def _load_browser_state(self, context_id: str, platform: str, site: str = None):
        """加载浏览器状态"""
        try:
            state_file = self._get_state_file(platform, site)
            
            if not state_file.exists():
                return
            
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            context = self.contexts.get(context_id)
            page = self.pages.get(context_id)
            
            if not context or not page:
                return
            
            # 恢复Cookies
            cookies = state_data.get("cookies", [])
            if cookies:
                await context.add_cookies(cookies)
                print(f"✅ 已恢复 {len(cookies)} 个Cookies")
            
            # 恢复Local Storage
            local_storage = state_data.get("local_storage", {})
            if local_storage:
                for key, value in local_storage.items():
                    await page.evaluate(f"localStorage.setItem('{key}', '{value}');")
                print(f"✅ 已恢复 {len(local_storage)} 个Local Storage项")
            
            # 恢复Session Storage
            session_storage = state_data.get("session_storage", {})
            if session_storage:
                for key, value in session_storage.items():
                    await page.evaluate(f"sessionStorage.setItem('{key}', '{value}');")
                print(f"✅ 已恢复 {len(session_storage)} 个Session Storage项")
            
            print(f"✅ 浏览器状态已加载: {platform}")
            
        except Exception as e:
            print(f"⚠️ 加载浏览器状态失败: {e}")
    
    async def clear_browser_state(self, platform: str, site: str = None):
        """清除浏览器状态"""
        try:
            context_id = f"{platform}_{site}" if site else platform
            
            # 清除内存中的状态
            self.cookies.pop(context_id, None)
            self.local_storage.pop(context_id, None)
            self.session_storage.pop(context_id, None)
            
            # 清除文件状态
            state_file = self._get_state_file(platform, site)
            if state_file.exists():
                state_file.unlink()
            
            # 清除用户数据目录
            user_data_dir = self._get_user_data_dir(platform, site)
            if user_data_dir.exists():
                shutil.rmtree(user_data_dir)
            
            print(f"✅ 浏览器状态已清除: {platform}")
            
        except Exception as e:
            print(f"⚠️ 清除浏览器状态失败: {e}")
    
    async def list_saved_states(self) -> List[Dict[str, Any]]:
        """列出所有保存的状态"""
        states = []
        
        for state_file in self.base_data_dir.glob("*_state.json"):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                states.append({
                    "platform": state_data.get("platform"),
                    "site": state_data.get("site"),
                    "saved_at": state_data.get("saved_at"),
                    "cookies_count": len(state_data.get("cookies", [])),
                    "local_storage_count": len(state_data.get("local_storage", {})),
                    "session_storage_count": len(state_data.get("session_storage", {})),
                    "file_path": str(state_file)
                })
            except:
                continue
        
        return states
    
    async def cleanup(self):
        """清理所有资源"""
        try:
            # 保存所有状态
            for context_id in self.contexts.keys():
                platform = context_id.split('_')[0]
                site = '_'.join(context_id.split('_')[1:]) if '_' in context_id else None
                await self.save_browser_state(platform, site)
            
            # 关闭所有上下文
            for context in self.contexts.values():
                await context.close()
            
            # 关闭所有浏览器
            for browser in self.browsers.values():
                await browser.close()
            
            # 停止Playwright
            if self.playwright:
                await self.playwright.stop()
            
            print("✅ 浏览器资源已清理")
            
        except Exception as e:
            print(f"⚠️ 清理浏览器资源失败: {e}")


# 全局实例
_persistent_browser_manager = None

def get_persistent_browser_manager() -> PersistentBrowserManager:
    """获取全局持久化浏览器管理器实例"""
    global _persistent_browser_manager
    if _persistent_browser_manager is None:
        _persistent_browser_manager = PersistentBrowserManager()
    return _persistent_browser_manager

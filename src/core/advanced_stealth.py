#!/usr/bin/env python3
"""
高级反爬虫策略模块

提供更高级的反检测技术来绕过搜狗等网站的反爬虫机制
"""

import asyncio
import random
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from playwright.async_api import BrowserContext, Page


class AdvancedStealth:
    """高级隐身技术类"""
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        ]
        
        self.screen_resolutions = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864},
            {"width": 1280, "height": 720}
        ]
        
        self.languages = [
            "zh-CN,zh;q=0.9,en;q=0.8",
            "zh-CN,zh;q=0.8,en;q=0.7",
            "zh-CN,zh;q=0.9",
            "en-US,en;q=0.9,zh;q=0.8"
        ]
    
    def get_random_user_agent(self) -> str:
        """获取随机用户代理"""
        return random.choice(self.user_agents)
    
    def get_random_screen_resolution(self) -> Dict[str, int]:
        """获取随机屏幕分辨率"""
        return random.choice(self.screen_resolutions)
    
    def get_random_language(self) -> str:
        """获取随机语言设置"""
        return random.choice(self.languages)
    
    def get_stealth_args(self) -> List[str]:
        """获取隐身浏览器参数"""
        return [
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-sync",
            "--disable-extensions",
            "--disable-default-apps",
            "--disable-background-timer-throttling",
            "--disable-background-networking",
            "--disable-breakpad",
            "--disable-component-extensions-with-background-pages",
            "--disable-domain-reliability",
            "--disable-features=TranslateUI,VizDisplayCompositor",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-sync-preferences",
            "--disable-web-resources",
            "--enable-features=NetworkService,NetworkServiceLogging",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--safebrowsing-disable-auto-update",
            "--password-store=basic",
            "--use-mock-keychain",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-hang-monitor",
            "--disable-sync",
            "--disable-translate",
            "--disable-ipc-flooding-protection",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-component-extensions-with-background-pages",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-features=TranslateUI,BlinkGenPropertyTrees",
            "--disable-ipc-flooding-protection",
            "--enable-features=NetworkService,NetworkServiceLogging",
            "--force-color-profile=srgb",
            "--hide-scrollbars",
            "--mute-audio",
            "--no-default-browser-check",
            "--no-first-run",
            "--no-pings",
            "--no-zygote",
            "--use-mock-keychain",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-hang-monitor",
            "--disable-sync",
            "--disable-translate",
            "--disable-ipc-flooding-protection",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-component-extensions-with-background-pages",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-features=TranslateUI,BlinkGenPropertyTrees",
            "--disable-ipc-flooding-protection",
            "--enable-features=NetworkService,NetworkServiceLogging",
            "--force-color-profile=srgb",
            "--hide-scrollbars",
            "--mute-audio",
            "--no-default-browser-check",
            "--no-first-run",
            "--no-pings",
            "--no-zygote",
            "--use-mock-keychain"
        ]
    
    async def setup_stealth_context(self, browser, headless: bool = False) -> BrowserContext:
        """设置隐身浏览器上下文"""
        # 随机选择用户代理和屏幕分辨率
        user_agent = self.get_random_user_agent()
        screen_resolution = self.get_random_screen_resolution()
        language = self.get_random_language()
        
        # 创建上下文
        context = await browser.new_context(
            viewport=screen_resolution,
            user_agent=user_agent,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            geolocation={"latitude": 39.9042, "longitude": 116.4074},  # 北京
            permissions=["geolocation"],
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": language,
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"'
            }
        )
        
        return context
    
    async def setup_stealth_page(self, context: BrowserContext) -> Page:
        """设置隐身页面"""
        page = await context.new_page()
        
        # 注入反检测脚本
        await self._inject_stealth_scripts(page)
        
        # 设置随机延迟
        await page.wait_for_timeout(random.randint(1000, 3000))
        
        return page
    
    async def _inject_stealth_scripts(self, page: Page):
        """注入反检测脚本"""
        stealth_script = """
        // 移除webdriver属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // 重写plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // 重写languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en'],
        });
        
        // 重写permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 重写chrome对象
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // 重写权限API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 模拟真实的鼠标移动
        let mouseX = 0, mouseY = 0;
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        // 重写getBoundingClientRect
        const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
        Element.prototype.getBoundingClientRect = function() {
            const rect = originalGetBoundingClientRect.call(this);
            return {
                ...rect,
                x: rect.x + Math.random() * 0.1,
                y: rect.y + Math.random() * 0.1
            };
        };
        """
        
        await page.add_init_script(stealth_script)
    
    async def simulate_human_behavior(self, page: Page, duration: int = 5):
        """模拟人类行为"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # 随机鼠标移动
            await self._random_mouse_movement(page)
            
            # 随机滚动
            await self._random_scroll(page)
            
            # 随机等待
            await page.wait_for_timeout(random.randint(500, 2000))
    
    async def _random_mouse_movement(self, page: Page):
        """随机鼠标移动"""
        try:
            # 获取页面尺寸
            viewport = page.viewport_size
            if not viewport:
                return
            
            # 随机移动鼠标
            x = random.randint(0, viewport["width"])
            y = random.randint(0, viewport["height"])
            
            await page.mouse.move(x, y)
        except Exception:
            pass
    
    async def _random_scroll(self, page: Page):
        """随机滚动"""
        try:
            # 随机滚动距离
            scroll_distance = random.randint(-300, 300)
            await page.mouse.wheel(0, scroll_distance)
        except Exception:
            pass
    
    async def random_delay(self, min_ms: int = 1000, max_ms: int = 5000):
        """随机延迟"""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)
    
    def get_random_headers(self) -> Dict[str, str]:
        """获取随机HTTP头"""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": self.get_random_language(),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"'
        }

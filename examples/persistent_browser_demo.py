#!/usr/bin/env python3
"""
持久化浏览器演示脚本

展示如何使用增强版scraper-toolkit的持久化功能：
- 自动保存和恢复登录状态
- Cookie和会话持久化
- 跨平台状态管理

使用方法:
    python persistent_browser_demo.py

作者: AI Assistant
日期: 2025年9月20日
"""

import asyncio
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.enhanced_scraper_toolkit import EnhancedScraperToolkit, Platform, EnhancedScrapingConfig


async def demo_persistent_browser():
    """演示持久化浏览器功能"""
    print("🚀 持久化浏览器演示")
    print("=" * 50)
    
    # 创建配置
    config = EnhancedScrapingConfig(
        platform=Platform.ZHIHU,
        headless=False,  # 显示浏览器窗口
        persistent=True,  # 启用持久化
        auto_save_state=True,  # 自动保存状态
        state_save_interval=10  # 每10秒保存一次状态
    )
    
    # 创建增强版工具包
    toolkit = EnhancedScraperToolkit(config)
    
    try:
        # 1. 设置持久化浏览器
        print("📱 设置持久化浏览器...")
        result = await toolkit.setup_persistent_browser(Platform.ZHIHU)
        print(f"结果: {result['message']}")
        
        # 2. 检查登录状态
        print("\n🔐 检查登录状态...")
        login_status = await toolkit.check_login_status(Platform.ZHIHU)
        print(f"登录状态: {login_status['message']}")
        
        # 3. 导航到知乎
        print("\n🌐 导航到知乎...")
        nav_result = await toolkit.navigate_to("https://www.zhihu.com")
        print(f"导航结果: {nav_result['message']}")
        
        # 4. 等待用户操作（可以手动登录）
        print("\n⏳ 等待30秒，您可以手动登录...")
        print("   登录后，状态会自动保存")
        await asyncio.sleep(30)
        
        # 5. 再次检查登录状态
        print("\n🔐 再次检查登录状态...")
        login_status = await toolkit.check_login_status(Platform.ZHIHU)
        print(f"登录状态: {login_status['message']}")
        
        # 6. 执行搜索
        print("\n🔍 执行搜索...")
        search_result = await toolkit.search(Platform.ZHIHU, "人工智能", max_pages=2)
        if search_result["status"] == "success":
            print(f"找到 {len(search_result['results'])} 个结果")
            for i, item in enumerate(search_result["results"][:3], 1):
                print(f"  {i}. {item['title']}")
        else:
            print(f"搜索失败: {search_result['message']}")
        
        # 7. 列出保存的状态
        print("\n📋 列出保存的状态...")
        states = await toolkit.list_saved_states()
        for state in states:
            print(f"  平台: {state['platform']}")
            print(f"  保存时间: {state['saved_at']}")
            print(f"  Cookies: {state['cookies_count']} 个")
            print(f"  Local Storage: {state['local_storage_count']} 项")
            print()
        
        print("✅ 演示完成！")
        print("💡 提示: 下次运行时会自动恢复登录状态")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        await toolkit.cleanup()


async def demo_cross_platform():
    """演示跨平台状态管理"""
    print("\n🌍 跨平台状态管理演示")
    print("=" * 50)
    
    # 知乎平台
    print("📱 设置知乎平台...")
    zhihu_toolkit = EnhancedScraperToolkit(
        EnhancedScrapingConfig(platform=Platform.ZHIHU, persistent=True)
    )
    await zhihu_toolkit.setup_persistent_browser(Platform.ZHIHU)
    
    # 微信平台
    print("📱 设置微信平台...")
    wechat_toolkit = EnhancedScraperToolkit(
        EnhancedScrapingConfig(platform=Platform.WECHAT, persistent=True)
    )
    await wechat_toolkit.setup_persistent_browser(Platform.WECHAT)
    
    # 列出所有状态
    print("\n📋 所有平台状态:")
    states = await zhihu_toolkit.list_saved_states()
    for state in states:
        print(f"  {state['platform']}: {state['cookies_count']} cookies, {state['local_storage_count']} local storage")
    
    # 清理
    await zhihu_toolkit.cleanup()
    await wechat_toolkit.cleanup()


async def demo_state_management():
    """演示状态管理功能"""
    print("\n🔧 状态管理功能演示")
    print("=" * 50)
    
    toolkit = EnhancedScraperToolkit(
        EnhancedScrapingConfig(platform=Platform.GENERAL, persistent=True)
    )
    
    try:
        # 设置浏览器
        await toolkit.setup_persistent_browser(Platform.GENERAL)
        
        # 导航到测试页面
        await toolkit.navigate_to("https://httpbin.org/cookies/set/test_cookie/test_value")
        
        # 手动保存状态
        print("💾 手动保存状态...")
        await toolkit.browser_manager.save_browser_state(Platform.GENERAL.value)
        
        # 列出状态
        states = await toolkit.list_saved_states()
        print(f"📋 当前状态数量: {len(states)}")
        
        # 清除状态
        print("🗑️ 清除状态...")
        await toolkit.clear_platform_state(Platform.GENERAL)
        
        # 再次列出状态
        states = await toolkit.list_saved_states()
        print(f"📋 清除后状态数量: {len(states)}")
        
    finally:
        await toolkit.cleanup()


async def main():
    """主函数"""
    print("🎯 持久化浏览器功能演示")
    print("=" * 60)
    
    try:
        # 基础演示
        await demo_persistent_browser()
        
        # 跨平台演示
        await demo_cross_platform()
        
        # 状态管理演示
        await demo_state_management()
        
        print("\n🎉 所有演示完成！")
        print("\n💡 使用建议:")
        print("1. 启用persistent=True以保持登录状态")
        print("2. 设置auto_save_state=True自动保存状态")
        print("3. 使用check_login_status()检查登录状态")
        print("4. 定期调用cleanup()清理资源")
        
    except KeyboardInterrupt:
        print("\n⏹️ 演示被取消")
    except Exception as e:
        print(f"\n❌ 演示异常: {e}")


if __name__ == "__main__":
    asyncio.run(main())

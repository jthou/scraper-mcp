#!/usr/bin/env python3
"""
简化的微信功能测试

直接测试WeChatScraper类
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.wechat_scraper import WeChatScraper


async def test_wechat_scraper():
    """测试WeChatScraper类"""
    print("🔍 微信抓取器测试")
    print("=" * 40)
    
    scraper = WeChatScraper()
    
    try:
        # 测试连接
        print("\n1. 测试连接...")
        connection_result = await scraper.test_connection()
        print(f"   结果: {connection_result}")
        
        # 设置浏览器
        print("\n2. 设置浏览器...")
        setup_result = await scraper.setup_browser(headless=False, persistent=False)
        print(f"   结果: {setup_result}")
        
        if setup_result["status"] == "success":
            # 搜索测试
            print("\n3. 搜索微信内容...")
            search_result = await scraper.search_wechat("Python编程", max_pages=1)
            print(f"   结果: {search_result}")
            
            if search_result["status"] == "success":
                print(f"   ✅ 找到 {search_result['total_results']} 个结果")
                print(f"   📋 链接数量: {search_result['unique_links']}")
                
                # 显示前3个结果
                results = search_result.get('results', [])
                for i, item in enumerate(results[:3], 1):
                    print(f"\n   结果 {i}:")
                    print(f"     标题: {item['title']}")
                    print(f"     作者: {item['author']}")
                    print(f"     公众号: {item['account_name']}")
                    print(f"     时间: {item['publish_time']}")
                    print(f"     链接: {item['link']}")
            else:
                print(f"   ❌ 搜索失败: {search_result['message']}")
        else:
            print(f"   ❌ 浏览器设置失败: {setup_result['message']}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理资源
        print("\n4. 清理资源...")
        try:
            await scraper.cleanup()
            print("   ✅ 资源清理完成")
        except Exception as e:
            print(f"   ⚠️ 资源清理警告: {e}")
    
    print("\n🎉 微信抓取器测试完成！")


async def main():
    """主函数"""
    try:
        await test_wechat_scraper()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

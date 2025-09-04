#!/usr/bin/env python3
"""
微信公众号搜索测试脚本

这个脚本用于测试微信公众号搜索功能的各种方法
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from experiments.wechat_search_experiment import WeChatSearchExperiment


async def test_sogou_search():
    """测试搜狗微信搜索"""
    print("🔍 测试搜狗微信搜索")
    print("-" * 30)
    
    experiment = WeChatSearchExperiment()
    
    # 设置浏览器
    if not await experiment.setup_browser(headless=False):
        print("❌ 浏览器设置失败")
        return False
    
    try:
        # 测试搜索
        result = await experiment.method1_sogou_wechat_search("Python编程")
        
        if result["status"] == "success":
            print(f"✅ 搜索成功: {result['message']}")
            print(f"📊 结果数量: {len(result.get('results', []))}")
            
            # 显示前3个结果
            for i, item in enumerate(result.get('results', [])[:3], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   作者: {item['author']}")
                print(f"   摘要: {item['summary'][:100]}...")
                print(f"   链接: {item['link']}")
        else:
            print(f"❌ 搜索失败: {result['message']}")
        
        return result["status"] == "success"
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False
    
    finally:
        if experiment.browser:
            await experiment.browser.close()
        if experiment.playwright:
            await experiment.playwright.stop()


async def test_wechat_pc_search():
    """测试微信PC版搜索"""
    print("\n🔍 测试微信PC版搜索")
    print("-" * 30)
    
    experiment = WeChatSearchExperiment()
    
    # 设置浏览器
    if not await experiment.setup_browser(headless=False):
        print("❌ 浏览器设置失败")
        return False
    
    try:
        # 测试搜索
        result = await experiment.method2_wechat_pc_search("机器学习")
        
        if result["status"] == "success":
            print(f"✅ 搜索成功: {result['message']}")
            print(f"📊 结果数量: {len(result.get('results', []))}")
        elif result["status"] == "waiting":
            print(f"⏳ 需要登录: {result['message']}")
            print(f"💡 请手动登录微信账号")
        else:
            print(f"❌ 搜索失败: {result['message']}")
        
        return result["status"] in ["success", "waiting"]
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False
    
    finally:
        if experiment.browser:
            await experiment.browser.close()
        if experiment.playwright:
            await experiment.playwright.stop()


async def test_third_party_search():
    """测试第三方平台搜索"""
    print("\n🔍 测试第三方平台搜索")
    print("-" * 30)
    
    experiment = WeChatSearchExperiment()
    
    # 设置浏览器
    if not await experiment.setup_browser(headless=False):
        print("❌ 浏览器设置失败")
        return False
    
    try:
        # 测试搜索
        result = await experiment.method3_third_party_search("人工智能")
        
        if result["status"] == "success":
            print(f"✅ 搜索成功: {result['message']}")
            print(f"📊 结果数量: {len(result.get('results', []))}")
            
            # 显示前3个结果
            for i, item in enumerate(result.get('results', [])[:3], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   作者: {item['author']}")
                print(f"   摘要: {item['summary'][:100]}...")
                print(f"   链接: {item['link']}")
        else:
            print(f"❌ 搜索失败: {result['message']}")
        
        return result["status"] == "success"
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False
    
    finally:
        if experiment.browser:
            await experiment.browser.close()
        if experiment.playwright:
            await experiment.playwright.stop()


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始微信公众号搜索测试")
    print("=" * 50)
    
    tests = [
        ("搜狗微信搜索", test_sogou_search),
        ("微信PC版搜索", test_wechat_pc_search),
        ("第三方平台搜索", test_third_party_search)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        try:
            success = await test_func()
            results[test_name] = success
            print(f"{'✅' if success else '❌'} {test_name}: {'通过' if success else '失败'}")
        except Exception as e:
            print(f"❌ {test_name}: 异常 - {e}")
            results[test_name] = False
        
        # 等待一下再运行下一个测试
        await asyncio.sleep(2)
    
    # 显示测试总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    return results


async def main():
    """主函数"""
    try:
        results = await run_all_tests()
        
        # 根据测试结果决定退出码
        all_passed = all(results.values())
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

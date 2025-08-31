#!/usr/bin/env python3
"""
测试MCP Server的所有工具功能
"""
import asyncio
import sys
import json
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.web_scraper import WebScraper
from utils.logger import Logger


async def test_mcp_tools():
    """测试所有MCP工具功能"""
    logger = Logger("MCP工具测试")
    
    # 创建WebScraper实例
    scraper = WebScraper()
    
    print("🚀 开始测试MCP Server的所有工具...")
    
    # 测试1: 登录知乎
    print("\n" + "="*50)
    print("🔐 测试1: 登录知乎")
    print("="*50)
    
    login_result = await scraper.login_zhihu(headless=False)
    if login_result["status"] == "success":
        print("✅ 登录成功！")
    else:
        print(f"❌ 登录失败: {login_result['message']}")
        return False
    
    # 测试2: 搜索知乎内容
    print("\n" + "="*50)
    print("🔍 测试2: 搜索知乎内容")
    print("="*50)
    
    search_result = await scraper.search_zhihu(
        query="Python编程",
        max_pages=1,
        min_relevance=0.5
    )
    
    if search_result["status"] == "success":
        print("✅ 搜索成功！")
        print(f"📊 总结果数: {search_result['total_results']}")
        print(f"🎯 符合要求的结果数: {search_result['filtered_results']}")
        
        qualified_links = search_result.get("qualified_links", [])
        if qualified_links:
            print(f"\n📋 符合要求的所有页面链接 ({len(qualified_links)}个):")
            for i, link in enumerate(qualified_links[:5], 1):  # 只显示前5个
                print(f"  {i}. {link}")
    else:
        print(f"❌ 搜索失败: {search_result['message']}")
        return False
    
    # 测试3: 读取知乎页面内容
    if qualified_links:
        print("\n" + "="*50)
        print("📖 测试3: 读取知乎页面内容")
        print("="*50)
        
        # 选择第一个链接进行测试
        test_url = qualified_links[0]
        print(f"🔗 测试URL: {test_url}")
        
        read_result = await scraper.read_zhihu_page(test_url)
        
        if read_result["status"] == "success":
            print("✅ 页面读取成功！")
            print(f"📄 页面标题: {read_result['title']}")
            print(f"📏 内容长度: {read_result['text_length']} 字符")
            print(f"📝 内容预览: {read_result['text_content'][:200]}...")
        else:
            print(f"❌ 页面读取失败: {read_result['message']}")
    
    print("\n" + "="*50)
    print("🎉 所有MCP工具测试完成！")
    print("="*50)
    
    return True


async def main():
    """主函数"""
    try:
        success = await test_mcp_tools()
        if success:
            print("\n✅ 所有测试通过！MCP Server工具功能正常！")
        else:
            print("\n❌ 测试失败！")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

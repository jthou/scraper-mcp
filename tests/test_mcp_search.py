#!/usr/bin/env python3
"""
测试MCP Server的知乎搜索功能
"""
import asyncio
import sys
import json
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.web_scraper import WebScraper
from utils.logger import Logger


async def test_mcp_search_tool():
    """测试MCP搜索工具功能"""
    logger = Logger("MCP搜索工具测试")
    
    # 创建WebScraper实例
    scraper = WebScraper()
    
    # 先登录知乎
    print("🔐 正在登录知乎...")
    login_result = await scraper.login_zhihu(headless=False)
    if login_result["status"] != "success":
        print(f"❌ 登录失败: {login_result['message']}")
        return False
    
    print("✅ 登录成功！")
    
    # 测试搜索功能
    test_queries = [
        {
            "query": "Python编程",
            "max_pages": 2,
            "min_relevance": 0.5
        },
        {
            "query": "机器学习算法",
            "max_pages": 1,
            "min_relevance": 0.6
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"🧪 测试 {i}: {test_case['query']}")
        print(f"{'='*60}")
        
        # 调用搜索功能
        result = await scraper.search_zhihu(
            query=test_case["query"],
            max_pages=test_case["max_pages"],
            min_relevance=test_case["min_relevance"]
        )
        
        if result["status"] == "success":
            print(f"✅ 搜索成功!")
            print(f"📊 总结果数: {result['total_results']}")
            print(f"🎯 符合要求的结果数: {result['filtered_results']}")
            
            # 显示符合要求的所有页面链接
            qualified_links = result.get("qualified_links", [])
            if qualified_links:
                print(f"\n📋 符合要求的所有页面链接 ({len(qualified_links)}个):")
                for j, link in enumerate(qualified_links, 1):
                    print(f"  {j}. {link}")
                
                # 显示前3个结果的详细信息
                results = result.get("results", [])
                print(f"\n📊 前3个结果详细信息:")
                for j, item in enumerate(results[:3], 1):
                    print(f"\n  {j}. {item['title']}")
                    print(f"     作者: {item['author']}")
                    print(f"     点赞: {item['vote_count']}")
                    print(f"     相关性: {item['relevance_score']:.2f}")
                    print(f"     链接: {item['url']}")
                    if item['summary']:
                        print(f"     摘要: {item['summary'][:80]}...")
            else:
                print("❌ 没有找到符合要求的结果")
        else:
            print(f"❌ 搜索失败: {result['message']}")
    
    print(f"\n{'='*60}")
    print("🎉 MCP搜索工具测试完成！")
    print(f"{'='*60}")
    
    return True


async def main():
    """主函数"""
    print("🚀 开始测试MCP Server的知乎搜索功能...")
    
    try:
        success = await test_mcp_search_tool()
        if success:
            print("\n✅ 所有测试通过！")
        else:
            print("\n❌ 测试失败！")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

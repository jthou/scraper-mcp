#!/usr/bin/env python3
"""
ArXiv文献搜索与下载示例

演示如何使用ArXiv搜索器进行文献搜索和下载
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.arxiv_searcher import ArxivSearcher


async def example_basic_search():
    """基础搜索示例"""
    print("🔍 ArXiv基础搜索示例")
    print("=" * 40)
    
    searcher = ArxivSearcher(Path("data/arxiv_demo"))
    
    # 1. 基础搜索
    print("\n1. 搜索机器学习相关论文...")
    search_result = await searcher.search_arxiv(
        query="machine learning",
        max_results=5,
        sort_by="relevance"
    )
    
    if search_result["status"] == "success":
        papers = search_result["results"]
        print(f"   找到 {len(papers)} 篇论文:")
        for i, paper in enumerate(papers, 1):
            print(f"   {i}. {paper['title'][:60]}...")
            print(f"      ID: {paper['arxiv_id']}, 分类: {paper['primary_category']}")
    
    return search_result


async def example_category_search():
    """分类搜索示例"""
    print("\n🎯 分类搜索示例")
    print("=" * 40)
    
    searcher = ArxivSearcher(Path("data/arxiv_demo"))
    
    # 2. 按分类搜索
    print("\n2. 搜索计算机视觉论文...")
    search_result = await searcher.search_arxiv(
        query="computer vision",
        max_results=3,
        categories=["cs.CV"],
        sort_by="submittedDate",
        sort_order="descending"
    )
    
    if search_result["status"] == "success":
        papers = search_result["results"]
        print(f"   找到 {len(papers)} 篇计算机视觉论文:")
        for paper in papers:
            print(f"   • {paper['title']}")
            print(f"     作者: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
            print(f"     发布: {paper['published'][:10] if paper['published'] else 'N/A'}")
    
    return search_result


async def example_download_papers():
    """下载论文示例"""
    print("\n📥 论文下载示例")
    print("=" * 40)
    
    searcher = ArxivSearcher(Path("data/arxiv_demo"))
    
    # 3. 搜索并下载
    print("\n3. 搜索并下载深度学习论文...")
    result = await searcher.search_and_download(
        query="deep learning",
        max_results=3,
        categories=["cs.LG"],
        auto_download=True
    )
    
    if result["status"] in ["success", "partial"]:
        summary = result.get("download_summary", {})
        print(f"   下载摘要:")
        print(f"   • 总论文数: {summary.get('total_papers', 0)}")
        print(f"   • 成功下载: {summary.get('successful_downloads', 0)}")
        print(f"   • 已存在跳过: {summary.get('skipped_papers', 0)}")
        print(f"   • 下载失败: {summary.get('failed_downloads', 0)}")
        print(f"   • 成功率: {summary.get('success_rate', 0):.1f}%")
    
    return result


async def example_date_filtered_search():
    """日期过滤搜索示例"""
    print("\n📅 日期过滤搜索示例")
    print("=" * 40)
    
    searcher = ArxivSearcher(Path("data/arxiv_demo"))
    
    # 4. 按日期搜索
    print("\n4. 搜索2024年的自然语言处理论文...")
    search_result = await searcher.search_arxiv(
        query="natural language processing",
        max_results=5,
        categories=["cs.CL"],
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    
    if search_result["status"] == "success":
        papers = search_result["results"]
        print(f"   找到 {len(papers)} 篇2024年NLP论文:")
        for paper in papers:
            pub_date = paper['published'][:10] if paper['published'] else 'N/A'
            print(f"   • [{pub_date}] {paper['title'][:50]}...")
    
    return search_result


async def main():
    """运行所有示例"""
    print("🚀 ArXiv文献搜索与下载示例")
    print("=" * 50)
    
    try:
        # 运行各种示例
        await example_basic_search()
        await example_category_search()
        await example_download_papers()
        await example_date_filtered_search()
        
        print("\n✅ 所有示例运行完成!")
        print("\n💡 提示:")
        print("   • PDF文件保存在: data/arxiv_demo/pdfs/")
        print("   • 元数据保存在: data/arxiv_demo/metadata/")
        print("   • 进度文件: data/arxiv_demo/progress.json")
        print("   • 搜索缓存: data/arxiv_demo/search_cache.json")
        
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
ArXiv文献快速搜索下载工具

简单易用的arxiv文献搜索下载工具，集成到现有项目架构中
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))
from core.arxiv_searcher import ArxivSearcher


async def quick_search_and_download():
    """快速搜索并下载示例"""
    print("🔬 ArXiv文献快速搜索下载工具")
    print("=" * 50)
    
    # 创建搜索器
    searcher = ArxivSearcher()
    
    # 获取用户输入
    query = input("请输入搜索关键词 (如: machine learning): ").strip()
    if not query:
        query = "machine learning"
    
    try:
        max_results = int(input("最大结果数 (默认5): ").strip() or "5")
    except ValueError:
        max_results = 5
    
    download_choice = input("是否下载PDF? (y/n, 默认y): ").strip().lower()
    auto_download = download_choice != 'n'
    
    # 新增：Markdown转换选项
    markdown_choice = "n"
    convert_method = "none"
    if auto_download and searcher.enable_markdown:
        markdown_choice = input("是否转换为Markdown? (y/n, 默认n): ").strip().lower()
        if markdown_choice == 'y':
            method_choice = input("转换方法 (pdf/tex/both, 默认pdf): ").strip().lower()
            convert_method = method_choice if method_choice in ["pdf", "tex", "both"] else "pdf"
    
    print(f"\n🔍 搜索关键词: {query}")
    print(f"📊 最大结果数: {max_results}")
    print(f"📥 自动下载: {'是' if auto_download else '否'}")
    if auto_download:
        print(f"📝 Markdown转换: {'是' if markdown_choice == 'y' else '否'}")
        if markdown_choice == 'y':
            print(f"🔧 转换方法: {convert_method}")
    print("-" * 50)
    
    # 执行搜索和下载
    if markdown_choice == 'y':
        # 先搜索
        search_result = await searcher.search_arxiv(
            query=query,
            max_results=max_results
        )
        
        if search_result["status"] == "success" and search_result["results"]:
            papers = search_result["results"]
            print(f"🔍 找到 {len(papers)} 篇相关文献")
            
            # 批量转换
            result = await searcher.batch_convert_to_markdown(
                papers,
                convert_method=convert_method
            )
        else:
            result = search_result
    else:
        # 传统的搜索下载
        result = await searcher.search_and_download(
            query=query,
            max_results=max_results,
            auto_download=auto_download
        )
    
    if result["status"] in ["success", "partial"]:
        print(f"\n✅ 任务完成!")
        if auto_download and markdown_choice != 'y':
            summary = result.get("download_summary", {})
            print(f"📊 下载统计:")
            print(f"  • 总文献数: {summary.get('total_papers', 0)}")
            print(f"  • 成功下载: {summary.get('successful_downloads', 0)}")
            print(f"  • 已存在跳过: {summary.get('skipped_papers', 0)}")
            print(f"  • 下载失败: {summary.get('failed_downloads', 0)}")
            print(f"  • 成功率: {summary.get('success_rate', 0):.1f}%")
            print(f"\n📁 文件保存在: {searcher.output_dir}")
        elif markdown_choice == 'y':
            summary = result.get("summary", {})
            print(f"📝 转换统计:")
            print(f"  • 总文献数: {summary.get('total_papers', 0)}")
            print(f"  • 成功转换: {summary.get('successful_conversions', 0)}")
            print(f"  • 转换失败: {summary.get('failed_conversions', 0)}")
            print(f"  • 成功率: {summary.get('success_rate', 0):.1f}%")
            print(f"\n📁 PDF文件: {searcher.pdf_dir}")
            print(f"📄 Markdown文件: {searcher.markdown_dir}")
        else:
            search_count = len(result.get('results', []))
            print(f"📄 找到 {search_count} 篇相关文献")
    else:
        print(f"❌ 任务失败: {result.get('message')}")


if __name__ == "__main__":
    print("ArXiv文献搜索下载工具")
    print("基于现有项目架构，提供简单易用的学术文献获取功能")
    print()
    
    try:
        asyncio.run(quick_search_and_download())
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        
    print("\n感谢使用！")

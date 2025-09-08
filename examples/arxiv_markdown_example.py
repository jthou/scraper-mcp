#!/usr/bin/env python3
"""
ArXiv Markdown转换示例

演示如何使用ArXiv搜索器的Markdown转换功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))
from core.arxiv_searcher import ArxivSearcher


async def test_pdf_to_markdown():
    """测试PDF转Markdown"""
    print("🔬 测试PDF转Markdown功能")
    print("=" * 50)
    
    searcher = ArxivSearcher()
    
    # 搜索一篇论文
    search_result = await searcher.search_arxiv(
        query="transformer attention",
        max_results=1
    )
    
    if search_result["status"] == "success" and search_result["results"]:
        paper = search_result["results"][0]
        print(f"选中论文: {paper['title']}")
        
        # 下载并转换为Markdown
        result = await searcher.download_and_convert_to_markdown(
            paper, 
            convert_method="pdf"
        )
        
        print("\n转换结果:")
        print(f"状态: {result['status']}")
        if result["status"] == "success":
            pdf_conversion = result["conversions"]["pdf_to_markdown"]
            if pdf_conversion["status"] == "success":
                print(f"✅ PDF转换成功!")
                print(f"📄 Markdown文件: {pdf_conversion['markdown_path']}")
                print(f"📏 内容长度: {pdf_conversion['content_length']} 字符")
            else:
                print(f"❌ PDF转换失败: {pdf_conversion['message']}")
    else:
        print("❌ 未找到论文")


async def test_tex_to_markdown():
    """测试TeX转Markdown"""
    print("\n🔬 测试TeX转Markdown功能")
    print("=" * 50)
    
    searcher = ArxivSearcher()
    
    # 搜索一篇论文
    search_result = await searcher.search_arxiv(
        query="neural network",
        max_results=1
    )
    
    if search_result["status"] == "success" and search_result["results"]:
        paper = search_result["results"][0]
        print(f"选中论文: {paper['title']}")
        
        # 下载并转换为Markdown
        result = await searcher.download_and_convert_to_markdown(
            paper, 
            convert_method="tex"
        )
        
        print("\n转换结果:")
        print(f"状态: {result['status']}")
        if result["status"] == "success":
            tex_conversion = result["conversions"]["tex_to_markdown"]
            if tex_conversion["status"] == "success":
                print(f"✅ TeX转换成功!")
                print(f"📄 Markdown文件: {tex_conversion['markdown_path']}")
                print(f"📏 内容长度: {tex_conversion['content_length']} 字符")
                print(f"📝 源TeX文件: {tex_conversion['source_tex']}")
            else:
                print(f"❌ TeX转换失败: {tex_conversion['message']}")
    else:
        print("❌ 未找到论文")


async def test_both_conversions():
    """测试双重转换（PDF + TeX）"""
    print("\n🔬 测试双重转换功能")
    print("=" * 50)
    
    searcher = ArxivSearcher()
    
    # 搜索一篇论文
    search_result = await searcher.search_arxiv(
        query="computer vision",
        max_results=1
    )
    
    if search_result["status"] == "success" and search_result["results"]:
        paper = search_result["results"][0]
        print(f"选中论文: {paper['title']}")
        
        # 下载并转换为Markdown（两种方法都试）
        result = await searcher.download_and_convert_to_markdown(
            paper, 
            convert_method="both"
        )
        
        print("\n转换结果:")
        print(f"总体状态: {result['status']}")
        
        # PDF转换结果
        if "pdf_to_markdown" in result["conversions"]:
            pdf_conv = result["conversions"]["pdf_to_markdown"]
            print(f"\n📄 PDF转换: {pdf_conv['status']}")
            if pdf_conv["status"] == "success":
                print(f"  ✅ 文件: {pdf_conv['markdown_path']}")
                print(f"  📏 长度: {pdf_conv['content_length']} 字符")
        
        # TeX转换结果
        if "tex_to_markdown" in result["conversions"]:
            tex_conv = result["conversions"]["tex_to_markdown"]
            print(f"\n📝 TeX转换: {tex_conv['status']}")
            if tex_conv["status"] == "success":
                print(f"  ✅ 文件: {tex_conv['markdown_path']}")
                print(f"  📏 长度: {tex_conv['content_length']} 字符")
                print(f"  📋 源文件: {tex_conv['source_tex']}")
    else:
        print("❌ 未找到论文")


async def test_batch_conversion():
    """测试批量转换"""
    print("\n🔬 测试批量转换功能")
    print("=" * 50)
    
    searcher = ArxivSearcher()
    
    # 搜索多篇论文
    search_result = await searcher.search_arxiv(
        query="machine learning",
        max_results=2
    )
    
    if search_result["status"] == "success" and search_result["results"]:
        papers = search_result["results"]
        print(f"找到 {len(papers)} 篇论文，开始批量转换...")
        
        # 批量转换（只用PDF转换，速度较快）
        result = await searcher.batch_convert_to_markdown(
            papers, 
            convert_method="pdf"
        )
        
        print("\n批量转换结果:")
        summary = result["summary"]
        print(f"📊 总数: {summary['total_papers']}")
        print(f"✅ 成功: {summary['successful_conversions']}")
        print(f"❌ 失败: {summary['failed_conversions']}")
        print(f"📈 成功率: {summary['success_rate']}%")
    else:
        print("❌ 未找到论文")


async def main():
    """主函数"""
    print("🎯 ArXiv Markdown转换功能测试")
    print("基于ArXiv搜索器的Markdown转换能力展示")
    print()
    
    try:
        # 测试各种转换功能
        await test_pdf_to_markdown()
        await test_tex_to_markdown()
        await test_both_conversions()
        await test_batch_conversion()
        
        print("\n🎉 所有测试完成!")
        print("检查 K-Vault/ArXiv/markdown/ 目录查看转换结果")
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

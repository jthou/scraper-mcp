#!/usr/bin/env python3
"""
Isaac项目遗留文件清理脚本
自动归档有价值的报告文件，删除无用的脚本
"""

import os
import shutil
from pathlib import Path

def main():
    """主清理函数"""
    print("🧹 Isaac项目遗留文件清理工具")
    print("=" * 50)
    
    # 确保归档目录存在
    archives_dir = Path("archives/isaac_legacy")
    archives_dir.mkdir(parents=True, exist_ok=True)
    
    # 需要归档的有价值文件（报告、分析结果等）
    files_to_archive = [
        "isaac_real_docs_discovery.json",
        "isaac_url_analysis_report.json",
        # 如果存在其他报告文件也可以加入
    ]
    
    # 需要删除的无用脚本文件
    files_to_delete = [
        # 早期实验版本脚本
        "auto_download_isaac.py",
        "clean_isaac_links.py", 
        "collect_isaac_pages.py",
        "download_isaac_docs.py",
        "isaac_batch_downloader.py",
        "isaac_clean_downloader.py",
        "isaac_complete_downloader.py",
        "isaac_continue_downloader.py",
        "isaac_sim_simple.py",
        
        # 特定功能脚本（任务已完成）
        "isaac_link_discoverer.py",
        "isaac_pdf_scraper.py", 
        "isaac_playwright_scraper.py",
        "isaac_real_docs_finder.py",
        "isaac_simulation_cases_finder.py",
        "isaac_smart_crawler.py",
        "isaac_smart_scraper.py",
        "isaac_supplement_downloader.py",
        "isaac_url_discoverer.py",
        "isaac_validated_downloader.py",
        "smart_isaac_search.py",
    ]
    
    # 归档有价值文件
    print("\n📦 归档有价值文件:")
    archived_count = 0
    for file_name in files_to_archive:
        if os.path.exists(file_name):
            try:
                shutil.move(file_name, archives_dir / file_name)
                print(f"  ✅ 已归档: {file_name}")
                archived_count += 1
            except Exception as e:
                print(f"  ❌ 归档失败: {file_name} - {e}")
        else:
            print(f"  ⚪ 不存在: {file_name}")
    
    # 删除无用脚本
    print(f"\n🗑️  删除无用脚本:")
    deleted_count = 0
    total_size = 0
    
    for file_name in files_to_delete:
        if os.path.exists(file_name):
            try:
                file_size = os.path.getsize(file_name)
                os.remove(file_name)
                print(f"  ✅ 已删除: {file_name} ({file_size/1024:.1f}KB)")
                deleted_count += 1
                total_size += file_size
            except Exception as e:
                print(f"  ❌ 删除失败: {file_name} - {e}")
        else:
            print(f"  ⚪ 不存在: {file_name}")
    
    # 检查是否还有其他isaac文件
    print(f"\n🔍 检查剩余Isaac文件:")
    remaining_files = []
    for file in os.listdir("."):
        if "isaac" in file.lower() and os.path.isfile(file):
            remaining_files.append(file)
    
    if remaining_files:
        print("  发现剩余文件:")
        for file in remaining_files:
            print(f"    📄 {file}")
        print("  请手动检查这些文件是否需要处理")
    else:
        print("  ✅ 没有发现其他Isaac相关文件")
    
    # 总结
    print(f"\n🎉 清理完成!")
    print(f"  📦 归档文件: {archived_count} 个")
    print(f"  🗑️  删除文件: {deleted_count} 个") 
    print(f"  💾 释放空间: {total_size/1024:.1f}KB")
    print(f"  📁 保留工具: examples/tools/ 目录中的8个核心工具")
    print(f"  📚 文档集合: K-Vault/Isaac/ 目录中的821MB文档")

if __name__ == "__main__":
    main()

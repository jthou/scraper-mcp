#!/usr/bin/env python3
"""
Isaac文档项目最终清理工具
安全删除不再需要的临时目录和文件
"""

import os
import shutil
import sys
from pathlib import Path

# 要删除的目录列表
DIRECTORIES_TO_DELETE = [
    "isaac_complete_links",
    "isaac_complete_pdfs", 
    "isaac_sim_docs_20250908_215351",
    "isaac_sim_downloads",
    "isaac_sim_pdfs",
    "isaac_simulation_cases",
    "isaac_site_analysis", 
    "isaac_supplement_downloads",
    "isaac_url_validation",
    "isaac_validated_downloads"
]

# 要删除的文件列表（可选）
FILES_TO_DELETE = [
    "isaac_smart_cleanup_report.json"  # 清理报告文件也可以删除
]

def get_directory_size(path):
    """计算目录大小"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
    except OSError:
        pass
    return total_size

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def main():
    """主函数"""
    print("🧹 Isaac文档项目最终清理工具")
    print("=" * 50)
    
    # 确认K-Vault/Isaac存在且完整
    kvault_path = Path("K-Vault/Isaac")
    if not kvault_path.exists():
        print("❌ 错误: K-Vault/Isaac目录不存在！")
        print("   为了安全起见，不执行清理操作。")
        return 1
    
    kvault_size = get_directory_size(kvault_path)
    print(f"✅ K-Vault/Isaac目录存在，大小: {format_size(kvault_size)}")
    
    # 检查要删除的目录
    existing_dirs = []
    total_size_to_delete = 0
    
    print("\n🔍 扫描待删除目录:")
    for dir_name in DIRECTORIES_TO_DELETE:
        if os.path.exists(dir_name):
            size = get_directory_size(dir_name)
            total_size_to_delete += size
            existing_dirs.append((dir_name, size))
            print(f"  📁 {dir_name} - {format_size(size)}")
        else:
            print(f"  ⚪ {dir_name} - 不存在")
    
    # 检查要删除的文件
    existing_files = []
    print("\n🔍 扫描待删除文件:")
    for file_name in FILES_TO_DELETE:
        if os.path.exists(file_name):
            size = os.path.getsize(file_name)
            total_size_to_delete += size
            existing_files.append((file_name, size))
            print(f"  📄 {file_name} - {format_size(size)}")
        else:
            print(f"  ⚪ {file_name} - 不存在")
    
    if not existing_dirs and not existing_files:
        print("\n✅ 没有找到需要删除的目录或文件")
        return 0
    
    print(f"\n📊 总计将释放空间: {format_size(total_size_to_delete)}")
    
    # 确认删除
    print("\n⚠️  确认删除操作:")
    print("   这将永久删除上述列出的目录和文件")
    print("   K-Vault/Isaac目录将保持完整不变")
    
    confirm = input("\n❓ 确定要继续吗？(输入 'YES' 确认): ")
    if confirm != 'YES':
        print("❌ 取消删除操作")
        return 1
    
    # 执行删除
    print("\n🗑️  开始删除...")
    deleted_count = 0
    
    # 删除目录
    for dir_name, size in existing_dirs:
        try:
            shutil.rmtree(dir_name)
            print(f"  ✅ 已删除目录: {dir_name} ({format_size(size)})")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ 删除失败: {dir_name} - {e}")
    
    # 删除文件  
    for file_name, size in existing_files:
        try:
            os.remove(file_name)
            print(f"  ✅ 已删除文件: {file_name} ({format_size(size)})")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ 删除失败: {file_name} - {e}")
    
    print(f"\n🎉 清理完成!")
    print(f"   删除了 {deleted_count} 个项目")
    print(f"   释放空间: {format_size(total_size_to_delete)}")
    print(f"   K-Vault/Isaac保持完整: {format_size(kvault_size)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

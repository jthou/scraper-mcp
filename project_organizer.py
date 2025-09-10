#!/usr/bin/env python3
"""
项目根目录文件整理脚本
分析文件价值，移动到合适位置或删除无用文件
"""

import os
import shutil
from pathlib import Path

def main():
    """主整理函数"""
    print("📂 项目根目录文件整理工具")
    print("=" * 50)
    
    # 确保目标目录存在
    examples_dir = Path("examples")
    archives_dir = Path("archives/legacy")
    docs_dir = Path("docs")
    
    for dir_path in [examples_dir, archives_dir, docs_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 文件分类和处理规则
    file_rules = {
        # GitHub Token相关 - 移动到examples（有价值的示例）
        "github_tools": {
            "target": examples_dir,
            "files": [
                "example_token_usage.py",      # GitHub Token使用示例
                "github_token_cli.py",         # 命令行工具  
                "simple_setup.py",            # 简单设置脚本
                "simple_test.py",             # 测试脚本
                "setup_github_token.py",      # 设置向导
            ]
        },
        
        # 文档 - 移动到docs
        "documentation": {
            "target": docs_dir,
            "files": [
                "GITHUB_TOKEN_SETUP.md",      # 设置文档
            ]
        },
        
        # 归档文件 - 移动到archives
        "archive": {
            "target": archives_dir,  
            "files": [
                "FINAL_ISAAC_DOWNLOAD_REPORT.md",  # Isaac项目最终报告
                "isaac_legacy_cleaner.py",         # 刚用过的清理脚本
                "run_with_system_python.sh",       # 运行脚本（已过时）
            ]
        },
        
        # 保留在根目录（重要文件）
        "keep_root": {
            "target": None,
            "files": [
                "README.md",                   # 项目说明
                "requirements.txt",            # 依赖文件
            ]
        }
    }
    
    # 执行文件整理
    for category, config in file_rules.items():
        target_dir = config["target"]
        files = config["files"]
        
        print(f"\n📁 处理 {category} 类别:")
        
        if target_dir is None:
            print(f"  🔒 保留在根目录")
            for file_name in files:
                if os.path.exists(file_name):
                    print(f"    ✅ 保留: {file_name}")
                else:
                    print(f"    ⚪ 不存在: {file_name}")
            continue
        
        # 移动文件
        moved_count = 0
        for file_name in files:
            if os.path.exists(file_name):
                try:
                    target_path = target_dir / file_name
                    shutil.move(file_name, target_path)
                    print(f"    ✅ 已移动: {file_name} → {target_dir}")
                    moved_count += 1
                except Exception as e:
                    print(f"    ❌ 移动失败: {file_name} - {e}")
            else:
                print(f"    ⚪ 不存在: {file_name}")
        
        print(f"    📊 {category}: 移动了 {moved_count} 个文件")
    
    # 检查根目录还有什么文件
    print(f"\n🔍 检查根目录剩余文件:")
    root_files = [f for f in os.listdir(".") if os.path.isfile(f) and not f.startswith('.')]
    
    # 过滤掉已知的重要文件
    known_important = {
        "README.md", "requirements.txt", "main.py", "mcp_client.py", 
        "config.yaml", "server.log", "tags", "TODO.md"
    }
    
    remaining_files = [f for f in root_files if f not in known_important]
    
    if remaining_files:
        print("  发现其他文件:")
        for file in remaining_files:
            print(f"    📄 {file}")
    else:
        print("  ✅ 根目录已整理完毕")
    
    # 总结
    print(f"\n🎉 整理完成!")
    print(f"  📁 examples/: GitHub工具示例")
    print(f"  📁 docs/: 项目文档")  
    print(f"  📁 archives/legacy/: 归档文件")
    print(f"  📁 根目录: 保留核心项目文件")

if __name__ == "__main__":
    main()

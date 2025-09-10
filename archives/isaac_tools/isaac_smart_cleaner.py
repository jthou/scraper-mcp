#!/usr/bin/env python3
"""
Isaac文档智能清理工具
- 如果文件已在K-Vault/Isaac中存在，则删除原文件
- 如果文件不存在，则移动到K-Vault/Isaac
- 支持PDF和Markdown文件
"""

import os
import shutil
from pathlib import Path
import hashlib
import json
from datetime import datetime

class IsaacSmartCleaner:
    def __init__(self):
        self.base_dir = Path(".")
        self.k_vault_dir = Path("K-Vault/Isaac")
        self.k_vault_pdfs = self.k_vault_dir / "pdfs"
        self.k_vault_markdown = self.k_vault_dir / "markdown"
        
        # 统计信息
        self.stats = {
            "processed_directories": [],
            "deleted_files": [],
            "moved_files": [],
            "skipped_files": [],
            "total_freed_mb": 0,
            "total_moved_mb": 0
        }
        
        # 构建K-Vault中已有文件的索引
        self.k_vault_file_hashes = {}
        self.k_vault_file_names = set()
        self.build_k_vault_index()
        
    def calculate_file_hash(self, file_path):
        """计算文件的MD5哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def build_k_vault_index(self):
        """构建K-Vault中已有文件的索引"""
        print("🔍 构建K-Vault文件索引...")
        
        # 索引PDF文件
        if self.k_vault_pdfs.exists():
            for pdf_file in self.k_vault_pdfs.glob("*.pdf"):
                file_hash = self.calculate_file_hash(pdf_file)
                if file_hash:
                    self.k_vault_file_hashes[file_hash] = str(pdf_file)
                self.k_vault_file_names.add(pdf_file.name.lower())
        
        # 索引Markdown文件
        if self.k_vault_markdown.exists():
            for md_file in self.k_vault_markdown.glob("*.md"):
                file_hash = self.calculate_file_hash(md_file)
                if file_hash:
                    self.k_vault_file_hashes[file_hash] = str(md_file)
                self.k_vault_file_names.add(md_file.name.lower())
        
        print(f"  📋 已索引 {len(self.k_vault_file_hashes)} 个文件哈希")
        print(f"  📋 已索引 {len(self.k_vault_file_names)} 个文件名")
    
    def find_isaac_directories(self):
        """查找所有待清理的Isaac目录"""
        isaac_dirs = [
            "isaac_complete_docs",
            "isaac_complete_links", 
            "isaac_complete_pdfs",
            "isaac_sim_docs_20250908_215351",
            "isaac_sim_docs_20250908_215422",
            "isaac_sim_downloads",
            "isaac_sim_pdfs",
            "isaac_simulation_cases",
            "isaac_site_analysis",
            "isaac_smart_crawl",
            "isaac_supplement_downloads",
            "isaac_unlimited_downloads",
            "isaac_url_validation",
            "isaac_validated_downloads"
        ]
        
        # 检查目录是否存在
        existing_dirs = []
        for dir_name in isaac_dirs:
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                existing_dirs.append(dir_path)
        
        print(f"🔍 发现 {len(existing_dirs)} 个待清理的Isaac目录:")
        for dir_path in existing_dirs:
            print(f"  📁 {dir_path}")
        
        return existing_dirs
    
    def process_file(self, file_path, target_dir):
        """处理单个文件：检查是否存在，决定删除还是移动"""
        file_hash = self.calculate_file_hash(file_path)
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        # 检查文件是否已存在（通过哈希值）
        if file_hash and file_hash in self.k_vault_file_hashes:
            # 文件已存在，删除原文件
            existing_file = self.k_vault_file_hashes[file_hash]
            file_path.unlink()
            
            self.stats["deleted_files"].append({
                "original_path": str(file_path),
                "existing_in_kvault": existing_file,
                "size_mb": round(file_size_mb, 2),
                "hash": file_hash
            })
            self.stats["total_freed_mb"] += file_size_mb
            
            print(f"    🗑️  删除重复文件: {file_path.name} ({file_size_mb:.1f} MB)")
            return "deleted"
        
        # 检查文件名是否已存在（备用检查）
        elif file_path.name.lower() in self.k_vault_file_names:
            # 文件名已存在，但哈希不同，生成新名称
            counter = 1
            new_name = file_path.name
            while new_name.lower() in self.k_vault_file_names:
                name_parts = file_path.name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{file_path.name}_{counter}"
                counter += 1
            
            # 移动文件到目标目录
            target_path = target_dir / new_name
            shutil.move(str(file_path), str(target_path))
            
            # 更新索引
            if file_hash:
                self.k_vault_file_hashes[file_hash] = str(target_path)
            self.k_vault_file_names.add(new_name.lower())
            
            self.stats["moved_files"].append({
                "original_path": str(file_path),
                "new_path": str(target_path),
                "size_mb": round(file_size_mb, 2),
                "renamed": True
            })
            self.stats["total_moved_mb"] += file_size_mb
            
            print(f"    📦 移动文件(重命名): {file_path.name} -> {new_name} ({file_size_mb:.1f} MB)")
            return "moved"
        
        else:
            # 文件不存在，直接移动
            target_path = target_dir / file_path.name
            shutil.move(str(file_path), str(target_path))
            
            # 更新索引
            if file_hash:
                self.k_vault_file_hashes[file_hash] = str(target_path)
            self.k_vault_file_names.add(file_path.name.lower())
            
            self.stats["moved_files"].append({
                "original_path": str(file_path),
                "new_path": str(target_path),
                "size_mb": round(file_size_mb, 2),
                "renamed": False
            })
            self.stats["total_moved_mb"] += file_size_mb
            
            print(f"    📦 移动文件: {file_path.name} ({file_size_mb:.1f} MB)")
            return "moved"
    
    def process_directory(self, dir_path):
        """处理单个目录"""
        print(f"\n🔄 处理目录: {dir_path}")
        
        dir_stats = {
            "directory": str(dir_path),
            "pdf_deleted": 0,
            "pdf_moved": 0,
            "md_deleted": 0,
            "md_moved": 0,
            "other_files": 0
        }
        
        # 查找所有文件
        all_files = []
        
        # 递归查找PDF和Markdown文件
        for pattern in ["**/*.pdf", "**/*.md"]:
            all_files.extend(dir_path.glob(pattern))
        
        if not all_files:
            print(f"  ⚪ 跳过: 目录中无PDF/Markdown文件")
            # 如果目录为空或只有其他类型文件，可以考虑删除整个目录
            self.try_remove_empty_directory(dir_path)
            return dir_stats
        
        print(f"  📄 发现 {len(all_files)} 个文件")
        
        # 处理每个文件
        for file_path in all_files:
            try:
                if file_path.suffix.lower() == '.pdf':
                    result = self.process_file(file_path, self.k_vault_pdfs)
                    if result == "deleted":
                        dir_stats["pdf_deleted"] += 1
                    elif result == "moved":
                        dir_stats["pdf_moved"] += 1
                        
                elif file_path.suffix.lower() == '.md':
                    result = self.process_file(file_path, self.k_vault_markdown)
                    if result == "deleted":
                        dir_stats["md_deleted"] += 1
                    elif result == "moved":
                        dir_stats["md_moved"] += 1
                
            except Exception as e:
                print(f"    ❌ 处理失败 {file_path.name}: {e}")
                self.stats["skipped_files"].append({
                    "path": str(file_path),
                    "error": str(e)
                })
        
        # 处理完成后尝试删除空目录
        self.try_remove_empty_directory(dir_path)
        
        total_processed = dir_stats["pdf_deleted"] + dir_stats["pdf_moved"] + dir_stats["md_deleted"] + dir_stats["md_moved"]
        print(f"  ✅ 完成: 删除{dir_stats['pdf_deleted']+dir_stats['md_deleted']}个, 移动{dir_stats['pdf_moved']+dir_stats['md_moved']}个")
        
        self.stats["processed_directories"].append(dir_stats)
        return dir_stats
    
    def try_remove_empty_directory(self, dir_path):
        """尝试删除空目录"""
        try:
            # 检查目录是否为空或只包含空的子目录
            if dir_path.exists() and dir_path.is_dir():
                # 获取所有内容
                contents = list(dir_path.rglob("*"))
                # 过滤掉目录，只看文件
                files = [item for item in contents if item.is_file()]
                
                if not files:
                    # 目录为空，可以删除
                    shutil.rmtree(dir_path)
                    print(f"  🗑️  删除空目录: {dir_path}")
                    return True
        except Exception as e:
            print(f"  ⚠️  无法删除目录 {dir_path}: {e}")
        
        return False
    
    def smart_cleanup(self):
        """执行智能清理"""
        print("🚀 开始Isaac文档智能清理...")
        
        # 查找所有Isaac目录
        isaac_dirs = self.find_isaac_directories()
        
        if not isaac_dirs:
            print("❌ 未找到需要清理的Isaac目录")
            return
        
        print(f"\n📦 开始处理 {len(isaac_dirs)} 个目录...")
        
        for dir_path in isaac_dirs:
            self.process_directory(dir_path)
        
        # 生成清理报告
        self.generate_cleanup_report()
    
    def generate_cleanup_report(self):
        """生成清理报告"""
        print(f"\n🎉 智能清理完成!")
        print(f"📊 清理统计:")
        print(f"  🗑️  删除重复文件: {len(self.stats['deleted_files'])} 个")
        print(f"  📦 移动新文件: {len(self.stats['moved_files'])} 个")
        print(f"  ⚠️  跳过文件: {len(self.stats['skipped_files'])} 个")
        print(f"  💾 释放空间: {self.stats['total_freed_mb']:.1f} MB")
        print(f"  📁 新增内容: {self.stats['total_moved_mb']:.1f} MB")
        
        # 按目录统计
        print(f"\n📊 按目录统计:")
        for dir_stat in self.stats["processed_directories"]:
            dir_name = Path(dir_stat["directory"]).name
            total_deleted = dir_stat["pdf_deleted"] + dir_stat["md_deleted"]
            total_moved = dir_stat["pdf_moved"] + dir_stat["md_moved"]
            print(f"  📂 {dir_name}: 删除{total_deleted}个, 移动{total_moved}个")
        
        # 保存详细报告
        report = {
            "清理时间": datetime.now().isoformat(),
            "统计信息": self.stats,
            "K_Vault状态": {
                "总文件数": len(self.k_vault_file_hashes),
                "PDF目录": str(self.k_vault_pdfs),
                "Markdown目录": str(self.k_vault_markdown)
            }
        }
        
        report_file = Path("isaac_smart_cleanup_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 详细报告: {report_file}")
        
        # 显示一些删除的文件示例
        if self.stats["deleted_files"]:
            print(f"\n🗑️  删除的重复文件示例 (前5个):")
            for item in self.stats["deleted_files"][:5]:
                print(f"  ❌ {Path(item['original_path']).name} ({item['size_mb']} MB)")
        
        # 显示一些移动的文件示例
        if self.stats["moved_files"]:
            print(f"\n📦 移动的新文件示例 (前5个):")
            for item in self.stats["moved_files"][:5]:
                original_name = Path(item['original_path']).name
                new_name = Path(item['new_path']).name
                if item.get('renamed', False):
                    print(f"  📁 {original_name} -> {new_name} ({item['size_mb']} MB)")
                else:
                    print(f"  📁 {original_name} ({item['size_mb']} MB)")

def main():
    cleaner = IsaacSmartCleaner()
    cleaner.smart_cleanup()

if __name__ == "__main__":
    main()

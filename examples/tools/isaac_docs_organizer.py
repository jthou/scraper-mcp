#!/usr/bin/env python3
"""
Isaac文档整理工具
将所有Isaac相关的PDF和Markdown文档汇聚到K-Vault/Isaac目录
"""

import os
import shutil
from pathlib import Path
import hashlib
import json
from datetime import datetime
import subprocess

class IsaacDocumentOrganizer:
    def __init__(self):
        self.base_dir = Path(".")
        self.k_vault_dir = Path("K-Vault/Isaac")
        self.pdf_dir = self.k_vault_dir / "pdfs"
        self.markdown_dir = self.k_vault_dir / "markdown"
        
        # 创建目标目录
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计信息
        self.stats = {
            "pdf_files": 0,
            "markdown_files": 0,
            "duplicates_removed": 0,
            "total_size_mb": 0,
            "source_directories": [],
            "files_by_source": {}
        }
        
        # 文件去重用的哈希表
        self.file_hashes = {}
        
    def calculate_file_hash(self, file_path):
        """计算文件的MD5哈希值用于去重"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def find_isaac_directories(self):
        """查找所有Isaac相关的目录"""
        isaac_dirs = []
        
        # 查找包含isaac的目录名
        for item in self.base_dir.iterdir():
            if item.is_dir() and 'isaac' in item.name.lower():
                isaac_dirs.append(item)
        
        # 查找data目录下的isaac相关目录
        data_dir = self.base_dir / "data"
        if data_dir.exists():
            for item in data_dir.iterdir():
                if item.is_dir() and 'isaac' in item.name.lower():
                    isaac_dirs.append(item)
        
        print(f"🔍 发现 {len(isaac_dirs)} 个Isaac相关目录:")
        for dir_path in isaac_dirs:
            print(f"  📁 {dir_path}")
        
        return isaac_dirs
    
    def organize_pdfs_from_directory(self, source_dir):
        """从指定目录整理PDF文件"""
        pdf_count = 0
        
        # 查找PDF文件
        pdf_files = []
        
        # 检查pdfs子目录
        pdfs_subdir = source_dir / "pdfs"
        if pdfs_subdir.exists():
            pdf_files.extend(pdfs_subdir.glob("*.pdf"))
        
        # 检查根目录
        pdf_files.extend(source_dir.glob("*.pdf"))
        
        # 递归查找所有PDF文件
        for pdf_file in source_dir.rglob("*.pdf"):
            if pdf_file not in pdf_files:
                pdf_files.append(pdf_file)
        
        if not pdf_files:
            return 0
        
        print(f"  📄 发现 {len(pdf_files)} 个PDF文件")
        
        source_stats = {
            "directory": str(source_dir),
            "pdf_count": 0,
            "size_mb": 0,
            "files": []
        }
        
        for pdf_file in pdf_files:
            try:
                # 计算文件哈希
                file_hash = self.calculate_file_hash(pdf_file)
                
                if file_hash and file_hash in self.file_hashes:
                    print(f"    🔄 跳过重复文件: {pdf_file.name}")
                    self.stats["duplicates_removed"] += 1
                    continue
                
                # 生成新的文件名，包含来源信息
                source_name = source_dir.name.replace('_', '-')
                new_filename = f"{source_name}_{pdf_file.name}"
                
                # 如果文件名太长，使用哈希缩短
                if len(new_filename) > 100:
                    file_ext = pdf_file.suffix
                    name_part = new_filename[:80]
                    hash_part = file_hash[:8] if file_hash else "unknown"
                    new_filename = f"{name_part}_{hash_part}{file_ext}"
                
                target_path = self.pdf_dir / new_filename
                
                # 避免文件名冲突
                counter = 1
                while target_path.exists():
                    name_without_ext = target_path.stem
                    ext = target_path.suffix
                    target_path = self.pdf_dir / f"{name_without_ext}_{counter}{ext}"
                    counter += 1
                
                # 复制文件
                shutil.copy2(pdf_file, target_path)
                
                # 记录文件信息
                file_size = pdf_file.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                
                source_stats["files"].append({
                    "original_name": pdf_file.name,
                    "new_name": target_path.name,
                    "size_mb": round(file_size_mb, 2)
                })
                
                source_stats["pdf_count"] += 1
                source_stats["size_mb"] += file_size_mb
                
                if file_hash:
                    self.file_hashes[file_hash] = str(target_path)
                
                pdf_count += 1
                self.stats["pdf_files"] += 1
                self.stats["total_size_mb"] += file_size_mb
                
                print(f"    ✅ {pdf_file.name} -> {target_path.name}")
                
            except Exception as e:
                print(f"    ❌ 复制失败 {pdf_file.name}: {e}")
        
        self.stats["files_by_source"][str(source_dir)] = source_stats
        return pdf_count
    
    def organize_markdown_files(self, source_dir):
        """整理Markdown文件"""
        markdown_count = 0
        
        # 查找Markdown文件
        markdown_files = []
        markdown_files.extend(source_dir.glob("*.md"))
        markdown_files.extend(source_dir.rglob("*.md"))
        
        if not markdown_files:
            return 0
        
        print(f"  📝 发现 {len(markdown_files)} 个Markdown文件")
        
        for md_file in markdown_files:
            try:
                # 生成新的文件名
                source_name = source_dir.name.replace('_', '-')
                new_filename = f"{source_name}_{md_file.name}"
                target_path = self.markdown_dir / new_filename
                
                # 避免文件名冲突
                counter = 1
                while target_path.exists():
                    name_without_ext = target_path.stem
                    ext = target_path.suffix
                    target_path = self.markdown_dir / f"{name_without_ext}_{counter}{ext}"
                    counter += 1
                
                # 复制文件
                shutil.copy2(md_file, target_path)
                markdown_count += 1
                self.stats["markdown_files"] += 1
                
                print(f"    ✅ {md_file.name} -> {target_path.name}")
                
            except Exception as e:
                print(f"    ❌ 复制失败 {md_file.name}: {e}")
        
        return markdown_count
    
    def organize_all_isaac_docs(self):
        """整理所有Isaac文档"""
        print("🚀 开始整理Isaac文档到K-Vault...")
        print(f"📁 目标目录: {self.k_vault_dir}")
        print()
        
        # 查找所有Isaac目录
        isaac_dirs = self.find_isaac_directories()
        
        if not isaac_dirs:
            print("❌ 未找到Isaac相关目录")
            return
        
        print(f"\n📦 开始整理文档...")
        
        for source_dir in isaac_dirs:
            print(f"\n🔄 处理目录: {source_dir}")
            self.stats["source_directories"].append(str(source_dir))
            
            # 整理PDF文件
            pdf_count = self.organize_pdfs_from_directory(source_dir)
            
            # 整理Markdown文件
            md_count = self.organize_markdown_files(source_dir)
            
            total_files = pdf_count + md_count
            if total_files > 0:
                print(f"  ✅ 完成: {pdf_count} PDF + {md_count} Markdown = {total_files} 文件")
            else:
                print(f"  ⚪ 跳过: 未找到文档文件")
        
        # 生成报告
        self.generate_organization_report()
    
    def generate_organization_report(self):
        """生成整理报告"""
        print(f"\n🎉 Isaac文档整理完成!")
        print(f"📊 整理统计:")
        print(f"  📄 PDF文件: {self.stats['pdf_files']} 个")
        print(f"  📝 Markdown文件: {self.stats['markdown_files']} 个")
        print(f"  🔄 去重文件: {self.stats['duplicates_removed']} 个")
        print(f"  💾 总大小: {self.stats['total_size_mb']:.1f} MB")
        print(f"  📁 源目录: {len(self.stats['source_directories'])} 个")
        
        print(f"\n📁 文档位置:")
        print(f"  📄 PDF文档: {self.pdf_dir}")
        print(f"  📝 Markdown文档: {self.markdown_dir}")
        
        # 按来源分组统计
        print(f"\n📊 按来源统计:")
        for source, stats in self.stats["files_by_source"].items():
            if stats["pdf_count"] > 0:
                print(f"  📂 {Path(source).name}: {stats['pdf_count']} PDF, {stats['size_mb']:.1f} MB")
        
        # 保存详细报告
        report = {
            "整理时间": datetime.now().isoformat(),
            "统计信息": self.stats,
            "目标目录": {
                "PDF目录": str(self.pdf_dir),
                "Markdown目录": str(self.markdown_dir)
            }
        }
        
        report_file = self.k_vault_dir / "isaac_docs_organization_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 详细报告: {report_file}")
        
        # 生成索引文件
        self.generate_index_files()
    
    def generate_index_files(self):
        """生成索引文件"""
        # PDF索引
        pdf_index_content = f"""# Isaac PDF文档索引

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计信息
- 总PDF文件: {self.stats['pdf_files']} 个
- 总大小: {self.stats['total_size_mb']:.1f} MB
- 去重文件: {self.stats['duplicates_removed']} 个

## 文件列表
"""
        
        # 按来源分组列出PDF文件
        for source, stats in self.stats["files_by_source"].items():
            if stats["pdf_count"] > 0:
                pdf_index_content += f"\n### {Path(source).name} ({stats['pdf_count']} 文件, {stats['size_mb']:.1f} MB)\n"
                for file_info in stats["files"]:
                    pdf_index_content += f"- [{file_info['new_name']}](./pdfs/{file_info['new_name']}) ({file_info['size_mb']:.1f} MB)\n"
        
        pdf_index_file = self.k_vault_dir / "PDF_INDEX.md"
        with open(pdf_index_file, 'w', encoding='utf-8') as f:
            f.write(pdf_index_content)
        
        # Markdown索引
        md_files = list(self.markdown_dir.glob("*.md"))
        md_index_content = f"""# Isaac Markdown文档索引

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计信息
- 总Markdown文件: {len(md_files)} 个

## 文件列表
"""
        
        for md_file in sorted(md_files):
            md_index_content += f"- [{md_file.name}](./markdown/{md_file.name})\n"
        
        md_index_file = self.k_vault_dir / "MARKDOWN_INDEX.md"
        with open(md_index_file, 'w', encoding='utf-8') as f:
            f.write(md_index_content)
        
        print(f"📋 PDF索引: {pdf_index_file}")
        print(f"📋 Markdown索引: {md_index_file}")

def main():
    organizer = IsaacDocumentOrganizer()
    organizer.organize_all_isaac_docs()

if __name__ == "__main__":
    main()

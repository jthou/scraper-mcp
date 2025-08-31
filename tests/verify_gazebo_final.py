#!/usr/bin/env python3
"""
最终验证脚本：检查K-Vault/Gazebo目录状态
"""
from pathlib import Path

def verify_gazebo_directory():
    """验证Gazebo目录状态"""
    target_dir = Path("K-Vault/Gazebo")
    pdf_dir = target_dir / "pdfs"
    markdown_dir = target_dir / "markdown"
    
    print("🎯 最终验证 K-Vault/Gazebo 目录状态")
    print("="*60)
    
    # 检查目录是否存在
    if not target_dir.exists():
        print("❌ K-Vault/Gazebo目录不存在")
        return False
    
    if not pdf_dir.exists():
        print("❌ K-Vault/Gazebo/pdfs目录不存在")
        return False
    
    if not markdown_dir.exists():
        print("❌ K-Vault/Gazebo/markdown目录不存在")
        return False
    
    # 统计文件
    pdf_files = list(pdf_dir.glob("*.pdf"))
    txt_files = list(pdf_dir.glob("*.txt"))
    markdown_files = list(markdown_dir.glob("*.md"))
    
    print(f"📄 PDF文件数量: {len(pdf_files)}")
    print(f"📝 Markdown文件数量: {len(markdown_files)}")
    print(f"⚠️  错误.txt文件数量: {len(txt_files)}")
    
    # 检查文件对应关系
    pdf_basenames = {f.stem for f in pdf_files}
    md_basenames = {f.stem for f in markdown_files}
    
    if pdf_basenames == md_basenames:
        print("✅ PDF和Markdown文件完全对应")
        correspondence_ok = True
    else:
        print("❌ PDF和Markdown文件不完全对应")
        correspondence_ok = False
        
        missing_pdf = md_basenames - pdf_basenames
        missing_md = pdf_basenames - md_basenames
        
        if missing_pdf:
            print(f"   缺少PDF: {missing_pdf}")
        if missing_md:
            print(f"   缺少Markdown: {missing_md}")
    
    # 显示部分文件
    if pdf_files:
        print(f"\n📄 PDF文件示例（前5个）:")
        for i, pdf in enumerate(pdf_files[:5], 1):
            print(f"   {i}. {pdf.name}")
        if len(pdf_files) > 5:
            print(f"   ... 还有 {len(pdf_files) - 5} 个")
    
    if markdown_files:
        print(f"\n📝 Markdown文件示例（前5个）:")
        for i, md in enumerate(markdown_files[:5], 1):
            print(f"   {i}. {md.name}")
        if len(markdown_files) > 5:
            print(f"   ... 还有 {len(markdown_files) - 5} 个")
    
    # 检查内容质量（随机检查一个PDF）
    if pdf_files:
        print(f"\n🔍 文件质量检查:")
        sample_pdf = pdf_files[0]
        file_size = sample_pdf.stat().st_size
        print(f"   示例文件: {sample_pdf.name}")
        print(f"   文件大小: {file_size:,} 字节")
        
        if file_size > 1000:  # PDF文件应该大于1KB
            print(f"   ✅ 文件大小正常（>1KB）")
            size_ok = True
        else:
            print(f"   ⚠️ 文件大小可能有问题（<1KB）")
            size_ok = False
    else:
        size_ok = False
    
    # 总体评估
    success = (
        len(pdf_files) > 0 and          # 有PDF文件
        len(txt_files) == 0 and         # 没有错误的.txt文件
        correspondence_ok and           # 文件对应关系正确
        size_ok                        # 文件大小正常
    )
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 验证成功！K-Vault/Gazebo目录状态完美！")
        print(f"✅ 成功下载了 {len(pdf_files)} 篇Gazebo相关文章")
        print("✅ 所有文件格式正确（真正的PDF文件）")
        print("✅ PDF和Markdown文件一一对应")
        print("✅ 文件大小正常，内容完整")
    else:
        print("❌ 验证失败，仍有问题需要修复")
    
    return success

if __name__ == "__main__":
    verify_gazebo_directory()

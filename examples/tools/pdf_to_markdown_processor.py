#!/usr/bin/env python3
"""
PDF转Markdown处理器
将Isaac Sim PDF文件转换为高质量的Markdown文档
"""

import os
import sys
from pathlib import Path
import pymupdf  # PyMuPDF
from datetime import datetime
import json
import re

class PDFToMarkdownProcessor:
    def __init__(self, pdf_dir="isaac_sim_pdfs/pdfs", output_dir="isaac_sim_pdfs/markdowns"):
        self.pdf_dir = Path(pdf_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.conversion_log = []
        
    def log_conversion(self, action, file="", status="", details=""):
        """记录转换日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "file": file,
            "status": status,
            "details": details
        }
        self.conversion_log.append(log_entry)
        print(f"[{log_entry['timestamp']}] {action}: {status} - {file}")
    
    def extract_text_from_pdf(self, pdf_path):
        """从PDF提取文本内容"""
        try:
            doc = pymupdf.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # 简单的文本清理
                text = self.clean_extracted_text(text)
                full_text += f"\n\n--- 第{page_num + 1}页 ---\n\n{text}"
            
            doc.close()
            return full_text
            
        except Exception as e:
            self.log_conversion("PDF读取失败", str(pdf_path), "错误", str(e))
            return ""
    
    def clean_extracted_text(self, text):
        """清理提取的文本"""
        # 移除多余的空行
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # 移除页眉页脚（简单规则）
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # 跳过可能是页眉页脚的短行
            if len(line) < 3:
                continue
            # 跳过只包含数字的行（页码）
            if line.isdigit():
                continue
                
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def text_to_markdown(self, text, pdf_filename):
        """将提取的文本转换为Markdown格式"""
        lines = text.split('\n')
        markdown_lines = []
        
        # 添加文档头部
        markdown_lines.extend([
            f"# {pdf_filename} - Isaac Sim文档",
            "",
            f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> **源文件**: {pdf_filename}",
            f"> **处理方式**: PDF→Markdown自动转换",
            "",
            "---",
            ""
        ])
        
        current_section = ""
        in_code_block = False
        
        for line in lines:
            line = line.strip()
            
            if not line:
                markdown_lines.append("")
                continue
            
            # 检测标题（简单规则）
            if self.is_likely_heading(line):
                level = self.detect_heading_level(line)
                markdown_lines.append(f"{'#' * level} {line}")
                markdown_lines.append("")
                
            # 检测代码块
            elif line.startswith("```") or line.endswith("```"):
                markdown_lines.append(line)
                in_code_block = not in_code_block
                
            # 检测列表项
            elif line.startswith(("- ", "• ", "* ")):
                markdown_lines.append(f"- {line[2:]}")
                
            # 检测数字列表
            elif re.match(r'^\d+[\.\)]\s+', line):
                num_match = re.match(r'^(\d+)[\.\)]\s+(.+)', line)
                if num_match:
                    markdown_lines.append(f"{num_match.group(1)}. {num_match.group(2)}")
                    
            # 普通段落
            else:
                if not in_code_block:
                    # 加粗重要关键词
                    line = self.highlight_keywords(line)
                markdown_lines.append(line)
        
        return '\n'.join(markdown_lines)
    
    def is_likely_heading(self, line):
        """判断行是否可能是标题"""
        # 简单的标题检测规则
        if len(line) < 3:
            return False
            
        # 全大写的短行
        if line.isupper() and len(line) < 50:
            return True
            
        # 包含常见标题关键词
        heading_keywords = [
            "Installation", "Setup", "Getting Started", "Tutorial", "Guide",
            "Overview", "Introduction", "Configuration", "Usage", "API",
            "Examples", "Reference", "Documentation", "Features"
        ]
        
        for keyword in heading_keywords:
            if keyword.lower() in line.lower():
                return True
                
        return False
    
    def detect_heading_level(self, line):
        """检测标题级别"""
        if len(line) < 10:
            return 2
        elif "installation" in line.lower() or "setup" in line.lower():
            return 2
        elif "tutorial" in line.lower() or "guide" in line.lower():
            return 3
        else:
            return 4
    
    def highlight_keywords(self, line):
        """高亮重要关键词"""
        isaac_keywords = [
            "Isaac Sim", "Isaac Lab", "Omniverse", "NVIDIA", "PyTorch", 
            "reinforcement learning", "simulation", "robotics", "gymnasium"
        ]
        
        for keyword in isaac_keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            line = pattern.sub(f"**{keyword}**", line)
            
        return line
    
    def process_pdf_file(self, pdf_path):
        """处理单个PDF文件"""
        self.log_conversion("开始处理PDF", pdf_path.name, "进行中")
        
        try:
            # 提取文本
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text.strip():
                self.log_conversion("PDF内容为空", pdf_path.name, "警告")
                return None
            
            # 转换为Markdown
            markdown_content = self.text_to_markdown(text, pdf_path.name)
            
            # 保存Markdown文件
            markdown_filename = pdf_path.stem + ".md"
            markdown_path = self.output_dir / markdown_filename
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.log_conversion("Markdown生成成功", pdf_path.name, "成功", f"输出: {markdown_filename}")
            
            return {
                'pdf_file': pdf_path.name,
                'markdown_file': markdown_filename,
                'markdown_path': markdown_path,
                'text_length': len(text),
                'lines_count': len(markdown_content.split('\n'))
            }
            
        except Exception as e:
            self.log_conversion("PDF处理失败", pdf_path.name, "错误", str(e))
            return None
    
    def process_all_pdfs(self):
        """处理所有PDF文件"""
        print(f"🚀 开始PDF转Markdown处理")
        print(f"📁 PDF目录: {self.pdf_dir.absolute()}")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        if not pdf_files:
            print("❌ 未找到PDF文件")
            return []
        
        print(f"📄 找到 {len(pdf_files)} 个PDF文件")
        
        results = []
        
        for pdf_file in pdf_files:
            result = self.process_pdf_file(pdf_file)
            if result:
                results.append(result)
        
        # 生成处理报告
        self.generate_conversion_report(results)
        
        return results
    
    def generate_conversion_report(self, results):
        """生成转换报告"""
        report_path = self.output_dir / "conversion_report.md"
        
        report_content = f"""# PDF转Markdown转换报告

## 转换概况
- **转换时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **处理PDF数量**: {len(results)}
- **成功转换**: {len([r for r in results if r])}
- **输出目录**: {self.output_dir.absolute()}

## 转换结果

"""
        
        for i, result in enumerate(results, 1):
            report_content += f"""### {i}. {result['pdf_file']}
- **Markdown文件**: {result['markdown_file']}
- **文本长度**: {result['text_length']:,} 字符
- **行数**: {result['lines_count']:,} 行
- **状态**: ✅ 成功转换

"""
        
        report_content += f"""
## 文件清单
```
{self.output_dir.name}/
"""
        
        for result in results:
            report_content += f"├── {result['markdown_file']}\n"
        
        report_content += "└── conversion_report.md\n```\n"
        
        # 保存转换日志
        log_path = self.output_dir / f"conversion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.conversion_log, f, ensure_ascii=False, indent=2)
        
        report_content += f"\n## 详细日志\n转换日志已保存到: {log_path.name}\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 转换报告已生成: {report_path}")

def main():
    """主函数"""
    # 检查依赖
    try:
        import pymupdf
    except ImportError:
        print("❌ 缺少依赖: pip install pymupdf")
        sys.exit(1)
    
    processor = PDFToMarkdownProcessor()
    results = processor.process_all_pdfs()
    
    print(f"\n🎉 转换完成！")
    print(f"📄 处理了 {len(results)} 个PDF文件")
    print(f"📁 Markdown文件保存在: {processor.output_dir.absolute()}")
    
    if results:
        total_chars = sum(r['text_length'] for r in results)
        total_lines = sum(r['lines_count'] for r in results)
        print(f"📊 总计提取: {total_chars:,} 字符, {total_lines:,} 行")

if __name__ == "__main__":
    main()

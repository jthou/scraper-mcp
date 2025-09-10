#!/usr/bin/env python3
"""
从已下载的Isaac Lab内容中提取所有链接
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class LocalLinkExtractor:
    def __init__(self):
        self.isaac_downloads_dir = Path("isaac_sim_downloads")
        self.output_dir = Path("isaac_complete_links")
        self.output_dir.mkdir(exist_ok=True)
        
        self.all_links = set()
        self.page_info = []
    
    def extract_links_from_html_file(self, html_file):
        """从单个HTML文件提取链接"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 获取页面标题
            title = soup.title.string if soup.title else "无标题"
            
            # 提取所有链接
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                text = a_tag.get_text(strip=True)
                
                # 转换为绝对URL
                if href.startswith('/'):
                    if 'isaac-sim.github.io' in str(html_file):
                        base_url = "https://isaac-sim.github.io"
                    elif 'leggedrobotics.github.io' in str(html_file):
                        base_url = "https://leggedrobotics.github.io"
                    else:
                        continue
                    absolute_url = base_url + href
                elif href.startswith('http'):
                    absolute_url = href
                else:
                    # 相对链接
                    if 'isaac-sim.github.io' in str(html_file):
                        base_url = "https://isaac-sim.github.io/IsaacLab/"
                    elif 'leggedrobotics.github.io' in str(html_file):
                        base_url = "https://leggedrobotics.github.io/legged_gym/"
                    else:
                        continue
                    absolute_url = urljoin(base_url, href)
                
                # 过滤有效的Isaac相关链接
                if self.is_isaac_related_link(absolute_url):
                    links.append({
                        'url': absolute_url,
                        'text': text[:100],
                        'source_file': str(html_file)
                    })
                    self.all_links.add(absolute_url)
            
            page_info = {
                'file': str(html_file),
                'title': title,
                'links_count': len(links),
                'links': links
            }
            
            return page_info
            
        except Exception as e:
            print(f"❌ 处理文件失败 {html_file}: {str(e)}")
            return None
    
    def is_isaac_related_link(self, url):
        """判断是否为Isaac相关的有效链接"""
        parsed = urlparse(url)
        
        # 必须是目标域名
        valid_domains = ['isaac-sim.github.io', 'leggedrobotics.github.io', 'zhengyiluo.github.io']
        if not any(domain in parsed.netloc for domain in valid_domains):
            return False
        
        # 必须包含Isaac相关路径
        isaac_paths = ['/IsaacLab/', '/legged_gym/', '/PHC/']
        if not any(path in parsed.path for path in isaac_paths):
            return False
        
        # 排除不需要的文件类型
        excluded_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.zip', '.tar.gz']
        if any(parsed.path.lower().endswith(ext) for ext in excluded_extensions):
            return False
        
        # 排除锚点链接
        if '#' in url and len(parsed.fragment) > 0:
            return False
        
        return True
    
    def scan_downloaded_content(self):
        """扫描已下载的内容提取链接"""
        print("🔍 扫描已下载的Isaac Sim内容...")
        
        html_files = []
        
        # 搜索所有可能的Isaac相关HTML文件
        search_patterns = [
            "./isaac_sim_downloads/**/isaac-sim.github.io/**/*.html",
            "./isaac_sim_downloads/**/leggedrobotics.github.io/**/*.html", 
            "./isaac_sim_downloads/**/zhengyiluo.github.io/**/*.html",
            "./**/isaac-sim.github.io/**/*.html",
            "./**/leggedrobotics.github.io/**/*.html",
            "./isaac-sim.github.io/**/*.html",
            "./leggedrobotics.github.io/**/*.html"
        ]
        
        for pattern in search_patterns:
            found_files = list(Path(".").glob(pattern))
            html_files.extend(found_files)
            if found_files:
                print(f"📁 在 {pattern} 找到 {len(found_files)} 个文件")
        
        # 去重
        html_files = list(set(html_files))
        print(f"📄 总计找到 {len(html_files)} 个HTML文件")
        
        # 处理每个HTML文件
        for html_file in html_files:
            print(f"🔗 提取链接: {html_file.name}")
            page_info = self.extract_links_from_html_file(html_file)
            if page_info:
                self.page_info.append(page_info)
        
        return len(self.all_links)
    
    def categorize_links(self):
        """对链接进行分类"""
        categorized = {
            'installation': [],
            'tutorials': [],
            'api': [],
            'guides': [],
            'features': [],
            'examples': [],
            'other': []
        }
        
        for link in self.all_links:
            link_lower = link.lower()
            
            if any(keyword in link_lower for keyword in ['install', 'setup', 'quickstart']):
                categorized['installation'].append(link)
            elif any(keyword in link_lower for keyword in ['tutorial', 'walkthrough']):
                categorized['tutorials'].append(link)
            elif any(keyword in link_lower for keyword in ['api', 'reference']):
                categorized['api'].append(link)
            elif any(keyword in link_lower for keyword in ['guide', 'how-to']):
                categorized['guides'].append(link)
            elif any(keyword in link_lower for keyword in ['feature', 'overview']):
                categorized['features'].append(link)
            elif any(keyword in link_lower for keyword in ['example', 'demo']):
                categorized['examples'].append(link)
            else:
                categorized['other'].append(link)
        
        return categorized
    
    def generate_download_queue(self):
        """生成优先级下载队列"""
        categorized = self.categorize_links()
        
        # 定义优先级顺序
        priority_order = ['installation', 'tutorials', 'guides', 'features', 'api', 'examples', 'other']
        
        download_queue = []
        
        for category in priority_order:
            links = categorized[category]
            for i, link in enumerate(links):
                download_queue.append({
                    'url': link,
                    'category': category,
                    'priority': len(priority_order) - priority_order.index(category),
                    'filename': f"{category}_{i+1:03d}"
                })
        
        return download_queue
    
    def save_results(self):
        """保存提取结果"""
        # 保存所有链接
        all_links_file = self.output_dir / "all_isaac_links.json"
        with open(all_links_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.all_links), f, ensure_ascii=False, indent=2)
        
        # 保存分类链接
        categorized = self.categorize_links()
        categorized_file = self.output_dir / "categorized_links.json"
        with open(categorized_file, 'w', encoding='utf-8') as f:
            json.dump(categorized, f, ensure_ascii=False, indent=2)
        
        # 保存下载队列
        download_queue = self.generate_download_queue()
        queue_file = self.output_dir / "download_queue.json"
        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump(download_queue, f, ensure_ascii=False, indent=2)
        
        # 生成报告
        self.generate_report(categorized, download_queue)
        
        return {
            'all_links': len(self.all_links),
            'categorized': categorized,
            'download_queue': len(download_queue)
        }
    
    def generate_report(self, categorized, download_queue):
        """生成链接提取报告"""
        report_file = self.output_dir / "link_extraction_report.md"
        
        report_content = f"""# Isaac Sim 链接提取报告

## 提取概况
- **提取时间**: {Path().cwd().name}
- **处理文件数**: {len(self.page_info)}
- **总链接数**: {len(self.all_links)}
- **分类数**: {len(categorized)}

## 链接分类统计

"""
        
        for category, links in categorized.items():
            if links:
                report_content += f"### {category.upper()} ({len(links)}个)\n"
                for i, link in enumerate(links[:5], 1):  # 只显示前5个
                    report_content += f"{i}. {link}\n"
                if len(links) > 5:
                    report_content += f"... 还有 {len(links) - 5} 个链接\n"
                report_content += "\n"
        
        report_content += f"""
## 下载队列

已生成优先级下载队列，共 {len(download_queue)} 个页面：

### 优先级说明
1. **Installation** - 安装和设置相关 (最高优先级)
2. **Tutorials** - 教程和演练
3. **Guides** - 指南和How-to文档  
4. **Features** - 功能和概览
5. **API** - API参考文档
6. **Examples** - 示例和演示
7. **Other** - 其他文档

## 输出文件
- `all_isaac_links.json` - 所有提取的链接
- `categorized_links.json` - 分类后的链接
- `download_queue.json` - 优先级下载队列

## 下一步
运行批量下载器：
```bash
python isaac_batch_downloader.py
```
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 提取报告已生成: {report_file}")

def main():
    """主函数"""
    extractor = LocalLinkExtractor()
    
    # 扫描已下载内容
    total_links = extractor.scan_downloaded_content()
    
    if total_links == 0:
        print("❌ 未找到有效链接，请先运行wget下载或检查下载目录")
        return
    
    # 保存结果
    results = extractor.save_results()
    
    print(f"\n🎉 链接提取完成！")
    print(f"🔗 总计提取 {results['all_links']} 个有效链接")
    print(f"📁 结果保存在: {extractor.output_dir.absolute()}")
    
    # 显示分类统计
    print(f"\n📊 分类统计:")
    for category, links in results['categorized'].items():
        if links:
            print(f"  {category}: {len(links)} 个链接")

if __name__ == "__main__":
    main()

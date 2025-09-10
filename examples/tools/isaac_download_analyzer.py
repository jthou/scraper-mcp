#!/usr/bin/env python3
"""
Isaac Sim 下载完成度分析器
检查还有哪些内容没有下载完
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import re

class IsaacDownloadAnalyzer:
    def __init__(self):
        self.base_dir = Path(".")
        self.downloaded_files = set()
        self.failed_urls = set()
        self.analysis_results = {}
        
    def scan_downloaded_files(self):
        """扫描所有已下载的文件"""
        print("🔍 扫描已下载的文件...")
        
        download_dirs = [
            "isaac_unlimited_downloads/pdfs",
            "isaac_complete_pdfs/pdfs", 
            "isaac_smart_crawl/pdfs",
            "isaac_sim_pdfs/pdfs"
        ]
        
        total_files = 0
        total_size = 0
        
        for dir_path in download_dirs:
            full_path = self.base_dir / dir_path
            if full_path.exists():
                files = list(full_path.glob("*.pdf"))
                print(f"  📁 {dir_path}: {len(files)} 个PDF文件")
                
                for file in files:
                    self.downloaded_files.add(file.name)
                    total_files += 1
                    total_size += file.stat().st_size
        
        print(f"📊 总计: {total_files} 个PDF文件, {total_size / 1024 / 1024:.1f} MB")
        return total_files, total_size
    
    def analyze_failed_downloads(self):
        """分析失败的下载"""
        print("\n❌ 分析失败的下载...")
        
        failed_files = [
            "isaac_complete_pdfs/logs/failed_downloads.json",
            "isaac_complete_pdfs/logs/failed_downloads_clean.json"
        ]
        
        failed_by_reason = defaultdict(list)
        
        for file_path in failed_files:
            full_path = self.base_dir / file_path
            if full_path.exists():
                print(f"  📋 读取: {file_path}")
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    try:
                        failed_data = json.load(f)
                        for item in failed_data:
                            url = item.get('url', '')
                            error = item.get('error', 'Unknown error')
                            self.failed_urls.add(url)
                            
                            # 分类错误原因
                            if 'HTTP错误: 404' in error:
                                failed_by_reason['404错误'].append(url)
                            elif 'Timeout' in error:
                                failed_by_reason['超时'].append(url)
                            elif 'PDF文件太小' in error:
                                failed_by_reason['PDF生成失败'].append(url)
                            else:
                                failed_by_reason['其他错误'].append(url)
                    
                    except Exception as e:
                        print(f"    ⚠️ 读取失败: {e}")
        
        print(f"📊 失败统计:")
        for reason, urls in failed_by_reason.items():
            print(f"  {reason}: {len(urls)} 个")
            # 显示前5个示例
            for url in urls[:5]:
                print(f"    - {url}")
            if len(urls) > 5:
                print(f"    ... 还有 {len(urls) - 5} 个")
        
        return failed_by_reason
    
    def identify_missing_content(self):
        """识别可能遗漏的重要内容"""
        print("\n🎯 识别可能遗漏的重要内容...")
        
        # 重要的Isaac Sim主题和关键词
        important_topics = {
            "Isaac Lab教程": [
                "isaac-lab", "isaaclab", "tutorial", "getting-started",
                "installation", "quickstart"
            ],
            "机器人仿真": [
                "robot", "articulation", "joints", "physics", "simulation"
            ],
            "传感器系统": [
                "camera", "sensor", "imu", "lidar", "contact"
            ],
            "强化学习": [
                "rl", "reinforcement", "training", "policy", "environment"
            ],
            "ROS集成": [
                "ros", "ros2", "bridge", "navigation"
            ],
            "Omniverse开发": [
                "omniverse", "kit", "extension", "usd", "nucleus"
            ]
        }
        
        # 分析已下载文件涵盖的主题
        covered_topics = defaultdict(int)
        
        for filename in self.downloaded_files:
            filename_lower = filename.lower()
            for topic, keywords in important_topics.items():
                for keyword in keywords:
                    if keyword in filename_lower:
                        covered_topics[topic] += 1
                        break
        
        print("📈 主题覆盖情况:")
        for topic, keywords in important_topics.items():
            count = covered_topics.get(topic, 0)
            status = "✅" if count > 0 else "⚠️"
            print(f"  {status} {topic}: {count} 个文件")
        
        return covered_topics
    
    def suggest_additional_sources(self):
        """建议额外的下载源"""
        print("\n💡 建议额外的下载源...")
        
        additional_sources = [
            {
                "名称": "NVIDIA Isaac Sim官方文档",
                "URL": "https://docs.omniverse.nvidia.com/isaacsim/latest/",
                "说明": "完整的Isaac Sim官方文档"
            },
            {
                "名称": "Isaac ROS文档",
                "URL": "https://nvidia-isaac-ros.github.io/",
                "说明": "Isaac ROS包的完整文档"
            },
            {
                "名称": "Omniverse Kit开发者文档",
                "URL": "https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/",
                "说明": "Kit框架开发指南"
            },
            {
                "名称": "PhysX文档",
                "URL": "https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/",
                "说明": "物理引擎详细文档"
            },
            {
                "名称": "USD文档",
                "URL": "https://docs.omniverse.nvidia.com/usd/latest/",
                "说明": "Universal Scene Description格式文档"
            }
        ]
        
        for source in additional_sources:
            print(f"  🔗 {source['名称']}")
            print(f"     URL: {source['URL']}")
            print(f"     说明: {source['说明']}")
            print()
    
    def check_specific_missing_content(self):
        """检查特定的可能遗漏内容"""
        print("\n🔍 检查特定可能遗漏的内容...")
        
        # 检查是否有这些重要文件
        important_files_patterns = [
            r".*installation.*guide.*",
            r".*getting.*started.*",
            r".*quick.*start.*",
            r".*tutorial.*intro.*",
            r".*api.*reference.*",
            r".*troubleshooting.*",
            r".*deployment.*",
            r".*configuration.*"
        ]
        
        found_patterns = set()
        
        for filename in self.downloaded_files:
            filename_lower = filename.lower()
            for pattern in important_files_patterns:
                if re.match(pattern, filename_lower):
                    found_patterns.add(pattern)
        
        missing_patterns = set(important_files_patterns) - found_patterns
        
        if missing_patterns:
            print("⚠️ 可能遗漏的重要内容类型:")
            for pattern in missing_patterns:
                print(f"  - {pattern}")
        else:
            print("✅ 重要内容类型基本齐全")
    
    def generate_completion_report(self):
        """生成完成度报告"""
        print("\n📋 生成完成度报告...")
        
        total_files, total_size = self.scan_downloaded_files()
        failed_by_reason = self.analyze_failed_downloads()
        covered_topics = self.identify_missing_content()
        self.check_specific_missing_content()
        self.suggest_additional_sources()
        
        # 估算完成度
        total_attempted = total_files + len(self.failed_urls)
        completion_rate = (total_files / total_attempted * 100) if total_attempted > 0 else 0
        
        report = {
            "下载统计": {
                "成功下载": total_files,
                "文件大小MB": f"{total_size / 1024 / 1024:.1f}",
                "失败下载": len(self.failed_urls),
                "完成率": f"{completion_rate:.1f}%"
            },
            "失败分析": {reason: len(urls) for reason, urls in failed_by_reason.items()},
            "主题覆盖": dict(covered_topics),
            "建议": "查看上述额外下载源以获得更完整的文档集合"
        }
        
        # 保存报告
        report_file = self.base_dir / "isaac_download_completion_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存: {report_file}")
        
        print(f"\n🎉 总结:")
        print(f"  ✅ 成功下载: {total_files} 个PDF文件 ({total_size / 1024 / 1024:.1f} MB)")
        print(f"  ❌ 失败下载: {len(self.failed_urls)} 个URL")
        print(f"  📊 估计完成率: {completion_rate:.1f}%")

def main():
    analyzer = IsaacDownloadAnalyzer()
    analyzer.generate_completion_report()

if __name__ == "__main__":
    main()

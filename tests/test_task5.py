#!/usr/bin/env python3
"""
测试任务5：完善内容下载和文件管理功能
"""
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.web_scraper import WebScraper
from utils.logger import Logger


class Task5Tester:
    """任务5功能测试器"""
    
    def __init__(self):
        self.logger = Logger("任务5测试")
        self.scraper = WebScraper()
        self.test_output_dir = Path("test_output_task5")
    
    async def test_5_1_5_2_filename_cleaning(self):
        """测试5.1-5.2: 文件名清理功能"""
        print("\n" + "="*60)
        print("🧪 测试5.1-5.2: 文件名清理功能")
        print("="*60)
        
        test_titles = [
            "Gazebo仿真教程：从入门到精通",
            "ROS+Gazebo机器人开发指南 | 完整教程",
            "【深度解析】Gazebo物理引擎的工作原理",
            "这是一个非常非常长的标题需要测试长度限制功能的处理能力和效果展示这个标题确实很长很长很长",
            "文件名<>:\"/\\|?*特殊字符测试",
            "",  # 空标题
            "   空格    测试   ",
            "中文，。！？；：""''【】《》（）标点符号"
        ]
        
        all_passed = True
        for i, title in enumerate(test_titles, 1):
            clean_name = self.scraper.clean_filename(title)
            print(f"{i}. 原标题: '{title}'")
            print(f"   文件名: '{clean_name}'")
            print(f"   长度: {len(clean_name)}")
            
            # 验证规则
            if len(clean_name) > 100:
                print(f"   ❌ 文件名长度超限: {len(clean_name)}")
                all_passed = False
            elif any(char in clean_name for char in '<>:"/\\|?*'):
                print(f"   ❌ 包含非法字符")
                all_passed = False
            elif not clean_name:
                print(f"   ❌ 文件名为空")
                all_passed = False
            else:
                print(f"   ✅ 文件名符合规范")
            print()
        
        if all_passed:
            print("✅ 文件名清理功能测试通过")
        else:
            print("❌ 文件名清理功能测试失败")
        
        return all_passed
    
    async def test_5_3_single_download(self):
        """测试5.3: 单个内容下载功能"""
        print("\n" + "="*60)
        print("🧪 测试5.3: 单个内容下载功能")
        print("="*60)
        
        # 先登录
        login_result = await self.scraper.login_zhihu(headless=False)
        if login_result["status"] != "success":
            print(f"❌ 登录失败: {login_result['message']}")
            return False
        
        print("✅ 知乎登录成功")
        
        # 测试URL (知乎首页)
        test_url = "https://www.zhihu.com"
        test_title = "知乎首页测试"
        
        print(f"📥 测试下载: {test_url}")
        print(f"📁 保存目录: {self.test_output_dir}")
        
        result = await self.scraper.download_and_save_content(
            url=test_url,
            output_dir=self.test_output_dir,
            title=test_title
        )
        
        if result["status"] == "success":
            print(f"✅ 下载成功: {result['message']}")
            print(f"📄 文件名: {result['base_name']}")
            print(f"📁 Markdown: {result['files']['markdown']}")
            print(f"📄 PDF: {result['files']['pdf']}")
            
            # 验证文件是否存在
            markdown_path = Path(result['files']['markdown'])
            pdf_path = Path(result['files']['pdf'])
            
            if markdown_path.exists():
                print(f"✅ Markdown文件已创建: {markdown_path}")
            else:
                print(f"❌ Markdown文件未创建: {markdown_path}")
                return False
            
            if pdf_path.exists():
                print(f"✅ PDF文件已创建: {pdf_path}")
            else:
                print(f"❌ PDF文件未创建: {pdf_path}")
                return False
            
            # 验证映射文件
            mapping_file = self.test_output_dir / "file_mapping.json"
            if mapping_file.exists():
                print(f"✅ 映射文件已创建: {mapping_file}")
                
                import json
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                
                if result['base_name'] in mapping_data:
                    print(f"✅ 映射记录正确")
                else:
                    print(f"❌ 映射记录缺失")
                    return False
            else:
                print(f"❌ 映射文件未创建")
                return False
            
            return True
        else:
            print(f"❌ 下载失败: {result['message']}")
            return False
    
    async def test_5_4_batch_download(self):
        """测试5.4: 批量下载功能"""
        print("\n" + "="*60)
        print("🧪 测试5.4: 批量下载功能")
        print("="*60)
        
        query = "Python"  # 使用一个简单的搜索词
        batch_output_dir = self.test_output_dir / "batch_test"
        
        print(f"🔍 搜索关键词: {query}")
        print(f"📁 保存目录: {batch_output_dir}")
        
        result = await self.scraper.batch_download_content(
            query=query,
            output_dir=batch_output_dir,
            max_pages=1,  # 只搜索1页，减少测试时间
            min_relevance=0.3
        )
        
        if result["status"] == "success":
            print(f"✅ 批量下载成功: {result['message']}")
            print(f"🔍 搜索关键词: {result['query']}")
            print(f"📊 总计发现: {result['total_found']} 篇")
            print(f"✅ 成功下载: {result['success_count']} 篇")
            print(f"❌ 失败: {result['failed_count']} 篇")
            
            # 验证目录结构
            pdf_dir = batch_output_dir / "pdfs"
            markdown_dir = batch_output_dir / "markdown"
            
            if pdf_dir.exists() and markdown_dir.exists():
                print(f"✅ 目录结构正确")
                
                pdf_files = list(pdf_dir.glob("*.pdf"))  # 现在是真正的PDF文件
                markdown_files = list(markdown_dir.glob("*.md"))
                
                print(f"📄 PDF文件数量: {len(pdf_files)}")
                print(f"📝 Markdown文件数量: {len(markdown_files)}")
                
                # 检查文件对应关系
                if len(pdf_files) == len(markdown_files) == result['success_count']:
                    print(f"✅ 文件数量匹配")
                else:
                    print(f"⚠️ 文件数量不匹配")
                
                return True
            else:
                print(f"❌ 目录结构错误")
                return False
        else:
            print(f"❌ 批量下载失败: {result['message']}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始执行任务5功能测试")
        
        # 清理测试目录
        if self.test_output_dir.exists():
            import shutil
            shutil.rmtree(self.test_output_dir)
        
        test_results = []
        
        # 测试5.1-5.2: 文件名清理
        result_1 = await self.test_5_1_5_2_filename_cleaning()
        test_results.append(("文件名清理", result_1))
        
        # 测试5.3: 单个下载
        result_2 = await self.test_5_3_single_download()
        test_results.append(("单个下载", result_2))
        
        # 测试5.4: 批量下载
        if result_2:  # 只有单个下载成功才进行批量测试
            result_3 = await self.test_5_4_batch_download()
            test_results.append(("批量下载", result_3))
        
        # 输出测试总结
        print("\n" + "="*60)
        print("📊 任务5测试结果总结")
        print("="*60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 任务5所有测试通过！")
            return True
        else:
            print("⚠️ 部分测试失败，需要修复")
            return False


async def main():
    """主函数"""
    tester = Task5Tester()
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n{'='*50}")
    if success:
        print("🎉 任务5测试完成!")
    else:
        print("❌ 任务5测试失败!")
    print(f"{'='*50}")
    sys.exit(0 if success else 1)

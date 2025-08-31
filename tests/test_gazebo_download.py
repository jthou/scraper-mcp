#!/usr/bin/env python3
"""
测试Gazebo内容下载到K-Vault/Gazebo目录
测试任务5的真正需求：从知乎搜索Gazebo相关文章并保存到指定目录
"""
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.web_scraper import WebScraper
from utils.logger import Logger


class GazeboDownloadTester:
    """Gazebo内容下载测试器"""
    
    def __init__(self):
        self.logger = Logger("Gazebo下载测试")
        self.scraper = WebScraper()
        self.target_dir = Path("K-Vault/Gazebo")
        self.pdf_dir = self.target_dir / "pdfs"
        self.markdown_dir = self.target_dir / "markdown"
    
    def check_initial_state(self):
        """检查初始状态"""
        print("🔍 检查K-Vault/Gazebo目录初始状态...")
        
        if not self.target_dir.exists():
            print("❌ K-Vault/Gazebo目录不存在")
            return False
        
        # 检查PDF目录
        pdf_files = list(self.pdf_dir.glob("*")) if self.pdf_dir.exists() else []
        markdown_files = list(self.markdown_dir.glob("*")) if self.markdown_dir.exists() else []
        
        print(f"📁 PDF目录文件数: {len(pdf_files)}")
        print(f"📝 Markdown目录文件数: {len(markdown_files)}")
        
        # 检查是否有.txt文件（错误格式）
        txt_files = list(self.pdf_dir.glob("*.txt")) if self.pdf_dir.exists() else []
        if txt_files:
            print(f"⚠️  发现 {len(txt_files)} 个.txt文件（应该是PDF文件）:")
            for txt_file in txt_files[:3]:  # 只显示前3个
                print(f"    - {txt_file.name}")
            if len(txt_files) > 3:
                print(f"    ... 还有 {len(txt_files) - 3} 个")
        
        # 检查是否有真正的PDF文件
        real_pdf_files = list(self.pdf_dir.glob("*.pdf")) if self.pdf_dir.exists() else []
        print(f"✅ 真正的PDF文件数: {len(real_pdf_files)}")
        
        return True
    
    async def test_login(self):
        """测试登录功能"""
        print("\n" + "="*60)
        print("🔐 测试知乎登录")
        print("="*60)
        
        login_result = await self.scraper.login_zhihu(headless=False)
        if login_result["status"] == "success":
            print("✅ 知乎登录成功")
            return True
        elif login_result["status"] == "waiting":
            print("⏳ 等待用户扫码登录...")
            print("请在浏览器中完成登录，然后按回车继续...")
            input()
            
            # 再次检查登录状态
            if self.scraper.zhihu_context and self.scraper.zhihu_page:
                print("✅ 登录状态已确认")
                return True
            else:
                print("❌ 登录状态确认失败")
                return False
        else:
            print(f"❌ 登录失败: {login_result['message']}")
            return False
    
    async def test_single_gazebo_download(self):
        """测试单个Gazebo文章下载"""
        print("\n" + "="*60)
        print("🧪 测试单个Gazebo文章下载")
        print("="*60)
        
        # 测试一个具体的Gazebo相关URL（如果能找到的话）
        # 这里我们用一个通用的方法：先搜索，然后下载第一个结果
        search_result = await self.scraper.search_zhihu(
            query="Gazebo",
            max_pages=1,
            min_relevance=0.3
        )
        
        if search_result["status"] != "success":
            print(f"❌ 搜索失败: {search_result['message']}")
            return False
        
        results = search_result.get("results", [])
        if not results:
            print("❌ 没有找到Gazebo相关文章")
            return False
        
        # 选择第一个结果进行测试
        test_article = results[0]
        test_url = test_article.get("url", "")
        test_title = test_article.get("title", "")
        
        if not test_url:
            print("❌ 测试文章URL为空")
            return False
        
        print(f"📥 测试文章: {test_title}")
        print(f"🔗 URL: {test_url}")
        print(f"📁 保存目录: {self.target_dir}")
        
        # 下载文章
        download_result = await self.scraper.download_and_save_content(
            url=test_url,
            output_dir=self.target_dir,
            title=test_title
        )
        
        if download_result["status"] == "success":
            print(f"✅ 下载成功: {download_result['message']}")
            print(f"📄 文件名: {download_result['base_name']}")
            
            # 验证文件
            pdf_path = Path(download_result['files']['pdf'])
            markdown_path = Path(download_result['files']['markdown'])
            
            print(f"📄 PDF文件: {pdf_path}")
            print(f"📝 Markdown文件: {markdown_path}")
            
            # 检查文件是否真的存在
            if pdf_path.exists():
                print(f"✅ PDF文件已创建")
                # 检查是否是真正的PDF文件
                if pdf_path.suffix == '.pdf':
                    print(f"✅ 文件格式正确（.pdf）")
                else:
                    print(f"❌ 文件格式错误: {pdf_path.suffix}")
                    return False
            else:
                print(f"❌ PDF文件未创建: {pdf_path}")
                return False
            
            if markdown_path.exists():
                print(f"✅ Markdown文件已创建")
            else:
                print(f"❌ Markdown文件未创建: {markdown_path}")
                return False
            
            return True
        else:
            print(f"❌ 下载失败: {download_result['message']}")
            return False
    
    async def test_batch_gazebo_download(self):
        """测试批量Gazebo文章下载"""
        print("\n" + "="*60)
        print("🧪 测试批量Gazebo文章下载")
        print("="*60)
        
        print(f"🔍 搜索关键词: Gazebo")
        print(f"📁 保存目录: {self.target_dir}")
        print(f"📖 最大页数: 2")
        print(f"🎯 最小相关性: 0.4")
        
        batch_result = await self.scraper.batch_download_content(
            query="Gazebo",
            output_dir=self.target_dir,
            max_pages=2,  # 搜索2页，获取更多Gazebo内容
            min_relevance=0.4
        )
        
        if batch_result["status"] == "success":
            print(f"✅ 批量下载成功: {batch_result['message']}")
            print(f"📊 总计发现: {batch_result['total_found']} 篇")
            print(f"✅ 成功下载: {batch_result['success_count']} 篇")
            print(f"❌ 失败: {batch_result['failed_count']} 篇")
            
            # 验证最终文件状态
            return self.verify_final_state(batch_result['success_count'])
        else:
            print(f"❌ 批量下载失败: {batch_result['message']}")
            return False
    
    def verify_final_state(self, expected_count=None):
        """验证最终文件状态"""
        print("\n" + "="*50)
        print("🔍 验证最终文件状态")
        print("="*50)
        
        # 检查目录结构
        if not self.pdf_dir.exists() or not self.markdown_dir.exists():
            print("❌ 目录结构不完整")
            return False
        
        # 统计文件
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        txt_files = list(self.pdf_dir.glob("*.txt"))
        markdown_files = list(self.markdown_dir.glob("*.md"))
        
        print(f"📄 真正的PDF文件: {len(pdf_files)} 个")
        print(f"⚠️  错误的.txt文件: {len(txt_files)} 个")
        print(f"📝 Markdown文件: {len(markdown_files)} 个")
        
        # 显示文件列表
        if pdf_files:
            print("\n✅ PDF文件列表:")
            for i, pdf_file in enumerate(pdf_files[:5], 1):  # 最多显示5个
                print(f"  {i}. {pdf_file.name}")
            if len(pdf_files) > 5:
                print(f"  ... 还有 {len(pdf_files) - 5} 个")
        
        if markdown_files:
            print("\n📝 Markdown文件列表:")
            for i, md_file in enumerate(markdown_files[:5], 1):  # 最多显示5个
                print(f"  {i}. {md_file.name}")
            if len(markdown_files) > 5:
                print(f"  ... 还有 {len(markdown_files) - 5} 个")
        
        # 检查文件对应关系
        pdf_basenames = {f.stem for f in pdf_files}
        md_basenames = {f.stem for f in markdown_files}
        
        if pdf_basenames == md_basenames:
            print("\n✅ PDF和Markdown文件完全对应")
        else:
            print("\n⚠️ PDF和Markdown文件不完全对应")
            missing_in_pdf = md_basenames - pdf_basenames
            missing_in_md = pdf_basenames - md_basenames
            if missing_in_pdf:
                print(f"   缺少PDF的文件: {missing_in_pdf}")
            if missing_in_md:
                print(f"   缺少Markdown的文件: {missing_in_md}")
        
        # 检查是否有错误的.txt文件
        if txt_files:
            print(f"\n❌ 发现 {len(txt_files)} 个错误的.txt文件（应该是PDF）")
            return False
        
        # 检查数量
        if expected_count and len(pdf_files) != expected_count:
            print(f"\n⚠️ PDF文件数量不符合预期: 期望{expected_count}，实际{len(pdf_files)}")
        
        # 总体评估
        success = (
            len(pdf_files) > 0 and  # 有真正的PDF文件
            len(txt_files) == 0 and  # 没有错误的.txt文件
            len(pdf_files) == len(markdown_files)  # PDF和Markdown数量匹配
        )
        
        if success:
            print(f"\n🎉 验证通过！K-Vault/Gazebo目录状态正确")
        else:
            print(f"\n❌ 验证失败！存在问题需要修复")
        
        return success
    
    async def run_complete_test(self):
        """运行完整的测试流程"""
        print("🚀 开始Gazebo内容下载测试")
        print("目标：搜索Gazebo相关文章并保存到K-Vault/Gazebo目录")
        
        test_results = []
        
        # 1. 检查初始状态
        print("\n📋 步骤1: 检查初始状态")
        initial_check = self.check_initial_state()
        test_results.append(("初始状态检查", initial_check))
        
        if not initial_check:
            print("❌ 初始状态检查失败，无法继续测试")
            return False
        
        # 2. 测试登录
        print("\n📋 步骤2: 测试登录")
        login_success = await self.test_login()
        test_results.append(("知乎登录", login_success))
        
        if not login_success:
            print("❌ 登录失败，无法继续测试")
            return False
        
        # 3. 测试单个下载
        print("\n📋 步骤3: 测试单个Gazebo文章下载")
        single_success = await self.test_single_gazebo_download()
        test_results.append(("单个下载", single_success))
        
        # 4. 测试批量下载（只有单个下载成功才进行）
        if single_success:
            print("\n📋 步骤4: 测试批量Gazebo文章下载")
            batch_success = await self.test_batch_gazebo_download()
            test_results.append(("批量下载", batch_success))
        else:
            print("\n⏭️  跳过批量下载测试（单个下载失败）")
            batch_success = False
        
        # 5. 最终验证
        if single_success or batch_success:
            print("\n📋 步骤5: 最终状态验证")
            final_verification = self.verify_final_state()
            test_results.append(("最终验证", final_verification))
        
        # 输出测试总结
        print("\n" + "="*60)
        print("📊 Gazebo下载测试结果总结")
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
            print("🎉 所有测试通过！Gazebo内容已成功下载到K-Vault/Gazebo目录")
            return True
        else:
            print("⚠️ 部分测试失败，需要修复问题")
            return False


async def main():
    """主函数"""
    tester = GazeboDownloadTester()
    success = await tester.run_complete_test()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n{'='*60}")
    if success:
        print("🎉 Gazebo内容下载测试完成！")
        print("📁 检查K-Vault/Gazebo目录查看下载的文件")
    else:
        print("❌ Gazebo内容下载测试失败！")
        print("🔧 需要修复代码中的问题")
    print(f"{'='*60}")
    sys.exit(0 if success else 1)

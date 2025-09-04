#!/usr/bin/env python3
"""
搜狗微信搜索测试脚本

专门测试搜狗微信搜索功能的各种场景
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from experiments.sogou_wechat_search import SogouWeChatSearch


class SogouSearchTester:
    """搜狗搜索测试类"""
    
    def __init__(self):
        self.searcher = SogouWeChatSearch()
        self.test_results = []
    
    async def test_basic_search(self):
        """测试基础搜索功能"""
        print("🧪 测试1: 基础搜索功能")
        print("-" * 30)
        
        test_queries = [
            "Python编程",
            "机器学习",
            "人工智能"
        ]
        
        for query in test_queries:
            print(f"\n🔍 搜索: {query}")
            
            try:
                result = await self.searcher.search(query, max_pages=1)
                
                if result["status"] == "success":
                    print(f"✅ 搜索成功: {result['message']}")
                    print(f"📊 结果数量: {result['total_results']}")
                    
                    # 验证结果质量
                    quality_score = self._evaluate_result_quality(result)
                    print(f"📈 质量评分: {quality_score}/10")
                    
                    self.test_results.append({
                        "test": "basic_search",
                        "query": query,
                        "status": "success",
                        "results_count": result['total_results'],
                        "quality_score": quality_score
                    })
                else:
                    print(f"❌ 搜索失败: {result['message']}")
                    self.test_results.append({
                        "test": "basic_search",
                        "query": query,
                        "status": "failed",
                        "error": result['message']
                    })
                
            except Exception as e:
                print(f"💥 搜索异常: {e}")
                self.test_results.append({
                    "test": "basic_search",
                    "query": query,
                    "status": "error",
                    "error": str(e)
                })
    
    async def test_pagination(self):
        """测试翻页功能"""
        print("\n🧪 测试2: 翻页功能")
        print("-" * 30)
        
        query = "Python编程"
        max_pages = 3
        
        print(f"🔍 搜索: {query} (最多{max_pages}页)")
        
        try:
            result = await self.searcher.search(query, max_pages=max_pages)
            
            if result["status"] == "success":
                print(f"✅ 搜索成功: {result['message']}")
                print(f"📊 总结果数: {result['total_results']}")
                print(f"📄 搜索页数: {result['pages_searched']}")
                
                # 验证翻页效果
                if result['pages_searched'] > 1:
                    print("✅ 翻页功能正常")
                    pagination_score = 10
                else:
                    print("⚠️ 只搜索了1页，翻页功能可能有问题")
                    pagination_score = 5
                
                self.test_results.append({
                    "test": "pagination",
                    "query": query,
                    "status": "success",
                    "pages_searched": result['pages_searched'],
                    "total_results": result['total_results'],
                    "pagination_score": pagination_score
                })
            else:
                print(f"❌ 搜索失败: {result['message']}")
                self.test_results.append({
                    "test": "pagination",
                    "query": query,
                    "status": "failed",
                    "error": result['message']
                })
                
        except Exception as e:
            print(f"💥 翻页测试异常: {e}")
            self.test_results.append({
                "test": "pagination",
                "query": query,
                "status": "error",
                "error": str(e)
            })
    
    async def test_captcha_handling(self):
        """测试验证码处理"""
        print("\n🧪 测试3: 验证码处理")
        print("-" * 30)
        
        # 设置浏览器
        if not await self.searcher.setup_browser(headless=False):
            print("❌ 浏览器设置失败")
            return
        
        try:
            # 访问搜狗搜索页面
            await self.searcher.page.goto("https://weixin.sogou.com/weixin?type=2&query=test")
            await self.searcher.page.wait_for_load_state("networkidle")
            
            # 检查验证码
            captcha_result = await self.searcher._check_captcha()
            
            if captcha_result["has_captcha"]:
                print(f"⚠️ 检测到验证码: {captcha_result['type']}")
                print("💡 建议: 需要人工处理验证码")
                captcha_score = 5
            else:
                print("✅ 未检测到验证码")
                captcha_score = 10
            
            self.test_results.append({
                "test": "captcha_handling",
                "status": "success",
                "has_captcha": captcha_result["has_captcha"],
                "captcha_type": captcha_result.get("type", ""),
                "captcha_score": captcha_score
            })
            
        except Exception as e:
            print(f"💥 验证码测试异常: {e}")
            self.test_results.append({
                "test": "captcha_handling",
                "status": "error",
                "error": str(e)
            })
    
    async def test_retry_mechanism(self):
        """测试重试机制"""
        print("\n🧪 测试4: 重试机制")
        print("-" * 30)
        
        query = "机器学习算法"
        max_retries = 2
        
        print(f"🔍 搜索: {query} (最多重试{max_retries}次)")
        
        try:
            result = await self.searcher.search_with_retry(query, max_pages=1, max_retries=max_retries)
            
            if result["status"] == "success":
                print(f"✅ 搜索成功: {result['message']}")
                retry_score = 10
            else:
                print(f"❌ 搜索失败: {result['message']}")
                retry_score = 0
            
            self.test_results.append({
                "test": "retry_mechanism",
                "query": query,
                "status": result["status"],
                "retry_score": retry_score
            })
            
        except Exception as e:
            print(f"💥 重试测试异常: {e}")
            self.test_results.append({
                "test": "retry_mechanism",
                "query": query,
                "status": "error",
                "error": str(e)
            })
    
    async def test_data_quality(self):
        """测试数据质量"""
        print("\n🧪 测试5: 数据质量")
        print("-" * 30)
        
        query = "Python编程教程"
        
        print(f"🔍 搜索: {query}")
        
        try:
            result = await self.searcher.search(query, max_pages=1)
            
            if result["status"] == "success":
                results = result.get('results', [])
                
                if results:
                    # 分析数据质量
                    quality_metrics = self._analyze_data_quality(results)
                    
                    print(f"📊 数据质量分析:")
                    print(f"  - 有效结果数: {quality_metrics['valid_results']}/{len(results)}")
                    print(f"  - 平均标题长度: {quality_metrics['avg_title_length']:.1f}")
                    print(f"  - 平均摘要长度: {quality_metrics['avg_summary_length']:.1f}")
                    print(f"  - 链接完整性: {quality_metrics['link_completeness']:.1%}")
                    print(f"  - 作者信息完整性: {quality_metrics['author_completeness']:.1%}")
                    
                    quality_score = quality_metrics['overall_score']
                    print(f"📈 总体质量评分: {quality_score}/10")
                    
                    self.test_results.append({
                        "test": "data_quality",
                        "query": query,
                        "status": "success",
                        "quality_metrics": quality_metrics
                    })
                else:
                    print("❌ 没有找到结果")
                    self.test_results.append({
                        "test": "data_quality",
                        "query": query,
                        "status": "failed",
                        "error": "没有找到结果"
                    })
            else:
                print(f"❌ 搜索失败: {result['message']}")
                self.test_results.append({
                    "test": "data_quality",
                    "query": query,
                    "status": "failed",
                    "error": result['message']
                })
                
        except Exception as e:
            print(f"💥 数据质量测试异常: {e}")
            self.test_results.append({
                "test": "data_quality",
                "query": query,
                "status": "error",
                "error": str(e)
            })
    
    def _evaluate_result_quality(self, result: dict) -> int:
        """评估搜索结果质量"""
        try:
            results = result.get('results', [])
            if not results:
                return 0
            
            score = 0
            
            # 结果数量评分 (0-3分)
            if len(results) >= 10:
                score += 3
            elif len(results) >= 5:
                score += 2
            elif len(results) >= 1:
                score += 1
            
            # 数据完整性评分 (0-4分)
            complete_results = 0
            for item in results:
                if item.get('title') and item.get('link'):
                    complete_results += 1
            
            completeness_ratio = complete_results / len(results)
            score += int(completeness_ratio * 4)
            
            # 数据质量评分 (0-3分)
            quality_results = 0
            for item in results:
                title = item.get('title', '')
                summary = item.get('summary', '')
                if len(title) > 10 and len(summary) > 20:
                    quality_results += 1
            
            quality_ratio = quality_results / len(results)
            score += int(quality_ratio * 3)
            
            return min(score, 10)
            
        except Exception:
            return 0
    
    def _analyze_data_quality(self, results: list) -> dict:
        """分析数据质量指标"""
        try:
            total_results = len(results)
            valid_results = 0
            title_lengths = []
            summary_lengths = []
            link_count = 0
            author_count = 0
            
            for item in results:
                # 检查结果有效性
                if item.get('title') and item.get('link'):
                    valid_results += 1
                
                # 标题长度
                title = item.get('title', '')
                if title:
                    title_lengths.append(len(title))
                
                # 摘要长度
                summary = item.get('summary', '')
                if summary:
                    summary_lengths.append(len(summary))
                
                # 链接完整性
                if item.get('link'):
                    link_count += 1
                
                # 作者信息完整性
                if item.get('author'):
                    author_count += 1
            
            # 计算指标
            avg_title_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0
            avg_summary_length = sum(summary_lengths) / len(summary_lengths) if summary_lengths else 0
            link_completeness = link_count / total_results if total_results > 0 else 0
            author_completeness = author_count / total_results if total_results > 0 else 0
            
            # 总体质量评分
            overall_score = (
                (valid_results / total_results) * 4 +  # 有效性 40%
                (link_completeness) * 3 +  # 链接完整性 30%
                (author_completeness) * 2 +  # 作者信息 20%
                min(avg_title_length / 50, 1) * 1  # 标题质量 10%
            ) * 10
            
            return {
                'valid_results': valid_results,
                'total_results': total_results,
                'avg_title_length': avg_title_length,
                'avg_summary_length': avg_summary_length,
                'link_completeness': link_completeness,
                'author_completeness': author_completeness,
                'overall_score': min(overall_score, 10)
            }
            
        except Exception as e:
            return {
                'valid_results': 0,
                'total_results': len(results),
                'avg_title_length': 0,
                'avg_summary_length': 0,
                'link_completeness': 0,
                'author_completeness': 0,
                'overall_score': 0
            }
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始搜狗微信搜索测试")
        print("=" * 50)
        
        try:
            # 设置浏览器
            if not await self.searcher.setup_browser(headless=False):
                print("❌ 浏览器设置失败，无法进行测试")
                return False
            
            # 运行各项测试
            await self.test_basic_search()
            await self.test_pagination()
            await self.test_captcha_handling()
            await self.test_retry_mechanism()
            await self.test_data_quality()
            
            # 生成测试报告
            self._generate_test_report()
            
            return True
            
        except Exception as e:
            print(f"💥 测试过程中发生错误: {e}")
            return False
        
        finally:
            await self.searcher.cleanup()
    
    def _generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📊 测试报告")
        print("=" * 50)
        
        # 统计测试结果
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['status'] == 'success')
        failed_tests = sum(1 for result in self.test_results if result['status'] == 'failed')
        error_tests = sum(1 for result in self.test_results if result['status'] == 'error')
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"错误: {error_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        # 详细结果
        print("\n详细结果:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'failed' else "💥"
            print(f"  {status_icon} {result['test']}: {result['status']}")
            if result['status'] == 'failed' and 'error' in result:
                print(f"     错误: {result['error']}")
        
        # 保存测试报告
        report_file = Path(__file__).parent / f"sogou_search_test_report_{int(datetime.now().timestamp())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'failed_tests': failed_tests,
                    'error_tests': error_tests,
                    'success_rate': successful_tests/total_tests*100
                },
                'results': self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 测试报告已保存到: {report_file}")


async def main():
    """主函数"""
    tester = SogouSearchTester()
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

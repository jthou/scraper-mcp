"""GitHub仓库抓取实际应用示例"""
import asyncio
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.github import (
    GitHubConfig, 
    scrape_github_content,
    discover_github_content
)


async def analyze_popular_repos():
    """分析热门开源项目"""
    print("🔥 分析热门开源项目仓库\n")
    
    # 精选的代表性开源项目
    popular_repos = [
        ("microsoft", "vscode"),       # 代码编辑器
        ("facebook", "react"),         # 前端框架  
        ("tensorflow", "tensorflow"),  # 机器学习
        ("torvalds", "linux"),         # 操作系统内核
        ("git", "git"),               # 版本控制
    ]
    
    # 轻量级配置，只获取核心文档
    config = GitHubConfig(
        repo_max_files=15,
        repo_delay=0.2,
        save_metadata=True,  # 保存结果到K-Vault
        convert_to_markdown=True,
        max_file_size=200 * 1024  # 200KB限制
    )
    
    analysis_results = []
    
    for owner, repo in popular_repos:
        print(f"📊 分析 {owner}/{repo}...")
        
        try:
            # 先发现内容源
            discovery = await discover_github_content(f"{owner}/{repo}")
            
            if discovery.get("status") == "success":
                repo_info = discovery["sources"].get("repository_info", {})
                
                if repo_info.get("status") == "success":
                    print(f"✅ 仓库发现成功:")
                    print(f"   名称: {repo_info.get('full_name')}")
                    print(f"   描述: {repo_info.get('description', 'N/A')[:80]}...")
                    print(f"   语言: {repo_info.get('language', 'N/A')}")
                    print(f"   星标: {repo_info.get('stargazers_count', 0):,}")
                    print(f"   大小: {repo_info.get('size', 0):,} KB")
                    
                    # 抓取仓库文档
                    result = await scrape_github_content(
                        f"{owner}/{repo}",
                        scrape_type="repository",
                        config=config
                    )
                    
                    if result.get("status") == "success":
                        summary = result.get("scrape_summary", {})
                        files = result.get("files", [])
                        
                        print(f"   抓取结果: {summary.get('extracted_files', 0)} 个文件")
                        
                        # 分析文档类型
                        doc_types = {}
                        total_size = 0
                        
                        for file_data in files:
                            if file_data.get("status") == "success":
                                file_type = file_data.get("file_type", "other")
                                doc_types[file_type] = doc_types.get(file_type, 0) + 1
                                total_size += file_data.get("size", 0)
                        
                        print(f"   文档类型: {dict(doc_types)}")
                        print(f"   总大小: {total_size:,} bytes")
                        
                        analysis_results.append({
                            "repo": f"{owner}/{repo}",
                            "info": repo_info,
                            "doc_summary": summary,
                            "doc_types": doc_types,
                            "total_size": total_size
                        })
                    else:
                        print(f"   ❌ 抓取失败: {result.get('error')}")
                else:
                    print(f"   ❌ 仓库信息获取失败")
            else:
                print(f"   ❌ 发现失败: {discovery.get('error')}")
        
        except Exception as e:
            print(f"   ❌ 分析失败: {e}")
        
        print()  # 空行分隔
    
    # 生成分析报告
    if analysis_results:
        print("📈 分析报告汇总:")
        print("=" * 60)
        
        total_stars = sum(r["info"].get("stargazers_count", 0) for r in analysis_results)
        total_files = sum(r["doc_summary"].get("extracted_files", 0) for r in analysis_results)
        total_size = sum(r["total_size"] for r in analysis_results)
        
        print(f"📊 总体统计:")
        print(f"   分析项目: {len(analysis_results)} 个")
        print(f"   总星标数: {total_stars:,}")
        print(f"   总文档数: {total_files}")
        print(f"   总文档大小: {total_size:,} bytes")
        
        print(f"\n📋 项目详情:")
        for result in analysis_results:
            repo = result["repo"]
            info = result["info"]
            summary = result["doc_summary"]
            
            print(f"   {repo}:")
            print(f"     语言: {info.get('language', 'N/A')}")
            print(f"     星标: {info.get('stargazers_count', 0):,}")
            print(f"     文档: {summary.get('extracted_files', 0)} 个")
            print(f"     类型: {list(result['doc_types'].keys())}")
        
        print(f"\n💾 文档已保存到 K-Vault/GitHub/Repositories/ 目录")


async def explore_trending_topics():
    """探索特定技术领域的项目"""
    print("🚀 探索机器学习相关项目\n")
    
    # 机器学习相关的优质项目
    ml_repos = [
        ("pytorch", "pytorch"),
        ("scikit-learn", "scikit-learn"), 
        ("huggingface", "transformers"),
        ("openai", "whisper"),
        ("microsoft", "LightGBM")
    ]
    
    config = GitHubConfig(
        repo_max_files=10,
        repo_delay=0.1,
        save_metadata=False,  # 只做分析，不保存
        convert_to_markdown=True
    )
    
    ml_analysis = []
    
    for owner, repo in ml_repos:
        print(f"🤖 探索 {owner}/{repo}...")
        
        try:
            result = await scrape_github_content(
                f"{owner}/{repo}",
                scrape_type="repository", 
                config=config
            )
            
            if result.get("status") == "success":
                repo_info = result.get("repository", {})
                languages = result.get("languages", {})
                files = result.get("files", [])
                
                print(f"✅ 项目信息:")
                print(f"   描述: {repo_info.get('description', 'N/A')[:60]}...")
                print(f"   主要语言: {repo_info.get('language', 'N/A')}")
                
                if languages:
                    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
                    lang_summary = ", ".join([f"{lang}" for lang, _ in top_langs])
                    print(f"   语言分布: {lang_summary}")
                
                # 分析README和文档质量
                readme_files = [f for f in files if 'readme' in f.get('path', '').lower()]
                doc_files = [f for f in files if f.get('file_type') == 'documentation']
                
                print(f"   README文件: {len(readme_files)} 个")
                print(f"   文档文件: {len(doc_files)} 个")
                
                # 检查是否有特定的ML相关文件
                ml_indicators = []
                for file_data in files:
                    path = file_data.get('path', '').lower()
                    if any(keyword in path for keyword in ['model', 'train', 'neural', 'ai', 'ml', 'deep']):
                        ml_indicators.append(file_data.get('path'))
                
                if ml_indicators:
                    print(f"   ML相关文件: {len(ml_indicators)} 个")
                    for indicator in ml_indicators[:3]:
                        print(f"     📄 {indicator}")
                
                ml_analysis.append({
                    "repo": f"{owner}/{repo}",
                    "language": repo_info.get('language'),
                    "stars": repo_info.get('stargazers_count', 0),
                    "doc_count": len(doc_files),
                    "ml_files": len(ml_indicators),
                    "top_languages": [lang for lang, _ in top_langs] if languages else []
                })
            else:
                print(f"   ❌ 探索失败: {result.get('error')}")
        
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        print()
    
    # 生成趋势分析
    if ml_analysis:
        print("📊 机器学习项目趋势分析:")
        print("=" * 50)
        
        # 语言统计
        lang_counts = {}
        for analysis in ml_analysis:
            for lang in analysis["top_languages"][:2]:  # 只统计前两种语言
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        print(f"🔤 热门语言:")
        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {lang}: {count} 个项目")
        
        # 项目规模
        total_stars = sum(a["stars"] for a in ml_analysis)
        avg_docs = sum(a["doc_count"] for a in ml_analysis) / len(ml_analysis)
        
        print(f"\n📈 项目统计:")
        print(f"   总星标数: {total_stars:,}")
        print(f"   平均文档数: {avg_docs:.1f} 个/项目")
        
        # 按星标排序
        print(f"\n⭐ 按热度排序:")
        sorted_projects = sorted(ml_analysis, key=lambda x: x["stars"], reverse=True)
        for project in sorted_projects:
            print(f"   {project['repo']}: {project['stars']:,} stars ({project['language']})")


async def main():
    """主函数"""
    print("🚀 GitHub仓库抓取实际应用演示\n")
    
    # 演示1: 分析热门开源项目
    await analyze_popular_repos()
    
    print("\n" + "="*80 + "\n")
    
    # 演示2: 探索特定技术领域  
    await explore_trending_topics()
    
    print("\n🎉 演示完成！")
    print("\n💡 应用场景:")
    print("✅ 开源项目调研 - 快速了解项目结构和文档")
    print("✅ 技术选型参考 - 对比不同项目的文档质量")
    print("✅ 学习资源收集 - 自动抓取优质技术文档")
    print("✅ 竞品分析 - 分析同类项目的特点")
    print("✅ 代码库审计 - 检查文档完整性")
    print("✅ 知识库构建 - 批量收集技术资料")


if __name__ == "__main__":
    asyncio.run(main())

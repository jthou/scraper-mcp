"""轻量级GitHub仓库抓取演示 - 避免API限制"""
import asyncio
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.github import (
    GitHubConfig, 
    scrape_github_repository,
    get_github_repository_info
)


async def demo_single_repo_analysis():
    """演示单个仓库的深度分析"""
    print("🔍 单个仓库深度分析演示\n")
    
    # 选择一个中等规模的仓库进行分析
    owner, repo = "octocat", "Hello-World"
    
    print(f"📊 分析目标: {owner}/{repo}")
    print("=" * 50)
    
    # 配置详细抓取
    config = GitHubConfig(
        repo_max_files=50,    # 增加文件数量
        repo_delay=0.5,       # 减少请求频率
        save_metadata=True,   # 保存详细元数据
        convert_to_markdown=True,
        max_file_size=1024 * 1024  # 1MB限制
    )
    
    try:
        # 步骤1: 获取仓库基本信息
        print("📋 步骤1: 获取仓库基本信息...")
        repo_info = await get_github_repository_info(owner, repo, config)
        
        if repo_info.get("status") == "success":
            print("✅ 仓库信息获取成功:")
            print(f"   📁 仓库名: {repo_info.get('full_name')}")
            print(f"   📝 描述: {repo_info.get('description', 'N/A')}")
            print(f"   🗣️ 主要语言: {repo_info.get('language', 'N/A')}")
            print(f"   ⭐ 星标数: {repo_info.get('stargazers_count', 0):,}")
            print(f"   🍴 Fork数: {repo_info.get('forks_count', 0):,}")
            print(f"   📦 大小: {repo_info.get('size', 0):,} KB")
            print(f"   📅 创建时间: {repo_info.get('created_at', 'N/A')}")
            print(f"   🔄 更新时间: {repo_info.get('updated_at', 'N/A')}")
            print(f"   ⚖️ 许可证: {repo_info.get('license', 'N/A')}")
            
            # 特殊标记
            features = []
            if repo_info.get('has_pages'):
                features.append("📄 GitHub Pages")
            if repo_info.get('has_wiki'):
                features.append("📚 Wiki")
            if repo_info.get('homepage'):
                features.append("🌐 主页")
            
            if features:
                print(f"   🎯 特性: {' | '.join(features)}")
        else:
            print(f"❌ 仓库信息获取失败: {repo_info.get('error')}")
            return
        
        print()
        
        # 步骤2: 抓取仓库内容
        print("📚 步骤2: 抓取仓库文档内容...")
        
        result = await scrape_github_repository(
            owner, repo,
            max_files=50,
            include_code=True,  # 包含代码文件
            config=config
        )
        
        if result.get("status") == "success":
            print("✅ 内容抓取成功:")
            
            # 分析语言分布
            languages = result.get("languages", {})
            if languages:
                print(f"   🌍 语言分布:")
                total_bytes = sum(languages.values())
                for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                    print(f"     {lang}: {percentage:.1f}% ({bytes_count:,} bytes)")
            
            # 抓取统计
            summary = result.get("scrape_summary", {})
            print(f"   📊 抓取统计:")
            print(f"     发现文件总数: {summary.get('total_files_found', 0)}")
            print(f"     文档文件数: {summary.get('documentation_files', 0)}")
            print(f"     成功抓取数: {summary.get('extracted_files', 0)}")
            
            # 文件分析
            files = result.get("files", [])
            if files:
                print(f"   📄 文件详情:")
                
                # 按类型分组
                file_types = {}
                total_content_size = 0
                
                for file_data in files:
                    if file_data.get("status") == "success":
                        file_type = file_data.get("file_type", "other")
                        if file_type not in file_types:
                            file_types[file_type] = []
                        file_types[file_type].append(file_data)
                        
                        # 计算内容大小
                        content = file_data.get("content", "")
                        if content and file_data.get("encoding") != "base64":
                            total_content_size += len(content)
                
                print(f"     总内容大小: {total_content_size:,} 字符")
                
                # 按优先级显示重要文件
                important_files = sorted(
                    [f for f in files if f.get("status") == "success"],
                    key=lambda x: x.get("priority", 0),
                    reverse=True
                )
                
                print(f"     重要文件 (按优先级排序):")
                for file_data in important_files[:10]:  # 显示前10个
                    path = file_data.get("path", "unknown")
                    file_type = file_data.get("file_type", "unknown")
                    size = file_data.get("size", 0)
                    priority = file_data.get("priority", 0)
                    
                    # 选择合适的图标
                    icon = "📄"
                    if file_type == "documentation":
                        icon = "📚"
                    elif file_type == "configuration":
                        icon = "⚙️"
                    elif file_type == "code":
                        icon = "💻"
                    elif file_type == "legal":
                        icon = "⚖️"
                    elif file_type == "build":
                        icon = "🔨"
                    
                    print(f"       {icon} {path} ({file_type}, {size} bytes, 优先级: {priority})")
                
                # 类型分布
                print(f"     文件类型分布:")
                for file_type, type_files in file_types.items():
                    print(f"       {file_type}: {len(type_files)} 个文件")
            
            print(f"\n💾 详细内容已保存到: K-Vault/GitHub/Repositories/{owner}_{repo}/")
        else:
            print(f"❌ 内容抓取失败: {result.get('error')}")
        
    except Exception as e:
        print(f"❌ 分析过程出错: {e}")


async def demo_api_rate_limiting():
    """演示API速率限制处理"""
    print("\n🚦 API速率限制演示\n")
    
    config = GitHubConfig(
        repo_delay=1.0,  # 增加延迟到1秒
        repo_max_files=3  # 减少文件数量
    )
    
    print("⚙️ 配置参数:")
    print(f"   API延迟: {config.repo_delay} 秒")
    print(f"   最大文件数: {config.repo_max_files}")
    print(f"   API限制: {config.api_rate_limit} 请求/小时")
    
    # 测试多个小型仓库
    test_repos = [
        ("octocat", "Hello-World"),
        ("octocat", "Spoon-Knife"),
    ]
    
    print(f"\n🔄 连续抓取 {len(test_repos)} 个仓库...")
    
    for i, (owner, repo) in enumerate(test_repos, 1):
        print(f"\n📊 [{i}/{len(test_repos)}] 抓取 {owner}/{repo}...")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            result = await scrape_github_repository(
                owner, repo,
                max_files=config.repo_max_files,
                include_code=False,  # 只要文档
                config=config
            )
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            if result.get("status") == "success":
                summary = result.get("scrape_summary", {})
                print(f"✅ 成功 - 用时 {duration:.1f}秒")
                print(f"   抓取文件: {summary.get('extracted_files', 0)} 个")
            else:
                print(f"❌ 失败: {result.get('error')}")
                
                # 检查是否是速率限制错误
                error_msg = result.get('error', '')
                if 'rate limit' in error_msg.lower():
                    print("⚠️ 遇到API速率限制，这是正常现象")
                    print("💡 解决方案:")
                    print("   1. 添加GitHub API token到配置")
                    print("   2. 增加 repo_delay 参数")
                    print("   3. 减少 repo_max_files 参数")
                    break
        
        except Exception as e:
            print(f"❌ 错误: {e}")


def show_configuration_guide():
    """显示配置指南"""
    print("\n📖 GitHub API配置指南\n")
    
    print("🔑 获取GitHub API Token:")
    print("1. 登录GitHub，进入 Settings > Developer settings")
    print("2. 选择 Personal access tokens > Tokens (classic)")
    print("3. 点击 Generate new token")
    print("4. 选择权限: public_repo (用于公开仓库)")
    print("5. 复制生成的token")
    
    print("\n⚙️ 配置方法:")
    print("```python")
    print("from core.github import GitHubConfig")
    print("")
    print("config = GitHubConfig(")
    print("    api_token='your_token_here',  # 你的API token")
    print("    api_rate_limit=5000,          # 认证用户: 5000/小时")
    print("    repo_delay=0.1,              # API调用间隔")
    print("    repo_max_files=100           # 最大文件数")
    print(")")
    print("```")
    
    print("\n📊 速率限制对比:")
    print("   未认证用户: 60 请求/小时")
    print("   认证用户: 5,000 请求/小时")
    print("   GitHub Apps: 5,000 请求/小时/安装")
    
    print("\n💡 最佳实践:")
    print("✅ 使用API token进行认证")
    print("✅ 合理设置延迟参数 (0.1-1.0秒)")
    print("✅ 限制单次抓取的文件数量")
    print("✅ 实现错误重试机制")
    print("✅ 监控速率限制状态")


async def main():
    """主函数"""
    print("🚀 GitHub仓库抓取功能演示\n")
    print("=" * 60)
    
    # 演示1: 单个仓库深度分析
    await demo_single_repo_analysis()
    
    # 演示2: API速率限制处理
    await demo_api_rate_limiting()
    
    # 显示配置指南
    show_configuration_guide()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    
    print("\n📋 功能总结:")
    print("✅ 仓库信息获取 - 完整的元数据和统计")
    print("✅ 内容智能抓取 - 自动识别文档和代码")
    print("✅ 文件分类排序 - 按重要程度和类型组织")
    print("✅ 语言分布分析 - 技术栈统计")
    print("✅ 速率限制处理 - 避免API限制")
    print("✅ 错误恢复机制 - 完善的异常处理")
    print("✅ 结果持久化 - 自动保存到K-Vault")


if __name__ == "__main__":
    asyncio.run(main())

"""GitHub Token管理系统使用示例"""
import asyncio
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.github.token_manager import GitHubTokenManager
from core.github.config import GitHubConfig
from core.github.repo_scraper import GitHubRepoScraper


async def demo_token_management():
    """演示Token管理功能"""
    print("🚀 GitHub Token管理系统演示")
    print("=" * 50)
    
    # 1. 创建Token管理器
    print("\n1️⃣ 创建Token管理器...")
    manager = GitHubTokenManager()
    
    # 2. 检查当前Token状态
    print("\n2️⃣ 检查Token状态...")
    current_token = manager.get_token()
    if current_token:
        print(f"✅ 找到Token: {current_token[:10]}...")
        # 获取Token信息
        token_info = manager.get_token_info()
        print(f"📊 Token信息: {token_info}")
    else:
        print("❌ 未找到Token")
        print("💡 请设置环境变量 GITHUB_TOKEN 或添加Token")
        return
    
    # 3. 检查安全性
    print("\n3️⃣ Token安全性检查...")
    security_info = manager.security_manager.validate_token_security(current_token)
    print(f"🔒 安全评分: {security_info['score']}/100")
    if security_info['issues']:
        print("⚠️ 安全问题:")
        for issue in security_info['issues']:
            print(f"   - {issue}")
    
    # 4. 测试配置自动检测
    print("\n4️⃣ 测试配置自动检测...")
    config = GitHubConfig()
    print(f"📋 配置信息:")
    print(f"   - Token已配置: {'是' if config.github_token else '否'}")
    print(f"   - 最大重试: {config.max_retries}")
    print(f"   - 请求延迟: {config.request_delay}秒")
    
    # 5. 测试API功能
    print("\n5️⃣ 测试GitHub API功能...")
    try:
        scraper = GitHubRepoScraper(config)
        
        # 获取用户信息
        print("📡 获取用户信息...")
        user_info = await scraper.get_user_info()
        if user_info:
            print(f"👤 用户: {user_info.get('login', 'unknown')}")
            print(f"🏢 公司: {user_info.get('company', 'N/A')}")
        
        # 获取速率限制信息
        print("\n📊 获取速率限制信息...")
        rate_info = await scraper.get_rate_limit()
        if rate_info:
            core_limit = rate_info.get('resources', {}).get('core', {})
            print(f"🔢 核心API限制: {core_limit.get('limit', 'unknown')}/小时")
            print(f"🔄 剩余请求: {core_limit.get('remaining', 'unknown')}")
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
    
    print("\n✅ 演示完成!")


async def demo_repo_scraping():
    """演示仓库抓取功能"""
    print("\n" + "=" * 50)
    print("📦 GitHub仓库抓取演示")
    print("=" * 50)
    
    # 配置
    config = GitHubConfig()
    if not config.github_token:
        print("❌ 需要GitHub Token才能继续演示")
        return
    
    scraper = GitHubRepoScraper(config)
    
    # 抓取一个简单的仓库信息
    repo_url = "https://github.com/octocat/Hello-World"
    print(f"\n📡 抓取仓库: {repo_url}")
    
    try:
        repo_data = await scraper.scrape_repository(repo_url)
        if repo_data:
            print(f"✅ 仓库信息获取成功:")
            print(f"   - 名称: {repo_data['basic_info']['name']}")
            print(f"   - 描述: {repo_data['basic_info']['description']}")
            print(f"   - 语言: {repo_data['basic_info']['language']}")
            print(f"   - 星标: {repo_data['basic_info']['stargazers_count']}")
            print(f"   - 分支数: {len(repo_data.get('branches', []))}")
        else:
            print("❌ 仓库信息获取失败")
            
    except Exception as e:
        print(f"❌ 抓取异常: {e}")


def main():
    """主函数"""
    try:
        # 运行Token管理演示
        asyncio.run(demo_token_management())
        
        # 运行仓库抓取演示
        asyncio.run(demo_repo_scraping())
        
    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户取消")
    except Exception as e:
        print(f"❌ 演示异常: {e}")


if __name__ == "__main__":
    main()

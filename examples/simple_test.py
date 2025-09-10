#!/usr/bin/env python3
"""简单的GitHub API测试"""
import sys
import asyncio
import aiohttp
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.github.simple_config import GitHubConfig


async def test_github_api():
    """测试GitHub API"""
    print("🧪 GitHub API 连接测试")
    print("=" * 30)
    
    # 加载配置
    config = GitHubConfig()
    
    # 验证配置
    is_valid, message = config.validate()
    if not is_valid:
        print(f"❌ 配置无效: {message}")
        print("\n💡 请先运行: python simple_setup.py")
        return False
    
    print(f"✅ 配置有效: {config.github_token[:10]}...")
    
    # 测试API连接
    try:
        async with aiohttp.ClientSession() as session:
            print("\n📡 测试API连接...")
            
            # 获取用户信息
            async with session.get(
                f"{config.base_url}/user",
                headers=config.headers,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                
                if response.status == 200:
                    user_data = await response.json()
                    print("✅ API连接成功!")
                    print(f"👤 用户: {user_data.get('login', 'unknown')}")
                    print(f"📧 邮箱: {user_data.get('email', 'private')}")
                    
                    # 速率限制信息
                    rate_limit = response.headers.get('X-RateLimit-Limit', 'unknown')
                    rate_remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
                    print(f"🔢 速率限制: {rate_remaining}/{rate_limit}")
                    
                    return True
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API请求失败: HTTP {response.status}")
                    print(f"错误: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ API请求超时")
        return False
    except Exception as e:
        print(f"❌ API请求异常: {e}")
        return False


async def test_repo_access():
    """测试仓库访问"""
    print("\n📦 测试仓库访问...")
    
    config = GitHubConfig()
    
    try:
        async with aiohttp.ClientSession() as session:
            # 测试访问一个公开仓库
            repo_url = f"{config.base_url}/repos/octocat/Hello-World"
            
            async with session.get(
                repo_url,
                headers=config.headers,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                
                if response.status == 200:
                    repo_data = await response.json()
                    print("✅ 仓库访问成功!")
                    print(f"📦 仓库: {repo_data.get('full_name')}")
                    print(f"⭐ 星标: {repo_data.get('stargazers_count', 0)}")
                    print(f"🍴 分叉: {repo_data.get('forks_count', 0)}")
                    return True
                else:
                    print(f"❌ 仓库访问失败: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ 仓库访问异常: {e}")
        return False


def main():
    """主函数"""
    try:
        # 运行测试
        api_ok = asyncio.run(test_github_api())
        
        if api_ok:
            repo_ok = asyncio.run(test_repo_access())
            
            if repo_ok:
                print("\n🎉 所有测试通过!")
                print("现在可以使用GitHub抓取功能了")
            else:
                print("\n⚠️ 部分测试失败")
        else:
            print("\n❌ API测试失败")
            print("请检查Token配置")
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试被取消")
    except Exception as e:
        print(f"❌ 测试异常: {e}")


if __name__ == "__main__":
    main()

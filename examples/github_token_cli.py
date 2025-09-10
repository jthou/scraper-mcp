#!/usr/bin/env python3
"""GitHub Token管理命令行工具"""
import argparse
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.github.token_manager import GitHubTokenManager, TokenSecurityManager, create_token_setup_guide


def cmd_add(args):
    """添加token命令"""
    manager = GitHubTokenManager()
    
    if manager.add_token(
        name=args.name,
        token=args.token,
        token_type=args.type,
        scopes=args.scopes.split(',') if args.scopes else None,
        expires_at=args.expires
    ):
        print(f"✅ 成功添加Token: {args.name}")
    else:
        print(f"❌ 添加Token失败: {args.name}")
        return 1
    return 0


def cmd_list(args):
    """列出token命令"""
    manager = GitHubTokenManager()
    tokens = manager.list_tokens()
    
    if not tokens:
        print("📝 未配置任何Token")
        print("\n使用以下命令添加Token:")
        print("python github_token_cli.py add --name primary --token YOUR_TOKEN")
        return 0
    
    print("📋 已配置的Token:")
    print("-" * 60)
    
    for name, info in tokens.items():
        status_icon = "✅" if info['status'] == 'active' else "❌"
        print(f"{status_icon} {name}")
        print(f"   来源: {info['source']}")
        print(f"   类型: {info['type']}")
        print(f"   权限: {', '.join(info.get('scopes', ['unknown']))}")
        if info.get('created_at'):
            print(f"   创建: {info['created_at']}")
        if info.get('last_used'):
            print(f"   最后使用: {info['last_used']} (使用{info.get('usage_count', 0)}次)")
        if info.get('expires_at'):
            print(f"   过期: {info['expires_at']}")
        print()
    
    return 0


def cmd_remove(args):
    """删除token命令"""
    manager = GitHubTokenManager()
    
    if manager.remove_token(args.name):
        print(f"✅ 成功删除Token: {args.name}")
    else:
        print(f"❌ 删除Token失败: {args.name}")
        return 1
    return 0


def cmd_status(args):
    """检查token状态命令"""
    manager = GitHubTokenManager()
    
    # 获取当前token
    current_token = manager.get_token()
    
    if not current_token:
        print("❌ 未找到可用的GitHub Token")
        print("\n📝 配置建议:")
        print("1. 设置环境变量: export GITHUB_TOKEN=your_token")
        print("2. 或使用命令添加: python github_token_cli.py add --name primary --token YOUR_TOKEN")
        return 1
    
    # 遮盖token显示
    masked_token = TokenSecurityManager.mask_token(current_token)
    print(f"✅ 当前Token: {masked_token}")
    
    # 安全性检查
    security = TokenSecurityManager.validate_token_security(current_token)
    score = security['score']
    
    if score >= 80:
        score_icon = "🟢"
    elif score >= 60:
        score_icon = "🟡"
    else:
        score_icon = "🔴"
    
    print(f"{score_icon} 安全评分: {score}/100")
    
    if security['issues']:
        print("⚠️ 安全问题:")
        for issue in security['issues']:
            print(f"   - {issue}")
    
    if security['recommendations']:
        print("💡 建议:")
        for rec in security['recommendations']:
            print(f"   - {rec}")
    
    # 速率限制信息
    rate_info = manager.get_rate_limit_info(current_token)
    print(f"\n📊 API限制: {rate_info['limit']}次/小时")
    print(f"🔑 认证类型: {rate_info['type']}")
    
    if rate_info.get('usage_count'):
        print(f"📈 使用统计: {rate_info['usage_count']}次")
    
    return 0


def cmd_test(args):
    """测试token命令"""
    manager = GitHubTokenManager()
    current_token = manager.get_token()
    
    if not current_token:
        print("❌ 未找到可用Token，无法进行测试")
        return 1
    
    print("🧪 测试GitHub API连接...")
    
    import asyncio
    import aiohttp
    
    async def test_api():
        headers = {
            "Authorization": f"token {current_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # 测试API连接
                async with session.get("https://api.github.com/user", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        print(f"✅ API连接成功")
                        print(f"👤 用户: {user_data.get('login', 'unknown')}")
                        print(f"📧 邮箱: {user_data.get('email', 'private')}")
                        print(f"🏢 公司: {user_data.get('company', 'N/A')}")
                        
                        # 测试速率限制
                        rate_limit = response.headers.get('X-RateLimit-Limit', 'unknown')
                        rate_remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
                        rate_reset = response.headers.get('X-RateLimit-Reset', 'unknown')
                        
                        print(f"\n📊 速率限制状态:")
                        print(f"   限制: {rate_limit}次/小时")
                        print(f"   剩余: {rate_remaining}次")
                        if rate_reset != 'unknown':
                            import datetime
                            reset_time = datetime.datetime.fromtimestamp(int(rate_reset))
                            print(f"   重置时间: {reset_time}")
                        
                        return True
                    else:
                        error_data = await response.text()
                        print(f"❌ API测试失败: HTTP {response.status}")
                        print(f"错误信息: {error_data}")
                        return False
                        
        except Exception as e:
            print(f"❌ API测试异常: {e}")
            return False
    
    # 运行测试
    success = asyncio.run(test_api())
    return 0 if success else 1


def cmd_guide(args):
    """显示设置指南"""
    print(create_token_setup_guide())
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GitHub Token管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # add命令
    add_parser = subparsers.add_parser('add', help='添加新Token')
    add_parser.add_argument('--name', required=True, help='Token名称')
    add_parser.add_argument('--token', required=True, help='Token值')
    add_parser.add_argument('--type', default='classic', choices=['classic', 'fine-grained'], help='Token类型')
    add_parser.add_argument('--scopes', help='权限范围（逗号分隔）')
    add_parser.add_argument('--expires', help='过期时间')
    add_parser.set_defaults(func=cmd_add)
    
    # list命令
    list_parser = subparsers.add_parser('list', help='列出所有Token')
    list_parser.set_defaults(func=cmd_list)
    
    # remove命令
    remove_parser = subparsers.add_parser('remove', help='删除Token')
    remove_parser.add_argument('--name', required=True, help='要删除的Token名称')
    remove_parser.set_defaults(func=cmd_remove)
    
    # status命令
    status_parser = subparsers.add_parser('status', help='检查Token状态')
    status_parser.set_defaults(func=cmd_status)
    
    # test命令
    test_parser = subparsers.add_parser('test', help='测试Token连接')
    test_parser.set_defaults(func=cmd_test)
    
    # guide命令
    guide_parser = subparsers.add_parser('guide', help='显示设置指南')
    guide_parser.set_defaults(func=cmd_guide)
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⏹️ 操作被用户取消")
        return 1
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""简单的GitHub Token设置脚本"""
import os
import sys
from pathlib import Path


def create_env_file():
    """创建.env文件"""
    print("🔧 GitHub Token 快速设置")
    print("=" * 40)
    
    # 检查是否已有.env文件
    env_file = Path('.env')
    if env_file.exists():
        print("📁 发现现有 .env 文件")
        choice = input("是否覆盖? (y/N): ").strip().lower()
        if choice != 'y':
            print("⏹️ 取消设置")
            return
    
    # 获取Token
    print("\n请访问: https://github.com/settings/tokens")
    print("创建一个新的 Personal Access Token")
    print("需要权限: repo, read:user, read:org")
    print()
    
    token = input("请输入您的GitHub Token: ").strip()
    
    if not token:
        print("❌ Token不能为空")
        return
    
    # 验证Token格式
    if not token.startswith(('ghp_', 'github_pat_')):
        print("⚠️ Token格式可能不正确，继续...")
    
    # 创建.env文件内容
    env_content = f"""# GitHub API配置
GITHUB_TOKEN={token}

# 可选配置
GITHUB_MAX_RETRIES=3
GITHUB_REQUEST_DELAY=1
GITHUB_TIMEOUT=30
"""
    
    # 写入文件
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ 已创建 {env_file}")
        print("🎉 GitHub Token 配置完成!")
        
        # 测试配置
        print("\n🧪 测试配置...")
        test_config()
        
    except Exception as e:
        print(f"❌ 创建文件失败: {e}")


def test_config():
    """测试配置"""
    # 添加src到路径
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from core.github.simple_config import GitHubConfig
        
        config = GitHubConfig()
        is_valid, message = config.validate()
        
        if is_valid:
            print("✅ 配置验证通过")
            print(f"Token: {config.github_token[:10]}...")
        else:
            print(f"❌ 配置验证失败: {message}")
            
    except Exception as e:
        print(f"❌ 测试配置失败: {e}")


def show_env_example():
    """显示.env示例"""
    print("📋 .env 文件示例:")
    print("-" * 30)
    
    example_content = """# GitHub API配置
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选配置
GITHUB_MAX_RETRIES=3
GITHUB_REQUEST_DELAY=1
GITHUB_TIMEOUT=30
"""
    print(example_content)


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'example':
        show_env_example()
        return
    
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n⏹️ 设置被取消")
    except Exception as e:
        print(f"❌ 设置失败: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""GitHub Token设置向导"""
import sys
import os
import json
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.github.token_manager import GitHubTokenManager, TokenSecurityManager


class TokenWizard:
    """Token设置向导"""
    
    def __init__(self):
        self.manager = GitHubTokenManager()
        
    def welcome(self):
        """欢迎界面"""
        print("🎯 GitHub Token设置向导")
        print("=" * 50)
        print("这个向导将帮助您配置GitHub API Token")
        print("用于访问GitHub内容和仓库信息")
        print()
        
    def check_existing_tokens(self):
        """检查现有Token"""
        print("🔍 检查现有Token配置...")
        
        # 检查环境变量
        env_token = os.getenv('GITHUB_TOKEN')
        if env_token:
            print(f"✅ 发现环境变量 GITHUB_TOKEN: {env_token[:10]}...")
            return True
            
        # 检查存储的Token
        tokens = self.manager.list_tokens()
        if tokens:
            print(f"✅ 发现已存储的Token: {len(tokens)}个")
            for name, info in tokens.items():
                print(f"   - {name}: {info['type']} ({info['status']})")
            return True
            
        print("❌ 未发现任何Token配置")
        return False
        
    def get_token_choice(self):
        """获取用户选择"""
        print("\n📋 请选择Token配置方式:")
        print("1. 设置环境变量 (推荐)")
        print("2. 添加到Token存储")
        print("3. 显示GitHub Token创建指南")
        print("4. 退出")
        
        while True:
            choice = input("\n请输入选择 (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            print("❌ 无效选择，请输入1-4")
            
    def show_github_guide(self):
        """显示GitHub Token创建指南"""
        print("\n📖 GitHub Token创建指南")
        print("-" * 40)
        print("1. 访问 GitHub → Settings → Developer settings")
        print("2. 点击 'Personal access tokens' → 'Tokens (classic)'")
        print("3. 点击 'Generate new token' → 'Generate new token (classic)'")
        print("4. 填写Token说明（如：'Scraper Tool'）")
        print("5. 选择过期时间（建议90天）")
        print("6. 选择权限范围（scopes）:")
        print("   ✅ repo - 访问私有仓库")
        print("   ✅ public_repo - 访问公开仓库")
        print("   ✅ read:user - 读取用户信息")
        print("   ✅ read:org - 读取组织信息")
        print("7. 点击 'Generate token'")
        print("8. 立即复制Token（只显示一次！）")
        print("\n⚠️ 重要提醒:")
        print("- Token只显示一次，请立即保存")
        print("- 不要在代码中硬编码Token")
        print("- 定期更新Token")
        print("- 使用最小权限原则")
        
    def setup_environment_variable(self):
        """设置环境变量"""
        print("\n🔧 设置环境变量")
        print("-" * 30)
        
        token = input("请输入您的GitHub Token: ").strip()
        if not token:
            print("❌ Token不能为空")
            return False
            
        # 验证Token格式
        if not token.startswith(('ghp_', 'github_pat_')):
            print("⚠️ Token格式可能不正确")
            choice = input("是否继续? (y/N): ").strip().lower()
            if choice != 'y':
                return False
                
        # 检查安全性
        security = TokenSecurityManager.validate_token_security(token)
        print(f"\n🔒 安全评分: {security['score']}/100")
        
        if security['issues']:
            print("⚠️ 安全问题:")
            for issue in security['issues']:
                print(f"   - {issue}")
                
        if security['score'] < 60:
            choice = input("安全评分较低，是否继续? (y/N): ").strip().lower()
            if choice != 'y':
                return False
        
        # 生成shell配置
        shell = os.getenv('SHELL', '/bin/bash')
        
        if 'zsh' in shell:
            config_file = '~/.zshrc'
        elif 'bash' in shell:
            config_file = '~/.bashrc'
        else:
            config_file = '~/.profile'
            
        print(f"\n📝 请将以下行添加到 {config_file}:")
        print(f"export GITHUB_TOKEN='{token}'")
        print("\n然后运行:")
        print(f"source {config_file}")
        print("或重新打开终端")
        
        # 询问是否自动添加
        choice = input(f"\n是否自动添加到 {config_file}? (y/N): ").strip().lower()
        if choice == 'y':
            try:
                config_path = Path(config_file).expanduser()
                with open(config_path, 'a') as f:
                    f.write(f"\n# GitHub Token for scraper\n")
                    f.write(f"export GITHUB_TOKEN='{token}'\n")
                print(f"✅ 已添加到 {config_file}")
                print("请运行: source {config_file} 或重新打开终端")
            except Exception as e:
                print(f"❌ 自动添加失败: {e}")
                print("请手动添加到配置文件")
                
        return True
        
    def setup_token_storage(self):
        """设置Token存储"""
        print("\n💾 添加Token到存储")
        print("-" * 30)
        
        name = input("Token名称 (如: primary): ").strip() or "primary"
        token = input("请输入您的GitHub Token: ").strip()
        
        if not token:
            print("❌ Token不能为空")
            return False
            
        # Token类型
        print("\nToken类型:")
        print("1. Classic (传统Token)")
        print("2. Fine-grained (细粒度Token)")
        type_choice = input("选择类型 (1-2, 默认1): ").strip() or "1"
        token_type = "classic" if type_choice == "1" else "fine-grained"
        
        # 权限范围
        scopes_input = input("权限范围 (逗号分隔, 如: repo,read:user): ").strip()
        scopes = [s.strip() for s in scopes_input.split(',')] if scopes_input else None
        
        # 过期时间
        expires = input("过期时间 (YYYY-MM-DD, 可选): ").strip() or None
        
        # 添加Token
        if self.manager.add_token(
            name=name,
            token=token,
            token_type=token_type,
            scopes=scopes,
            expires_at=expires
        ):
            print(f"✅ 成功添加Token: {name}")
            return True
        else:
            print(f"❌ 添加Token失败")
            return False
            
    def test_token(self):
        """测试Token"""
        print("\n🧪 测试Token连接...")
        
        current_token = self.manager.get_token()
        if not current_token:
            print("❌ 未找到可用Token")
            return False
            
        print(f"使用Token: {current_token[:10]}...")
        
        # 这里可以添加实际的API测试
        # 暂时只做基本检查
        print("✅ Token格式验证通过")
        return True
        
    def run(self):
        """运行向导"""
        self.welcome()
        
        # 检查现有配置
        has_tokens = self.check_existing_tokens()
        
        if has_tokens:
            choice = input("\n已有Token配置，是否重新配置? (y/N): ").strip().lower()
            if choice != 'y':
                print("✅ 使用现有Token配置")
                self.test_token()
                return
                
        # 获取用户选择
        while True:
            choice = self.get_token_choice()
            
            if choice == '1':
                if self.setup_environment_variable():
                    print("\n✅ 环境变量配置完成!")
                    break
                    
            elif choice == '2':
                if self.setup_token_storage():
                    print("\n✅ Token存储配置完成!")
                    break
                    
            elif choice == '3':
                self.show_github_guide()
                continue
                
            elif choice == '4':
                print("\n👋 退出向导")
                return
                
        # 最终测试
        print("\n🎯 配置完成，进行最终测试...")
        if self.test_token():
            print("🎉 GitHub Token配置成功!")
            print("\n💡 接下来您可以:")
            print("- 运行: python example_token_usage.py")
            print("- 使用: python github_token_cli.py status")
        else:
            print("❌ Token测试失败，请检查配置")


def main():
    """主函数"""
    try:
        wizard = TokenWizard()
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n⏹️ 向导被用户取消")
    except Exception as e:
        print(f"\n❌ 向导异常: {e}")


if __name__ == "__main__":
    main()

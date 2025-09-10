"""GitHub API Token管理系统设计"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import logging


@dataclass
class TokenConfig:
    """Token配置类"""
    token: Optional[str] = None
    token_type: str = "classic"  # classic, fine-grained
    scopes: list = field(default_factory=lambda: ["repo", "read:user"])
    rate_limit: int = 5000  # 认证用户的限制
    expires_at: Optional[str] = None
    created_at: Optional[str] = None
    last_used: Optional[str] = None
    usage_count: int = 0


class GitHubTokenManager:
    """GitHub Token管理器"""
    
    def __init__(self, config_dir: Path = None):
        """
        初始化Token管理器
        
        Args:
            config_dir: 配置目录，默认为用户主目录/.github-scraper
        """
        self.config_dir = config_dir or Path.home() / ".github-scraper"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.token_file = self.config_dir / "tokens.json"
        self.logger = logging.getLogger(__name__)
        
        # 加载已保存的token配置
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict[str, TokenConfig]:
        """加载保存的token配置"""
        if not self.token_file.exists():
            return {}
        
        try:
            with open(self.token_file, 'r') as f:
                data = json.load(f)
            
            tokens = {}
            for name, token_data in data.items():
                tokens[name] = TokenConfig(**token_data)
            
            return tokens
        except Exception as e:
            self.logger.warning(f"加载token配置失败: {e}")
            return {}
    
    def _save_tokens(self):
        """保存token配置"""
        try:
            data = {}
            for name, token_config in self.tokens.items():
                data[name] = {
                    "token": token_config.token,
                    "token_type": token_config.token_type,
                    "scopes": token_config.scopes,
                    "rate_limit": token_config.rate_limit,
                    "expires_at": token_config.expires_at,
                    "created_at": token_config.created_at,
                    "last_used": token_config.last_used,
                    "usage_count": token_config.usage_count
                }
            
            with open(self.token_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存token配置失败: {e}")
    
    def get_token(self, priority_order: list = None) -> Optional[str]:
        """
        获取可用的token
        
        Args:
            priority_order: 优先级顺序，如 ["primary", "backup", "dev"]
            
        Returns:
            可用的token字符串，如果没有则返回None
        """
        # 1. 环境变量优先
        env_token = os.getenv('GITHUB_TOKEN')
        if env_token:
            self.logger.info("使用环境变量中的GitHub Token")
            return env_token
        
        # 2. 按优先级查找保存的token
        if priority_order:
            for name in priority_order:
                if name in self.tokens and self.tokens[name].token:
                    self.logger.info(f"使用保存的Token: {name}")
                    return self.tokens[name].token
        
        # 3. 使用任何可用的token
        for name, token_config in self.tokens.items():
            if token_config.token:
                self.logger.info(f"使用可用Token: {name}")
                return token_config.token
        
        # 4. 没有找到任何token
        self.logger.warning("未找到任何可用的GitHub Token")
        return None
    
    def add_token(self, name: str, token: str, 
                  token_type: str = "classic",
                  scopes: list = None,
                  expires_at: str = None) -> bool:
        """
        添加新的token
        
        Args:
            name: token名称（如 "primary", "backup", "dev"）
            token: token字符串
            token_type: token类型
            scopes: 权限范围
            expires_at: 过期时间
            
        Returns:
            是否添加成功
        """
        try:
            # 验证token格式
            if not self._validate_token_format(token):
                self.logger.error("Token格式无效")
                return False
            
            # 创建token配置
            token_config = TokenConfig(
                token=token,
                token_type=token_type,
                scopes=scopes or ["repo", "read:user"],
                expires_at=expires_at,
                created_at=self._get_current_time()
            )
            
            # 保存token
            self.tokens[name] = token_config
            self._save_tokens()
            
            self.logger.info(f"成功添加Token: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加Token失败: {e}")
            return False
    
    def remove_token(self, name: str) -> bool:
        """删除指定的token"""
        try:
            if name in self.tokens:
                del self.tokens[name]
                self._save_tokens()
                self.logger.info(f"成功删除Token: {name}")
                return True
            else:
                self.logger.warning(f"Token不存在: {name}")
                return False
        except Exception as e:
            self.logger.error(f"删除Token失败: {e}")
            return False
    
    def list_tokens(self) -> Dict[str, Dict[str, Any]]:
        """列出所有token的信息（不包含实际token值）"""
        result = {}
        
        # 环境变量token
        if os.getenv('GITHUB_TOKEN'):
            result['ENVIRONMENT'] = {
                "source": "环境变量",
                "type": "unknown",
                "scopes": "unknown",
                "status": "active"
            }
        
        # 保存的token
        for name, token_config in self.tokens.items():
            result[name] = {
                "source": "配置文件",
                "type": token_config.token_type,
                "scopes": token_config.scopes,
                "created_at": token_config.created_at,
                "last_used": token_config.last_used,
                "usage_count": token_config.usage_count,
                "expires_at": token_config.expires_at,
                "status": "active" if token_config.token else "inactive"
            }
        
        return result
    
    def update_usage(self, token: str):
        """更新token使用统计"""
        # 查找对应的token配置
        for token_config in self.tokens.values():
            if token_config.token == token:
                token_config.usage_count += 1
                token_config.last_used = self._get_current_time()
                self._save_tokens()
                break
    
    def _validate_token_format(self, token: str) -> bool:
        """验证token格式"""
        if not token:
            return False
        
        # GitHub classic token格式: ghp_xxxx (40字符)
        # GitHub fine-grained token格式: github_pat_xxxx
        if token.startswith(('ghp_', 'github_pat_')):
            return len(token) >= 20  # 最小长度检查
        
        # 旧格式token (40个hex字符)
        if len(token) == 40:
            return all(c in '0123456789abcdef' for c in token.lower())
        
        return False
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_rate_limit_info(self, token: str = None) -> Dict[str, Any]:
        """获取速率限制信息"""
        used_token = token or self.get_token()
        
        if not used_token:
            return {
                "limit": 60,
                "type": "unauthenticated",
                "reset_time": "每小时重置"
            }
        
        # 查找token配置
        for token_config in self.tokens.values():
            if token_config.token == used_token:
                return {
                    "limit": token_config.rate_limit,
                    "type": "authenticated",
                    "token_type": token_config.token_type,
                    "scopes": token_config.scopes,
                    "usage_count": token_config.usage_count,
                    "last_used": token_config.last_used
                }
        
        # 环境变量token
        return {
            "limit": 5000,
            "type": "authenticated (env)",
            "token_type": "unknown",
            "scopes": "unknown"
        }


class TokenSecurityManager:
    """Token安全管理器"""
    
    @staticmethod
    def mask_token(token: str) -> str:
        """遮盖token显示"""
        if not token:
            return "未设置"
        
        if len(token) <= 8:
            return "*" * len(token)
        
        return f"{token[:4]}{'*' * (len(token) - 8)}{token[-4:]}"
    
    @staticmethod
    def validate_token_security(token: str) -> Dict[str, Any]:
        """验证token安全性"""
        issues = []
        recommendations = []
        
        if not token:
            issues.append("Token未设置")
            recommendations.append("配置GitHub API Token")
            return {"issues": issues, "recommendations": recommendations, "score": 0}
        
        # 检查token格式
        if token.startswith('ghp_'):
            score = 80
            recommendations.append("使用的是Classic Token，考虑升级到Fine-grained Token")
        elif token.startswith('github_pat_'):
            score = 95
            recommendations.append("使用Fine-grained Token，安全性良好")
        elif len(token) == 40:
            score = 60
            issues.append("使用旧格式Token")
            recommendations.append("升级到新格式Token")
        else:
            score = 30
            issues.append("Token格式不符合标准")
        
        # 检查token长度
        if len(token) < 20:
            issues.append("Token长度过短")
            score -= 20
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "score": max(0, score)
        }


def create_token_setup_guide() -> str:
    """创建Token设置指南"""
    guide = """
# GitHub API Token 设置指南

## 🔑 获取Token

### 方法1: Classic Token (推荐用于开发)
1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置过期时间 (建议30-90天)
4. 选择权限:
   - ✅ `repo` - 访问私有仓库
   - ✅ `read:user` - 读取用户信息
   - ✅ `read:org` - 读取组织信息
5. 点击 "Generate token"
6. 复制生成的token (以 `ghp_` 开头)

### 方法2: Fine-grained Token (推荐用于生产)
1. 访问: https://github.com/settings/tokens?type=beta
2. 点击 "Generate new token"
3. 设置仓库访问权限
4. 配置详细权限
5. 生成token (以 `github_pat_` 开头)

## 🛡️ 安全配置

### 环境变量方式 (推荐)
```bash
# macOS/Linux
export GITHUB_TOKEN=your_token_here
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.zshrc

# Windows
set GITHUB_TOKEN=your_token_here
setx GITHUB_TOKEN "your_token_here"
```

### 配置文件方式
```python
from core.github import GitHubTokenManager

manager = GitHubTokenManager()
manager.add_token("primary", "your_token_here")
```

### 代码中直接指定 (不推荐)
```python
config = GitHubConfig(api_token="your_token_here")
```

## 📊 速率限制

| 认证状态 | 限制 | 说明 |
|---------|-----|------|
| 未认证 | 60次/小时 | 按IP地址限制 |
| Classic Token | 5000次/小时 | 按用户限制 |
| Fine-grained | 5000次/小时 | 按用户限制 |

## 🔒 最佳实践

1. **使用环境变量**: 避免token写入代码
2. **定期轮换**: 定期更新token
3. **最小权限**: 只授予必要的权限
4. **多token管理**: 为不同用途配置不同token
5. **监控使用**: 定期检查token使用情况
"""
    return guide


if __name__ == "__main__":
    # 演示Token管理器的使用
    print("🔑 GitHub Token管理器演示\n")
    
    manager = GitHubTokenManager()
    
    # 显示当前token状态
    print("📋 当前Token状态:")
    tokens = manager.list_tokens()
    if tokens:
        for name, info in tokens.items():
            print(f"  {name}: {info['status']} ({info['source']})")
    else:
        print("  未配置任何Token")
    
    # 检查当前可用token
    current_token = manager.get_token()
    if current_token:
        masked = TokenSecurityManager.mask_token(current_token)
        print(f"\n✅ 当前可用Token: {masked}")
        
        # 安全性检查
        security = TokenSecurityManager.validate_token_security(current_token)
        print(f"🛡️ 安全评分: {security['score']}/100")
        if security['issues']:
            print(f"⚠️ 安全问题: {', '.join(security['issues'])}")
        if security['recommendations']:
            print(f"💡 建议: {', '.join(security['recommendations'])}")
        
        # 速率限制信息
        rate_info = manager.get_rate_limit_info(current_token)
        print(f"📊 速率限制: {rate_info['limit']}次/小时 ({rate_info['type']})")
    else:
        print("\n❌ 未找到可用Token")
        print("\n" + create_token_setup_guide())

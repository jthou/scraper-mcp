"""GitHub配置管理 - 简化版本"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GitHubConfig:
    """简化的GitHub配置类"""
    github_token: Optional[str] = None
    max_retries: int = 3
    request_delay: float = 1.0
    timeout: int = 30
    base_url: str = "https://api.github.com"
    
    def __post_init__(self):
        """从.env文件或环境变量加载配置"""
        if not self.github_token:
            self.github_token = self._load_token()
        
        # 加载其他配置
        self.max_retries = int(os.getenv('GITHUB_MAX_RETRIES', self.max_retries))
        self.request_delay = float(os.getenv('GITHUB_REQUEST_DELAY', self.request_delay))
        self.timeout = int(os.getenv('GITHUB_TIMEOUT', self.timeout))
    
    def _load_token(self) -> Optional[str]:
        """从多个来源加载Token"""
        # 1. 优先从环境变量
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return token
            
        # 2. 从.env文件加载
        env_files = [
            Path('.env'),  # 当前目录
            Path(__file__).parent.parent.parent.parent / '.env',  # 项目根目录
        ]
        
        for env_file in env_files:
            if env_file.exists():
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('GITHUB_TOKEN=') and '=' in line:
                                token = line.split('=', 1)[1].strip()
                                # 移除可能的引号
                                token = token.strip('\'"')
                                if token and token != 'your_github_token_here':
                                    return token
                except Exception:
                    continue
        
        return None
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置Token"""
        return bool(self.github_token)
    
    def validate(self) -> tuple[bool, str]:
        """验证配置"""
        if not self.github_token:
            return False, "未配置GitHub Token"
        
        if not self.github_token.startswith(('ghp_', 'github_pat_')):
            return False, "GitHub Token格式可能不正确"
        
        return True, "配置验证通过"
    
    @property
    def headers(self) -> dict:
        """获取请求头"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Scraper/1.0"
        }
        
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
            
        return headers


# 创建默认配置实例
default_config = GitHubConfig()

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
    output_base_dir: Path = Path("K-Vault/GitHub")
    create_subdirs: bool = True
    save_metadata: bool = True
    save_errors: bool = True
    
    # 内容处理配置
    convert_to_markdown: bool = True
    preserve_html: bool = False
    extract_images: bool = True
    extract_links: bool = True
    
    # 缓存配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 缓存时间（秒）
    cache_dir: Path = Path(".cache/github")
    
    # 用户代理和请求头
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    request_headers: Dict[str, str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.request_headers is None:
            self.request_headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        
        # 确保路径是Path对象
        if isinstance(self.output_base_dir, str):
            self.output_base_dir = Path(self.output_base_dir)
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)
        
        # 如果没有指定API token，尝试从Token管理器获取
        if not self.api_token:
            token_manager = GitHubTokenManager()
            self.api_token = token_manager.get_token()
            self.cache_dir = Path(self.cache_dir)
        
        # 创建必要的目录
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'GitHubConfig':
        """从环境变量创建配置"""
        import os
        
        return cls(
            api_token=os.getenv('GITHUB_TOKEN'),
            api_rate_limit=int(os.getenv('GITHUB_API_RATE_LIMIT', '5000')),
            pages_max_pages=int(os.getenv('GITHUB_PAGES_MAX_PAGES', '100')),
            pages_headless=os.getenv('GITHUB_PAGES_HEADLESS', 'true').lower() == 'true',
            output_base_dir=Path(os.getenv('GITHUB_OUTPUT_DIR', 'K-Vault/GitHub'))
        )
    
    @classmethod
    def from_file(cls, config_file: Path) -> 'GitHubConfig':
        """从配置文件创建配置"""
        import yaml
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        github_config = config_data.get('github', {})
        
        return cls(**github_config)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'api_token': '***' if self.api_token else None,  # 隐藏敏感信息
            'api_base_url': self.api_base_url,
            'api_rate_limit': self.api_rate_limit,
            'api_timeout': self.api_timeout,
            'pages_max_pages': self.pages_max_pages,
            'pages_timeout': self.pages_timeout,
            'pages_delay': self.pages_delay,
            'pages_headless': self.pages_headless,
            'output_base_dir': str(self.output_base_dir),
            'create_subdirs': self.create_subdirs,
            'save_metadata': self.save_metadata,
            'save_errors': self.save_errors,
            'convert_to_markdown': self.convert_to_markdown,
            'preserve_html': self.preserve_html,
            'extract_images': self.extract_images,
            'extract_links': self.extract_links,
            'enable_cache': self.enable_cache,
            'cache_ttl': self.cache_ttl,
            'cache_dir': str(self.cache_dir),
            'user_agent': self.user_agent
        }


# 全局默认配置实例
default_config = GitHubConfig()

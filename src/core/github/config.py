"""GitHub模块配置"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class GitHubConfig:
    """GitHub模块统一配置"""
    
    # GitHub API配置
    api_token: Optional[str] = None
    api_base_url: str = "https://api.github.com"
    api_rate_limit: int = 5000  # 认证用户限制
    api_timeout: int = 30
    
    # 仓库抓取配置
    repo_max_files: int = 200
    repo_delay: float = 0.1  # API调用间延迟（秒）
    max_file_size: int = 1024 * 1024  # 1MB，单个文件大小限制
    
    # Pages抓取配置
    pages_max_pages: int = 100
    pages_timeout: int = 30
    pages_delay: float = 0.5  # 页面间延迟（秒）
    pages_headless: bool = True
    
    # 输出配置
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

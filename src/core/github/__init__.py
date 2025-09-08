"""GitHub内容抓取模块

这个模块提供了完整的GitHub内容抓取功能，包括：
- GitHub API仓库内容抓取
- GitHub Pages文档站点抓取  
- 统一的内容抓取接口
- 灵活的配置管理
- 实用工具函数

主要组件：
- GitHubConfig: 配置管理
- GitHubUtils: 实用工具函数
- GitHubRepoScraper: 仓库API抓取器
- GitHubPagesScraper: Pages站点抓取器
- GitHubContentScraper: 统一内容抓取器
"""

from .config import GitHubConfig, default_config
from .utils import GitHubUtils, AsyncRateLimiter, ContentExtractor
from .repo_scraper import GitHubRepoScraper, scrape_github_repository, get_github_repository_info
from .pages_scraper import GitHubPagesScraper, scrape_github_pages, discover_github_pages
from .content_scraper import GitHubContentScraper, scrape_github_content, discover_github_content

__all__ = [
    # 配置
    "GitHubConfig",
    "default_config",
    
    # 工具类
    "GitHubUtils", 
    "AsyncRateLimiter",
    "ContentExtractor",
    
    # 抓取器类
    "GitHubRepoScraper",
    "GitHubPagesScraper", 
    "GitHubContentScraper",
    
    # 便捷函数
    "scrape_github_repository",
    "get_github_repository_info",
    "scrape_github_pages",
    "discover_github_pages",
    "scrape_github_content",
    "discover_github_content",
]

# 版本信息
__version__ = '2.0.0'
__author__ = 'GitHub Scraper Team'
__description__ = 'GitHub内容抓取模块集合 - 重构版'

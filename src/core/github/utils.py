"""GitHub通用工具函数"""
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse, urljoin
import aiohttp
import asyncio


class GitHubUtils:
    """GitHub模块通用工具类"""
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 100) -> str:
        """生成安全的文件名"""
        # 移除特殊字符
        safe_filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # 替换空格为下划线
        safe_filename = re.sub(r'\s+', '_', safe_filename)
        
        # 移除多余的下划线
        safe_filename = re.sub(r'_+', '_', safe_filename).strip('_')
        
        # 限制长度
        if len(safe_filename) > max_length:
            # 保留文件扩展名
            if '.' in safe_filename:
                name, ext = safe_filename.rsplit('.', 1)
                max_name_length = max_length - len(ext) - 1
                safe_filename = name[:max_name_length] + '.' + ext
            else:
                safe_filename = safe_filename[:max_length]
        
        return safe_filename or 'untitled'
    
    @staticmethod
    def extract_github_info(url: str) -> Optional[Dict[str, str]]:
        """从GitHub URL提取owner和repo信息"""
        patterns = [
            r'github\.com/([^/]+)/([^/]+)',
            r'([^.]+)\.github\.io/([^/]+)',
            r'([^.]+)\.github\.io/?$'  # 用户主页
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                if len(match.groups()) == 2:
                    return {
                        'owner': match.group(1),
                        'repo': match.group(2)
                    }
                else:  # 用户主页情况
                    return {
                        'owner': match.group(1),
                        'repo': None
                    }
        
        return None
    
    @staticmethod
    def is_github_url(url: str) -> bool:
        """判断是否为GitHub相关URL"""
        github_domains = [
            'github.com',
            'github.io',
            'raw.githubusercontent.com',
            'gist.github.com'
        ]
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        return any(domain.endswith(gh_domain) for gh_domain in github_domains)
    
    @staticmethod
    def is_github_pages_url(url: str) -> bool:
        """判断是否为GitHub Pages URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 直接的github.io域名
        if domain.endswith('.github.io'):
            return True
        
        # 自定义域名需要其他方式验证
        return False
    
    @staticmethod
    def generate_cache_key(url: str, **kwargs) -> str:
        """生成缓存键"""
        # 组合URL和参数
        cache_data = {'url': url, **kwargs}
        cache_string = json.dumps(cache_data, sort_keys=True)
        
        # 生成哈希
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    @staticmethod
    def get_url_domain(url: str) -> str:
        """获取URL的域名"""
        return urlparse(url).netloc
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """标准化URL"""
        # 移除尾部斜杠
        url = url.rstrip('/')
        
        # 确保有协议
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @staticmethod
    def create_directory_structure(base_path: Path, owner: str, repo: str = None) -> Path:
        """创建标准的目录结构"""
        if repo:
            dir_name = f"{owner}-{repo}"
        else:
            dir_name = owner
        
        target_dir = base_path / dir_name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        subdirs = ['pages', 'metadata', 'assets', 'cache']
        for subdir in subdirs:
            (target_dir / subdir).mkdir(exist_ok=True)
        
        return target_dir
    
    @staticmethod
    def save_json(data: Any, file_path: Path, indent: int = 2) -> bool:
        """保存JSON数据"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"保存JSON失败 {file_path}: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: Path) -> Optional[Any]:
        """加载JSON数据"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载JSON失败 {file_path}: {e}")
        return None
    
    @staticmethod
    def save_markdown(content: str, file_path: Path, metadata: Dict[str, Any] = None) -> bool:
        """保存Markdown文件（可包含元数据）"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if metadata:
                    # 添加元数据头部
                    f.write("---\n")
                    for key, value in metadata.items():
                        f.write(f"{key}: {value}\n")
                    f.write("---\n\n")
                
                f.write(content)
            return True
        except Exception as e:
            print(f"保存Markdown失败 {file_path}: {e}")
            return False
    
    @staticmethod
    def filter_urls(urls: List[str], base_url: str, exclude_patterns: List[str] = None) -> List[str]:
        """过滤URL列表"""
        if exclude_patterns is None:
            exclude_patterns = [
                r'\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|pdf)$',
                r'/api/',
                r'/admin/',
                r'/login',
                r'/logout',
                r'#'
            ]
        
        base_domain = urlparse(base_url).netloc
        filtered_urls = []
        
        for url in urls:
            # 转换为绝对URL
            if url.startswith('/'):
                url = urljoin(base_url, url)
            elif not url.startswith(('http://', 'https://')):
                continue
            
            # 检查域名
            if urlparse(url).netloc != base_domain:
                continue
            
            # 检查排除模式
            should_exclude = False
            for pattern in exclude_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    should_exclude = True
                    break
            
            if not should_exclude:
                filtered_urls.append(url)
        
        return list(set(filtered_urls))  # 去重


class AsyncRateLimiter:
    """异步速率限制器"""
    
    def __init__(self, max_requests: int, time_window: int = 3600):
        """
        初始化速率限制器
        
        Args:
            max_requests: 时间窗口内的最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """获取请求许可"""
        async with self._lock:
            now = datetime.now().timestamp()
            
            # 清理过期的请求记录
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            # 检查是否超过限制
            if len(self.requests) >= self.max_requests:
                # 计算需要等待的时间
                oldest_request = min(self.requests)
                wait_time = self.time_window - (now - oldest_request)
                
                if wait_time > 0:
                    print(f"⏰ 速率限制：等待 {wait_time:.1f} 秒")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()  # 递归重试
            
            # 记录本次请求
            self.requests.append(now)
    
    def get_remaining_requests(self) -> int:
        """获取剩余请求数"""
        now = datetime.now().timestamp()
        recent_requests = [req_time for req_time in self.requests 
                         if now - req_time < self.time_window]
        return max(0, self.max_requests - len(recent_requests))


class ContentExtractor:
    """内容提取工具"""
    
    @staticmethod
    def extract_text_content(html: str, min_length: int = 50) -> str:
        """从HTML提取纯文本内容"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 获取文本
        text = soup.get_text()
        
        # 清理文本
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text if len(text) >= min_length else ""
    
    @staticmethod
    def extract_links(html: str, base_url: str) -> List[Dict[str, str]]:
        """从HTML提取链接"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # 转换为绝对URL
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith(('http://', 'https://')):
                continue
            
            if href and text:
                links.append({
                    'url': href,
                    'text': text,
                    'title': link.get('title', '')
                })
        
        return links
    
    @staticmethod
    def extract_images(html: str, base_url: str) -> List[Dict[str, str]]:
        """从HTML提取图片"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            
            # 转换为绝对URL
            if src.startswith('/'):
                src = urljoin(base_url, src)
            elif not src.startswith(('http://', 'https://')):
                continue
            
            if src:
                images.append({
                    'url': src,
                    'alt': alt,
                    'title': img.get('title', '')
                })
        
        return images

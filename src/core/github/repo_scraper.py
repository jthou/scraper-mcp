"""GitHub仓库内容抓取器 - 使用GitHub API"""
import asyncio
import aiohttp
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import quote

from .config import GitHubConfig, default_config
from .utils import GitHubUtils, AsyncRateLimiter


class GitHubRepoScraper:
    """GitHub仓库内容抓取器 - 基于GitHub API"""
    
    def __init__(self, config: GitHubConfig = None):
        """
        初始化GitHub仓库抓取器
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or default_config
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = AsyncRateLimiter(
            self.config.api_rate_limit, 
            3600  # 每小时
        )
        
        # 构建请求头
        self.headers = self.config.request_headers.copy()
        if self.config.api_token:
            self.headers['Authorization'] = f'token {self.config.api_token}'
        
        # 创建输出目录
        self.output_dir = self.config.output_base_dir / "Repositories"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API端点
        self.api_base = "https://api.github.com"
        
        # 支持的文件类型
        self.text_extensions = {
            '.md', '.markdown', '.rst', '.txt', '.py', '.js', '.ts', '.java',
            '.cpp', '.c', '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php',
            '.html', '.css', '.scss', '.sass', '.json', '.yaml', '.yml',
            '.xml', '.toml', '.ini', '.cfg', '.conf', '.sh', '.bash',
            '.dockerfile', '.makefile', '.cmake', '.gradle', '.maven'
        }
        
        # 文档相关文件模式
        self.doc_patterns = [
            'readme', 'contributing', 'changelog', 'license', 'install',
            'usage', 'api', 'guide', 'tutorial', 'example', 'demo',
            'doc', 'docs', 'documentation', 'wiki', 'faq', 'help'
        ]
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.config.api_timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        获取仓库基本信息
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            仓库信息字典
        """
        print(f"📋 获取仓库信息: {owner}/{repo}")
        
        try:
            await self.rate_limiter.acquire()
            
            url = f"{self.api_base}/repos/{owner}/{repo}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    repo_data = await response.json()
                    
                    # 提取有用信息
                    return {
                        "status": "success",
                        "owner": repo_data.get("owner", {}).get("login"),
                        "name": repo_data.get("name"),
                        "full_name": repo_data.get("full_name"),
                        "description": repo_data.get("description"),
                        "language": repo_data.get("language"),
                        "languages_url": repo_data.get("languages_url"),
                        "size": repo_data.get("size"),
                        "stargazers_count": repo_data.get("stargazers_count"),
                        "forks_count": repo_data.get("forks_count"),
                        "created_at": repo_data.get("created_at"),
                        "updated_at": repo_data.get("updated_at"),
                        "pushed_at": repo_data.get("pushed_at"),
                        "default_branch": repo_data.get("default_branch"),
                        "topics": repo_data.get("topics", []),
                        "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                        "has_wiki": repo_data.get("has_wiki"),
                        "has_pages": repo_data.get("has_pages"),
                        "homepage": repo_data.get("homepage"),
                        "archive_url": repo_data.get("archive_url"),
                        "contents_url": repo_data.get("contents_url"),
                        "documentation_url": repo_data.get("documentation"),
                        "fetched_at": datetime.now().isoformat()
                    }
                elif response.status == 404:
                    return {
                        "status": "not_found",
                        "owner": owner,
                        "name": repo,
                        "error": "Repository not found",
                        "fetched_at": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "error",
                        "owner": owner,
                        "name": repo,
                        "error": f"HTTP {response.status}: {await response.text()}",
                        "fetched_at": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "owner": owner,
                "name": repo,
                "error": str(e),
                "fetched_at": datetime.now().isoformat()
            }
    
    async def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        获取仓库使用的编程语言统计
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            语言统计字典 (语言名: 字节数)
        """
        try:
            await self.rate_limiter.acquire()
            
            url = f"{self.api_base}/repos/{owner}/{repo}/languages"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
        except Exception:
            return {}
    
    async def list_repository_contents(self, owner: str, repo: str, 
                                     path: str = "", 
                                     branch: str = None) -> List[Dict[str, Any]]:
        """
        列出仓库目录内容
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 目录路径（默认为根目录）
            branch: 分支名（默认为主分支）
            
        Returns:
            文件和目录列表
        """
        try:
            await self.rate_limiter.acquire()
            
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            params = {}
            if branch:
                params['ref'] = branch
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    contents = await response.json()
                    
                    # 如果返回单个文件，转换为列表
                    if isinstance(contents, dict):
                        contents = [contents]
                    
                    return contents
                else:
                    return []
                    
        except Exception as e:
            print(f"⚠️ 列出目录内容失败 {owner}/{repo}/{path}: {e}")
            return []
    
    async def get_file_content(self, owner: str, repo: str, 
                              file_path: str, 
                              branch: str = None) -> Optional[Dict[str, Any]]:
        """
        获取文件内容
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            file_path: 文件路径
            branch: 分支名
            
        Returns:
            文件内容字典或None
        """
        try:
            await self.rate_limiter.acquire()
            
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{file_path}"
            params = {}
            if branch:
                params['ref'] = branch
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    file_data = await response.json()
                    
                    # 如果是文件（不是目录）
                    if file_data.get('type') == 'file':
                        content = file_data.get('content', '')
                        encoding = file_data.get('encoding', 'base64')
                        
                        # 解码内容
                        if encoding == 'base64':
                            try:
                                decoded_content = base64.b64decode(content).decode('utf-8')
                            except UnicodeDecodeError:
                                # 如果是二进制文件，返回base64内容
                                decoded_content = content
                                encoding = 'base64'
                        else:
                            decoded_content = content
                        
                        return {
                            "status": "success",
                            "path": file_data.get('path'),
                            "name": file_data.get('name'),
                            "content": decoded_content,
                            "encoding": encoding,
                            "size": file_data.get('size'),
                            "sha": file_data.get('sha'),
                            "download_url": file_data.get('download_url'),
                            "html_url": file_data.get('html_url'),
                            "retrieved_at": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "path": file_path,
                            "error": "Path is a directory, not a file",
                            "retrieved_at": datetime.now().isoformat()
                        }
                elif response.status == 404:
                    return {
                        "status": "not_found",
                        "path": file_path,
                        "error": "File not found",
                        "retrieved_at": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "error",
                        "path": file_path,
                        "error": f"HTTP {response.status}",
                        "retrieved_at": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "path": file_path,
                "error": str(e),
                "retrieved_at": datetime.now().isoformat()
            }
    
    async def scrape_repository_documentation(self, owner: str, repo: str, 
                                            max_files: int = None,
                                            include_code: bool = True) -> Dict[str, Any]:
        """
        抓取仓库的文档内容
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            max_files: 最大文件数量限制
            include_code: 是否包含代码文件
            
        Returns:
            抓取结果字典
        """
        max_files = max_files or self.config.repo_max_files
        
        print(f"📚 开始抓取仓库文档: {owner}/{repo}")
        print(f"📊 最大文件数: {max_files}")
        
        # 创建输出目录
        repo_dir = self.output_dir / f"{owner}_{repo}"
        repo_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 获取仓库基本信息
            repo_info = await self.get_repository_info(owner, repo)
            if repo_info.get("status") != "success":
                return repo_info
            
            # 获取语言统计
            languages = await self.get_repository_languages(owner, repo)
            
            # 递归收集所有文件
            all_files = await self._collect_all_files(owner, repo, "", max_files)
            
            # 过滤文档相关文件
            documentation_files = self._filter_documentation_files(all_files, include_code)
            
            print(f"📋 发现 {len(all_files)} 个文件，{len(documentation_files)} 个文档文件")
            
            # 抓取文件内容
            extracted_files = []
            for i, file_info in enumerate(documentation_files[:max_files], 1):
                print(f"📄 抓取文件 {i}/{min(len(documentation_files), max_files)}: {file_info['path']}")
                
                file_content = await self.get_file_content(owner, repo, file_info['path'])
                if file_content and file_content.get("status") == "success":
                    # 添加文件类型信息
                    file_content["file_type"] = self._classify_file_type(file_info['path'])
                    file_content["priority"] = self._calculate_file_priority(file_info['path'])
                    extracted_files.append(file_content)
                
                # API 限制延迟
                if self.config.repo_delay > 0:
                    await asyncio.sleep(self.config.repo_delay)
            
            # 按优先级排序
            extracted_files.sort(key=lambda x: x.get("priority", 0), reverse=True)
            
            # 构建结果
            result = {
                "status": "success",
                "repository": repo_info,
                "languages": languages,
                "scrape_summary": {
                    "total_files_found": len(all_files),
                    "documentation_files": len(documentation_files),
                    "extracted_files": len(extracted_files),
                    "scraped_at": datetime.now().isoformat(),
                    "config_used": self.config.to_dict()
                },
                "files": extracted_files
            }
            
            # 保存结果
            if self.config.save_metadata:
                await self._save_repository_content(result, repo_dir)
            
            return result
            
        except Exception as e:
            print(f"❌ 抓取仓库失败: {e}")
            return {
                "status": "error",
                "owner": owner,
                "repo": repo,
                "error": str(e),
                "scraped_at": datetime.now().isoformat()
            }
    
    async def _collect_all_files(self, owner: str, repo: str, path: str, 
                               max_files: int, collected: List = None) -> List[Dict[str, Any]]:
        """递归收集所有文件信息"""
        if collected is None:
            collected = []
        
        if len(collected) >= max_files:
            return collected
        
        contents = await self.list_repository_contents(owner, repo, path)
        
        for item in contents:
            if len(collected) >= max_files:
                break
            
            if item.get('type') == 'file':
                collected.append({
                    'path': item.get('path'),
                    'name': item.get('name'),
                    'size': item.get('size'),
                    'download_url': item.get('download_url'),
                    'html_url': item.get('html_url')
                })
            elif item.get('type') == 'dir':
                # 递归进入子目录
                await self._collect_all_files(owner, repo, item.get('path'), 
                                            max_files, collected)
        
        return collected
    
    def _filter_documentation_files(self, files: List[Dict[str, Any]], 
                                   include_code: bool) -> List[Dict[str, Any]]:
        """过滤文档相关文件"""
        doc_files = []
        
        for file_info in files:
            path = file_info.get('path', '').lower()
            name = file_info.get('name', '').lower()
            
            # 检查是否为文档文件
            is_doc_file = False
            
            # 1. 检查文档相关的文件名模式
            for pattern in self.doc_patterns:
                if pattern in name or pattern in path:
                    is_doc_file = True
                    break
            
            # 2. 检查文件扩展名
            file_ext = Path(path).suffix.lower()
            if file_ext in self.text_extensions:
                if file_ext in ['.md', '.rst', '.txt']:
                    is_doc_file = True  # 总是包含文档格式
                elif include_code and file_ext in self.text_extensions:
                    is_doc_file = True  # 如果包含代码文件
            
            # 3. 特殊文件（无扩展名但重要）
            if name in ['readme', 'license', 'contributing', 'changelog', 'makefile', 'dockerfile']:
                is_doc_file = True
            
            # 4. 过滤掉太大的文件
            if file_info.get('size', 0) > self.config.max_file_size:
                is_doc_file = False
            
            if is_doc_file:
                doc_files.append(file_info)
        
        return doc_files
    
    def _classify_file_type(self, path: str) -> str:
        """分类文件类型"""
        path_lower = path.lower()
        name = Path(path).name.lower()
        ext = Path(path).suffix.lower()
        
        # 文档文件
        if any(pattern in path_lower for pattern in ['readme', 'doc', 'guide', 'tutorial']):
            return "documentation"
        
        # 配置文件
        if ext in ['.yaml', '.yml', '.json', '.toml', '.ini', '.cfg', '.conf']:
            return "configuration"
        
        # 构建文件
        if name in ['makefile', 'dockerfile', 'cmake'] or ext in ['.gradle', '.maven']:
            return "build"
        
        # 代码文件
        if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb']:
            return "code"
        
        # 标记文档
        if ext in ['.md', '.rst', '.txt']:
            return "markup"
        
        # 许可证和法律文件
        if any(pattern in name for pattern in ['license', 'copyright', 'legal']):
            return "legal"
        
        return "other"
    
    def _calculate_file_priority(self, path: str) -> int:
        """计算文件优先级（用于排序）"""
        path_lower = path.lower()
        name = Path(path).name.lower()
        ext = Path(path).suffix.lower()
        
        priority = 0
        
        # README文件最高优先级
        if 'readme' in name:
            priority += 100
        
        # 其他重要文档
        high_priority_patterns = ['contributing', 'changelog', 'license', 'install', 'usage', 'api']
        for pattern in high_priority_patterns:
            if pattern in name:
                priority += 80
                break
        
        # 文档格式文件
        if ext in ['.md', '.rst']:
            priority += 60
        elif ext == '.txt':
            priority += 40
        
        # 文档目录中的文件
        if 'doc' in path_lower or 'guide' in path_lower:
            priority += 30
        
        # 根目录文件优先级更高
        if '/' not in path or path.count('/') == 1:
            priority += 20
        
        # 配置文件
        if ext in ['.yaml', '.yml', '.json']:
            priority += 10
        
        return priority
    
    async def _save_repository_content(self, result: Dict[str, Any], repo_dir: Path):
        """保存仓库内容"""
        repo_info = result["repository"]
        
        # 保存元数据
        metadata = {
            "repository": repo_info,
            "languages": result["languages"],
            "scrape_summary": result["scrape_summary"]
        }
        
        metadata_file = repo_dir / "metadata.json"
        GitHubUtils.save_json(metadata, metadata_file)
        
        # 保存每个文件的内容
        files_dir = repo_dir / "files"
        files_dir.mkdir(exist_ok=True)
        
        for file_data in result["files"]:
            if file_data.get("status") == "success" and file_data.get("encoding") != "base64":
                # 生成安全的文件名
                original_path = file_data["path"]
                safe_path = GitHubUtils.sanitize_filename(original_path.replace('/', '_'), 100)
                
                file_ext = Path(original_path).suffix
                if not file_ext:
                    file_ext = '.txt'
                
                filename = f"{safe_path}{file_ext}"
                output_file = files_dir / filename
                
                # 构建文件内容
                file_content = f"# {original_path}\n\n"
                file_content += f"**仓库**: {repo_info['full_name']}\n"
                file_content += f"**文件类型**: {file_data.get('file_type', 'unknown')}\n"
                file_content += f"**大小**: {file_data.get('size', 0)} bytes\n"
                file_content += f"**抓取时间**: {file_data['retrieved_at']}\n"
                file_content += f"**原始URL**: {file_data.get('html_url', '')}\n\n"
                file_content += "---\n\n"
                file_content += file_data["content"]
                
                # 保存文件
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(file_content)
        
        # 生成总结报告
        self._generate_repository_summary(result, repo_dir)
        
        print(f"📁 仓库内容已保存到: {repo_dir}")
    
    def _generate_repository_summary(self, result: Dict[str, Any], repo_dir: Path):
        """生成仓库总结报告"""
        summary_file = repo_dir / "README.md"
        
        repo = result["repository"]
        summary = result["scrape_summary"]
        languages = result.get("languages", {})
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {repo['full_name']} 仓库抓取报告\n\n")
            
            f.write("## 仓库信息\n\n")
            f.write(f"**描述**: {repo.get('description', 'N/A')}\n")
            f.write(f"**主要语言**: {repo.get('language', 'N/A')}\n")
            f.write(f"**星标数**: {repo.get('stargazers_count', 0):,}\n")
            f.write(f"**Fork数**: {repo.get('forks_count', 0):,}\n")
            f.write(f"**大小**: {repo.get('size', 0):,} KB\n")
            f.write(f"**创建时间**: {repo.get('created_at', 'N/A')}\n")
            f.write(f"**更新时间**: {repo.get('updated_at', 'N/A')}\n")
            f.write(f"**主页**: {repo.get('homepage', 'N/A')}\n")
            f.write(f"**许可证**: {repo.get('license', 'N/A')}\n\n")
            
            if languages:
                f.write("## 编程语言统计\n\n")
                total_bytes = sum(languages.values())
                for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                    f.write(f"- {lang}: {percentage:.1f}% ({bytes_count:,} bytes)\n")
                f.write("\n")
            
            f.write("## 抓取统计\n\n")
            f.write(f"**抓取时间**: {summary['scraped_at']}\n")
            f.write(f"**总文件数**: {summary['total_files_found']}\n")
            f.write(f"**文档文件数**: {summary['documentation_files']}\n")
            f.write(f"**已抓取文件数**: {summary['extracted_files']}\n\n")
            
            f.write("## 抓取的文件\n\n")
            for file_data in result["files"][:20]:  # 只显示前20个
                if file_data.get("status") == "success":
                    file_type = file_data.get("file_type", "unknown")
                    size = file_data.get("size", 0)
                    f.write(f"- [{file_data['path']}]({file_data.get('html_url', '')}) ")
                    f.write(f"({file_type}, {size} bytes)\n")
            
            if len(result["files"]) > 20:
                f.write(f"\n... 以及其他 {len(result['files']) - 20} 个文件\n")


# 便捷函数
async def scrape_github_repository(owner: str, repo: str, 
                                 max_files: int = 100, 
                                 include_code: bool = True,
                                 config: GitHubConfig = None) -> Dict[str, Any]:
    """
    便捷函数：抓取GitHub仓库
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
        max_files: 最大文件数
        include_code: 是否包含代码文件
        config: 配置对象
        
    Returns:
        抓取结果
    """
    async with GitHubRepoScraper(config) as scraper:
        return await scraper.scrape_repository_documentation(owner, repo, max_files, include_code)


async def get_github_repository_info(owner: str, repo: str, config: GitHubConfig = None) -> Dict[str, Any]:
    """
    便捷函数：获取GitHub仓库信息
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
        config: 配置对象
        
    Returns:
        仓库信息
    """
    async with GitHubRepoScraper(config) as scraper:
        return await scraper.get_repository_info(owner, repo)

"""GitHub统一内容抓取器 - 整合API和Pages抓取"""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse

from .config import GitHubConfig, default_config
from .utils import GitHubUtils
from .repo_scraper import GitHubRepoScraper
from .pages_scraper import GitHubPagesScraper


class GitHubContentScraper:
    """GitHub统一内容抓取器 - 整合仓库API和Pages抓取功能"""
    
    def __init__(self, config: GitHubConfig = None):
        """
        初始化GitHub内容抓取器
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or default_config
        self.repo_scraper = GitHubRepoScraper(config)
        self.pages_scraper = GitHubPagesScraper(config)
        
        # 创建输出目录
        self.output_dir = self.config.output_base_dir / "GitHub"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.repo_scraper.__aenter__()
        await self.pages_scraper.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.repo_scraper.__aexit__(exc_type, exc_val, exc_tb)
        await self.pages_scraper.__aexit__(exc_type, exc_val, exc_tb)
    
    async def scrape_comprehensive(self, owner: str, repo: str = None, 
                                 include_pages: bool = True,
                                 include_repo: bool = True,
                                 max_repo_files: int = None,
                                 max_pages: int = None) -> Dict[str, Any]:
        """
        综合抓取GitHub内容（仓库+Pages）
        
        Args:
            owner: GitHub用户名或组织名
            repo: 仓库名，如果为None则抓取用户的主要内容
            include_pages: 是否包含GitHub Pages抓取
            include_repo: 是否包含仓库内容抓取
            max_repo_files: 仓库最大文件数
            max_pages: Pages最大页面数
            
        Returns:
            综合抓取结果
        """
        print(f"🚀 开始综合抓取GitHub内容: {owner}/{repo if repo else 'all-content'}")
        
        results = {
            "status": "success",
            "owner": owner,
            "repo": repo,
            "scrape_type": "comprehensive",
            "started_at": datetime.now().isoformat(),
            "config_used": self.config.to_dict()
        }
        
        # 创建输出目录
        target_name = f"{owner}_{repo}" if repo else owner
        output_dir = self.output_dir / target_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tasks = []
        
        try:
            # 1. 抓取仓库内容（如果指定了repo）
            if include_repo and repo:
                print("📚 准备抓取仓库内容...")
                tasks.append(("repository", self._scrape_repository_task(owner, repo, max_repo_files)))
            
            # 2. 发现并抓取GitHub Pages
            if include_pages:
                print("🕷️ 准备抓取GitHub Pages...")
                tasks.append(("pages", self._scrape_pages_task(owner, repo, max_pages)))
            
            # 并行执行抓取任务
            if tasks:
                task_results = await asyncio.gather(
                    *[task[1] for task in tasks], 
                    return_exceptions=True
                )
                
                # 整理结果
                for i, (task_name, result) in enumerate(zip([t[0] for t in tasks], task_results)):
                    if isinstance(result, Exception):
                        results[task_name] = {
                            "status": "error",
                            "error": str(result),
                            "completed_at": datetime.now().isoformat()
                        }
                        print(f"❌ {task_name} 抓取失败: {result}")
                    else:
                        results[task_name] = result
                        print(f"✅ {task_name} 抓取完成")
            
            results["completed_at"] = datetime.now().isoformat()
            
            # 生成统一报告
            if self.config.save_metadata:
                await self._save_comprehensive_results(results, output_dir)
            
            # 计算总体统计
            self._calculate_comprehensive_stats(results)
            
            return results
            
        except Exception as e:
            print(f"❌ 综合抓取失败: {e}")
            results.update({
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            })
            return results
    
    async def _scrape_repository_task(self, owner: str, repo: str, max_files: int) -> Dict[str, Any]:
        """仓库抓取任务"""
        return await self.repo_scraper.scrape_repository_documentation(
            owner, repo, max_files or self.config.repo_max_files, True
        )
    
    async def _scrape_pages_task(self, owner: str, repo: str, max_pages: int) -> Dict[str, Any]:
        """Pages抓取任务"""
        # 首先发现Pages站点
        discovered_sites = await self.pages_scraper.discover_github_pages(owner, repo)
        
        if not discovered_sites:
            return {
                "status": "no_pages_found",
                "owner": owner,
                "repo": repo,
                "message": "No GitHub Pages sites discovered",
                "completed_at": datetime.now().isoformat()
            }
        
        # 抓取发现的站点
        pages_results = []
        
        for site in discovered_sites:
            if site.get("status") == "active":
                site_url = site["url"]
                print(f"🕷️ 抓取Pages站点: {site_url}")
                
                site_result = await self.pages_scraper.scrape_documentation_site(
                    site_url, max_pages or self.config.pages_max_pages
                )
                
                # 添加站点发现信息
                site_result["discovery_info"] = site
                pages_results.append(site_result)
        
        return {
            "status": "success",
            "discovered_sites": discovered_sites,
            "scraped_sites": pages_results,
            "sites_count": len(discovered_sites),
            "successful_scrapes": len([r for r in pages_results if r.get("status") == "success"]),
            "completed_at": datetime.now().isoformat()
        }
    
    def _calculate_comprehensive_stats(self, results: Dict[str, Any]):
        """计算综合统计信息"""
        stats = {
            "total_content_sources": 0,
            "total_files": 0,
            "total_pages": 0,
            "total_words": 0,
            "success_rate": 0.0,
            "content_types": set()
        }
        
        # 统计仓库内容
        if "repository" in results and results["repository"].get("status") == "success":
            repo_data = results["repository"]
            stats["total_content_sources"] += 1
            stats["total_files"] += repo_data.get("scrape_summary", {}).get("extracted_files", 0)
            stats["content_types"].add("repository")
        
        # 统计Pages内容
        if "pages" in results and results["pages"].get("status") == "success":
            pages_data = results["pages"]
            stats["total_content_sources"] += 1
            stats["content_types"].add("pages")
            
            for site_result in pages_data.get("scraped_sites", []):
                if site_result.get("status") == "success":
                    site_summary = site_result.get("scrape_summary", {})
                    stats["total_pages"] += site_summary.get("successful_pages", 0)
                    stats["total_words"] += site_summary.get("total_words", 0)
        
        # 计算成功率
        total_sources = len([k for k in results.keys() if k in ["repository", "pages"]])
        successful_sources = len([k for k in ["repository", "pages"] 
                                if k in results and results[k].get("status") == "success"])
        
        if total_sources > 0:
            stats["success_rate"] = (successful_sources / total_sources) * 100
        
        stats["content_types"] = list(stats["content_types"])
        results["comprehensive_stats"] = stats
    
    async def discover_github_content(self, owner: str, repo: str = None) -> Dict[str, Any]:
        """
        发现GitHub内容源（不进行实际抓取）
        
        Args:
            owner: GitHub用户名或组织名
            repo: 仓库名
            
        Returns:
            发现的内容源信息
        """
        print(f"🔍 发现GitHub内容源: {owner}/{repo if repo else 'all'}")
        
        discovery_results = {
            "status": "success",
            "owner": owner,
            "repo": repo,
            "discovered_at": datetime.now().isoformat(),
            "sources": {}
        }
        
        try:
            # 并行发现不同类型的内容
            tasks = []
            
            # 发现仓库信息
            if repo:
                tasks.append(("repository_info", self.repo_scraper.get_repository_info(owner, repo)))
            
            # 发现Pages站点
            tasks.append(("pages_sites", self.pages_scraper.discover_github_pages(owner, repo)))
            
            # 执行发现任务
            results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            
            # 整理发现结果
            for i, (task_name, result) in enumerate(zip([t[0] for t in tasks], results)):
                if isinstance(result, Exception):
                    discovery_results["sources"][task_name] = {
                        "status": "error",
                        "error": str(result)
                    }
                else:
                    discovery_results["sources"][task_name] = result
            
            return discovery_results
            
        except Exception as e:
            discovery_results.update({
                "status": "error", 
                "error": str(e)
            })
            return discovery_results
    
    async def scrape_by_url(self, url: str, 
                          scrape_type: str = "auto") -> Dict[str, Any]:
        """
        根据URL自动识别并抓取GitHub内容
        
        Args:
            url: GitHub URL
            scrape_type: 抓取类型 ("auto", "repository", "pages")
            
        Returns:
            抓取结果
        """
        print(f"🔗 根据URL抓取GitHub内容: {url}")
        
        # 解析URL
        url_info = self._parse_github_url(url)
        if not url_info:
            return {
                "status": "error",
                "error": "Invalid GitHub URL",
                "url": url,
                "scraped_at": datetime.now().isoformat()
            }
        
        print(f"🎯 识别到: {url_info['type']} - {url_info.get('owner')}/{url_info.get('repo', 'N/A')}")
        
        # 根据URL类型选择抓取方式
        if scrape_type == "auto":
            if url_info["type"] == "repository":
                scrape_type = "repository"
            elif url_info["type"] == "pages":
                scrape_type = "pages"
            else:
                scrape_type = "comprehensive"  # 如果无法确定，使用综合模式
        
        try:
            if scrape_type == "repository":
                return await self.repo_scraper.scrape_repository_documentation(
                    url_info["owner"], url_info["repo"]
                )
            elif scrape_type == "pages":
                return await self.pages_scraper.scrape_documentation_site(url)
            else:  # comprehensive
                return await self.scrape_comprehensive(
                    url_info["owner"], url_info.get("repo")
                )
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": url,
                "scraped_at": datetime.now().isoformat()
            }
    
    def _parse_github_url(self, url: str) -> Optional[Dict[str, Any]]:
        """解析GitHub URL"""
        try:
            parsed = urlparse(url)
            
            if parsed.netloc not in ["github.com", "www.github.com"]:
                # 检查是否为GitHub Pages
                if ".github.io" in parsed.netloc:
                    parts = parsed.netloc.split(".")
                    if len(parts) >= 3 and parts[-2] == "github" and parts[-1] == "io":
                        owner = parts[0]
                        # 尝试从路径中提取repo名
                        path_parts = parsed.path.strip("/").split("/")
                        repo = path_parts[0] if path_parts and path_parts[0] else None
                        
                        return {
                            "type": "pages",
                            "owner": owner,
                            "repo": repo,
                            "url": url
                        }
                return None
            
            # 解析github.com URL
            path_parts = parsed.path.strip("/").split("/")
            
            if len(path_parts) < 1:
                return None
            
            owner = path_parts[0]
            repo = path_parts[1] if len(path_parts) > 1 else None
            
            return {
                "type": "repository",
                "owner": owner,
                "repo": repo,
                "url": url
            }
            
        except Exception:
            return None
    
    async def _save_comprehensive_results(self, results: Dict[str, Any], output_dir: Path):
        """保存综合抓取结果"""
        # 保存主要元数据
        metadata = {
            "scrape_info": {
                k: v for k, v in results.items() 
                if k not in ["repository", "pages"]
            }
        }
        
        metadata_file = output_dir / "comprehensive_metadata.json"
        GitHubUtils.save_json(metadata, metadata_file)
        
        # 生成综合报告
        self._generate_comprehensive_report(results, output_dir)
        
        print(f"📁 综合抓取结果已保存到: {output_dir}")
    
    def _generate_comprehensive_report(self, results: Dict[str, Any], output_dir: Path):
        """生成综合抓取报告"""
        report_file = output_dir / "README.md"
        
        owner = results.get("owner", "unknown")
        repo = results.get("repo")
        stats = results.get("comprehensive_stats", {})
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# {owner}/{repo if repo else 'GitHub内容'} 综合抓取报告\n\n")
            
            f.write("## 抓取概览\n\n")
            f.write(f"**目标**: {owner}/{repo if repo else 'All content'}\n")
            f.write(f"**抓取时间**: {results.get('started_at', 'N/A')}\n")
            f.write(f"**完成时间**: {results.get('completed_at', 'N/A')}\n")
            f.write(f"**成功率**: {stats.get('success_rate', 0):.1f}%\n\n")
            
            f.write("## 内容统计\n\n")
            f.write(f"- **内容源数量**: {stats.get('total_content_sources', 0)}\n")
            f.write(f"- **仓库文件数**: {stats.get('total_files', 0)}\n")
            f.write(f"- **Pages页面数**: {stats.get('total_pages', 0)}\n")
            f.write(f"- **总字数**: {stats.get('total_words', 0):,}\n")
            f.write(f"- **内容类型**: {', '.join(stats.get('content_types', []))}\n\n")
            
            # 仓库抓取结果
            if "repository" in results:
                repo_result = results["repository"]
                f.write("## 仓库内容抓取\n\n")
                
                if repo_result.get("status") == "success":
                    repo_summary = repo_result.get("scrape_summary", {})
                    f.write(f"✅ **状态**: 成功\n")
                    f.write(f"- 总文件数: {repo_summary.get('total_files_found', 0)}\n")
                    f.write(f"- 文档文件数: {repo_summary.get('documentation_files', 0)}\n")
                    f.write(f"- 已抓取文件数: {repo_summary.get('extracted_files', 0)}\n\n")
                else:
                    f.write(f"❌ **状态**: 失败\n")
                    f.write(f"- 错误: {repo_result.get('error', 'Unknown error')}\n\n")
            
            # Pages抓取结果
            if "pages" in results:
                pages_result = results["pages"]
                f.write("## GitHub Pages抓取\n\n")
                
                if pages_result.get("status") == "success":
                    f.write(f"✅ **状态**: 成功\n")
                    f.write(f"- 发现站点数: {pages_result.get('sites_count', 0)}\n")
                    f.write(f"- 成功抓取数: {pages_result.get('successful_scrapes', 0)}\n\n")
                    
                    # 列出抓取的站点
                    for site_result in pages_result.get("scraped_sites", []):
                        if site_result.get("status") == "success":
                            site_summary = site_result.get("scrape_summary", {})
                            discovery_info = site_result.get("discovery_info", {})
                            
                            f.write(f"### {discovery_info.get('url', 'Unknown site')}\n")
                            f.write(f"- 生成器: {discovery_info.get('generator', 'Unknown')}\n")
                            f.write(f"- 成功页面: {site_summary.get('successful_pages', 0)}\n")
                            f.write(f"- 总字数: {site_summary.get('total_words', 0):,}\n\n")
                else:
                    f.write(f"❌ **状态**: 失败\n")
                    f.write(f"- 错误: {pages_result.get('error', 'Unknown error')}\n\n")
            
            f.write("---\n\n")
            f.write("*报告由 GitHub Content Scraper 生成*\n")


# 便捷函数
async def scrape_github_content(target: str, 
                              scrape_type: str = "auto",
                              include_pages: bool = True,
                              include_repo: bool = True,
                              config: GitHubConfig = None) -> Dict[str, Any]:
    """
    便捷函数：抓取GitHub内容
    
    Args:
        target: GitHub URL 或 "owner" 或 "owner/repo" 格式
        scrape_type: 抓取类型 ("auto", "repository", "pages", "comprehensive") 
        include_pages: 是否包含Pages抓取
        include_repo: 是否包含仓库抓取
        config: 配置对象
        
    Returns:
        抓取结果
    """
    async with GitHubContentScraper(config) as scraper:
        if target.startswith("http"):
            # URL格式
            return await scraper.scrape_by_url(target, scrape_type)
        else:
            # owner 或 owner/repo 格式
            parts = target.split("/")
            owner = parts[0]
            repo = parts[1] if len(parts) > 1 else None
            
            if scrape_type == "comprehensive":
                return await scraper.scrape_comprehensive(
                    owner, repo, include_pages, include_repo
                )
            elif scrape_type == "repository" and repo:
                return await scraper.repo_scraper.scrape_repository_documentation(owner, repo)
            elif scrape_type == "pages":
                if repo:
                    sites = await scraper.pages_scraper.discover_github_pages(owner, repo)
                    if sites and sites[0].get("status") == "active":
                        return await scraper.pages_scraper.scrape_documentation_site(sites[0]["url"])
                return {"status": "no_pages_found", "message": "No GitHub Pages found"}
            else:
                # 自动模式
                return await scraper.scrape_comprehensive(
                    owner, repo, include_pages, include_repo
                )


async def discover_github_content(target: str, config: GitHubConfig = None) -> Dict[str, Any]:
    """
    便捷函数：发现GitHub内容源
    
    Args:
        target: "owner" 或 "owner/repo" 格式
        config: 配置对象
        
    Returns:
        发现结果
    """
    async with GitHubContentScraper(config) as scraper:
        parts = target.split("/")
        owner = parts[0]
        repo = parts[1] if len(parts) > 1 else None
        
        return await scraper.discover_github_content(owner, repo)

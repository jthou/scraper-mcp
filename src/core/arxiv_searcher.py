#!/usr/bin/env python3
"""
ArXiv文献搜索与下载模块

基于现有项目架构，提供ArXiv学术文献的搜索、下载和管理功能
支持：
- ArXiv API搜索（无需浏览器）
- PDF直接下载
- 元数据提取和管理
- 批量下载和进度管理
- 分类组织
"""

import asyncio
import aiohttp
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlencode
import feedparser
import sys
import tempfile
import tarfile
import subprocess
import os

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import Logger

# 转换工具导入
try:
    from marker.converters.pdf import PdfConverter
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False

try:
    import pymupdf4llm
    PYMUPDF4LLM_AVAILABLE = True
except ImportError:
    PYMUPDF4LLM_AVAILABLE = False

try:
    import pypandoc
    PYPANDOC_AVAILABLE = True
except ImportError:
    PYPANDOC_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

CONVERSION_AVAILABLE = MARKER_AVAILABLE or PYMUPDF4LLM_AVAILABLE or PYPANDOC_AVAILABLE or PDFPLUMBER_AVAILABLE


class ArxivSearcher:
    """ArXiv搜索和下载器"""
    
    def __init__(self, output_dir: Path = None):
        self.logger = Logger("ArXiv文献搜索器")
        self.output_dir = output_dir or Path("K-Vault/ArXiv")
        self.pdf_dir = self.output_dir / "pdfs"
        self.metadata_dir = self.output_dir / "metadata"
        self.markdown_dir = self.output_dir / "markdown"  # 新增markdown目录
        self.tex_dir = self.output_dir / "tex_sources"    # 新增tex源码目录
        self.progress_file = self.output_dir / "progress.json"
        self.search_cache_file = self.output_dir / "search_cache.json"
        
        # 创建必要目录
        for dir_path in [self.pdf_dir, self.metadata_dir, self.markdown_dir, self.tex_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # ArXiv API配置
        self.api_base = "http://export.arxiv.org/api/query"
        self.delay_between_requests = 3  # ArXiv要求至少3秒间隔
        
        # 转换配置
        self.enable_markdown = CONVERSION_AVAILABLE
        self.preferred_converter = "auto"  # auto, marker, pymupdf4llm, pypandoc
        
        # 检查可用的转换器
        self.available_converters = []
        if PYMUPDF4LLM_AVAILABLE:
            self.available_converters.append("pymupdf4llm")
        if PDFPLUMBER_AVAILABLE:
            self.available_converters.append("pdfplumber")
        if PYPANDOC_AVAILABLE:
            self.available_converters.append("pypandoc")
        # if MARKER_AVAILABLE:
        #     self.available_converters.append("marker")  # 暂时禁用，API复杂
        
        if not CONVERSION_AVAILABLE:
            self.logger.warning("📝 Markdown转换功能不可用，请安装转换工具")
        else:
            self.logger.info(f"📝 可用转换器: {', '.join(self.available_converters)}")
        
        # 进度缓存
        self.progress_cache = self._load_progress()
        self.search_cache = self._load_search_cache()
    
    def _load_progress(self) -> Dict[str, Any]:
        """加载下载进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_progress(self):
        """保存下载进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存进度失败: {e}")
    
    def _load_search_cache(self) -> Dict[str, Any]:
        """加载搜索缓存"""
        if self.search_cache_file.exists():
            try:
                with open(self.search_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_search_cache(self):
        """保存搜索缓存"""
        try:
            with open(self.search_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存搜索缓存失败: {e}")
    
    def clean_filename(self, title: str, arxiv_id: str = None) -> str:
        """清理文件名"""
        # 移除特殊字符
        clean_title = re.sub(r'[<>:"/\\|?*\[\]]', '_', title)
        clean_title = re.sub(r'\s+', '_', clean_title)
        clean_title = clean_title.strip('_.')
        
        # 限制长度，为arxiv_id留空间
        max_len = 80 if arxiv_id else 100
        if len(clean_title) > max_len:
            clean_title = clean_title[:max_len-3] + "..."
        
        # 如果有arxiv_id，作为前缀
        if arxiv_id:
            return f"{arxiv_id}_{clean_title}"
        return clean_title
    
    async def search_arxiv(
        self,
        query: str,
        max_results: int = 100,
        sort_by: str = "relevance",
        sort_order: str = "descending",
        categories: List[str] = None,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        搜索ArXiv文献
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            sort_by: 排序方式 (relevance, lastUpdatedDate, submittedDate)
            sort_order: 排序顺序 (ascending, descending)
            categories: 分类过滤 (如 ['cs.AI', 'cs.LG'])
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        self.logger.info(f"🔍 搜索ArXiv文献: {query}")
        
        # 构建搜索查询
        search_query = f"all:{query}"
        
        # 添加分类过滤
        if categories:
            cat_filter = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({search_query}) AND ({cat_filter})"
        
        # 添加日期过滤
        if start_date or end_date:
            date_filter = self._build_date_filter(start_date, end_date)
            if date_filter:
                search_query = f"({search_query}) AND {date_filter}"
        
        # API参数
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': sort_order
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}?{urlencode(params)}"
                self.logger.info(f"📡 请求URL: {url}")
                
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_arxiv_response(content, query)
                    else:
                        return {
                            "status": "error",
                            "message": f"API请求失败: HTTP {response.status}",
                            "query": query
                        }
        
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return {
                "status": "error",
                "message": f"搜索失败: {str(e)}",
                "query": query
            }
    
    def _build_date_filter(self, start_date: str, end_date: str) -> str:
        """构建日期过滤器"""
        filters = []
        
        if start_date:
            # ArXiv日期格式: YYYYMMDDHHMMSS
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            start_str = start_dt.strftime("%Y%m%d") + "000000"
            filters.append(f"submittedDate:[{start_str} TO *]")
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_str = end_dt.strftime("%Y%m%d") + "235959"
            filters.append(f"submittedDate:[* TO {end_str}]")
        
        return " AND ".join(filters) if filters else ""
    
    def _parse_arxiv_response(self, xml_content: str, query: str) -> Dict[str, Any]:
        """解析ArXiv API响应"""
        try:
            # 使用feedparser解析Atom feed
            feed = feedparser.parse(xml_content)
            
            if not feed.entries:
                return {
                    "status": "success",
                    "message": "未找到相关文献",
                    "query": query,
                    "total_results": 0,
                    "results": []
                }
            
            results = []
            for entry in feed.entries:
                # 提取ArXiv ID
                arxiv_id = entry.id.split('/')[-1]
                
                # 提取作者信息
                authors = []
                if hasattr(entry, 'authors'):
                    authors = [author.name for author in entry.authors]
                elif hasattr(entry, 'author'):
                    authors = [entry.author]
                
                # 提取分类
                categories = []
                if hasattr(entry, 'arxiv_primary_category'):
                    categories.append(entry.arxiv_primary_category['term'])
                if hasattr(entry, 'tags'):
                    categories.extend([tag['term'] for tag in entry.tags if tag['scheme'].endswith('arxiv')])
                
                # 构建PDF链接
                pdf_url = None
                for link in entry.links:
                    if link.get('type') == 'application/pdf':
                        pdf_url = link.href
                        break
                
                if not pdf_url:
                    # 构造标准PDF URL
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                
                paper_info = {
                    "arxiv_id": arxiv_id,
                    "title": entry.title,
                    "summary": entry.summary,
                    "authors": authors,
                    "categories": categories,
                    "published": entry.published if hasattr(entry, 'published') else None,
                    "updated": entry.updated if hasattr(entry, 'updated') else None,
                    "pdf_url": pdf_url,
                    "arxiv_url": entry.link,
                    "primary_category": categories[0] if categories else "unknown"
                }
                
                results.append(paper_info)
            
            self.logger.info(f"✅ 找到 {len(results)} 篇文献")
            
            # 缓存搜索结果
            cache_key = f"{query}_{datetime.now().strftime('%Y%m%d')}"
            self.search_cache[cache_key] = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "total_results": len(results),
                "results": results
            }
            self._save_search_cache()
            
            return {
                "status": "success",
                "message": f"成功搜索到 {len(results)} 篇文献",
                "query": query,
                "total_results": len(results),
                "results": results
            }
        
        except Exception as e:
            self.logger.error(f"解析响应失败: {e}")
            return {
                "status": "error",
                "message": f"解析响应失败: {str(e)}",
                "query": query
            }
    
    async def download_paper(self, paper_info: Dict[str, Any]) -> Dict[str, Any]:
        """下载单篇文献"""
        arxiv_id = paper_info["arxiv_id"]
        title = paper_info["title"]
        pdf_url = paper_info["pdf_url"]
        
        # 检查是否已下载
        if self._is_already_downloaded(arxiv_id):
            return {
                "status": "skipped",
                "message": "文献已存在",
                "arxiv_id": arxiv_id,
                "title": title
            }
        
        self.logger.info(f"📥 下载文献: {title}")
        
        try:
            # 创建清理后的文件名
            clean_title = self.clean_filename(title, arxiv_id)
            pdf_filename = f"{clean_title}.pdf"
            metadata_filename = f"{clean_title}.json"
            
            pdf_path = self.pdf_dir / pdf_filename
            metadata_path = self.metadata_dir / metadata_filename
            
            # 下载PDF
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        pdf_content = await response.read()
                        
                        # 验证PDF内容
                        if len(pdf_content) < 1024:  # 小于1KB认为无效
                            return {
                                "status": "error",
                                "message": "PDF文件过小，可能下载失败",
                                "arxiv_id": arxiv_id
                            }
                        
                        # 保存PDF
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_content)
                        
                        # 保存元数据
                        enhanced_metadata = {
                            **paper_info,
                            "download_timestamp": datetime.now().isoformat(),
                            "local_pdf_path": str(pdf_path),
                            "local_metadata_path": str(metadata_path),
                            "file_size": len(pdf_content)
                        }
                        
                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json.dump(enhanced_metadata, f, ensure_ascii=False, indent=2)
                        
                        # 更新进度
                        self.progress_cache[arxiv_id] = {
                            "status": "success",
                            "title": title,
                            "download_time": datetime.now().isoformat(),
                            "pdf_path": str(pdf_path),
                            "metadata_path": str(metadata_path)
                        }
                        self._save_progress()
                        
                        self.logger.info(f"✅ 下载完成: {clean_title}")
                        
                        return {
                            "status": "success",
                            "message": "下载成功",
                            "arxiv_id": arxiv_id,
                            "title": title,
                            "pdf_path": str(pdf_path),
                            "metadata_path": str(metadata_path),
                            "file_size": len(pdf_content)
                        }
                    
                    else:
                        return {
                            "status": "error",
                            "message": f"下载失败: HTTP {response.status}",
                            "arxiv_id": arxiv_id,
                            "pdf_url": pdf_url
                        }
        
        except Exception as e:
            self.logger.error(f"下载失败: {e}")
            return {
                "status": "error",
                "message": f"下载失败: {str(e)}",
                "arxiv_id": arxiv_id
            }
    
    def _is_already_downloaded(self, arxiv_id: str) -> bool:
        """检查文献是否已下载"""
        # 检查进度缓存
        if arxiv_id in self.progress_cache:
            status = self.progress_cache[arxiv_id].get("status")
            if status == "success":
                # 验证文件是否还存在
                pdf_path = self.progress_cache[arxiv_id].get("pdf_path")
                if pdf_path and Path(pdf_path).exists():
                    return True
        
        # 检查文件是否存在（通过文件名模式匹配）
        for pdf_file in self.pdf_dir.glob(f"{arxiv_id}_*.pdf"):
            if pdf_file.exists():
                return True
        
        return False
    
    async def batch_download(
        self,
        papers: List[Dict[str, Any]],
        max_concurrent: int = 3,
        delay_between: float = None
    ) -> Dict[str, Any]:
        """批量下载文献"""
        delay = delay_between or self.delay_between_requests
        total = len(papers)
        self.logger.info(f"📚 开始批量下载 {total} 篇文献")
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        errors = []
        
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(paper, index):
            async with semaphore:
                try:
                    self.logger.info(f"📥 [{index+1}/{total}] 处理: {paper['title'][:50]}...")
                    result = await self.download_paper(paper)
                    
                    # 请求间隔
                    if index < total - 1:  # 最后一个不需要等待
                        await asyncio.sleep(delay)
                    
                    return result
                
                except Exception as e:
                    self.logger.error(f"下载异常: {e}")
                    return {
                        "status": "error",
                        "message": str(e),
                        "arxiv_id": paper.get("arxiv_id", "unknown")
                    }
        
        # 并发下载
        tasks = [download_with_semaphore(paper, i) for i, paper in enumerate(papers)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        for result in results:
            if isinstance(result, Exception):
                error_count += 1
                errors.append(str(result))
            elif result["status"] == "success":
                success_count += 1
            elif result["status"] == "skipped":
                skipped_count += 1
            else:
                error_count += 1
                errors.append(result.get("message", "未知错误"))
        
        # 生成摘要
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_papers": total,
            "successful_downloads": success_count,
            "skipped_papers": skipped_count,
            "failed_downloads": error_count,
            "success_rate": (success_count / total * 100) if total > 0 else 0,
            "errors": errors[:10],  # 只保存前10个错误
            "output_directory": str(self.output_dir)
        }
        
        # 保存摘要
        summary_file = self.output_dir / "download_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.logger.info("📊 批量下载统计:")
        self.logger.info(f"  • 总文献数: {total}")
        self.logger.info(f"  • 成功下载: {success_count}")
        self.logger.info(f"  • 已存在跳过: {skipped_count}")
        self.logger.info(f"  • 下载失败: {error_count}")
        self.logger.info(f"  • 成功率: {summary['success_rate']:.1f}%")
        
        return {
            "status": "success" if error_count == 0 else "partial",
            "message": f"批量下载完成，成功率: {summary['success_rate']:.1f}%",
            "summary": summary
        }
    
    async def search_and_download(
        self,
        query: str,
        max_results: int = 50,
        categories: List[str] = None,
        start_date: str = None,
        end_date: str = None,
        auto_download: bool = True
    ) -> Dict[str, Any]:
        """搜索并下载文献（一站式服务）"""
        self.logger.info(f"🎯 一站式搜索下载: {query}")
        
        # 1. 搜索
        search_result = await self.search_arxiv(
            query=query,
            max_results=max_results,
            categories=categories,
            start_date=start_date,
            end_date=end_date
        )
        
        if search_result["status"] != "success":
            return search_result
        
        papers = search_result["results"]
        if not papers:
            return {
                "status": "success",
                "message": "未找到相关文献",
                "query": query
            }
        
        self.logger.info(f"📚 找到 {len(papers)} 篇文献")
        
        # 2. 下载（如果启用）
        if auto_download:
            download_result = await self.batch_download(papers)
            return {
                "status": "success",
                "message": f"搜索并下载完成",
                "query": query,
                "search_results": len(papers),
                "download_summary": download_result["summary"]
            }
        else:
            return {
                "status": "success",
                "message": f"搜索完成，找到 {len(papers)} 篇文献",
                "query": query,
                "results": papers
            }


    async def download_tex_source(self, arxiv_id: str) -> Dict[str, Any]:
        """下载TeX源码"""
        if not self.enable_markdown:
            return {"status": "error", "message": "转换功能不可用"}
        
        tex_url = f"https://arxiv.org/src/{arxiv_id}"
        tex_filename = f"{arxiv_id}_source.tar.gz"
        tex_path = self.tex_dir / tex_filename
        
        try:
            self.logger.info(f"📥 下载TeX源码: {arxiv_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(tex_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        tex_path.write_bytes(content)
                        
                        # 解压源码
                        extract_dir = self.tex_dir / f"{arxiv_id}_extracted"
                        extract_dir.mkdir(exist_ok=True)
                        
                        with tarfile.open(tex_path, 'r:gz') as tar:
                            tar.extractall(extract_dir)
                        
                        return {
                            "status": "success",
                            "tex_path": str(tex_path),
                            "extract_dir": str(extract_dir)
                        }
                    else:
                        return {"status": "error", "message": f"下载失败: {response.status}"}
                        
        except Exception as e:
            self.logger.error(f"❌ TeX源码下载失败: {e}")
            return {"status": "error", "message": str(e)}


    def convert_pdf_to_markdown(self, pdf_path: Path, converter: str = "auto") -> Dict[str, Any]:
        """将PDF转换为Markdown（智能转换器选择）"""
        if not self.enable_markdown:
            return {"status": "error", "message": "转换功能不可用"}
        
        # 智能选择转换器
        if converter == "auto":
            converter = self._choose_best_converter()
        
        self.logger.info(f"📝 PDF转Markdown: {pdf_path.name} (使用{converter})")
        
        # 按优先级尝试转换器
        converters_to_try = [converter] if converter != "auto" else self.available_converters
        
        for conv in converters_to_try:
            try:
                result = self._convert_with_specific_tool(pdf_path, conv)
                if result["status"] == "success":
                    result["converter_used"] = conv
                    return result
                else:
                    self.logger.warning(f"⚠️ {conv}转换失败: {result.get('message')}")
            except Exception as e:
                self.logger.warning(f"⚠️ {conv}转换出错: {e}")
                continue
        
        return {"status": "error", "message": "所有转换器都失败了"}


    def _choose_best_converter(self) -> str:
        """智能选择最佳转换器"""
        # 按质量优先级排序 (当前推荐pymupdf4llm作为主力)
        priority_order = ["pymupdf4llm", "pdfplumber", "pypandoc", "marker"]
        
        for converter in priority_order:
            if converter in self.available_converters:
                return converter
        
        return self.available_converters[0] if self.available_converters else "none"


    def _convert_with_specific_tool(self, pdf_path: Path, converter: str) -> Dict[str, Any]:
        """使用指定工具转换PDF"""
        
        if converter == "pymupdf4llm":
            return self._convert_with_pymupdf4llm(pdf_path)
        elif converter == "pdfplumber":
            return self._convert_with_pdfplumber(pdf_path)
        elif converter == "pypandoc":
            return self._convert_with_pypandoc(pdf_path)
        elif converter == "marker":
            return self._convert_with_marker(pdf_path)
        else:
            return {"status": "error", "message": f"未知转换器: {converter}"}


    def _convert_with_marker(self, pdf_path: Path) -> Dict[str, Any]:
        """使用Marker转换PDF（最高质量，基于AI）"""
        try:
            import tempfile
            import subprocess
            import json
            
            self.logger.info(f"📝 使用Marker转换: {pdf_path.name}")
            
            # 创建临时输出目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_output = Path(temp_dir) / "output"
                
                # 使用marker命令行工具
                cmd = [
                    "python3", "-m", "marker.scripts.convert_single",
                    str(pdf_path),
                    str(temp_output),
                    "--config_file", "marker/settings/marker_local.yaml"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode == 0:
                    # 查找生成的markdown文件
                    markdown_files = list(temp_output.glob("*.md"))
                    if markdown_files:
                        markdown_content = markdown_files[0].read_text(encoding='utf-8')
                        
                        # 保存到正式目录
                        markdown_filename = pdf_path.stem + "_marker.md"
                        markdown_path = self.markdown_dir / markdown_filename
                        markdown_path.write_text(markdown_content, encoding='utf-8')
                        
                        return {
                            "status": "success",
                            "markdown_path": str(markdown_path),
                            "content_length": len(markdown_content),
                            "converter": "marker"
                        }
                    else:
                        return {"status": "error", "message": "Marker转换未生成markdown文件"}
                else:
                    error_msg = result.stderr or result.stdout or "未知错误"
                    return {"status": "error", "message": f"Marker命令行执行失败: {error_msg}"}
            
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Marker转换超时（>5分钟）"}
        except Exception as e:
            return {"status": "error", "message": f"Marker转换失败: {e}"}


    def _convert_with_pymupdf4llm(self, pdf_path: Path) -> Dict[str, Any]:
        """使用PyMuPDF4LLM转换PDF（推荐，快速且质量好）"""
        try:
            import pymupdf4llm
            
            markdown_content = pymupdf4llm.to_markdown(str(pdf_path))
            
            # 保存markdown文件
            markdown_filename = pdf_path.stem + "_pymupdf.md"
            markdown_path = self.markdown_dir / markdown_filename
            
            markdown_path.write_text(markdown_content, encoding='utf-8')
            
            return {
                "status": "success",
                "markdown_path": str(markdown_path),
                "content_length": len(markdown_content)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"PyMuPDF4LLM转换失败: {e}"}


    def _convert_with_pdfplumber(self, pdf_path: Path) -> Dict[str, Any]:
        """使用pdfplumber转换PDF（轻量级，适合简单文档）"""
        try:
            import pdfplumber
            
            markdown_content = []
            
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取文本
                    text = page.extract_text()
                    if text:
                        markdown_content.append(f"## Page {page_num}\n\n{text}\n\n")
                    
                    # 提取表格
                    tables = page.extract_tables()
                    for table_num, table in enumerate(tables, 1):
                        if table:
                            markdown_content.append(f"### Table {table_num} (Page {page_num})\n\n")
                            # 转换为markdown表格
                            if len(table) > 0:
                                # 表头
                                header = "| " + " | ".join(str(cell) if cell else "" for cell in table[0]) + " |\n"
                                separator = "|" + "---|" * len(table[0]) + "\n"
                                markdown_content.append(header + separator)
                                
                                # 表格数据
                                for row in table[1:]:
                                    row_md = "| " + " | ".join(str(cell) if cell else "" for cell in row) + " |\n"
                                    markdown_content.append(row_md)
                                markdown_content.append("\n")
            
            final_markdown = "".join(markdown_content)
            
            # 保存markdown文件
            markdown_filename = pdf_path.stem + "_pdfplumber.md"
            markdown_path = self.markdown_dir / markdown_filename
            
            markdown_path.write_text(final_markdown, encoding='utf-8')
            
            return {
                "status": "success",
                "markdown_path": str(markdown_path),
                "content_length": len(final_markdown)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"pdfplumber转换失败: {e}"}


    def _convert_with_pypandoc(self, pdf_path: Path) -> Dict[str, Any]:
        """使用Pypandoc转换PDF（基础质量）"""
        try:
            import pypandoc
            
            # 注意：pypandoc处理PDF效果不好，这里只是作为最后备选
            markdown_content = pypandoc.convert_file(
                str(pdf_path),
                'markdown',
                extra_args=['--wrap=none']
            )
            
            # 保存markdown文件
            markdown_filename = pdf_path.stem + "_pandoc.md"
            markdown_path = self.markdown_dir / markdown_filename
            
            markdown_path.write_text(markdown_content, encoding='utf-8')
            
            return {
                "status": "success",
                "markdown_path": str(markdown_path),
                "content_length": len(markdown_content)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Pypandoc转换失败: {e}"}


    def convert_tex_to_markdown(self, tex_dir: Path, main_tex_file: str = None) -> Dict[str, Any]:
        """将TeX源码转换为Markdown"""
        if not self.enable_markdown:
            return {"status": "error", "message": "转换功能不可用"}
        
        try:
            self.logger.info(f"📝 TeX转Markdown: {tex_dir.name}")
            
            # 寻找主TeX文件
            if not main_tex_file:
                tex_files = list(tex_dir.glob("*.tex"))
                if not tex_files:
                    return {"status": "error", "message": "未找到TeX文件"}
                
                # 尝试找到主文件（通常包含\\documentclass）
                main_tex_file = None
                for tex_file in tex_files:
                    content = tex_file.read_text(encoding='utf-8', errors='ignore')
                    if '\\documentclass' in content:
                        main_tex_file = tex_file.name
                        break
                
                if not main_tex_file:
                    main_tex_file = tex_files[0].name
            
            tex_file_path = tex_dir / main_tex_file
            
            # 使用pandoc转换（需要在tex目录中执行以处理引用）
            import pypandoc
            
            # 切换到TeX目录
            original_cwd = os.getcwd()
            os.chdir(tex_dir)
            
            try:
                markdown_content = pypandoc.convert_file(
                    main_tex_file,
                    'markdown',
                    extra_args=[
                        '--wrap=none',
                        '--bibliography-title=References',
                        '--standalone'
                    ]
                )
                
                # 保存markdown文件
                markdown_filename = tex_file_path.stem + ".md"
                markdown_path = self.markdown_dir / markdown_filename
                
                markdown_path.write_text(markdown_content, encoding='utf-8')
                
                return {
                    "status": "success",
                    "markdown_path": str(markdown_path),
                    "content_length": len(markdown_content),
                    "source_tex": main_tex_file
                }
                
            finally:
                os.chdir(original_cwd)
            
        except Exception as e:
            self.logger.error(f"❌ TeX转Markdown失败: {e}")
            return {"status": "error", "message": str(e)}


    async def download_and_convert_to_markdown(
        self,
        paper: Dict[str, Any],
        convert_method: str = "both"  # "pdf", "tex", "both"
    ) -> Dict[str, Any]:
        """下载并转换为Markdown（一站式）"""
        if not self.enable_markdown:
            return {"status": "error", "message": "转换功能不可用"}
        
        arxiv_id = paper["arxiv_id"]
        title = paper["title"]
        
        self.logger.info(f"📚 下载并转换: {title}")
        
        results = {"status": "success", "conversions": {}}
        
        # 下载PDF和转换
        if convert_method in ["pdf", "both"]:
            # 先下载PDF
            download_result = await self.download_paper(paper)
            
            if download_result["status"] == "success":
                pdf_path = Path(download_result["pdf_path"])
                
                # 转换PDF为Markdown
                pdf_conversion = self.convert_pdf_to_markdown(pdf_path)
                results["conversions"]["pdf_to_markdown"] = pdf_conversion
            else:
                results["conversions"]["pdf_to_markdown"] = {
                    "status": "error", 
                    "message": "PDF下载失败"
                }
        
        # 下载TeX源码和转换
        if convert_method in ["tex", "both"]:
            # 下载TeX源码
            tex_result = await self.download_tex_source(arxiv_id)
            
            if tex_result["status"] == "success":
                extract_dir = Path(tex_result["extract_dir"])
                
                # 转换TeX为Markdown
                tex_conversion = self.convert_tex_to_markdown(extract_dir)
                results["conversions"]["tex_to_markdown"] = tex_conversion
            else:
                results["conversions"]["tex_to_markdown"] = {
                    "status": "error",
                    "message": "TeX源码下载失败"
                }
        
        # 检查是否有任何成功的转换
        successful_conversions = [
            conv for conv in results["conversions"].values()
            if conv["status"] == "success"
        ]
        
        if not successful_conversions:
            results["status"] = "error"
            results["message"] = "所有转换方法都失败了"
        
        return results


    async def batch_convert_to_markdown(
        self,
        papers: List[Dict[str, Any]],
        convert_method: str = "both"
    ) -> Dict[str, Any]:
        """批量转换为Markdown"""
        if not self.enable_markdown:
            return {"status": "error", "message": "转换功能不可用"}
        
        self.logger.info(f"📚 开始批量Markdown转换 {len(papers)} 篇文献")
        
        successful_conversions = 0
        failed_conversions = 0
        conversion_details = []
        
        for i, paper in enumerate(papers, 1):
            self.logger.info(f"📝 [{i}/{len(papers)}] 转换: {paper['title'][:50]}...")
            
            try:
                result = await self.download_and_convert_to_markdown(paper, convert_method)
                
                conversion_details.append({
                    "arxiv_id": paper["arxiv_id"],
                    "title": paper["title"],
                    "result": result
                })
                
                if result["status"] == "success":
                    successful_conversions += 1
                else:
                    failed_conversions += 1
                    
            except Exception as e:
                self.logger.error(f"❌ 转换出错: {e}")
                failed_conversions += 1
                conversion_details.append({
                    "arxiv_id": paper["arxiv_id"],
                    "title": paper["title"],
                    "result": {"status": "error", "message": str(e)}
                })
            
            # 添加延迟
            await asyncio.sleep(self.delay_between_requests)
        
        # 统计结果
        success_rate = (successful_conversions / len(papers)) * 100 if papers else 0
        
        summary = {
            "total_papers": len(papers),
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions,
            "success_rate": round(success_rate, 1)
        }
        
        self.logger.info(f"📊 批量转换统计:")
        self.logger.info(f"  • 总文献数: {summary['total_papers']}")
        self.logger.info(f"  • 成功转换: {summary['successful_conversions']}")
        self.logger.info(f"  • 转换失败: {summary['failed_conversions']}")
        self.logger.info(f"  • 成功率: {summary['success_rate']}%")
        
        return {
            "status": "success",
            "summary": summary,
            "details": conversion_details
        }


async def main():
    """测试函数"""
    searcher = ArxivSearcher()
    
    # 测试搜索
    result = await searcher.search_and_download(
        query="machine learning",
        max_results=5,
        categories=["cs.LG", "cs.AI"],
        auto_download=True
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

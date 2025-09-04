#!/usr/bin/env python3
"""
网页内容抓取工具命令行接口

提供命令行接口来使用ScraperToolkit
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.scraper_toolkit import ScraperToolkit, ScrapingConfig, Platform, quick_search, quick_download, quick_batch_download


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="网页内容抓取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 搜索知乎内容
  python -m src.cli search zhihu "Python编程" --max-pages 2

  # 下载单个页面
  python -m src.cli download zhihu "https://www.zhihu.com/question/123456"

  # 批量下载
  python -m src.cli batch zhihu "机器学习" --max-pages 3 --output data/ml

  # 快速搜索（使用便捷函数）
  python -m src.cli quick-search zhihu "深度学习"

  # 快速下载（使用便捷函数）
  python -m src.cli quick-download zhihu "https://www.zhihu.com/question/123456"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索内容')
    search_parser.add_argument('platform', choices=['zhihu', 'wechat'], help='平台')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--max-pages', type=int, default=3, help='最大搜索页数')
    search_parser.add_argument('--headless', action='store_true', help='无头模式')
    search_parser.add_argument('--output', type=Path, default=Path('data'), help='输出目录')
    
    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载单个页面')
    download_parser.add_argument('platform', choices=['zhihu', 'wechat'], help='平台')
    download_parser.add_argument('url', help='页面URL')
    download_parser.add_argument('--title', help='自定义标题')
    download_parser.add_argument('--headless', action='store_true', help='无头模式')
    download_parser.add_argument('--output', type=Path, default=Path('data'), help='输出目录')
    
    # 批量下载命令
    batch_parser = subparsers.add_parser('batch', help='批量下载搜索结果')
    batch_parser.add_argument('platform', choices=['zhihu', 'wechat'], help='平台')
    batch_parser.add_argument('query', help='搜索关键词')
    batch_parser.add_argument('--max-pages', type=int, default=3, help='最大搜索页数')
    batch_parser.add_argument('--headless', action='store_true', help='无头模式')
    batch_parser.add_argument('--output', type=Path, default=Path('data'), help='输出目录')
    
    # 快速搜索命令
    quick_search_parser = subparsers.add_parser('quick-search', help='快速搜索（便捷函数）')
    quick_search_parser.add_argument('platform', choices=['zhihu', 'wechat'], help='平台')
    quick_search_parser.add_argument('query', help='搜索关键词')
    quick_search_parser.add_argument('--max-pages', type=int, default=3, help='最大搜索页数')
    quick_search_parser.add_argument('--headless', action='store_true', help='无头模式')
    
    # 快速下载命令
    quick_download_parser = subparsers.add_parser('quick-download', help='快速下载（便捷函数）')
    quick_download_parser.add_argument('platform', choices=['zhihu', 'wechat'], help='平台')
    quick_download_parser.add_argument('url', help='页面URL')
    quick_download_parser.add_argument('--headless', action='store_true', help='无头模式')
    quick_download_parser.add_argument('--output', type=str, default='data', help='输出目录')
    
    # 信息命令
    info_parser = subparsers.add_parser('info', help='显示平台信息')
    info_parser.add_argument('platform', nargs='?', choices=['zhihu', 'wechat', 'all'], help='平台（可选）')
    
    return parser


async def cmd_search(args):
    """搜索命令处理"""
    platform = Platform(args.platform)
    config = ScrapingConfig(
        platform=platform,
        headless=args.headless,
        max_pages=args.max_pages,
        output_dir=args.output
    )
    
    toolkit = ScraperToolkit(config)
    
    try:
        print(f"搜索 {platform.value} 内容: {args.query}")
        result = await toolkit.search(platform, args.query, args.max_pages)
        print(f"搜索结果: {result}")
        
        # 如果有结果，询问是否下载第一个
        if result.get("status") == "success" and result.get("results"):
            results = result["results"]
            print(f"\n找到 {len(results)} 个结果:")
            for i, item in enumerate(results[:5], 1):
                print(f"  {i}. {item['title']}")
            
            if input(f"\n是否下载第一个结果? (y/N): ").lower() == 'y':
                first_result = results[0]
                download_result = await toolkit.download_content(
                    platform,
                    first_result.get('url') or first_result.get('link'),
                    args.output,
                    first_result['title']
                )
                print(f"下载结果: {download_result}")
    
    finally:
        await toolkit.cleanup()


async def cmd_download(args):
    """下载命令处理"""
    platform = Platform(args.platform)
    config = ScrapingConfig(
        platform=platform,
        headless=args.headless,
        output_dir=args.output
    )
    
    toolkit = ScraperToolkit(config)
    
    try:
        print(f"下载 {platform.value} 页面: {args.url}")
        print("[1/3] 初始化浏览器与页面...")
        # 浏览器在内部按需初始化，这里只做提示
        print("[2/3] 正在读取并渲染页面（可能需要人工验证）...")
        print("[3/3] 正在生成PDF并转换为Markdown...")
        result = await toolkit.download_content(
            platform,
            args.url,
            args.output,
            args.title
        )
        if result.get("status") == "success":
            files = result.get("files", {})
            print("✅ 下载并转换完成：")
            if files.get("pdf"):
                print(f"  PDF: {files['pdf']}")
            if files.get("markdown"):
                print(f"  Markdown: {files['markdown']}")
            if files.get("mapping"):
                print(f"  映射: {files['mapping']}")
        else:
            print(f"❌ 下载失败: {result.get('message')}")
    
    finally:
        await toolkit.cleanup()


async def cmd_batch(args):
    """批量下载命令处理"""
    platform = Platform(args.platform)
    config = ScrapingConfig(
        platform=platform,
        headless=args.headless,
        max_pages=args.max_pages,
        output_dir=args.output
    )
    
    toolkit = ScraperToolkit(config)
    
    try:
        print(f"批量下载 {platform.value} 内容: {args.query}")
        print("[1/3] 搜索内容...")
        print("[2/3] 逐条读取并渲染页面（可能需要人工验证）...")
        print("[3/3] 生成PDF并转换为Markdown...")
        result = await toolkit.batch_download(
            platform,
            args.query,
            args.output,
            args.max_pages
        )
        if result.get("status") == "success":
            print("✅ 批量下载完成")
            print(f"  成功: {result.get('successful_downloads')}, 失败: {result.get('failed_downloads')}")
            files = result.get("files") or []
            preview = files[:3]
            if preview:
                print("  示例文件(最多3条):")
                for item in preview:
                    title = item.get('title') or '未命名'
                    pdf = item.get('pdf_file')
                    md = item.get('markdown_file')
                    print(f"   - {title}")
                    if pdf:
                        print(f"     PDF: {pdf}")
                    if md:
                        print(f"     Markdown: {md}")
        else:
            print(f"❌ 批量下载失败: {result.get('message')}")
    
    finally:
        await toolkit.cleanup()


async def cmd_quick_search(args):
    """快速搜索命令处理"""
    print(f"快速搜索 {args.platform} 内容: {args.query}")
    print("[1/1] 正在搜索...")
    result = await quick_search(
        args.platform,
        args.query,
        args.max_pages,
        args.headless
    )
    if result.get("status") == "success":
        results = result.get("results") or []
        print(f"✅ 搜索完成，共 {len(results)} 条")
        for i, item in enumerate(results[:5], 1):
            title = item.get('title') or '未命名'
            link = item.get('url') or item.get('link')
            print(f"  {i}. {title}")
            if link:
                print(f"     链接: {link}")
    else:
        print(f"❌ 搜索失败: {result.get('message')}")


async def cmd_quick_download(args):
    """快速下载命令处理"""
    print(f"快速下载 {args.platform} 页面: {args.url}")
    print("[1/3] 初始化浏览器与页面...")
    print("[2/3] 正在读取并渲染页面（可能需要人工验证）...")
    print("[3/3] 正在生成PDF并转换为Markdown...")
    result = await quick_download(
        args.platform,
        args.url,
        args.output,
        args.headless
    )
    if result.get("status") == "success":
        files = result.get("files", {})
        print("✅ 下载并转换完成：")
        if files.get("pdf"):
            print(f"  PDF: {files['pdf']}")
        if files.get("markdown"):
            print(f"  Markdown: {files['markdown']}")
        if files.get("mapping"):
            print(f"  映射: {files['mapping']}")
    else:
        print(f"❌ 下载失败: {result.get('message')}")


def cmd_info(args):
    """信息命令处理"""
    toolkit = ScraperToolkit()
    
    if args.platform == 'all' or args.platform is None:
        print("支持的平台:")
        for platform in Platform:
            info = toolkit.get_platform_info(platform)
            print(f"\n{platform.value.upper()}:")
            print(f"  名称: {info['name']}")
            print(f"  描述: {info['description']}")
            print(f"  功能: {', '.join(info['features'])}")
            print(f"  需要验证: {'是' if info['requires_verification'] else '否'}")
    else:
        platform = Platform(args.platform)
        info = toolkit.get_platform_info(platform)
        print(f"{platform.value.upper()} 平台信息:")
        print(f"  名称: {info['name']}")
        print(f"  描述: {info['description']}")
        print(f"  功能: {', '.join(info['features'])}")
        print(f"  需要验证: {'是' if info['requires_verification'] else '否'}")


async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'search':
            await cmd_search(args)
        elif args.command == 'download':
            await cmd_download(args)
        elif args.command == 'batch':
            await cmd_batch(args)
        elif args.command == 'quick-search':
            await cmd_quick_search(args)
        elif args.command == 'quick-download':
            await cmd_quick_download(args)
        elif args.command == 'info':
            cmd_info(args)
        else:
            print(f"未知命令: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n⏹️ 操作被用户中断")
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

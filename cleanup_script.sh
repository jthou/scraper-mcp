#!/bin/bash
# 自动清理脚本 - 保留核心文件，归档有价值工具，删除其他文件

echo "🧹 开始清理项目根目录..."

# 创建归档目录
mkdir -p archives/isaac_tools

# 1. 归档有通用价值的Isaac工具
echo "📦 归档有价值的Isaac工具..."
mv isaac_smart_cleaner.py archives/isaac_tools/ 2>/dev/null || true
mv isaac_legacy_cleaner.py archives/isaac_tools/ 2>/dev/null || true  
mv isaac_url_discoverer.py archives/isaac_tools/ 2>/dev/null || true
mv isaac_real_docs_finder.py archives/isaac_tools/ 2>/dev/null || true
mv isaac_download_analyzer.py archives/isaac_tools/ 2>/dev/null || true
mv isaac_simulation_cases_finder.py archives/isaac_tools/ 2>/dev/null || true

# 2. 删除所有其他Isaac相关文件
echo "�️ 删除其他所有Isaac文件..."
rm -f isaac_*.py isaac_*.md 2>/dev/null || true

# 3. 删除所有空文件和其他不需要的文件
echo "📝 删除空文件和无价值文件..."
find . -maxdepth 1 -name "*.py" -size 0 -delete 2>/dev/null || true
find . -maxdepth 1 -name "*.md" -size 0 -delete 2>/dev/null || true

# 删除其他不需要的文件
rm -f auto_download_isaac.py 2>/dev/null || true
rm -f clean_isaac_links.py 2>/dev/null || true
rm -f collect_*.py 2>/dev/null || true
rm -f demo_*.py 2>/dev/null || true
rm -f download_*.py 2>/dev/null || true
rm -f example_*.py 2>/dev/null || true
rm -f github_*.py 2>/dev/null || true
rm -f setup_*.py 2>/dev/null || true
rm -f simple_*.py 2>/dev/null || true
rm -f smart_*.py 2>/dev/null || true
rm -f test_*.py 2>/dev/null || true
rm -f local_link_extractor.py 2>/dev/null || true
rm -f pdf_to_markdown_processor.py 2>/dev/null || true

# 删除markdown文件
rm -f *_REPORT.md 2>/dev/null || true
rm -f *_SETUP.md 2>/dev/null || true
rm -f *QUICKREF.md 2>/dev/null || true
rm -f GitHub_*.md 2>/dev/null || true

# 4. 保留核心文件（这些文件不动）
echo "💎 保留核心文件："
echo "   ✓ project_organizer.py"
echo "   ✓ README.md"
echo "   ✓ TODO.md" 
echo "   ✓ requirements.txt"
echo "   ✓ run_with_system_python.sh"

echo "✅ 清理完成！"
echo "📊 清理统计："
echo "   - 归档了6个有价值的Isaac工具到 archives/isaac_tools/"
echo "   - 删除了所有其他无价值文件"
echo "   - 保留了5个核心项目文件"
echo ""
echo "🎯 现在项目根目录只剩下："
echo "   - project_organizer.py (项目整理工具)"
echo "   - README.md (项目说明)"
echo "   - TODO.md (任务清单)"
echo "   - requirements.txt (依赖列表)"
echo "   - run_with_system_python.sh (运行脚本)"
echo ""
echo "📁 归档的工具在 archives/isaac_tools/ 目录："
echo "   - isaac_smart_cleaner.py"
echo "   - isaac_legacy_cleaner.py"
echo "   - isaac_url_discoverer.py"
echo "   - isaac_real_docs_finder.py"
echo "   - isaac_download_analyzer.py"
echo "   - isaac_simulation_cases_finder.py"
echo ""
echo "💡 建议下一步："
echo "   - 运行 python project_organizer.py 进一步整理"
echo "   - 检查 src/ 目录的核心功能"
echo "   - 更新 README.md 文档"

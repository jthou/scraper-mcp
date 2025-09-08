#!/bin/bash
# 直接使用系统Python运行Isaac收集器

echo "🚀 使用系统Python运行Isaac收集器"
echo "确保已安装必要依赖..."

# 检查Python版本
python3 --version

# 安装依赖（如果尚未安装）
echo "📦 安装依赖包..."
pip3 install pyyaml playwright PyPDF2 weasyprint reportlab click pytest pytest-asyncio

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器..."
python3 -m playwright install chromium

# 运行收集器
echo "▶️ 启动Isaac内容收集器..."
python3 collect_isaacsim_content.py

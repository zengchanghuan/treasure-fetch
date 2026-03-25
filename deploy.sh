#!/bin/bash

# 一键部署脚本 (适用于 Ubuntu/Debian + Nginx + Systemd)
# 确保在项目根目录执行: ./deploy.sh

set -e

echo "🚀 开始部署 Moyun Fetch (Treasure Fetch)..."

# 1. 拉取最新代码
echo "📦 正在拉取代码..."
git pull origin main

# 2. 更新虚拟环境依赖 (如果需要)
echo "🐍 正在检查并更新 Python 依赖..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

# 3. 重启 Systemd 服务
echo "🔄 正在重启 FastAPI 服务..."
sudo systemctl daemon-reload
sudo systemctl restart treasure-fetch

# 4. 检查服务状态
echo "✅ 部署完成！当前服务状态："
sudo systemctl status treasure-fetch --no-pager | head -n 5

echo "🌐 请访问你的域名检查服务是否正常运行。"

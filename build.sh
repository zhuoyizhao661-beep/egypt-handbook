#!/usr/bin/env bash
# 重新生成 index.html。必须在仓库根目录执行：./build.sh
set -euo pipefail

cd "$(dirname "$0")"

if ! python3 -c "import PIL" 2>/dev/null; then
  echo "缺少 Pillow，请先安装："
  echo "  python3 -m pip install pillow"
  exit 1
fi

mkdir -p outputs
python3 work/magazine/redesign.py

OUT="outputs/埃及随身手册·离线图文阅读版.html"
cp "$OUT" index.html

echo
echo "已更新 index.html（$(wc -c < index.html | tr -d ' ') 字节）"
echo "本地预览：open index.html"
echo "发布上线：提交并推送到 main，约 1~2 分钟后生效"

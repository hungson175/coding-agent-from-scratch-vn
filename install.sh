#!/usr/bin/env bash
# One-line installer cho khóa học "AI Coding Agent Từ Số 0 (Tiếng Việt)"
#   curl -fsSL https://raw.githubusercontent.com/hungson175/coding-agent-from-scratch-vn/main/install.sh | bash
set -euo pipefail

REPO="https://github.com/hungson175/coding-agent-from-scratch-vn.git"
DIR="coding-agent-from-scratch-vn"

red()  { printf '\033[31m%s\033[0m\n' "$*"; }
grn()  { printf '\033[32m%s\033[0m\n' "$*"; }
ylw()  { printf '\033[33m%s\033[0m\n' "$*"; }

missing=0
need() {  # need <cmd> <tên> <link>
  if command -v "$1" >/dev/null 2>&1; then
    grn "  ✓ $2  ($($1 --version 2>&1 | head -1))"
  else
    red "  ✗ $2 chưa có → $3"; missing=1
  fi
}

echo
echo "Kiểm tra yêu cầu:"
need git  "git (Xcode Command Line Tools)" "chạy: xcode-select --install"
need uv   "uv"                             "https://docs.astral.sh/uv/getting-started/installation/"
need node "Node.js (cần cho bài capstone)" "https://nodejs.org"

if [ "$missing" -eq 1 ]; then
  echo; red "Thiếu tool ở trên. Cài xong chạy lại lệnh này."; exit 1
fi

echo
if [ -d "$DIR" ]; then
  ylw "Thư mục $DIR đã có sẵn — bỏ qua bước clone."
else
  echo "Clone code..."; git clone --depth 1 "$REPO" "$DIR"
fi

cd "$DIR"
echo "Cài Python + thư viện (uv sync)..."
uv sync

[ -f .env ] || cp .env.example .env

echo
grn "Xong. Còn đúng 2 việc:"
echo "  1. Mở $DIR/.env và dán DeepSeek API key vào (lấy ở https://platform.deepseek.com)"
echo "  2. Chạy thử:"
echo "       cd $DIR && uv run python steps/s01_most_simple_LLM.py"
echo "     rồi gõ: What is the capital of France?"
echo

#!/usr/bin/env bash
# One-line installer — khóa học "AI Coding Agent Từ Số 0 (Tiếng Việt)"
#   curl -fsSL https://raw.githubusercontent.com/hungson175/coding-agent-from-scratch-vn/main/install.sh | bash
#
# Thiếu tool nào, script tự cài tool đó. Bạn không phải cài tay gì cả.
set -uo pipefail

REPO="https://github.com/hungson175/coding-agent-from-scratch-vn.git"
DIR="coding-agent-from-scratch-vn"

red() { printf '\033[31m%s\033[0m\n' "$*"; }
grn() { printf '\033[32m%s\033[0m\n' "$*"; }
ylw() { printf '\033[33m%s\033[0m\n' "$*"; }
step(){ printf '\n\033[1m▸ %s\033[0m\n' "$*"; }

# Chạy qua `curl | bash` thì stdin không phải terminal -> sudo/brew không hỏi được mật khẩu.
# Nối lại stdin vào terminal để các bước cần mật khẩu vẫn chạy được.
[ -t 0 ] || { exec </dev/tty; } 2>/dev/null || true

[ "$(uname -s)" = "Darwin" ] || { red "Script này hiện chỉ hỗ trợ macOS. Windows: dùng WSL2. Linux: sẽ có bản riêng."; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

# ---------- 1. Xcode Command Line Tools (để có git) ----------
if ! have git || ! xcode-select -p >/dev/null 2>&1; then
  step "Cài Xcode Command Line Tools (để có git)"
  xcode-select --install >/dev/null 2>&1 || true
  ylw "  Một cửa sổ cài đặt của macOS vừa hiện ra — bấm Install rồi đợi nó xong."
  until xcode-select -p >/dev/null 2>&1 && have git; do sleep 10; done
fi
grn "✓ git  $(git --version)"

# ---------- 2. Homebrew ----------
if ! have brew; then
  step "Cài Homebrew"
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
    red "Cài Homebrew thất bại. Xem https://brew.sh rồi chạy lại lệnh này."; exit 1; }
fi
# nạp brew vào PATH cho phiên hiện tại (Apple Silicon và Intel khác đường dẫn)
for p in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$p" ] && eval "$("$p" shellenv)"; done
have brew || { red "Không tìm thấy brew sau khi cài. Mở terminal mới rồi chạy lại."; exit 1; }
grn "✓ brew $(brew --version | head -1)"

# ---------- 3. uv ----------
have uv || { step "Cài uv"; brew install uv; }
grn "✓ uv   $(uv --version)"

# ---------- 4. Node.js (cần cho bài capstone) ----------
have node || { step "Cài Node.js"; brew install node; }
grn "✓ node $(node -v)"

# ---------- 5. VS Code ----------
if ! have code && [ ! -d "/Applications/Visual Studio Code.app" ]; then
  step "Cài VS Code"
  brew install --cask visual-studio-code || ylw "  Cài VS Code không xong — tải tay ở https://code.visualstudio.com (không chặn các bước sau)."
fi
[ -d "/Applications/Visual Studio Code.app" ] && grn "✓ VS Code"

# ---------- 6. Code của khóa học ----------
step "Lấy code khóa học"
if [ -d "$DIR" ]; then ylw "  Thư mục $DIR đã có — bỏ qua clone."; else git clone --depth 1 "$REPO" "$DIR"; fi
cd "$DIR"

step "Cài Python + thư viện (uv sync)"
uv sync

[ -f .env ] || cp .env.example .env

echo
grn "Xong. Còn đúng 2 việc:"
echo "  1. Mở $DIR/.env, dán DeepSeek API key vào (lấy ở https://platform.deepseek.com)"
echo "  2. Chạy thử:"
echo "       cd $DIR && uv run python steps/s01_most_simple_LLM.py"
echo "     rồi gõ:  What is the capital of France?"
echo

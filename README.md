# AI Coding Agent Từ Số 0 — code khóa học (Tiếng Việt)

Code đi kèm khóa học **AI Coding Agent Từ Số 0** trên Udemy.
Mỗi file trong `steps/` là một bước, chạy độc lập được.

---

## Cài đặt — một lệnh (macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/hungson175/coding-agent-from-scratch-vn/main/install.sh | bash
```

Lệnh này kiểm tra tool, clone repo vào thư mục `coding-agent-from-scratch-vn`, chạy `uv sync`, tạo sẵn `.env`.

Sau đó còn đúng 2 việc:

1. Dán **DeepSeek API key** vào `.env` — lấy ở https://platform.deepseek.com
2. Chạy thử: `cd coding-agent-from-scratch-vn && uv run python steps/s01_most_simple_LLM.py` → gõ `What is the capital of France?` → ra `Paris.` là xong.

*(Linux / Windows: chưa hỗ trợ. Windows dùng WSL2.)*

## Hoặc: bảo coding agent của bạn tự làm

Bạn đang dùng Claude Code / Codex rồi, nên nhanh nhất là:

> Đọc https://github.com/hungson175/coding-agent-from-scratch-vn và setup project này trên máy tao.

File này viết để một coding agent đọc và tự thực hiện được.

---

## Yêu cầu

| Tool | Vì sao | Link |
|---|---|---|
| `git` | clone code — macOS: `xcode-select --install` (**không cần Xcode full**) | https://developer.apple.com/xcode/resources/ |
| `uv` | quản lý Python + thư viện. **Không cần cài Python riêng** (project cần Python ≥ 3.11) | https://docs.astral.sh/uv/getting-started/installation/ |
| `node` **≥ 20** | **bắt buộc cho bài capstone** — agent tự dựng app Vite + React rồi chạy dev server | https://nodejs.org |
| DeepSeek API key | model dùng trong khóa, trả theo mức dùng | https://platform.deepseek.com |

Kiểm tra nhanh: `git --version && uv --version && node -v`

## Ladder

`s01` một cú gọi LLM → `s02` vòng chat chưa nhớ → `s03` messages + system prompt → `s04` memory →
`s05_1` tool đầu tiên → `s05_2` **agentic loop** → `s05_3` gọn thành `chat()` → `s06` tool crash →
`s07` magic function → `s08` tool `bash` → `s09` `todowrite` → `s09_1` prompt ra file → `s10` bản hoàn chỉnh.

> `s09_1` và `s10` đọc `prompts/` theo đường dẫn tương đối — **chạy từ thư mục gốc repo**.

## Đổi sang OpenAI

3 chỗ trong phần khởi tạo `ChatOpenAI`: tên model, bỏ `base_url`, đổi sang `OPENAI_API_KEY`.

---

Code để **học**, không phải để đưa lên production.
Không liên kết, không được tài trợ hay xác nhận bởi Anthropic, OpenAI hay bất kỳ nhà cung cấp nào được nhắc tới.

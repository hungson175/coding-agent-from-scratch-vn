import os
import sys
import json
import select
import subprocess
import time
import termios
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env", override=True)

# ============================================================================
# CORE -- same shape as the previous step: tools, llm, messages, chat() loop.
# The only new logic here is background=True in bash. Everything else that
# changed in this step is display, and it lives in the section below.
# ============================================================================

@tool
def bash(command: str, background: bool = False) -> str:
	"""Execute a bash command."""
	if background:
		log_path = f"/tmp/agent-bash-{int(time.time() * 1000)}.log"
		log_f = open(log_path, "w")
		proc = subprocess.Popen(
			command,
			shell=True,
			stdin=subprocess.DEVNULL,
			stdout=log_f,
			stderr=subprocess.STDOUT,
			start_new_session=True,
		)
		log_f.close()
		time.sleep(0.4)
		if proc.poll() is not None:
			tail = Path(log_path).read_text(errors="replace")[-2000:]
			return f"Background process exited immediately code={proc.returncode}\nlog={log_path}\n{tail}"
		return f"Started in background\nPID={proc.pid}\nlog={log_path}\ncommand={command}"

	# stdin=DEVNULL is load-bearing: without it an interactive command (npm create, apt)
	# steals the terminal and the agent hangs forever waiting for input. Do not remove.
	result = subprocess.run(command, shell=True, capture_output=True, text=True, stdin=subprocess.DEVNULL)
	output = result.stdout
	if result.stderr:
		output += "\nSTDERR:\n" + result.stderr
	if result.returncode != 0:
		output += f"\n(exit code {result.returncode})"
	return output or "(no output)"

@tool
def todowrite(todos: list[dict]) -> str:
	"""Create and manage a structured task list."""
	return "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress."

with open(_ROOT / "prompts/final/bash.txt") as f:
	bash.description = f.read()
with open(_ROOT / "prompts/final/todowrite.txt") as f:
	todowrite.description = f.read()

tools = [bash, todowrite]
tools_by_name = {t.name: t for t in tools}

MODEL = "deepseek-v4-flash"
# MODEL = "deepseek-v4-pro"
# THINKING = {"type": "disabled"}
THINKING = {"type": "enabled"}
MAX_TOKENS = 4000  # caps reasoning + content (no separate reasoning max in DeepSeek API)
llm = ChatOpenAI(
	model=MODEL,
	base_url="https://api.deepseek.com",
	api_key=os.getenv("DEEPSEEK_API_KEY"),
	max_tokens=MAX_TOKENS,
	reasoning_effort="high",
	extra_body={"thinking": THINKING},
).bind_tools(tools)

with open(_ROOT / "prompts/final/system_prompt.txt") as f:
	system_prompt = f.read()
messages = [SystemMessage(content=system_prompt)]

def chat(user_input: str):
	messages.append(HumanMessage(content=user_input))
	step = 0
	while True:
		step += 1
		# log_messages(messages, step)  -- uncomment to dump the full LLM input
		response = llm.invoke(messages)
		messages.append(response)
		log_response(response, step)

		if not response.tool_calls:
			return response.content

		for i, tc in enumerate(response.tool_calls, 1):
			log_tool_call(i, len(response.tool_calls), tc)
			result = tools_by_name[tc["name"]].invoke(tc["args"])
			log_tool_result(tc, result)
			messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

# ============================================================================
# DISPLAY -- printing only, no logic. Nothing below this line changes what the
# agent does; it only changes what you can see it doing.
# ============================================================================

LOG_MAX = 256

STATUS_MARK = {
	"pending": "[ ]",
	"in_progress": "[~]",
	"completed": "[x]",
}

def clip(s, n=LOG_MAX):
	s = str(s)
	return s if len(s) <= n else s[:n] + "..."

def print_todos(todos):
	print("  ---- todos ----")
	if not todos:
		print("  (empty)")
	else:
		for i, t in enumerate(todos, 1):
			mark = STATUS_MARK.get(t.get("status", ""), "[?]")
			content = t.get("content", "")
			active = t.get("activeForm", "")
			line = f"  {i}. {mark} {content}"
			if active:
				line += f"  ({active})"
			print(line)
	print("  ---------------")

def format_tool_args(name: str, args: dict) -> str:
	if name == "todowrite":
		return "(see list below)"
	return clip(json.dumps(args, ensure_ascii=False))

def log_messages(msgs, step: int):
	print(f"\n===== LLM input (step {step}) -- messages[{len(msgs)}] =====")
	for i, m in enumerate(msgs):
		role = type(m).__name__
		print(f"\n[{i}] {role}")
		if getattr(m, "content", None):
			print(f"  content: {clip(m.content)}")
		if getattr(m, "tool_calls", None):
			print(f"  tool_calls: {clip(json.dumps(m.tool_calls, ensure_ascii=False))}")
		if getattr(m, "tool_call_id", None):
			print(f"  tool_call_id: {m.tool_call_id}")
	print("=" * 40)

def log_response(response, step: int):
	print(f"\n===== LLM step {step} =====")
	reasoning = response.additional_kwargs.get("reasoning_content")
	if reasoning:
		print(f"[Reasoning] {clip(reasoning)}")
	details = (response.usage_metadata or {}).get("output_token_details") or {}
	if details.get("reasoning"):
		print(f"[reasoning_tokens] {details['reasoning']}")
	if response.content:
		print(f"[Content] {clip(response.content)}")
	if response.tool_calls:
		print(f"[Tool calls] ({len(response.tool_calls)})")
		for i, tc in enumerate(response.tool_calls, 1):
			print(f"  {i}/{len(response.tool_calls)} {tc['name']} {format_tool_args(tc['name'], tc['args'])}")
			if tc["name"] == "todowrite":
				print_todos(tc["args"].get("todos", []))
	else:
		print("[Tool calls] none -- done")

def log_tool_call(i: int, total: int, tc: dict):
	if tc["name"] == "todowrite":
		print(f"  -> exec {i}/{total} todowrite")
	else:
		print(f"  -> exec {i}/{total} {tc['name']} {clip(json.dumps(tc['args'], ensure_ascii=False))}")

def log_tool_result(tc: dict, result):
	if tc["name"] != "todowrite":
		print(f"  <- {clip(result)}")

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
	print("Tools: bash, todowrite")
	print("Type 'quit' to exit\n")

	def clear_stdin():
		# Drop keystrokes/paste buffered while the agent was busy (otherwise the
		# next input() instantly re-submits leftover lines and looks like a re-run).
		if sys.stdin.isatty():
			try:
				termios.tcflush(sys.stdin, termios.TCIFLUSH)
			except termios.error:
				pass

	def read_user_input():
		# A pasted multi-line prompt arrives as many lines at once, but input()
		# takes only the first -- the rest used to be silently flushed away, so the
		# agent never saw the requirements. Drain whatever is already buffered and
		# treat the whole paste as ONE message.
		first = input("You: ")
		if not sys.stdin.isatty():
			return first  # piped input: every line is its own message, don't merge
		rest = []
		while select.select([sys.stdin], [], [], 0.05)[0]:
			nxt = sys.stdin.readline()
			if not nxt:
				break
			rest.append(nxt.rstrip("\n"))
		return "\n".join([first, *rest]) if rest else first

	while True:
		clear_stdin()
		user_input = read_user_input()
		if user_input.strip().lower() == "quit":
			break
		if not user_input.strip():
			continue
		print(f"\nAI: {chat(user_input)}\n")

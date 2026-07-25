import os
import json
import subprocess
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

load_dotenv(override=True)

@tool
def bash(command: str) -> str:
	"""Execute a bash command and return the output. Use this tool to run shell commands, inspect files, install packages, run tests, and interact with the system."""
	# stdin=DEVNULL is load-bearing: without it an interactive command (npm create, apt)
	# steals the terminal and the agent hangs forever waiting for input. Do not remove.
	result = subprocess.run(command, shell=True, capture_output=True, text=True, stdin=subprocess.DEVNULL)
	output = result.stdout
	if result.stderr:
		output += "\nSTDERR:\n" + result.stderr
	return output or "(no output)"

tools = [bash]
MODEL = "deepseek-v4-flash"
# MODEL = "deepseek-v4-pro"
THINKING = {"type": "disabled"}
# THINKING = {"type": "enabled"}
llm = ChatOpenAI(
	model=MODEL,
	base_url="https://api.deepseek.com",
	api_key=os.getenv("DEEPSEEK_API_KEY"),
	extra_body={"thinking": THINKING},
).bind_tools(tools)
tools_by_name = {t.name: t for t in tools}

messages = [SystemMessage(content="You are a helpful assistant with access to a bash tool. Use it to answer questions about the system, files, and to run commands.")]

def chat(user_input: str):
	messages.append(HumanMessage(content=user_input))
	while True:
		response = llm.invoke(messages)
		messages.append(response)

		if not response.tool_calls:
			return response.content

		for tc in response.tool_calls:
			print(f"  [Tool: {tc['name']}] {json.dumps(tc['args'], ensure_ascii=False)[:120]}")
			result = tools_by_name[tc["name"]].invoke(tc["args"])
			print(f"  [Result] {str(result)[:200]}")
			messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

# ---- display only: added at the END of this step; the next step starts without it ----
print("--- One Tool: bash ---")
print("Try: 'how many python files are in the steps directory?'")
print("Type 'quit' to exit\n")

while True:
	user_input = input("You: ")
	if user_input.strip().lower() == "quit":
		break
	print(chat(user_input))

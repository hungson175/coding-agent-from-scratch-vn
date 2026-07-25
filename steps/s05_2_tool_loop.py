import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

load_dotenv(override=True)

@tool
def compute(a: int, b: int, operator: str) -> str:
	"""Compute a math operation on two integers. operator is one of: +, -, *, /"""
	if operator == "+":
		return str(a + b)
	if operator == "-":
		return str(a - b)
	if operator == "*":
		return str(a * b)
	if operator == "/":
		return str(a / b)
	return f"Unknown operator: {operator}"

MODEL = "deepseek-v4-flash"
# MODEL = "deepseek-v4-pro"
THINKING = {"type": "disabled"}
# THINKING = {"type": "enabled"}
llm = ChatOpenAI(
	model=MODEL,
	base_url="https://api.deepseek.com",
	api_key=os.getenv("DEEPSEEK_API_KEY"),
	extra_body={"thinking": THINKING},
).bind_tools([compute])

messages = [SystemMessage(content="You are a helpful assistant with access to a compute tool.")]

# ---- display only: added at the END of this step; the next step starts without it ----
print("--- The agentic loop: keep going until it stops asking ---")
print("Try: 'what is 12 * 7, then add 5 to that' -- watch it take two round trips")
print("Type 'quit' to exit\n")

# Outer loop = one human turn. Inner loop = the model working until it's done.
while True:
	user_input = input("You: ")
	if user_input.strip().lower() == "quit":
		break

	messages.append(HumanMessage(content=user_input))
	while True:
		response = llm.invoke(messages)
		messages.append(response)

		if not response.tool_calls:
			print(f"AI: {response.content}")
			break

		# `for`, not `if`: the model may ask for several calls at once, and every
		# one of them needs a ToolMessage back or the next invoke() fails.
		for tc in response.tool_calls:
			print(f"  [Tool: {tc['name']}] {json.dumps(tc['args'], ensure_ascii=False)}")
			result = compute.invoke(tc["args"])
			print(f"  [Result] {result}")
			messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

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
		return str(a / b)  # DELIBERATE: try "what is 5 / 0" live -- the unhandled ZeroDivisionError
		                   # kills the whole loop. Fixing this on camera IS the lecture. Do not pre-fix.
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

def chat(user_input: str):
	messages.append(HumanMessage(content=user_input))
	while True:
		response = llm.invoke(messages)
		messages.append(response)

		if not response.tool_calls:
			return response.content

		# `for`, not `if`: the model may ask for several calls at once, and every
		# one of them needs a ToolMessage back or the next invoke() fails.
		for tc in response.tool_calls:
			print(f"  [Tool: {tc['name']}] {json.dumps(tc['args'], ensure_ascii=False)}")
			result = compute.invoke(tc["args"])
			print(f"  [Result] {result}")
			messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

# ---- display only: added at the END of this step; the next step starts without it ----
print("--- Debug the Simple Tool ---")
print("Ask: 'what is 20 divided by 4', then ask: 'what is 5 divided by 0'")
print("Type 'quit' to exit\n")
# The fix is NOT printed here on purpose -- the banner must not spoil the lesson
# before the crash happens on camera. Work it out live, then apply it.

while True:
	user_input = input("You: ")
	if user_input.strip().lower() == "quit":
		break
	print(f"AI: {chat(user_input)}")

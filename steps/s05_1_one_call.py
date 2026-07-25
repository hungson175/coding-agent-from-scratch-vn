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
messages.append(HumanMessage(content=input("You: ")))

# 1. The model CANNOT run anything. All it can do is ask.
response = llm.invoke(messages)
messages.append(response)

if not response.tool_calls:
	print(f"AI: {response.content}")
	raise SystemExit

# 2. WE run it -- the model never touches the function.
tc = response.tool_calls[0]
print(f"  [Tool: {tc['name']}] {json.dumps(tc['args'], ensure_ascii=False)}")
result = compute.invoke(tc["args"])
print(f"  [Result] {result}")

# 3. Hand the result back as a new kind of message, tagged with the id it asked under.
messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

# 4. Ask again. Only now can it answer in words.
response = llm.invoke(messages)
print(f"AI: {response.content}")

# ---- display only: added at the END of this step; the next step starts without it ----
print("\nThat was ONE round trip: it asks, you run, you report, it answers.")
print("A two-step question ('12 * 7, then add 5') stops halfway -- one trip is not enough.")
print("That is what the next step fixes.")

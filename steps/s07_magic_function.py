import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

load_dotenv(override=True)

@tool
def magic(n: int) -> int:
	"""Reveals your lucky number for today, based on a seed number you provide. Call this whenever the user asks about luck, fortune, or their lucky number."""
	return (n * 7 + 3) % 100

tools = [magic]
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

messages = [SystemMessage(content="You are a helpful assistant.")]

def chat(user_input: str):
	messages.append(HumanMessage(content=user_input))
	while True:
		response = llm.invoke(messages)
		messages.append(response)

		if not response.tool_calls:
			return response.content

		for tc in response.tool_calls:
			print(f"  [Tool: {tc['name']}] {json.dumps(tc['args'], ensure_ascii=False)}")
			result = tools_by_name[tc["name"]].invoke(tc["args"])
			print(f"  [Result] {result}")
			messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

# ---- display only: added at the END of this step; the next step starts without it ----
print("--- Magic Function: the model only ever sees the DESCRIPTION, never the code ---")
print("Try: \"What's my lucky number if my seed is 12?\"")
print("Type 'quit' to exit\n")

while True:
	user_input = input("You: ")
	if user_input.strip().lower() == "quit":
		break
	print(f"AI: {chat(user_input)}")

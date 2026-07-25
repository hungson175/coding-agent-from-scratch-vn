import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv(override=True)

system_prompt = "You are helpful assistant, you talk in language user talks to you. In case of ambiguity: English"

MODEL = "deepseek-v4-flash"
# MODEL = "deepseek-v4-pro"
THINKING = {"type": "disabled"}
# THINKING = {"type": "enabled"}
llm = ChatOpenAI(
	model=MODEL,
	base_url="https://api.deepseek.com",
	api_key=os.getenv("DEEPSEEK_API_KEY"),
	extra_body={"thinking": THINKING},
)

print("Type 'quit' to exit\n")

while True:
	user_input = input("You: ")
	if user_input.strip().lower() == "quit":
		break
	messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
	response = llm.invoke(messages)
	print(f"AI: {response.content}")

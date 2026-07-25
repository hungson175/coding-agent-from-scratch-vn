import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

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
	response = llm.invoke(user_input)
	print(f"AI: {response.content}")

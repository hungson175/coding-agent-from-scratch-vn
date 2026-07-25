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
user_input = input("You: ")
response = llm.invoke(user_input)
print(response.content)

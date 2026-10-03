from dotenv import load_dotenv
import os
load_dotenv()
from langchain_openai import ChatOpenAI
model=ChatOpenAI(
        model="zai-org/glm-5.3",
        api_key=os.getenv("GLM_API_KEY"),
        base_url=os.getenv("GLM_BASE_URL")
    )
# backend = StateBackend()
# response = model.invoke("hello")
# print(response)
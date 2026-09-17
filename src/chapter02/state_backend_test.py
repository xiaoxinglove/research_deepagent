from dotenv import load_dotenv
import os
load_dotenv()
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
model = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 创建 Agent
agent = create_deep_agent(
    model=model
)


config = {
    "configurable": {
        "thread_id": "test-thread"
    }
}


# 第一次任务
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content":
                """
                创建一个文件:

                /workspace/demo.txt

                内容:

                Backend=StateBackend
                """
            }
        ]
    },
    config=config
)


print(result)


# 第二次读取

result = agent.invoke(
    {
        "messages":[
            {
                "role":"user",
                "content":
                """
                读取:

                /workspace/demo.txt
                """
            }
        ]
    },
    config=config
)


print(result)
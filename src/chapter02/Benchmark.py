from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
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


backend = FilesystemBackend(
    root_dir="./workspace",
    virtual_mode=True
)
agent=create_deep_agent(
    model=model,
    backend=backend
)
import time


def benchmark(agent, task):

    start=time.time()

    result=agent.invoke(
        {
            "messages":[
                {
                    "role":"user",
                    "content":task
                }
            ]
        }
    )

    cost=time.time()-start

    return {
        "time":cost,
        "result":result
    }



tasks=[
    "写入1000行文本",
    "读取文件",
    "搜索关键词"
]


for t in tasks:

    print(
        benchmark(agent,t)
    )
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


result=agent.invoke(
    {
        "messages":[
            {
                "role":"user",
                "content":
                """
                创建文件:

                /workspace/demo.txt


                内容:

                Backend=FilesystemBackend
                """
            }
        ]
    }
)


print(result)



result=agent.invoke(
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
    }
)


print(result)
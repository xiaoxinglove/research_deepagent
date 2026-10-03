from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langchain_openai import ChatOpenAI
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

backend = FilesystemBackend(
    root_dir=str(BASE_DIR),
    virtual_mode=True,
)
model = ChatOpenAI(
    model="zai-org/GLM-5.3",
    api_key=os.getenv("GLM_API_KEY"),
    base_url=os.getenv("GLM_BASE_URL"),
    temperature=0
)
agent = create_deep_agent(
    model=model,
    backend=backend,
    skills=["/skills/"],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is LangGraph?"}]},
    config={"configurable": {"thread_id": "1"}},
)
print(result["messages"][-1].content)
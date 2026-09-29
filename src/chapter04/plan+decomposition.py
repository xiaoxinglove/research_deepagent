from dotenv import load_dotenv
import os
load_dotenv()
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import TodoListMiddleware
from deepagents.middleware import FilesystemMiddleware, SummarizationMiddleware
from deepagents.backends import StateBackend    
from tavily import TavilyClient

model=ChatOpenAI(
        model="zai-org/glm-5.3",
        api_key=os.getenv("GLM_API_KEY"),
        base_url=os.getenv("GLM_BASE_URL")
    )
backend = StateBackend()
# response = model.invoke("hello")
# print(response)

# 搜索工具
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(query: str, max_results: int = 5) -> dict:
    """搜索互联网获取最新信息。"""
    return tavily_client.search(query, max_results=max_results)

# 创建 Agent，并显式启用 write_todos
agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    middleware=[
        # 任务规划
        TodoListMiddleware(),
        # 文件工作空间
        FilesystemMiddleware(
            backend=backend
        ),
        # 长上下文压缩
        SummarizationMiddleware(
            model=model,
            backend=backend,
            # 超过4000 token触发摘要
            trigger=(
                "tokens",
                4000
            ),
            # 保留最近20轮消息
            keep=(
                "messages",
                20
            ),
        ),
    ],


    system_prompt="""

你是一名专业 AI Agent 技术研究员。

处理复杂研究任务必须遵循以下流程：

## Step 1 任务规划

首先调用 write_todos 创建研究计划。

计划必须包含：

- 研究对象
- 信息收集任务
- 技术分析任务
- 对比任务
- 报告撰写任务


## Step 2 信息收集

使用 internet_search 获取资料。

优先选择：

1. 官方文档
2. Github Repository
3. 官方博客
4. 技术论文


## Step 3 文件整理

将：

- 搜索结果
- 技术笔记
- 对比表格

保存到文件系统。


## Step 4 技术分析

分析：

- 架构设计
- 核心机制
- Agent Loop
- Middleware/Hooks
- Tool Calling
- Memory
- 使用场景


## Step 5 输出报告

最终生成：

# Agent Harness Framework Analysis


## 1. Overview
## 2. Architecture Comparison
## 3. Capability Comparison
## 4. Strengths and Limitations
## 5. Suitable Scenarios


所有结论需要注明来源。

"""
)

# 发起一个需要规划的复杂任务
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "请调研 Agent 开发领域的三大 Harness 框架（Deep Agents、Claude Agent SDK、Codex SDK），对比它们的核心能力差异，写一份简要分析报告。"
    }]
})

print(result["messages"][-1].content)
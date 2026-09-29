import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from tavily import TavilyClient
load_dotenv()

model = ChatOpenAI(
    model="zai-org/GLM-5.3",
    api_key=os.getenv("GLM_API_KEY"),
    base_url=os.getenv("GLM_BASE_URL"),
    temperature=0
)
tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

def internet_search(query: str):
    """
    网络搜索工具
    researcher 专属工具
    """

    result = tavily_client.search(
        query=query,
        max_results=5
    )

    return result



def statistical_analysis(text: str):
    """
    数据分析工具

    analyst 专属工具
    """

    return {
        "insights": [
            "AI Agent企业应用快速增加",
            "多Agent协作成为重要方向",
            "模型成本下降推动落地"
        ],
        "risks": [
            "数据安全问题",
            "Agent可靠性问题"
        ]
    }

# 数据收集 Agent
researcher = {

    "name": "researcher",

    "description": """
    数据收集专家。

    负责：
    - 搜索互联网信息
    - 收集事实数据
    - 整理资料

    不负责：
    - 数据分析
    - 最终报告撰写
    """,

    "system_prompt": """

你是一名数据研究员。
你的任务：
1. 根据主 Agent 的任务收集资料。
2. 使用搜索工具获取信息。
3. 输出结构化结果。
输出格式：
{
    "facts":[],
    "sources":[]
}
不要进行观点判断。
""",

    "tools":[
        internet_search
    ]
}

#分析agent
analyst = {
    "name":"analyst",

    "description": """

    数据分析专家。

    负责：
    - 分析已有数据
    - 提取趋势
    - 发现风险


    不负责：
    - 网络搜索
    """,


    "system_prompt": """
你是一名数据分析专家。


你的任务：
1.读取 researcher 返回的数据。

2.提炼：
- 关键趋势
- 风险
- 建议
输出：
{
    "insights":[],
    "risks":[],
    "recommendations":[]
}
不要主动搜索。
""",

    "tools":[
        statistical_analysis
    ]

}

# 主 Agent
agent = create_deep_agent(

    model=model,

    middleware=[
        TodoListMiddleware()
    ],

    system_prompt="""

你是一个项目协调 Agent。
处理复杂任务时：
1.首先使用 write_todos 制定任务计划。
2.需要资料时：调用 researcher。
3.需要分析时：调用 analyst。
4.最后整合所有结果。你负责协调，不要替代子 Agent 完成专业工作。
""",
    subagents=[
        researcher,
        analyst
    ]
)

# 调用主Agent

# #流式测试
# for chunk in agent.stream(
#     {
#         "messages":[
#             {
#                 "role":"user",
#                 "content":
#                """分析2026年AI Agent行业发展趋势。要求：
#                 1. 收集行业信息
#                 2. 分析主要趋势
#                 3. 总结机会和风险
#                 """
#             }
#         ]
#     },
#     stream_mode="values"
# ):

#     print(chunk)
response = agent.invoke(
    {
        "messages":[
            {
                "role":"user",
                "content":
                """
                分析2026年AI Agent行业发展趋势。
                要求：
                1. 收集行业信息
                2. 分析主要趋势
                3. 总结机会和风险
                """
            }
        ]
    }
)
print(response["messages"][-1].content)
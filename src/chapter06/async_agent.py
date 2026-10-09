"""在项目根目录先启动服务，再运行此客户端。

PowerShell 终端一：
    cd D:\2026项目\20260910deepagents\agentseek\research_deepagent
    $env:PYTHONUTF8="1"
    uv run --with "langgraph-cli[inmem]" langgraph dev --config src/chapter06/langgraph.async.json --n-jobs-per-worker 4 --no-browser
PowerShell 终端二：
    cd D:\2026项目\20260910deepagents\agentseek\research_deepagent
    uv run python src/chapter06/async_agent.py
"""

import argparse
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import httpx


load_dotenv(Path(__file__).resolve().parents[2] / ".env", encoding="utf-8-sig")
model = ChatOpenAI(
    model="zai-org/GLM-5.3",
    api_key=os.getenv("GLM_API_KEY"),
    base_url=os.getenv("GLM_BASE_URL"),
    temperature=0
)


async def observation_window() -> str:
    """演示专用：等待 20 秒，给用户留下追加指令或取消任务的窗口。"""
    await asyncio.sleep(20)
    return "观察窗口结束，请完成分析。"


def make_worker(role: str):
    from deepagents import create_deep_agent

    return create_deep_agent(
        model=model,
        tools=[observation_window],
        system_prompt=(
            f"你是{role}。每次收到用户任务或追加指令，先调用 observation_window 一次，"
            "再结合已有历史和最新指令，用中文给出简短分析。不要委派任务。"
            "本演示没有联网检索工具，不得声称已检索或核实外部资料。"
        ),
    )


def researcher():
    return make_worker("架构分析员")


def reviewer():
    return make_worker("从专家视角寻找反例和失效路径的审查员")


def supervisor():
    from deepagents import AsyncSubAgent, create_deep_agent

    return create_deep_agent(
        model=model,
        subagents=[
            AsyncSubAgent(name="researcher", description="分析架构、优点和实现方案", graph_id="researcher"),
            AsyncSubAgent(name="reviewer", description="从专家视角分析风险和反例", graph_id="reviewer"),
        ],
        system_prompt="""你是异步任务主管，使用中文。
用户要求并行任务时，启动所有指定子任务，然后立即返回完整 task_id。
启动后不要轮询或等待结果；允许用户继续交互。
查询时必须调用 check_async_task 或 list_async_tasks，不能依据旧消息猜测状态。
追加指令和恢复已取消任务均使用 update_async_task，保持原 task_id。
恢复意味着同一 thread 上启动新 run，不保证从被取消的代码行继续。
取消使用 cancel_async_task。工具报错时如实报告，不得宣称成功。
缺少明确 task_id 且有多个任务时，先列出任务再让用户选择，不得猜测目标。
用户仅要求列出任务时使用 list_async_tasks；要求结果时再 check 各任务。
当前没有联网搜索工具。遇到联网请求时明确说明限制，不得声称已检索。
""",
    )


async def chat(url: str, thread_id: str | None):
    from langgraph_sdk import get_client

    client = get_client(url=url)
    # ponytail: 同一主管 thread 保存任务登记；用 --thread 重新连接，无额外数据库。
    if thread_id is None:
        thread_id = (await client.threads.create())["thread_id"]
    else:
        await client.threads.get(thread_id)
    print(f"主管 thread_id: {thread_id}\n重新连接: python async_agent.py --thread {thread_id}")
    print("输入任务或控制指令；输入 exit 退出客户端（后台任务继续）。")
    while True:
        message = (await asyncio.to_thread(input, "\n你> ")).strip()
        if message.lower() in {"exit", "quit"}:
            return
        if not message:
            continue
        result = await client.runs.wait(
            thread_id,
            "supervisor",
            input={"messages": [{"role": "user", "content": message}]},
            raise_error=False,
        )
        if "__error__" in result:
            print("服务端错误:", result["__error__"])
            continue
        messages = result.get("messages", [])
        print("主管>", messages[-1].get("content", "") if messages else result)


# 加载模块时构建，避免服务在事件循环内重复构图并触发同步 I/O 检查。
supervisor_graph = supervisor()
researcher_graph = researcher()
reviewer_graph = reviewer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://127.0.0.1:2024", help="本地 LangGraph 服务地址")
    parser.add_argument("--thread", help="重新连接已存在的主管 thread")
    args = parser.parse_args()
    try:
        asyncio.run(chat(args.url, args.thread))
    except httpx.ConnectError:
        print(f"无法连接 LangGraph 服务 {args.url}。请先按文件顶部说明启动服务，等待启动完成后重试。")
        raise SystemExit(1)
    except (KeyboardInterrupt, EOFError):
        print("\n客户端退出；后台任务不会自动取消。")

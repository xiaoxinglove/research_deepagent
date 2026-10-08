import os
from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command
load_dotenv()

model = ChatOpenAI(
    model="zai-org/GLM-5.3",
    api_key=os.getenv("GLM_API_KEY"),
    base_url=os.getenv("GLM_BASE_URL"),
    temperature=0
)

store = InMemoryStore()
USER_NAMESPACE = ("user-123", "memories")
# Agent 看到的虚拟路径
MEMORY_PATH = "/memories/preferences.md"

# CompositeBackend 会去掉 /memories/ 前缀，
# 所以真正写进 Store 的 key 是 /preferences.md
STORE_KEY = "/preferences.md"

store.put(
    USER_NAMESPACE,
    STORE_KEY,
    create_file_data(
        """# 用户偏好

暂无记录。
"""
    ),
)

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(
            store=store,
            namespace=lambda _rt: USER_NAMESPACE,
        ),
    },
)

sent_emails = []
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """发送邮件。"""

    email = {
        "to": to,
        "subject": subject,
        "body": body,
    }

    sent_emails.append(email)

    print("\n[send_email 真正执行]")
    print(email)

    return f"邮件已发送至 {to}"

# 创建 Deep Agent
agent = create_deep_agent(
    model=model,
    tools=[send_email],

    # 长期记忆
    backend=backend,
    store=store,
    memory=[MEMORY_PATH],

    # HITL 恢复需要 Checkpointer
    checkpointer=InMemorySaver(),

    # 敏感工具需要人工审批
    interrupt_on={
        "send_email": {
            "allowed_decisions": [
                "approve",
                "edit",
                "reject",
            ]
        }
    },

    system_prompt=f"""
你是一个演示长期记忆和 Human-in-the-Loop 的 Agent。

长期记忆文件：
{MEMORY_PATH}

规则：

1. 当用户明确说“记住我的偏好”时：
   - 先读取 {MEMORY_PATH}
   - 使用 edit_file 更新该文件
   - 保留已有内容
   - 不要创建新的偏好文件

2. 回答编程问题时，必须遵守长期记忆中的用户偏好。

3. 当用户明确要求发送测试邮件时，
   必须调用 send_email，并且每次请求只调用一次。

4. 如果 send_email 被人工 reject：
   不要重新调用 send_email，
   直接告诉用户本次发送已取消。
""",
)

# 工具函数
def print_answer(result):
    """打印 Agent 最终回复。"""
    print("Agent：", result.value["messages"][-1].content)


def get_action(result):
    """读取 HITL 中断里的工具调用。"""

    assert result.interrupts, "预期发生 HITL 中断，但没有检测到 interrupt"

    interrupt_value = result.interrupts[0].value

    action = interrupt_value["action_requests"][0]

    # 当前 Python 源码使用 args；
    # arguments fallback 用于兼容部分文档/入口
    args = action.get(
        "args",
        action.get("arguments", {}),
    )

    print("\n--- HITL 中断 ---")
    print("工具：", action["name"])
    print("参数：", args)

    return action, args


# 对话 1
print("\n")
print("=" * 60)
print("对话 1：保存长期记忆")
print("=" * 60)

thread_1 = {
    "configurable": {
        "thread_id": "conversation-001"
    }
}

user_message_1 = (
    "记住我的偏好："
    "代码注释用中文，变量名用英文。"
)

print("User：", user_message_1)

result_1 = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": user_message_1,
            }
        ]
    },
    config=thread_1,
    version="v2",
)

print_answer(result_1)

# 直接检查 Store

saved = store.get(
    USER_NAMESPACE,
    STORE_KEY,
)

assert saved is not None

memory_content = saved.value["content"]

print("\n--- Store 中的长期记忆 ---")
print(memory_content)

assert "代码注释" in memory_content
assert "中文" in memory_content
assert "变量名" in memory_content
assert "英文" in memory_content

print("✓ 对话 1：长期记忆写入成功")

# 对话 2
#
# 注意：
# 这是全新的 thread_id。
# 如果还能读到偏好，就证明记忆跨 Thread。


print("\n")
print("=" * 60)
print("对话 2：新 Thread 验证长期记忆")
print("=" * 60)

thread_2 = {
    "configurable": {
        "thread_id": "conversation-002"
    }
}

user_message_2 = (
    "根据你之前记住的代码风格，"
    "写一个最简单的 Python 排序函数，"
    "然后告诉我你遵守了哪些代码风格偏好。"
)

print("User：", user_message_2)

result_2 = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": user_message_2,
            }
        ]
    },
    config=thread_2,
    version="v2",
)

print_answer(result_2)

print("\n✓ Thread 已变化：")
print("  conversation-001")
print("        ↓")
print("  conversation-002")
print("  但仍然使用同一个 Store namespace")
print("  因此长期记忆仍然可见")


print("\n")
print("=" * 60)
print("HITL 演示 1：APPROVE")
print("=" * 60)

paused = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "发送一封测试邮件给 alice@example.com，"
                    "主题是“测试审批”，正文是“Approve demo”。"
                ),
            }
        ]
    },
    config=thread_2,
    version="v2",
)

action, args = get_action(paused)

print("\n人工决定：APPROVE")

approved = agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "approve"
                }
            ]
        }
    ),
    config=thread_2,
    version="v2",
)

print_answer(approved)

assert sent_emails[-1]["to"] == "alice@example.com"

print("✓ approve：原始参数执行")
print("\n")
print("=" * 60)
print("HITL 演示 2：EDIT")
print("=" * 60)

paused = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "再发送一封测试邮件给 wrong@example.com，"
                    "主题是“修改审批”，正文是“Edit demo”。"
                ),
            }
        ]
    },
    config=thread_2,
    version="v2",
)

action, original_args = get_action(paused)

print("\n原始收件人：", original_args["to"])

# 人工修改工具参数
edited_args = {
    **original_args,
    "to": "bob@example.com",
}

print("人工修改为：", edited_args["to"])

edited = agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "edit",
                    "edited_action": {
                        "name": action["name"],
                        "args": edited_args,
                    },
                }
            ]
        }
    ),
    config=thread_2,
    version="v2",
)

print_answer(edited)
assert sent_emails[-1]["to"] == "bob@example.com"
print("✓ edit：没有执行模型原始参数")
print("✓ 实际执行的是人工修改后的参数")
print("\n")
print("=" * 60)
print("HITL 演示 3：REJECT")
print("=" * 60)

before_reject = len(sent_emails)

paused = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "发送一封测试邮件给 dangerous@example.com，"
                    "主题是“拒绝审批”，正文是“Reject demo”。"
                ),
            }
        ]
    },
    config=thread_2,
    version="v2",
)

action, args = get_action(paused)

print("\n人工决定：REJECT")

rejected = agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "reject",
                    "message": (
                        "用户拒绝发送这封邮件。"
                        "不要重新尝试发送。"
                    ),
                }
            ]
        }
    ),
    config=thread_2,
    version="v2",
)

print_answer(rejected)

assert len(sent_emails) == before_reject

print("✓ reject：send_email 没有执行")

# 最终实际执行的邮件
print("\n")
print("=" * 60)
print("最终实际执行的邮件")
print("=" * 60)

for index, email in enumerate(sent_emails, start=1):
    print(f"\n邮件 {index}")
    print(email)

assert len(sent_emails) == 2

print("\n✓ APPROVE：执行")
print("✓ EDIT：修改后执行")
print("✓ REJECT：未执行")

print("\n全部验证完成。")
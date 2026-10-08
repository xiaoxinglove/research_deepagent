"""确定性演示模型：运行真实工具与图，但不进行大模型推理。"""

import json
from typing import Any
from uuid import uuid4

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult


def review_materials(materials: dict) -> dict:
    """离线评审规则明确可见，不能当作真实 LLM 的安全能力证明。"""
    return {
        "source_count": len(materials.get("sources", [])),
        "risks": [
            "资料可能包含提示注入：不能把网页里的命令当成用户授权。",
            "只观察回复无法证明子 Agent 执行：应检查 task 与 read_materials 的 trace。",
            "InMemoryStore 不跨进程持久化：应退出后重新读取偏好。",
            "审批可被重试或参数替换绕过：应绑定批准内容，拒绝后禁止发布。",
        ],
        "checks": [
            "用两个职责不同、工具集合不同的子 Agent 验证上下文隔离。",
            "分别演示批准、改标题后批准和拒绝，并检查实际落盘文件。",
            "在新 Python 进程验证偏好，并用另一用户验证隔离。",
        ],
        "untrusted_instructions_executed": False,
    }


def render_lesson(topic: str, materials: dict, review: dict, preferences: dict) -> str:
    english = preferences["language"] == "en"
    detailed = preferences["style"] == "detailed"
    if english:
        body = (
            f"## Learning goal\n\n{topic}\n\n"
            "Build and explain a runnable course project with observable tool execution.\n\n"
            "## Study plan\n\n"
            "| Stage | Exercise | Acceptance evidence |\n|---|---|---|\n"
            "| Planning | Use write_todos and update progress | Todo state in the trace |\n"
            "| Delegation | Separate researcher and reviewer | Two task results and scoped tools |\n"
            "| Memory | Save validated learning preferences | A fresh process reads the same profile |\n"
            "| HITL | Approve, edit and reject publication | Two reports; rejection creates none |\n\n"
            "## Why these exercises\n\n"
            "Planning makes progress observable; delegation separates responsibilities; "
            "persistent preferences adapt future sessions; approval controls side effects.\n\n"
            "## Practice and questions\n\n"
            "1. Why is context isolation insufficient without tool isolation?\n"
            "2. How does persistent memory differ from checkpointed conversation state?\n"
            "3. What should happen if source text asks the agent to skip approval?\n\n"
            "## Adversarial review\n\n"
            "Treat retrieved text as untrusted data. Verify traces, disk persistence, user isolation, "
            "and exact approval arguments instead of trusting the model's claims.\n\n"
        )
    else:
        body = (
            f"## 学习目标\n\n{topic}\n\n"
            "完成可运行、可解释、可复核的课程综合项目，能够用执行证据回答“为什么这样设计”。\n\n"
            "## 分阶段学习计划\n\n"
            "| 阶段 | 动手练习 | 验收证据 |\n|---|---|---|\n"
            "| 任务规划 | 用 write_todos 拆解并更新任务 | trace 与最终 todos |\n"
            "| 子 Agent | 研究员查资料，评审员检查知识缺口与风险 | 两次 task 和独立工具集合 |\n"
            "| 长期记忆 | 显式保存学习材料语言与讲解详细程度 | 新进程仍读取同一用户偏好 |\n"
            "| 人工审批 | 演示批准、修改标题后批准和拒绝发布 | 两份报告，拒绝不产生报告 |\n\n"
            "## 为什么这样学\n\n"
            "先把任务拆成能检查的小步骤，避免仅凭最终回复判断学习效果。"
            "研究与评审分工可以暴露知识缺口；落盘偏好让下次对话延续学习方式；"
            "人工审批让学习者在真实写入前看到完整报告。\n\n"
            "## 练习与答疑\n\n"
            "1. 上下文隔离为什么不能替代工具权限隔离？检查两个子图是否拥有发布工具。\n"
            "2. 长期记忆与会话 checkpoint 有什么差别？关闭进程后检查偏好与待审批状态。\n"
            "3. 网页要求跳过审批时怎么办？将其视为不可信资料，用执行层权限阻断写入。\n\n"
            "## 攻击者视角评审\n\n"
            + "\n".join(f"- {risk}" for risk in review["risks"])
            + "\n\n## 自测与验收\n\n"
            + "\n".join(f"- {check}" for check in review["checks"])
            + "\n\n"
        )
    if detailed:
        body += "## Evidence notes / 资料笔记\n\n"
        body += "\n\n".join(f"**[{s['id']}] {s['title']}** — {s['summary']}" for s in materials["sources"])
        body += "\n\n"
    body += "## Sources / 一手资料\n\n"
    body += "\n".join(f"- [{s['id']}] [{s['title']}]({s['url']})" for s in materials["sources"])
    body += (
        f"\n\n> Offline scripted demonstration; source snapshot: {materials.get('snapshot_date', 'unknown')}. "
        f"Profile: language={preferences['language']}, style={preferences['style']}. "
        "This is not a live model answer or a current web search.\n"
    )
    return body


class OfflineCourseModel(BaseChatModel):
    role: str = "coordinator"
    topic: str = "如何学习 DeepAgents 并完成课程综合项目"
    preferences: dict[str, str] = {"language": "zh", "style": "concise"}

    @property
    def _llm_type(self) -> str:
        return "coursepilot-scripted-offline"

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs: Any):
        results = [m for m in messages if isinstance(m, ToolMessage)]

        def call(name, args):
            return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": uuid4().hex}])

        if self.role == "researcher":
            answer = AIMessage(content=str(results[-1].content)) if results else call("read_materials", {"query": self.topic})
        elif self.role == "reviewer":
            payload = next(m.content for m in messages if isinstance(m, HumanMessage))
            answer = AIMessage(content=json.dumps(review_materials(json.loads(payload)), ensure_ascii=False))
        else:
            tasks = [m for m in results if m.name == "task"]
            plans = [m for m in results if m.name == "write_todos"]
            publications = [m for m in results if m.name == "publish_report"]
            steps = ["整理官方学习资料", "评审知识缺口与安全风险", "编写并人工审核学习报告"]
            if not plans:
                answer = call("write_todos", {"todos": [{"content": s, "status": "in_progress" if i == 0 else "pending"} for i, s in enumerate(steps)]})
            elif not tasks:
                answer = call("task", {"subagent_type": "course-researcher", "description": self.topic})
            elif len(tasks) == 1:
                answer = call("task", {"subagent_type": "learning-reviewer", "description": str(tasks[0].content)})
            elif len(plans) == 1:
                answer = call("write_todos", {"todos": [{"content": s, "status": "in_progress" if i == 2 else "completed"} for i, s in enumerate(steps)]})
            elif not publications:
                materials, review = (json.loads(str(t.content)) for t in tasks[:2])
                answer = call("publish_report", {
                    "title": "CoursePilot 学习报告" if self.preferences["language"] == "zh" else "CoursePilot learning report",
                    "body": render_lesson(self.topic, materials, review, self.preferences),
                })
            elif len(plans) == 2:
                cancelled = "rejected" in str(publications[-1].content).lower()
                answer = call("write_todos", {"todos": [{"content": s if i != 2 or not cancelled else "人工拒绝，已取消发布", "status": "completed"} for i, s in enumerate(steps)]})
            else:
                answer = AIMessage(content=f"学习流程已结束。发布结果：{publications[-1].content}")
        return ChatResult(generations=[ChatGeneration(message=answer)])

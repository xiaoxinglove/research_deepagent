# 人工修订：DeepAgents 课程学习计划

## 学习目标

如何学习 DeepAgents 并完成课程综合项目

完成可运行、可解释、可复核的课程综合项目，能够用执行证据回答“为什么这样设计”。

## 分阶段学习计划

| 阶段 | 动手练习 | 验收证据 |
|---|---|---|
| 任务规划 | 用 write_todos 拆解并更新任务 | trace 与最终 todos |
| 子 Agent | 研究员查资料，评审员检查知识缺口与风险 | 两次 task 和独立工具集合 |
| 长期记忆 | 显式保存学习材料语言与讲解详细程度 | 新进程仍读取同一用户偏好 |
| 人工审批 | 演示批准、修改标题后批准和拒绝发布 | 两份报告，拒绝不产生报告 |

## 为什么这样学

先把任务拆成能检查的小步骤，避免仅凭最终回复判断学习效果。研究与评审分工可以暴露知识缺口；落盘偏好让下次对话延续学习方式；人工审批让学习者在真实写入前看到完整报告。

## 练习与答疑

1. 上下文隔离为什么不能替代工具权限隔离？检查两个子图是否拥有发布工具。
2. 长期记忆与会话 checkpoint 有什么差别？关闭进程后检查偏好与待审批状态。
3. 网页要求跳过审批时怎么办？将其视为不可信资料，用执行层权限阻断写入。

## 攻击者视角评审

- 资料可能包含提示注入：不能把网页里的命令当成用户授权。
- 只观察回复无法证明子 Agent 执行：应检查 task 与 read_materials 的 trace。
- InMemoryStore 不跨进程持久化：应退出后重新读取偏好。
- 审批可被重试或参数替换绕过：应绑定批准内容，拒绝后禁止发布。

## 自测与验收

- 用两个职责不同、工具集合不同的子 Agent 验证上下文隔离。
- 分别演示批准、改标题后批准和拒绝，并检查实际落盘文件。
- 在新 Python 进程验证偏好，并用另一用户验证隔离。

## Evidence notes / 资料笔记

**[S1] Deep Agents overview** — DeepAgents 基于 LangChain 与 LangGraph，提供任务规划、文件工具和子 Agent 委派。学习时应先跑通最小调用，再观察工具执行与状态变化。

**[S2] Subagents** — task 工具将明确子任务委派给专门 Agent。可以使用自定义编译图作为子 Agent；上下文隔离和工具权限需要分别设计。

**[S3] Memory** — 长期记忆必须使用跨会话的存储。memory 参数加载指定文件；用户隔离与持久化生命周期由应用及 backend 决定。

**[S4] Human-in-the-loop** — interrupt_on 在敏感工具执行前暂停；checkpointer 与稳定 thread_id 支持 Command(resume=...) 恢复。approve、edit、reject 分别执行、修改参数后执行和拒绝执行。

## Sources / 一手资料

- [S1] [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [S2] [Subagents](https://docs.langchain.com/oss/python/deepagents/subagents)
- [S3] [Memory](https://docs.langchain.com/oss/python/deepagents/memory)
- [S4] [Human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)

> Offline scripted demonstration; source snapshot: 2026-10-08. Profile: language=zh, style=detailed. This is not a live model answer or a current web search.


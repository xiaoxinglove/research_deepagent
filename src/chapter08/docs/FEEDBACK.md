# 验收反馈与真实体验记录

本文件区分可重复的自动化验收与真实学习者反馈。自动化检查由开发代理运行，不能代表外部用户已使用项目，也不能代表真实模型的教学质量已经验证。

## 首次离线自动化验收反馈（历史）

执行日期：2026-10-08（北京时间）。执行人：开发代理。首次记录：一键离线演示已实测通过，16 项安全与业务回归测试全部通过，耗时 8.389 秒。API 配置更新后的最终测试与真实调用结果见下节。

证据：[验收汇总](../artifacts/demo/summary.json)、[跨进程记忆检查](../artifacts/demo/memory-check.json)、[演示页](../artifacts/demo/demo.html)、[实际测试输出](../artifacts/demo/test-results.txt)。本次记录的演示验证时间为 14:41:50，三条审批分支使用独立 Thread。

| 检查 | 预期结果 | 当前结果 |
| --- | --- | --- |
| 锁定依赖安装 | `uv sync --locked` 成功 | 通过：已按锁文件同步依赖 |
| 离线项目运行 | 不需要外部 API Key，真实 DeepAgents 图完成任务 | 通过：三分支完成 |
| 任务规划 | 轨迹记录 `write_todos` | 通过：三分支的 todos 均完成，拒绝分支明确取消发布 |
| 子 Agent | 委派课程研究员和学习审查员 | 通过：每分支真实执行两次 `task` 和 `read_materials` |
| 长期记忆 | 不同进程读取同一用户的 JSON 偏好 | 通过：新 Python 进程读回 Alice 的 `zh/detailed`；Bob 仍为默认 `zh/concise` |
| 批准发布 | 创建本地 `report.md` | 通过：审批前没有报告，批准后创建报告 |
| 编辑发布 | 实际报告采用审批后参数 | 通过：报告标题为「人工修订：DeepAgents 课程学习计划」 |
| 拒绝发布 | 终止流程，无报告、无重试 | 通过：拒绝分支未产生报告，状态为 `published=false` |
| 演示素材 | 汇总页、轨迹、对话、结果均存在 | 通过：HTML 总览、三分支记录与 JSON 检查证据已生成 |
| 浏览器查看 | 总览可显示，批准 / 拒绝结果可展开 | 通过：实际打开并展开页面，三张截图已保存 |
| 安全回归 | 偏好验证、精确审批、权限隔离等反例通过 | 通过：16 项全部通过，8.389 秒，结果为 `OK` |
| 真实模型 | 至少一次实际供应商调用与内容评估 | 首次离线验收时未验证；追加 API 验证见下节 |

默认演示每次自动创建新的目录，避免覆盖已提交的素材；安全回归命令为：

```powershell
.\.venv\Scripts\python.exe -m chapter08.demo demo
.\.venv\Scripts\python.exe -m unittest chapter08.test_project -v
```

回归包括审批前无副作用、未授权直接调用、拒绝后重试、重复发布、标题或正文参数替换、用户路径穿越、污染 JSON、跨进程与跨用户记忆、英文详细材料、输出目录保留和真实模式禁止脚本审批。恶意研究子 Agent 尝试 `publish_report` 收到「not a valid tool」；恶意题目未造成路径逃逸，拒绝后没有报告。

## 2026-10-08 API 配置追加验证

真实模型和搜索 API 已改为读取 `src/chapter08/.env`；本章文件存在时不混入根目录 `.env` 或终端环境变量。现有 GLM 密钥与地址保持原值，仅将 `GLM_MODEL` 从接口不接受的 `glm-5.3` 修正为完整 ID `zai-org/GLM-5.3`。原模型名返回 HTTP 400、代码 `20012`、`Model does not exist`；平台模型列表与 [SiliconFlow 官方说明](https://www.siliconflow.com/zh-tw/blog/glm-5.3-now-live-on-siliconflow) 支持该修正。

21:30:21（北京时间）已实测真实 API 返回与工具调用，见 [脱敏验证结果](../artifacts/api-check.json)。API 探测通过不代表学习材料质量已获得评价。配置调整阶段新增 9 项回归，当时完整 25 项测试全部通过，耗时 7.958 秒，见 [配置阶段测试输出](../artifacts/demo/test-results-env.txt)。首次离线验收的 16 项测试与用户实际反馈保留不变。

启用 API 流式响应阶段的回归为 25 项全部通过，耗时 8.284 秒；[流式配置阶段测试输出](../artifacts/demo/test-results-api-final.txt) 已随附，配置测试包含 `streaming=True` 断言。该日志保留作为阶段证据，最终结果见本节末尾。

评审员输入在非流式调用时曾遇到 60 秒超时；改为流式响应后，21:37:20（北京时间）的同输入重放取得真实响应，见 [流式重放证据](../artifacts/api-streaming-check.json)。该次默认推理配置下的单次评审约耗时 4 分 13 秒。[官方说明](https://www.siliconflow.com/zh-tw/blog/glm-5.3-now-live-on-siliconflow) 列出 GLM-5.3 的 `low`、`high`、`max` 三种推理强度并注明服务默认 `max`；本项目随后为该模型默认设置 `low`，允许通过本章 `.env` 的 `GLM_REASONING_EFFORT` 覆盖。未配置 Tavily 时，也提示研究员一次读取完整快照。

21:49:45（北京时间）开始的真实 `live` 工作流拒绝分支验证已完成，耗时 145.5 秒，约 2 分 25 秒。实际执行 `write_todos` 4 次，分别委派 `course-researcher`、`learning-reviewer` 各 1 次，`read_materials` 1 次；收到 `publish_report` 人工审批中断，审批前无报告，测试拒绝后仍无报告且 `published=false`。见 [真实工作流验证](../artifacts/api-workflow-check.json)，运行轨迹位于 [本次运行目录](../artifacts/run-live-ready-check-e9fc881f)。这是自动化真实 API 拒绝测试，不是用户体验评价，也不证明真实模式批准保存已测试。实际运行仍需等待多轮模型调用，耗时会变化。

最终 28 项回归全部通过，耗时 8.218 秒，见 [最终测试输出](../artifacts/demo/test-results-api-ready.txt)。最后新增的 3 项测试在本地检查 SDK 实际请求体，验证推理强度默认值与覆盖、其他模型不注入参数、无效值拒绝，不发起真实网络请求。历史 16 / 25 项日志保留，当前验收采用最终 28 项结果。

## 已知限制与改进方向

- 离线模型为确定性脚本，只证明流程、子图与审批可运行；教学内容质量需要真实模型和学习者评估。
- 离线材料范围固定为 DeepAgents 课程，改变 `--topic` 仅调整目标，不提供任意学科知识答疑。
- 未启用在线搜索时资料来自固定官方快照，不代表最新课程或 API 变化。
- JSON 偏好适合单机课程演示。多人并发、跨设备同步与用户身份认证属于后续扩展。
- 待审批 checkpoint 仅存在于当前进程内存中，进程退出后需要重新发起任务。
- 学习审查员能指出疑点，不能替代来源核查和权限约束。继续以拒绝发布、编辑参数绑定、子 Agent 权限隔离等反例检验流程。
- 攻击者回归验证确定性离线模型与执行层边界，不代表真实 LLM 已全面抵御提示注入。

## 真实体验反馈表

状态：已收到本次项目用户的真实反馈。来源为 2026-10-08 当前项目聊天中的实际回答；流程清晰度通过 `feedback` CLI 写入 [feedback.jsonl](../artifacts/demo/feedback.jsonl)。下表只记录实际回答，未询问或未回答的维度保持未评价。

| 字段 | 实际记录 |
| --- | --- |
| 体验日期与演示方式 | 2026-10-08；项目演示与聊天反馈 |
| 体验者角色（可匿名） | 当前项目用户（匿名） |
| 运行模式与题目 | offline 课程演示；如何学习 DeepAgents 并完成课程综合项目 |
| 流程清晰度评分（1–5） | 5；原回答：「5 分：清楚」 |
| 学习计划可执行性评分（1–5） | 未评价：未询问、未回答 |
| 是否理解批准、编辑、拒绝的区别 | 未评价：未询问、未回答 |
| 最有帮助的内容 | 未评价：未询问、未回答 |
| 发现的问题与对应运行目录 | 未评价：未询问、未回答 |
| 建议与后续改进 | 原回答：「当前演示已够用」 |
| 运行方式偏好 | 用户确认：「命令行一键演示（推荐）」 |
| 演示记录位置 | [HTML 演示](../artifacts/demo/demo.html)、[总览截图](../artifacts/demo/overview.jpg)、[批准报告截图](../artifacts/demo/approved-report.jpg)、[拒绝结果截图](../artifacts/demo/rejected-report.jpg)；未提供录屏 |

也可以用 CLI 记录一条实际评分与评论：

```powershell
.\.venv\Scripts\python.exe -m chapter08.demo feedback --output .\src\chapter08\artifacts\demo --rating 4 --comment '替换为实际体验反馈'
```

后续体验者可继续补充真实反馈，保持运行轨迹与评论能够对应。当前反馈确认流程清晰与演示形式足够，没有对真实模型的教学质量作评价。

# CoursePilot 演示脚本

建议用 5–7 分钟完成演示。屏幕录制与真实人的体验评论需要由演示者实际完成；项目提供运行素材与讲解脚本。

## 演示前准备

从 `research_deepagent` 根目录执行：

```powershell
uv sync --locked
.\.venv\Scripts\python.exe -m chapter08.demo demo
```

打开终端打印的 `demo.html` 路径，也可直接打开仓库已附带的 `src/chapter08/artifacts/demo/demo.html`。默认每次生成新的时间戳与 UUID 目录，可重复执行。保留终端窗口，便于展示命令确实运行，以及每个运行目录的 `trace.jsonl`、`transcript.md`、`result.json` 和已批准的 `report.md`。使用显式 `--output` 时，目录必须为空。

离线演示通过上述 CLI 命令执行。若要展示真实 API 调用，双击 `src/chapter08/start_live.bat`；它运行一次 `run --mode live`，报告保存前仍会等待人工审批。真实模型与搜索的应用配置读取 `src/chapter08/.env`；现有 GLM 文件中的 `GLM_API_KEY`、`GLM_BASE_URL`、`GLM_MODEL` 可直接使用。本章文件存在时，应用配置加载器不读取根目录 `.env`，也不合并终端变量；底层 SDK 对未显式传入参数的默认行为见 README 的 API 配置说明。多个供应商密钥并存时，在本章文件中指定 `CHAPTER08_PROVIDER`；`CHAPTER08_MODEL` 可覆盖供应商模型变量。演示过程不要展示配置文件内容。

随附浏览器演示截图可直接用于提交：[总览](../artifacts/demo/overview.jpg)、[批准报告展开](../artifacts/demo/approved-report.jpg)、[拒绝结果展开](../artifacts/demo/rejected-report.jpg)。

说明本次演示采用确定性离线模型，使用真实 DeepAgents / LangGraph 工作流与本地官方资料快照。模型输出的教学内容按脚本固定，范围是 DeepAgents 课程；调整题目不会使它成为任意学科的知识答疑系统。不能将本次展示描述为实时联网或自由推理效果。

## 讲解流程

| 时间 | 演示操作 | 讲解要点与证据 |
| --- | --- | --- |
| 0:00–0:40 | 展示题目和 README 的四项能力表 | 用户想学会 DeepAgents 并完成综合项目；产物包含学习目标、阶段计划、练习和验收标准 |
| 0:40–1:30 | 打开批准分支的轨迹与对话 | 展示 `write_todos` 创建并更新任务；它让遗漏步骤可见 |
| 1:30–2:30 | 展示两次 `task` 委派 | `course-researcher` 整理一手资料；`learning-reviewer` 检查知识缺口、提示注入和权限绕过；子 Agent 无发布权限 |
| 2:30–3:15 | 展示 `memory-check.json`，运行下方 `memory` 命令 | 学习材料语言、讲解详细程度由用户显式保存，另一个进程可读取；模型不能改宿主机偏好文件 |
| 3:15–4:45 | 依次展示批准、编辑、拒绝三分支 | 审批展示完整参数；编辑后的标题与报告一致；拒绝分支没有 `report.md`，该次流程终止 |
| 4:45–5:30 | 打开批准后的学习报告 | 指出学习目标、分阶段计划、练习、验收方式和来源；说明质量评价需真实模型 / 学习者验证 |
| 5:30–6:30 | 展示或记录实际体验反馈 | 展示本次用户「5 分：清楚」与「当前演示已够用」的实际记录；新体验者可用反馈命令记录，区分自动化验收与真实人的反馈 |

## 现场交互命令

为了展示审批不是只存在于静态素材中，可单独运行一次：

```powershell
.\.venv\Scripts\python.exe -m chapter08.demo remember --user-id presenter --language zh --style concise --data-dir .\src\chapter08\artifacts\presenter-memory
.\.venv\Scripts\python.exe -m chapter08.demo memory --user-id presenter --data-dir .\src\chapter08\artifacts\presenter-memory
.\.venv\Scripts\python.exe -m chapter08.demo run --mode offline --topic '如何学习 DeepAgents 并完成课程综合项目' --user-id presenter --data-dir .\src\chapter08\artifacts\presenter-memory --output .\src\chapter08\artifacts\presenter-run
```

在审批提示处查看完整参数后选择编辑，按提示修改标题；系统再次显示完整参数后，明确输入 `approve` 才会保存，其他输入一律拒绝。当前 CLI 的编辑功能修改标题，正文仍按完整显示的参数审批。想展示拒绝时，请使用新的输出目录运行第二次，选择拒绝并检查其中没有 `report.md`。

真实模型现场演示可以将上述 `run` 命令的 `--mode offline` 改为 `--mode live`，或直接使用 `start_live.bat`。应保留该次实际调用的轨迹和结果，单独评价学习材料质量；离线截图与固定输出不能作为真实模型运行证据。

现已附 [真实 API 工作流验证](../artifacts/api-workflow-check.json)：任务规划、两个子 Agent、一次资料读取执行后，报告保存等待人工审批中断，测试拒绝后没有报告。该次真实调用约 2 分 25 秒；现场演示预留模型等待时间，实际耗时会变化。这份证据来自自动化真实 API 拒绝测试，真实模式批准保存与学习者教学质量评价仍需现场执行和反馈。最终 [28 项回归测试](../artifacts/demo/test-results-api-ready.txt) 已通过。

记录真实体验：

```powershell
.\.venv\Scripts\python.exe -m chapter08.demo feedback --output .\src\chapter08\artifacts\demo --rating 4 --comment '请在此填写演示者实际体验后的评价'
```

请将 `--output` 换成本次演示目录，或保留路径以评价随附标准素材，并替换示例评分与评论。录屏时避免显示 `.env` 或 API 密钥。

## 从攻击者角度做一次反例验证

1. 指出课程资料是输入材料，不能赋予子 Agent 发布报告的权限。
2. 在拒绝分支中验证：模型即使准备好了内容，拒绝后也不能生成报告或重试发布。
3. 展示编辑分支：审批后的标题是报告实际使用的标题，避免「审批前是一份、保存后是另一份」。
4. 展示本地偏好文件与 CLI 枚举字段：长期记忆只接收用户明确提交的受限值，不把模型生成文本直接写进下一次运行的记忆。

这些检查验证的是已实现的边界，不宣称已经抵御所有提示注入或模型攻击。

## 提交前清单

- [ ] 从项目根目录成功运行 `demo`，保留返回结果与产物。
- [ ] 浏览器能打开 `demo.html`，三个分支都可查看。
- [ ] 展示中能定位 `write_todos` 和两个子 Agent 的委派事件。
- [ ] 已展示另一个进程读取偏好。
- [ ] 编辑报告与审批参数一致，拒绝分支无报告。
- [ ] 附上随附浏览器截图与真实反馈；课程若另要求录屏，再实际录制并提交。
- [ ] 提交材料中不包含 API Key、私人信息或未经脱敏的真实学习者数据。

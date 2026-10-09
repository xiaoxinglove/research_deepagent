# 本项目为自学deepagents教程
主要内容均在src里面，按照PDCA来进行循环迭代。
跟着张海立老师的教程一步一步走。

###  结课demo放在src\chapter08-demo里面

## 目录与架构

```text
research_deepagent/
├── README.md                     # 项目简介与目录导航
├── pyproject.toml / uv.lock       # Python 依赖声明与锁文件
├── .env                          # 本地模型与工具凭证（不提交）
├── .agentseek/lifecycle.toml      # 旧研究应用的服务与任务配置
├── langgraph.json                # 旧 research 图配置，目标脚本已不存在
├── frontend/                     # 保留的 React / TypeScript / Vite 前端
│   ├── .env.example              # 前端配置样例
│   └── src/                      # 会话、工具卡片、规划与 Markdown 渲染
├── src/
│   ├── chapter02/                # DeepAgent 入门
│   ├── chapter03/                # StateBackend、文件后端与基准实验
│   ├── chapter04/                # 规划分解与联网探测
│   ├── chapter05/                # 多 Agent 协作
│   ├── chapter06/                # Skills 与异步子 Agent
│   │   ├── skill.py / skills/    # Skills 加载脚本与技能文件
│   │   ├── async_agent.py        # 并行子任务、追加指令、取消与恢复
│   │   └── langgraph.async.json  # 主管与两个子 Agent 的服务配置
│   ├── chapter07/                # 记忆与人工审批
│   ├── chapter08-demo/           # CoursePilot 独立 CLI
│   │   ├── README.md             # 演示运行说明
│   │   ├── start_live.bat / demo.py # 真实入口与 CLI
│   │   ├── agent.py / offline.py # 工作流与离线模型
│   │   ├── test_project.py       # 配置、安全与业务回归
│   │   ├── evidence.json         # 官方资料快照
│   │   └── docs/ / artifacts/    # 演示说明、验收反馈与运行证据
│   └── chapter09/                # 沙箱执行学习与练习
│       ├── 第九章任务.md          # 沙箱接入、文件传输、隔离与生命周期学习任务
│       └── sandbox.py            # 沙箱练习脚本（当前为空，待实现）
└── 课程目标.md                   # 课程综合项目要求
```



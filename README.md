#本项目为自学deepagent教程
主要内容均在src里面，按照PDCA来进行循环迭代。
跟着张海立老师的教程一步一步走。



## 目录与架构

```text
research_deepagent/
├── README.md                     # 全局安装、运行与验收导航
├── pyproject.toml / uv.lock       # Python 依赖声明与锁文件
├── .agentseek/lifecycle.toml      # Web 服务、进程、检查与任务
├── langgraph.json                # research 图注册、根 .env 加载
├── frontend/                     # React / TypeScript / Vite
│   ├── .env.example              # 前端配置样例
│   └── src/                      # 会话、工具卡片、规划与 Markdown 渲染
├── src/research_deepagent/        # 研究图、提示词与搜索工具
├── src/chapter02/                # DeepAgent 入门
├── src/chapter03/                # StateBackend、文件后端与基准实验
├── src/chapter04/                # 规划分解与联网探测
├── src/chapter05/                # 多 Agent 协作
├── src/chapter06/                # Skills 与相关练习
├── src/chapter07/                # 记忆与人工审批
├── src/chapter08-demo/                # CoursePilot 独立 CLI
│   ├── start_live.bat / demo.py   # 真实入口与 CLI
│   ├── agent.py / offline.py     # 工作流与离线模型
│   ├── test_project.py           # 配置、安全与业务回归
│   ├── evidence.json             # 官方资料快照
│   └── docs/ / artifacts/        # 演示说明、验收反馈与运行证据
└── 课程目标.md                   # 课程综合项目要求
```

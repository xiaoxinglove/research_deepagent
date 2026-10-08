"""python -m chapter08.demo demo：课程项目一键运行与验收。"""

import argparse
from datetime import datetime, timedelta, timezone
import html
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chapter08.agent import (CourseSession, DEFAULT_TOPIC, HERE, load_preferences,
                             save_preferences, validate_report)


def now():
    return datetime.now(timezone(timedelta(hours=8)))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def run_session(args):
    if args.mode == "live" and args.decision:
        raise ValueError("live 模式必须交互审核完整报告，不能通过命令行自动批准")
    session = CourseSession(mode=args.mode, topic=args.topic, user_id=args.user_id,
                            data_dir=args.data_dir, output=args.output)
    print(f"[START] CoursePilot | {args.mode} | thread={session.thread_id}", flush=True)
    session.start()
    action = session.pending_action()
    print("\n[HITL] 以下是将保存到 report.md 的完整报告：\n", flush=True)
    print(json.dumps(action["args"], ensure_ascii=False, indent=2), flush=True)
    decision, title = args.decision, args.edited_title
    if decision is None:
        decision = input("人工选择 approve / edit / reject（回车默认 reject）：").strip().lower() or "reject"
        if decision == "edit":
            title = input("请输入修改后的标题：").strip()
            edited = validate_report({**action["args"], "title": title})
            print(json.dumps(edited, ensure_ascii=False, indent=2), flush=True)
            if input("确认上述完整参数？输入 approve，否则拒绝：").strip().lower() != "approve":
                decision = "reject"
    session.decide(decision, title)
    result = session.export()
    print(f"\n[DONE] decision={decision} published={result['published']} output={session.output}")
    return result


def run_demo(output: Path):
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("演示目录非空；请指定新的 --output 目录，已有素材将保留")
    output.mkdir(parents=True, exist_ok=True)
    data_dir = output / "data"
    saved = {"language": "zh", "style": "detailed"}
    save_preferences(data_dir, "alice", saved)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(HERE.parent)
    env["PYTHONIOENCODING"] = "utf-8"
    probe = subprocess.run([sys.executable, "-m", "chapter08.demo", "memory", "--user-id", "alice", "--data-dir", str(data_dir)],
                           check=True, capture_output=True, text=True, encoding="utf-8", env=env, timeout=45)
    restored = json.loads(probe.stdout)
    other_user = load_preferences(data_dir, "bob")
    if restored != saved or other_user == saved:
        raise RuntimeError("跨进程记忆或用户偏好隔离检查失败")
    memory_check = {"saved": saved, "restored_in_new_process": restored, "other_user": other_user,
                    "cross_process_pass": True, "user_isolation_pass": True}
    write_json(output / "memory-check.json", memory_check)
    print("[PASS] 跨进程长期记忆与不同用户偏好隔离", flush=True)
    runs = []
    for decision in ("approve", "edit", "reject"):
        session = CourseSession(mode="offline", topic=DEFAULT_TOPIC, user_id="alice", data_dir=data_dir, output=output / decision)
        session.start()
        session.pending_action()
        if (session.output / "report.md").exists():
            raise RuntimeError("报告在审批前产生")
        session.trace.emit("demo_assertion", check="no_report_before_approval", passed=True)
        session.decide(decision, "人工修订：DeepAgents 课程学习计划" if decision == "edit" else None)
        result = session.export()
        events = [json.loads(line) for line in session.trace.path.read_text(encoding="utf-8").splitlines()]
        tools = [e for e in events if e["event"] == "tool_start"]
        delegates = [e for e in tools if e["name"] == "task"]
        if len(delegates) != 2 or not any(e["name"] == "read_materials" for e in tools):
            raise RuntimeError("缺少真实子 Agent 委派或资料工具调用")
        if not result["todos"] or any(t["status"] != "completed" for t in result["todos"]):
            raise RuntimeError("计划未闭环")
        report = session.output / "report.md"
        if report.exists() != (decision != "reject"):
            raise RuntimeError("审批结果与磁盘副作用不符")
        if decision == "edit" and not report.read_text(encoding="utf-8").startswith("# 人工修订："):
            raise RuntimeError("修改后的标题未执行")
        runs.append(result)
        print(f"[PASS] {decision}: delegates=2 todos=completed report={report.exists()}", flush=True)
    summary = {"project": "CoursePilot", "mode": "offline scripted model + real DeepAgents graph",
               "validated_at": now().isoformat(),
               "capabilities": ["task_planning", "subagents", "persistent_memory", "human_in_the_loop"],
               "memory": memory_check, "runs": runs,
               "external_human_feedback": "pending", "live_model_validation": "not_run"}
    write_json(output / "summary.json", summary)
    write_demo_page(output, summary)
    (output / "console.txt").write_text(
        "CoursePilot offline demonstration\nPASS cross-process memory\nPASS user isolation\n"
        "PASS approve: report created\nPASS edit: edited title saved\nPASS reject: no report\n"
        "PASS all scenarios: write_todos, two task calls, read_materials, real HITL\n", encoding="utf-8")
    print(f"[DONE] 演示素材：{output / 'demo.html'}", flush=True)
    return summary


def write_demo_page(output: Path, summary: dict):
    cards = []
    for run in summary["runs"]:
        decision = run["decisions"][0]
        transcript = (output / decision / "transcript.md").read_text(encoding="utf-8")
        report_path = output / decision / "report.md"
        report = report_path.read_text(encoding="utf-8") if report_path.exists() else "人工拒绝：未创建 report.md。"
        cards.append(f"<section><h2>{decision.upper()} · {'已保存' if run['published'] else '已拒绝'}</h2>"
                     f"<p>独立 Thread：<code>{run['thread_id']}</code> · 学习偏好：{html.escape(str(run['preferences']))}</p>"
                     f"<details><summary>完整学习报告 / 拒绝结果</summary><pre>{html.escape(report)}</pre></details>"
                     f"<details><summary>查看真实工具、子 Agent 与审批记录</summary><pre>{html.escape(transcript)}</pre></details>"
                     f"<p><a href='{decision}/result.json'>结果 JSON</a> · <a href='{decision}/trace.jsonl'>执行 Trace</a> · "
                     f"<a href='{decision}/transcript.md'>完整文字记录</a></p></section>")
    page = """<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CoursePilot 综合项目演示</title><style>
body{background:#f3f6fb;color:#183047;font:16px/1.7 system-ui,sans-serif;max-width:1050px;margin:40px auto;padding:0 24px}
header,section{background:white;border:1px solid #dce4ef;border-radius:16px;padding:28px;margin:20px 0}
h1{font-size:34px;margin:0}h2{font-size:23px}a{color:#1767a6}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fa;padding:18px;font-size:14px}
summary{cursor:pointer;font-weight:600;padding:12px 0}.badge{display:inline-block;background:#e5f4eb;color:#206040;padding:5px 12px;border-radius:8px;margin:5px}
</style><header><p>CHAPTER 08 · 课程学习与答疑助教</p><h1>CoursePilot</h1>
<p>从学习目标出发：规划 → 课程研究员 → 学习评审员 → 按长期偏好编写 → 人工审核。</p>
<p><span class="badge">任务规划 ✓</span><span class="badge">两个子 Agent ✓</span><span class="badge">跨进程记忆 ✓</span><span class="badge">人工审批 ✓</span></p>
<p>此页面来自实际离线运行。模型响应为公开的确定性脚本，工具、子图、记忆和审批真实执行；不代表真实模型能力或最新联网研究。</p></header>"""
    page += "<section><h2>长期记忆验证</h2><pre>" + html.escape(json.dumps(summary["memory"], ensure_ascii=False, indent=2)) + "</pre><p>已在新的 Python 进程读取 Alice 偏好；Bob 使用默认偏好。</p></section>"
    page += "".join(cards)
    feedback_file = output / "feedback.jsonl"
    if feedback_file.exists():
        records = [json.loads(line) for line in feedback_file.read_text(encoding="utf-8").splitlines()]
        feedback_text = "".join(f"<p>评分：{record['rating']}/5 · {html.escape(record['comment'])}</p>" for record in records[-5:])
    else:
        feedback_text = "<p>真实使用者反馈待填写，可通过 feedback 命令记录。</p>"
    page += "<section><h2>反馈与限制</h2><p>自动验收已完成。</p>" + feedback_text
    page += "<p>会话审批 checkpoint 只保存在内存中，进程退出后需要重新发起任务。</p><a href='summary.json'>完整验收汇总</a></section></html>"
    (output / "demo.html").write_text(page, encoding="utf-8")


def parser():
    cli = argparse.ArgumentParser(description="CoursePilot 课程学习与答疑助教")
    commands = cli.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="一键运行三种审批和跨进程记忆验收")
    demo.add_argument("--output", type=Path, default=HERE / "artifacts" / ("demo-" + now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]))
    run = commands.add_parser("run", help="发起学习任务并人工审核")
    run.add_argument("--mode", choices=["offline", "live"], default="offline")
    run.add_argument("--topic", default=DEFAULT_TOPIC)
    run.add_argument("--decision", choices=["approve", "edit", "reject"], help="仅离线演示可脚本化审批")
    run.add_argument("--edited-title")
    run.add_argument("--output", type=Path, default=HERE / "artifacts" / ("run-" + now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]))
    for name, help_text in [("remember", "显式保存学习偏好"), ("memory", "查看当前用户长期偏好")]:
        cmd = commands.add_parser(name, help=help_text)
        cmd.add_argument("--user-id", default="alice")
        cmd.add_argument("--data-dir", type=Path, default=HERE / ".data")
        if name == "remember":
            cmd.add_argument("--language", choices=["zh", "en"], default="zh")
            cmd.add_argument("--style", choices=["concise", "detailed"], default="concise")
    run.add_argument("--user-id", default="alice")
    run.add_argument("--data-dir", type=Path, default=HERE / ".data")
    feedback = commands.add_parser("feedback", help="记录真实体验者评分，不替代自动验收")
    feedback.add_argument("--output", type=Path, required=True)
    feedback.add_argument("--rating", type=int, choices=range(1, 6), required=True)
    feedback.add_argument("--comment", required=True)
    return cli


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "demo":
            run_demo(args.output)
        elif args.command == "run":
            run_session(args)
        elif args.command == "remember":
            path = save_preferences(args.data_dir, args.user_id, {"language": args.language, "style": args.style})
            print(f"已保存：{path}")
        elif args.command == "memory":
            print(json.dumps(load_preferences(args.data_dir, args.user_id), ensure_ascii=False))
        elif args.command == "feedback":
            if not args.output.is_dir() or not (args.output / "summary.json").exists():
                raise ValueError("反馈必须指向已完成的一键演示目录")
            if not args.comment.strip() or len(args.comment) > 4000:
                raise ValueError("反馈须为 1–4000 字符")
            summary = json.loads((args.output / "summary.json").read_text(encoding="utf-8"))
            if not isinstance(summary, dict):
                raise ValueError("演示汇总格式无效")
            with (args.output / "feedback.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"rating": args.rating, "comment": args.comment,
                    "submitted_at": now().isoformat(), "source": "user_supplied"}, ensure_ascii=False) + "\n")
            summary["external_human_feedback"] = "received"
            write_json(args.output / "summary.json", summary)
            if "runs" in summary and "memory" in summary:
                write_demo_page(args.output, summary)
            print("已记录体验反馈。")
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[ERROR] {type(exc).__name__}；运行未完成，请检查模型服务或使用 offline 模式。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

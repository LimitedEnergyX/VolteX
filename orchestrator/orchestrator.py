#!/usr/bin/env python3
"""VolteX agent orchestrator — local task dispatcher."""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config — fixed local paths (single-machine setup)
# ---------------------------------------------------------------------------

VOLTEX_ROOT = Path(r"D:\AI-Agents\VolteX")
LOGS_DIR = VOLTEX_ROOT / "orchestrator" / "logs"
PROTECTED_BRANCH = "main"
MAX_TURNS = 3
TIMEOUT_SECONDS = 300

AGENTS = {
    "claude": {
        "worktree": VOLTEX_ROOT / "project-claude",
        "branch": "agent/claude",
        "cli": "claude",
        "available": True,
    },
    "codex": {
        "worktree": VOLTEX_ROOT / "project-chatgpt",
        "branch": "agent/chatgpt",
        "cli": "codex",
        "available": False,
        "unavailable_reason": (
            "Codex CLI not installed. "
            "Install and verify before using this worker."
        ),
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_current_branch(worktree: Path) -> str:
    r = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=worktree, capture_output=True, text=True,
    )
    return r.stdout.strip()


def build_command(agent_name: str, task: str) -> list[str]:
    if agent_name == "claude":
        return ["claude", "-p", "--max-turns", str(MAX_TURNS), task]
    if agent_name == "codex":
        return ["codex", "exec", task]
    raise ValueError(f"Unknown agent: {agent_name}")

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def run_task(agent_name: str, task: str, dry_run: bool) -> int:
    agent = AGENTS.get(agent_name)
    if agent is None:
        print(
            f"ERROR: Unknown agent '{agent_name}'. "
            f"Available: {', '.join(AGENTS)}",
            file=sys.stderr,
        )
        return 1

    if not agent["available"]:
        print(f"ERROR: {agent['unavailable_reason']}", file=sys.stderr)
        return 1

    worktree: Path = agent["worktree"]
    if not worktree.exists():
        print(f"ERROR: Worktree not found: {worktree}", file=sys.stderr)
        return 1

    branch = get_current_branch(worktree)
    if branch == PROTECTED_BRANCH:
        print(
            f"ERROR: Worktree '{worktree.name}' is on protected branch "
            f"'{PROTECTED_BRANCH}'. Refusing to run.",
            file=sys.stderr,
        )
        return 1

    cmd = build_command(agent_name, task)

    print(f"agent    : {agent_name}")
    print(f"branch   : {branch}")
    print(f"worktree : {worktree}")
    print(f"command  : {' '.join(cmd)}")
    print(f"timeout  : {TIMEOUT_SECONDS}s")
    print(f"dry-run  : {dry_run}")
    print("-" * 60)

    if dry_run:
        print("[dry-run] No execution. Command printed above.")
        return 0

    if not shutil.which(cmd[0]):
        print(f"ERROR: '{cmd[0]}' not found on PATH.", file=sys.stderr)
        return 127

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = LOGS_DIR / f"{ts}_{agent_name}.log"
    start = datetime.now()

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(worktree),
            timeout=TIMEOUT_SECONDS,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        end = datetime.now()
        stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode

    except subprocess.TimeoutExpired as exc:
        end = datetime.now()
        stdout = (exc.stdout or b"").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = f"[TIMEOUT after {TIMEOUT_SECONDS}s]"
        returncode = 124

    except FileNotFoundError:
        end = datetime.now()
        stdout, stderr = "", f"[CLI not found: {cmd[0]}]"
        returncode = 127

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"agent      : {agent_name}\n")
        f.write(f"branch     : {branch}\n")
        f.write(f"worktree   : {worktree}\n")
        f.write(f"command    : {' '.join(cmd)}\n")
        f.write(f"start      : {start.isoformat()}\n")
        f.write(f"end        : {end.isoformat()}\n")
        f.write(f"duration   : {(end - start).total_seconds():.1f}s\n")
        f.write(f"returncode : {returncode}\n")
        f.write("-" * 60 + "\n")
        f.write("--- stdout ---\n")
        f.write(stdout or "")
        f.write("\n--- stderr ---\n")
        f.write(stderr or "")

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    print(f"\n[log: {log_path}]")
    print(f"[exit: {returncode}]")
    return returncode

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_run(args) -> int:
    return run_task(args.agent, args.task, args.dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="orchestrator",
        description="VolteX local agent dispatcher. Routes tasks to Claude or Codex workers.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Dispatch a task to an agent worker")
    run_p.add_argument(
        "--agent", required=True, choices=list(AGENTS),
        help="Target worker: claude | codex",
    )
    run_p.add_argument("--task", required=True, help="Task prompt string")
    run_p.add_argument(
        "--dry-run", action="store_true",
        help="Print the command without executing",
    )
    run_p.set_defaults(func=cmd_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

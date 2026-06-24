#!/usr/bin/env python3
"""VolteX agent orchestrator — local task dispatcher."""

import argparse
import os
import re
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
CODEX_FALLBACK_PATH = r"C:\Users\RDPJarvis\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe"

# ---------------------------------------------------------------------------
# Review bridge — structured verdict protocol
# ---------------------------------------------------------------------------

REVIEW_PROMPT_TEMPLATE = """\
You are a technical reviewer. Analyze the proposal below and respond with ONLY a structured verdict.

DO NOT edit any files. DO NOT run any commands. Return ONLY the formatted verdict.

If VERDICT is "Approved":
  VERDICT: Approved
  RECOMMENDATION: <one sentence>

If VERDICT is "Approved with changes" or "Do not proceed":
  VERDICT: <Approved with changes | Do not proceed>
  CONSTRAINT: <one sentence — what specific problem exists>
  PROPOSED_SOLUTION: <one sentence — what must change>
  COST_IMPACT: <one sentence — effort or risk level>
  TIMELINE: <one sentence — when this could be resolved>
  RECOMMENDATION: <one sentence — summary action>

--- REVIEW PACKET ---
{packet}
"""

VERDICT_RE = re.compile(
    r"^VERDICT:\s*(Approved with changes|Do not proceed|Approved)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
FIELD_RE = re.compile(
    r"^(CONSTRAINT|PROPOSED_SOLUTION|COST_IMPACT|TIMELINE|RECOMMENDATION):\s*(.+?)\s*$",
    re.MULTILINE,
)

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
        "available": True,
        "cli_fallback": CODEX_FALLBACK_PATH,
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


def resolve_cli(name: str, fallback: str | None = None) -> str | None:
    """Return the absolute path to a CLI.

    Resolution order:
    1. <NAME>_CLI_PATH env var (e.g. CODEX_CLI_PATH, CLAUDE_CLI_PATH)
    2. PATH lookup (.cmd / .ps1 wrappers included)
    3. Explicit fallback path (known install location)
    """
    env_path = os.environ.get(name.upper().replace("-", "_") + "_CLI_PATH")
    if env_path and Path(env_path).is_file():
        return env_path
    found = (
        shutil.which(name)
        or shutil.which(name + ".cmd")
        or shutil.which(name + ".ps1")
    )
    if found:
        return found
    if fallback and Path(fallback).is_file():
        return fallback
    return None


def make_exec_cmd(cmd: list[str], cli_fallback: str | None = None) -> list[str]:
    """
    Resolve the CLI to its absolute path and build a directly executable
    command without shell=True.

    On Windows, .cmd/.bat files are not directly executable by CreateProcess —
    they require cmd.exe. We wrap them explicitly rather than using shell=True
    to avoid any shell injection surface from task text.
    """
    cli_path = resolve_cli(cmd[0], fallback=cli_fallback)
    if cli_path is None:
        return cmd  # unresolved — let subprocess raise FileNotFoundError

    if sys.platform == "win32" and cli_path.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", cli_path] + cmd[1:]

    return [cli_path] + cmd[1:]


def build_command(agent_name: str, task: str) -> list[str]:
    if agent_name == "claude":
        return ["claude", "-p", "--max-turns", str(MAX_TURNS), task]
    if agent_name == "codex":
        return ["codex", "exec", "--sandbox", "read-only", task]
    raise ValueError(f"Unknown agent: {agent_name}")


def _latest_log(agent_name: str) -> Path | None:
    logs = sorted(LOGS_DIR.glob(f"*_{agent_name}.log"))
    return logs[-1] if logs else None


def _stdout_from_log(log_path: Path) -> str:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    marker = "--- stdout ---\n"
    idx = text.find(marker)
    if idx == -1:
        return ""
    after = text[idx + len(marker):]
    end = after.find("\n--- stderr ---")
    return after[:end] if end != -1 else after


def parse_verdict(output: str) -> dict:
    m = VERDICT_RE.search(output)
    verdict = m.group(1).strip() if m else None
    if verdict:
        # Normalise casing to canonical form
        canonical = {v.lower(): v for v in ("Approved", "Approved with changes", "Do not proceed")}
        verdict = canonical.get(verdict.lower(), verdict)
    fields = dict(FIELD_RE.findall(output))
    return {"verdict": verdict, "fields": fields}


def run_review(packet: str, dry_run: bool) -> int:
    task = REVIEW_PROMPT_TEMPLATE.format(packet=packet)
    rc = run_task("codex", task, dry_run)

    if dry_run:
        return rc

    if rc != 0:
        print(
            f"ERROR: Codex exited {rc}. Check the log above.",
            file=sys.stderr,
        )
        return 1

    log_path = _latest_log("codex")
    if log_path is None:
        print("ERROR: No Codex log found after run.", file=sys.stderr)
        return 1

    stdout = _stdout_from_log(log_path)
    result = parse_verdict(stdout)
    verdict = result["verdict"]
    fields = result["fields"]

    print("\n" + "=" * 60)
    print(f"REVIEW VERDICT: {verdict or 'NOT FOUND'}")
    print("=" * 60)

    if verdict is None:
        print(
            "WARNING: Codex did not return a structured verdict.\n"
            "Raw output is in the log file above.",
            file=sys.stderr,
        )
        return 1

    rec = fields.get("RECOMMENDATION", "")
    if verdict == "Approved":
        if rec:
            print(f"RECOMMENDATION: {rec}")
        return 0

    for field in ("CONSTRAINT", "PROPOSED_SOLUTION", "COST_IMPACT", "TIMELINE", "RECOMMENDATION"):
        print(f"{field}: {fields.get(field, 'Not provided')}")

    return 2 if verdict == "Approved with changes" else 3

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

    cli_fallback = agent.get("cli_fallback")
    cli_path = resolve_cli(cmd[0], fallback=cli_fallback)
    if cli_path is None:
        print(f"ERROR: '{cmd[0]}' not found on PATH.", file=sys.stderr)
        return 127

    exec_cmd = make_exec_cmd(cmd, cli_fallback=cli_fallback)
    print(f"resolved : {cli_path}")
    print(f"exec_cmd : {' '.join(exec_cmd)}")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = LOGS_DIR / f"{ts}_{agent_name}.log"
    start = datetime.now()

    try:
        proc = subprocess.run(
            exec_cmd,
            cwd=str(worktree),
            timeout=TIMEOUT_SECONDS,
            stdin=subprocess.DEVNULL,
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
        f.write(f"resolved   : {cli_path}\n")
        f.write(f"exec_cmd   : {' '.join(exec_cmd)}\n")
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


def cmd_review(args) -> int:
    if args.packet_file:
        packet = Path(args.packet_file).read_text(encoding="utf-8")
    else:
        packet = args.packet
    return run_review(packet, args.dry_run)


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

    review_p = sub.add_parser(
        "review",
        help="Send a review packet to Codex and capture a structured verdict",
    )
    packet_group = review_p.add_mutually_exclusive_group(required=True)
    packet_group.add_argument(
        "--packet", metavar="TEXT",
        help="Review packet as an inline string",
    )
    packet_group.add_argument(
        "--packet-file", metavar="PATH",
        help="Path to a file containing the review packet",
    )
    review_p.add_argument(
        "--dry-run", action="store_true",
        help="Print the Codex command without executing",
    )
    review_p.set_defaults(func=cmd_review)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

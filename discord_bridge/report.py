#!/usr/bin/env python3
"""Read-only data gatherers for the VolteX Discord operator interface.

No Discord dependency -- importable and compilable without discord.py.

All git access uses fixed, read-only git commands with a fixed working
directory and a short timeout. No caller-supplied (Discord) input is ever
passed into a subprocess argument list, and shell=True is never used.

This module never executes Codex, never calls orchestrator review, and never
mutates any state. It only reads local repo status, transcripts, and a static
template.
"""

import shutil
import subprocess
from pathlib import Path

VOLTEX_ROOT = Path(r"D:\AI-Agents\VolteX")
PROJECT_MAIN = VOLTEX_ROOT / "project-main"
REVIEWS_DIR = VOLTEX_ROOT / "orchestrator" / "reviews"
CODEX_FALLBACK_PATH = Path(
    r"C:\Users\RDPJarvis\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe"
)
GIT_TIMEOUT = 15

# Fixed, read-only git commands. No Discord input is ever appended to these.
_GIT_HEAD = ["git", "rev-parse", "--short", "HEAD"]
_GIT_STATUS = ["git", "status", "-sb"]
_GIT_TAGS = ["git", "tag", "--sort=-creatordate"]


def _run_git(args):
    """Run a fixed, read-only git command in PROJECT_MAIN.

    shell=False, fixed cwd, short timeout, stdin closed. `args` is always one of
    the module-level constants above -- never built from Discord input. Returns
    stripped stdout on success, or an empty string on any failure.
    """
    try:
        proc = subprocess.run(
            args,
            cwd=str(PROJECT_MAIN),
            timeout=GIT_TIMEOUT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def review_bridge_available():
    """Return True if the codex CLI resolves, without executing it.

    Only checks that the binary exists (PATH or the known install path). Never
    runs Codex.
    """
    if shutil.which("codex") or shutil.which("codex.cmd"):
        return True
    return CODEX_FALLBACK_PATH.is_file()


def gather_status():
    """Return a dict of read-only repo status fields for /voltex status."""
    head = _run_git(_GIT_HEAD) or "unknown"
    status = _run_git(_GIT_STATUS) or "unavailable"
    tags = _run_git(_GIT_TAGS)
    latest_tag = tags.splitlines()[0] if tags else "none"
    return {
        "main_commit": head,
        "worktree_status": status,
        "latest_tag": latest_tag,
        "review_bridge": "available" if review_bridge_available() else "unavailable",
    }


def _extract_section(text, header):
    """Return the lines under a markdown header up to the next header or '---'."""
    out = []
    capturing = False
    for line in text.splitlines():
        if line.strip() == header:
            capturing = True
            continue
        if capturing:
            if line.startswith("## ") or line.strip() == "---":
                break
            out.append(line)
    body = "\n".join(out).strip()
    return body or None


def _extract_field(text, name):
    """Return the value of a '**Name:** value' line, or None."""
    marker = "**" + name + ":**"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(marker):
            value = stripped[len(marker):].strip()
            return value or None
    return None


def latest_transcript():
    """Return (path, executive_summary, verdict) for the newest transcript.

    Read-only. Returns (None, None, None) if no transcript exists.
    """
    if not REVIEWS_DIR.is_dir():
        return None, None, None
    files = sorted(REVIEWS_DIR.glob("*_review.md"))
    if not files:
        return None, None, None
    path = files[-1]
    text = path.read_text(encoding="utf-8", errors="replace")
    summary = _extract_section(text, "## Executive Summary")
    verdict = _extract_field(text, "Verdict")
    return path, summary, verdict


PACKET_TEMPLATE = """\
## 1. Mission
<what is being decided or proposed?>

## 2. Current state
<current situation, repo state, or context>

## 3. Constraint
<constraint, limitation, or blocker -- or None>

## 4. Proposed action
<specific action proposed>

## 5. Commands or manual steps
<commands or steps that would be executed>

## 6. Files affected
<files created, modified, or deleted>

## 7. Risks
<what could go wrong>

## 8. Rollback plan
<how this is reversed>

## 9. Success criteria
<how we know it worked>

## 10. Requested reviewer
<ChatGPT | Codex | human>

## 11. Requested response format
Approved / Approved with changes / Do not proceed
If not approved: Constraint / Proposed solution / Cost-impact / Timeline / Recommendation
"""


def packet_template():
    """Return the canonical review-packet template text (template-only)."""
    return PACKET_TEMPLATE

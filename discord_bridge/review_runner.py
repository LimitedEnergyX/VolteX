#!/usr/bin/env python3
"""Run exactly one Codex read-only review via the existing orchestrator bridge.

Used by /voltex review. Invokes `orchestrator review --packet <text>` as a fixed
command list (no shell). The orchestrator path and working directory are derived
repo-relative from this module's location -- no absolute path is hard-coded.

Discord-supplied input (the packet text) is the ONLY user input. It is passed as
a single argument-list item and never controls the executable, the orchestrator
path, the working directory, or the command shape.

This module does not change the orchestrator pipeline or Codex permissions. Codex
remains read-only (enforced by the orchestrator). This module never reads .env.
"""

import asyncio
import re
import sys
from pathlib import Path

# Repo-relative: discord_bridge/review_runner.py -> parents[1] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR_PATH = REPO_ROOT / "orchestrator" / "orchestrator.py"

PACKET_MAX_LEN = 4000
REVIEW_TIMEOUT = 330  # seconds; just above the orchestrator's internal 300s limit

# Orchestrator review exit codes -> review verdicts (see orchestrator/README.md).
_VERDICT_BY_CODE = {
    0: "Approved",
    2: "Approved with changes",
    3: "Do not proceed",
}

_RECOMMENDATION_RE = re.compile(r"^RECOMMENDATION:\s*(.+?)\s*$", re.MULTILINE)
_TRANSCRIPT_RE = re.compile(r"\[transcript:\s*(.+?)\s*\]")


class ReviewResult:
    """Outcome of a /voltex review run.

    ok=True  -> a review verdict (exit 0/2/3); see verdict/recommendation/transcript.
    ok=False -> a bot/process failure (timeout, missing orchestrator, bad exit,
                exception); see error/detail. This is NOT a review verdict.
    """

    def __init__(self, ok, verdict=None, recommendation=None, transcript=None,
                 error=None, detail=None):
        self.ok = ok
        self.verdict = verdict
        self.recommendation = recommendation
        self.transcript = transcript
        self.error = error
        self.detail = detail


def validate_packet(packet):
    """Return (ok, message). Reject empty/whitespace or over-long packets."""
    if packet is None or not packet.strip():
        return False, "Empty packet -- provide review text."
    if len(packet) > PACKET_MAX_LEN:
        return False, f"Packet too long ({len(packet)} chars); max is {PACKET_MAX_LEN}."
    return True, ""


def _short(text, limit=300):
    return (text or "").strip().replace("\n", " ")[:limit]


async def run_review(packet):
    """Run one Codex read-only review via the orchestrator. Async, non-blocking.

    Returns a ReviewResult; classifies all normal failures rather than raising.
    """
    if not ORCHESTRATOR_PATH.is_file():
        return ReviewResult(False, error="Orchestrator not found",
                            detail=f"Missing: {ORCHESTRATOR_PATH}")

    # Fixed command list: executable, fixed orchestrator path, subcommand, then
    # the packet text as a single argument-list item. No shell, no user-controlled
    # path or command shape.
    cmd = [sys.executable, str(ORCHESTRATOR_PATH), "review", "--packet", packet]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(REPO_ROOT),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError as exc:
        return ReviewResult(False, error="Could not start review process",
                            detail=_short(str(exc)))

    try:
        out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=REVIEW_TIMEOUT)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        # Reap the killed child so it is not left as a transient zombie and does
        # not emit an asyncio ResourceWarning during garbage collection.
        try:
            await asyncio.wait_for(proc.wait(), timeout=5)
        except (asyncio.TimeoutError, ProcessLookupError):
            pass
        return ReviewResult(False, error="Review timed out",
                            detail=f"No result within {REVIEW_TIMEOUT}s.")

    code = proc.returncode
    stdout = (out_b or b"").decode("utf-8", errors="replace")
    stderr = (err_b or b"").decode("utf-8", errors="replace")

    if code in _VERDICT_BY_CODE:
        recs = _RECOMMENDATION_RE.findall(stdout)
        tr = _TRANSCRIPT_RE.search(stdout)
        return ReviewResult(
            True,
            verdict=_VERDICT_BY_CODE[code],
            recommendation=recs[-1] if recs else None,
            transcript=tr.group(1) if tr else None,
        )

    # exit 1 / unexpected code -> bot/process failure (not a verdict).
    return ReviewResult(False, error=f"Review process failed (exit {code})",
                        detail=_short(stderr) or _short(stdout) or "(no output)")

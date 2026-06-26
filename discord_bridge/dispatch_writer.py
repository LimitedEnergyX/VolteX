#!/usr/bin/env python3
"""Write a structured Claude task packet to a local, gitignored outbox.

Used by /voltex dispatch. The operator submits a bounded task from Discord; this
module validates it, sanitizes a filename, and writes a self-contained Markdown
packet to orchestrator/dispatch_outbox/. It does NOT execute anything: Claude runs
the task later, manually, only after the operator explicitly instructs it to.

Safety properties:
- The only user input that reaches the filesystem path is the title, and only
  after it is reduced to [a-z0-9-] (no dots, slashes, or "..") -- so no path
  traversal is possible. A defensive check confirms the final path stays inside
  the outbox.
- The task body is written to the local packet only. It is never executed and
  (by the caller) never posted to any public channel.
- This module never reads or writes .env, runs a shell, or touches GitHub.
"""

import re
from datetime import datetime
from pathlib import Path

# Repo-relative: discord_bridge/dispatch_writer.py -> parents[1] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
OUTBOX = REPO_ROOT / "orchestrator" / "dispatch_outbox"

TITLE_MAX_LEN = 120
TASK_MAX_LEN = 4000
SLUG_MAX_LEN = 40
PRIORITIES = ("low", "normal", "high")
DEFAULT_PRIORITY = "normal"


class DispatchResult:
    """Outcome of writing a dispatch packet.

    ok=True  -> packet written; see path.
    ok=False -> a write/validation failure; see error. Never raised to the caller.
    """

    def __init__(self, ok, path=None, error=None):
        self.ok = ok
        self.path = path
        self.error = error


def validate_dispatch(title, task):
    """Return (ok, message). Reject empty/whitespace or over-long title/task."""
    if title is None or not title.strip():
        return False, "Empty title -- provide a short dispatch title."
    if len(title) > TITLE_MAX_LEN:
        return False, f"Title too long ({len(title)} chars); max is {TITLE_MAX_LEN}."
    if task is None or not task.strip():
        return False, "Empty task -- provide the task text."
    if len(task) > TASK_MAX_LEN:
        return False, f"Task too long ({len(task)} chars); max is {TASK_MAX_LEN}."
    return True, ""


def normalize_priority(priority):
    """Return a known priority value, defaulting unknown/empty input to normal."""
    if priority and priority.strip().lower() in PRIORITIES:
        return priority.strip().lower()
    return DEFAULT_PRIORITY


def sanitize_title_for_filename(title):
    """Reduce a title to a safe filename slug: [a-z0-9-] only, length-capped.

    This is the single defense that keeps user input out of the path: collapsing
    every non-alphanumeric run to '-' removes dots, slashes, backslashes, and ".."
    so no directory traversal or extension trickery is possible.
    """
    slug = re.sub(r"[^A-Za-z0-9]+", "-", title or "").strip("-").lower()
    slug = slug[:SLUG_MAX_LEN].strip("-")
    return slug or "dispatch"


def build_packet(title, task, priority, operator, created):
    """Build the self-contained Markdown packet text.

    The constraints / required-gates / safety-boundary sections are fixed
    boilerplate so the gates travel with the packet when it is handed to Claude.
    """
    ts = created.isoformat(timespec="seconds")
    return (
        f"# {title.strip()}\n\n"
        f"- **Created:** {ts}\n"
        f"- **Requested by:** {operator}\n"
        f"- **Priority:** {priority}\n"
        "- **Source:** Discord /voltex dispatch\n"
        "- **Status:** Packet created -- NOT executed. Claude runs this only "
        "after the operator explicitly instructs it to use this packet.\n\n"
        "## Task\n\n"
        f"{task.strip()}\n\n"
        "## Constraints\n\n"
        "- Operate only in the project-claude worktree (branch agent/claude).\n"
        "- Keep the change minimal and surgical -- within the stated task only.\n"
        "- ASCII-only source files. No secrets in code or commits.\n"
        "- Do not read or print .env. Do not expose secrets.\n"
        "- Do not add API integrations, autonomous loops, or Discord-triggered "
        "execution.\n\n"
        "## Required gates\n\n"
        "- All work via a pull request to main (protected); no direct pushes.\n"
        "- Codex read-only review + ChatGPT strategic review + operator approval "
        "before merge.\n"
        "- CI must be green (py_compile + smoke tests).\n"
        "- No agent merges its own PR.\n\n"
        "## Explicit safety boundaries\n\n"
        "- This packet is a REQUEST, not an execution. Claude has not run it.\n"
        "- Claude executes only after the operator explicitly instructs it to use "
        "this packet.\n"
        "- No GitHub mutation, merge, push, approval, or issue change results from "
        "this packet alone.\n"
        "- The packet lives in a gitignored local outbox and is never committed.\n"
    )


def write_packet(title, task, priority, operator, created=None):
    """Validate, sanitize, and write the packet. Return a DispatchResult.

    Never raises: validation and filesystem errors are returned as ok=False so the
    caller can report a clean failure instead of crashing.
    """
    ok, message = validate_dispatch(title, task)
    if not ok:
        return DispatchResult(False, error=message)

    priority = normalize_priority(priority)
    if created is None:
        created = datetime.now()

    slug = sanitize_title_for_filename(title)
    filename = f"{created:%Y-%m-%d_%H-%M-%S}_{slug}.md"

    try:
        outbox = OUTBOX.resolve()
        outbox.mkdir(parents=True, exist_ok=True)
        final = (outbox / filename).resolve()
        # Defensive: the sanitized filename cannot escape the outbox, but verify.
        if final.parent != outbox:
            return DispatchResult(False, error="Refused unsafe packet path.")
        final.write_text(build_packet(title, task, priority, operator, created),
                         encoding="utf-8")
    except OSError as exc:
        return DispatchResult(False, error=f"Could not write packet ({exc.__class__.__name__}).")

    return DispatchResult(True, path=str(final))


def to_repo_relative(path):
    """Return path relative to the repo root, or the bare filename as a fallback.

    Used so the public agent-log summary discloses a short repo-relative path
    instead of the host's absolute directory layout. The operator's private reply
    still shows the absolute path.
    """
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except (ValueError, OSError):
        return Path(path).name


def _read_title(path):
    """Read ONLY the packet's title (first heading / first non-empty line).

    Deliberately does not read or return the task body.
    """
    try:
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                s = line.strip()
                if s.startswith("# "):
                    return s[2:].strip()
                if s:
                    return s
    except OSError:
        pass
    return path.stem


def latest_packet():
    """Return (path, title) for the newest dispatch packet, or (None, None).

    Filenames are timestamp-prefixed, so a lexical sort is chronological. Reads
    only the title line of the newest packet -- never the task body. Never raises.
    """
    try:
        if not OUTBOX.is_dir():
            return None, None
        files = sorted(OUTBOX.glob("*.md"))
        if not files:
            return None, None
        newest = files[-1]
        return str(newest), _read_title(newest)
    except OSError:
        return None, None

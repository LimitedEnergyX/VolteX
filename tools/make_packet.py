#!/usr/bin/env python3
"""Generate a structured review packet for agent or human review.

Usage:
    python tools/make_packet.py
    python tools/make_packet.py --out packet.md

Each field is collected interactively. Type content freely -- blank lines are
allowed inside a field. Type --- on its own line to advance to the next field.
"""

import argparse
import sys
from pathlib import Path

FIELDS = [
    (
        "Mission",
        "What is being decided or proposed?",
        "",
    ),
    (
        "Current state",
        "What is the current situation, repo state, or context?",
        "",
    ),
    (
        "Constraint",
        "What constraint, limitation, or blocker is relevant? (type None if not applicable)",
        "",
    ),
    (
        "Proposed action",
        "What specific action is proposed?",
        "",
    ),
    (
        "Commands or manual steps",
        "What commands or steps would be executed?",
        "",
    ),
    (
        "Files affected",
        "Which files would be created, modified, or deleted?",
        "",
    ),
    (
        "Risks",
        "What could go wrong?",
        "",
    ),
    (
        "Rollback plan",
        "How is this reversed if something goes wrong?",
        "",
    ),
    (
        "Success criteria",
        "How do we know this worked?",
        "",
    ),
    (
        "Requested reviewer",
        "Who should review this packet? (e.g. ChatGPT, Codex, human)",
        "",
    ),
    (
        "Requested response format",
        "What verdict format should the reviewer use?",
        (
            "Approved / Approved with changes / Do not proceed\n"
            "\n"
            "If not approved, include:\n"
            "- Constraint\n"
            "- Proposed solution\n"
            "- Cost / impact\n"
            "- Timeline\n"
            "- Recommendation"
        ),
    ),
]

TERMINATOR = "---"


def collect_field(number: int, name: str, hint: str, default: str) -> str:
    """Prompt for one field. Returns the entered text, or default if empty."""
    print()
    print(f"[{number}] {name}")
    if hint:
        print(f"    {hint}")
    if default:
        print(f"    Default:")
        for line in default.splitlines():
            print(f"      {line}")
        print(f"    (enter {TERMINATOR} to accept default, or type to override)")
    else:
        print(f"    (enter {TERMINATOR} on its own line when done)")

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.rstrip() == TERMINATOR:
            break
        lines.append(line)

    text = "\n".join(lines).strip()
    return text if text else default


def render_packet(values: list[tuple[str, str]]) -> str:
    """Render collected field values as a formatted Markdown packet."""
    sections = []
    for i, (name, value) in enumerate(values, 1):
        body = value.strip() if value.strip() else "(not provided)"
        sections.append(f"## {i}. {name}\n\n{body}")
    return "\n\n".join(sections) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="make_packet",
        description=(
            "Generate a structured review packet for agent or human review. "
            "Prompts for each field interactively. "
            "Type --- on its own line to advance to the next field. "
            "Blank lines are allowed inside field content."
        ),
    )
    parser.add_argument(
        "--out",
        metavar="PATH",
        help="Write the packet to this file in addition to printing to stdout",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Review Packet Generator")
    print("=" * 60)
    print(f"Fill in each field. Type {TERMINATOR} on its own line to advance.")
    print("Blank lines are allowed inside field content.")

    collected: list[tuple[str, str]] = []
    for i, (name, hint, default) in enumerate(FIELDS, 1):
        value = collect_field(i, name, hint, default)
        collected.append((name, value))

    packet = render_packet(collected)

    print()
    print("=" * 60)
    print("REVIEW PACKET")
    print("=" * 60)
    print()
    print(packet)

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(packet, encoding="utf-8")
        print(f"[written to {out_path}]")

    return 0


if __name__ == "__main__":
    sys.exit(main())

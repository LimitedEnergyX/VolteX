# VolteX -- Consensus Protocol

This document records the design for VolteX's multi-agent consensus process. The
active workflow today is the single-pass orchestrator review bridge (Claude
proposes, Codex reviews via a structured verdict, the user approves, PR-only
merges); the full multi-round loop below is the target direction.

## Purpose

VolteX coordinates AI agents so that work is auditable, reviewable, and
confidence-checked before anything is built. The consensus protocol is how
proposals are reviewed and how decisions reach the user. The current
implementation focuses on software and code review; the same model can extend to
other project types later.

## Roles

- The user: final authority and approval gate.
- Claude: proposes plans, performs local implementation, and operates the workflow.
- Codex: performs local read-only review and returns structured verdicts.
- ChatGPT: provides strategic validation, conflict review, and user-facing
  plain-English decision review.
- Local execution tools (Desktop Commander, Chrome MCP): carry out actions. They
  are tools, not independent decision-makers.

## Consensus Loop

1. Claude proposes an approach.
2. Codex and/or ChatGPT review the approach.
3. Agents may use condensed, high-efficiency technical language in agent-facing
   discussion.
4. User-facing summaries are always plain English.
5. Agent discussion is limited to five rounds unless the user explicitly extends
   it.

## Consensus Criteria

Consensus means the reviewing agents recommend the same primary solution and do
not identify unresolved blocking risks. When consensus is reached, the recommended
solution is presented to the user in plain English for approval.

## No-Consensus Path (RFI)

If consensus is not reached after five rounds, the agents present the user with an
RFI-style decision package:

- Constraint
- Proposed solutions
- Cost
- Impact
- Estimated timeline
- Recommendation (if any)

The user makes the final call. The agents then execute the user's directive
without further debate.

## Human in the Loop

Non-negotiable: no action is taken without the user's explicit approval at each
decision gate.

## Git Workflow

All approved work follows a proper Git workflow:

- branch
- commit
- review
- CI / checks
- merge
- tag or handoff when appropriate

## Operator Interface

A local Discord operator interface is live: the user runs slash commands
(`/voltex status`, `/voltex latest`, `/voltex packet`, `/voltex review`,
`/voltex room-status`), and `/voltex review` can post a plain-English summary to an
optional agent-log channel. See
[../discord_bridge/README.md](../discord_bridge/README.md).

## Implementation Status

The single-pass review bridge and the Discord operator interface are live. The
full multi-round consensus loop and any further automation remain the documented
direction.

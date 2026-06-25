# VolteX -- Consensus Protocol (Direction)

**Status: direction only.** This document records the agreed design for VolteX's
multi-agent consensus process. It is not yet implemented. No orchestrator code,
CI, or agent behavior in this repo implements this protocol today; implementation
is deferred to future PRs. Until then, the active workflow remains the current
orchestrator review bridge (Claude proposes, Codex reviews via a structured
verdict, Shawn approves, PR-only merges).

## Purpose

VolteX coordinates AI coding assistants so that software work is auditable,
reviewable, and confidence-checked before anything is built. The consensus
protocol is how proposals are reviewed and how decisions reach Shawn.

## Roles

- Shawn: final authority and approval gate.
- Claude: proposes plans, performs local implementation, and operates the
  workflow.
- Codex: performs local read-only review and returns structured verdicts.
- ChatGPT: provides strategic validation, conflict review, and Shawn-facing
  plain-English decision review.
- Desktop Commander and Chrome MCP: execution tools on Jarvis (write code,
  navigate GitHub, fill forms, manage the local environment). They are tools, not
  independent decision-makers.

## Consensus Loop (planned)

1. Claude proposes an approach.
2. Codex and/or ChatGPT review the approach.
3. Agents may use condensed, high-efficiency technical language in agent-facing
   discussion.
4. Shawn-facing summaries are always plain English.
5. Agent discussion is limited to five rounds unless Shawn explicitly extends it.

## Consensus Criteria

Consensus means the reviewing agents recommend the same primary solution and do
not identify unresolved blocking risks. When consensus is reached, the
recommended solution is presented to Shawn in plain English for approval.

## No-Consensus Path

If consensus is not reached after five rounds, the agents present a structured
decision package:

- Constraint
- Proposed solutions
- Cost
- Impact
- Estimated timeline
- Recommendation (if any)

Shawn makes the final call. Both agents execute Shawn's directive without further
debate.

## Human in the Loop

Non-negotiable: no action is taken without Shawn's explicit approval at each
decision gate.

## Git Workflow

All approved work follows a proper Git workflow:

- branch
- commit
- review
- CI / checks
- merge
- tag or handoff when appropriate

## Planned Operator Interface

Discord, running locally on Jarvis, is the planned operator interface:

- one channel for agent consensus traffic
- one channel for Shawn-facing plain-English decisions and approvals

Discord is not implemented in this PR and is deferred to a future PR.

## Implementation Status

Everything in this document is direction, not current behavior. Discord,
multi-round consensus automation, and any orchestrator, CI, or agent-behavior
changes needed to implement this protocol are deferred to future PRs.

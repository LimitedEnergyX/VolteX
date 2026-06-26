# VolteX -- Project Brief

## What is VolteX?

VolteX is a general-purpose multi-agent AI consensus platform. AI agents
collaborate and cross-check each other's work through a structured, user-approved
consensus process, so the user can review recommendations and approve next steps
with confidence. The current implementation focuses on software and code review;
the same consensus model can extend to other project types later.

See [SCOPE.md](SCOPE.md) for the canonical scope definition and
[CONSENSUS_PROTOCOL.md](CONSENSUS_PROTOCOL.md) for the consensus process.

The name combines Volt (energy, live current) and -ex (platform suffix). It
denotes the consensus platform itself.

## Problem

Coordinating multiple AI agents by hand is error-prone: work is hard to review,
decisions are not auditable, and there is no safe, repeatable handoff between the
agents and the user. There is no single control plane that enforces review, builds
consensus, and keeps a durable record.

## Solution

VolteX provides that control plane. The agents propose and review in a bounded
consensus loop. A recommended solution -- or, if the agents cannot agree, an
RFI-style decision package (constraints, options, cost, impact, timeline) -- is
presented to the user in plain English. Nothing proceeds without the user's
approval. Approved work follows a proper Git workflow (branch, commit, review, CI,
merge, tag/handoff).

## Current Phase

**In scope now:**
- VolteX defined as the general-purpose multi-agent AI consensus platform
- Orchestrator dispatch and the Claude-to-Codex structured review bridge
- The local Discord operator interface
- CI gate, approval gates, transcripts, handoffs, restore tags

**Direction (documented, not yet implemented):**
- The full multi-round agent consensus loop
- Extending the consensus model to non-software project types

## Stakeholders

- Maintainer: Shawn C. Tovey, RCDD / LimitedEnergyX
- Agents: Claude (operator/implementer), Codex (reviewer), ChatGPT (strategic reviewer)
- The user: reviews recommendations and approves decisions

## Success Criteria

- VolteX reads as a general-purpose platform any user can use
- The multi-agent workflow remains safe, reviewable, and repeatable
- Every change is gated by review and the user's explicit approval

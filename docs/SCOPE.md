# VolteX -- Scope Definition

This is the canonical definition of what VolteX is and is not. The other docs
(README, PROJECT_BRIEF, ARCHITECTURE, AGENTS) summarize this file and link here.

## What VolteX Is

VolteX is the coding-assistant coordination platform, not the downstream
application being built.

It is Shawn's control plane for coordinating AI coding assistants and the
infrastructure around them:

- Operators and reviewers: Claude (operator/implementer), Codex (worker),
  ChatGPT (reviewer/strategist), with Shawn as the sole human authority.
- Source of truth: GitHub (branches, pull requests, issues).
- Quality gate: CI on every pull request.
- Auditable record: review transcripts and structured verdicts.
- Continuity: session handoffs and restore tags.
- Safety: approval gates and PR-only merges to main.

VolteX's job is to make multi-agent software work safe, reviewable, and
repeatable. It coordinates the assistants; it is not the product they build.

## What VolteX Is Not

- VolteX is not the Revit tool.
- VolteX is not a Revit or BIM integration product.
- VolteX does not itself implement downstream applications.

VolteX may later help build or refine those downstream projects, but they are
separate efforts with their own scope.

## Downstream Projects

Separate projects that VolteX may help coordinate, refine, or build. They are
not VolteX itself:

- PLEX: existing tool VolteX may help refine.
- Purple Rainmaker: existing project VolteX may help maintain or improve.
- Revit tool: future downstream project VolteX may help build.

## Current Scope

In scope now:
- The multi-agent coordination workflow (orchestrator dispatch, review bridge,
  structured verdicts, transcripts, handoffs, restore tags, CI gate, approval
  gates).
- Documentation that keeps this scope accurate.

Deferred / not active scope:
- The Revit tool and any Revit/BIM integration work. It is deferred downstream
  work (tracked under GitHub Issue #4), not a current build target.
- Discord, voice, and any agent-feature expansion beyond the proven workflow.

## Why the Name Stays

VolteX keeps its name. The name now denotes the coordination platform itself,
not a Revit or BIM product. Earlier docs framed VolteX around Revit and BIM;
that framing is superseded by this file.

# VolteX

VolteX is the coding-assistant coordination platform, not the downstream
application being built. It is Shawn's control plane for coordinating AI coding
assistants (Claude, Codex, ChatGPT) through GitHub, CI, review transcripts,
handoffs, restore tags, and approval gates.

See [docs/SCOPE.md](docs/SCOPE.md) for the canonical scope definition.

## Status

Active. The multi-agent coordination workflow is built and in use: orchestrator
dispatch, Claude-to-Codex review bridge, structured verdicts, review
transcripts, manual review packets, CI gate, and restore tags.

Revit is deferred. VolteX is not the Revit tool -- see Downstream Projects.

## Structure

```
+- docs/            Scope, project brief, and architecture
+- orchestrator/    Multi-agent orchestration layer
+- AGENTS.md        Rules for AI agent collaboration
+- README.md
```

## Agent Workflow

Claude and Codex collaborate on this repo using isolated git worktrees and a
strict PR-only handoff model. See [AGENTS.md](AGENTS.md) for rules and
invocation commands.

## Downstream Projects

Separate projects VolteX may help coordinate, refine, or build -- not VolteX
itself:

- PLEX: existing tool VolteX may help refine.
- Purple Rainmaker: existing project VolteX may help maintain or improve.
- Revit tool: future downstream project VolteX may help build.

# VolteX — Project Brief

## What is VolteX?

VolteX is a live Revit integration platform. In spirit it is similar to Plex — a clean, modern
interface for accessing and interacting with content in real time — but aimed at Revit models
and BIM workflows.

The name combines *Volt* (energy, live current) and *-ex* (platform suffix), signaling a
real-time, powered connection to your Revit environment.

## Problem

Revit data is largely locked inside desktop sessions. Teams have no lightweight way to:
- View live model state without opening Revit
- Stream model data to dashboards or other tools
- Collaborate across the model in real time

## Solution (Vision)

VolteX provides a live bridge to open Revit models, exposing model data as a stream that
other tools, dashboards, and collaborators can subscribe to.

## Current Phase

Architecture and agent workflow foundation.

**In scope now:**
- Repository structure and documentation
- Multi-agent development workflow (Claude + Codex)
- Proving the headless CLI agent bridge
- Defining the architecture before writing application code

**Out of scope now:**
- Revit plugin development
- UI / frontend
- Authentication / user management
- Discord integration (planned later as command/status layer only)

## Stakeholders

- Owner: Shawn Tovey / LimitedEnergyX
- Agents: Claude (orchestrator), Codex (reviewer/strategist)

## Success Criteria — Phase 0

- [ ] Repo scaffolded with README, AGENTS.md, architecture docs
- [ ] Git worktrees created for both agents
- [ ] Both CLIs confirmed working in headless mode
- [ ] Branch protection on `main` enabled
- [ ] No application code written yet

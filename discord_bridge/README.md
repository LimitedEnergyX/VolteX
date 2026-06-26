# VolteX Discord Operator Interface (MVP)

A local Discord bot that lets the operator query VolteX and trigger one review over slash
commands. It is an **interface, not an authority**: no GitHub mutation, no merges,
no approvals. `/voltex review` runs exactly one Codex **read-only** review through
the existing orchestrator bridge; all other commands are read-only / template-only.

## Scope

- `/voltex status` -- current `main` commit, latest restore tag, worktree status
  summary, and whether the review bridge (codex CLI) is available. Read-only.
- `/voltex latest` -- newest review transcript path, executive summary, and
  verdict if present. Read-only.
- `/voltex packet` -- displays the canonical review-packet template to copy and
  fill in. Template-only (creates no files).
- `/voltex review <packet>` -- runs **one** Codex read-only review of the inline
  packet text through the existing `orchestrator review` bridge, then returns the
  verdict and transcript path. Inline text only (no file paths, no attachments).
  One review at a time -- a concurrent `/voltex review` is rejected, not queued.
  The reply clearly separates a review verdict from a bot/process failure. If the
  agent-log channel is configured (see below), it also posts a public summary
  there; pass `post_to_log:false` to keep a review private.
- `/voltex room-status` -- shows bot connection, the operator channel, whether the
  agent-log channel is configured, and review-bridge availability. Read-only.
- `/voltex dispatch <title> <task> [priority] [post_to_log]` -- writes a structured
  Claude task packet to the local gitignored outbox `orchestrator/dispatch_outbox/`
  and (by default) posts a safe summary to the agent-log channel. It does **not**
  execute anything: Claude runs the task later, manually, only after the operator
  explicitly instructs it. The public summary never includes the task body.
- `/voltex dispatch-latest` -- shows the newest dispatch packet's path and title.
  Read-only; does not print the task body.

## Agent room (optional)

Set `VOLTEX_AGENT_LOG_CHANNEL_ID` (the numeric ID of `#voltex-agent-log`) to turn
the server into a shared agent room: after each `/voltex review`, VolteX posts a
plain-English summary (timestamp, command, verdict, recommendation, transcript
path, and a read-only reminder) to that channel, while the operator still gets the
private ephemeral reply.

This is optional and safe:
- If `VOLTEX_AGENT_LOG_CHANNEL_ID` is unset or invalid, public logging is skipped
  and every command works exactly as before.
- If the bot cannot post there (channel missing or no permission), it reports that
  in the operator's private reply and does **not** crash.

## Dispatch workflow (controlled Claude dispatch)

`/voltex dispatch` is a one-way bridge from a Discord request to a local Claude task
packet -- never to automatic execution:

```
Discord /voltex dispatch  ->  local packet in orchestrator/dispatch_outbox/
                          ->  safe public summary in the agent-log channel
                          ->  (manual) Claude executes only after the operator says so
                          ->  normal Codex / ChatGPT review + PR gate
```

- The packet is a timestamped Markdown file `YYYY-MM-DD_HH-MM-SS_<sanitized-title>.md`
  containing the title, created timestamp, requester, priority, source, the task,
  and fixed constraints / required gates / safety boundaries.
- The outbox `orchestrator/dispatch_outbox/` is gitignored; packets are never committed.
- The bot validates and length-limits the title and task, sanitizes the filename to
  `[a-z0-9-]`, accepts no file paths or attachments, and reads no local files.
- The public agent-log summary includes the title, priority, packet path, and a
  "packet created, not executed" status -- never the task body. Mentions are disabled.
- Claude does nothing automatically. The operator must explicitly tell Claude to use
  a packet; it then runs through the normal Codex / ChatGPT / operator review and PR
  gate.

## Requirements

- Python 3.9+
- `discord.py` 2.x

```
pip install -r discord_bridge/requirements.txt
```

## Setup

1. Create an application and bot in the Discord Developer Portal and copy the
   bot token. Invite the bot to your private server. No privileged intents are
   needed -- the bot uses slash commands only.
2. Enable Developer Mode in Discord, then right-click your server, your user,
   and the operator channel to copy each numeric ID.
3. Copy `.env.example` to `.env` in this folder and fill in:
   - `DISCORD_BOT_TOKEN`
   - `VOLTEX_GUILD_ID`
   - `VOLTEX_ALLOWED_USER_ID`
   - `VOLTEX_ALLOWED_CHANNEL_ID`
   - (optional) `VOLTEX_AGENT_LOG_CHANNEL_ID` -- the agent-room log channel (see above)

   `.env` is gitignored and must never be committed.
4. Run the bot:

```
python discord_bridge/bot.py
```

   For repeatable start/stop/restart that prevents duplicate bot processes, use the
   lifecycle script: `pwsh scripts\voltex_bot.ps1 -Action status|start|stop|restart`
   (see [../scripts/README.md](../scripts/README.md)).

## Safety

- Slash commands only. Minimal intents. No message-content intent.
- Guild-scoped command registration (no global commands).
- Fail closed: the bot refuses to start if the token or any ID is missing or
  invalid.
- Every command checks guild ID, user ID, and channel ID; unauthorized requests
  are rejected with a clear message.
- No arbitrary shell, no Codex execution, no orchestrator review call, no GitHub
  mutation, no approvals. The `/voltex status` git lookups are fixed, read-only
  commands with no Discord-supplied arguments.

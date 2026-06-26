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

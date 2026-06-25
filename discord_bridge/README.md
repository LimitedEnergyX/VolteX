# VolteX Discord Operator Interface (MVP)

A local Discord bot that lets Shawn query VolteX over slash commands. It is an
**interface, not an authority**: read-only / template-only, with no Codex
execution, no GitHub mutation, and no approvals.

## Scope (PR #10)

- `/voltex status` -- current `main` commit, latest restore tag, worktree status
  summary, and whether the review bridge (codex CLI) is available. Read-only.
- `/voltex latest` -- newest review transcript path, executive summary, and
  verdict if present. Read-only.
- `/voltex packet` -- displays the canonical review-packet template to copy and
  fill in. Template-only (creates no files).

`/voltex review` (running a Codex review from Discord) is intentionally NOT in
this MVP; it is planned for PR #11.

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

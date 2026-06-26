# VolteX Operations Scripts

Local Windows PowerShell scripts for operating VolteX. They manage processes and
local state only -- they do not change bot behavior, the token, orchestrator code,
or Codex permissions, and they never read or print `.env`.

## voltex_bot.ps1 -- bot lifecycle control

Safely start, stop, restart, and inspect the local VolteX Discord bot, ensuring
exactly one canonical bot runs and no duplicate Python bot processes accumulate on
the same token. Duplicates cause Discord 10062 "Unknown interaction" races (two
bots receive the same slash command and race to acknowledge it).

```
pwsh scripts\voltex_bot.ps1 -Action status
pwsh scripts\voltex_bot.ps1 -Action stop
pwsh scripts\voltex_bot.ps1 -Action start          # refuses if a bot already runs
pwsh scripts\voltex_bot.ps1 -Action start -Force
pwsh scripts\voltex_bot.ps1 -Action restart        # stop all -> confirm 0 -> start 1
```

- **status** -- bot process count, PID, command line, and worktree
  (project-main / project-claude / project-chatgpt / other).
- **stop** -- terminates the actual Python bot process(es), not just a launcher
  shell, and confirms none remain.
- **start** -- starts one canonical bot from `project-main`; refuses if a VolteX
  bot is already running unless `-Force` is given.
- **restart** -- stops all VolteX bots, confirms zero remain, starts exactly one
  from `project-main`, and confirms exactly one remains.

It matches **only** VolteX bot command lines (a Python process under
`D:\AI-Agents\VolteX` running `discord_bridge\bot.py`); unrelated Python processes
are never touched. Paths are configurable at the top of the script and default to
the canonical layout. No admin privileges are required.

## Operating rule

- The **production bot runs from `project-main`** (canonical merged code).
- **PR testing** may temporarily run a bot from `project-claude` -- but only after
  stopping the production bot, and you must return to a single `project-main` bot
  afterward.
- **Always verify exactly one bot process after a restart** (`-Action status`).
- Stop the bot by its **Python process** (this script does that). Killing only a
  launcher/shell session can leave an orphaned bot running on the token.

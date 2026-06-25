#!/usr/bin/env python3
"""VolteX Discord operator interface (MVP).

Slash commands only. Minimal intents. No message-content intent. Guild-scoped
command sync. The bot is read-only / template-only: it does NOT run Codex, call
orchestrator review, mutate GitHub, or execute approvals.

Fail closed: the bot refuses to start unless DISCORD_BOT_TOKEN, VOLTEX_GUILD_ID,
VOLTEX_ALLOWED_USER_ID, and VOLTEX_ALLOWED_CHANNEL_ID are all set and valid.
Every command checks guild ID, user ID, and channel ID before doing anything.

See discord_bridge/README.md for setup. Commands: /voltex status, /voltex latest,
/voltex packet. (/voltex review is intentionally deferred to PR #11.)
"""

import os
import sys
from pathlib import Path

import discord
from discord import app_commands

import report

# Populated by main() at runtime (not at import) so the module stays importable
# and compilable without configuration present.
CONFIG = {}
GUILD = None


def _load_dotenv():
    """Minimal stdlib .env loader for the local discord_bridge/.env file.

    Sets os.environ from KEY=value lines. Does not overwrite existing
    environment variables. No third-party dependency. The .env file is
    gitignored and must never be committed.
    """
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _load_config():
    """Load and validate required config. Fail closed (exit 1) if anything is
    missing or not a valid integer ID."""
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    guild_id = os.environ.get("VOLTEX_GUILD_ID", "").strip()
    user_id = os.environ.get("VOLTEX_ALLOWED_USER_ID", "").strip()
    channel_id = os.environ.get("VOLTEX_ALLOWED_CHANNEL_ID", "").strip()

    missing = [
        name
        for name, val in (
            ("DISCORD_BOT_TOKEN", token),
            ("VOLTEX_GUILD_ID", guild_id),
            ("VOLTEX_ALLOWED_USER_ID", user_id),
            ("VOLTEX_ALLOWED_CHANNEL_ID", channel_id),
        )
        if not val
    ]
    if missing:
        print(
            "FAIL CLOSED: missing required config: "
            + ", ".join(missing)
            + ".\nSet them in discord_bridge/.env (see .env.example). "
            "The bot will not start.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        return {
            "token": token,
            "guild_id": int(guild_id),
            "user_id": int(user_id),
            "channel_id": int(channel_id),
        }
    except ValueError:
        print(
            "FAIL CLOSED: VOLTEX_GUILD_ID, VOLTEX_ALLOWED_USER_ID, and "
            "VOLTEX_ALLOWED_CHANNEL_ID must be integers. The bot will not start.",
            file=sys.stderr,
        )
        sys.exit(1)


class VolteXClient(discord.Client):
    def __init__(self):
        # Minimal intents -- no message-content, no privileged intents.
        intents = discord.Intents.none()
        intents.guilds = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Guild-scoped sync: instant registration, scoped to the one server.
        if GUILD is not None:
            self.tree.copy_global_to(guild=GUILD)
            await self.tree.sync(guild=GUILD)


def _authorized(interaction):
    """True only if guild, user, and channel all match the allowlist.

    guild_id is checked for None first so a DM-context interaction (guild_id is
    None) can never satisfy the allowlist via a None == None comparison. CONFIG
    is read by subscript, so an unpopulated config raises rather than silently
    yielding None.
    """
    return (
        interaction.guild_id is not None
        and interaction.guild_id == CONFIG["guild_id"]
        and interaction.user.id == CONFIG["user_id"]
        and interaction.channel_id == CONFIG["channel_id"]
    )


async def _reject(interaction):
    await interaction.response.send_message(
        "Unauthorized: this command is restricted to the configured operator "
        "and channel.",
        ephemeral=True,
    )


voltex = app_commands.Group(name="voltex", description="VolteX operator interface")


@voltex.command(
    name="status",
    description="Repo status, latest restore tag, and review-bridge availability",
)
async def status(interaction):
    if not _authorized(interaction):
        await _reject(interaction)
        return
    s = report.gather_status()
    msg = (
        "**VolteX status**\n"
        f"- main commit: `{s['main_commit']}`\n"
        f"- latest restore tag: `{s['latest_tag']}`\n"
        f"- review bridge: {s['review_bridge']}\n"
        f"- worktree:\n```\n{s['worktree_status']}\n```"
    )
    await interaction.response.send_message(msg, ephemeral=True)


@voltex.command(
    name="latest",
    description="Latest review transcript path, executive summary, and verdict",
)
async def latest(interaction):
    if not _authorized(interaction):
        await _reject(interaction)
        return
    path, summary, verdict = report.latest_transcript()
    if path is None:
        await interaction.response.send_message(
            "No review transcript found yet.", ephemeral=True
        )
        return
    msg = f"**Latest review transcript**\n- path: `{path}`\n"
    if verdict:
        msg += f"- verdict: {verdict}\n"
    if summary:
        snippet = summary if len(summary) <= 1500 else summary[:1500] + " ..."
        msg += f"\n{snippet}"
    await interaction.response.send_message(msg, ephemeral=True)


@voltex.command(
    name="packet",
    description="Display the canonical review-packet template (template-only)",
)
async def packet(interaction):
    if not _authorized(interaction):
        await _reject(interaction)
        return
    template = report.packet_template()
    await interaction.response.send_message(
        "**Review packet template** -- copy, fill in, and submit for review:\n"
        f"```\n{template}\n```",
        ephemeral=True,
    )


def main():
    global CONFIG, GUILD
    _load_dotenv()
    CONFIG = _load_config()
    GUILD = discord.Object(id=CONFIG["guild_id"])
    client = VolteXClient()
    client.tree.add_command(voltex)
    client.run(CONFIG["token"])


if __name__ == "__main__":
    main()

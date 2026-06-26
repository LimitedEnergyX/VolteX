#!/usr/bin/env python3
"""VolteX Discord operator interface (MVP).

Slash commands only. Minimal intents. No message-content intent. Guild-scoped
command sync. The bot does not mutate GitHub or execute approvals. /voltex review
runs exactly one Codex read-only review through the existing orchestrator review
bridge (reused unchanged); all other commands are read-only / template-only.

Fail closed: the bot refuses to start unless DISCORD_BOT_TOKEN, VOLTEX_GUILD_ID,
VOLTEX_ALLOWED_USER_ID, and VOLTEX_ALLOWED_CHANNEL_ID are all set and valid.
Every command checks guild ID, user ID, and channel ID before doing anything.

An optional VOLTEX_AGENT_LOG_CHANNEL_ID enables posting a plain-English review
summary to the agent-log channel; if it is unset or invalid, public logging is
simply skipped and the commands work unchanged.

See discord_bridge/README.md for setup. Commands: /voltex status, /voltex latest,
/voltex packet, /voltex review, /voltex room-status.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import discord
from discord import app_commands

import report
import review_runner

# Populated by main() at runtime (not at import) so the module stays importable
# and compilable without configuration present.
CONFIG = {}
GUILD = None

# Hard single-review lock: True while a /voltex review runs. It is checked and
# set with no await in between, so on the single-threaded event loop a concurrent
# /voltex review is rejected (never queued).
_review_in_flight = False


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
        cfg = {
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

    # Optional agent-room log channel. Unset or invalid -> None; public logging is
    # simply skipped and the bot never fails because of this value.
    agent_log = os.environ.get("VOLTEX_AGENT_LOG_CHANNEL_ID", "").strip()
    try:
        cfg["agent_log_channel_id"] = int(agent_log) if agent_log else None
    except ValueError:
        cfg["agent_log_channel_id"] = None
    return cfg


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


def _format_result(result):
    """Format a ReviewResult for Discord, clearly separating a review verdict
    from a bot/process failure."""
    if result.ok:
        lines = [f"**Review verdict:** {result.verdict}"]
        if result.recommendation:
            lines.append(f"**Recommendation:** {result.recommendation}")
        if result.transcript:
            lines.append(f"**Transcript:** `{result.transcript}`")
        lines.append("Use `/voltex latest` for the latest transcript.")
    else:
        lines = [
            "**Bot/process failure** (this is NOT a review verdict).",
            f"- {result.error}",
        ]
        if result.detail:
            lines.append(f"- detail: {result.detail}")
        lines.append("Use `/voltex latest` for the latest transcript if one exists.")
    msg = "\n".join(lines)
    return msg if len(msg) <= 1900 else msg[:1900] + " ..."


def _format_log_summary(result):
    """Plain-English review summary for the public agent-log channel.

    Public-channel safety: include ONLY timestamp, command name, verdict,
    recommendation, transcript path, and the read-only reminder. NEVER include the
    review packet text or raw stdout/stderr -- result.error/result.detail are
    deliberately not used, and public logging only runs for a real verdict
    (result.ok), so failure output never reaches the channel.
    """
    ts = datetime.now().isoformat(timespec="seconds")
    lines = [
        "**VolteX review**",
        f"- time: {ts}",
        "- command: /voltex review",
        f"- verdict: {result.verdict}",
    ]
    if result.recommendation:
        lines.append(f"- recommendation: {result.recommendation}")
    if result.transcript:
        lines.append(f"- transcript: `{result.transcript}`")
    lines.append("- Codex ran read-only.")
    msg = "\n".join(lines)
    return msg if len(msg) <= 1900 else msg[:1900] + " ..."


async def _post_review_to_log(client, summary):
    """Post a summary to the agent-log channel. Returns a short status string and
    never raises -- failures are reported, not crashed. Public logging is skipped
    entirely when the channel is not configured."""
    chan_id = CONFIG.get("agent_log_channel_id")
    if not chan_id:
        return "channel not configured"
    channel = client.get_channel(chan_id)
    if channel is None:
        try:
            channel = await client.fetch_channel(chan_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return "channel not found or not accessible"
    if not isinstance(channel, discord.abc.Messageable):
        return "configured channel is not a text channel"
    try:
        await channel.send(summary)
        return "posted"
    except discord.Forbidden:
        return "missing permission to post there"
    except discord.HTTPException as exc:
        return f"post failed ({exc.__class__.__name__})"


@voltex.command(
    name="review",
    description="Run one Codex read-only review of an inline packet (one at a time)",
)
@app_commands.describe(
    packet="The review packet text (inline only -- no files or attachments)",
    post_to_log="Also post a summary to the agent-log channel if configured (default: yes)",
)
async def review(interaction, packet: str, post_to_log: bool = True):
    global _review_in_flight
    if not _authorized(interaction):
        await _reject(interaction)
        return
    ok, message = review_runner.validate_packet(packet)
    if not ok:
        await interaction.response.send_message(message, ephemeral=True)
        return
    # Reject (never queue) a concurrent review. The flag is set before any await,
    # so two near-simultaneous invocations cannot both pass this gate.
    if _review_in_flight:
        await interaction.response.send_message(
            "A review is already running; please wait for it to finish.",
            ephemeral=True,
        )
        return
    _review_in_flight = True
    try:
        await interaction.response.defer(ephemeral=True)
        result = await review_runner.run_review(packet)
        await interaction.followup.send(_format_result(result), ephemeral=True)
        # Optional agent-room logging: additive, never blocks the private reply.
        if post_to_log and result.ok:
            status = await _post_review_to_log(
                interaction.client, _format_log_summary(result)
            )
            if status != "posted":
                await interaction.followup.send(
                    f"(agent-log not updated: {status})", ephemeral=True
                )
    finally:
        _review_in_flight = False


@voltex.command(
    name="room-status",
    description="Agent-room status: bot connection, channels, and review bridge",
)
async def room_status(interaction):
    if not _authorized(interaction):
        await _reject(interaction)
        return
    agent_log = CONFIG.get("agent_log_channel_id")
    bridge = "available" if report.review_bridge_available() else "unavailable"
    lines = [
        "**VolteX room status**",
        f"- bot: connected as {interaction.client.user}",
        f"- operator channel: configured (<#{CONFIG['channel_id']}>)",
        "- agent-log channel: "
        + (f"configured (<#{agent_log}>)" if agent_log else "not configured"),
        f"- review bridge: {bridge}",
    ]
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


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

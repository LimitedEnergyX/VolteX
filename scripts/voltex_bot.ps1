<#
.SYNOPSIS
  VolteX bot lifecycle control: status, start, stop, restart.

.DESCRIPTION
  Safely manages the local VolteX Discord bot (discord_bridge/bot.py) so that
  exactly one canonical bot runs from project-main and duplicate Python bot
  processes never accumulate on the same token. Duplicate instances on one token
  caused Discord 10062 "Unknown interaction" races during earlier testing, because
  multiple bots received the same slash command and raced to acknowledge it.

  This script matches ONLY VolteX bot processes by command line (under the VolteX
  root and running discord_bridge\bot.py). It never touches unrelated Python
  processes. It does not read or print .env, change the token, or change bot
  behavior -- it only manages the bot process.

.PARAMETER Action
  status  -- list VolteX bot processes (count, PID, command line, worktree).
  start   -- start one canonical bot from project-main; refuses if a VolteX bot is
             already running unless -Force is given.
  stop    -- terminate all VolteX bot Python processes; confirm none remain.
  restart -- stop all, confirm none remain, start one from project-main, confirm
             exactly one remains.

.PARAMETER Force
  With -Action start, start even if a VolteX bot is already running. This does NOT
  stop the existing one; use -Action restart for a clean single-instance restart.

.EXAMPLE
  pwsh scripts\voltex_bot.ps1 -Action status
  pwsh scripts\voltex_bot.ps1 -Action restart
#>

[CmdletBinding()]
param(
    [ValidateSet('status', 'start', 'stop', 'restart')]
    [string]$Action = 'status',
    [switch]$Force
)

# --- Configuration (defaults to the canonical local layout) -----------------
$VolteXRoot        = 'D:\AI-Agents\VolteX'
$CanonicalWorktree = Join-Path $VolteXRoot 'project-main'
$CanonicalBot      = Join-Path $CanonicalWorktree 'discord_bridge\bot.py'
$PythonExe         = 'python'

# A VolteX bot is a python process whose command line is under the VolteX root
# AND runs the contiguous script path ...\discord_bridge\bot.py. Requiring the
# contiguous tail (no wildcard gap between discord_bridge and bot.py) avoids
# matching an unrelated python process that merely mentions the root and the
# string "bot.py" in separate arguments.
$RootMatch     = '*' + $VolteXRoot + '*'
$BotScriptTail = '*\discord_bridge\bot.py*'


function Get-VolteXBot {
    # Return VolteX bot processes with PID, detected worktree, and command line.
    # Slashes are normalized to backslash before matching so a forward-slash
    # launch (python D:/AI-Agents/VolteX/.../bot.py) is still detected.
    $procs = Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -and
            (($_.CommandLine -replace '/', '\') -like $RootMatch) -and
            (($_.CommandLine -replace '/', '\') -like $BotScriptTail)
        }
    foreach ($p in $procs) {
        $norm = $p.CommandLine -replace '/', '\'
        $worktree = 'other'
        if ($norm -like '*\project-main\*')        { $worktree = 'project-main' }
        elseif ($norm -like '*\project-claude\*')  { $worktree = 'project-claude' }
        elseif ($norm -like '*\project-chatgpt\*') { $worktree = 'project-chatgpt' }
        [pscustomobject]@{
            ProcessId = $p.ProcessId
            Worktree  = $worktree
            Command   = ($p.CommandLine -replace '\s+', ' ').Trim()
        }
    }
}


function Show-VolteXStatus {
    $bots = @(Get-VolteXBot)
    Write-Host ("VolteX bot processes: {0}" -f $bots.Count)
    foreach ($b in $bots) {
        Write-Host ("  PID {0}  [{1}]  {2}" -f $b.ProcessId, $b.Worktree, $b.Command)
    }
}


function Stop-VolteXBot {
    $bots = @(Get-VolteXBot)
    if ($bots.Count -eq 0) {
        Write-Host 'No VolteX bot processes running.'
        return
    }
    foreach ($b in $bots) {
        try {
            Stop-Process -Id $b.ProcessId -Force -ErrorAction Stop
            Write-Host ("Stopped PID {0} [{1}]." -f $b.ProcessId, $b.Worktree)
        } catch {
            Write-Host ("Could not stop PID {0}: {1}" -f $b.ProcessId, $_.Exception.Message)
        }
    }
    # Poll until the OS reaps the killed process(es), up to ~3s, so "confirm
    # zero" is reliable on a busy box instead of depending on a fixed sleep.
    $remaining = @(Get-VolteXBot)
    $waitedMs = 0
    while ($remaining.Count -gt 0 -and $waitedMs -lt 3000) {
        Start-Sleep -Milliseconds 300
        $waitedMs += 300
        $remaining = @(Get-VolteXBot)
    }
    if ($remaining.Count -eq 0) {
        Write-Host 'Confirmed: no VolteX bot processes remain.'
    } else {
        Write-Host ("WARNING: {0} VolteX bot process(es) still running." -f $remaining.Count)
    }
}


function Start-VolteXBot {
    if (-not (Test-Path -LiteralPath $CanonicalBot)) {
        Write-Host ("ERROR: canonical bot not found: {0}" -f $CanonicalBot)
        return
    }
    # The bot loads its own config from discord_bridge/.env; this script never
    # reads .env. The bot runs hidden and detached so it persists after this
    # script (and the terminal) exits.
    $proc = Start-Process -FilePath $PythonExe `
        -ArgumentList @("`"$CanonicalBot`"") `
        -WorkingDirectory $CanonicalWorktree `
        -WindowStyle Hidden -PassThru
    Write-Host ("Started VolteX bot from project-main (PID {0})." -f $proc.Id)
    Write-Host '(Hidden process. If a start fails closed -- missing config -- run the bot directly to see why.)'
    Start-Sleep -Seconds 3
}


switch ($Action) {
    'status' {
        Show-VolteXStatus
    }
    'stop' {
        Stop-VolteXBot
    }
    'start' {
        $running = @(Get-VolteXBot)
        if ($running.Count -gt 0 -and -not $Force) {
            Write-Host ("Refusing to start: {0} VolteX bot process(es) already running (PID {1})." -f `
                $running.Count, ($running.ProcessId -join ', '))
            Write-Host 'Use -Action restart for a clean single-instance restart, or -Force to start anyway.'
            break
        }
        Start-VolteXBot
        Show-VolteXStatus
    }
    'restart' {
        Write-Host '== Stopping all VolteX bots =='
        Stop-VolteXBot
        $remaining = @(Get-VolteXBot)
        if ($remaining.Count -ne 0) {
            Write-Host 'ERROR: bots still running after stop; aborting restart to avoid duplicates.'
            break
        }
        Write-Host '== Starting one canonical bot from project-main =='
        Start-VolteXBot
        $after = @(Get-VolteXBot)
        Show-VolteXStatus
        if ($after.Count -eq 1 -and $after[0].Worktree -eq 'project-main') {
            Write-Host 'Restart OK: exactly one bot running from project-main.'
        } else {
            Write-Host ("WARNING: expected exactly one bot from project-main; found {0}." -f $after.Count)
        }
    }
}

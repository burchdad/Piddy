#!/usr/bin/env python3
"""
piddy — Unified CLI for Piddy AI Assistant

Usage:
    python piddy.py start          Start all services (background)
    python piddy.py start --fg     Start in foreground (debug)
    python piddy.py stop           Stop all running services
    python piddy.py status         Show system status
    python piddy.py doctor         Run self-diagnosis
    python piddy.py config         Open settings / show config
    python piddy.py export         Export all data to JSON
    python piddy.py agents         List registered agents
    python piddy.py skills         List loaded skills
    python piddy.py desktop        Launch Electron desktop app
"""

import argparse
import json
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def cmd_start(args):
    """Start Piddy services."""
    script = PROJECT_ROOT / "start_piddy.py"
    flags = []
    if args.foreground:
        flags.append("--foreground")
    if args.dashboard_only:
        flags.append("--dashboard-only")
    if args.desktop:
        flags.append("--desktop")
    os.execv(sys.executable, [sys.executable, str(script)] + flags)


def cmd_stop(_args):
    """Stop running services."""
    pid_file = PROJECT_ROOT / "data" / "piddy.pid"
    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        try:
            os.kill(pid, 0)  # check if alive
            os.kill(pid, 15)  # SIGTERM (15 works on Windows via TerminateProcess)
            pid_file.unlink()
            print(f"✓ Stopped process {pid}")
        except ProcessLookupError:
            pid_file.unlink()
            print("Service was already stopped.")
        except PermissionError:
            print(f"⚠ Cannot stop process {pid} — permission denied.")
    else:
        print("No running service found.")


def cmd_status(_args):
    """Show system status."""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8889/api/system/overview")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            print(f"Status:      {data.get('status', 'unknown')}")
            print(f"Agents:      {data.get('agents_online', 0)} online")
            print(f"Missions:    {data.get('missions_active', 0)} active")
            print(f"Decisions:   {data.get('decisions_pending', 0)} pending")
            print(f"Approvals:   {data.get('approvals_pending', 0)} pending")
    except Exception:
        print("Piddy is not running. Start with:  python piddy.py start")


def cmd_doctor(_args):
    """Run self-diagnosis."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.api.doctor import run_diagnosis
    report = run_diagnosis()
    print(f"\nPiddy Health — {report['status'].upper()}")
    print(f"Platform: {report.get('platform', 'unknown')}\n")
    for check in report.get("checks", []):
        icon = {"ok": "✅", "warn": "⚠️", "error": "❌", "skip": "⏭️"}.get(check["status"], "?")
        name = check["name"].ljust(25)
        msg = check.get("message") or check.get("version") or ""
        print(f"  {icon} {name} {msg}")
    s = report.get("summary", {})
    print(f"\n  {s.get('ok', 0)} OK · {s.get('warnings', 0)} Warnings · {s.get('errors', 0)} Errors")


def cmd_config(_args):
    """Show current configuration."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from config.settings import get_settings
    s = get_settings()
    print("Piddy Configuration")
    print(f"  local_only:        {s.local_only}")
    print(f"  ollama_enabled:    {s.ollama_enabled}")
    print(f"  ollama_model:      {s.ollama_model}")
    print(f"  ollama_base_url:   {s.ollama_base_url}")
    print(f"  agent_model:       {s.agent_model}")
    print(f"  agent_temperature: {s.agent_temperature}")
    print(f"  agent_max_tokens:  {s.agent_max_tokens}")
    print(f"  log_level:         {s.log_level}")


def cmd_export(_args):
    """Export all data."""
    out_dir = PROJECT_ROOT / "exports"
    out_dir.mkdir(exist_ok=True)
    data_dir = PROJECT_ROOT / "data"
    count = 0
    for f in data_dir.glob("*.json"):
        dest = out_dir / f.name
        dest.write_bytes(f.read_bytes())
        count += 1
    print(f"✓ Exported {count} data files to exports/")


def cmd_agents(_args):
    """List registered agents."""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8889/api/agents")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            agents = data if isinstance(data, list) else data.get("agents", [])
            print(f"Registered Agents: {len(agents)}\n")
            for a in agents:
                name = (a.get("name") or a.get("agent_id", "?")).ljust(25)
                role = a.get("role", "?").ljust(20)
                status = a.get("status", "?")
                print(f"  {name} {role} {status}")
    except Exception:
        print("Cannot reach Piddy API. Is it running?")


def cmd_skills(_args):
    """List loaded skills."""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8889/api/skills")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            skills = data.get("skills", [])
            print(f"Loaded Skills: {data.get('count', len(skills))}\n")
            for s in skills[:30]:
                name = (s.get("name") or "?").ljust(30)
                print(f"  ⚡ {name} {s.get('description', '')[:50]}")
            if len(skills) > 30:
                print(f"  … and {len(skills) - 30} more")
    except Exception:
        print("Cannot reach Piddy API. Is it running?")


def cmd_desktop(_args):
    """Launch Electron desktop app."""
    cmd_start(argparse.Namespace(foreground=False, dashboard_only=False, desktop=True))


def cmd_scan(args):
    """Scan the host machine or a repository."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.api.host_scanner import scan_host, analyze_repo, scan_installed_programs

    if args.repo:
        print(f"Analyzing repository: {args.repo}\n")
        result = analyze_repo(args.repo)
        if "error" in result:
            print(f"  ❌ {result['error']}")
            return
        # Languages
        langs = result.get("languages", {})
        if langs:
            print("  Languages:")
            for lang, count in list(langs.items())[:10]:
                print(f"    {lang.ljust(18)} {count} files")
        # Git
        git = result.get("git")
        if git:
            print(f"\n  Branch:   {git.get('branch', '?')}")
            print(f"  Commit:   {git.get('last_commit', '?')}")
            clean = git.get('clean')
            uncommitted = git.get('uncommitted_changes', 0)
            clean_txt = '✅' if clean else f'⚠ {uncommitted} changes'
            print(f"  Clean:    {clean_txt}")
        # Dependencies
        deps = result.get("dependencies", {})
        if deps:
            print(f"\n  Dependency manifests: {', '.join(deps.keys())}")
        # Issues & Recommendations
        issues = result.get("issues", [])
        recs = result.get("recommendations", [])
        if issues:
            print("\n  Issues:")
            for i in issues:
                icon = {"warn": "⚠️", "error": "❌", "info": "ℹ️"}.get(i["severity"], "?")
                print(f"    {icon} {i['msg']}")
        if recs:
            print("\n  Recommendations:")
            for r in recs:
                print(f"    💡 {r}")
    elif args.programs:
        print("Scanning installed programs...\n")
        programs = scan_installed_programs()
        print(f"  Found {len(programs)} programs\n")
        for p in programs[:50]:
            name = p["name"].ljust(40)
            ver = p.get("version", "")[:20]
            print(f"  {name} {ver}")
        if len(programs) > 50:
            print(f"  … and {len(programs) - 50} more")
    else:
        print("Scanning host machine...\n")
        host = scan_host()
        os_info = host.get("os", {})
        hw = host.get("hardware", {})
        net = host.get("network", {})
        print(f"  OS:        {os_info.get('platform')} {os_info.get('release', '')} ({os_info.get('arch')})")
        print(f"  Hostname:  {os_info.get('hostname')}")
        print(f"  CPU:       {hw.get('cpu_cores', '?')} cores — {hw.get('processor', '?')}")
        print(f"  RAM:       {hw.get('ram_gb', '?')} GB")
        print(f"  Internet:  {'✅ Connected' if net.get('internet_available') else '❌ Offline'}")
        runtimes = host.get("runtimes", {})
        if runtimes:
            print(f"\n  Detected Runtimes ({len(runtimes)}):")
            for name, info in runtimes.items():
                ver = (info.get("version") or "")[:50]
                print(f"    {name.ljust(14)} {ver}")
        disks = host.get("disk", [])
        if disks:
            print(f"\n  Disk:")
            for d in disks:
                print(f"    {d['mount']}  {d['free_gb']} GB free / {d['total_gb']} GB total ({d['used_pct']}% used)")
        tools = host.get("installed_tools", [])
        if tools:
            print(f"\n  Dev Tools ({len(tools)}):")
            for t in tools:
                print(f"    ✓ {t['name'].ljust(14)} ({t['category']})")


def cmd_update(args):
    """Check for or apply updates."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.api.updater import check_for_updates, apply_update

    if args.apply:
        print("Applying update...\n")
        result = apply_update()
        if result.get("success"):
            print(f"  ✅ {result.get('message', 'Update applied')}")
            print(f"  New version: {result.get('new_version', '?')}")
        else:
            print(f"  ❌ {result.get('error', 'Update failed')}")
    else:
        print("Checking for updates...\n")
        result = check_for_updates()
        print(f"  Current version: {result.get('current_version', '?')}")
        if not result.get("internet"):
            print(f"  ⚠ {result.get('message', 'No internet')}")
            return
        if result.get("available"):
            latest = result.get("latest_version") or result.get("remote_sha", "?")
            print(f"  Latest:          {latest}")
            print(f"  📦 {result.get('message', 'Update available')}")
            print(f"\n  To install: python piddy.py update --apply")
        else:
            print(f"  ✅ {result.get('message', 'Up to date')}")


def cmd_platform(_args):
    """Show cross-platform runtime detection."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.platform.runtime import platform_summary

    info = platform_summary()
    print(f"Platform: {info['os']} ({info['arch']})  Machine: {info['machine']}")
    print(f"Hostname: {info['hostname']}\n")
    for rt_name in ("python", "node", "ollama"):
        rt = info.get(rt_name, {})
        path = rt.get("path")
        if isinstance(path, Path):
            path = str(path)
        embedded = "embedded" if rt.get("embedded") else "system"
        ver = rt.get("version") or "not found"
        print(f"  {rt_name.ljust(10)} {ver.ljust(30)} [{embedded}]  {path or ''}")


def cmd_discord(args):
    """Manage the Discord bot."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.integrations.discord_bot import get_discord_bot
    bot = get_discord_bot()
    if args.action == "start":
        result = bot.start()
        print(f"  {'✅' if result.get('success') else '❌'} {result.get('message') or result.get('error')}")
    elif args.action == "stop":
        result = bot.stop()
        print(f"  {'✅' if result.get('success') else '❌'} {result.get('message') or result.get('error')}")
    else:
        s = bot.status()
        print(f"  Running:    {s['running']}")
        print(f"  Library:    {'installed' if s['library_installed'] else 'not installed'}")
        if s.get('connected'):
            print(f"  Guilds:     {s.get('guilds', 0)}")


def cmd_telegram(args):
    """Manage the Telegram bot."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.integrations.telegram_bot import get_telegram_bot
    bot = get_telegram_bot()
    if args.action == "start":
        result = bot.start()
        print(f"  {'✅' if result.get('success') else '❌'} {result.get('message') or result.get('error')}")
    elif args.action == "stop":
        result = bot.stop()
        print(f"  {'✅' if result.get('success') else '❌'} {result.get('message') or result.get('error')}")
    else:
        s = bot.status()
        print(f"  Running:    {s['running']}")
        print(f"  Library:    {'installed' if s['library_installed'] else 'not installed'}")


def cmd_browse(args):
    """Browser automation tool."""
    sys.path.insert(0, str(PROJECT_ROOT))
    import asyncio as _asyncio
    from src.tools.browser_automation import get_browser
    b = get_browser()

    async def _run():
        if args.action == "open":
            await b.launch(headless=not args.visible)
            print("  ✅ Browser launched")
            if args.url:
                result = await b.navigate(args.url)
                print(f"  Navigated to: {result.get('title', '?')} ({result.get('url')})")
        elif args.action == "close":
            await b.close()
            print("  ✅ Browser closed")
        elif args.action == "screenshot":
            dest = args.output or "screenshot.png"
            await b.screenshot(path=dest, full_page=True)
            print(f"  ✅ Screenshot saved to {dest}")
        elif args.action == "extract":
            result = await b.extract_text(args.selector)
            print(result.get("text", "")[:2000])
        else:
            s = b.status()
            print(f"  Playwright: {'installed' if s['library_installed'] else 'not installed'}")
            print(f"  Running:    {s['running']}")
            if s.get('current_url'):
                print(f"  URL:        {s['current_url']}")
    _asyncio.run(_run())


def cmd_productivity(args):
    """Show productivity connector status."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.integrations.productivity import get_all_connector_status
    status = get_all_connector_status()
    for name, info in status.items():
        configured = info.get("configured", False)
        icon = "✅" if configured else "❌"
        print(f"  {icon} {name.ljust(20)} {'configured' if configured else 'not configured'}")
        if info.get("base_url"):
            print(f"     URL: {info['base_url']}")


def main():
    parser = argparse.ArgumentParser(
        prog="piddy",
        description="🎯 Piddy AI Assistant — Unified CLI",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_start = sub.add_parser("start", help="Start Piddy services")
    p_start.add_argument("--fg", "--foreground", dest="foreground", action="store_true", help="Run in foreground")
    p_start.add_argument("--dashboard-only", action="store_true", help="Start only the dashboard API")
    p_start.add_argument("--desktop", action="store_true", help="Launch Electron desktop app")

    sub.add_parser("stop", help="Stop all services")
    sub.add_parser("status", help="Show system status")
    sub.add_parser("doctor", help="Run self-diagnosis")
    sub.add_parser("config", help="Show current configuration")
    sub.add_parser("export", help="Export data to exports/")
    sub.add_parser("agents", help="List registered agents")
    sub.add_parser("skills", help="List loaded skills")
    sub.add_parser("desktop", help="Launch Electron desktop app")

    p_scan = sub.add_parser("scan", help="Scan host machine or a repo")
    p_scan.add_argument("--repo", type=str, help="Path to a local repo to analyze")
    p_scan.add_argument("--programs", action="store_true", help="List installed programs")

    p_update = sub.add_parser("update", help="Check for Piddy updates")
    p_update.add_argument("--apply", action="store_true", help="Apply the update")

    sub.add_parser("platform", help="Show detected runtimes and OS info")

    p_discord = sub.add_parser("discord", help="Manage Discord bot")
    p_discord.add_argument("action", nargs="?", default="status", choices=["start", "stop", "status"])

    p_telegram = sub.add_parser("telegram", help="Manage Telegram bot")
    p_telegram.add_argument("action", nargs="?", default="status", choices=["start", "stop", "status"])

    p_browse = sub.add_parser("browse", help="Browser automation tool")
    p_browse.add_argument("action", nargs="?", default="status", choices=["open", "close", "screenshot", "extract", "status"])
    p_browse.add_argument("--url", type=str, help="URL to navigate to")
    p_browse.add_argument("--visible", action="store_true", help="Show browser window (non-headless)")
    p_browse.add_argument("--output", type=str, help="Screenshot output path")
    p_browse.add_argument("--selector", type=str, help="CSS selector for extraction")

    sub.add_parser("productivity", help="Show productivity connector status")

    args = parser.parse_args()

    commands = {
        "start": cmd_start,
        "stop": cmd_stop,
        "status": cmd_status,
        "doctor": cmd_doctor,
        "config": cmd_config,
        "export": cmd_export,
        "agents": cmd_agents,
        "skills": cmd_skills,
        "desktop": cmd_desktop,
        "scan": cmd_scan,
        "update": cmd_update,
        "platform": cmd_platform,
        "discord": cmd_discord,
        "telegram": cmd_telegram,
        "browse": cmd_browse,
        "productivity": cmd_productivity,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

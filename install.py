#!/usr/bin/env python3
"""
install.py — OpenClaw safety guardrails installer
https://github.com/WilsonWordsofWisdom/SecureOpenClaw/

Behaviour
---------
• New files / folders   → copied into the workspace (existing file backed up first).
• Patched files         → new sections are diffed and appended/merged into the user's
                          live file. Each injected block is wrapped in comment markers
                          so the user knows exactly what was added and can revert it.
• --all-agents          → discovers all workspace-* folders under ~/.openclaw/ and
                          installs into every one automatically.

Usage
-----
    python3 install.py                        # install into default workspace
    python3 install.py --all-agents           # install into ALL agent workspaces
    python3 install.py --workspace PATH       # install into a specific path
    python3 install.py --profile PROFILE      # install into workspace-<PROFILE>
    python3 install.py --dry-run              # preview without making changes
    python3 install.py --all-agents --dry-run # preview all-agent install
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ── ANSI colours ────────────────────────────────────────────────────────────
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
CYAN   = "\033[36m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def info(msg):    print(f"  {GREEN}✔{RESET}  {msg}")
def warn(msg):    print(f"  {YELLOW}!{RESET}  {msg}")
def error(msg):   print(f"  {RED}✘{RESET}  {msg}", file=sys.stderr)
def section(msg): print(f"\n{BOLD}{CYAN}{msg}{RESET}")

# ── Marker constants ─────────────────────────────────────────────────────────
MARKER_BEGIN = "<!-- [GUARDRAILS INSTALL] BEGIN ADDED SECTION: {label} -->"
MARKER_END   = "<!-- [GUARDRAILS INSTALL] END ADDED SECTION: {label} -->"

# ── Patch targets ────────────────────────────────────────────────────────────
# Files listed here are MERGED (new sections appended).
# Everything else is copied verbatim.
PATCH_TARGETS: dict[str, str] = {
    "AGENTS.md":    "AGENTS.md",
    "SOUL.md":      "SOUL.md",
    "HEARTBEAT.md": "HEARTBEAT.md",
}

# ── Workspace discovery ──────────────────────────────────────────────────────

def discover_all_workspaces(openclaw_home: Path) -> list[Path]:
    """
    Find all workspace directories under ~/.openclaw/:
      - workspace          (main)
      - workspace-<name>   (per-agent)
    Excludes backup folders (workspace_backup_*).
    """
    workspaces: list[Path] = []
    for p in sorted(openclaw_home.iterdir()):
        if not p.is_dir():
            continue
        name = p.name
        if name == "workspace":
            workspaces.append(p)
        elif name.startswith("workspace-") and not name.startswith("workspace_backup"):
            workspaces.append(p)
    return workspaces


def resolve_workspace(args_workspace: str | None, args_profile: str | None) -> Path:
    if args_workspace:
        return Path(args_workspace).expanduser().resolve()
    profile = args_profile or os.environ.get("OPENCLAW_PROFILE", "default")
    base = Path(os.environ.get("OPENCLAW_HOME", "~/.openclaw")).expanduser()
    if profile and profile != "default":
        return (base / f"workspace-{profile}").resolve()
    return (base / "workspace").resolve()

# ── Backup helper ────────────────────────────────────────────────────────────

def backup_file(target: Path, backup_dir: Path, dry_run: bool) -> None:
    """Copy a file into the timestamped backup dir, preserving relative structure."""
    openclaw_home = backup_dir.parent
    try:
        rel  = target.relative_to(openclaw_home)
        dest = backup_dir / rel
    except ValueError:
        dest = backup_dir / target.name

    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, dest)
    warn(f"Backed up  : {target}  →  {dest}")

# ── Plain-copy helper ────────────────────────────────────────────────────────

def copy_item(src: Path, dst: Path, backup_dir: Path, dry_run: bool) -> None:
    if dst.exists():
        backup_file(dst, backup_dir, dry_run)
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    verb = "Would install" if dry_run else "Installed"
    info(f"{verb} (new)    : {src.name}  →  {dst}")

# ── Diff-merge helper ────────────────────────────────────────────────────────

def extract_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) tuples. Blank heading = preamble."""
    sections: list[tuple[str, str]] = []
    current_heading = ""
    current_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("#"):
            sections.append((current_heading, "".join(current_lines)))
            current_heading = line.rstrip()
            current_lines = []
        else:
            current_lines.append(line)
    sections.append((current_heading, "".join(current_lines)))
    return sections


def merge_patch(live_path: Path, repo_path: Path, backup_dir: Path, dry_run: bool) -> bool:
    """
    Append sections from repo_path that are absent from live_path.
    Each block is wrapped in GUARDRAILS INSTALL markers.
    Returns True if any changes were (or would be) made.
    """
    live_text = live_path.read_text(encoding="utf-8")
    repo_text = repo_path.read_text(encoding="utf-8")

    blocks_to_add: list[tuple[str, str]] = []

    for heading, body in extract_sections(repo_text):
        if not heading:
            continue
        label = heading.lstrip("#").strip()
        begin = MARKER_BEGIN.format(label=label)

        if heading in live_text or begin in live_text:
            info(f"  ↳ Already present, skipping : {heading}")
            continue

        end   = MARKER_END.format(label=label)
        block = f"\n{begin}\n{heading}\n{body.rstrip()}\n{end}\n"
        blocks_to_add.append((heading, block))

    if not blocks_to_add:
        info(f"No new sections to merge into : {live_path.name}")
        return False

    for heading, _ in blocks_to_add:
        warn(f"  ↳ Will inject section       : {heading}")

    if not dry_run:
        backup_file(live_path, backup_dir, dry_run=False)
        with live_path.open("a", encoding="utf-8") as fh:
            fh.write("\n")
            for _, block in blocks_to_add:
                fh.write(block)

    verb = "Would merge" if dry_run else "Merged"
    info(f"{verb} (patch)  : {repo_path.name}  →  {live_path}")
    return True

# ── Extra dirs outside workspace ─────────────────────────────────────────────

def ensure_extra_dirs(workspace: Path, dry_run: bool) -> None:
    """Create directories that live outside ~/.openclaw/workspace/."""
    openclaw_home = workspace.parent
    extra_dirs = [
        openclaw_home / "logs",
    ]
    for d in extra_dirs:
        if not d.exists():
            if not dry_run:
                d.mkdir(parents=True, exist_ok=True)
            verb = "Would create" if dry_run else "Created dir"
            info(f"{verb}          : {d}")
        else:
            info(f"Dir exists, skipping     : {d}")

# ── Per-workspace install ─────────────────────────────────────────────────────

def install_into_workspace(
    source_dir: Path,
    workspace: Path,
    backup_dir: Path,
    dry_run: bool,
) -> dict[str, int]:
    """Install guardrails into a single workspace. Returns counts dict."""
    counts = {"new": 0, "merged": 0, "skipped": 0}

    ensure_extra_dirs(workspace, dry_run)

    for src in sorted(source_dir.rglob("*")):
        rel     = src.relative_to(source_dir)
        rel_str = str(rel)
        dst     = workspace / rel

        if src.is_dir():
            if not dst.exists():
                if not dry_run:
                    dst.mkdir(parents=True, exist_ok=True)
                verb = "Would create" if dry_run else "Created dir"
                info(f"{verb}          : {dst}")
            continue

        if rel_str in PATCH_TARGETS:
            target = workspace / PATCH_TARGETS[rel_str]
            if not target.exists():
                copy_item(src, target, backup_dir, dry_run)
                counts["new"] += 1
            else:
                changed = merge_patch(target, src, backup_dir, dry_run)
                counts["merged" if changed else "skipped"] += 1
        else:
            copy_item(src, dst, backup_dir, dry_run)
            counts["new"] += 1

    return counts

# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install OpenClaw safety guardrails into your workspace(s)."
    )
    parser.add_argument("--workspace", "-w", metavar="PATH",
                        help="Override the target workspace directory.")
    parser.add_argument("--profile", "-p", metavar="PROFILE",
                        help="OpenClaw profile name (targets workspace-<PROFILE>).")
    parser.add_argument("--all-agents", "-a", action="store_true",
                        help="Install into ALL workspace and workspace-* folders.")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Preview changes without writing anything.")
    args = parser.parse_args()

    repo_root  = Path(__file__).parent.resolve()
    source_dir = repo_root / "workspace"
    openclaw_home = Path(os.environ.get("OPENCLAW_HOME", "~/.openclaw")).expanduser()
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = openclaw_home / f"workspace_backup_{timestamp}"

    section("OpenClaw Safety Guardrails Installer")
    if args.dry_run:
        warn("DRY RUN — no files will be changed.\n")

    if not source_dir.exists():
        error(
            f"Source directory not found: {source_dir}\n"
            "Ensure you cloned the full repository and run this script from its root."
        )
        sys.exit(1)

    # ── Determine target workspaces ──────────────────────────────────────────
    if args.all_agents:
        workspaces = discover_all_workspaces(openclaw_home)
        if not workspaces:
            error(f"No workspace directories found under {openclaw_home}")
            sys.exit(1)
        print(f"  Found {len(workspaces)} workspace(s) to install into:")
        for ws in workspaces:
            print(f"    • {ws}")
    else:
        workspace = resolve_workspace(args.workspace, args.profile)
        if not workspace.exists():
            warn(f"Workspace not found: {workspace}")
            if not args.dry_run:
                confirm = input("  Create it now? [y/N] ").strip().lower()
                if confirm != "y":
                    error("Aborting.")
                    sys.exit(1)
                workspace.mkdir(parents=True, exist_ok=True)
                info(f"Created workspace: {workspace}")
        workspaces = [workspace]

    print(f"  Source    : {source_dir}")
    print(f"  Backups   : {backup_dir}  (only created if needed)")

    # ── Install into each workspace ──────────────────────────────────────────
    total = {"new": 0, "merged": 0, "skipped": 0}

    for workspace in workspaces:
        section(f"Workspace: {workspace.name}")
        counts = install_into_workspace(source_dir, workspace, backup_dir, args.dry_run)
        for k in total:
            total[k] += counts[k]

    # ── Summary ───────────────────────────────────────────────────────────────
    section("Summary")
    if args.all_agents:
        print(f"  Workspaces processed : {len(workspaces)}")
    print(f"  New files installed  : {total['new']}")
    print(f"  Files patched        : {total['merged']}")
    print(f"  Already up-to-date   : {total['skipped']}")

    if total["new"] + total["merged"] > 0 and not args.dry_run:
        print(
            f"\n  Restart your gateway to pick up the changes:\n"
            f"    openclaw gateway restart\n"
        )
    if args.dry_run:
        warn("Dry run complete. Re-run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()

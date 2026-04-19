#!/usr/bin/env python3
"""
install.py — OpenClaw safety guardrails installer
https://github.com/you/your-repo

Behaviour
---------
• New files / folders   → copied into the workspace (existing file backed up first).
• Patched files         → new sections are diffed and appended/merged into the user's
                          live file. Each injected block is wrapped in comment markers
                          so the user knows exactly what was added and can revert it.

Usage
-----
    python3 install.py [--workspace PATH] [--profile PROFILE] [--dry-run]
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

# ── Marker constants (used to wrap injected sections) ────────────────────────
MARKER_BEGIN = "<!-- [GUARDRAILS INSTALL] BEGIN ADDED SECTION: {label} -->"
MARKER_END   = "<!-- [GUARDRAILS INSTALL] END ADDED SECTION: {label} -->"
MARKER_RE    = re.compile(r"<!--\s*\[GUARDRAILS INSTALL\]")


# ── Identify which files are "patch" targets vs plain new files ──────────────
#
# Keys   : paths relative to the `workspace/` source folder in this repo.
# Values : paths relative to the OpenClaw workspace root on the target machine.
#
# Files listed here are MERGED (diff-based section append).
# Everything else is copied verbatim.
#
PATCH_TARGETS: dict[str, str] = {
    "AGENTS.md":    "AGENTS.md",
    "SOUL.md":      "SOUL.md",
    "HEARTBEAT.md": "HEARTBEAT.md",
}


# ── Workspace resolution ─────────────────────────────────────────────────────

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
    """Copy an existing file into the timestamped backup directory."""
    try:
        rel  = target.relative_to(Path.home())
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
    """
    Split markdown into top-level sections as (heading_line, body) tuples.
    A blank heading captures any preamble before the first '#' line.
    """
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
    Append any top-level sections from repo_path that don't already appear
    in live_path. Each injected block is wrapped in GUARDRAILS INSTALL markers.

    Returns True if any changes were (or would be) made.
    """
    live_text = live_path.read_text(encoding="utf-8")
    repo_text = repo_path.read_text(encoding="utf-8")

    repo_sections = extract_sections(repo_text)
    blocks_to_add: list[str] = []

    for heading, body in repo_sections:
        if not heading:
            continue  # skip preamble

        # Skip if this heading is already present in the live file
        if heading in live_text:
            info(f"  ↳ Already present, skipping : {heading}")
            continue

        # Also skip if we've injected it before (marker present)
        label = heading.lstrip("#").strip()
        if MARKER_BEGIN.format(label=label) in live_text:
            info(f"  ↳ Already injected, skipping: {heading}")
            continue

        begin = MARKER_BEGIN.format(label=label)
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


# ── Extra dirs (outside workspace) ──────────────────────────────────────────

def ensure_extra_dirs(workspace: Path, dry_run: bool) -> None:
    """
    Create directories that live outside ~/.openclaw/workspace/.
    Edit this list to match your guardrails setup.
    """
    openclaw_home = workspace.parent   # ~/.openclaw/
    extra_dirs = [
        openclaw_home / "logs",        # ~/.openclaw/logs
    ]
    for d in extra_dirs:
        if not d.exists():
            if not dry_run:
                d.mkdir(parents=True, exist_ok=True)
            verb = "Would create" if dry_run else "Created dir"
            info(f"{verb}          : {d}")
        else:
            info(f"Dir exists, skipping     : {d}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install OpenClaw safety guardrails into your workspace."
    )
    parser.add_argument("--workspace", "-w", metavar="PATH",
                        help="Override the target workspace directory.")
    parser.add_argument("--profile", "-p", metavar="PROFILE",
                        help="OpenClaw profile name.")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Preview changes without writing anything.")
    args = parser.parse_args()

    repo_root  = Path(__file__).parent.resolve()
    source_dir = repo_root / "workspace"
    workspace  = resolve_workspace(args.workspace, args.profile)
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = workspace.parent / f"workspace_backup_{timestamp}"

    section("OpenClaw Safety Guardrails Installer")
    if args.dry_run:
        warn("DRY RUN — no files will be changed.\n")

    if not source_dir.exists():
        error(
            f"Source directory not found: {source_dir}\n"
            "Ensure you cloned the full repository and run this script from its root."
        )
        sys.exit(1)

    if not workspace.exists():
        warn(f"Workspace not found: {workspace}")
        if not args.dry_run:
            confirm = input("  Create it now? [y/N] ").strip().lower()
            if confirm != "y":
                error("Aborting.")
                sys.exit(1)
            workspace.mkdir(parents=True, exist_ok=True)
            info(f"Created workspace: {workspace}")

    print(f"  Source    : {source_dir}")
    print(f"  Workspace : {workspace}")
    print(f"  Backups   : {backup_dir}  (only created if needed)")

    section("Creating extra directories…")
    ensure_extra_dirs(workspace, args.dry_run)

    section("Installing / merging files…")

    counts = {"new": 0, "merged": 0, "skipped": 0}

    for src in sorted(source_dir.rglob("*")):
        rel     = src.relative_to(source_dir)
        rel_str = str(rel)
        dst     = workspace / rel

        if src.is_dir():
            if not dst.exists():
                if not dry_run:
                    dst.mkdir(parents=True, exist_ok=True)
                verb = "Would create" if args.dry_run else "Created dir"
                info(f"{verb}          : {dst}")
            continue

        if rel_str in PATCH_TARGETS:
            target = workspace / PATCH_TARGETS[rel_str]
            if not target.exists():
                copy_item(src, target, backup_dir, args.dry_run)
                counts["new"] += 1
            else:
                changed = merge_patch(target, src, backup_dir, args.dry_run)
                counts["merged" if changed else "skipped"] += 1
        else:
            copy_item(src, dst, backup_dir, args.dry_run)
            counts["new"] += 1

    section("Summary")
    print(f"  New files installed : {counts['new']}")
    print(f"  Files patched       : {counts['merged']}")
    print(f"  Already up-to-date  : {counts['skipped']}")

    if counts["new"] + counts["merged"] > 0 and not args.dry_run:
        print(
            f"\n  Restart your gateway to pick up the changes:\n"
            f"    openclaw gateway restart\n"
        )
    if args.dry_run:
        warn("Dry run complete. Re-run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()

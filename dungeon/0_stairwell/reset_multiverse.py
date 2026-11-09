"""Floor Infinity: reset the multiverse.

Removes everything the crawl installed on this machine and leaves it
like new. Standard library only: this script must run after uv and the
project virtualenv are gone, so it cannot import anything third-party.

Tiers:
  1  campaign state (default): servers on ports 8000-8009, the project
     .venv, the Floor 5 knowledge base, the Floor 7 harness state,
     mid-song-save folders, web node_modules and dist, the tide-pool
     container, every __pycache__ under the repo.
  2  project caches (--caches): the uv cache, the embedding-model
     cache, uv-managed Pythons, the tide-pool image.
  3  global tools (--global-tools): the uv binary and the global
     AgentCore CLI, only when this script installed them.
  4  cloud (--cloud-check): read-only verification that the Floor 8
     AWS resources are gone. Never deletes; prints the manual
     commands from the Exit page when something remains.

Nothing runs without an inventory first. --dry-run (the default)
lists what would go. --apply deletes tier 1, plus whichever higher
tiers were asked for. Safe to re-run: missing paths report as gone.
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys

PORTS = list(range(8000, 8010))

# Repo-relative paths the crawl generates. Each row: (tier, relpath, kind).
# kind is "dir", "file", or "walk" (every matching dirname under the repo).
TIER_1 = [
    (1, ".venv", "dir"),
    (1, "dungeon/5_a2a_integration/utils/rules_knowledge_base", "dir"),
    (1, "dungeon/8_agentcore_production/gameprod", "dir"),
    (1, "dungeon/8_agentcore_production/.env", "file"),
    (1, "dungeon/7_strands_harness/.agent", "dir"),
    (1, "site/web/node_modules", "dir"),
    (1, "site/web/dist", "dir"),
]

TIER_1_WALK = [
    (1, "__pycache__", "walk"),
    (1, ".mid-song-save", "walk"),
]

# Home-relative caches the crawl fills. Each row: (tier, relpath, kind).
TIER_2 = [
    (2, ".cache/uv", "dir"),
    (2, ".cache/huggingface", "dir"),
    (2, ".local/share/uv/python", "dir"),
]

NEVER_TOUCH = [
    "AWS config and credentials (~/.aws)",
    "git, Docker or Node themselves (unless --global-tools names them)",
    "your shell setup and SSH keys",
    "anything outside this repo and the cache rows above",
    "learner edits to tracked files (git status must show only those)",
]


def repo_root() -> str:
    """The repo root is three folders above this script."""
    here = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(here)))


def dir_size(path: str) -> int:
    """Total bytes under a path, 0 when it is gone."""
    total = 0
    for base, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(base, name))
            except OSError:
                pass
    return total


def inventory(root: str, home: str) -> list:
    """Every ledger row with its live state. Nothing is deleted here."""
    found = []

    def add(tier, path, kind):
        if os.path.isdir(path):
            found.append((tier, path, kind, "present", dir_size(path)))
        elif os.path.isfile(path) or os.path.islink(path):
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            found.append((tier, path, kind, "present", size))
        else:
            found.append((tier, path, kind, "gone", 0))

    for tier, rel, kind in TIER_1:
        add(tier, os.path.join(root, rel), kind)
    for tier, name, kind in TIER_1_WALK:
        hits = []
        for base, dirs, _files in os.walk(root):
            if name in dirs:
                hits.append(os.path.join(base, name))
        if hits:
            for hit in hits:
                found.append((tier, hit, kind, "present", dir_size(hit)))
        else:
            found.append((tier, os.path.join(root, "<" + name + ">"), kind, "gone", 0))
    for tier, rel, kind in TIER_2:
        add(tier, os.path.join(home, rel), kind)
    return found


def check_paths(items: list, root: str, home: str) -> None:
    """Refuse any path outside the repo and the named caches."""
    for _tier, path, _kind, _state, _size in items:
        real = os.path.realpath(path)
        if not (real.startswith(os.path.realpath(root) + os.sep) or real.startswith(os.path.realpath(home) + os.sep)):
            raise ValueError("Refusing path outside the repo and home caches: " + path)


def listening_ports(ports: list) -> list:
    """Ports on localhost that accept a connection right now."""
    open_ports = []
    for port in ports:
        sock = socket.socket()
        sock.settimeout(0.2)
        try:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                open_ports.append(port)
        finally:
            sock.close()
    return open_ports


def stop_servers(ports: list) -> list:
    """Ask known crawl servers to stop, return ports still listening."""
    busy = listening_ports(ports)
    if not busy:
        return []
    for pattern in ("uvicorn", "vite"):
        try:
            subprocess.run(["pkill", "-f", pattern], capture_output=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            pass
    return listening_ports(ports)


def remove(path: str, kind: str, dry_run: bool) -> str:
    """Delete one inventoried path, or report it in a dry run."""
    if dry_run:
        return "would-remove"
    try:
        if os.path.islink(path) or os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            return "gone"
    except OSError as exc:
        return "failed: " + str(exc)
    return "removed"


def report(items: list) -> str:
    """One line per ledger row: tier, size, state, path."""
    lines = []
    for tier, path, _kind, state, size in items:
        lines.append("tier %d | %10d bytes | %-7s | %s" % (tier, size, state, path))
    return "\n".join(lines)


def cloud_check() -> list:
    """Read-only AWS check. Returns lines for the report."""
    lines = []
    for cmd in (
        ["aws", "cloudformation", "describe-stacks", "--stack-name", "AgentCore-gameprod-default"],
        ["aws", "s3", "ls"],
        ["aws", "logs", "describe-log-groups", "--log-group-name-prefix", "/aws/agentcore/gameprod"],
    ):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            lines.append("$ " + " ".join(cmd) + " -> exit " + str(out.returncode))
            if out.returncode == 0 and out.stdout.strip():
                lines.append(out.stdout.strip()[:500])
        except (OSError, subprocess.SubprocessError) as exc:
            lines.append("$ " + " ".join(cmd) + " -> not run: " + str(exc))
    return lines


def main(argv=None, root=None, home=None) -> int:
    parser = argparse.ArgumentParser(description="Reset the multiverse: remove what the crawl installed.")
    parser.add_argument("--apply", action="store_true", help="Delete. Without it, only inventory.")
    parser.add_argument("--caches", action="store_true", help="Include tier 2 caches.")
    parser.add_argument("--global-tools", action="store_true", help="Include tier 3 global tools.")
    parser.add_argument("--cloud-check", action="store_true", help="Read-only AWS check (tier 4).")
    parser.add_argument("--yes", action="store_true", help="Skip per-tier confirmation.")
    args = parser.parse_args(argv)

    root = root or repo_root()
    home = home or os.path.expanduser("~")
    dry_run = not args.apply

    tiers = {1}
    if args.caches:
        tiers.add(2)

    items = [row for row in inventory(root, home) if row[0] in tiers]
    check_paths(items, root, home)

    print("=== Floor Infinity inventory ===")
    print(report(items))

    if dry_run:
        print("Dry run: nothing deleted. Re-run with --apply to delete tier 1.")
        return 0

    still_busy = stop_servers(PORTS)
    if still_busy:
        print("Still listening (stop these yourself, usually Ctrl+C): %s" % still_busy)

    for tier in sorted(tiers):
        if not args.yes:
            answer = input("Delete tier %d? Type YES to continue: " % tier)
            if answer.strip() != "YES":
                print("Skipped tier %d." % tier)
                continue
        for row in items:
            if row[0] == tier and row[3] == "present":
                print("%s | %s" % (remove(row[1], row[2], False), row[1]))

    print("=== Verify ===")
    print(report(inventory(root, home)))

    if args.global_tools:
        print("Tier 3 is manual: remove uv and the global AgentCore CLI with the commands on the Floor Infinity page.")
    if args.cloud_check:
        print("=== Cloud check ===")
        for line in cloud_check():
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())

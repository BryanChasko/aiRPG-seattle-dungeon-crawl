"""Floor 0 preflight: check the local setup before you climb.

    uv run python dungeon/0_stairwell/preflight.py           local checks only
    uv run python dungeon/0_stairwell/preflight.py --live    also one tiny Amazon Nova 2 Lite request

Exit 0 when nothing failed; otherwise exit 1 with a one-line fix under each FAIL. A WARN never fails the run.
"""

import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DUNGEON = REPO_ROOT / "dungeon"
MODEL_ID = "us.amazon.nova-2-lite-v1:0"
REGION = "us-west-2"
PORTS = {  # port -> who uses it
    8000: "Rules Agent", 8001: "Character Agent", 8002: "dice MCP server", 8003: "tide server / Barnaby's line",
    8004: "warehouse grid server", 8009: "Narrator", 5173: "Vite dev server (Floor 6)",
}
results: list[tuple[str, str, str, str]] = []  # (status, name, detail, fix)


def check(status: str, name: str, detail: str = "", fix: str = "") -> None:
    results.append((status, name, detail, fix))
    print(f"{status:<4}  {name}: {detail}")


def minimum_python() -> tuple[int, ...]:
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    found = re.search(r'requires-python\s*=\s*"[^"\d]*(\d+(?:\.\d+)*)', text)
    return tuple(int(n) for n in found.group(1).split(".")) if found else (3, 10)


def run(cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def check_python_and_venv() -> None:
    need, have = minimum_python(), sys.version_info[: len(minimum_python())]
    label = ".".join(map(str, need))
    if have >= need:
        check("PASS", "python", f"{sys.version.split()[0]} (needs >= {label})")
    else:
        check("FAIL", "python", f"{sys.version.split()[0]} is older than {label}", f"run: uv python install {label}, then uv sync")
    if sys.prefix != sys.base_prefix:
        check("PASS", "venv", f"running inside {sys.prefix}")
    else:
        check("FAIL", "venv", "not running inside the project venv", "run: uv sync, then start with uv run python ...")


def check_tools() -> None:
    check("PASS", "uv", shutil.which("uv")) if shutil.which("uv") else check(
        "FAIL", "uv", "not on PATH", "install uv from https://docs.astral.sh/uv/ and reopen the terminal")
    if not shutil.which("docker"):
        check("WARN", "docker", "not on PATH (Sandbox Tide Pool and the web build need it)", "install Docker and start it")
    else:
        try:
            ok = run(["docker", "info"], 20).returncode == 0
        except subprocess.TimeoutExpired:
            ok = False
        if ok:
            check("PASS", "docker", "daemon reachable")
        else:
            check("FAIL", "docker", "installed but the daemon does not answer", "start Docker Desktop or run: sudo systemctl start docker")
    if shutil.which("node"):
        check("PASS", "node", run(["node", "--version"]).stdout.strip() + " (Floor 6)")
    else:
        check("WARN", "node", "not on PATH (Floor 6 web interface needs it)", "install Node 24, or build the web interface with Docker")


def check_ports() -> None:
    busy = []
    for port, who in PORTS.items():
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                busy.append(f"{port} ({who})")
    if busy:
        check("WARN", "ports", "in use: " + ", ".join(busy), "stop whatever holds them (lsof -i :<port>) before starting that floor's servers")
    else:
        check("PASS", "ports", "free: " + ", ".join(map(str, PORTS)))


def check_aws(live: bool) -> None:
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        check("FAIL", "boto3", "not installed", "run: uv sync")
        return
    profile = os.environ.get("AWS_PROFILE")
    try:
        session = boto3.Session()
        region = session.region_name
    except BotoCoreError as err:
        check("FAIL", "aws profile", str(err)[:90], "set AWS_PROFILE to a profile that exists in ~/.aws/config")
        return
    if region == REGION:
        check("PASS", "region", region)
    else:
        check("FAIL", "region", f"{region or 'unset'} (the workshop uses {REGION})", f"run: export AWS_DEFAULT_REGION={REGION}")
    expired = f"run aws sso login --profile {profile or '<profile>'}"
    try:
        who = session.client("sts", region_name=REGION).get_caller_identity()
        check("PASS", "aws credentials", f"{who['Arn'].split('/')[-1]} in account {who['Account']} (profile {profile or 'default chain'})")
    except Exception as err:  # SSO expiry surfaces as several botocore exception types
        text = str(err)
        if "NoCredentialsError" in type(err).__name__ or "Unable to locate" in text:
            check("FAIL", "aws credentials", "none found", f"set AWS_PROFILE, then {expired}")
        elif any(w in text.lower() for w in ("sso", "expired", "token", "refresh")):
            check("FAIL", "aws credentials", "SSO session expired or missing", expired)
        else:
            check("FAIL", "aws credentials", text[:90], f"check AWS_PROFILE ({profile or 'unset'}) and your network, then {expired}")
        return
    if live:
        try:
            reply = session.client("bedrock-runtime", region_name=REGION).converse(
                modelId=MODEL_ID, messages=[{"role": "user", "content": [{"text": "Say ready."}]}],
                inferenceConfig={"maxTokens": 10})
            words = reply["output"]["message"]["content"][0]["text"].strip()
            check("PASS", "nova 2 lite", f"{MODEL_ID} answered: {words[:40]!r}")
        except (BotoCoreError, ClientError, KeyError, IndexError) as err:
            check("FAIL", "nova 2 lite", str(err)[:100], f"enable the model in Amazon Bedrock for {REGION}, or {expired}")


def main() -> int:
    live = "--live" in sys.argv[1:]
    print(f"Floor 0 preflight{' (live)' if live else ''}\n")
    check_python_and_venv()
    check_tools()
    check_ports()
    check_aws(live)
    failed = [r for r in results if r[0] == "FAIL"]
    print()
    for _, name, _, fix in failed:
        print(f"FIX   {name}: {fix}")
    print(f"{len(failed)} failed, {sum(r[0] == 'WARN' for r in results)} warnings" if failed else "All clear. Climb on.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

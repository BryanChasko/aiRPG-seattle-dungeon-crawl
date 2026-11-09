#!/usr/bin/env python3
"""Small client for the Meta API (api.meta.ai/v1) that the art tools share: key lookup, GET and POST.

Usage:
  python3 tools/meta_api.py models        list the models this key can call (free, no render)

The key comes from META_IMAGE_API_KEY, then MODEL_API_KEY, then ~/.config/muse/auth.json
(providers.meta.api_key), and is never printed or written anywhere. The auth.json key is the
Muse subscription OAuth credential: it covers the muse-* models but has zero SAM quota
(sam-3.1 answers 429 rate_limit_exceeded instantly). SAM needs a Meta Model API key
(MODEL_API_KEY in Meta's samples); ours lives in AWS Systems Manager Parameter Store at
/heraldstack/shared/meta-model-api-key (account 211125425201), e.g.
  export META_IMAGE_API_KEY=$(aws ssm get-parameter --name /heraldstack/shared/meta-model-api-key \
    --with-decryption --profile ops-reader --region us-west-2 --query Parameter.Value --output text)
(the parameter lives in us-west-2; a profile defaulting elsewhere creates a stray copy there.)
"""
from __future__ import annotations
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

AUTH_FILE = Path.home() / ".config" / "muse" / "auth.json"


def _meta() -> dict:
    try:
        return json.loads(AUTH_FILE.read_text())["providers"]["meta"]
    except (OSError, KeyError, ValueError):
        return {}


BASE = (_meta().get("api_base_url") or "https://api.meta.ai/v1").rstrip("/")


def api_key() -> str:
    return (os.environ.get("META_IMAGE_API_KEY") or os.environ.get("MODEL_API_KEY")
            or _meta().get("api_key", ""))


def request(method: str, path: str, body: dict | None = None, timeout: int = 300, waits=(5, 20, 60)) -> dict:
    """One API call; retries a burst 429 or a 5xx, but raises at once on a usage cap (long Retry-After)."""
    import time
    data = json.dumps(body).encode() if body is not None else None
    for i, wait in enumerate((0,) + tuple(waits)):
        time.sleep(wait)
        rq = urllib.request.Request(BASE + path, data=data, method=method,
                                    headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(rq, timeout=timeout) as rp:
                return json.loads(rp.read())
        except urllib.error.HTTPError as e:
            retry_after = int(e.headers.get("Retry-After") or 0)
            if e.code not in (429, 500, 502, 503) or retry_after > max(waits) or i == len(waits):
                raise
            print(f"{e.code} on {path}, retry {i + 1} of {len(waits)}", file=sys.stderr)
    raise RuntimeError("unreachable")


def main() -> int:
    if sys.argv[1:] != ["models"]:
        print(__doc__); return 2
    try:
        out = request("GET", "/models")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}"); return 1
    for m in out.get("data", out if isinstance(out, list) else []):
        print(m.get("id"), "|", m.get("owned_by", ""), "|", ",".join(m.get("capabilities", []) or []))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""One-shot SAM 3.1 diagnostic: a single raw call, no retries, full status/headers/body.

Splits the three 429 kinds: burst limit (small Retry-After), usage cap (large Retry-After),
and zero quota / model not provisioned for this key (error code in the body). A tiny synthetic
image rules out payload size; an optional control call to a muse-* model on the same key
rules out the key and the /responses surface itself.

Usage:
  uv run --with pillow python3 tools/sam_probe.py                 tiny synthetic image
  uv run --with pillow python3 tools/sam_probe.py <image> "concept"
  uv run --with pillow python3 tools/sam_probe.py --control       also call muse-spark-1.3
"""
from __future__ import annotations
import base64, io, json, sys, time, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meta_api  # noqa: E402


def one_call(label: str, body: dict) -> None:
    data = json.dumps(body).encode()
    rq = urllib.request.Request(meta_api.BASE + "/responses", data=data, method="POST",
                                headers={"Authorization": f"Bearer {meta_api.api_key()}",
                                         "Content-Type": "application/json"})
    print(f"\n== {label} ==\nPOST {meta_api.BASE}/responses  model={body['model']}  body={len(data)}B")
    t0 = time.time()
    try:
        with urllib.request.urlopen(rq, timeout=120) as rp:
            raw = rp.read()
            print(f"status {rp.status} in {time.time()-t0:.1f}s")
            for h in ("Retry-After", "x-request-id", "x-ratelimit-limit-requests",
                      "x-ratelimit-remaining-requests", "x-ratelimit-reset-requests"):
                if rp.headers.get(h):
                    print(f"  {h}: {rp.headers[h]}")
            out = json.loads(raw)
            text = "".join(c.get("text", "") for o in out.get("output", [])
                           for c in o.get("content", []) or [] if c.get("type") == "output_text")
            print(f"output_text: {len(text)} chars | head: {text[:200]!r}")
            if out.get("usage"):
                print(f"usage: {out['usage']}")
    except urllib.error.HTTPError as e:
        raw = e.read()
        print(f"status {e.code} in {time.time()-t0:.1f}s")
        for k, v in e.headers.items():
            if any(s in k.lower() for s in ("retry", "ratelimit", "request-id", "quota")):
                print(f"  {k}: {v}")
        try:
            err = json.loads(raw).get("error", json.loads(raw))
            print(f"error.type={err.get('type')} code={err.get('code')}")
            print(f"error.message={err.get('message')}")
            print(f"error full: {json.dumps(err)[:600]}")
        except ValueError:
            print(f"body (not json): {raw[:600].decode('utf-8', 'replace')}")


def upload_file(png_bytes: bytes) -> str:
    """POST /v1/files (multipart, purpose=user_data), the playground path. Returns the file id."""
    import uuid
    b = "----samprobe" + uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"purpose\"\r\n\r\nuser_data\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"upload.png\"\r\n"
            "Content-Type: image/png\r\n\r\n").encode() + png_bytes + f"\r\n--{b}--\r\n".encode()
    rq = urllib.request.Request(meta_api.BASE + "/files", data=body, method="POST",
                                headers={"Authorization": f"Bearer {meta_api.api_key()}",
                                         "Content-Type": f"multipart/form-data; boundary={b}"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(rq, timeout=120) as rp:
            out = json.loads(rp.read())
            print(f"upload: status {rp.status} in {time.time()-t0:.1f}s id={out.get('id')} "
                  f"bytes={out.get('bytes')} purpose={out.get('purpose')}")
            return out["id"]
    except urllib.error.HTTPError as e:
        print(f"upload: status {e.code} retry-after={e.headers.get('Retry-After')} "
              f"body={e.read()[:400].decode('utf-8', 'replace')}")
        raise


def stream_call(label: str, body: dict) -> str:
    """POST /responses with SSE; print event types, return the joined output_text."""
    data = json.dumps(body).encode()
    rq = urllib.request.Request(meta_api.BASE + "/responses", data=data, method="POST",
                                headers={"Authorization": f"Bearer {meta_api.api_key()}",
                                         "Content-Type": "application/json", "Accept": "text/event-stream"})
    print(f"\n== {label} ==\nPOST {meta_api.BASE}/responses stream model={body['model']} body={len(data)}B")
    t0, text, kinds = time.time(), [], []
    try:
        with urllib.request.urlopen(rq, timeout=300) as rp:
            print(f"status {rp.status} (headers in {time.time()-t0:.1f}s)")
            for raw in rp:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    kinds.append("[DONE]"); break
                try:
                    ev = json.loads(payload)
                except ValueError:
                    kinds.append(f"<unparsed {len(payload)}B>"); continue
                kinds.append(ev.get("type", "?"))
                if ev.get("type") == "response.output_text.delta":
                    text.append(ev.get("delta", ""))
                if ev.get("type") in ("response.failed", "error"):
                    print(f"  failure event: {json.dumps(ev)[:500]}")
    except urllib.error.HTTPError as e:
        print(f"status {e.code} retry-after={e.headers.get('Retry-After')} "
              f"body={e.read()[:500].decode('utf-8', 'replace')}")
        return ""
    joined = "".join(text)
    seen = list(dict.fromkeys(kinds))
    print(f"events ({len(kinds)}): {seen} | {time.time()-t0:.1f}s total")
    print(f"output_text: {len(joined)} chars | head: {joined[:220]!r}")
    return joined


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    control = "--control" in sys.argv[1:]
    if args:
        from PIL import Image
        png = io.BytesIO(); Image.open(args[0]).convert("RGB").save(png, "PNG")
        concept = args[1] if len(args) > 1 else "character"
    else:
        from PIL import Image, ImageDraw
        im = Image.new("RGB", (128, 128), "white"); ImageDraw.Draw(im).rectangle((24, 24, 104, 104), fill="red")
        png = io.BytesIO(); im.save(png, "PNG"); concept = "red square"
    if "--playground" in sys.argv[1:]:
        try:
            fid = upload_file(png.getvalue())
        except urllib.error.HTTPError:
            return 1
        stream_call(f"playground shape: {concept!r}", {"model": "sam-3.1", "stream": True,
                    "metadata": {"mask_encoding": "lossless", "include_confidence": "true"},
                    "input": [{"type": "message", "role": "user", "content": [
                        {"type": "input_text", "text": concept},
                        {"type": "input_image", "file_id": fid}]}]})
        return 0
    data_url = "data:image/png;base64," + base64.b64encode(png.getvalue()).decode()
    one_call(f"SAM probe: {concept!r}", {"model": "sam-3.1", "stream": False,
             "metadata": {"include_confidence": "true"},
             "input": [{"type": "message", "role": "user", "content": [
                 {"type": "input_text", "text": concept},
                 {"type": "input_image", "image_url": data_url}]}]})
    if control:
        one_call("control: muse-spark-1.3 text", {"model": "muse-spark-1.3", "stream": False,
                 "input": [{"type": "message", "role": "user", "content": [
                     {"type": "input_text", "text": "Reply with the single word: pong"}]}]})
    return 0


if __name__ == "__main__":
    sys.exit(main())

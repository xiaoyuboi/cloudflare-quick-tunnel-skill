#!/usr/bin/env python3
"""End-to-end test for the Cloudflare Tunnel skill quick mode.

The test starts a temporary local HTTP site, exposes it with cloudflared
Quick Tunnel, extracts the trycloudflare.com URL, then verifies that the
public URL returns the expected page content.
"""

from __future__ import annotations

import functools
import http.server
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.request import Request, urlopen

EXPECTED = "Cloudflare Tunnel Skill Quick Mode Test OK"
TIMEOUT_SECONDS = 120


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def get_free_port() -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def fetch(url: str, timeout: int = 15) -> str:
    # Prefer curl because macOS/Python urllib may inherit local proxy settings that
    # break trycloudflare.com verification. --noproxy '*' tests the public URL directly.
    if shutil.which("curl"):
        result = subprocess.run(
            ["curl", "--noproxy", "*", "-sS", "-L", "--max-time", str(timeout), url],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode == 6:
            # DNS resolution failed. Fake-IP proxy resolvers and slow trycloudflare
            # propagation both break the system resolver, so retry via DNS-over-HTTPS.
            result = subprocess.run(
                ["curl", "--noproxy", "*", "--doh-url", "https://1.1.1.1/dns-query",
                 "-sS", "-L", "--max-time", str(timeout), url],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        if result.returncode == 0:
            return result.stdout
        raise RuntimeError(result.stderr.strip() or f"curl exited {result.returncode}")
    req = Request(url, headers={"User-Agent": "quick-tunnel-skill-test/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    if not shutil.which("cloudflared"):
        print("ERROR: cloudflared not found. Install it first.", file=sys.stderr)
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="quick-tunnel-skill-"))
    config = tmp / "cloudflared-empty.yml"
    config.write_text("", encoding="utf-8")
    (tmp / "index.html").write_text(
        f"<!doctype html><meta charset='utf-8'><title>Quick Tunnel Test</title><h1>{EXPECTED}</h1>",
        encoding="utf-8",
    )

    port = get_free_port()
    handler = functools.partial(QuietHandler, directory=str(tmp))
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    local_url = f"http://127.0.0.1:{port}"
    public_url = None
    proc = None

    try:
        local_body = fetch(local_url)
        if EXPECTED not in local_body:
            print("ERROR: local site did not return expected content", file=sys.stderr)
            return 1

        cmd = [
            "cloudflared",
            "--config",
            str(config),
            "tunnel",
            "--no-autoupdate",
            "--protocol",
            "http2",
            "--url",
            local_url,
        ]
        print("Starting:", " ".join(cmd))
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        deadline = time.time() + TIMEOUT_SECONDS
        lines: list[str] = []
        pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

        public_url = None
        registered = False
        while time.time() < deadline:
            assert proc.stdout is not None
            line = proc.stdout.readline()
            if line:
                lines.append(line.rstrip())
                print(line, end="")
                match = pattern.search(line)
                if match:
                    public_url = match.group(0)
                if "Registered tunnel connection" in line:
                    registered = True
                if public_url and registered:
                    break
            elif proc.poll() is not None:
                print("ERROR: cloudflared exited early", file=sys.stderr)
                print("\n".join(lines[-40:]), file=sys.stderr)
                return 1
            else:
                time.sleep(0.2)

        if not public_url:
            print("ERROR: did not find trycloudflare.com URL in cloudflared output", file=sys.stderr)
            print("\n".join(lines[-40:]), file=sys.stderr)
            return 1
        if not registered:
            print("ERROR: cloudflared did not register an edge connection in time", file=sys.stderr)
            print("\n".join(lines[-40:]), file=sys.stderr)
            return 1

        print(f"Public URL: {public_url}")

        # DNS for a fresh trycloudflare subdomain can take a while to propagate,
        # so keep retrying for a couple of minutes before declaring failure.
        last_error = None
        for attempt in range(1, 16):
            try:
                body = fetch(public_url, timeout=20)
                if EXPECTED in body:
                    print(f"PASS: public URL returned expected content on attempt {attempt}")
                    return 0
                last_error = "expected content not found"
            except Exception as exc:  # noqa: BLE001 - diagnostic script
                last_error = repr(exc)
            time.sleep(5)

        print(f"ERROR: public URL verification failed: {last_error}", file=sys.stderr)
        return 1
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()
        httpd.shutdown()
        httpd.server_close()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

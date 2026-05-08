#!/usr/bin/env python3
"""Small helper for Cloudflare Tunnel agent workflows.

The quick command starts cloudflared in the background, waits for the
trycloudflare URL, and records state under .cloudflare-tunnel/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


STATE_DIR = Path(".cloudflare-tunnel")
PID_FILE = STATE_DIR / "quick.pid"
URL_FILE = STATE_DIR / "quick-url.txt"
LOG_FILE = STATE_DIR / "quick.log"
EMPTY_CONFIG = STATE_DIR / "cloudflared-empty.yml"
DEFAULT_TIMEOUT = 120
URL_PATTERN = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")


def fail(message: str, code: int = 1) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    return code


def print_json(data: dict[str, object]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def require_cloudflared() -> str:
    path = shutil.which("cloudflared")
    if not path:
        raise RuntimeError("cloudflared not found. Install it first.")
    return path


def normalize_url(args: argparse.Namespace) -> str:
    if args.url:
        return args.url
    if args.port:
        return f"http://localhost:{args.port}"
    raise RuntimeError("provide --url or --port")


def fetch(url: str, timeout: int = 15) -> tuple[int | None, str]:
    if shutil.which("curl"):
        result = subprocess.run(
            ["curl", "--noproxy", "*", "-sS", "-L", "--max-time", str(timeout), "-w", "\n%{http_code}", url],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"curl exited {result.returncode}")
        body, _, status_text = result.stdout.rpartition("\n")
        try:
            status = int(status_text)
        except ValueError:
            status = None
        return status, body

    req = Request(url, headers={"User-Agent": "cloudflare-tunnel-skill/2.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except URLError as exc:
        raise RuntimeError(str(exc)) from exc


def verify_local(url: str) -> None:
    status, _ = fetch(url, timeout=10)
    if status is None:
        return
    if status in {200, 204, 301, 302, 304, 401, 403} or 200 <= status < 500:
        return
    raise RuntimeError(f"local service returned HTTP {status}")


def is_pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def read_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def cmd_check(_: argparse.Namespace) -> int:
    try:
        path = require_cloudflared()
        result = subprocess.run([path, "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print_json({"ok": True, "cloudflared": path, "version": result.stdout.strip()})
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI diagnostics
        return fail(str(exc))


def cmd_quick(args: argparse.Namespace) -> int:
    try:
        cloudflared = require_cloudflared()
        local_url = normalize_url(args)
        verify_local(local_url)

        existing_pid = read_pid()
        if existing_pid and is_pid_running(existing_pid) and URL_FILE.exists():
            print_json(
                {
                    "ok": True,
                    "mode": "quick",
                    "reused": True,
                    "pid": existing_pid,
                    "local_url": local_url,
                    "public_url": URL_FILE.read_text(encoding="utf-8").strip(),
                    "log_file": str(LOG_FILE),
                }
            )
            return 0

        STATE_DIR.mkdir(parents=True, exist_ok=True)
        EMPTY_CONFIG.write_text("", encoding="utf-8")
        log = LOG_FILE.open("w", encoding="utf-8")

        cmd = [
            cloudflared,
            "--config",
            str(EMPTY_CONFIG),
            "tunnel",
            "--no-autoupdate",
            "--protocol",
            args.protocol,
        ]
        if args.no_tls_verify:
            cmd.append("--no-tls-verify")
        cmd.extend(["--url", local_url])

        proc = subprocess.Popen(
            cmd,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        PID_FILE.write_text(str(proc.pid), encoding="utf-8")

        public_url = None
        registered = False
        deadline = time.time() + args.timeout
        offset = 0

        while time.time() < deadline:
            if proc.poll() is not None:
                log.close()
                return fail(f"cloudflared exited early with code {proc.returncode}. See {LOG_FILE}")

            if LOG_FILE.exists():
                content = LOG_FILE.read_text(encoding="utf-8", errors="replace")
                if len(content) != offset:
                    new_content = content[offset:]
                    offset = len(content)
                    match = URL_PATTERN.search(new_content) or URL_PATTERN.search(content)
                    if match:
                        public_url = match.group(0)
                    if "Registered tunnel connection" in new_content or "Registered tunnel connection" in content:
                        registered = True
                    if public_url and registered:
                        break
            time.sleep(0.5)

        log.close()

        if not public_url:
            return fail(f"did not find trycloudflare.com URL in {LOG_FILE}")
        if not registered:
            return fail(f"cloudflared did not register an edge connection in time. See {LOG_FILE}")

        URL_FILE.write_text(public_url + "\n", encoding="utf-8")
        print_json(
            {
                "ok": True,
                "mode": "quick",
                "pid": proc.pid,
                "local_url": local_url,
                "public_url": public_url,
                "log_file": str(LOG_FILE),
                "stop_command": "python3 scripts/tunnel_helper.py stop",
            }
        )
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI diagnostics
        return fail(str(exc))


def cmd_status(_: argparse.Namespace) -> int:
    pid = read_pid()
    running = bool(pid and is_pid_running(pid))
    public_url = URL_FILE.read_text(encoding="utf-8").strip() if URL_FILE.exists() else None
    print_json({"ok": True, "mode": "quick", "running": running, "pid": pid, "public_url": public_url})
    return 0


def cmd_stop(_: argparse.Namespace) -> int:
    pid = read_pid()
    if not pid:
        print_json({"ok": True, "stopped": False, "message": "no quick tunnel pid file found"})
        return 0
    if not is_pid_running(pid):
        print_json({"ok": True, "stopped": False, "message": "process is not running", "pid": pid})
        return 0
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except PermissionError:
        os.kill(pid, signal.SIGTERM)
    deadline = time.time() + 8
    while time.time() < deadline:
        if not is_pid_running(pid):
            break
        time.sleep(0.2)
    if is_pid_running(pid):
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except PermissionError:
            os.kill(pid, signal.SIGKILL)
    print_json({"ok": True, "stopped": True, "pid": pid})
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        status, body = fetch(args.url, timeout=args.timeout)
        contains = args.contains in body if args.contains else None
        ok = status is None or 200 <= status < 500
        if args.contains:
            ok = ok and bool(contains)
        print_json({"ok": ok, "url": args.url, "status": status, "contains": contains})
        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001 - CLI diagnostics
        return fail(str(exc))


def safe_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", name).strip("-")


def cmd_named_config(args: argparse.Namespace) -> int:
    try:
        local_url = normalize_url(args)
        name = safe_name(args.name)
        if not name:
            raise RuntimeError("invalid tunnel name")
        if not args.hostname or "." not in args.hostname:
            raise RuntimeError("provide a valid --hostname")
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        config_path = STATE_DIR / f"{name}.yml"
        lines = [
            f"tunnel: {name}",
        ]
        if args.credentials_file:
            lines.append(f"credentials-file: {args.credentials_file}")
        lines.extend(
            [
                "",
                "ingress:",
                f"  - hostname: {args.hostname}",
                f"    service: {local_url}",
                "  - service: http_status:404",
                "",
            ]
        )
        config_path.write_text("\n".join(lines), encoding="utf-8")
        print_json(
            {
                "ok": True,
                "mode": "named",
                "config": str(config_path),
                "hostname": args.hostname,
                "local_url": local_url,
                "run_command": f"cloudflared tunnel --config {config_path} run {name}",
            }
        )
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI diagnostics
        return fail(str(exc))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cloudflare Tunnel skill helper")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="check cloudflared")
    check.set_defaults(func=cmd_check)

    quick = sub.add_parser("quick", help="start a quick tunnel in the background")
    quick.add_argument("--url", help="local URL, for example http://localhost:3000")
    quick.add_argument("--port", type=int, help="local HTTP port")
    quick.add_argument("--protocol", default="http2", choices=["http2", "quic"], help="cloudflared protocol")
    quick.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    quick.add_argument("--no-tls-verify", action="store_true", help="allow self-signed local HTTPS")
    quick.set_defaults(func=cmd_quick)

    status = sub.add_parser("status", help="show quick tunnel status")
    status.set_defaults(func=cmd_status)

    stop = sub.add_parser("stop", help="stop helper-started quick tunnel")
    stop.set_defaults(func=cmd_stop)

    verify = sub.add_parser("verify", help="verify a public URL")
    verify.add_argument("--url", required=True)
    verify.add_argument("--contains", help="optional response substring to require")
    verify.add_argument("--timeout", type=int, default=20)
    verify.set_defaults(func=cmd_verify)

    named = sub.add_parser("named-config", help="write a named tunnel config")
    named.add_argument("--name", required=True, help="tunnel name")
    named.add_argument("--hostname", required=True, help="public hostname")
    named.add_argument("--url", help="local URL")
    named.add_argument("--port", type=int, help="local HTTP port")
    named.add_argument("--credentials-file", help="optional Cloudflare tunnel credentials JSON")
    named.set_defaults(func=cmd_named_config)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

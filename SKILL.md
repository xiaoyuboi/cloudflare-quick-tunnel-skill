---
name: cloudflare-tunnel
description: Use when a user wants to expose a local HTTP/HTTPS service to the public internet with Cloudflare Tunnel. Supports temporary Quick Tunnel URLs for previews and named tunnels with fixed custom domains for stable public mapping.
license: MIT
metadata:
  tags: [cloudflare, tunnel, cloudflared, localhost, public-url, preview, custom-domain]
---

# Cloudflare Tunnel Agent Workflow

Help the user expose a local service through Cloudflare Tunnel. Choose the safest working mode:

- **Quick mode**: temporary `https://*.trycloudflare.com` URL. Use for demos, previews, classroom sharing, and short-lived testing.
- **Named mode**: fixed hostname such as `app.example.com`. Use when the user owns a Cloudflare-managed domain and needs a stable public URL.

Before running commands, identify:

1. Local service URL, usually `http://localhost:<port>` or `https://localhost:<port>`.
2. Exposure mode: quick or named.
3. Whether the service contains admin panels, tokens, private data, internal systems, or unauthenticated write APIs.

If the service is sensitive, pause and warn the user before exposing it. See `references/security.md`.

## Paths and State

All `scripts/...` and `references/...` paths in this document are relative to this skill's install directory, not the user's project. When the working directory is the user's project, call the helper with its full installed path, for example:

```bash
python3 ~/.claude/skills/cloudflare-tunnel/scripts/tunnel_helper.py quick --url http://localhost:3000
```

The helper writes runtime state to `.cloudflare-tunnel/` inside the current working directory, so run `status` and `stop` from the same directory where `quick` was started. If that directory is a git repository, make sure `.cloudflare-tunnel/` is in its `.gitignore` before committing.

## Mode Selection

Use **quick mode** when:

- The user says temporary, demo, preview, share localhost, quick public link, or no domain.
- The URL may change after restart.
- The user does not need Cloudflare login.

Use **named mode** when:

- The user asks for a fixed domain, stable public URL, webhook endpoint, or long-lived mapping.
- The user has a Cloudflare account and a domain whose DNS is managed by Cloudflare.
- The hostname should survive process restarts.

If unclear, default to quick mode for non-sensitive demos and ask only when exposing a sensitive service or creating a fixed hostname.

## Required Checks

Check `cloudflared`:

```bash
cloudflared --version
```

Verify the local service before creating a tunnel:

```bash
curl -I http://localhost:<PORT>
```

Treat `200`, `301`, `302`, `304`, `401`, and `403` as evidence that the service is reachable. Investigate connection failures before starting a tunnel.

## Quick Mode

Read `references/quick-tunnel.md` when the user wants a temporary public URL.

Preferred helper:

```bash
python3 scripts/tunnel_helper.py quick --url http://localhost:<PORT>
```

The helper starts `cloudflared` in the background, waits for a `trycloudflare.com` URL, writes state under `.cloudflare-tunnel/`, and prints JSON with the public URL.

Helper behavior worth knowing:

- If a quick tunnel for the **same** local URL is already running, it is reused (`"reused": true`). A running tunnel for a **different** local URL is stopped and replaced.
- Transient `api.trycloudflare.com` failures are retried up to 3 times automatically.
- `verify` falls back to DNS-over-HTTPS when the system resolver cannot resolve a fresh `trycloudflare.com` hostname (common behind fake-IP proxy DNS). DNS propagation can take one or two minutes; retry `verify` before treating the tunnel as broken.

Manual fallback:

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:<PORT>
```

Wait for both:

- `https://*.trycloudflare.com` in the output
- at least one `Registered tunnel connection` log line

Then verify:

```bash
python3 scripts/tunnel_helper.py verify --url https://xxxx.trycloudflare.com
```

Stop a helper-started tunnel:

```bash
python3 scripts/tunnel_helper.py stop
```

## Named Mode

Read `references/named-tunnel.md` when the user wants a fixed domain.

Typical locally-managed CLI flow:

```bash
cloudflared tunnel login
cloudflared tunnel create <TUNNEL_NAME>
cloudflared tunnel route dns <TUNNEL_NAME> <HOSTNAME>
```

Create a config:

```bash
python3 scripts/tunnel_helper.py named-config \
  --name <TUNNEL_NAME> \
  --hostname <HOSTNAME> \
  --url http://localhost:<PORT>
```

Run:

```bash
cloudflared tunnel --config .cloudflare-tunnel/<TUNNEL_NAME>.yml run <TUNNEL_NAME>
```

Named mode may require an interactive browser login. Do not paste, print, commit, or store Cloudflare tokens outside the user's local Cloudflare config.

## Output

After success, return:

- Public URL
- Local URL
- Mode used
- How to stop the tunnel
- A short temporary/stability warning for quick mode

Example:

```text
Public URL: https://xxxx.trycloudflare.com
Local URL: http://localhost:3000
Mode: quick
Stop: python3 scripts/tunnel_helper.py stop

This is a temporary Quick Tunnel URL. It stops working if cloudflared exits, the computer sleeps, or the network disconnects.
```

## Troubleshooting

Use `references/troubleshooting.md` for:

- no public URL in logs
- 404 from the tunnel
- 502 / Bad Gateway
- self-signed local HTTPS
- phone cannot open the link
- named tunnel DNS or login failures

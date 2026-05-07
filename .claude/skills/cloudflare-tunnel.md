# Cloudflare Tunnel

Use this skill when the user wants to expose, publish, share, preview, or map a local HTTP/HTTPS service to the public internet with Cloudflare Tunnel.

支持两种模式：

- Quick Tunnel: temporary `https://*.trycloudflare.com` URL.
- Named Tunnel: fixed custom hostname such as `app.example.com`.

## Required Workflow

1. Identify the local URL, for example `http://localhost:3000`.
2. Check whether the user needs a temporary URL or a fixed hostname.
3. Check for sensitive data, admin panels, tokens, or internal systems before exposing.
4. Verify the local service works.
5. Start the tunnel.
6. Extract and verify the public URL.
7. Return the URL, mode, local URL, stop command, and relevant warning.

## Quick Tunnel

Use for temporary demos and previews.

```bash
python3 scripts/tunnel_helper.py quick --url http://localhost:<PORT>
```

Manual fallback:

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:<PORT>
```

Wait for:

- `https://*.trycloudflare.com`
- `Registered tunnel connection`

Verify:

```bash
python3 scripts/tunnel_helper.py verify --url https://xxxx.trycloudflare.com
```

Stop:

```bash
python3 scripts/tunnel_helper.py stop
```

## Named Tunnel

Use for fixed hostnames and stable public mapping.

Prerequisites:

- Cloudflare account
- Cloudflare-managed DNS zone
- `cloudflared`

Flow:

```bash
cloudflared tunnel login
cloudflared tunnel create <TUNNEL_NAME>
cloudflared tunnel route dns <TUNNEL_NAME> <HOSTNAME>
python3 scripts/tunnel_helper.py named-config --name <TUNNEL_NAME> --hostname <HOSTNAME> --url http://localhost:<PORT>
cloudflared tunnel --config .cloudflare-tunnel/<TUNNEL_NAME>.yml run <TUNNEL_NAME>
```

Do not print, commit, or store Cloudflare tunnel tokens in repo files.

## Safety

Ask before exposing sensitive services:

- admin dashboards
- tokens, cookies, API keys
- internal systems
- database or debug consoles
- unauthenticated write APIs

For sensitive fixed-hostname services, recommend application login or Cloudflare Access.

## Final Response Template

```text
Public URL: https://xxxx.trycloudflare.com
Local URL: http://localhost:<PORT>
Mode: quick
Stop: python3 scripts/tunnel_helper.py stop

This Quick Tunnel URL is temporary. It stops working if cloudflared exits, the computer sleeps, or the network disconnects.
```

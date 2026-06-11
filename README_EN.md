# Cloudflare Tunnel Skill

An agent workflow skill for exposing local HTTP/HTTPS services through Cloudflare Tunnel.

It supports two modes:

- **Quick Tunnel**: temporary `https://*.trycloudflare.com` preview URLs for demos and short-lived sharing.
- **Named Tunnel**: fixed custom hostnames such as `app.example.com -> http://localhost:3000`.

## Use Cases

- Share `localhost:3000` with someone else.
- Create a temporary public URL for a local API.
- Map a fixed domain to a local development service.
- Provide webhook endpoints for GitHub, Slack, Stripe, n8n, and similar tools.
- Let an agent check the local service, start a tunnel, extract the public URL, and verify it.

## Avoid For

- Sensitive admin panels without authentication.
- Raw databases, Redis, Docker API, or private network services.
- Public file hosting or large downloads.
- Production services that cannot tolerate local machine sleep, process exits, or network loss.

## Install

> Claude Code only discovers skills laid out as `.claude/skills/<name>/SKILL.md` (a directory containing `SKILL.md`), and the helper script must be installed alongside it — always copy `SKILL.md` + `scripts/` + `references/` together.

Claude Code global install (recommended, available in all projects):

```bash
git clone https://github.com/xiaoyuboi/cloudflare-tunnel-skill /tmp/cloudflare-tunnel-skill
mkdir -p ~/.claude/skills/cloudflare-tunnel
cp /tmp/cloudflare-tunnel-skill/SKILL.md ~/.claude/skills/cloudflare-tunnel/
cp -R /tmp/cloudflare-tunnel-skill/scripts /tmp/cloudflare-tunnel-skill/references ~/.claude/skills/cloudflare-tunnel/
rm -rf /tmp/cloudflare-tunnel-skill
```

Claude Code project-level install (current project only): same as above, but copy into `.claude/skills/cloudflare-tunnel/` inside the project.

Codex install: same as above, but copy into `~/.codex/skills/cloudflare-tunnel/`.

> Requirements: `cloudflared` (see `references/troubleshooting.md` for install commands) and Python 3. The helper script is fully tested on macOS / Linux; Windows support is best-effort (process management uses `tasklist`/`taskkill`) — prefer WSL or the manual fallback commands on Windows.

## Quick Tunnel

```bash
python3 scripts/tunnel_helper.py quick --url http://localhost:3000
```

Status:

```bash
python3 scripts/tunnel_helper.py status
```

Stop:

```bash
python3 scripts/tunnel_helper.py stop
```

Manual fallback:

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

## Named Tunnel

Prerequisites:

- `cloudflared` is installed.
- You have a Cloudflare account.
- The domain is managed by Cloudflare DNS.

Flow:

```bash
cloudflared tunnel login
cloudflared tunnel create my-app
cloudflared tunnel route dns my-app app.example.com
python3 scripts/tunnel_helper.py named-config --name my-app --hostname app.example.com --url http://localhost:3000
cloudflared tunnel --config .cloudflare-tunnel/my-app.yml run my-app
```

## Test

```bash
python3 -m py_compile scripts/tunnel_helper.py scripts/test_quick_tunnel.py
python3 scripts/tunnel_helper.py --help
```

End-to-end Quick Tunnel test:

```bash
python3 scripts/test_quick_tunnel.py
```

## Security

Cloudflare Tunnel exposes your local service to the public internet. Before sharing a URL, make sure it does not expose tokens, cookies, API keys, private data, internal systems, unauthenticated admin panels, or unsafe write APIs.

Use application authentication or Cloudflare Access for sensitive services.

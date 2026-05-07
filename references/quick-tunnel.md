# Quick Tunnel

Quick Tunnel creates a temporary public URL under `trycloudflare.com` for a local HTTP/HTTPS service.

Use it for:

- local app previews
- demos and classroom sharing
- short-lived client review
- testing webhooks when a stable domain is not required

Avoid it for:

- production traffic
- fixed callback URLs
- large file distribution
- services that require guaranteed uptime
- streaming features that depend on Server-Sent Events (SSE)

## Recommended Flow

1. Find the local service URL.
2. Verify it locally.
3. Start the tunnel with HTTP/2 and an empty config.
4. Wait for the public URL and registered edge connection.
5. Verify the public URL.
6. Tell the user it is temporary.

## Helper Command

```bash
python3 scripts/tunnel_helper.py quick --url http://localhost:<PORT>
```

Useful options:

```bash
python3 scripts/tunnel_helper.py quick --port 3000
python3 scripts/tunnel_helper.py quick --url https://localhost:8443 --no-tls-verify
python3 scripts/tunnel_helper.py status
python3 scripts/tunnel_helper.py stop
```

The helper writes runtime files to `.cloudflare-tunnel/`:

- `quick.pid`
- `quick.log`
- `quick-url.txt`
- `cloudflared-empty.yml`

## Manual Command

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:<PORT>
```

For self-signed local HTTPS:

```bash
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --no-tls-verify --url https://localhost:8443
```

## Verification

```bash
curl --noproxy '*' -sS -L --max-time 20 https://xxxx.trycloudflare.com
```

The body should contain recognizable local app content. If the service returns JSON, verify a known endpoint such as `/health`.

## Notes

Quick Tunnel URLs are ephemeral. The URL changes when the process restarts, and it stops working when the machine sleeps, the network disconnects, or `cloudflared` exits.

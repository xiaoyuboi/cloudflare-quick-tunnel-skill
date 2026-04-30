# Cloudflare Quick Tunnel Demo

When the user asks to expose, publish, deploy, share, or preview a local project on the public internet temporarily, use Cloudflare Quick Tunnel.

Trigger examples:
- “把本地项目部署到公网给别人看”
- “localhost 怎么发给别人访问”
- “帮我把本地某某项目公网预览”
- “临时生成一个公网链接”
- “用 Cloudflare Quick Tunnel 展示这个项目”

Do not use this for long-term production deployment, fixed custom domains, large file distribution, public download sites, or sensitive admin panels without authentication.

## Goal

Turn a local URL like:

```text
http://localhost:3000
```

into a temporary public URL like:

```text
https://xxxx.trycloudflare.com
```

## Required workflow

1. Identify the local project path and local port.
2. Start the local project if it is not running.
3. Verify the local URL works.
4. Start Cloudflare Quick Tunnel with the stable HTTP/2 command.
5. Extract the `https://xxxx.trycloudflare.com` URL from terminal output.
6. Verify the public URL returns the local project content.
7. Return the public URL to the user and warn that it is temporary.

## Commands

Check cloudflared:

```bash
cloudflared --version
```

Install if missing:

macOS:

```bash
brew install cloudflared
```

Windows:

```powershell
winget install --id Cloudflare.cloudflared
```

Linux:

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/cloudflared
```

Verify the local service:

```bash
curl -I http://localhost:<PORT>
```

Start a stable Quick Tunnel:

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:<PORT>
```

If running via an agent, start it as a background process and watch for `trycloudflare.com`.

## Important stability notes

- Prefer `--protocol http2`; default QUIC can fail on some networks.
- Use an empty config file to avoid existing `~/.cloudflared/config.yml` interfering and causing unexpected 404s.
- Wait until logs show `Registered tunnel connection` before declaring success.
- The first public URL may take a few seconds to resolve; retry verification several times.

## Verification

After extracting the public URL:

```bash
curl --noproxy '*' -sS -L --max-time 20 https://xxxx.trycloudflare.com
```

The response should contain recognizable content from the local project.

## Final response template

```text
已部署到公网：
https://xxxx.trycloudflare.com

本地地址：
http://localhost:<PORT>

注意：这是 Cloudflare Quick Tunnel 临时链接。终端进程关闭、电脑睡眠或断网后，链接会失效；长期稳定服务要用正式 Cloudflare Tunnel。
```

## Safety warning

Before exposing a project, check whether it contains private data, tokens, admin panels, debug pages, or internal systems. If it does, ask the user before exposing it or add authentication first.

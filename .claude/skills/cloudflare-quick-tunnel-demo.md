# Cloudflare Quick Tunnel Demo / 本地项目公网展示

When the user asks to expose, publish, deploy, share, or preview a local project on the public internet temporarily, use Cloudflare Quick Tunnel.

当用户想把本地项目临时发布到公网、生成预览链接、把 localhost 发给别人访问时，使用 Cloudflare Quick Tunnel。

Trigger examples / 触发示例：

- “把本地项目部署到公网给别人看”
- “localhost 怎么发给别人访问”
- “帮我把本地某某项目公网预览”
- “临时生成一个公网链接”
- “用 Cloudflare Quick Tunnel 展示这个项目”
- “Expose this local project to the public internet”
- “Share my localhost app with someone”
- “Generate a temporary public preview URL”

Do not use this for long-term production deployment, fixed custom domains, large file distribution, public download sites, or sensitive admin panels without authentication.

不要用于长期生产部署、固定自定义域名、大文件分发、公开下载站，或没有认证保护的敏感后台。

## Goal / 目标

Turn a local URL like / 把本地地址：

```text
http://localhost:3000
```

into a temporary public URL like / 变成临时公网地址：

```text
https://xxxx.trycloudflare.com
```

## Required workflow / 必须执行的流程

1. Identify the local project path and local port.  
   确认本地项目目录和端口。
2. Start the local project if it is not running.  
   如果项目没启动，先启动本地项目。
3. Verify the local URL works.  
   验证本地 URL 可访问。
4. Start Cloudflare Quick Tunnel with the stable HTTP/2 command.  
   用稳定的 HTTP/2 命令启动 Quick Tunnel。
5. Extract the `https://xxxx.trycloudflare.com` URL from terminal output.  
   从终端输出中提取公网链接。
6. Verify the public URL returns the local project content.  
   验证公网链接能返回本地项目内容。
7. Return the public URL to the user and warn that it is temporary.  
   把公网链接发给用户，并提醒这是临时链接。

## Commands / 命令

Check cloudflared / 检查 cloudflared：

```bash
cloudflared --version
```

Install if missing / 如果没有安装：

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

Verify the local service / 验证本地服务：

```bash
curl -I http://localhost:<PORT>
```

Start a stable Quick Tunnel / 启动稳定版 Quick Tunnel：

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:<PORT>
```

If running via an agent, start it as a background process and watch for `trycloudflare.com`.

如果由 Agent 执行，应作为后台进程启动，并监听 `trycloudflare.com` 输出。

## Important stability notes / 稳定性注意事项

- Prefer `--protocol http2`; default QUIC can fail on some networks.  
  优先使用 `--protocol http2`；默认 QUIC 在部分网络下可能不稳定。
- Use an empty config file to avoid existing `~/.cloudflared/config.yml` interfering and causing unexpected 404s.  
  使用空配置文件，避免已有 `~/.cloudflared/config.yml` 干扰并导致 404。
- Wait until logs show `Registered tunnel connection` before declaring success.  
  等日志出现 `Registered tunnel connection` 后再宣布成功。
- The first public URL may take a few seconds to resolve; retry verification several times.  
  公网链接刚生成时可能需要几秒生效，应重试验证。

## Verification / 验证

After extracting the public URL / 拿到公网链接后：

```bash
curl --noproxy '*' -sS -L --max-time 20 https://xxxx.trycloudflare.com
```

The response should contain recognizable content from the local project.

返回内容应包含本地项目中的可识别内容。

## Final response template / 最终回复模板

Chinese / 中文：

```text
已部署到公网：
https://xxxx.trycloudflare.com

本地地址：
http://localhost:<PORT>

注意：这是 Cloudflare Quick Tunnel 临时链接。终端进程关闭、电脑睡眠或断网后，链接会失效；长期稳定服务要用正式 Cloudflare Tunnel。
```

English:

```text
Public preview URL:
https://xxxx.trycloudflare.com

Local URL:
http://localhost:<PORT>

Note: This is a temporary Cloudflare Quick Tunnel URL. It will stop working if the terminal process exits, the computer sleeps, or the network disconnects. For long-term stable hosting, use a named Cloudflare Tunnel.
```

## Safety warning / 安全提醒

Before exposing a project, check whether it contains private data, tokens, admin panels, debug pages, or internal systems. If it does, ask the user before exposing it or add authentication first.

发布到公网前，先检查项目是否包含隐私数据、Token、后台管理页、调试页面或内网系统。如果有，先询问用户或添加认证保护。

---
name: cloudflare-quick-tunnel-demo
description: Use when a beginner wants to quickly publish a local web project to a temporary public URL for demos, client previews, classroom sharing, or video demonstrations using Cloudflare Quick Tunnel.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cloudflare, quick-tunnel, localhost, public-demo, beginner, deployment]
    related_skills: [docker-cloudflared-quickstart]
---

# Cloudflare Quick Tunnel 本地项目公网展示

## Overview

这个 Skill 用来帮助小白把本地正在运行的项目，快速变成一个公网可访问链接。

适合场景：你本地有一个网页、API、Demo、AI 小工具，地址类似：

```text
http://localhost:3000
http://127.0.0.1:8080
```

你想临时发给朋友、客户、老师、同事看，但不想买服务器、不想部署、不想配置域名、不想做端口转发。Cloudflare Quick Tunnel 可以一行命令生成一个临时公网地址：

```text
https://xxxx.trycloudflare.com
```

## When to Use

使用这个 Skill：

- 用户说“把本地项目临时发给别人看”
- 用户说“localhost 怎么给别人访问”
- 用户说“快速部署到公网演示一下”
- 用户说“做一个临时公网链接”
- 用户要录视频演示 Quick Tunnel
- 用户不懂服务器、域名、Nginx、反向代理

不要用这个 Skill：

- 用户要长期稳定生产环境部署：用正式 Cloudflare Tunnel / VPS / Docker 部署
- 用户要大文件分发、公开网盘、视频下载站：Quick Tunnel 不适合
- 用户要绑定自己的固定域名：用 Named Cloudflare Tunnel
- 用户项目涉及敏感后台、私密数据：先加登录或 Access 保护

## Core Idea

Quick Tunnel 做的事很简单：

```text
本地服务 http://localhost:3000
        ↓
cloudflared tunnel --url http://localhost:3000
        ↓
临时公网链接 https://xxxx.trycloudflare.com
        ↓
别人打开链接，访问到你的本地项目
```

本地程序仍然跑在你的电脑上。公网链接只是 Cloudflare 帮你临时打了一条隧道。

## Prerequisites

### 1. 本地项目已经能打开

先确认本地项目可以访问。

例如：

```bash
curl -I http://localhost:3000
```

应该看到类似：

```text
HTTP/1.1 200 OK
```

如果本地都打不开，Quick Tunnel 也没法帮你变公网。

### 2. 安装 cloudflared

macOS：

```bash
brew install cloudflared
```

Windows：

```powershell
winget install --id Cloudflare.cloudflared
```

Linux：

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/cloudflared
```

验证：

```bash
cloudflared --version
```

## Quick Start

假设你的本地项目在：

```text
http://localhost:3000
```

执行：

```bash
cloudflared tunnel --url http://localhost:3000
```

等待终端输出：

```text
Your quick Tunnel has been created! Visit it at:
https://xxxx.trycloudflare.com
```

把这个 `https://xxxx.trycloudflare.com` 发给别人，对方就能访问你的本地项目。

## More Stable Command

有些网络环境下，默认 QUIC 协议可能连接不稳定。优先使用 HTTP/2：

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

如果这台机器已经有 `~/.cloudflared/config.yml`，可能会干扰 Quick Tunnel。可以指定一个空配置文件：

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

这是本 Skill 推荐的稳定命令。

## Beginner Workflow

### Step 1：启动本地项目

例如前端项目：

```bash
npm install
npm run dev
```

常见本地地址：

```text
http://localhost:3000
http://localhost:5173
http://localhost:8080
```

### Step 2：确认本地能访问

```bash
curl -I http://localhost:3000
```

看到 `200`、`301`、`302`、`304` 都通常说明服务在线。

### Step 3：启动 Quick Tunnel

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

### Step 4：复制公网链接

终端会出现：

```text
https://xxxx.trycloudflare.com
```

复制给别人。

### Step 5：验证公网访问

```bash
curl -I https://xxxx.trycloudflare.com
```

或者直接用浏览器打开。

## Demo Recipe: 表白网站

这是视频教学里最容易理解的演示场景。

### 创建一个本地网页

```bash
mkdir -p quick-tunnel-love-site
cd quick-tunnel-love-site
cat > index.html <<'HTML'
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>我喜欢你</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
      color: white;
      background: linear-gradient(135deg, #ff8fb3, #8e7dff, #ffd36e);
      overflow: hidden;
    }
    .card {
      width: min(680px, 90vw);
      padding: 56px 32px;
      text-align: center;
      border-radius: 32px;
      background: rgba(255,255,255,.18);
      border: 1px solid rgba(255,255,255,.35);
      box-shadow: 0 30px 90px rgba(94,37,91,.28);
      backdrop-filter: blur(20px);
    }
    h1 { font-size: clamp(48px, 9vw, 88px); margin: 0 0 18px; }
    p { font-size: 22px; line-height: 1.7; }
    button {
      border: 0;
      border-radius: 16px;
      padding: 14px 22px;
      font-weight: 800;
      color: #7f3769;
      background: white;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>我喜欢你</h1>
    <p>这个页面原本只在我的电脑里，<br>现在通过 Cloudflare Quick Tunnel 发到了公网。</p>
    <button onclick="alert('那我们就是双向奔赴啦 ❤️')">我也喜欢你</button>
  </div>
</body>
</html>
HTML
```

### 启动本地网页服务

```bash
python3 -m http.server 3000
```

本地访问：

```text
http://localhost:3000
```

### 另开一个终端启动 Quick Tunnel

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

复制输出的：

```text
https://xxxx.trycloudflare.com
```

发给别人即可。

## Common Local Ports

| 项目类型 | 常见地址 |
|---|---|
| Vite / Vue / React | `http://localhost:5173` |
| Next.js | `http://localhost:3000` |
| Nuxt | `http://localhost:3000` |
| Python http.server | `http://localhost:8000` 或 `3000` |
| Flask | `http://localhost:5000` |
| FastAPI | `http://localhost:8000` |
| n8n | `http://localhost:5678` |
| Stable Diffusion WebUI | `http://localhost:7860` |
| Teldrive | `http://localhost:8080` |

## Troubleshooting

### 1. 终端没有出现 trycloudflare.com 链接

可能原因：网络连接 Cloudflare 边缘节点慢。

解决：

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

### 2. 访问公网链接是 404

常见原因：本机已经有 Cloudflare 配置文件干扰 Quick Tunnel。

解决：

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

### 3. 公网链接打开 502 / Bad Gateway

说明 Cloudflare 连到了你的电脑，但你的本地服务没响应。

检查：

```bash
curl -I http://localhost:3000
```

如果本地失败，先启动本地项目。

### 4. 本地是 HTTPS 服务

如果本地服务是自签名 HTTPS，可能需要：

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --no-tls-verify --url https://localhost:8443
```

### 5. 终端关了，链接不能访问

正常。Quick Tunnel 是临时隧道，进程一停，链接就失效。

### 6. 电脑睡眠/断网，链接不能访问

正常。本地电脑就是服务器，电脑睡了服务就没了。

### 7. 手机打不开，但电脑能打开

先确认手机访问的是公网链接，不是 `localhost`。

正确：

```text
https://xxxx.trycloudflare.com
```

错误：

```text
http://localhost:3000
```

## Security Notes

Quick Tunnel 会把本地服务暴露到公网。发链接前先确认：

- 不要暴露后台管理系统，除非有登录
- 不要暴露含有密钥、Cookie、Token 的调试页面
- 不要暴露公司内网系统
- 不要把 Quick Tunnel 当公开网盘或大文件下载站
- 演示结束后，按 `Ctrl + C` 关闭 tunnel

## Video Script Phrases

可以这样对观众解释：

> “localhost 本来只有我自己能打开。现在我只需要一行命令，Cloudflare 就会给我一个临时公网链接。”

> “这不是把代码部署到了服务器，而是 Cloudflare 给我的电脑打了一条临时隧道。”

> “Quick Tunnel 适合临时演示。正式长期使用，应该用 Cloudflare Tunnel 绑定自己的域名。”

## Verification Checklist

- [ ] 本地项目能通过 `http://localhost:<port>` 打开
- [ ] `cloudflared --version` 可用
- [ ] 终端输出了 `https://xxxx.trycloudflare.com`
- [ ] 公网链接浏览器能打开
- [ ] 用手机流量访问公网链接也能打开
- [ ] 演示结束后关闭 tunnel 进程

## Recommended Command Template

把 `<PORT>` 换成你的本地端口：

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:<PORT>
```

示例：

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

# Cloudflare Quick Tunnel Demo Skill

[中文](#中文) | [English](#english)

---

## 中文

一个给小白用的 Skill：把本地正在运行的网页/API/Demo 快速变成公网临时链接，方便发给朋友、客户、老师、同事预览。

### 适合场景

- 本地网页想临时发给别人看
- localhost 项目需要公网访问
- 视频里演示 Cloudflare Quick Tunnel
- 不想买服务器、不想部署、不想配域名

### 一行命令

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

更稳定版本：

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

### 安装到 Hermes

把本仓库 clone 到本地后，将 `SKILL.md` 放入你的 Hermes skills 目录，例如：

```bash
mkdir -p ~/.hermes/skills/devops/cloudflare-quick-tunnel-demo
cp SKILL.md ~/.hermes/skills/devops/cloudflare-quick-tunnel-demo/SKILL.md
```

新会话中即可通过 skill 名称使用：

```text
cloudflare-quick-tunnel-demo
```

### 安装到 Claude Code

Claude Code 可以使用这个 Skill，但不能直接“从 GitHub 自动调用”。需要把 `.claude/skills/cloudflare-quick-tunnel-demo.md` 放到项目或用户级 Claude skills 目录。

#### 方式 A：只给某个项目使用

在你的项目根目录执行：

```bash
mkdir -p .claude/skills
curl -L https://raw.githubusercontent.com/xiaoyuboi/cloudflare-quick-tunnel-skill/main/.claude/skills/cloudflare-quick-tunnel-demo.md \
  -o .claude/skills/cloudflare-quick-tunnel-demo.md
```

然后在 Claude Code 里说：

```text
利用 cloudflare-quick-tunnel-demo 这个 skill，帮我把当前本地项目部署到公网给别人预览。
```

#### 方式 B：全局使用

```bash
mkdir -p ~/.claude/skills
curl -L https://raw.githubusercontent.com/xiaoyuboi/cloudflare-quick-tunnel-skill/main/.claude/skills/cloudflare-quick-tunnel-demo.md \
  -o ~/.claude/skills/cloudflare-quick-tunnel-demo.md
```

以后任何项目里都可以对 Claude Code 说：

```text
帮我把这个本地项目用 Cloudflare Quick Tunnel 临时发布到公网。
```

### 本地测试

```bash
python3 scripts/test_quick_tunnel.py
```

测试会：

1. 创建一个临时本地网页
2. 启动本地 HTTP 服务
3. 启动 Cloudflare Quick Tunnel
4. 提取 `trycloudflare.com` 公网链接
5. 用 curl 访问公网链接验证页面内容
6. 自动清理进程

### 注意

Quick Tunnel 是临时链接。终端关闭、电脑睡眠、网络断开后，公网链接会失效。

不要把它当长期生产环境、公开网盘、大文件下载站。长期服务请用正式 Cloudflare Tunnel。

---

## English

A beginner-friendly skill for turning a local web app/API/demo into a temporary public URL, so you can share it with friends, clients, teachers, or teammates without buying a server or configuring a domain.

### Use cases

- Share a local website with someone else
- Make a localhost project publicly accessible for preview
- Demonstrate Cloudflare Quick Tunnel in a video
- Avoid server purchase, deployment, custom domain, or router port forwarding

### One command

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

More stable version:

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

### Install for Hermes

Clone this repository and copy `SKILL.md` into your Hermes skills directory:

```bash
mkdir -p ~/.hermes/skills/devops/cloudflare-quick-tunnel-demo
cp SKILL.md ~/.hermes/skills/devops/cloudflare-quick-tunnel-demo/SKILL.md
```

Then use the skill name in a new session:

```text
cloudflare-quick-tunnel-demo
```

### Install for Claude Code

Claude Code can use this skill, but it will not automatically load it directly from GitHub. You need to place `.claude/skills/cloudflare-quick-tunnel-demo.md` in either a project-level or user-level Claude skills directory.

#### Option A: Project-level installation

Run this in your project root:

```bash
mkdir -p .claude/skills
curl -L https://raw.githubusercontent.com/xiaoyuboi/cloudflare-quick-tunnel-skill/main/.claude/skills/cloudflare-quick-tunnel-demo.md \
  -o .claude/skills/cloudflare-quick-tunnel-demo.md
```

Then tell Claude Code:

```text
Use the cloudflare-quick-tunnel-demo skill to expose the current local project to the public internet for preview.
```

#### Option B: Global installation

```bash
mkdir -p ~/.claude/skills
curl -L https://raw.githubusercontent.com/xiaoyuboi/cloudflare-quick-tunnel-skill/main/.claude/skills/cloudflare-quick-tunnel-demo.md \
  -o ~/.claude/skills/cloudflare-quick-tunnel-demo.md
```

After that, in any project you can ask Claude Code:

```text
Expose this local project with Cloudflare Quick Tunnel and give me a temporary public URL.
```

### Local test

```bash
python3 scripts/test_quick_tunnel.py
```

The test will:

1. Create a temporary local web page
2. Start a local HTTP server
3. Start Cloudflare Quick Tunnel
4. Extract the `trycloudflare.com` public URL
5. Verify the public URL with curl
6. Clean up all processes automatically

### Notes

Quick Tunnel URLs are temporary. If the terminal process stops, the computer sleeps, or the network disconnects, the public URL stops working.

Do not use Quick Tunnel as a long-term production deployment, public file-sharing service, or large-download site. Use a named Cloudflare Tunnel for stable long-term services.

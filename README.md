# Cloudflare Quick Tunnel Demo Skill

一个给小白用的 Hermes Skill：把本地正在运行的网页/API/Demo 快速变成公网临时链接，方便发给朋友、客户、老师、同事预览。

## 适合场景

- 本地网页想临时发给别人看
- localhost 项目需要公网访问
- 视频里演示 Cloudflare Quick Tunnel
- 不想买服务器、不想部署、不想配域名

## 一行命令

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

更稳定版本：

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

## 安装到 Hermes

把本仓库 clone 到本地后，将 `SKILL.md` 放入你的 Hermes skills 目录，例如：

```bash
mkdir -p ~/.hermes/skills/devops/cloudflare-quick-tunnel-demo
cp SKILL.md ~/.hermes/skills/devops/cloudflare-quick-tunnel-demo/SKILL.md
```

新会话中即可通过 skill 名称使用：

```text
cloudflare-quick-tunnel-demo
```

## 安装到 Claude Code

Claude Code 可以使用这个 Skill，但不能直接“从 GitHub 自动调用”。需要把 `.claude/skills/cloudflare-quick-tunnel-demo.md` 放到项目或用户级 Claude skills 目录。

### 方式 A：只给某个项目使用

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

### 方式 B：全局使用

```bash
mkdir -p ~/.claude/skills
curl -L https://raw.githubusercontent.com/xiaoyuboi/cloudflare-quick-tunnel-skill/main/.claude/skills/cloudflare-quick-tunnel-demo.md \
  -o ~/.claude/skills/cloudflare-quick-tunnel-demo.md
```

以后任何项目里都可以对 Claude Code 说：

```text
帮我把这个本地项目用 Cloudflare Quick Tunnel 临时发布到公网。
```

## 本地测试

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

## 注意

Quick Tunnel 是临时链接。终端关闭、电脑睡眠、网络断开后，公网链接会失效。

不要把它当长期生产环境、公开网盘、大文件下载站。长期服务请用正式 Cloudflare Tunnel。 

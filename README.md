# Cloudflare Tunnel Skill

[中文](#中文) | [English](README_EN.md)

---

## 中文

一个给 Agent 使用的 Cloudflare Tunnel workflow skill。它可以把本地 HTTP/HTTPS 服务暴露到公网，支持两种模式：

- **Quick Tunnel**：临时 `https://*.trycloudflare.com` 预览链接，适合 demo、课堂、客户临时预览。
- **Named Tunnel**：固定域名映射，例如 `app.example.com -> http://localhost:3000`，适合 webhook、长期预览、团队测试入口。

## 适合场景

- 把 `localhost:3000` 临时发给别人看
- 给本地 API 创建临时公网 URL
- 用固定域名访问本地开发服务
- 给 GitHub、Slack、Stripe、n8n 等 webhook 配一个公网入口
- 让 Agent 自动检查本地服务、启动 tunnel、验证公网 URL

## 不适合场景

- 没有认证保护的敏感后台
- 数据库、Redis、Docker API 等裸服务
- 大文件下载站或公开网盘
- 不愿意接受本地电脑断网/睡眠导致服务中断的生产服务

## 安装

> Claude Code 只识别 `.claude/skills/<名字>/SKILL.md` 这种**目录结构**，并且 helper 脚本必须随 skill 一起安装，所以请完整复制 `SKILL.md` + `scripts/` + `references/` 三部分。

Claude Code 全局安装（推荐，所有项目可用）：

```bash
git clone https://github.com/xiaoyuboi/cloudflare-tunnel-skill /tmp/cloudflare-tunnel-skill
mkdir -p ~/.claude/skills/cloudflare-tunnel
cp /tmp/cloudflare-tunnel-skill/SKILL.md ~/.claude/skills/cloudflare-tunnel/
cp -R /tmp/cloudflare-tunnel-skill/scripts /tmp/cloudflare-tunnel-skill/references ~/.claude/skills/cloudflare-tunnel/
rm -rf /tmp/cloudflare-tunnel-skill
```

Claude Code 项目级安装（仅当前项目可用）：

```bash
git clone https://github.com/xiaoyuboi/cloudflare-tunnel-skill /tmp/cloudflare-tunnel-skill
mkdir -p .claude/skills/cloudflare-tunnel
cp /tmp/cloudflare-tunnel-skill/SKILL.md .claude/skills/cloudflare-tunnel/
cp -R /tmp/cloudflare-tunnel-skill/scripts /tmp/cloudflare-tunnel-skill/references .claude/skills/cloudflare-tunnel/
rm -rf /tmp/cloudflare-tunnel-skill
```

Codex 安装：

```bash
git clone https://github.com/xiaoyuboi/cloudflare-tunnel-skill /tmp/cloudflare-tunnel-skill
mkdir -p ~/.codex/skills/cloudflare-tunnel
cp /tmp/cloudflare-tunnel-skill/SKILL.md ~/.codex/skills/cloudflare-tunnel/
cp -R /tmp/cloudflare-tunnel-skill/scripts /tmp/cloudflare-tunnel-skill/references ~/.codex/skills/cloudflare-tunnel/
rm -rf /tmp/cloudflare-tunnel-skill
```

> 系统要求：需要预装 `cloudflared`（安装方法见 `references/troubleshooting.md`）和 Python 3。helper 脚本在 macOS / Linux 上经过完整测试；Windows 为尽力支持（进程管理走 `tasklist`/`taskkill`），建议 Windows 用户优先使用 WSL 或手动命令。

## Quick Tunnel 临时链接

```bash
python3 scripts/tunnel_helper.py quick --url http://localhost:3000
```

查看状态：

```bash
python3 scripts/tunnel_helper.py status
```

停止：

```bash
python3 scripts/tunnel_helper.py stop
```

手动命令：

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

## Named Tunnel 固定域名

前提：

- 已安装 `cloudflared`
- 有 Cloudflare 账号
- 域名 DNS 已托管到 Cloudflare

基础流程：

```bash
cloudflared tunnel login
cloudflared tunnel create my-app
cloudflared tunnel route dns my-app app.example.com
python3 scripts/tunnel_helper.py named-config --name my-app --hostname app.example.com --url http://localhost:3000
cloudflared tunnel --config .cloudflare-tunnel/my-app.yml run my-app
```

## 本地测试

端到端 Quick Tunnel 测试：

```bash
python3 scripts/test_quick_tunnel.py
```

脚本基础检查：

```bash
python3 -m py_compile scripts/tunnel_helper.py scripts/test_quick_tunnel.py
python3 scripts/tunnel_helper.py --help
```

## 安全提醒

Tunnel 会把本地服务暴露到公网。发布前先确认没有公开：

- Token、Cookie、API key
- 未加认证的后台
- 内网系统
- 数据库或调试控制台
- 可修改数据的无认证 API

敏感服务请先加应用登录或 Cloudflare Access。

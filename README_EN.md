# Cloudflare Quick Tunnel Demo Skill

A beginner-friendly skill for turning a local web app/API/demo into a temporary public URL, so you can share it with friends, clients, teachers, or teammates without buying a server or configuring a domain.

## Use cases

- Share a local website with someone else
- Make a localhost project publicly accessible for preview
- Demonstrate Cloudflare Quick Tunnel in a video
- Avoid server purchase, deployment, custom domain, or router port forwarding

## One command

```bash
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

More stable version:

```bash
printf '' > /tmp/cloudflared-empty.yml
cloudflared --config /tmp/cloudflared-empty.yml tunnel --no-autoupdate --protocol http2 --url http://localhost:3000
```

## Install for Hermes

Clone this repository and copy `SKILL.md` into your Hermes skills directory:

```bash
mkdir -p ~/.hermes/skills/devops/cloudflare-quick-tunnel-demo
cp SKILL.md ~/.hermes/skills/devops/cloudflare-quick-tunnel-demo/SKILL.md
```

Then use the skill name in a new session:

```text
cloudflare-quick-tunnel-demo
```

## Install for Claude Code

Claude Code can use this skill, but it will not automatically load it directly from GitHub. You need to place `.claude/skills/cloudflare-quick-tunnel-demo.md` in either a project-level or user-level Claude skills directory.

### Option A: Project-level installation

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

### Option B: Global installation

```bash
mkdir -p ~/.claude/skills
curl -L https://raw.githubusercontent.com/xiaoyuboi/cloudflare-quick-tunnel-skill/main/.claude/skills/cloudflare-quick-tunnel-demo.md \
  -o ~/.claude/skills/cloudflare-quick-tunnel-demo.md
```

After that, in any project you can ask Claude Code:

```text
Expose this local project with Cloudflare Quick Tunnel and give me a temporary public URL.
```

## Local test

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

## Notes

Quick Tunnel URLs are temporary. If the terminal process stops, the computer sleeps, or the network disconnects, the public URL stops working.

Do not use Quick Tunnel as a long-term production deployment, public file-sharing service, or large-download site. Use a named Cloudflare Tunnel for stable long-term services.

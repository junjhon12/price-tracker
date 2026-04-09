# Claude Workshop Starter

Starter repo for the **progsu x Claude Code Workshop**, April 27, 2026.

## 60-second quickstart

```bash
git clone https://github.com/<org>/claude-workshop-starter.git
cd claude-workshop-starter

# Pick your OS
./setup/setup-mac-silicon.sh      # Apple Silicon
./setup/setup-mac-intel.sh        # Intel Mac
./setup/setup-linux.sh            # Linux
.\setup\setup-windows.ps1         # Windows (PowerShell as admin)

# Auth
gh auth login
claude login

# Go
claude
```

Then open **[GUIDE.md](./GUIDE.md)** and follow along.

## What's in the box

- **GUIDE.md**, the full workshop walkthrough
- **TROUBLESHOOTING.md**, when things break
- **.mcp.json**, preconfigured MCP servers (context7, github, vercel, playwright, magic)
- **.claude/agents/**, 5 ready-to-use subagents
- **.claude/skills/**, the `everything-claude-code-conventions` skill
- **setup/**, OS-specific setup scripts (Node, pnpm, Python, uv, Claude Code, gh)
- **projects/**, two project templates to pick from

## Projects

| Project | Difficulty | Time | Stack |
|---|---|---|---|
| [Personal portfolio site](./projects/01-portfolio/) | Easy | ~60–75 min | Next.js + Magic UI |
| [Browser price tracker](./projects/02-price-tracker/) | Hard | ~75–90 min | Next.js + FastAPI + Playwright |

## Requirements

- macOS, Linux, or Windows 10/11
- Git and a GitHub account
- ~2 GB free disk space (Playwright Chromium is chunky)
- A Claude account with credits, you got $40 at check-in


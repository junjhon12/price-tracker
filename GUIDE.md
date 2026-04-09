# Claude Code Workshop, Build Guide

Welcome. By the end of tonight you'll have a real project built with Claude Code, MCPs, subagents, and skills, and it'll be deployed to the internet.

**Time budget:** ~2 hours of building
**What you need:** a laptop, a terminal, a GitHub account, and the $40 in Claude credits we just handed you

---

## Table of contents

1. [Before you start](#1-before-you-start)
2. [Setup](#2-setup)
3. [Mental model: what is all this stuff?](#3-mental-model-what-is-all-this-stuff)
4. [Verify your environment](#4-verify-your-environment)
5. [Pick your project](#5-pick-your-project)
6. [Project A, Personal portfolio site](#6-project-a--personal-portfolio-site)
7. [Project B, Browser automation price tracker](#7-project-b--browser-automation-price-tracker)
8. [Using subagents](#8-using-subagents)
9. [Deploying with the Vercel MCP](#9-deploying-with-the-vercel-mcp)
10. [Stretch goals](#10-stretch-goals)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Before you start

### Redeem your credits

1. Go to https://console.anthropic.com
2. Sign in (or create an account, use the same email you gave us at check-in)
3. Go to **Billing → Credits** and paste the code from your card
4. Confirm the $40 balance shows up before moving on

### Accounts you'll need

- **Anthropic Console** (above), for Claude Code auth
- **GitHub**, you'll push your project here and the GitHub MCP will read from it
- **Vercel**, free tier is fine, sign in with GitHub at https://vercel.com

Do all three now. Seriously. This is the #1 cause of "I'm stuck" during the build block.

---

## 2. Setup

### Step 1: Clone the starter repo

```bash
git clone https://github.com/<org>/claude-workshop-starter.git
cd claude-workshop-starter
```

### Step 2: Run the setup script for your OS

Pick the one that matches your machine:

**macOS (Apple Silicon, M1/M2/M3/M4):**
```bash
./setup/setup-mac-silicon.sh
```

**macOS (Intel):**
```bash
./setup/setup-mac-intel.sh
```

**Linux:**
```bash
./setup/setup-linux.sh
```

**Windows (PowerShell, run as admin):**
```powershell
.\setup\setup-windows.ps1
```

The script will install or verify:
- **Node.js 20+** (via `nvm`)
- **pnpm**, our Node package manager for the workshop
- **Python 3.11+**
- **uv**, our Python package manager for the workshop
- **Claude Code CLI**
- **GitHub CLI (`gh`)**, for the GitHub MCP auth flow

> **Why `pnpm` and `uv` specifically?** Both are drop-in replacements for `npm` and `pip` that are dramatically faster and have better dependency resolution. The workshop uses them everywhere. If you normally use `npm` or `pip`, that's fine for your own projects, but please use `pnpm` and `uv` tonight so everyone's commands look the same.

### Step 3: Copy the env file

```bash
cp .env.example .env
```

You'll fill this in as you go. Don't worry about it yet.

### Step 4: Authenticate

```bash
claude login
gh auth login
```

For `gh auth login`, pick **GitHub.com → HTTPS → Login with a web browser**.

---

## 3. Mental model: what is all this stuff?

Before you start building, spend 2 minutes on this. It'll save you 20 minutes later.

| Thing | What it is | Think of it as |
|---|---|---|
| **Claude Code** | The CLI tool running Claude in your terminal, with access to your files and shell | The brain |
| **MCP** (Model Context Protocol) | A standard way for Claude Code to talk to external tools (Vercel, GitHub, browsers, docs, etc.) | Hands, lets Claude reach out into the world |
| **Skill** | A scoped set of instructions + helper files Claude loads when it detects a relevant task | A recipe card Claude grabs when needed |
| **Subagent** | A specialized Claude instance you can delegate a task to, with its own prompt and tools | A teammate you hand work to |
| **Plugin** | A package that bundles MCPs, skills, subagents, and commands together | A toolbox you install all at once |

**The key insight:** Claude Code alone is already good. Claude Code with the right MCPs and subagents for your task is several levels better because it stops guessing and starts *looking things up* and *delegating*.

---

## 4. Verify your environment

From the repo root:

```bash
claude
```

Once Claude Code launches, run this in the Claude Code prompt:

```
/mcp
```

You should see these MCP servers listed as connected:

- `context7`, live library docs
- `github`, read/write GitHub repos
- `vercel`, deploy and manage Vercel projects
- `playwright`, browser automation (for Project B)
- `magic`, Magic UI components (for Project A)

If any show as disconnected, see [Troubleshooting](#11-troubleshooting).

Also check the loaded subagents:

```
/agents
```

You should see: `ui-designer`, `code-reviewer`, `debugger`, `deploy-helper`, `docs-writer`.

And the skills:

```
/skills
```

You should see: `everything-claude-code-conventions` (and anything else we ship in `.claude/skills/`).

All good? Great. Pick a project.

---

## 5. Pick your project

We have two projects tonight. Pick the one that sounds more fun, there's no "right" one.

**Project A, Personal portfolio site**
A real developer portfolio you can put on your resume. Heavy on UI, uses Magic UI components, deployed to a custom Vercel URL. Easier, higher polish.

**Project B, Browser automation price tracker**
A tool that scrapes product prices from any URL, stores them, and shows a chart. Uses Playwright MCP to drive a real browser. Harder, more "systems-y", more impressive demo.

Jump to whichever one you picked.

---

## 6. Project A, Personal portfolio site

### What you're building

A single-page personal site with:
- Hero section with your name, title, and a one-liner
- Projects grid (3 cards minimum)
- About section
- Contact links
- Animated components from Magic UI
- Deployed to `your-name.vercel.app`

### MCPs and plugins active for this project

- `context7`, for Next.js, Tailwind, Magic UI docs
- `github`, to push your repo
- `vercel`, to deploy
- `magic`, Magic UI component library MCP
- `ui-designer` subagent, for focused styling work
- `everything-claude-code-conventions` skill, for consistent commit messages and code style

### Step-by-step

**1. Create the project folder**

```bash
cd projects/01-portfolio
```

Open `PROMPT.md` in that folder. This is your starter prompt, read it, tweak it with your own info (name, interests, projects you want to feature), and keep it open.

**2. Launch Claude Code in this folder**

```bash
claude
```

**3. Paste the starter prompt**

Copy the full contents of `PROMPT.md` into Claude Code. Starter prompt looks roughly like this, customize before pasting:

```
Build a personal developer portfolio for [YOUR NAME], a [YOUR MAJOR] student at [YOUR SCHOOL].

Requirements:
- Next.js 15 with App Router and TypeScript
- Tailwind CSS
- Use Magic UI components via the magic MCP for animated elements
  (hero text animation, project card hover effects, animated background)
- Single page, sections: Hero, Projects (3 cards), About, Contact
- Dark mode by default, clean and minimal
- Use pnpm for all package management
- Before writing code, use context7 to fetch the latest Next.js 15 App Router docs
  and the latest Magic UI component list
- When you need UI design decisions, delegate to the ui-designer subagent
- Follow the commit conventions from the everything-claude-code-conventions skill

Project details to feature:
- Project 1: [describe]
- Project 2: [describe]
- Project 3: [describe]

About me: [2-3 sentences]

Contact: GitHub, LinkedIn, email

When done, initialize git, create a new GitHub repo via the github MCP,
push, and deploy to Vercel via the vercel MCP.
```

**4. Work with Claude, don't just watch**

As Claude builds, review what it's doing. When it asks for confirmation, actually read the diff. If you see something you don't like, say so, "make the hero font bigger," "I don't like that color, use a warmer tone," "the project cards should be in a 3-column grid on desktop."

**5. Checkpoints to hit**

- [ ] `pnpm dev` runs locally and the site loads
- [ ] Magic UI animations are visible on the hero
- [ ] All 3 project cards are populated with your real projects
- [ ] `ui-designer` subagent was invoked at least once
- [ ] Pushed to a new GitHub repo via the github MCP
- [ ] Deployed to Vercel via the vercel MCP
- [ ] Live URL loads and looks good on mobile

Skip to [Section 9](#9-deploying-with-the-vercel-mcp) when you're ready to deploy.

---

## 7. Project B, Browser automation price tracker

### What you're building

A web app where you paste a product URL, the backend uses Playwright (driven by Claude Code via the Playwright MCP during development, and by a Python script at runtime) to scrape the price, store it, and display a chart of price history over time.

### MCPs and plugins active for this project

- `context7`, for FastAPI, Playwright, Recharts docs
- `github`, to push your repo
- `vercel`, to deploy the frontend
- `playwright`, browser automation (this is the star of the show)
- `everything-claude-code-conventions` skill, for consistent commit messages

### Architecture

```
Frontend (Next.js on Vercel)
    ↓ HTTP
Backend API (FastAPI, Python, uv-managed)
    ↓ subprocess
Playwright scraper (Python, headless Chromium)
    ↓
SQLite (dev) / Postgres (prod)
```

For tonight we'll keep it simple: frontend on Vercel, backend running locally, SQLite. You can harden it into a full production deploy as a stretch goal.

### Step-by-step

**1. Create the project folder**

```bash
cd projects/02-price-tracker
```

Open `PROMPT.md` and read it.

**2. Launch Claude Code**

```bash
claude
```

**3. Starter prompt**

Roughly:

```
Build a price tracker web app.

Stack:
- Frontend: Next.js 15 + TypeScript + Tailwind + Recharts, deployed to Vercel
- Backend: FastAPI (Python 3.11+), managed with uv
- Scraper: Playwright (Python), headless Chromium
- Storage: SQLite for dev

Features:
- User pastes a product URL (support at least: Amazon, Best Buy, generic og:price meta)
- Backend kicks off a Playwright scrape, extracts price + title + image
- Store in SQLite with a timestamp
- Frontend shows a list of tracked items and a line chart of price history per item
- "Refresh now" button re-scrapes on demand
- Manual "refresh all" endpoint (no cron needed tonight)

Workflow:
- Use uv for all Python deps: `uv init`, `uv add fastapi playwright ...`
- Use pnpm for all Node deps
- Use context7 to look up current FastAPI and Playwright Python API
  BEFORE writing scraper code, don't guess selectors or API shapes
- Use the playwright MCP to interactively test selectors on real pages during development
- When debugging failed scrapes, delegate to the debugger subagent
- Follow commit conventions from the everything-claude-code-conventions skill

When done, push to a new GitHub repo via the github MCP, deploy the frontend to
Vercel via the vercel MCP, and print clear instructions for running the backend locally.
```

**4. The Playwright MCP is your secret weapon**

Instead of writing a selector and running your script 15 times, ask Claude something like: "Use the playwright MCP to open amazon.com/dp/B08N5WRWNW, find the price element, and tell me the most stable selector." Claude will actually drive a real browser, inspect the DOM, and come back with a working answer. This alone is worth the entire workshop.

**5. Checkpoints to hit**

- [ ] `uv run uvicorn app.main:app --reload` starts the backend
- [ ] `pnpm dev` starts the frontend
- [ ] You can paste a URL and see a scrape succeed
- [ ] Price history chart renders for at least one item
- [ ] `debugger` subagent was invoked at least once
- [ ] Pushed to a new GitHub repo via the github MCP
- [ ] Frontend deployed to Vercel via the vercel MCP

---

## 8. Using subagents

Subagents live in `.claude/agents/`. You have five pre-loaded:

| Subagent | When to use it |
|---|---|
| `ui-designer` | "Make this look better," color/layout/spacing decisions, picking components |
| `code-reviewer` | "Review my last 10 commits," catching issues before push |
| `debugger` | A test is failing, a scraper broke, a stack trace you don't understand |
| `deploy-helper` | Vercel build errors, env var problems, domain setup |
| `docs-writer` | Writing your README, inline comments, API docs |

**How to invoke one:**

In Claude Code, just ask:
> "Use the debugger subagent to figure out why the Playwright scrape times out on bestbuy.com."

Or explicitly:
> "Delegate this to the code-reviewer subagent: review the last commit and flag any issues."

**Why bother with subagents instead of just asking Claude directly?** Two reasons: (1) each subagent has a focused system prompt so it doesn't get distracted by everything else in your session, and (2) it keeps your main conversation context clean for the high-level build.

---

## 9. Deploying with the Vercel MCP

The workflow is roughly:

1. Make sure your project is pushed to GitHub (use the `github` MCP, just tell Claude to create the repo and push)
2. Tell Claude: "Use the vercel MCP to create a new Vercel project from my GitHub repo `<username>/<reponame>`, deploy it, and give me the production URL"
3. If there are build errors, delegate to the `deploy-helper` subagent
4. Once it's live, open the URL on your phone to check mobile

For Project B, you're only deploying the **frontend** to Vercel. The backend stays local tonight.

---

## 10. Stretch goals

Finished early? Pick one:

- **Claude Swarm**, spin up multiple agents working in parallel on different parts of your project. Great for "build the API and the frontend at the same time" workflows.
- **superpowers plugin**, adds a pile of extra skills and commands. Install it and explore what it gives you.
- **Add a second MCP**, try adding the Context7 upstash or a weather/stocks MCP and integrate it into your project
- **Polish pass**, delegate to `ui-designer` for a full aesthetic review
- **README pass**, delegate to `docs-writer` for a beautiful README with badges, screenshots, and a demo GIF
- **Custom subagent**, write your own subagent in `.claude/agents/my-agent.md` and invoke it

---

## 11. Troubleshooting

**`claude` command not found after setup**
Restart your terminal. If still broken, check that `~/.local/bin` (or the equivalent) is in your `PATH`.

**MCPs show as disconnected in `/mcp`**
Run `claude mcp list` from the repo root. Look at `.mcp.json`, make sure you're running `claude` from the repo root, not a parent directory. MCP configs are per-directory.

**GitHub MCP can't authenticate**
Run `gh auth status`. If not logged in, `gh auth login`. The GitHub MCP reads from the `gh` CLI credentials.

**Vercel MCP can't deploy**
Make sure you've signed into vercel.com at least once in a browser. The MCP will walk you through a device-code auth flow on first use.

**Playwright says "browser not installed"**
Run `uv run playwright install chromium` from your project folder.

**`pnpm` or `uv` not found**
Re-run the setup script for your OS. If that fails, install manually:
- pnpm: https://pnpm.io/installation
- uv: https://docs.astral.sh/uv/getting-started/installation/

**I'm completely stuck**
Raise your hand. That's literally why we have floaters tonight.

---

Good luck. Build something you'd actually want to show your friends.

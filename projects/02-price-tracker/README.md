# Project B, Browser Automation Price Tracker

A full-stack price tracker. Paste a product URL, headless Chromium scrapes the price, SQLite stores history, and Recharts draws the line. The `playwright` MCP lets Claude drive a real browser during development to find the right selectors without guessing.

## Difficulty
**Medium to hard**, pick this if you want to see what MCP-driven browser automation actually feels like. It's the flashier demo.

## Time
~75–90 minutes

## Stack
- **Frontend:** Next.js 15 + TypeScript + Tailwind + Recharts (deployed to Vercel)
- **Backend:** FastAPI (Python 3.11+), managed with `uv`
- **Scraper:** Playwright for Python, headless Chromium
- **Storage:** SQLite (local file)

## MCPs used
- `context7`, FastAPI, Playwright, Recharts docs
- `github`, create the repo and push
- `vercel`, deploy the frontend
- `playwright`, **the star of the show**, drives a real browser during development

## Subagents used
- `debugger`, for when a scrape fails or a selector breaks

## Skills used
- `everything-claude-code-conventions`, consistent commit messages

## How to start
1. Have 1–2 real product URLs ready for testing (avoid Amazon if possible, bot detection is rough)
2. Launch Claude Code from this folder: `claude`
3. Paste the prompt from [`PROMPT.md`](./PROMPT.md)
4. **Use the `playwright` MCP interactively** to find selectors before writing scraper code

Full walkthrough is in the root [`GUIDE.md`](../../GUIDE.md) → Section 7.

## Repo layout (after build)
```
.
├── frontend/          # Next.js app
└── backend/           # FastAPI + scraper + SQLite
    ├── app/
    │   ├── main.py
    │   ├── db.py
    │   └── scraper.py
    └── pyproject.toml
```

## Running locally (after build)
```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
pnpm install
pnpm dev
```

## Deploy note
Only the **frontend** is deployed to Vercel tonight. The backend stays local. Turning this into a fully production-deployed app is a stretch goal.

## When you're done
See the "Done checklist" at the bottom of `PROMPT.md`.

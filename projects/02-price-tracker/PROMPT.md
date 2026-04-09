# Project B, Browser Automation Price Tracker

**Difficulty:** Medium to hard
**Estimated time:** 75–90 minutes
**Stack:** Next.js frontend + FastAPI backend + Playwright scraper + SQLite

## What you're building

A tool where you paste a product URL, a headless browser scrapes the price, and you get a chart of price history for every item you're tracking. The `playwright` MCP lets you use a real browser interactively during development to find the right selectors without a million trial-and-error runs.

## Before you paste the prompt

1. Make sure you're in this folder: `projects/02-price-tracker`
2. Launch Claude Code: `claude`
3. Have 1-2 real product URLs ready (Amazon, Best Buy, or anything with a visible price) for testing

## Your starter prompt

Copy everything between the triple-dashes into Claude Code:

---

Build a price tracker web application with a Next.js frontend and a Python backend.

**Architecture:**
- **Frontend:** Next.js 15 + TypeScript + Tailwind + Recharts, deployed to Vercel
- **Backend:** FastAPI (Python 3.11+), managed with `uv`
- **Scraper:** Playwright for Python, headless Chromium
- **Storage:** SQLite (local file, no cloud DB tonight)
- **Package managers:** `uv` for Python, `pnpm` for Node. Do not use `pip` or `npm`.

**Repo layout:**
```
.
├── frontend/          # Next.js app
├── backend/           # FastAPI + scraper + SQLite
│   ├── app/
│   │   ├── main.py
│   │   ├── db.py
│   │   └── scraper.py
│   └── pyproject.toml
└── README.md
```

**Backend features:**
- `POST /items`, body: `{ "url": "..." }`, triggers a scrape, stores `{id, url, title, image_url, created_at}` and the first price point
- `GET /items`, returns all tracked items with their latest price
- `GET /items/{id}/history`, returns the full price history for charting
- `POST /items/{id}/refresh`, re-scrapes and appends a new price point
- `POST /refresh-all`, re-scrapes all items

**Scraper logic:**
- Use Playwright headless Chromium
- Try these strategies in order for price extraction:
  1. Site-specific selectors for Amazon and Best Buy (look them up using the `playwright` MCP interactively, do not guess)
  2. Fallback: `og:price:amount` or `product:price:amount` meta tags
  3. Fallback: any element matching a currency regex near a heading
- Also extract the page title and the main product image URL
- Handle failures gracefully, return a clear error, don't crash

**Frontend features:**
- Input box at the top: paste a URL, click "Track"
- List of tracked items below, each showing image, title, current price, and a sparkline
- Click an item to expand it into a full line chart using Recharts
- "Refresh" button per item and a "Refresh all" button at the top
- Loading states while scrapes run
- Point it at `http://localhost:8000` for the backend (configurable via env var)

**Workflow requirements:**
- Before writing scraper code, use the `context7` MCP to fetch the current Playwright Python API docs and FastAPI async docs
- **Use the `playwright` MCP interactively during development** to open real product pages, inspect the DOM, and find stable selectors. This is the most important part, do not guess selectors from memory.
- When a scrape fails, delegate to the `debugger` subagent with the error and the target URL
- Follow commit conventions from the `everything-claude-code-conventions` skill (conventional commits)

**Deployment:**
- Only the **frontend** is deployed tonight. Use the `github` MCP to create a new public repo and push everything. Use the `vercel` MCP to deploy just the `frontend/` directory (set the root directory in the Vercel project settings).
- The backend runs locally via `uv run uvicorn app.main:app --reload --app-dir backend`
- Print a clear README with instructions for running both halves locally

**Test it with these URLs when the build is done:**
1. `[YOUR TEST URL 1]`
2. `[YOUR TEST URL 2]`

---

## Tips while building

- **The `playwright` MCP is the star of this project.** Use it like this: "Use the playwright MCP to open [url], find the element that contains the price, and tell me the most specific and stable CSS selector." You'll save 30+ minutes.
- **Amazon and Best Buy have bot detection.** If you hit a CAPTCHA page, that's the real error, not a selector issue. Ask the `debugger` subagent to help you detect and handle it.
- **Don't over-engineer the DB.** A single `items` table + a `price_history` table is enough.
- **`uv add fastapi[standard] playwright recharts ...`**, use `uv add` to install Python packages, never `pip install`.

## Done checklist

- [ ] Backend runs via `uv run uvicorn app.main:app --reload --app-dir backend`
- [ ] Frontend runs via `pnpm dev` in `frontend/`
- [ ] You can paste a URL and see a successful scrape with price + title + image
- [ ] At least one item has 2+ price points so the chart has something to draw
- [ ] `playwright` MCP was used interactively at least once during development
- [ ] `debugger` subagent was invoked at least once
- [ ] Pushed to GitHub via the `github` MCP
- [ ] Frontend deployed to Vercel via the `vercel` MCP
- [ ] README has clear "how to run locally" instructions

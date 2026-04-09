# Troubleshooting

Common problems from past workshops, in rough order of frequency.

## Setup issues

### `claude: command not found` after running the setup script

**Cause:** Your shell's `PATH` wasn't reloaded.

**Fix:**
```bash
# Mac/Linux
source ~/.zshrc   # or ~/.bashrc
# Or just close and reopen your terminal

# Windows
# Close and reopen PowerShell
```

If still broken:
```bash
# Check where claude was installed
npm root -g
# Add that bin dir to your PATH manually
```

### `pnpm: command not found`

You skipped or broke the pnpm install step. Manually:
```bash
npm install -g pnpm
```

### `uv: command not found`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Then reload your shell
```

Windows:
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### Setup script fails on Homebrew install (Mac)

Run it manually first, then re-run the setup script:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### `nvm: command not found` after install

`nvm` is shell-scoped, it gets added to `~/.zshrc` or `~/.bashrc`. Close and reopen your terminal, or:
```bash
source ~/.nvm/nvm.sh
```

### Windows: "script cannot be loaded because running scripts is disabled"

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then re-run the setup script.

---

## MCP issues

### `/mcp` shows servers as disconnected

**Most common cause:** You're running `claude` from the wrong directory. `.mcp.json` is per-directory. Make sure you're in the repo root:

```bash
cd claude-workshop-starter
claude
```

Then inside Claude Code:
```
/mcp
```

### `claude mcp list` shows nothing

Same fix, run it from the repo root.

### GitHub MCP: "authentication failed"

The GitHub MCP uses the `gh` CLI's credentials. Check:
```bash
gh auth status
```

If not logged in:
```bash
gh auth login
# Pick: GitHub.com → HTTPS → Login with web browser
```

Alternatively, set a personal access token in `.env`:
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```
Get one at https://github.com/settings/tokens (classic, with `repo` scope).

### Vercel MCP: "not authenticated"

First time you use it, the MCP walks you through a device-code auth flow. You'll get a URL to open in your browser. Make sure you're logged into vercel.com in that browser first.

### Playwright MCP: "browser not installed" or "executable doesn't exist"

```bash
npx -y playwright install chromium
```

On Linux you may also need system deps:
```bash
npx -y playwright install --with-deps chromium
```

### Magic MCP: doesn't return any components

Make sure you're actually asking Claude to use it. Try:
> "Use the magic MCP to list available hero section components."

If that still doesn't work, check `claude mcp list`, if `magic` isn't there, your `.mcp.json` didn't load (you're in the wrong directory).

---

## Project A, Portfolio

### `pnpm dev` fails with "Cannot find module"

```bash
rm -rf node_modules .next
pnpm install
pnpm dev
```

### Vercel build fails with "Module not found" but it works locally

Almost always a case-sensitivity issue. macOS is case-insensitive, Linux (Vercel's build env) isn't.

**Check:**
```bash
# This import:
import Button from './components/button'
# Won't match this file:
components/Button.tsx
```

Fix the import or rename the file so cases match.

### Magic UI components look broken / unstyled

Make sure Tailwind is actually processing the Magic UI files. Check your `tailwind.config.ts`:
```ts
content: [
  "./src/**/*.{ts,tsx}",
  "./node_modules/@magicuidesign/**/*.{ts,tsx}",  // <-- this line
],
```

---

## Project B, Price Tracker

### `uv run` fails with "no virtual environment found"

From the backend folder:
```bash
uv sync
# Then
uv run uvicorn app.main:app --reload
```

### Playwright scrape times out

**Step 1:** Use the `playwright` MCP to open the same URL interactively and see what's actually rendered. You're probably hitting a CAPTCHA page, not your target page.

**Step 2:** If it IS the right page, your selector is wrong. Ask Claude:
> "Use the playwright MCP to open [url] and tell me the most stable CSS selector for the product price."

**Step 3:** Amazon, Walmart, and Best Buy have aggressive bot detection. For the workshop, try a smaller site or use the og-meta fallback.

### CORS error from the frontend calling the backend

Add CORS middleware to FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SQLite "database is locked"

You have two processes writing at once. Stop one of them. For the workshop, a single uvicorn process is enough.

---

## Claude Code issues

### "Rate limit exceeded" or "insufficient credits"

Check your balance at https://console.anthropic.com → Billing. If you're at $0, the credits from check-in haven't been applied yet, grab a floater.

### Subagents aren't loading

```
/agents
```
Should list all 5. If empty, check that `.claude/agents/*.md` files exist in your current directory. They're per-directory, just like MCPs.

### Skills aren't loading

```
/skills
```
Should list `everything-claude-code-conventions`. If not, the skill file is missing from `.claude/skills/`, re-clone the repo or copy the file back.

### Claude Code is just… slow

First response in a session builds context and is always slower. Subsequent responses should be faster. If it's stuck for 2+ minutes, Ctrl+C and try a smaller prompt.

---

## Deploy issues

### Vercel build succeeds but the site is blank

Open DevTools → Console on the deployed URL. You're probably hitting a client-side error. Common culprits:
- Env var that's set locally but not on Vercel
- An API route that works locally but not in production
- Hardcoded `localhost:3000` somewhere

### Vercel deploy works, domain shows "DEPLOYMENT_NOT_FOUND"

Wait 30 seconds. Vercel's edge network takes a moment to propagate.

### Can't find the live URL

```
# Tell Claude:
> Use the vercel MCP to list my projects and show me the production URL for <project-name>.
```

---

## Still stuck?

**Raise your hand.** That's what the floaters are for. Seriously, don't burn 20 minutes on a setup issue when someone can fix it in 2.

After the workshop, drop it in the Discord and we'll get back to you.

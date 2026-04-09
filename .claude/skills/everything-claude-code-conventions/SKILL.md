---
name: everything-claude-code-conventions
description: Development conventions and patterns for projects built during the GSU Claude Code workshop. Teaches Claude to use conventional commits, consistent naming, and clean code style. Activate when committing, adding features, or reviewing code in workshop projects.
---

# Everything Claude Code Conventions

> Vendored from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) for the GSU Programming Club Claude Code workshop (April 27, 2026).

## Overview

This skill teaches Claude the development patterns and conventions used in everything-claude-code, adapted for the workshop projects (portfolio site and browser price tracker).

## When to Use This Skill

Activate this skill when:

- Making commits in a workshop project
- Adding new features following established patterns
- Writing tests that match project conventions
- Creating commits with proper message format

## Commit Conventions

Follow **Conventional Commits** format for all commits.

### Prefixes

- `feat:`, a new feature
- `fix:`, a bug fix
- `docs:`, documentation only
- `style:`, formatting, missing semis, etc. (no code change)
- `refactor:`, code change that neither fixes a bug nor adds a feature
- `test:`, adding or updating tests
- `chore:`, tooling, deps, build config

### Message Guidelines

- Keep the first line concise and descriptive (aim for ~65 chars)
- Use **imperative mood**: "Add feature" not "Added feature"
- Scope is optional but helpful: `feat(ui): add hero animation`

### Examples

```
feat(portfolio): add hero section with Magic UI sparkles
feat(scraper): support og:price meta fallback
fix: handle missing product image in scrape result
docs: add setup instructions for Windows
chore(deps): bump next to 15.2.0
refactor(db): extract price history query to helper
test(scraper): add selector tests for Best Buy
```

### Anti-examples (don't do these)

```
updated stuff              # vague, lowercase, no prefix
Fixed the bug              # past tense, vague, no prefix
WIP                        # not useful to anyone
feat: Added new feature    # past tense + prefix + still vague
```

## Code Style

### Naming

| Element | Convention | Example |
|---|---|---|
| Files | `camelCase` (JS/TS) or `snake_case` (Python) | `priceChart.tsx`, `scraper.py` |
| React components | `PascalCase` | `PriceChart`, `HeroSection` |
| Functions | `camelCase` (JS/TS) or `snake_case` (Python) | `fetchPrice`, `fetch_price` |
| Classes | `PascalCase` | `PriceScraper` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Environment variables | `SCREAMING_SNAKE_CASE` | `DATABASE_URL` |

### Import Style

**TypeScript/JavaScript:** Prefer relative imports within a package, absolute (`@/...`) imports across packages.

```ts
// within the same feature
import { Button } from '../components/Button'
import { useAuth } from './hooks/useAuth'

// across features (Next.js @ alias)
import { db } from '@/lib/db'
```

**Python:** Absolute imports from the package root.

```python
from app.db import get_connection
from app.scraper import scrape_product
```

## Error Handling

### TypeScript/JavaScript

Use try/catch around anything that can throw, log with context, rethrow with a user-friendly message if the error bubbles to the UI.

```ts
try {
  const result = await fetchPrice(url)
  return result
} catch (error) {
  console.error('fetchPrice failed:', { url, error })
  throw new Error('Could not fetch the current price')
}
```

### Python

Catch specific exceptions, never bare `except:`.

```python
try:
    price = await scrape_product(url)
except PlaywrightTimeoutError as e:
    logger.error(f"scrape timed out for {url}: {e}")
    raise ScraperError(f"Could not load {url}") from e
except Exception as e:
    logger.exception(f"unexpected error scraping {url}")
    raise
```

## Testing

- **Unit tests** for pure functions and utilities
- **Integration tests** for API routes and database queries
- Keep test files next to the code they test, named `*.test.ts` or `test_*.py`
- Aim for coverage of the critical path, not 100%

## Best Practices

### Do

- Use conventional commit format (`feat:`, `fix:`, etc.)
- Use imperative mood in commit messages
- Follow the naming conventions for the language you're in
- Handle errors with specific exception types
- Log errors with context (what was being attempted, with what inputs)

### Don't

- Write vague commit messages ("updated stuff", "fixes")
- Mix camelCase and snake_case in the same file
- Use bare `except:` in Python
- Swallow errors without logging
- Commit `.env` files or secrets

## Workshop-specific notes

- **Project A (Portfolio):** stick to camelCase for files, PascalCase for React components
- **Project B (Price Tracker):** backend uses snake_case (Python), frontend uses camelCase (TS)
- **Package management:** always `pnpm` for Node, `uv` for Python, never `npm` or `pip`
- **Before committing:** run `pnpm lint` (frontend) or `uv run ruff check` (backend) if configured

---

*Adapted for the GSU Programming Club Claude Code workshop. Original skill: [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code).*

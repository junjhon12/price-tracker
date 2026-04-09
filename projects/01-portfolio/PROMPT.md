# Project A, Personal Portfolio Site

**Difficulty:** Easy to medium
**Estimated time:** 60–75 minutes
**Stack:** Next.js 15 + TypeScript + Tailwind + Magic UI

## Before you paste the prompt

1. Fill in the `[BRACKETS]` below with your real info. Don't skip this, generic content = generic output.
2. Make sure you're in this folder: `projects/01-portfolio`
3. Launch Claude Code: `claude`

## Your starter prompt

Copy everything between the triple-dashes into Claude Code:

---

Build a personal developer portfolio for **[YOUR NAME]**, a **[YOUR MAJOR]** student at **[YOUR SCHOOL]**, graduating **[YEAR]**.

**Stack requirements:**
- Next.js 15 with App Router, TypeScript, and the `src/` directory layout
- Tailwind CSS (use the default config, no custom plugins unless needed)
- **Magic UI components via the `magic` MCP** for all animated elements, do not hand-roll animations
- Use `pnpm` for all package management (never `npm` or `yarn`)

**Workflow requirements:**
- Before writing any code, use the `context7` MCP to fetch the latest Next.js 15 App Router docs and the current Magic UI component catalog
- When making visual or layout decisions, delegate to the `ui-designer` subagent
- Follow commit message conventions from the `everything-claude-code-conventions` skill (conventional commits: `feat:`, `fix:`, `docs:`, etc.)

**Page structure (single page, smooth scroll between sections):**

1. **Hero**, my name, a one-line tagline, and an animated element from Magic UI (pick one that fits: animated gradient text, sparkles, or typing effect)
2. **Projects**, 3 cards in a responsive grid (1 col mobile, 2 col tablet, 3 col desktop). Each card should have a Magic UI hover effect.
3. **About**, 2-3 paragraphs about me, my interests, and what I'm looking for next
4. **Contact**, GitHub, LinkedIn, and email as icon links

**Design direction:**
- Dark mode by default, no light mode toggle needed
- Clean and minimal, whitespace over decoration
- One accent color: **[PICK ONE: blue / green / purple / orange / red]**
- Font: use a clean sans-serif from `next/font/google`, pick Inter, Geist, or JetBrains Mono

**My projects to feature:**

1. **[PROJECT 1 NAME]**, [1-2 sentence description], [tech stack], [link or "coming soon"]
2. **[PROJECT 2 NAME]**, [1-2 sentence description], [tech stack], [link]
3. **[PROJECT 3 NAME]**, [1-2 sentence description], [tech stack], [link]

**About me:**
[2-3 sentences about yourself, your interests, what you're working on, what you're looking for]

**Contact:**
- GitHub: [your username]
- LinkedIn: [your handle]
- Email: [your email]

**Deployment workflow (do this at the end):**
1. Run `pnpm build` locally and fix any errors
2. Use the `github` MCP to create a new public repo named `portfolio` under my GitHub account and push the code
3. Use the `vercel` MCP to create a new Vercel project from that GitHub repo and deploy it
4. Give me the final production URL

---

## Tips while building

- **Review Claude's diffs before accepting them.** If something looks off, push back.
- **Iterate on one thing at a time.** "The hero feels cramped, add more vertical padding" beats "make the whole site better."
- **Ask to see the Magic UI options.** Prompt: "Use the magic MCP to show me 5 hero animation components and let me pick one."
- **Don't skip the `ui-designer` subagent.** Try: "Delegate to ui-designer: review the projects section and suggest 3 improvements."

## Done checklist

- [ ] Site runs locally via `pnpm dev`
- [ ] At least 2 Magic UI components are visible on the page
- [ ] Your 3 real projects are in the grid, not placeholder text
- [ ] Looks good on a 375px viewport (Chrome DevTools mobile mode)
- [ ] Pushed to GitHub via the `github` MCP
- [ ] Deployed to Vercel via the `vercel` MCP
- [ ] You have a live URL you'd share with someone

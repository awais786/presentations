# Arbisoft Open Source Team — Presentation Deck

Context doc for Claude sessions on this project.

## Structure

- **Two themes**: `light/` (classic blue/white) and `dark/` (Genspark-inspired dark navy)
- **15 slides total** in each theme
- **Root**: `index.html` chooser between themes
- **Shared per theme**: `deck.css` + `deck.js` (keyboard nav via body data-attrs)
- **Canvas**: dark uses fixed 1280×720 absolute-positioned container; light uses viewport-responsive flex

## Slide order (both themes)

1. intro — hero: "Open Source at Arbisoft"
2. why-opensource — 2-col: Global Case + Arbisoft Edge
3. overview — Learn / Build / Transition pillars + 2025→2026 timeline
4. how-we-work — 6-step playbook grid
5. current — 4 full-time dev cards
6. parttime — 3 part-time cards
7. past — 9 alumni cards
8. engagements — major work grid + project pills
9. team-stats — per-developer breakdown with subtotals
10. project-stats — contributions-by-project table + domains
11. transitions — 6 engineers → client engagement cards
12. ai-work — Vibe coding, issue agents, chatbots, HR assistant, Django upgrade agent
13. vision — "More Code. Less Connection." 2026 AI vision + 3 pillars
14. cta — Join Us + opensource.arbisoft.com
15. questions — "Questions?" hero finale

## Design tokens (dark)

- bg: `#0f172a` → `#1e293b` gradient
- primary blue: `#3b82f6`, accent gradient: `#60a5fa` → `#a78bfa`
- text: `#f8fafc` (primary), `#cbd5e1`/`#94a3b8` (secondary), `#64748b` (muted)
- cards: `rgba(30, 41, 59, 0.5)` with `rgba(255,255,255,0.08)` border
- grid pattern overlay: 40×40 `rgba(255,255,255,0.03)` lines
- Font: Inter (300-800) + JetBrains Mono (400-500) via Google Fonts
- Icons: Font Awesome 6.4.0 CDN

## Design tokens (light)

- bg: `#ffffff`
- primary blue: `#0969da`
- cards: `#f6f8fa` with `#d1d9e0` border
- Font: system sans-serif

## Nav pattern

- `<body data-prev="..." data-next="..." data-first="..." data-last="...">` drives keyboard
- Footer in-slide: `.nav-btn` (chevron button)
- Floating viewport edges: `.deck-nav-float` (dark) / `.deck-nav` (light) — always visible during presentation
- Counter: `<span class="page-number">NN</span> / TT`

## Python helper scripts

- `fix-nav.py` — rewrites body data-attrs, footer hrefs, float-nav hrefs, counter display based on sorted filename order. Run after adding/removing/reordering slides.
- `inject-dark-nav.py` — injects `.deck-nav-float` block before `</body>` of each dark slide (one-time)

## Deploy

- GitHub: `awais786/presentations` (HTTPS + gh CLI auth)
- Vercel: `arbisoft-opensource` project, alias `arbisoft-opensource.vercel.app` is stable URL
- Deploy: `npx vercel deploy --prod --yes && npx vercel alias set <new-url> arbisoft-opensource.vercel.app`
- GitHub push does NOT auto-deploy (Vercel GitHub App not installed on repo)

## User preferences

- Prefers dark theme for primary deck; light kept for reference
- Wants em-dashes (—) replaced with hyphens (-) — em-dashes flag AI-generated content
- Prefers numbered cards (01/02/03) over emoji icons
- "Live" tags removed from AI Work slide; "In Progress"/"Planning" kept
- Caveman mode active — terse responses, drop articles/filler

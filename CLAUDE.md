# Arbisoft Open Source Presentation Decks

Static HTML slide decks. No build step, no framework. Every slide is a standalone `.html` file.

## Dark theme only

**There is no light theme. `q2/light/` and top-level `light/` were deleted - do not recreate them
and do not build a light variant of a slide unless explicitly asked.** A light theme was tried for
the Q2 deck; 5 of its 13 slides referenced dark-only classes (`.slide-container`, `.header`,
`.grid-pattern`, `.footer`) that its own `deck.css` never defined, so it rendered broken and was
removed rather than fixed.

When asked to change deck content, change the dark slide only.

## Which deck is live

`q2/dark/` is the current deck - 15 slides, the Q2 leadership review (Apr 1 - Jul 15, 2026).

Root `index.html` is the landing page and links only into `q2/dark/`. The older top-level `dark/`
deck (pre-Q2, 15 slides) still exists and is deployed and reachable by direct URL, but is unlinked
and superseded.

`q2/index.html` is a meta-refresh redirect back to root, so `/q2/` does not 404.

## Slide anatomy (dark)

Fixed 1280x720 absolute canvas. `deck.css` supplies `.slide-container`, `.grid-pattern`,
`.header`, `.logo`, `.nav-dots`, `.footer`, `.page-indicator`, `.nav-btn`, `.deck-nav-float`.
Per-slide layout goes in an inline `<style>` block; do not add slide-specific rules to `deck.css`.

Required skeleton - `fix-nav.py` depends on these exact markers:

```html
<body data-prev="..." data-next="..." data-first="..." data-last="...">
<div class="slide-container">
  <div class="grid-pattern"></div>
  <div class="header">...</div>
  <div class="main-content">...</div>
  <div class="footer">
    <div class="footer-right">
      <span class="page-indicator"><span class="page-number">NN</span> / 15</span>
      <a class="nav-btn" href="slide-NN-next.html" title="Next">...</a>
    </div>
  </div>
</div>
<!-- FLOAT-NAV:START -->
<a class="deck-nav-float prev" href="..." title="Previous">&#8249;</a>
<a class="deck-nav-float next" href="..." title="Next">&#8250;</a>
<!-- FLOAT-NAV:END -->
```

## Adding or reordering slides

Order comes from **sorted filename**, so the `slide-NN-` prefix is the ordering key.

1. `git mv` existing slides to their new numbers, **highest first**, or renames collide.
2. Write the new slide(s) using the skeleton above.
3. `python3 fix-nav.py q2/dark` - rewrites data-attrs, footer hrefs, float-nav hrefs, and all
   counters from filename order. Run it via `python3`; the file is not executable.
4. Update the slide count in root `index.html` ("NN-slide Q2 review").
5. Verify no dangling `href="slide-*"` and that counters read `NN / <total>`.

Never hand-edit nav links or counters. `fix-nav.py` owns them and will overwrite.

## Deploy

```bash
npx vercel deploy --prod --yes
npx vercel alias set <new-deployment-url> arbisoft-opensource.vercel.app
```

**The alias step is mandatory.** `arbisoft-opensource.vercel.app` is a manually pinned alias, not a
project production domain. A prod deploy updates `presentations-nine-beta.vercel.app` automatically
but leaves the alias frozen on whatever deployment it last pointed at. Skip the alias and the stable
URL keeps serving old slides while the deploy reports success.

Vercel deduplicates identical file trees: if nothing changed it returns an existing older deployment
rather than building. A deploy that "succeeds" instantly with a stale-looking URL usually means the
working tree was unchanged.

Project is `presentations` (`prj_sJue3zS0SYhLCWa958CWLkb5WtOa`), not `arbisoft-opensource`.
Direct `*.vercel.app` deployment URLs 302 to a login (Deployment Protection); the alias is public.

GitHub pushes do **not** trigger deploys - the Vercel GitHub App is not installed on the repo.
Deploying and pushing are separate steps; production can run ahead of `origin/main`.

## Content conventions

- **No em-dashes.** Use a hyphen surrounded by spaces. Em-dashes read as AI-generated.
- Mark unverified facts with `<!-- TODO: ... -->` rather than inventing specifics. Slides go in
  front of leadership; a plausible-looking wrong number is worse than a visible gap.
- Numbered cards (01/02/03) over emoji icons.
- Font Awesome 6.4.0 and Google Fonts (Inter + JetBrains Mono) load from CDN per slide.
- Team photos live in `/team/`, referenced from q2 slides as `../../team/<name>.jpg`.

## Stale files

`memory.md` predates the Q2 deck. It describes the old 15-slide `dark/` deck, names the Vercel
project `arbisoft-opensource`, and omits the alias-pinning trap. Prefer this file.

## Working style

Terse. Drop articles and filler.

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

`q2/dark-v2/` is the current deck - 19 slides, the Q2 leadership review (Apr 1 - Jul 15, 2026).

Root `index.html` is the landing page and links only into `q2/dark-v2/`, the only deck in the repo.
Two older decks (`q2/dark/`, 14 slides, and the top-level `dark/`, pre-Q2, 15 slides) were deleted
when Q2 2026 was wound up; those URLs now 404. Recover from git history if ever needed.

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

## Hiding a slide without deleting it

`fix-nav.py` discovers slides with `glob("slide-*.html")`. To drop a slide from the deck while
keeping the file, rename it out of that glob **in the same directory** - e.g.
`slide-04-vision.html` -> `hidden-slide-04-vision.html`. Do not move it into a subdirectory:
its `deck.css`, `deck.js`, and `../../team/` paths are directory-relative and will break.

A hidden slide keeps its old nav and counter (fix-nav.py no longer manages it) and stays reachable
by direct URL, so its links can dangle after a renumber. Point them at surviving slides by hand.

## Verifying after any nav or slide change

```bash
# dangling links
for f in q2/dark-v2/*.html; do grep -o 'href="slide-[^"]*"' "$f" | sed 's|href="||;s|"||' \
  | sort -u | while read t; do [ -f "q2/dark-v2/$t" ] || echo "MISSING $t (in $f)"; done; done

# counters: expect 01..NN with no gaps, all against the same total
grep -h 'page-number' q2/dark-v2/slide-*.html | sed 's/.*page-number">//;s|</span>||' | sort
```

Slides render on a fixed 1280x720 canvas with no scroll, so **content silently runs under the
footer instead of erroring**. Character-count estimates are unreliable - one was off by 120px on a
real slide. Measure the rendered layout instead: serve the repo (`python3 -m http.server 8766`),
run headless Chrome with `--remote-debugging-port`, and for each slide compare the lowest
`getBoundingClientRect().bottom` under `.main-content` against the `.footer` top.

Two traps when doing that: Chrome serves cached copies and an edit will appear to change nothing
(cache-bust the URL with a query string), and a full-bleed `inset: 0` wrapper always measures 720px
tall, so skip elements taller than ~640px or you get false positives.

## Deploy

```bash
npx vercel deploy --prod --yes --scope awais-projects-5072bb05
npx vercel alias set <new-deployment-url> arbisoft-opensource.vercel.app --scope awais-projects-5072bb05
```

**`--scope awais-projects-5072bb05` is required.** Without it the deploy fails with a bare
`{"status":"error","reason":"deploy_failed","message":"Not authorized"}` even though `vercel whoami`
succeeds and the project is linked. It is a scope-resolution failure, not an auth failure - do not
re-login chasing it.

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

- **No em-dashes, and no spaced hyphens either.** Both read as AI-generated. Rewrite the sentence:
  use a full stop, a comma, or a colon, and vary which one so a single substitute does not become
  the new tell. The deck was swept clean of all 77 spaced hyphens on 2026-08-26.
- Mark unverified facts with `<!-- TODO: ... -->` rather than inventing specifics. Slides go in
  front of leadership; a plausible-looking wrong number is worse than a visible gap.
- Numbered cards (01/02/03) over emoji icons.
- Font Awesome 6.4.0 and Google Fonts (Inter + JetBrains Mono) load from CDN per slide.
- Team photos live in `/team/`, referenced from q2 slides as `../../team/<name>.jpg`.

## Working style

Terse. Drop articles and filler.

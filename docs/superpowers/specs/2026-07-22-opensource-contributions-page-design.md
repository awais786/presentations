# Open Source Contributions Page - Design

Date: 2026-07-22
Status: Approved

## Purpose

A standalone marketing/community page showcasing Arbisoft's open source contributions
over a rolling 12-month window. Audience is the open source community - maintainers,
conference organisers, upstream contacts - so the page is peer-facing credibility
rather than a sales pitch.

## Audience and framing

Primary audience: the open source community.

Consequences for the design:

- Projects lead the page. No individual contributor profiles, no team photos.
- Depth of involvement is the organising principle, not raw volume.
- Every project card links to the repository the work actually lives in, so a reader
  clicking through never finds something that contradicts the page.
- Tone is factual. Numbers are stated plainly with their window and source.

## Data

### Contributors tracked

Six GitHub handles:

- `awais786`
- `usamasadiq`
- `hunzlahmalik`
- `aznszn`
- `AhtishamShahid`
- `jawad-khan`

### Metric

Merged pull requests authored by those handles, public repositories only.

Window: rolling last 365 days from the date the refresh script runs. The page displays
both the window description ("last 12 months") and an explicit last-updated date.

### Baseline (probe, 2026-07-22)

450 merged PRs across ~75 repositories and 20 organisations.

Per handle: awais786 189, usamasadiq 123, AhtishamShahid 44, jawad-khan 43,
aznszn 28, hunzlahmalik 23.

These are baseline figures. Actual page numbers come from the script at build time and
will differ as the rolling window moves.

### What is not counted

The metric is authored merged PRs only. Code reviews given, issues filed and triaged,
and commits outside PRs are out of scope for this version. This is stated on the page
so the numbers are not mistaken for total activity.

## Tiering

Four tiers, ordered by depth of relationship to the project. Tier assignment is by
repository owner organisation, configured explicitly in the refresh script.

### Tier 1 - We Maintain

Orgs: `openedx`, `edx`

Approximately 120 PRs across ~35 repositories.

Headline credential: `awais786` and `usamasadiq` are Open edX **core contributors**.
This is the strongest peer-facing signal on the page and gets the most visual weight.

Core contributor status is hand-curated data. It lives in a separate block that the
refresh script never overwrites.

Notable repos: `openedx-platform` (49), `edx-repo-health` (12),
`tutor-contrib-platform-notifications` (6), `wg-maintenance` (5), `repo-tools` (5),
plus roughly 30 more across the org.

### Tier 2 - We Contribute

Orgs: `meilisearch`, `BerriAI`, `wagtail`, `rust-lang`, `apache`, `celery`,
`BurntSushi`, `riscv-non-isa`, `overhangio`, `hactar-is`

Approximately 27 PRs across 10 organisations.

Rendered as a badge wall rather than large cards. Individually small numbers, but the
breadth is the point: contributions landed in `rust-lang/rustfmt`, `apache/devlake`,
`celery/django-celery-results`, `BurntSushi/jiff`, `riscv-non-isa`, `wagtail/wagtail`,
and 16 PRs to `meilisearch` client libraries.

### Tier 3 - We Build With

Org: `Pressingly`

Approximately 188 PRs across 12 repositories.

Projects: Plane (24), SurfSense (22), Penpot (22), Outline (20), Twenty (14),
MCP servers for Plane/SurfSense/Outline (36 combined), FOSS SSO e2e suite (45).

**Known caveat, decided deliberately.** All `Pressingly/*` repositories are forks.
Parents are `makeplane/plane`, `twentyhq/twenty`, `penpot/penpot`, `outline/outline`,
and `MODSetter/SurfSense`. This work landed in the fork, not upstream.

The project owner was shown this finding and chose to present the work as
contributions to those projects. The mitigation carried into the design: each card
links to the `Pressingly/*` repository where the code actually lives, so the page never
asserts something a click would contradict.

### Tier 4 - We Release

Orgs: the six contributor handles, plus `arbisoft`, `valkrypton`, `mubbsharanwar`,
`ChashmaGenie`

Tools and projects released to the community rather than contributed to someone else's
project. Includes the Wagtail trio (`wagtail-image-from-url`, `wagtail-ai-chat`,
`wagtail-meilisearch`), MCP servers, `policy-chatbot`, `hr_assistant`, and the
`moneta_devstack_e2e_tests` suite (49).

**Exclusion rule.** Repositories that are forks owned by a tracked handle are excluded
entirely. These are personal working forks where PRs are typically self-merged, and
counting them would inflate the total without representing released work. This drops
approximately four repositories including `awais786/twenty`, `awais786/bakerydemo`,
`awais786/meilisearch-python`, and `UsamaSadiq/edx-platform`.

### Unclassified orgs

Any organisation not present in the tier config is written to the JSON as
`tier: null` and printed as a warning when the script runs. The page does not render
unclassified entries. This forces an explicit editorial decision for each new org
rather than silently defaulting.

## Page structure

Single scrollable page, dark theme.

1. **Hero** - headline figure ("N merged pull requests. 12 months. N repositories."),
   subtitle naming the window and last-updated date, stat band: total PRs / repos /
   orgs / 2 Open edX core contributors.
2. **Tier 1 - We Maintain** - core contributor badges, then repo grid.
3. **Tier 2 - We Contribute** - badge wall.
4. **Tier 3 - We Build With** - project cards.
5. **Tier 4 - We Release** - project cards.
6. **Ledger** - collapsible table of every counted repository with PR count, tier, and
   an outbound link. Sortable by repo name and PR count.
7. **Footer** - methodology note (what is counted, what is not, window, data source),
   link to opensource.arbisoft.com.

## Visual design

Reuses the dark deck's tokens for brand consistency:

- Background `#0f172a` to `#1e293b` gradient, 40x40 grid overlay at
  `rgba(255,255,255,0.03)`
- Primary blue `#3b82f6`, accent gradient `#60a5fa` to `#a78bfa`
- Text `#f8fafc` primary, `#cbd5e1` / `#94a3b8` secondary, `#64748b` muted
- Cards `rgba(30,41,59,0.5)` with `rgba(255,255,255,0.08)` border
- Inter (300-800) and JetBrains Mono (400-500), Font Awesome 6.4.0

Departures from the deck: this is a responsive scrolling page, not a fixed 1280x720
canvas. No slide navigation. Numbered section markers (01/02/03) per the established
preference over emoji icons.

Content uses hyphens, not em-dashes.

## Components

### `refresh-contributions.py`

Follows the existing repo pattern (`fix-nav.py`, `inject-dark-nav.py`): standalone
Python script, no dependencies beyond the standard library.

Responsibilities:

1. For each of the six handles, query the GitHub search API for merged PRs created in
   the last 365 days, paging to completion.
2. Resolve each repository's fork status and parent (cached per repo to limit calls).
3. Apply the self-owned-fork exclusion rule.
4. Assign a tier per repository from the org tier config; warn on unclassified.
5. Aggregate: totals, per-tier rollups, per-repo counts.
6. Write `opensource/contributions.json` with a generation timestamp and window bounds.

Rate limiting: unauthenticated GitHub search allows 10 requests/minute. The script
sleeps between calls accordingly and uses `GH_TOKEN` from the environment when present
to raise the limit. It must not hard-fail on a rate limit - back off and retry.

The script never writes the curated block (core contributor status). That data lives
separately and is merged at render time.

### `opensource/contributions.json`

Generated artifact, committed to the repo so the page is fully static.

Shape: generation metadata (timestamp, window start/end), totals, an array of tier
objects each containing its repositories, and the list of unclassified orgs.

### `opensource/index.html`

Self-contained page. Inline CSS and JS, reads the baked JSON. No build step, no
runtime API calls, no external dependencies beyond the existing Google Fonts and Font
Awesome CDN links the deck already uses.

## Files

```
opensource/index.html          # the page, self-contained
opensource/contributions.json  # generated artifact, committed
refresh-contributions.py       # generator + tier config + curated data block
```

## Deploy

Existing flow, unchanged:

```
npx vercel deploy --prod --yes
npx vercel alias set <new-url> arbisoft-opensource.vercel.app
```

Page is reachable at `/opensource/`. The deck at `/dark/` and `/light/` is untouched.

## Refresh workflow

1. Run `python3 refresh-contributions.py`
2. Review the diff on `contributions.json`, resolve any unclassified-org warnings by
   adding them to the tier config
3. Commit and deploy

Intended cadence: before any marketing push.

## Out of scope

- Live GitHub API calls from the browser
- Individual contributor profiles or team photos
- Code review, issue, and commit metrics
- Light theme variant
- Upstreaming the Pressingly fork work

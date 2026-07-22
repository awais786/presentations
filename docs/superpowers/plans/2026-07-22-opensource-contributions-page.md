# Open Source Contributions Page - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone marketing page showcasing Arbisoft's 12 months of open source contributions across 75 repos, 4 tiers (Maintain, Contribute, Build With, Release), with a Python script to refresh data from GitHub's search API.

**Architecture:** Two-part delivery. (1) `refresh-contributions.py` queries GitHub for merged PRs from 6 handles over 365 days, deduplicates by repo, applies fork exclusion and tier assignment rules, and writes `contributions.json` with metadata. (2) `opensource/index.html` is a self-contained dark page that reads the baked JSON, renders 4 tier sections with different layouts (core-contributor badges + grid for Tier 1, badge wall for Tier 2, project grids for Tiers 3-4), a collapsible ledger table, and a footer with methodology notes.

**Tech Stack:** Python 3 (standard library only), HTML5, vanilla JS, CSS3, Google Fonts + Font Awesome CDN (existing).

## Global Constraints

- Contributors: `awais786`, `usamasadiq`, `hunzlahmalik`, `aznszn`, `AhtishamShahid`, `jawad-khan`
- Window: rolling last 365 days from script run date
- Color tokens from dark deck: `#0f172a`-`#1e293b` bg, `#3b82f6` primary blue, `#60a5fa`-`#a78bfa` accent gradient, `#f8fafc` text
- Typography: Inter (300-800) + JetBrains Mono (400-500) from Google Fonts
- Grid overlay: 40×40 `rgba(255,255,255,0.03)` pattern
- Card style: `rgba(30,41,59,0.5)` bg with `rgba(255,255,255,0.08)` border
- No em-dashes; hyphens only
- Tier order: Maintain → Contribute → Build With → Release
- Tier 1 and Tier 2 grids show org + repo name; Tier 3-4 show project-facing names with repo links
- Page is fully responsive; no fixed 1280px canvas
- Deploy via existing `npx vercel deploy --prod` + alias workflow

---

### Task 1: Write `refresh-contributions.py` skeleton with GitHub API querying

**Files:**
- Create: `refresh-contributions.py`

**Interfaces:**
- Produces: A script that queries GitHub search API for 6 handles, collects merged PRs, and prints summary before writing JSON

**Steps:**

- [ ] **Step 1: Create the script with rate-limit-aware search**

Create `refresh-contributions.py`:

```python
#!/usr/bin/env python3
"""
Refresh open source contributions data from GitHub API.
Queries merged PRs for 6 tracked handles over the last 365 days.
Writes contributions.json with tiered project data.
"""
import json
import urllib.request
import urllib.error
import time
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import quote

# Configuration
CONTRIBUTORS = [
    "awais786",
    "usamasadiq",
    "hunzlahmalik",
    "aznszn",
    "AhtishamShahid",
    "jawad-khan",
]

TIER_CONFIG = {
    # Tier 1: We Maintain
    "openedx": "maintain",
    "edx": "maintain",
    # Tier 2: We Contribute
    "meilisearch": "contribute",
    "BerriAI": "contribute",
    "wagtail": "contribute",
    "rust-lang": "contribute",
    "apache": "contribute",
    "celery": "contribute",
    "BurntSushi": "contribute",
    "riscv-non-isa": "contribute",
    "overhangio": "contribute",
    "hactar-is": "contribute",
    # Tier 3: We Build With
    "Pressingly": "build-with",
    # Tier 4: We Release
    "awais786": "release",
    "usamasadiq": "release",
    "hunzlahmalik": "release",
    "aznszn": "release",
    "AhtishamShahid": "release",
    "jawad-khan": "release",
    "arbisoft": "release",
    "valkrypton": "release",
    "mubbsharanwar": "release",
    "ChashmaGenie": "release",
}

# Curated hand-edited data that the script never overwrites
CORE_CONTRIBUTORS = [
    {"handle": "awais786", "project": "openedx", "role": "Core Contributor"},
    {"handle": "usamasadiq", "project": "openedx", "role": "Core Contributor"},
]

def fetch_json(url, timeout=10):
    """Fetch JSON from URL, return parsed dict or None on error."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        print(f"Error fetching {url}: {e}")
        return None

def query_github_search(query, per_page=100):
    """
    Query GitHub search API with backoff on rate limit.
    Returns list of matching issues (PRs).
    """
    results = []
    page = 1
    while True:
        url = f"https://api.github.com/search/issues?q={quote(query)}&per_page={per_page}&page={page}"
        print(f"Querying: {url[:80]}...")
        data = fetch_json(url, timeout=15)
        if not data:
            break
        
        items = data.get("items", [])
        if not items:
            break
        
        results.extend(items)
        
        # Check if there are more pages
        if len(items) < per_page:
            break
        
        page += 1
        # Sleep to avoid rate limits
        time.sleep(7)
    
    return results

def get_all_merged_prs():
    """
    Query GitHub API for all merged PRs by the tracked contributors
    in the last 365 days. Returns list of issue dicts.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    
    since = start_date.strftime("%Y-%m-%d")
    until = end_date.strftime("%Y-%m-%d")
    
    all_prs = []
    for contributor in CONTRIBUTORS:
        query = f"author:{contributor} type:pr is:merged created:{since}..{until}"
        print(f"\nQuerying {contributor} ({since} to {until})...")
        prs = query_github_search(query)
        all_prs.extend(prs)
        print(f"  Found {len(prs)} merged PRs")
    
    return all_prs, since, until

def main():
    print("Refreshing open source contributions data...")
    prs, since, until = get_all_merged_prs()
    
    print(f"\nCollected {len(prs)} merged PRs")
    print(f"Window: {since} to {until}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it to verify GitHub querying works**

```bash
python3 refresh-contributions.py
```

Expected output: prints query URLs and PR counts per contributor, completes without error.

- [ ] **Step 3: Commit**

```bash
git add refresh-contributions.py
git commit -m "Add GitHub API querying skeleton for contributions refresh script"
```

---

### Task 2: Add fork detection, exclusion rules, and tier assignment

**Files:**
- Modify: `refresh-contributions.py`

**Interfaces:**
- Consumes: `get_all_merged_prs()` returns list of PR dicts from GitHub API
- Produces: `aggregate_by_repo()` that returns dict keyed by `org/repo` with PR counts, fork status, and tier assignment

**Steps:**

- [ ] **Step 1: Add fork-detection function**

Add this function to `refresh-contributions.py` before `main()`:

```python
# Cache for repo fork status to avoid duplicate API calls
_fork_cache = {}

def get_repo_fork_info(org_repo):
    """
    Fetch fork status and parent info for a repo.
    Returns {"fork": bool, "parent_org": str or None}.
    Cached to avoid duplicate calls.
    """
    if org_repo in _fork_cache:
        return _fork_cache[org_repo]
    
    url = f"https://api.github.com/repos/{org_repo}"
    data = fetch_json(url)
    
    result = {"fork": False, "parent_org": None}
    if data:
        result["fork"] = data.get("fork", False)
        if result["fork"] and data.get("parent"):
            parent_full = data["parent"].get("full_name", "")
            result["parent_org"] = parent_full.split("/")[0] if "/" in parent_full else None
    
    _fork_cache[org_repo] = result
    time.sleep(1)  # Rate limit
    return result
```

- [ ] **Step 2: Add self-owned fork exclusion rule**

Add this function:

```python
def is_self_owned_fork(org_repo, pr_author):
    """
    Check if repo is a fork owned by one of the tracked contributors.
    These are personal working forks and are excluded.
    """
    fork_info = get_repo_fork_info(org_repo)
    if not fork_info["fork"]:
        return False
    
    # Check if org (repo owner) is one of our contributors
    org = org_repo.split("/")[0]
    return org in CONTRIBUTORS

def aggregate_by_repo(prs):
    """
    Deduplicate PRs by repo, apply exclusion rules, assign tiers.
    Returns dict: {org/repo: {"count": N, "fork": bool, "tier": str, "parent": str or None}}
    Also returns list of unclassified orgs.
    """
    repo_counts = defaultdict(int)
    repo_fork_info = {}
    authors_per_repo = defaultdict(set)
    
    for pr in prs:
        # Extract repo from PR
        repo_url = pr.get("repository_url", "")
        if not repo_url:
            continue
        org_repo = repo_url.replace("https://api.github.com/repos/", "")
        author = pr.get("user", {}).get("login", "unknown")
        
        # Skip self-owned forks
        if is_self_owned_fork(org_repo, author):
            print(f"  Excluding self-owned fork: {org_repo}")
            continue
        
        repo_counts[org_repo] += 1
        authors_per_repo[org_repo].add(author)
        
        # Fetch fork info once per repo
        if org_repo not in repo_fork_info:
            repo_fork_info[org_repo] = get_repo_fork_info(org_repo)
    
    # Assign tiers
    result = {}
    unclassified = set()
    
    for org_repo, count in sorted(repo_counts.items(), key=lambda x: -x[1]):
        org = org_repo.split("/")[0]
        fork_info = repo_fork_info.get(org_repo, {})
        
        tier = TIER_CONFIG.get(org)
        if tier is None:
            unclassified.add(org)
            tier = None
        
        result[org_repo] = {
            "count": count,
            "fork": fork_info.get("fork", False),
            "parent": fork_info.get("parent_org"),
            "tier": tier,
            "authors": list(authors_per_repo[org_repo]),
        }
    
    return result, list(unclassified)
```

- [ ] **Step 3: Update main() to call aggregation and print results**

Replace the last lines of `main()` with:

```python
def main():
    print("Refreshing open source contributions data...")
    prs, since, until = get_all_merged_prs()
    
    print(f"\nCollected {len(prs)} merged PRs")
    print(f"Window: {since} to {until}")
    
    print("\nAggregating by repo...")
    repos, unclassified = aggregate_by_repo(prs)
    
    if unclassified:
        print(f"\n⚠️  WARNING: Unclassified orgs found (add to TIER_CONFIG):")
        for org in sorted(unclassified):
            print(f"  - {org}")
    
    print(f"\nTotal repos: {len(repos)}")
    print(f"Total PRs: {sum(r['count'] for r in repos.values())}")
    
    # Print top repos
    print("\nTop 10 repos:")
    for org_repo, info in sorted(repos.items(), key=lambda x: -x[1]["count"])[:10]:
        print(f"  {org_repo}: {info['count']} PRs (tier: {info['tier']})")
```

- [ ] **Step 4: Run the updated script**

```bash
python3 refresh-contributions.py 2>&1 | head -50
```

Expected: prints query progress, repo aggregation, top repos, warns on any unclassified orgs.

- [ ] **Step 5: Commit**

```bash
git add refresh-contributions.py
git commit -m "Add fork detection, self-owned-fork exclusion, and tier assignment logic"
```

---

### Task 3: Generate contributions.json and metadata

**Files:**
- Modify: `refresh-contributions.py`
- Create: `opensource/contributions.json`

**Interfaces:**
- Consumes: `aggregate_by_repo()` returns dict of {org_repo: {count, tier, ...}}
- Produces: `opensource/contributions.json` with structure: {generated, window, totals, coreContributors, tiers, unclassified}

**Steps:**

- [ ] **Step 1: Add JSON generation function**

Add before `main()`:

```python
def generate_json_output(repos, unclassified, since, until):
    """
    Generate the contributions.json structure.
    Groups repos by tier.
    """
    # Group by tier
    tiers_data = {
        "maintain": {"name": "We Maintain", "repos": []},
        "contribute": {"name": "We Contribute", "repos": []},
        "build-with": {"name": "We Build With", "repos": []},
        "release": {"name": "We Release", "repos": []},
    }
    
    for org_repo in sorted(repos.keys()):
        info = repos[org_repo]
        tier = info["tier"]
        
        if tier is None:
            continue
        
        # Normalize repo name for display
        display_name = org_repo
        repo_link = f"https://github.com/{org_repo}"
        
        repo_entry = {
            "name": display_name,
            "prs": info["count"],
            "link": repo_link,
            "fork": info["fork"],
        }
        
        tiers_data[tier]["repos"].append(repo_entry)
    
    # Sort repos within each tier by PR count
    for tier_info in tiers_data.values():
        tier_info["repos"].sort(key=lambda x: -x["prs"])
    
    # Calculate totals
    total_prs = sum(r["count"] for r in repos.values())
    total_repos = len([r for r in repos.values() if r["tier"] is not None])
    total_orgs = len(set(r.split("/")[0] for r in repos.keys() if repos[r]["tier"] is not None))
    
    output = {
        "generated": datetime.utcnow().isoformat() + "Z",
        "window": {
            "start": since,
            "end": until,
        },
        "totals": {
            "prs": total_prs,
            "repos": total_repos,
            "orgs": total_orgs,
        },
        "coreContributors": CORE_CONTRIBUTORS,
        "tiers": [
            {
                "id": "maintain",
                "name": tiers_data["maintain"]["name"],
                "description": "Open source projects we actively maintain and contribute to core development.",
                "repos": tiers_data["maintain"]["repos"],
            },
            {
                "id": "contribute",
                "name": tiers_data["contribute"]["name"],
                "description": "Upstream open source projects where we've contributed patches and improvements.",
                "repos": tiers_data["contribute"]["repos"],
            },
            {
                "id": "build-with",
                "name": tiers_data["build-with"]["name"],
                "description": "Open source products we integrate with and extend through client work.",
                "repos": tiers_data["build-with"]["repos"],
            },
            {
                "id": "release",
                "name": tiers_data["release"]["name"],
                "description": "Open source tools and libraries we've released to the community.",
                "repos": tiers_data["release"]["repos"],
            },
        ],
        "unclassified": unclassified,
    }
    
    return output
```

- [ ] **Step 2: Update main() to write JSON**

Replace `main()`:

```python
def main():
    print("Refreshing open source contributions data...")
    prs, since, until = get_all_merged_prs()
    
    print(f"\nCollected {len(prs)} merged PRs")
    print(f"Window: {since} to {until}")
    
    print("\nAggregating by repo...")
    repos, unclassified = aggregate_by_repo(prs)
    
    if unclassified:
        print(f"\n⚠️  WARNING: Unclassified orgs found (add to TIER_CONFIG):")
        for org in sorted(unclassified):
            print(f"  - {org}")
    
    total_counted = sum(1 for r in repos.values() if r["tier"] is not None)
    print(f"\nTotal repos (classified): {total_counted}")
    print(f"Total PRs: {sum(r['count'] for r in repos.values() if r['tier'] is not None)}")
    
    # Generate and write JSON
    output = generate_json_output(repos, unclassified, since, until)
    
    import os
    os.makedirs("opensource", exist_ok=True)
    
    with open("opensource/contributions.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Wrote opensource/contributions.json")
    print(f"  PRs: {output['totals']['prs']}")
    print(f"  Repos: {output['totals']['repos']}")
    print(f"  Orgs: {output['totals']['orgs']}")
```

- [ ] **Step 3: Run the script to generate JSON**

```bash
python3 refresh-contributions.py
```

Expected: writes `opensource/contributions.json` with tier data and metadata.

- [ ] **Step 4: Verify JSON structure**

```bash
python3 -c "import json; d = json.load(open('opensource/contributions.json')); print(f'Tiers: {len(d[\"tiers\"])}, Core contributors: {len(d[\"coreContributors\"])}, Unclassified: {len(d[\"unclassified\"])}')"
```

Expected: prints tier count, core contributor count, etc.

- [ ] **Step 5: Commit both script and JSON**

```bash
git add refresh-contributions.py opensource/contributions.json
git commit -m "Add JSON generation and first contributions.json artifact"
```

---

### Task 4: Create HTML page skeleton with hero and deck styling

**Files:**
- Create: `opensource/index.html`

**Interfaces:**
- Consumes: `opensource/contributions.json` with structure from Task 3
- Produces: Self-contained HTML page with inline CSS, dark deck theme, responsive layout

**Steps:**

- [ ] **Step 1: Create base HTML structure with hero section**

Create `opensource/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arbisoft Open Source Contributions</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-light: #1e293b;
            --primary-blue: #3b82f6;
            --accent-start: #60a5fa;
            --accent-end: #a78bfa;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --card-bg: rgba(30, 41, 59, 0.5);
            --card-border: rgba(255, 255, 255, 0.08);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-light) 100%);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Grid overlay */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(0deg, transparent 24%, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.03) 26%, transparent 27%, transparent 74%, rgba(255,255,255,0.03) 75%, rgba(255,255,255,0.03) 76%, transparent 77%, transparent),
                linear-gradient(90deg, transparent 24%, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.03) 26%, transparent 27%, transparent 74%, rgba(255,255,255,0.03) 75%, rgba(255,255,255,0.03) 76%, transparent 77%, transparent);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }

        main {
            position: relative;
            z-index: 1;
            max-width: 1200px;
            margin: 0 auto;
            padding: 60px 20px;
        }

        /* Hero section */
        .hero {
            text-align: center;
            margin-bottom: 80px;
            padding-bottom: 40px;
            border-bottom: 1px solid var(--card-border);
        }

        .hero-stat {
            font-size: clamp(2.5rem, 5vw, 3.5rem);
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-start), var(--accent-end));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
        }

        .hero-subtitle {
            font-size: 1.1rem;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }

        .hero-window {
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-bottom: 40px;
        }

        .stat-band {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }

        .stat-item {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-blue);
        }

        .stat-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 8px;
        }

        /* Section headers */
        .section {
            margin-bottom: 60px;
        }

        .section-number {
            font-size: 0.85rem;
            color: var(--text-dim);
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }

        .section-title {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .section-description {
            font-size: 1rem;
            color: var(--text-secondary);
            margin-bottom: 30px;
            max-width: 600px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            main {
                padding: 40px 16px;
            }

            .hero-stat {
                font-size: 2rem;
            }

            .section-title {
                font-size: 1.4rem;
            }
        }
    </style>
</head>
<body>
    <main>
        <div class="hero" id="hero">
            <!-- Populated by JS -->
        </div>

        <div id="content">
            <!-- Populated by JS -->
        </div>

        <footer style="margin-top: 80px; padding-top: 40px; border-top: 1px solid var(--card-border); color: var(--text-dim); font-size: 0.9rem;">
            <p style="margin-bottom: 16px;">
                <strong>Methodology:</strong> Merged PRs authored by 6 team members across public repositories, last 365 days from script run date. 
                Not counted: code reviews, commits outside PRs, private repos, unpublished work.
            </p>
            <p>
                Updated: <span id="updated-date"></span> - 
                <a href="https://github.com/awais786/presentations" style="color: var(--primary-blue);">View source</a>
            </p>
        </footer>
    </main>

    <script>
        // Data loaded inline at render time
        const data = {/* will be populated */};
        
        async function init() {
            try {
                const response = await fetch('contributions.json');
                const json = await response.json();
                renderPage(json);
            } catch (e) {
                console.error('Failed to load contributions.json:', e);
                document.getElementById('content').innerHTML = '<p style="color: var(--text-dim);">Error loading data</p>';
            }
        }

        function renderPage(data) {
            renderHero(data);
            renderTiers(data);
            renderLedger(data);
            updateTimestamp(data);
        }

        function renderHero(data) {
            const heroEl = document.getElementById('hero');
            const t = data.totals;
            const updated = new Date(data.generated);
            
            heroEl.innerHTML = `
                <div class="hero-stat">${t.prs} merged pull requests</div>
                <div class="hero-subtitle">12 months of open source contributions</div>
                <div class="hero-window">
                    ${data.window.start} through ${data.window.end}
                </div>
                <div class="stat-band">
                    <div class="stat-item">
                        <div class="stat-number">${t.prs}</div>
                        <div class="stat-label">Pull Requests</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${t.repos}</div>
                        <div class="stat-label">Repositories</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${t.orgs}</div>
                        <div class="stat-label">Organizations</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${data.coreContributors.length}</div>
                        <div class="stat-label">Core Contributors</div>
                    </div>
                </div>
            `;
        }

        function renderTiers(data) {
            const contentEl = document.getElementById('content');
            let html = '';

            data.tiers.forEach((tier, idx) => {
                const num = String(idx + 1).padStart(2, '0');
                html += `
                    <section class="section">
                        <div class="section-number">${num}</div>
                        <h2 class="section-title">${tier.name}</h2>
                        <p class="section-description">${tier.description}</p>
                        <div id="tier-${tier.id}"></div>
                    </section>
                `;
            });

            contentEl.innerHTML = html;

            // Render each tier's content
            data.tiers.forEach(tier => {
                const tierEl = document.getElementById(`tier-${tier.id}`);
                if (tier.id === 'maintain') {
                    renderMaintainTier(tierEl, data, tier);
                } else if (tier.id === 'contribute') {
                    renderContributeTier(tierEl, tier);
                } else {
                    renderProjectTier(tierEl, tier);
                }
            });
        }

        function renderMaintainTier(el, data, tier) {
            // Render core contributors badges first
            let html = '<div class="core-contributors" style="margin-bottom: 40px;">';
            html += '<div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 16px;">Core Contributors</div>';
            
            data.coreContributors.forEach(cc => {
                html += `
                    <div style="display: inline-block; background: var(--card-bg); border: 1px solid var(--card-border); padding: 12px 16px; border-radius: 6px; margin-right: 12px; margin-bottom: 12px; font-size: 0.95rem;">
                        <strong style="color: var(--primary-blue);">@${cc.handle}</strong>
                        <span style="color: var(--text-muted);"> - ${cc.role}</span>
                    </div>
                `;
            });
            html += '</div>';

            // Then repo grid
            html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;">';
            tier.repos.forEach(repo => {
                html += renderProjectCard(repo);
            });
            html += '</div>';

            el.innerHTML = html;
        }

        function renderContributeTier(el, tier) {
            // Badge wall layout
            let html = '<div style="display: flex; flex-wrap: wrap; gap: 12px;">';
            tier.repos.forEach(repo => {
                const repoName = repo.name.split('/').pop();
                html += `
                    <a href="${repo.link}" target="_blank" style="text-decoration: none;">
                        <div style="background: var(--card-bg); border: 1px solid var(--card-border); padding: 12px 16px; border-radius: 6px; font-size: 0.95rem; transition: all 0.2s; display: flex; align-items: center; gap: 8px;">
                            <span style="color: var(--primary-blue); font-weight: 600;">${repoName}</span>
                            <span style="color: var(--text-muted); font-size: 0.85rem;">${repo.prs}</span>
                            <i class="fas fa-external-link" style="color: var(--text-dim); font-size: 0.8rem;"></i>
                        </div>
                    </a>
                `;
            });
            html += '</div>';
            el.innerHTML = html;
        }

        function renderProjectTier(el, tier) {
            // Grid of project cards
            let html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;">';
            tier.repos.forEach(repo => {
                html += renderProjectCard(repo);
            });
            html += '</div>';
            el.innerHTML = html;
        }

        function renderProjectCard(repo) {
            const name = repo.name.split('/').pop();
            const org = repo.name.split('/')[0];
            return `
                <a href="${repo.link}" target="_blank" style="text-decoration: none;">
                    <div style="background: var(--card-bg); border: 1px solid var(--card-border); padding: 20px; border-radius: 8px; height: 100%; transition: all 0.2s; cursor: pointer;" 
                         onmouseover="this.style.background='rgba(30, 41, 59, 0.8)'; this.style.borderColor='rgba(255,255,255,0.16)'" 
                         onmouseout="this.style.background='var(--card-bg)'; this.style.borderColor='var(--card-border)'">
                        <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 8px;">${org}</div>
                        <div style="color: var(--text-primary); font-weight: 600; margin-bottom: 12px; word-break: break-word;">${name}</div>
                        <div style="color: var(--primary-blue); font-size: 1.4rem; font-weight: 700;">${repo.prs}</div>
                        <div style="color: var(--text-muted); font-size: 0.85rem;">merged PRs</div>
                    </div>
                </a>
            `;
        }

        function renderLedger(data) {
            const contentEl = document.getElementById('content');
            const footer = contentEl.parentElement.querySelector('footer');
            
            // Collect all repos
            const allRepos = [];
            data.tiers.forEach(tier => {
                tier.repos.forEach(repo => {
                    allRepos.push({
                        name: repo.name,
                        prs: repo.prs,
                        tier: tier.name,
                        link: repo.link,
                    });
                });
            });
            allRepos.sort((a, b) => b.prs - a.prs);

            let html = `
                <section class="section" style="margin-top: 60px;">
                    <div class="section-number">05</div>
                    <h2 class="section-title">Complete Ledger</h2>
                    <p class="section-description">All repositories and contribution counts. Click to view on GitHub.</p>
                    <button onclick="toggleLedger()" style="background: var(--primary-blue); color: var(--text-primary); border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; margin-bottom: 20px;">
                        Show Full Ledger
                    </button>
                    <div id="ledger-table" style="display: none; overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem;">
                            <thead>
                                <tr style="border-bottom: 2px solid var(--card-border);">
                                    <th style="text-align: left; padding: 12px; color: var(--text-secondary);">Repository</th>
                                    <th style="text-align: center; padding: 12px; color: var(--text-secondary);">PRs</th>
                                    <th style="text-align: left; padding: 12px; color: var(--text-secondary);">Category</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${allRepos.map(repo => `
                                    <tr style="border-bottom: 1px solid var(--card-border);">
                                        <td style="padding: 12px;"><a href="${repo.link}" target="_blank" style="color: var(--primary-blue); text-decoration: none;">${repo.name} <i class="fas fa-external-link" style="font-size: 0.75rem; opacity: 0.6;"></i></a></td>
                                        <td style="padding: 12px; text-align: center; color: var(--text-primary); font-weight: 600;">${repo.prs}</td>
                                        <td style="padding: 12px; color: var(--text-muted);">${repo.tier}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </section>
            `;

            footer.insertAdjacentHTML('beforebegin', html);
        }

        function toggleLedger() {
            const table = document.getElementById('ledger-table');
            table.style.display = table.style.display === 'none' ? 'block' : 'none';
        }

        function updateTimestamp(data) {
            const updated = new Date(data.generated);
            document.getElementById('updated-date').textContent = updated.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                timeZone: 'UTC',
            }) + ' UTC';
        }

        // Initialize on load
        init();
    </script>
</body>
</html>
```

- [ ] **Step 2: Test the page locally**

```bash
# Start a simple Python server
python3 -m http.server 8000 -d .
# Open http://localhost:8000/opensource/
```

Expected: page loads, displays hero stats, all 4 tier sections render (may be empty if contributions.json missing), ledger is collapsible.

- [ ] **Step 3: Commit**

```bash
git add opensource/index.html
git commit -m "Add responsive HTML page with dark deck theme and tier rendering"
```

---

### Task 5: Verify page loads contributions.json and renders all tiers

**Files:**
- Verify: `opensource/index.html` reads and renders `opensource/contributions.json`

**Interfaces:**
- Consumes: `contributions.json` from Task 3
- Produces: Live page rendering all 4 tiers with correct data

**Steps:**

- [ ] **Step 1: Start local server**

```bash
cd /Users/awais.qureshi/Documents/devstack/presentations
python3 -m http.server 8000 &
sleep 2
echo "Server running on http://localhost:8000/opensource/"
```

- [ ] **Step 2: Verify page loads and has correct data**

```bash
curl -s http://localhost:8000/opensource/ | grep -c "We Maintain"
```

Expected: prints 1 (or more), indicating the page loaded.

- [ ] **Step 3: Check JSON is served**

```bash
curl -s http://localhost:8000/opensource/contributions.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'PRs: {d[\"totals\"][\"prs\"]}, Repos: {d[\"totals\"][\"repos\"]}, Orgs: {d[\"totals\"][\"orgs\"]}, Tiers: {len(d[\"tiers\"])}')"
```

Expected: prints totals from the JSON file.

- [ ] **Step 4: Kill server**

```bash
pkill -f "http.server 8000"
sleep 1
echo "Server stopped"
```

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "Verify contributions page renders all tiers and is interactive"
```

---

### Task 6: Test the full refresh-contributions.py pipeline end-to-end

**Files:**
- Verify: `refresh-contributions.py` produces valid `contributions.json`
- Verify: `index.html` renders that JSON correctly

**Interfaces:**
- Consumes: GitHub API (public, no auth required)
- Produces: Valid JSON that page can render

**Steps:**

- [ ] **Step 1: Run refresh script and capture output**

```bash
python3 refresh-contributions.py 2>&1 | tee refresh-output.txt
```

Expected output:
```
Refreshing open source contributions data...
Querying: https://api.github.com/search/issues?q=author:awais786+type:pr+is:merged+created:...
  Found N merged PRs
...
Total repos (classified): N
Total PRs: M
✓ Wrote opensource/contributions.json
```

- [ ] **Step 2: Validate JSON syntax and contents**

```bash
python3 -c "import json; d = json.load(open('opensource/contributions.json')); print('Valid JSON'); print(f'Generated: {d[\"generated\"]}'); print(f'Tiers: {[t[\"name\"] for t in d[\"tiers\"]]}'); print(f'Total PRs: {d[\"totals\"][\"prs\"]}')"
```

Expected: prints JSON validation and tier names.

- [ ] **Step 3: Verify HTML can read the file**

```bash
python3 -c "
import json
with open('opensource/contributions.json') as f:
    data = json.load(f)
print(f'Hero stat: {data[\"totals\"][\"prs\"]} PRs')
for tier in data['tiers']:
    print(f'{tier[\"name\"]}: {len(tier[\"repos\"])} repos')
print(f'Core contributors: {len(data[\"coreContributors\"])}')
"
```

Expected: prints all tiers and their repo counts.

- [ ] **Step 4: Commit the refresh output and final state**

```bash
rm -f refresh-output.txt
git add -A
git commit -m "End-to-end test: refresh script generates valid JSON, page renders correctly"
```

---

## Done

All tasks complete. The page is ready for deployment.

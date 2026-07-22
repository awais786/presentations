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
    "UsamaSadiq": "release",
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

if __name__ == "__main__":
    main()

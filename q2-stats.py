#!/usr/bin/env python3
"""Per-author merged-PR counts for a date window, filtered to real OSS work.

Reuses TIER_CONFIG from refresh-contributions.py so "what counts as open source"
has one definition. Queries through the authenticated `gh` CLI (5000 req/hr)
rather than the unauthenticated urllib path in refresh-contributions.py.

    ./q2-stats.py --since 2026-04-01 --until 2026-07-15
"""
import argparse
import collections
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# refresh-contributions.py has a hyphen, so it needs importlib rather than import
spec = importlib.util.spec_from_file_location(
    "refresh_contributions", os.path.join(HERE, "refresh-contributions.py")
)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

TIER_CONFIG = rc.TIER_CONFIG

# Tiers that represent upstream open source work, as opposed to our own releases
UPSTREAM_TIERS = {"maintain", "contribute", "build-with"}


def gh_search(query):
    """Page through the GitHub search API via gh. Returns list of PR items."""
    items, page = [], 1
    while True:
        out = subprocess.run(
            ["gh", "api", "-X", "GET", "search/issues",
             "-f", f"q={query}", "-f", "per_page=100", "-f", f"page={page}"],
            capture_output=True, text=True,
        )
        if out.returncode != 0:
            print(f"  query failed: {out.stderr.strip()[:200]}", file=sys.stderr)
            break
        batch = json.loads(out.stdout).get("items", [])
        if not batch:
            break
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def counts_for(handle, since, until):
    """Return {tier: n, ...} plus unclassified orgs for one author."""
    prs = gh_search(f"is:pr author:{handle} is:merged merged:{since}..{until}")
    by_tier = collections.Counter()
    unclassified = collections.Counter()
    repos, orgs = set(), set()

    for pr in prs:
        org_repo = pr.get("repository_url", "").replace(
            "https://api.github.com/repos/", "")
        if "/" not in org_repo:
            continue
        org = org_repo.split("/")[0]
        # personal working repos/forks owned by the author are not contributions
        if org.lower() == handle.lower():
            continue
        tier = TIER_CONFIG.get(org)
        if tier is None:
            unclassified[org] += 1
        else:
            by_tier[tier] += 1
            repos.add(org_repo)
            orgs.add(org)
    return by_tier, unclassified, len(prs), repos, orgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-04-01")
    ap.add_argument("--until", default="2026-07-15")
    ap.add_argument("--handles", nargs="+",
                    default=["awais786", "UsamaSadiq", "AhtishamShahid", "awais-ansari"])
    args = ap.parse_args()

    print(f"Window: {args.since} .. {args.until}\n")
    print(f"{'handle':<18}{'raw':>6}{'upstream':>10}{'release':>9}{'total OSS':>11}")
    print("-" * 54)

    all_unclassified = collections.Counter()
    all_repos, all_orgs = set(), set()
    grand_upstream = 0
    for h in args.handles:
        by_tier, unclassified, raw, repos, orgs = counts_for(h, args.since, args.until)
        upstream = sum(n for t, n in by_tier.items() if t in UPSTREAM_TIERS)
        release = by_tier.get("release", 0)
        grand_upstream += upstream
        all_unclassified.update(unclassified)
        all_repos |= repos
        all_orgs |= orgs
        print(f"{h:<18}{raw:>6}{upstream:>10}{release:>9}{upstream + release:>11}")
        for t, n in sorted(by_tier.items(), key=lambda x: -x[1]):
            print(f"    {t:<16}{n}")

    print("-" * 54)
    print(f"{'TOTAL upstream':<18}{'':>6}{grand_upstream:>10}")
    print(f"Distinct repos: {len(all_repos)}  Distinct orgs/projects: {len(all_orgs)}")

    if all_unclassified:
        print("\nUnclassified orgs (not in TIER_CONFIG, excluded from OSS totals):")
        for org, n in all_unclassified.most_common():
            print(f"  {org:<28}{n}")


if __name__ == "__main__":
    main()

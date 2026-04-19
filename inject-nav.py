#!/usr/bin/env python3
"""Inject deck.css/deck.js refs + nav markup into each slide-NN-*.html.

Shared CSS = deck.css · Shared JS = deck.js · data-attrs on <body> drive keyboard nav.
"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
slides = sorted(glob.glob(os.path.join(HERE, "slide-*.html")))

NAV_MARKER_START = "<!-- NAV:START -->"
NAV_MARKER_END = "<!-- NAV:END -->"
HEAD_MARKER_START = "<!-- DECK-HEAD:START -->"
HEAD_MARKER_END = "<!-- DECK-HEAD:END -->"
BODY_MARKER_START = "<!-- DECK-BODY:START -->"
BODY_MARKER_END = "<!-- DECK-BODY:END -->"

first_slide = os.path.basename(slides[0])
last_slide = os.path.basename(slides[-1])

head_block = f"""{HEAD_MARKER_START}
<link rel="stylesheet" href="deck.css">
<script src="deck.js" defer></script>
{HEAD_MARKER_END}"""

for i, path in enumerate(slides):
    prev_file = os.path.basename(slides[i - 1]) if i > 0 else ""
    next_file = os.path.basename(slides[i + 1]) if i < len(slides) - 1 else ""
    total = len(slides)
    num = i + 1

    body_attrs = f'data-prev="{prev_file}" data-next="{next_file}" data-first="{first_slide}" data-last="{last_slide}"'

    nav_block = f"""{NAV_MARKER_START}
<a class="deck-nav prev{' disabled' if not prev_file else ''}" href="{prev_file}" title="Previous">&#8249;</a>
<a class="deck-nav next{' disabled' if not next_file else ''}" href="{next_file}" title="Next">&#8250;</a>
<div class="deck-counter">{num:02d} / {total:02d}</div>
{NAV_MARKER_END}"""

    with open(path, "r") as f:
        html = f.read()

    # 1. Inject deck.css/js in head (idempotent)
    head_re = re.compile(re.escape(HEAD_MARKER_START) + r".*?" + re.escape(HEAD_MARKER_END), re.DOTALL)
    if head_re.search(html):
        html = head_re.sub(head_block, html)
    else:
        html = re.sub(r"</head>", head_block + "\n</head>", html, count=1)

    # 2. Set body data attrs (remove old if present, add new)
    html = re.sub(r'<body[^>]*>', f'<body {body_attrs}>', html, count=1)

    # 3. Inject nav block before </body> (replace old inline NAV block if present)
    nav_re = re.compile(re.escape(NAV_MARKER_START) + r".*?" + re.escape(NAV_MARKER_END), re.DOTALL)
    if nav_re.search(html):
        html = nav_re.sub(nav_block, html)
    else:
        html = html.replace("</body>", nav_block + "\n</body>")

    with open(path, "w") as f:
        f.write(html)

print(f"Injected deck.css/deck.js + nav into {len(slides)} slides. Counters /{len(slides):02d}.")

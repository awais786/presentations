#!/usr/bin/env python3
"""Inject floating .deck-nav-float arrow buttons into dark/ slides for presentation visibility."""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
slides = sorted(glob.glob(os.path.join(HERE, "dark", "slide-*.html")))

MARKER_START = "<!-- FLOAT-NAV:START -->"
MARKER_END = "<!-- FLOAT-NAV:END -->"

for i, path in enumerate(slides):
    prev_file = os.path.basename(slides[i - 1]) if i > 0 else ""
    next_file = os.path.basename(slides[i + 1]) if i < len(slides) - 1 else ""

    block = f"""{MARKER_START}
<a class="deck-nav-float prev{' disabled' if not prev_file else ''}" href="{prev_file}" title="Previous">&#8249;</a>
<a class="deck-nav-float next{' disabled' if not next_file else ''}" href="{next_file}" title="Next">&#8250;</a>
{MARKER_END}"""

    with open(path, "r") as f:
        html = f.read()

    pattern = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.DOTALL)
    if pattern.search(html):
        html = pattern.sub(block, html)
    else:
        html = html.replace("</body>", block + "\n</body>")

    with open(path, "w") as f:
        f.write(html)

print(f"Injected floating nav into {len(slides)} dark slides.")

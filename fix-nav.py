#!/usr/bin/env python3
"""Fix body data-prev/data-next attrs based on sorted filename order, for both light/ and dark/."""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

for folder in ["light", "dark"]:
    slides = sorted(glob.glob(os.path.join(HERE, folder, "slide-*.html")))
    total = len(slides)
    first = os.path.basename(slides[0])
    last = os.path.basename(slides[-1])

    for i, path in enumerate(slides):
        prev_f = os.path.basename(slides[i - 1]) if i > 0 else ""
        next_f = os.path.basename(slides[i + 1]) if i < total - 1 else ""
        num = i + 1

        with open(path, "r") as f:
            html = f.read()

        # Fix body data-attrs
        html = re.sub(
            r'<body\s+data-prev="[^"]*"\s+data-next="[^"]*"\s+data-first="[^"]*"\s+data-last="[^"]*">',
            f'<body data-prev="{prev_f}" data-next="{next_f}" data-first="{first}" data-last="{last}">',
            html
        )

        # Fix footer nav-btn href
        if next_f:
            html = re.sub(
                r'<a class="nav-btn[^"]*" href="[^"]*" title="Next">',
                f'<a class="nav-btn" href="{next_f}" title="Next">',
                html
            )
        else:
            html = re.sub(
                r'<a class="nav-btn[^"]*" href="[^"]*" title="[^"]*"><i class="fas fa-chevron-right">',
                f'<a class="nav-btn disabled" href="#" title="End"><i class="fas fa-check">',
                html
            )

        # Fix floating float-nav (dark) or inline nav links (light)
        html = re.sub(
            r'<a class="deck-nav-float prev[^"]*" href="[^"]*" title="Previous">([^<]*)</a>',
            f'<a class="deck-nav-float prev{"" if prev_f else " disabled"}" href="{prev_f}" title="Previous">\\1</a>',
            html
        )
        html = re.sub(
            r'<a class="deck-nav-float next[^"]*" href="[^"]*" title="Next">([^<]*)</a>',
            f'<a class="deck-nav-float next{"" if next_f else " disabled"}" href="{next_f}" title="Next">\\1</a>',
            html
        )
        html = re.sub(
            r'<a class="deck-nav prev[^"]*" href="[^"]*" title="Previous">([^<]*)</a>',
            f'<a class="deck-nav prev{"" if prev_f else " disabled"}" href="{prev_f}" title="Previous">\\1</a>',
            html
        )
        html = re.sub(
            r'<a class="deck-nav next[^"]*" href="[^"]*" title="Next">([^<]*)</a>',
            f'<a class="deck-nav next{"" if next_f else " disabled"}" href="{next_f}" title="Next">\\1</a>',
            html
        )

        # Fix page-number display
        html = re.sub(
            r'<span class="page-number">\d+</span>',
            f'<span class="page-number">{num:02d}</span>',
            html
        )
        html = re.sub(
            r'<div class="deck-counter">\d+\s*/\s*\d+</div>',
            f'<div class="deck-counter">{num:02d} / {total:02d}</div>',
            html
        )

        with open(path, "w") as f:
            f.write(html)

    print(f"{folder}/: fixed nav for {total} slides")

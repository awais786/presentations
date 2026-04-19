#!/usr/bin/env python3
"""Inject arrow-key + button navigation into each slide-NN-*.html so they navigate between each other."""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
slides = sorted(glob.glob(os.path.join(HERE, "slide-*.html")))

NAV_MARKER_START = "<!-- NAV:START -->"
NAV_MARKER_END = "<!-- NAV:END -->"
first_slide = os.path.basename(slides[0])
last_slide = os.path.basename(slides[-1])

for i, path in enumerate(slides):
    prev_file = os.path.basename(slides[i - 1]) if i > 0 else ""
    next_file = os.path.basename(slides[i + 1]) if i < len(slides) - 1 else ""
    total = len(slides)
    num = i + 1

    nav_html = f"""{NAV_MARKER_START}
<style>
  .deck-nav {{ position: fixed; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,.55); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,.2); color: #fff; width: 52px; height: 52px; border-radius: 50%; cursor: pointer; font-size: 26px; font-weight: 700; display: flex; align-items: center; justify-content: center; z-index: 9999; text-decoration: none; transition: background .15s, transform .15s, opacity .2s; opacity: .55; user-select: none; }}
  .deck-nav:hover {{ background: rgba(9,105,218,.95); opacity: 1; transform: translateY(-50%) scale(1.08); }}
  .deck-nav.prev {{ left: 18px; }}
  .deck-nav.next {{ right: 18px; }}
  .deck-nav.disabled {{ opacity: .15; pointer-events: none; }}
  .deck-counter {{ position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,.55); backdrop-filter: blur(10px); color: #fff; padding: 6px 16px; border-radius: 100px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums; z-index: 9999; letter-spacing: 1px; opacity: .6; transition: opacity .2s; }}
  .deck-counter:hover {{ opacity: 1; }}
  body:hover .deck-nav {{ opacity: .85; }}
  @media print {{ .deck-nav, .deck-counter {{ display: none !important; }} }}
</style>
<a class="deck-nav prev{' disabled' if not prev_file else ''}" href="{prev_file}" title="Previous">&#8249;</a>
<a class="deck-nav next{' disabled' if not next_file else ''}" href="{next_file}" title="Next">&#8250;</a>
<div class="deck-counter">{num:02d} / {total:02d}</div>
<script>
(function() {{
  var prev = {repr(prev_file)};
  var next = {repr(next_file)};
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
      if (next) {{ e.preventDefault(); window.location.href = next; }}
    }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
      if (prev) {{ e.preventDefault(); window.location.href = prev; }}
    }} else if (e.key === 'Home') {{
      window.location.href = {repr(first_slide)};
    }} else if (e.key === 'End') {{
      window.location.href = {repr(last_slide)};
    }} else if (e.key === 'f' || e.key === 'F') {{
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    }}
  }});
}})();
</script>
{NAV_MARKER_END}"""

    with open(path, "r") as f:
        html = f.read()

    pattern = re.compile(re.escape(NAV_MARKER_START) + r".*?" + re.escape(NAV_MARKER_END), re.DOTALL)
    if pattern.search(html):
        html = pattern.sub(nav_html, html)
    else:
        html = html.replace("</body>", nav_html + "\n</body>")

    with open(path, "w") as f:
        f.write(html)

print(f"Injected nav into {len(slides)} slides · counters updated to /{len(slides):02d}")

"""Refresh the figures inside index.html, then print the one-pager to writeup.pdf.

    python tools/build_site.py            # figures + PDF
    python tools/build_site.py --no-pdf   # figures only

index.html stays the editable source: only the text between the
<!--FIG:name--> markers (and the /*FIGCSS*/ block) is regenerated.
The PDF needs Playwright with Chromium.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figures  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIGS = {"recall": figures.recall_svg, "iv": figures.iv_svg}


def inject(path: Path) -> None:
    html = path.read_text()
    for name, fn in FIGS.items():
        pat = re.compile(rf"(<!--FIG:{name}-->).*?(<!--/FIG:{name}-->)", re.S)
        if not pat.search(html):
            continue
        html = pat.sub(lambda m: f"{m.group(1)}\n{fn()}\n{m.group(2)}", html)
    html = re.sub(r"(/\*FIGCSS\*/).*?(/\*/FIGCSS\*/)",
                  lambda m: f"{m.group(1)}{figures.FIG_CSS}{m.group(2)}", html, flags=re.S)
    path.write_text(html)
    print("updated", path.relative_to(ROOT))


def pdf(src: Path, out: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM")
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = b.new_page()
        pg.goto(src.as_uri())
        pg.emulate_media(media="print", color_scheme="light")
        pg.wait_for_timeout(300)
        pg.pdf(path=str(out), format="A4", print_background=True,
               margin=dict(top="0", bottom="0", left="0", right="0"))
        b.close()
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    for page in ("index.html", "writeup.html"):
        if (ROOT / page).exists():
            inject(ROOT / page)
    if "--no-pdf" not in sys.argv and (ROOT / "writeup.html").exists():
        pdf(ROOT / "writeup.html", ROOT / "writeup.pdf")

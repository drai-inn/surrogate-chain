"""Inline SVG figures for the write-up, drawn from data/*.json.

Colours are CSS custom properties set by the page (light and dark), so the
same markup themes with the site. Validated pairs (dataviz validator):
light --s1 #3F5FBC / --s2 #C79A4D on #fcfcfb; dark --s1 #6A84DE / --s2 #B8893C
on #141C36.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    return json.loads((ROOT / "data" / name).read_text())


def recall_svg() -> str:
    d = _load("lightning.json")["round3_pool3"]["recall_top1M"]
    rows = [
        ("VDSAI Lightning", d["lightning"], "s1"),
        ("AMPL", d["ampl"], "s2"),
        ("Rank by size", d["size_only"], "base"),
        ("Random picks", d["random"], "base"),
    ]
    W, H = 560, 196
    left, right, top, bar, gap = 128, 52, 12, 20, 18
    xmax = 0.40
    pw = W - left - right
    x = lambda v: left + pw * v / xmax                        # noqa: E731
    out = [f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" '
           'aria-labelledby="fig-recall-t fig-recall-d">',
           '<title id="fig-recall-t">Recall of the docking top 1M on pool_3</title>',
           '<desc id="fig-recall-d">VDSAI Lightning 35.0%, AMPL 32.3%, '
           'rank by heavy-atom count 2.6%, random 1.2%.</desc>']
    yb = top + len(rows) * (bar + gap) - gap + 10
    for t in range(0, 41, 10):
        xt = x(t / 100)
        out.append(f'<line class="grid" x1="{xt:.1f}" x2="{xt:.1f}" y1="{top - 4}" y2="{yb - 6}"/>')
        out.append(f'<text class="tick" x="{xt:.1f}" y="{yb + 8}" text-anchor="middle">{t}%</text>')
    for i, (name, v, cls) in enumerate(rows):
        y0 = top + i * (bar + gap)
        x1 = x(v)
        w = x1 - left
        r = min(4, w)
        # square at the baseline, 4px rounded at the data end
        path = (f"M{left},{y0} H{x1 - r:.1f} Q{x1:.1f},{y0} {x1:.1f},{y0 + r} "
                f"V{y0 + bar - r} Q{x1:.1f},{y0 + bar} {x1 - r:.1f},{y0 + bar} H{left} Z")
        out.append(f'<g class="mark"><title>{name}: {v * 100:.1f}%</title>'
                   f'<rect class="hit" x="0" y="{y0 - gap / 2}" width="{W}" height="{bar + gap}"/>'
                   f'<path class="bar {cls}" d="{path}"/></g>')
        out.append(f'<text class="lab" x="{left - 10}" y="{y0 + bar / 2 + 4.5}" text-anchor="end">{name}</text>')
        out.append(f'<text class="val" x="{x1 + 8:.1f}" y="{y0 + bar / 2 + 4.5}">{v * 100:.1f}%</text>')
    out.append(f'<line class="axis" x1="{left}" x2="{left}" y1="{top - 4}" y2="{yb - 6}"/>')
    out.append("</svg>")
    return "\n".join(out)


def iv_svg() -> str:
    d = _load("kcsa_permeation.json")
    V = d["V_mV"]
    I = [i * 1e12 for i in d["I"]]                                   # A -> pA
    Er = d["reversal_mV"]
    W, H = 560, 250
    left, right, top, bottom = 52, 16, 14, 40
    pw, ph = W - left - right, H - top - bottom
    xmin, xmax, ymin, ymax = -200, 200, -0.2, 1.4
    x = lambda v: left + pw * (v - xmin) / (xmax - xmin)            # noqa: E731
    y = lambda i: top + ph * (ymax - i) / (ymax - ymin)             # noqa: E731
    out = [f'<svg class="fig" viewBox="0 0 {W} {H}" role="img" '
           'aria-labelledby="fig-iv-t fig-iv-d">',
           '<title id="fig-iv-t">KcsA model current against membrane voltage</title>',
           f'<desc id="fig-iv-d">Steady-state current from the electrogenic bond graph, '
           f'140 mM K+ inside, 4 mM outside. It crosses zero at {Er:.2f} mV, the Nernst '
           f'potential for K+.</desc>']
    for t in (-200, -100, 0, 100, 200):
        out.append(f'<line class="grid" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top}" y2="{top + ph}"/>')
        out.append(f'<text class="tick" x="{x(t):.1f}" y="{top + ph + 16}" text-anchor="middle">{t}</text>')
    for t in (0.0, 0.4, 0.8, 1.2):
        out.append(f'<line class="grid" x1="{left}" x2="{left + pw}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>')
        out.append(f'<text class="tick" x="{left - 8}" y="{y(t) + 4:.1f}" text-anchor="end">{t:.1f}</text>')
    out.append(f'<line class="axis" x1="{left}" x2="{left + pw}" y1="{y(0):.1f}" y2="{y(0):.1f}"/>')
    pts = " ".join(f"{x(v):.1f},{y(i):.1f}" for v, i in zip(V, I))
    out.append(f'<polyline class="line s1" points="{pts}"/>')
    # sparse hover targets along the curve
    for v, i in list(zip(V, I))[::4]:
        out.append(f'<g class="mark"><title>{v:.0f} mV: {i:.2f} pA</title>'
                   f'<circle class="hit" cx="{x(v):.1f}" cy="{y(i):.1f}" r="9"/></g>')
    xe, ye = x(Er), y(0)
    out.append(f'<line class="ref" x1="{xe:.1f}" x2="{xe:.1f}" y1="{top}" y2="{top + ph}"/>')
    out.append(f'<g class="mark"><title>Reversal {Er:.2f} mV; Nernst E_K {d["nernst_mV"]:.2f} mV</title>'
               f'<circle class="ring" cx="{xe:.1f}" cy="{ye:.1f}" r="7"/>'
               f'<circle class="dot s2" cx="{xe:.1f}" cy="{ye:.1f}" r="5"/></g>')
    out.append(f'<text class="lab strong" x="{xe - 8:.1f}" y="{top + 16}" text-anchor="end">'
               f'E<tspan class="sub" dy="3">rev</tspan><tspan dy="-3"> = {Er:.2f} mV</tspan></text>')
    out.append(f'<text class="lab" x="{xe - 8:.1f}" y="{top + 34}" text-anchor="end">'
               f'= Nernst E<tspan class="sub" dy="3">K</tspan></text>')
    out.append(f'<text class="tick" x="{left + pw / 2}" y="{H - 4}" text-anchor="middle">'
               'membrane voltage (mV)</text>')
    out.append(f'<text class="tick" x="12" y="{top + ph / 2}" text-anchor="middle" '
               f'transform="rotate(-90 12 {top + ph / 2})">current (pA)</text>')
    out.append("</svg>")
    return "\n".join(out)


FIG_CSS = """
.fig{width:100%;height:auto;display:block;font-family:var(--font-display);overflow:visible}
.fig .grid{stroke:var(--grid);stroke-width:1}
.fig .axis{stroke:var(--axis);stroke-width:1}
.fig .ref{stroke:var(--s2);stroke-width:1;opacity:.55}
.fig .tick{fill:var(--ink-muted);font-size:11px;font-family:var(--font-mono)}
.fig .lab{fill:var(--ink-2);font-size:12.5px}
.fig .lab.strong{fill:var(--ink-1);font-weight:700}
.fig .sub{font-size:9px}
.fig .val{fill:var(--ink-1);font-size:12.5px;font-weight:700;font-family:var(--font-mono)}
.fig .bar.s1{fill:var(--s1)} .fig .bar.s2{fill:var(--s2)} .fig .bar.base{fill:var(--base)}
.fig .line{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.fig .line.s1{stroke:var(--s1)}
.fig .dot.s2{fill:var(--s2)} .fig .ring{fill:var(--surface)}
.fig .hit{fill:transparent}
.fig .mark:hover .bar{filter:brightness(1.12)}
.fig .mark:hover .hit{fill:var(--hover)}
"""

# How far can a chain of surrogates take us in biomolecular interactions?

**OSI Hackathon 2026 · Auckland hub.** Write-up, figures and video for two rungs of the surrogate ladder:

- **Rung 1 · Screening at scale.** VDSAI Lightning, an AttentiveFP docking surrogate. It scored 925M ZINC molecules in 4 h 27 min and recovered 35.0% of the docking top 1M (AMPL 32.3%, random 1.2%) with 381× fewer GPU hours.
- **Rung 2 · Atoms to a cell.** Molecular dynamics → measured diffusivity and learned free energy → thermodynamically consistent bond graph → CellML 2.0. The KcsA reversal potential is −91.30 mV, equal to Nernst E<sub>K</sub>.

| | |
|---|---|
| Site | https://drai-inn.github.io/surrogate-chain/ |
| One-page write-up | [`writeup.pdf`](writeup.pdf) (source [`writeup.html`](writeup.html)) |
| Video | [`assets/video/`](assets/video/), script in [`video/script.md`](video/script.md) |
| Code (rung 2) | https://github.com/jmdowrick/hackathon2026 |
| Data behind the figures | [`data/`](data/) |

Rebuild the figures and PDF with `python tools/build_site.py` (needs Playwright + Chromium; set `CHROMIUM=` to a binary if Playwright's own isn't installed). Panel (b) data comes from `tools/kcsa_data.py`, run inside the team repo.

Text and figures CC BY 4.0; code MIT.

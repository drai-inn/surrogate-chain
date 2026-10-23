# Video script: How far can a chain of surrogates take us?

Final cut: **3:43**, read at natural pace (Kokoro `af_heart`, speed 1.0, no speed-up).
This is the text as spoken. On-screen captions follow it word for word, with numbers written as
digits. The source of truth for both is [`narration.json`](narration.json): each sentence has a
`cap` (caption) and a `say` (pronunciation) form. Figures in brackets are what the scene shows.

---

## 1 · The question (0:00–0:19)

*[Title card over an event photo: "How far can a chain of surrogates take us?" OSI Hackathon 2026 ·
Auckland. The title rises and a chain builds: molecules interact → shape & structure change →
function changes → physiology. A gold bracket: drugs act on the whole system.]*

Physiological outcomes come from molecules interacting. Those interactions change function, and
function is driven by changes in shape and structure. Pharmacology is what drugs do to that whole
system. So how far can a chain of surrogates take us?

## 2 · The ladder (0:19–0:40)

*[Two ladders side by side. Biology: sequence → structure → atoms in motion → cells and tissue.
Machine learning: association models → 3D-aware models → interatomic potentials → multi-scale
models. Arrows from each biology rung to its surrogate; a "Trust" card (ground truth? simple
baseline? where it breaks?). Rung 1 (screening) and rung 2 (atoms to a cell) light up.]*

Biology has a ladder of scales: sequence, structure, atoms in motion, cells and tissue. Machine
learning now has a ladder alongside it, mostly open-weight, mostly new. Each rung swaps an
expensive physical calculation for a learned one, and the catch is trust. In two days in Auckland,
we climbed two rungs.

## 3 · Rung one: screening a billion molecules (0:41–1:40)

*[1,000,000,000 molecules; docking ≈ 100 days. Dock a sample → surrogate ranks the library → dock
only the top.]*

Docking a billion molecules takes about a hundred days. So you train a surrogate on docking scores,
and dock only what it ranks highest.

*[AMPL (GraphConv · TensorFlow) → VDSAI Lightning (AttentiveFP · PyTorch Geometric + Lightning).
Tiles: 13× faster training (2.4 h vs 32.4 h, 3.5M molecules); tuned test R² 0.752 vs 0.690; RMSE
4.41 vs 4.61.]*

We rebuilt that surrogate: VDSAI Lightning, an AttentiveFP graph network replacing AMPL's GraphConv
stack. On three and a half million molecules it trained 13× faster, and after tuning it beat AMPL on
every test metric.

*[Counter ticks to 925,000,000 ZINC molecules · 4 h 27 min · 1 workspace.]*

Then we scored 925 million molecules in under four and a half hours on a single workspace.

*[Bars, recall of the docking top 1M on pool_3 (98.3M molecules): Lightning 35.0%, AMPL 32.3%,
rank by size 2.6%, random 1.2%. 381× fewer GPU hours (0.44 h vs 166.4 h). Docking vs itself:
r = 0.30.]*

Head to head on a 98-million-molecule pool, Lightning recovered 35% of the true docking top
million. AMPL recovered 32%, ranking by size 2.6%, random picks 1.2%. And it used 381× fewer GPU
hours. Two dockings of the same molecules correlate at only 0.3, so the surrogate is now chasing a
noisy target.

## 4 · Rung two: from atoms to a cell (1:40–2:35)

*[Pipeline: MD trajectory → measure D(z) → learn F(z) → find barriers → bond graph → CellML, which
runs inside a heart or kidney cell model.]*

Rung two carries a molecular signal all the way up to physiology. Our pipeline turns a molecular
dynamics trajectory into a model that a heart or kidney cell model can run. It measures diffusion,
learns the free-energy landscape, finds the barriers, and builds a bond graph, a thermodynamic
circuit, written out as standard CellML.

*[Cycle affinity residual, log scale: structured model ~10⁻¹⁵; unconstrained network 10⁻⁴ to
10⁻²; test limit 10⁻¹⁰. Both fit the data.]*

The physics is in the architecture: the second law holds for any weights, at any point in training.
An unconstrained network fits just as well, and breaks thermodynamics. Ours cannot make current from
nothing.

*[KcsA I–V curve from the team code (single-ion bond graph, 140 mM in / 4 mM out, 298 K), zero
current at −91.30 mV on the dashed Nernst line. Selectivity filter F(z) with sites S0–S4 from 1K4C.
Nernst scan, 1.4 to 140 mM: model E_rev equals Nernst at every point, largest gap ~1×10⁻¹¹ mV.]*

On the KcsA potassium channel, with geometry from its crystal structure, the model gives a reversal
potential of −91.3 mV. That's the Nernst value, to numerical precision, across a hundred-fold range
of potassium: the check a broken model fails.

## 5 · How we tried not to fool ourselves (2:36–3:11)

*[How we check: provenance on every number · controls that must fail · mutation audit, 12 of 14
caught. What didn't work (yet): landscape constrained, not learned · barriers not pinned down ·
conductance more than 20× low (4.5 pS vs ~100 pS) · single-ion model, multi-ion channel → moved to
gramicidin A.]*

Every number records where it came from, and a mutation audit breaks the code on purpose to prove
the tests notice. We report what didn't work, too. The KcsA landscape is constrained to published
values, not yet learned, and trapped ions can't pin down the barriers. Conductance comes out more
than 20× too low, because potassium crosses KcsA by multi-ion knock-on and our model is single-ion.
So we've moved to gramicidin A, where one ion is the right model, now built in a membrane and
equilibrated.

## 6 · Where this goes (3:12–3:43)

*[The question again, answered. Rung cards: 925M molecules in 4 h 27 min; MD → bond graph →
CellML. Then the joined chain: screen (Lightning) → pose (co-folding) → simulate (MD) → bond graph
(CellML) → cell. End card over an event photo: repository and write-up URLs, the Auckland hub
team, OSI Hackathon 2026 · Auckland.]*

So how far can a chain of surrogates take us? Further than we expected, if every link carries its
own evidence. Lightning makes billion-molecule screening an afternoon's work. The bond-graph
pipeline turns atoms into a component physiologists can use. Next, we join them: screen the
library, pose the hits, simulate them, and ask what each one does to a cell.

It's all open source. Thanks for watching.

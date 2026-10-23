# Video script: How far can a chain of surrogates take us?

Target length 3:30–3:50, read at natural pace (no speed-up). Spoken text is below; on-screen
captions follow it word for word. Figures in brackets are what the scene shows.

---

## 1 · The question

*[Title card: "How far can a chain of surrogates take us?" OSI Hackathon 2026 · Auckland]*

Physiological outcomes come from molecules interacting. Those interactions change function, and
function is driven by changes in shape and structure. Pharmacology is what drugs do to that whole
system. So, how far can a chain of surrogates take us?

## 2 · The ladder

*[Two ladders side by side. Biology: sequence → structure → atoms in motion → cells and tissue.
Machine learning: association models → 3D-aware models → interatomic potentials → multi-scale
models. Two rungs light up.]*

Biology has a ladder of scales: sequence, structure, atoms in motion, cells and tissue. Machine
learning now has a ladder alongside it, mostly open-weight, mostly new. Each rung swaps an
expensive physical calculation for a learned one. The catch is trust: what's the ground truth,
what's the simple baseline, and where does it break? In two days in Auckland, we climbed two rungs.

## 3 · Rung one: screening a billion molecules

*[Docking: ~100 days for a billion molecules. Surrogate ranks, docking confirms the top.]*

Docking a billion molecules against a target takes about a hundred days. So you train a surrogate
on docking scores, and dock only what it ranks highest.

*[VDSAI Lightning: AttentiveFP · PyTorch Geometric · Lightning, replacing AMPL GraphConv ·
TensorFlow. 13× faster training; tuned R² 0.752 vs 0.690.]*

We rebuilt that surrogate. VDSAI Lightning replaces AMPL's GraphConv stack with an AttentiveFP
graph network in PyTorch Lightning. On three and a half million molecules it trained thirteen times
faster, and after tuning it beat AMPL on every test metric.

*[Counter: 925,000,000 molecules · 4 h 27 min · one workspace.]*

Then we scored 925 million ZINC molecules in under four and a half hours on a single workspace. We
had never screened a library that size.

*[Bar chart, recall of the docking top 1M on pool_3 (98.3M molecules): Lightning 35.0%, AMPL
32.3%, size-only 2.6%, random 1.2%. 381× fewer GPU hours.]*

Head to head on a 98-million-molecule pool, Lightning recovered 35 percent of the true docking top
million. AMPL recovered 32. Ranking by size gets 2.6, random picks 1.2. And Lightning used 381
times fewer GPU hours.

*[Two dockings of the same chunk: correlation 0.30.]*

We also measured the ceiling. Two dockings of the same molecules correlate at only 0.3, so the
surrogate is now chasing a noisy target.

## 4 · Rung two: from atoms to a cell

*[Pipeline: MD trajectory → measure D → learn F → find barriers → bond graph → CellML.]*

Rung two is the one nothing at last year's event reached: carrying a molecular signal up to
physiology. Our pipeline takes a molecular dynamics trajectory and returns a model that a heart or
kidney cell model can run. It measures diffusion, learns the free-energy landscape, finds the
barriers, and builds a bond graph, a thermodynamic circuit, written out as standard CellML.

*[Cycle residual: structured 1e-15 vs unconstrained 1e-2. Ḣ ≤ 0 for any weights.]*

The physics is in the architecture, not in a penalty term. The second law holds for any weights, at
any point in training. An unconstrained network fits the data just as well and breaks
thermodynamics. Ours cannot make a current from nothing.

*[KcsA selectivity filter, sites S0–S4 from 1K4C. I–V curve crossing zero at −91.3 mV.]*

On the KcsA potassium channel, with geometry from its crystal structure, the model gives a reversal
potential of minus 91.3 millivolts: the Nernst value, to a trillionth of a millivolt, across a
hundred-fold range of potassium. That only happens if charge and energy are conserved end to end,
and it's exactly the check a broken model fails.

## 5 · How we tried not to fool ourselves

*[Provenance on every number · tests with controls that must fail · mutation audit 12/14.]*

Every number records where it came from. Every test has a control that must fail, and a mutation
audit breaks the code on purpose to prove the tests notice.

*[What didn't work: landscape constrained, not learned · barriers unconstrained · conductance ~25×
low · single-ion vs knock-on → gramicidin A.]*

We report what didn't work, too. The KcsA landscape is constrained to published values, not yet
learned. Trapped ions can't pin down the barriers. Conductance comes out about twenty-five times
low, because potassium crosses KcsA by multi-ion knock-on and our model is single-ion. So we've
moved to gramicidin A, a single-file channel where one ion is the right model, now built in a
membrane and equilibrated.

## 6 · Where this goes

*[The two rungs joined: screen → pose → simulate → cell. Repository URL.]*

So how far can a chain of surrogates take us? Further than we expected, if every link carries its
own evidence. Lightning makes billion-molecule screening an afternoon's work. The bond-graph
pipeline turns atoms into a component physiologists can use. Next, we join them: screen the
library, pose the hits, simulate them, and ask what each one does to a cell.

It's all open source. Thanks for watching.

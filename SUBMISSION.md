# Submission kit

Everything needed for the OSI Hackathon 2026 submission on Moment
(<https://scientificintelligence.org/campaigns/osi-hackathon-2026>).

## Checklist

- [ ] **Video, up to 4 minutes, not sped up:** `assets/video/surrogate-chain.mp4`
- [ ] **Public post with the video** (YouTube, LinkedIn, X, Bluesky or Threads, no login to view). Text below.
- [x] **One-page write-up with a figure:** [`writeup.pdf`](writeup.pdf). Markdown version below for pasting.
- [x] **Code repository:** <https://github.com/jmdowrick/hackathon2026>, with write-up and video at <https://github.com/drai-inn/surrogate-chain>
- [ ] **Platforms used:** tick what applies. Only tick Valency, Adaption or marimo if a team actually used them (the sponsor prizes require it).
- [x] **Team:** Nick Jones, Chris Scott, Jack Copping, Te Xiao, Claire Rye, Samantha Rickard, Jarrah Dowrick, Jack Flanagan, Peter Hunter, Carvin Chen, Jun Huh, Neil Blake, Jagir Hussan, Ben Curran, Lizhe Hong, Mohamed Elwakdy.

**Project title:** How far can a chain of surrogates take us in biomolecular interactions?

**Platforms and tools:** PyTorch Geometric, PyTorch Lightning, Optuna, MLflow, NeSI HPC, OpenMM, deeptime, libcellml, Claude Code.

---

## One-page write-up (markdown)

```markdown
# How far can a chain of surrogates take us in biomolecular interactions?
*OSI Hackathon 2026 · Auckland hub*

**Team:** Nick Jones, Chris Scott, Jack Copping, Te Xiao, Claire Rye, Samantha Rickard, Jarrah Dowrick, Jack Flanagan, Peter Hunter, Carvin Chen, Jun Huh, Neil Blake, Jagir Hussan, Ben Curran, Lizhe Hong, Mohamed Elwakdy

Physiological outcomes come from molecules interacting. Those interactions produce functional change; function is driven by spatial and structural change; pharmacology is the effect of drugs on that system. Machine learning now offers a surrogate at every rung — association models over sequence, 3D-aware models over structure, interatomic potentials over atoms and motion, multi-scale models over cells and tissue. Most are open-weight and most arrived recently. Most of us know our own rung. We climbed two, and measured how far each can be trusted.

## Introduction
Each rung is a surrogate for a calculation too expensive to run at scale, such as docking a billion molecules or sampling an ion crossing a membrane. Chained, they could take a compound to its physiological effect. Two groups took rungs at opposite ends of the ladder:
- **Rung 1 · Screening at scale:** a graph-network surrogate for docking, fast enough for billion-molecule libraries.
- **Rung 2 · Atoms to a cell:** molecular dynamics turned into a thermodynamically consistent model that a cell-scale physiology model can run.

Both were held to four questions: what is the ground truth, what is the simple baseline, what would change our mind, and where would it break?

## Methods
**VDSAI Lightning** predicts docking fitness from the 2D molecular graph inside an active-learning loop, so that only the top-ranked compounds are docked. It replaces AMPL's GraphConv (TensorFlow) stack with AttentiveFP in PyTorch Geometric and Lightning. We used scaffold splits, an Optuna study (40 trials, median pruner) and a test set evaluated once. The ground truth is full docking of pool_3, a 98.3M-molecule ZINC chunk. The baselines are random picks, rank by heavy-atom count, and AMPL.

**Structure to physiology.** Diffusivity D is measured from the 2nd Kramers–Moyal moment and frozen, because learning D and F together is degenerate. A port-Hamiltonian network then learns the free energy F from the drift −D∇F, so the second law (dF/dt ≤ 0) holds for any weights at any point in training. States come from the MSM spectral gap and barriers from minimax saddles. The result is a Ce/Re bond graph with an electrical port (after Hunter et al.) in which the per-hop charges telescope to exactly one, written as CellML 2.0 and validated with libcellml. We validated on a toy system and alanine dipeptide, then applied it to the KcsA potassium channel with geometry from crystal structure 1K4C.

## Results
- **Faster and better than the incumbent.** On 3.5M molecules, training was 13.3× faster than AMPL (2 h 26 min vs 32 h 26 min). The tuned model's test R² was 0.752 vs 0.690, with lower RMSE and MAE.
- **Against docking (pool_3).** Lightning recovered **35.0%** of the docking top 1M, against 32.3% for AMPL, 2.6% for rank-by-size and 1.2% for random. It found 60.4% of the docking top 100k (AMPL 56.4%). Training was **27× faster** and scoring used **381× fewer GPU hours** (26 min on one GPU vs 4 days 9 h).
- **Billion scale.** **925M ZINC molecules scored in 4 h 27 min** on one workspace, about 540× faster than docking. This group had never been able to screen a library this size.
- **The noise ceiling.** Two dockings of the same chunk correlate at only r = 0.30, so the surrogate is now chasing a noisy target.
- **Thermodynamics by construction.** The cycle residual is ~10⁻¹⁵ for the structured model, against 10⁻⁴ to 10⁻² for an unconstrained network that fits as well. D is recovered to 0.5% on the toy, and the learned landscape correlates at r = 0.984 with a potential the network never saw.
- **KcsA.** The bond-graph reversal potential is **−91.30 mV**, equal to Nernst E_K to within 10⁻¹¹ mV across a 100-fold range of K⁺.
- **Honest limits.** The KcsA landscape is constrained to literature values, not learned. Trapped ions never cross the barriers. Conductance is about 20× low (single-ion model vs multi-ion knock-on). We have moved to gramicidin A, now built in a DMPC membrane with all equilibration checks passing.

## Conclusions
A surrogate can beat the incumbent on accuracy and cost at once, turning billion-molecule screening into an afternoon's work; its ceiling is now the noise in docking itself. Physical structure can be carried from atoms to an importable physiology component as an architectural invariant rather than a penalty. Each link is only as good as its hardest region: the top tail for docking, the barrier for MD. How far can a chain of surrogates take us? Further than we expected, if every link carries its own evidence.

## Future directions
Join the rungs into one chain: screen with Lightning, pose the hits with co-folding (Boltz-2, OpenFold3), simulate them, build the bond graph, and run a cell model. Raise the screening ceiling with consensus docking and 3D/MLIP rescoring. Learn barriers with weighted-ensemble sampling on gramicidin A. Model drug block and mutations as bond-graph perturbations in cardiac and renal cell models.
```

---

## Social post

> How far can a chain of surrogates take us in biomolecular interactions? 🧬⚡
>
> Two days at the #OSIHackathon Auckland hub, two rungs of the ladder:
>
> 🔹 Screening: our graph-network docking surrogate scored 925M ZINC molecules in under 4.5 hours on one workspace. It recovered more of the true docking top 1M than the incumbent (35.0% vs 32.3%), using 381× fewer GPU hours.
>
> 🔹 Atoms → cells: molecular dynamics turned into a thermodynamically consistent bond-graph model, exported as CellML. On the KcsA potassium channel it predicts the textbook reversal potential of −91.3 mV.
>
> We also reported what didn't work.
>
> 🎥 [video link]
> 🌐 drai-inn.github.io/surrogate-chain
> 💻 github.com/drai-inn/surrogate-chain
>
> #AI4Science #DrugDiscovery #OpenScience

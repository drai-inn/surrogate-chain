"""Compute KcsA permeation-graph outputs from the team code, for figures."""
import json, sys
import numpy as np
from ala2bg import kcsa, electro

out = {}
bg = kcsa.permeation_graph(0.02)
out["reversal_mV"] = bg.reversal_potential() * 1000
out["nernst_mV"] = bg.nernst(140.0, 4.0) * 1000
V = np.linspace(-0.2, 0.2, 81)
I = np.asarray(bg.iv_curve(V))
out["V_mV"] = (V * 1000).tolist()
out["I"] = I.tolist()
out["conductance"] = float(bg.conductance())
# Nernst check across 100-fold concentration range
rows = []
for c_out in [1.4, 4.0, 14.0, 40.0, 140.0]:
    b = kcsa.permeation_graph(0.02, c_out=c_out, c_in=140.0)
    Er = b.reversal_potential() * 1000
    En = b.nernst(140.0, c_out) * 1000
    rows.append(dict(c_out=c_out, E_rev_mV=Er, E_nernst_mV=En, diff_mV=Er - En))
out["nernst_scan"] = rows
z = np.linspace(-9, 9, 400)
out["landscape_z"] = z.tolist()
out["landscape_F_kJ"] = kcsa.filter_landscape(z).tolist()
out["sites"] = {k: float(v) for k, v in kcsa.SITES.items()}
out["provenance"] = kcsa.provenance()
try:
    out["charge_closure"] = bg.check_charge_closure()
except Exception as e:
    out["charge_closure"] = repr(e)
try:
    out["no_current_eq"] = bg.check_no_current_at_equilibrium()
except Exception as e:
    out["no_current_eq"] = repr(e)
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print(json.dumps({k: out[k] for k in ["reversal_mV", "nernst_mV", "conductance", "nernst_scan", "sites"]}, indent=1, default=str))
print(str(out["provenance"])[:600])
print(str(out["charge_closure"])[:300]); print(str(out["no_current_eq"])[:300])

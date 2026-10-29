import json, numpy as np
r1 = json.load(open("result.json"))
H = {"EIGHTHS": [365.2422/8, 365.2422/16], "MONTHS": [29.5306, 29.5306/2],
     "STAR GAPS": [v for v in r1["hyp"]["STAR GAPS"]["values"] if v > 0.05], "CALENDAR": r1["hyp"]["CALENDAR"]["values"]}
F = np.array([1/60, 1, 60, 1/360, 60/360, 1/21600]); NAMES = ["x/60 d", "x d", "60x d", "x UŠ", "60x UŠ", "x/60 UŠ"]
def score(X, V, detail=False):
    R = X[..., None, None] * F[:, None]                    # readings
    D = np.abs(np.log(R / np.asarray(V)[None, None, :]))   # [..., n, reading, value]
    best = D.min(-1).min(-1)
    if detail:
        i = D.min(-1).argmin(-1); j = D.min(-2)[np.arange(len(X)), :].argmin(-1) if False else None
        return best.mean(-1), [NAMES[k] for k in i]
    return best.mean(-1)
rng = np.random.default_rng(20261030)
out = {}
for X, tag in ((np.array([22,22,20,40,40,40,40,40.]), "8"), (np.array([22,22,20,40,40,40,40.]), "7")):
    U = rng.integers(1, 60, (20000, len(X))).astype(float)
    Rd = np.where(rng.random((20000, len(X))) < 0.5, rng.integers(1, 6, (20000, len(X))) * 10, rng.integers(1, 60, (20000, len(X)))).astype(float)
    for k, V in H.items():
        s, how = score(X, V, True)
        out.setdefault(k, {})[tag] = {"score": round(float(s), 3), "p_uniform": float((score(U, V) <= s).mean()),
                                      "p_round": float((score(Rd, V) <= s).mean()), "readings": how}
print(json.dumps(out, indent=1))

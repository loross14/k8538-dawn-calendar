"""Heliacal-rising crib drag with a real visibility model (Swiss Ephemeris heliacal_ut).

For each epoch, each crib star's heliacal rising at Nineveh is found; the Sun's longitude
(of date) on that morning is the star's angle in the year. Cribs, misses, rotation search and
null are as in crib_drag.py.
Usage: heliacal_drag.py EPHE_PATH OUT_JSON
"""
import json, sys
import numpy as np
import swisseph as swe
from crib_drag import CRIBS, miss

GEO = (43.15, 36.36, 250.0)
ATMOS = (1013.25, 15.0, 40.0, 0.25)
OBSERVER = (25.0, 1.0, 1, 1, 1, 1.0)
EPOCHS = list(range(-1600, -199, 50))


def angles(year):
    out, fails = {}, []
    jd0 = swe.julday(year, 1, 1, 0.0, swe.JUL_CAL)
    for lab, (_, stars) in CRIBS.items():
        a = []
        for s in stars:
            try:
                jd = swe.heliacal_ut(jd0, GEO, ATMOS, OBSERVER, s, swe.HELIACAL_RISING, swe.FLG_SWIEPH)[0]
                a.append(swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0])
            except swe.Error:
                fails.append(s)
        out[lab] = np.array(a)
    return out, fails


def best(by_epoch, slices):
    b = (1e9, None, None, None)
    for e, fmt in by_epoch.items():
        arrs = list(fmt.values())
        if any(len(a) == 0 for a in arrs):
            continue
        for d in (1, -1):
            for r in range(0, 360, 2):
                t = sum(miss((d * a + r) % 360, s) for a, s in zip(arrs, slices))
                if t < b[0]:
                    b = (t, r, d, e)
    return b


def main():
    swe.set_ephe_path(sys.argv[1])
    by_epoch, fails = {}, {}
    for e in EPOCHS:
        by_epoch[e], fails[e] = angles(e)
    true = [v[0] for v in CRIBS.values()]
    rng = np.random.default_rng(20261030)
    per_epoch = {}
    for e in EPOCHS:
        t, r, d, _ = best({e: by_epoch[e]}, true)
        per_epoch[e] = t
    t, r, d, e = best(by_epoch, true)
    null = np.array([best(by_epoch, rng.integers(1, 9, len(true)))[0] for _ in range(120)])
    each = {lab: miss((d * by_epoch[e][lab] + r) % 360, s) for lab, s in zip(CRIBS, true)}
    five = [k for k in CRIBS if not k.startswith("Tammuz")]
    by5 = {ep: {k: v for k, v in f.items() if k in five} for ep, f in by_epoch.items()}
    t5, r5, d5, e5 = best(by5, [CRIBS[k][0] for k in five])
    null5 = np.array([best(by5, rng.integers(1, 9, len(five)))[0] for _ in range(120)])
    res = {"all_six": {"miss": t, "epoch": e, "rotation": r, "direction": d,
                       "null_fraction": float(np.mean(null <= t)), "per_crib": each},
           "five_without_tammuz": {"miss": t5, "epoch": e5, "rotation": r5, "direction": d5,
                                   "null_fraction": float(np.mean(null5 <= t5))},
           "miss_by_epoch_all_six": per_epoch, "heliacal_failures": {k: v for k, v in fails.items() if v}}
    with open(sys.argv[2], "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps({k: v for k, v in res.items() if k != "miss_by_epoch_all_six"}, indent=1))
    print("miss by epoch:", {k: round(v, 1) for k, v in per_epoch.items()})


if __name__ == "__main__":
    main()

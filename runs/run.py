import json, sys
import numpy as np
import swisseph as swe
EXP = sys.argv[1]; sys.path.insert(0, EXP)
from heliacal_drag import GEO, ATMOS, OBSERVER
from crib_drag import miss
swe.set_ephe_path(sys.argv[2])
YEAR = -699  # astronomical year for 700 BCE
jd0 = swe.julday(YEAR, 1, 1, 0.0, swe.JUL_CAL)
def rise(s):
    jd = swe.heliacal_ut(jd0, GEO, ATMOS, OBSERVER, s, swe.HELIACAL_RISING, swe.FLG_SWIEPH)[0]
    return jd, swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
# calendar fit with Weidner cribs
cribs = {2: ["Mirach"], 4: ["Betelgeuse", "Rigel", "Bellatrix", "Alnilam"], 5: ["Alhena", "Alzirr"]}
lam = {s: np.array([rise(x)[1] for x in xs]) for s, xs in cribs.items()}
zero = [r for r in range(0, 360, 2) if sum(miss((a + r) % 360, s) for s, a in lam.items()) == 0]
# zero-miss rotations may wrap; take the contiguous run
runs, cur = [], [zero[0]]
for r in zero[1:]:
    if r - cur[-1] == 2: cur.append(r)
    else: runs.append(cur); cur = [r]
runs.append(cur)
if len(runs) > 1 and runs[0][0] == 0 and runs[-1][-1] == 358: runs = [runs[-1] + [x + 360 for x in runs[0]]] + runs[1:-1]
run = max(runs, key=len); rot = (run[0] + run[-1]) / 2 % 360
# bright stars
names = "Sirius Arcturus Vega Capella Rigel Procyon Betelgeuse Altair Aldebaran Antares Spica Pollux Fomalhaut Deneb Regulus Adhara Castor Shaula Bellatrix Elnath Alnilam Alnitak Mirach Hamal Markab".split()
events, dropped = [], []
for n in names:
    try:
        jd, l = rise(n); events.append((jd, l, n))
    except swe.Error:
        dropped.append(n)
events.sort()
jds = np.array([e[0] for e in events])
gaps_all = list(np.diff(jds)) + [jds[0] + 365.2422 - jds[-1]]
# slice 6 window in Sun longitude: angle=(lam+rot)%360 in [225,270)
lo_l, hi_l = (225 - rot) % 360, (270 - rot) % 360
def in_win(l): return ((l + rot) % 360 >= 225) and ((l + rot) % 360 < 270)
inside = [e for e in events if in_win(e[1])]
def sun_jd(target):  # first time after jd0 the Sun reaches longitude target (daily scan, then bisection)
    sun = lambda jd: swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
    past = lambda jd: (sun(jd) - target + 360) % 360 < 180
    jd = jd0
    while past(jd): jd += 1.0
    while not past(jd): jd += 1.0
    a, b = jd - 1.0, jd
    for _ in range(40):
        m = (a + b) / 2
        a, b = (a, m) if past(m) else (m, b)
    return b
w0 = sun_jd(lo_l); w1 = sun_jd(hi_l)
if w1 < w0: w1 += 365.2422
ins = sorted(e[0] if e[0] >= w0 else e[0] + 365.2422 for e in inside)
pts = [w0] + ins + [w1]
gaps_cal = list(np.diff(pts))
X8 = np.array([22, 22, 20, 40, 40, 40, 40, 40.0]); X7 = np.array([22, 22, 20, 40, 40, 40, 40.0])
H = {"EIGHTHS": [365.2422/8, 365.2422/16], "MONTHS": [29.5306, 29.5306/2], "STAR GAPS": gaps_all, "CALENDAR": gaps_cal}
def score(x, V):
    V = np.asarray(V)[None, :]
    return np.abs(x[..., None] - V).min(-1).mean(-1)
rng = np.random.default_rng(20261029)
out = {"rotation": rot, "zero_miss_rotations": [run[0] % 360, run[-1] % 360], "slice6_window_days": [w0, w1],
       "window_length_days": w1 - w0, "stars_inside_slice6": [e[2] for e in sorted(inside)], "dropped": dropped,
       "hyp": {}}
for X, tag in ((X8, "8"), (X7, "7")):
    R = rng.integers(1, 60, (20000, len(X))).astype(float)
    for k, V in H.items():
        s = float(score(X, V)); p = float((score(R, V) <= s).mean())
        out["hyp"].setdefault(k, {})["values"] = [round(v, 2) for v in sorted(V)]
        out["hyp"][k]["score_" + tag] = round(s, 2); out["hyp"][k]["p_" + tag] = p
print(json.dumps(out, indent=1, default=float))

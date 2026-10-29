import sys, numpy as np, swisseph as swe
EXP = sys.argv[1]; sys.path.insert(0, EXP)
from heliacal_drag import GEO, ATMOS, OBSERVER
from crib_drag import miss
swe.set_ephe_path(sys.argv[2])
cribs = {2: ["Mirach"], 4: ["Betelgeuse", "Rigel", "Bellatrix", "Alnilam"], 5: ["Alhena", "Alzirr"]}
for label, year, m, d in (("Bond & Hempsell", -3122, 6, 29), ("Seifert & Lemke", -2192, 9, 22)):
    jd0 = swe.julday(year, 1, 1, 0.0, swe.JUL_CAL)
    lam = {s: np.array([swe.calc_ut(swe.heliacal_ut(jd0, GEO, ATMOS, OBSERVER, x, swe.HELIACAL_RISING, swe.FLG_SWIEPH)[0], swe.SUN, swe.FLG_SWIEPH)[0][0] for x in xs]) for s, xs in cribs.items()}
    zero = [r for r in range(0, 360, 2) if sum(miss((a + r) % 360, s) for s, a in lam.items()) == 0]
    ev = swe.calc_ut(swe.julday(year, m, d, 3.0, swe.JUL_CAL), swe.SUN, swe.FLG_SWIEPH)[0][0]
    slices = sorted({int(((ev + r) % 360) // 45) + 1 for r in zero})
    print(f"{label}: {abs(year)+1} BCE {m}/{d} Julian, Sun lon {ev:.1f}; zero-miss rotations {zero[0] if zero else None}..{zero[-1] if zero else None} ({len(zero)}); event falls in King slice(s) {slices}")

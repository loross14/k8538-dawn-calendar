"""Crib drag across formats (Logan's Mamari crib method applied to K 8538's slices).

Each verified label crib sits in a known slice (King 1912 numbering, slice k spans
[(k-1)*45, k*45) degrees). A "format" turns each crib's member stars into an angle around
the tablet. The search slides every format by rotation and direction (and epoch, where the
format depends on precession). A crib misses by 0 if any member star lands inside its slice.
Null: the same search on random slice assignments.

Usage: crib_drag.py EPHE_PATH OUT_JSON
"""
import json, sys
import numpy as np
import swisseph as swe

PHI = 36.36                                # Nineveh latitude
CRIBS = {                                  # label -> (King slice, member stars); IDs from MUL.APIN tables
    "Gula=Aquarius": (1, ["Sadalmelik", "Sadalsuud", "Skat", "Sadachbia"]),
    "Tammuz=Hired Man (Aries)": (1, ["Hamal", "Sheratan", "Mesarthim"]),
    "Anunitu=NE Pisces+bAnd": (2, ["Mirach"]),
    "Icu=Pegasus": (2, ["Markab", "Scheat", "Algenib", "Alpheratz"]),
    "Sibzianna=Orion": (5, ["Betelgeuse", "Rigel", "Bellatrix", "Alnilam"]),
    "Bartabba=Gemini": (5, ["Castor", "Pollux"]),
}
EPOCHS = [-3000, -2500, -2000, -1500, -1000, -650]


def radec(name, jd):
    xx = swe.fixstar2_ut(name, jd, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
    return xx[0], xx[1]


def eclon(name, jd):
    return swe.fixstar2_ut(name, jd, swe.FLG_SWIEPH)[0][0]


def ascendant(lst, eps, phi=PHI):
    """Ecliptic longitude rising on the eastern horizon at local sidereal time lst (deg)."""
    t, e, p = np.radians(lst), np.radians(eps), np.radians(phi)
    return np.degrees(np.arctan2(np.cos(t), -(np.sin(t) * np.cos(e) + np.tan(p) * np.sin(e)))) % 360


def formats(jd):
    eps = swe.calc_ut(jd, swe.ECL_NUT, 0)[0][0]
    out = {k: {} for k in ("ecliptic longitude", "right ascension (culmination / ziqpu order)",
                           "rising azimuth on the horizon", "co-rising ecliptic point (heliacal-rising order)",
                           "co-setting ecliptic point (heliacal-setting order)", "declination ring as angle")}
    for lab, (_, stars) in CRIBS.items():
        L, R, AZ, CR, CS, DE = [], [], [], [], [], []
        for s in stars:
            ra, de = radec(s, jd)
            L.append(eclon(s, jd)); R.append(ra)
            AZ.append(np.degrees(np.arccos(np.clip(np.sin(np.radians(de)) / np.cos(np.radians(PHI)), -1, 1))))
            h0 = np.degrees(np.arccos(np.clip(-np.tan(np.radians(PHI)) * np.tan(np.radians(de)), -1, 1)))
            CR.append(ascendant((ra - h0) % 360, eps)); CS.append((ascendant((ra + h0) % 360, eps) + 180) % 360)
            DE.append((de + 90) * 2)           # declination -90..90 stretched to 0..360, a deliberately odd control
        for k, v in zip(out, (L, R, AZ, CR, CS, DE)):
            out[k][lab] = np.array(v)
    return out


def miss(a, s):
    lo, hi = (s - 1) * 45, s * 45
    if ((a >= lo) & (a < hi)).any():
        return 0.0
    return float(min(min(abs((x - lo + 180) % 360 - 180), abs((x - hi + 180) % 360 - 180)) for x in a))


def best(fmt_by_epoch, slices):
    b = (1e9, None, None, None)
    for e, fmt in fmt_by_epoch.items():
        arrs = list(fmt.values())
        for d in (1, -1):
            for r in range(0, 360, 2):
                t = sum(miss((d * a + r) % 360, s) for a, s in zip(arrs, slices))
                if t < b[0]:
                    b = (t, r, d, e)
    return b


def main():
    swe.set_ephe_path(sys.argv[1])
    per_epoch = {e: formats(swe.julday(e, 7, 1, 0.0, swe.JUL_CAL)) for e in EPOCHS}
    names = list(per_epoch[EPOCHS[0]])
    true_slices = [v[0] for v in CRIBS.values()]
    rng = np.random.default_rng(20261029)
    rand_sets = [rng.integers(1, 9, len(CRIBS)) for _ in range(150)]
    results = {}
    for f in names:
        fmt_by_epoch = {e: per_epoch[e][f] for e in EPOCHS}
        t, r, d, e = best(fmt_by_epoch, true_slices)
        null = np.array([best(fmt_by_epoch, s)[0] for s in rand_sets])
        each = {lab: miss((d * per_epoch[e][f][lab] + r) % 360, s) for lab, s in zip(CRIBS, true_slices)}
        results[f] = {"total_miss": t, "rotation": r, "direction": d, "epoch": e,
                      "null_fraction_as_good": float(np.mean(null <= t)), "per_crib_miss": each}
        print(f"{f:52s} miss {t:6.1f}  epoch {e}  rot {r} dir {d:+d}  null {np.mean(null <= t) * 100:5.1f}%  "
              + "  ".join(f"{k.split('=')[0]}:{v:.0f}" for k, v in each.items()), flush=True)
    with open(sys.argv[2], "w") as fh:
        json.dump(results, fh, indent=2)


if __name__ == "__main__":
    main()

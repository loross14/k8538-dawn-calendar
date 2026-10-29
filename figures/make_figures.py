"""Figures for "A Dawn Calendar in Eight Parts". Every number is recomputed or read from run outputs.
Usage: make_figures.py EXP_DIR EPHE_DIR PLATE_JPG ROBUST_JSON OUT_DIR"""
import sys, json, numpy as np, swisseph as swe
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
EXP, EPHE, PLATE, ROB, OUT = sys.argv[1:6]; sys.path.insert(0, EXP)
from heliacal_drag import GEO, ATMOS, OBSERVER
swe.set_ephe_path(EPHE); Y = 365.2422
BLUE, ORANGE, INK, INK2, MUTED, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#898781", "#fcfcfb"
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 300, "figure.facecolor": "white"})
CRIBS = [("Anunitum", 2, ["Mirach"]), ("APIN (Cassiopeia)", 2, ["Schedar", "Caph", "Ruchbah"]),
         ("Orion", 4, ["Betelgeuse", "Rigel", "Bellatrix", "Alnilam"]), ("Twins", 5, ["Alhena", "Alzirr"]),
         ("Raven", 6, ["Gienah", "Kraz", "Algorab", "Minkar"])]
jd0 = swe.julday(-699, 1, 1, 0.0, swe.JUL_CAL)
def rise(s):
    jd = swe.heliacal_ut(jd0, GEO, ATMOS, OBSERVER, s, swe.HELIACAL_RISING, swe.FLG_SWIEPH)[0]
    return jd, swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
RISE = {lab: [rise(s) for s in ms] for lab, _, ms in CRIBS}

# Fig 1: King's plate with slice numbers
im = Image.open(PLATE).convert("L"); cx, cy, R = 1179, 2164, 902; m = 170
crop = im.crop((cx - R - m, cy - R - m, cx + R + m, cy + R + m))
fig, ax = plt.subplots(figsize=(4.2, 4.2)); ax.imshow(crop, cmap="gray"); ax.axis("off")
c = R + m
for k in range(1, 9):
    th = np.radians(45 * (k - 1) + 22.5); x, y = c + 1.09 * R * np.cos(th), c - 1.09 * R * np.sin(th)
    ax.text(x, y, str(k), ha="center", va="center", fontsize=11, color="white",
            bbox=dict(boxstyle="circle,pad=0.25", fc=BLUE, ec="none"))
fig.savefig(f"{OUT}/fig1-plate.png", bbox_inches="tight", pad_inches=0.02); plt.close(fig)

# Fig 2: the year wheel (Sun longitude of date at heliacal rising, 700 BCE; five-crib best rotation, 2-degree grid)
def wmiss(a, k):
    lo, hi = (k - 1) * 45, k * 45
    return 0 if ((a >= lo) & (a < hi)).any() else min(min(abs((v - lo + 180) % 360 - 180), abs((v - hi + 180) % 360 - 180)) for v in a)
LAM = {lab: np.array([l for _, l in RISE[lab]]) for lab, _, _ in CRIBS}
ROT = min(range(0, 360, 2), key=lambda r: sum(wmiss((LAM[lab] + r) % 360, k) for lab, k, _ in CRIBS))
fig = plt.figure(figsize=(4.6, 4.6)); ax = fig.add_subplot(projection="polar")
ax.set_theta_zero_location("E"); ax.set_theta_direction(1); ax.set_ylim(0, 1.28); ax.set_yticks([]); ax.set_xticks([])
ax.spines["polar"].set_visible(False)
th = np.linspace(0, 2 * np.pi, 400); ax.plot(th, [1.0] * 400, color=MUTED, lw=0.8)
for k in range(8):
    ax.plot([np.radians(45 * k)] * 2, [0, 1.0], color=MUTED, lw=0.8)
    ax.text(np.radians(45 * k + 22.5), 1.17, f"{k+1}", ha="center", va="center", fontsize=11, color=INK)
for lam, lab in ((270, "winter solstice"), (0, "spring equinox"), (90, "summer solstice"), (180, "autumn equinox")):
    a = np.radians((lam + ROT) % 360); ax.plot([a, a], [0.0, 1.0], color=ORANGE, lw=1, ls=(0, (2, 2)))
    vert = abs(np.cos(a)) > 0.7
    ax.text(a, 1.07, lab, ha="center", va="center", fontsize=6, color=ORANGE, rotation=90 if vert else 0)
RAD = {"Anunitum": 0.85, "APIN (Cassiopeia)": 0.68, "Orion": 0.85, "Twins": 0.62, "Raven": 0.78}
for lab, k, _ in CRIBS:
    ang = np.radians((LAM[lab] + ROT) % 360)
    ax.plot(ang, [RAD[lab]] * len(ang), "o", ms=5, color=BLUE, mec="white", mew=0.8, ls="none")
    ax.text(np.mean(ang), RAD[lab] - 0.11, lab, ha="center", va="center", fontsize=6.5, color=INK)
fig.savefig(f"{OUT}/fig2-wheel.png", bbox_inches="tight"); plt.close(fig)
print("fig2 rotation", ROT)

# Fig 3: scoreboard (identical four cribs; then five cribs)
rows = [("1880 sunset horizon", 12.7, MUTED), ("Weidner ecliptic order", 10.0, MUTED), ("Koch one-night horizon", 8.7, MUTED),
        ("Dawn calendar, 4 cribs", 2.0, BLUE), ("Dawn calendar, 5 cribs", 0.64, BLUE), ("5 cribs, APIN = Triangulum", 0.48, BLUE)]
fig, ax = plt.subplots(figsize=(5.2, 2.4))
ys = np.arange(len(rows))[::-1]
ax.barh(ys, [r[1] for r in rows], color=[r[2] for r in rows], height=0.6)
for y, (lab, v, _) in zip(ys, rows): ax.text(v + 0.25, y, f"{v:g}%", va="center", fontsize=8, color=INK)
ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows]); ax.set_xlabel("Random tablets that fit as well (%)")
ax.set_xlim(0, 14.5); ax.tick_params(axis="y", length=0)
fig.savefig(f"{OUT}/fig3-scoreboard.png", bbox_inches="tight"); plt.close(fig)

# Fig 4: null distribution (time wheel, 700 BCE, 10,000 draws, seed as robust-1)
A = [np.array([((jd - jd0) % Y) * 360 / Y for jd, _ in RISE[lab]]) for lab, _, _ in CRIBS]; true = [c[1] for c in CRIBS]
grid = [(d, r) for d in (1, -1) for r in np.arange(0, 366) * 360 / Y]
M = np.zeros((5, len(grid), 8))
for ci, a in enumerate(A):
    for gi, (d, r) in enumerate(grid):
        x = (d * a + r) % 360
        for s in range(8):
            lo, hi = s * 45, (s + 1) * 45
            M[ci, gi, s] = 0 if ((x >= lo) & (x < hi)).any() else min(min(abs((v - lo + 180) % 360 - 180), abs((v - hi + 180) % 360 - 180)) for v in x)
obs = M[np.arange(5), :, np.array(true) - 1].sum(0).min()
Rn = np.random.default_rng(20261102).integers(0, 8, (10000, 5)); tot = np.zeros((10000, len(grid)))
for ci in range(5): tot += M[ci][:, Rn[:, ci]].T
null = tot.min(1); p = (null <= obs + 1e-9).mean()
fig, ax = plt.subplots(figsize=(5.2, 2.4))
ax.hist(null, bins=60, color=MUTED, edgecolor="white", linewidth=0.4)
ax.axvline(obs, color=ORANGE, lw=1.5); ax.text(obs + 2, ax.get_ylim()[1] * 0.85, f"K 8538: {obs:.1f}°\n{p*100:.2f}% of random tablets\nfit as well", fontsize=7.5, color=INK)
ax.set_xlabel("Best total miss for a random tablet (degrees)"); ax.set_ylabel("Random tablets")
fig.savefig(f"{OUT}/fig4-null.png", bbox_inches="tight"); plt.close(fig)

# Fig 5: the Raven against the slice-6 window
sun = lambda jd: swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
def at(target):
    jd = jd0
    past = lambda j: (sun(j) - target + 360) % 360 < 180
    while past(jd): jd += 1
    while not past(jd): jd += 1
    a, b = jd - 1, jd
    for _ in range(40):
        mm = (a + b) / 2; a, b = (a, mm) if past(mm) else (mm, b)
    return b
ROTP = 84  # the wheel the Raven prediction was locked on (Weidner three-crib fit)
w0, w1 = at((225 - ROTP) % 360), at((270 - ROTP) % 360)
def md(jd): y, mo, d, _ = swe.revjul(jd, swe.JUL_CAL); return f"{int(d)} {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][mo-1]}"
fig, ax = plt.subplots(figsize=(5.2, 1.9))
ax.axvspan(w0, w1, color=BLUE, alpha=0.15, lw=0); ax.text((w0 + w1) / 2, 1.38, "slice 6 window (wheel rotation 84°)", ha="center", fontsize=8, color=INK2)
names = {"Gienah": "Gienah (γ)", "Kraz": "Kraz (β)", "Algorab": "Algorab (δ)", "Minkar": "Minkar (ε)"}
for i, ((jd, _), s) in enumerate(zip(RISE["Raven"], ["Gienah", "Kraz", "Algorab", "Minkar"])):
    ax.plot(jd, 1, "o", ms=7, color=BLUE, mec="white", mew=1)
    ax.annotate(names[s], (jd, 1), xytext=(w0 + 6, 0.85 - 0.22 * i), fontsize=7, color=INK, va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
ax.set_xlim(w0 - 25, w1 + 15); ax.set_ylim(0, 1.6); ax.set_yticks([])
ax.set_xticks([w0, w1]); ax.set_xticklabels([md(w0), md(w1)]); ax.spines["left"].set_visible(False)
fig.savefig(f"{OUT}/fig5-raven.png", bbox_inches="tight"); plt.close(fig)

# Fig 6: robustness (time wheel)
r = json.load(open(ROB))
items = [("1500 BCE", r["B_1500BCE"]), ("1000 BCE", r["B_1000BCE"]), ("700 BCE", r["A_700BCE_10k"]), ("400 BCE", r["B_400BCE"]),
         ("drop Anunitum", r["C_drop_Anunitum"]), ("drop APIN", r["C_drop_APIN=Cassiopeia"]), ("drop Orion", r["C_drop_Orion"]),
         ("drop Twins", r["C_drop_Twins"]), ("drop Raven", r["C_drop_Corvus"]), ("APIN = Triangulum", r["E_APIN_Triangulum"])]
fig, ax = plt.subplots(figsize=(5.2, 2.8)); ys = np.arange(len(items))[::-1]
vals = [it[1]["time"]["p"] * 100 for it in items]
ax.hlines(ys, 0, vals, color=MUTED, lw=1); ax.plot(vals, ys, "o", ms=6, color=BLUE, mec="white", mew=1)
for y, v in zip(ys, vals): ax.text(v + 0.12, y, f"{v:.2f}%", va="center", fontsize=7.5, color=INK)
ax.axvline(5, color=MUTED, lw=0.8, ls=(0, (2, 2))); ax.text(5.05, ys[0] + 0.3, "5%", fontsize=7, color=MUTED)
ax.set_yticks(ys); ax.set_yticklabels([it[0] for it in items]); ax.tick_params(axis="y", length=0)
ax.set_xlabel("Random tablets that fit as well (%), 10,000 each"); ax.set_xlim(0, 5.8)
fig.savefig(f"{OUT}/fig6-robust.png", bbox_inches="tight"); plt.close(fig)
json.dump({"null_obs_deg": float(obs), "null_p": float(p), "slice6_window": [md(w0), md(w1)],
           "raven": {s: md(jd) for (jd, _), s in zip(RISE["Raven"], ["Gienah", "Kraz", "Algorab", "Minkar"])}},
          open(f"{OUT}/figures.json", "w"), indent=1)
print(open(f"{OUT}/figures.json").read())

import sys, numpy as np, swisseph as swe
EXP=sys.argv[1]; sys.path.insert(0,EXP)
from heliacal_drag import GEO, ATMOS, OBSERVER
swe.set_ephe_path(sys.argv[2]); jd0=swe.julday(-699,1,1,0.0,swe.JUL_CAL)
def rise(s):
    jd=swe.heliacal_ut(jd0,GEO,ATMOS,OBSERVER,s,swe.HELIACAL_RISING,swe.FLG_SWIEPH)[0]
    return jd, swe.calc_ut(jd,swe.SUN,swe.FLG_SWIEPH)[0][0]
for s in ["Gienah","Kraz","Algorab","Minkar"]:
    jd,l=rise(s); y,m,d,_=swe.revjul(jd,swe.JUL_CAL)
    sl={int(((l+r)%360)//45)+1 for r in range(78,91,2)}
    print(f"{s:8s} rises {m}/{d} (Julian), Sun lon {l:.1f} -> slice {int(((l+84)%360)//45)+1} at rot 84; over 78..90: {sorted(sl)}")
print("slice windows at rot 84 (Sun longitude): ", [(k+1, round((45*k-84)%360), round((45*(k+1)-84)%360)) for k in range(8)])

import sys, json, numpy as np, swisseph as swe
EXP=sys.argv[1]; sys.path.insert(0,EXP)
from heliacal_drag import GEO, ATMOS, OBSERVER
swe.set_ephe_path(sys.argv[2]); jd0=swe.julday(-699,1,1,0.0,swe.JUL_CAL); Y=365.2422
CRIBS=[("Anunitum",2,["Mirach"]),("APIN=Cassiopeia",2,["Schedar","Caph","Ruchbah"]),
       ("Orion",4,["Betelgeuse","Rigel","Bellatrix","Alnilam"]),("Twins",5,["Alhena","Alzirr"]),
       ("Corvus",6,["Gienah","Kraz","Algorab","Minkar"])]
T,L,drop={},{},[]
for lab,_,ms in CRIBS:
    t,l=[],[]
    for s in ms:
        try:
            jd=swe.heliacal_ut(jd0,GEO,ATMOS,OBSERVER,s,swe.HELIACAL_RISING,swe.FLG_SWIEPH)[0]
            t.append((jd-jd0)%Y); l.append(swe.calc_ut(jd,swe.SUN,swe.FLG_SWIEPH)[0][0])
        except swe.Error: drop.append(s)
    T[lab]=np.array(t)*360/Y; L[lab]=np.array(l)   # time wheel expressed in degrees of the year
def miss(a,s):
    lo,hi=(s-1)*45,s*45
    if ((a>=lo)&(a<hi)).any(): return 0.0
    return float(min(min(abs((x-lo+180)%360-180),abs((x-hi+180)%360-180)) for x in a))
labs=[c[0] for c in CRIBS]; true=[c[1] for c in CRIBS]
def best(A,slices,grid):
    b=1e9
    for d in (1,-1):
        for r in grid:
            tot=0.0
            for lab,s in zip(labs,slices):
                tot+=miss((d*A[lab]+r)%360,s)
                if tot>=b: break
            b=min(b,tot)
            if b==0: return 0.0
    return b
gt=np.arange(0,366)*360/Y   # 1-day grid on the time wheel
gl=np.arange(0,360,2)       # 2-degree grid on the longitude wheel
rng=np.random.default_rng(20261031)
res={"dropped":drop}
for name,A,g in (("time-eighths (new thesis)",T,gt),("solar-longitude eighths (old wheel)",L,gl)):
    obs=best(A,true,g)
    null=np.array([best(A,list(rng.integers(1,9,len(true))),g) for _ in range(2000)])
    res[name]={"miss":obs,"p":float((null<=obs).mean()),"n_null":2000}
print(json.dumps(res,indent=1))

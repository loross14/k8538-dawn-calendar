import sys, json, numpy as np, swisseph as swe
EXP=sys.argv[1]; sys.path.insert(0,EXP)
from heliacal_drag import GEO, ATMOS, OBSERVER
swe.set_ephe_path(sys.argv[2]); Y=365.2422
BASE=[("Anunitum",2,["Mirach"]),("APIN=Cassiopeia",2,["Schedar","Caph","Ruchbah"]),("Orion",4,["Betelgeuse","Rigel","Bellatrix","Alnilam"]),
      ("Twins",5,["Alhena","Alzirr"]),("Corvus",6,["Gienah","Kraz","Algorab","Minkar"])]
TRI=("APIN=Triangulum",2,["Mothallah"])
def angles(year,cribs):
    jd0=swe.julday(year,1,1,0.0,swe.JUL_CAL); T,L=[],[]
    for _,_,ms in cribs:
        t,l=[],[]
        for s in ms:
            jd=swe.heliacal_ut(jd0,GEO,ATMOS,OBSERVER,s,swe.HELIACAL_RISING,swe.FLG_SWIEPH)[0]
            t.append(((jd-jd0)%Y)*360/Y); l.append(swe.calc_ut(jd,swe.SUN,swe.FLG_SWIEPH)[0][0])
        T.append(np.array(t)); L.append(np.array(l))
    return T,L
def table(A,grid):
    # M[c,g,s]: miss of crib c at grid point g if assigned slice s
    G=[(d,r) for d in (1,-1) for r in grid]; M=np.zeros((len(A),len(G),8))
    for c,a in enumerate(A):
        for gi,(d,r) in enumerate(G):
            x=(d*a+r)%360
            for s in range(8):
                lo,hi=s*45,(s+1)*45
                M[c,gi,s]=0.0 if ((x>=lo)&(x<hi)).any() else min(min(abs((v-lo+180)%360-180),abs((v-hi+180)%360-180)) for v in x)
    return M
def p_of(M,true,n,seed):
    obs=M[np.arange(len(true)),:,np.array(true)-1].sum(0).min()
    rng=np.random.default_rng(seed); R=rng.integers(0,8,(n,len(true)))
    tot=np.zeros((n,M.shape[1]))
    for c in range(len(true)): tot+=M[c][:,R[:,c]].T
    null=tot.min(1); return float(obs), float((null<=obs+1e-9).mean())
gt=np.arange(0,366)*360/Y; gl=np.arange(0,360,2)
out={}
def run(tag,year,cribs,n=10000,seed=20261102):
    T,L=angles(year,cribs); true=[c[1] for c in cribs]
    for wname,A,g in (("time",T,gt),("lon",L,gl)):
        m,p=p_of(table(A,g),true,n,seed); out.setdefault(tag,{})[wname]={"miss":round(m,2),"p":p}
    print(tag, out[tag], flush=True)
run("A_700BCE_10k",-699,BASE)
for y,lab in ((-1499,"1500"),(-999,"1000"),(-399,"400")): run("B_"+lab+"BCE",y,BASE)
for i,c in enumerate(BASE): run("C_drop_"+c[0],-699,[b for j,b in enumerate(BASE) if j!=i])
run("D_no_Corvus",-699,BASE[:4])
run("E_APIN_Triangulum",-699,[BASE[0],TRI]+BASE[2:])
json.dump(out,open("result-robust.json","w"),indent=1)

import json, numpy as np
D={"Orion (SIPA.ZI.AN.NA)":(4,[70]),"Great Twins (MAS.TAB.BA.GAL.GAL)":(5,[70]),"Raven (UGA.MUSEN)":(6,[160])}
labs=list(D); true=[D[k][0] for k in labs]; A={k:np.array(D[k][1])*1.0 for k in labs}  # schematic days; 360-day wheel = degrees
def miss(a,s):
    lo,hi=(s-1)*45,s*45
    if ((a>=lo)&(a<hi)).any(): return 0.0
    return float(min(min(abs((x-lo+180)%360-180),abs((x-hi+180)%360-180)) for x in a))
def best(slices):
    b=(1e9,None,None)
    for d in (1,-1):
        for r in range(360):
            t=sum(miss((d*A[k]+r)%360,s) for k,s in zip(labs,slices))
            if t<b[0]: b=(t,r,d)
    return b
t,r,d=best(true)
per={k:miss((d*A[k]+r)%360,s) for k,s in zip(labs,true)}
rng=np.random.default_rng(20261101)
null=np.array([best(list(rng.integers(1,9,3)))[0] for _ in range(2000)])
print(json.dumps({"miss":t,"start":r,"direction":d,"per_crib":per,"p":float((null<=t).mean()),"dropped":["APIN (no MUL.APIN rising date found)","Anunitum (no MUL.APIN rising date found)"]},indent=1))

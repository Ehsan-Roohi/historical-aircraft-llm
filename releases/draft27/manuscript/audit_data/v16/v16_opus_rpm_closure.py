"""Conditional speed equilibrium, not an engine map or flight certification."""
import json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'output/received_v16_65049531/claude-opus-5-5/response.json'
raw=json.loads(src.read_text())['response'].strip()
if raw.startswith('```'):raw=raw.split('\n',1)[1].rsplit('```',1)[0]
d=json.loads(raw)
assert d['propulsion']['section_polar_assumed']['Clmax']==1.2
def bisect(f,lo,hi):
    assert f(lo)*f(hi)<0,(lo,hi,f(lo),f(hi))
    for _ in range(65):
        mid=(lo+hi)/2
        if f(lo)*f(mid)>0:lo=mid
        else:hi=mid
    return (lo+hi)/2
def prop(V,rpm,N):
    omega=rpm*2*math.pi/60; dr=.9/N
    def loads(vi):
        T=Q=0.
        for i in range(N):
            r=.3+(i+.5)*dr
            beta=math.atan(19/(52.36*r))+math.radians(4)
            phi=math.atan2(V+vi,omega*r)
            cl=max(-1.2,min(1.2,5.655*(beta-phi+math.radians(3))))
            cd=.012+.01*cl*cl
            q=.5*1.225*((V+vi)**2+(omega*r)**2)*1.2*dr
            T+=q*(cl*math.cos(phi)-cd*math.sin(phi))
            Q+=q*(cl*math.sin(phi)+cd*math.cos(phi))*r
        return T,Q
    f=lambda vi:loads(vi)[0]-2*1.225*math.pi*1.2**2*(V+vi)*vi
    vi=bisect(f,0,30);T,Q=loads(vi)
    assert abs(f(vi))<1e-7
    return dict(rpm=rpm,crank_rpm=3.2*rpm,vi=vi,T_N=T,Q_Nm=Q,P_W=omega*Q)
rows=[]
for N in (3,12,48,192):
    baseline=prop(13,500,N)
    # Two explicit hypothetical engine envelopes; neither is supplied evidence.
    for envelope in ('constant_crank_torque','constant_shaft_power'):
        def balance(rpm):
            p=prop(13,rpm,N)
            return p['Q_Nm']-107.43*3.2*.97 if envelope=='constant_crank_torque' else p['P_W']-17460
        rpm=bisect(balance,450,500)
        p=prop(13,rpm,N)
        assert abs(balance(rpm))<1e-6
        rows.append(dict(radial_cells=N,assumed_engine_envelope=envelope,baseline_500rpm=baseline,equilibrium=p,residual=balance(rpm)))
out=dict(parent_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),author='evaluator',
 limitations=['Constant torque and constant power below rated rpm are sensitivity assumptions, not a measured engine map.','Same assumed polar; no swirl, tip loss, Reynolds correction or installation effects.','No same-speed updated aircraft drag available; thrust sufficiency is not assessed.','Negative Cl symmetric clipping is an evaluator convention; low-speed stall and flight remain unverified.'],results=rows,flight_accepted=False)
(ROOT/'analysis/results/v16_opus_rpm_closure01.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(rows[-2:],indent=2))

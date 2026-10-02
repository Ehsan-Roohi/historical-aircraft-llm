"""Evaluator-only radial resolution check of Astra's assumed propeller law."""
import json,math,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'output/received_v16_65049531/gpt-6-astra/response.json'
data=json.loads(json.loads(source.read_text())['response'])
model=data['drive_and_propeller']['reproducible_blade_model']
rho=model['rho_kg_m3']; omega=model['omega_rad_s']; B=model['B']; R=model['R_m']; c=model['c_m']; beta=model['beta_rad']
r0=data['drive_and_propeller']['blade_geometry']['aerodynamic_root_radius_m']
def solve(V,N):
    dr=(R-r0)/N
    def forces(vi):
        T=Q=0.
        for i in range(N):
            r=r0+(i+.5)*dr; ua=V+vi; ut=omega*r
            phi=math.atan2(ua,ut); cl=max(-1,min(1,2*math.pi*(beta-phi))); cd=.02+.02*cl*cl
            q=.5*rho*(ua*ua+ut*ut)*B*c*dr
            T+=q*(cl*math.cos(phi)-cd*math.sin(phi)); Q+=q*r*(cl*math.sin(phi)+cd*math.cos(phi))
        return T,Q
    def residual(v):return forces(v)[0]-2*rho*math.pi*R*R*v*(V+v)
    lo,hi=0.,20.
    assert residual(lo)>0 and residual(hi)<0
    for _ in range(70):
        mid=(lo+hi)/2
        if residual(mid)>0:lo=mid
        else:hi=mid
    vi=(lo+hi)/2; T,Q=forces(vi)
    assert abs(residual(vi))<1e-7
    return dict(speed_m_s=V,radial_cells=N,vi_m_s=vi,thrust_N=T,torque_Nm=Q,shaft_power_W=omega*Q,shaft_ceiling_W=19000,power_reserve_W=19000-omega*Q)
rows=[solve(v,n) for v in (12,13,15) for n in (1,8,32,128)]
result=dict(parent_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),author='evaluator',scope='Same assumed clipped polar and full-disk uniform induction; only midpoint radial resolution changed. No swirl, tip losses, measured data or flight acceptance.',results=rows,flight_proven=False)
p=root/'analysis/results/v16_astra_propeller_quadrature01.json'
p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(rows,indent=2))

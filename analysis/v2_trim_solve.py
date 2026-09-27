"""Fixed-V conditional V2 trim; bounded Newton solve, immutable geometry.

Before execution: 2 meshes (10x48,14x72); <=4 steps each; finite differences
0.2 deg; alpha [-3,12], elevator [-15,15] deg; normalized residual <=0.001.
Thrust is eliminated using T=D/cos(alpha). Two unknowns: alpha and elevator.
No physical flight claim; Astra parasite drag remains incomplete as in probe01.
"""
import concurrent.futures
import hashlib
import json
import math
import subprocess
import numpy as np
from v2_independent_probe import ROOT, EXE, geometry
from avl_reference_gate import parse

OUT=ROOT/'analysis/results/v2_trim_solve01'


def residual(coeff,s,alpha):
    q=.5*1.225*s['V']**2; qs=q*s['S']; w=s['mass']*9.80665
    a=math.radians(alpha); lift=qs*coeff['CLtot']; drag=qs*(coeff['CDind']+s['CD0'])
    thrust=drag/math.cos(a); ma=qs*s['c']*coeff['Cmtot'];mt=s['arm']*thrust
    rz=lift+thrust*math.sin(a)-w; rm=ma+mt
    return {'L_N':lift,'W_N':w,'D_N':drag,'T_N':thrust,'Tvertical_N':thrust*math.sin(a),
            'Maero_Nm':ma,'Mthrust_Nm':mt,'Rz_N':rz,'Rx_N':thrust*math.cos(a)-drag,'My_Nm':rm,
            'normalized':[rz/w,rm/(w*s['c'])], 'useful_power_W':drag*s['V']}


def batch(work,g,foil,states,s):
    work.mkdir()
    (work/'aircraft.avl').write_text(g,encoding='ascii');(work/'section.dat').write_text(foil,encoding='ascii')
    cmd='load aircraft.avl\noper\n'+''.join(f'a a {a:.10f}\nd1 d1 {d:.10f}\nx\nft\nf{i}.txt\nfs\ns{i}.txt\n' for i,(a,d) in enumerate(states))+'\nquit\n'
    (work/'commands.txt').write_text(cmd)
    p=subprocess.run([str(EXE)],input=cmd,capture_output=True,text=True,cwd=work,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (work/'stdout.txt').write_text(p.stdout);(work/'stderr.txt').write_text(p.stderr)
    if p.returncode: raise RuntimeError('solver failure')
    rows=[]
    for i,(a,d) in enumerate(states):
        t=(work/f'f{i}.txt').read_text();c={k:parse(t,k) for k in ['CLtot','CDind','Cmtot','Alpha','pitch']}
        if abs(c['Alpha']-a)>1e-5 or abs(c['pitch']-d)>1e-5: raise ValueError('Condition mismatch')
        rows.append({'alpha_deg':a,'elevator_TE_down_deg':d,'coefficients':c,'balance':residual(c,s,a)})
    (work/'results.json').write_text(json.dumps(rows,indent=2))
    return rows


def solve(name, meshes=((10,48),(14,72)), initial_guess=None):
    dest=OUT/name;dest.mkdir();results=[];guess=None if initial_guess is None else np.array(initial_guess,float)
    for nc,ns in meshes:
        g,foil,s=geometry(name,nc,ns)
        if guess is None: guess=np.array([s['alpha'],s['delta']],float)
        result={'mesh':[nc,ns],'state_parameters':s,'geometry_sha256':hashlib.sha256(g.encode()).hexdigest(),'steps':[],'status':'no_convergence_within_budget'}
        results.append(result)
        for step in range(4):
            states=[guess.tolist(),(guess+[.2,0]).tolist(),(guess+[0,.2]).tolist()]
            rows=batch(dest/f'c{nc}_s{ns}_step{step}',g,foil,states,s)
            result['steps'].append(rows)
            f=np.array(rows[0]['balance']['normalized'])
            if max(abs(f))<=.001:
                result['status']='numerical_trim_only';result['trim']=rows[0]
                probes=batch(dest/f'c{nc}_s{ns}_verify',g,foil,[guess.tolist(),(guess+[-.25,0]).tolist(),(guess+[.25,0]).tolist()],s)
                result['verification']=probes
                if max(abs(np.array(probes[0]['balance']['normalized'])))>.001: raise ValueError('Replay failed')
                cl=(probes[2]['coefficients']['CLtot']-probes[1]['coefficients']['CLtot'])/.5
                cm=(probes[2]['coefficients']['Cmtot']-probes[1]['coefficients']['Cmtot'])/.5
                result['fixed_control_slope']={'CLalpha_per_deg':cl,'Cmalpha_per_deg':cm,'effective_margin_percent':-100*cm/cl}
                break
            jac=np.column_stack([(np.array(rows[j]['balance']['normalized'])-f)/.2 for j in (1,2)])
            delta=np.linalg.solve(jac,-f)
            delta=np.clip(delta,[-2,-3],[2,3]); guess=guess+delta
            if not (-3<=guess[0]<=12 and -15<=guess[1]<=15):
                result['status']='outside_predeclared_bounds';break
        (dest/'summary.json').write_text(json.dumps(results,indent=2))
        print(name,nc,result['status'],flush=True)
        if result['status']!='numerical_trim_only':break
    return {'model':name,'meshes':results}


if __name__=='__main__':
    OUT.mkdir(exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(solve,['gpt-6-astra','claude-opus-5-5']))
    (OUT/'summary.json').write_text(json.dumps({'scope':__doc__,'solver_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),'results':results},indent=2))
    for r in results:
        for m in r['meshes']:
            print(r['model'],m['mesh'],json.dumps(m.get('trim')),json.dumps(m.get('fixed_control_slope')))

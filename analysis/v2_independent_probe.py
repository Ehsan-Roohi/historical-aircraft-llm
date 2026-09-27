"""Bounded attached-flow probes of V2, not a flight or structural validation.

Two meshes and three alpha values each, frozen proposed pitch control. No trim
search or researcher geometry repair. Fable deferred for geometry reconciliation.
Omit vertical surfaces at beta=0; no lateral-directional conclusion is possible.
"""
import concurrent.futures
import hashlib
import json
import math
from pathlib import Path
import subprocess
from avl_reference_gate import parse

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT/'analysis/tools/avl/avl352.exe'
SOURCE = ROOT/'analysis/results/received_v2_audit01'
OUT = ROOT/'analysis/results/v2_independent_probe01'


def geometry(name, nc, ns):
    d = json.loads((SOURCE/(name+'.design.json')).read_text(encoding='utf-8'))
    a = name == 'gpt-6-astra'
    ledger = json.loads((SOURCE/'summary.json').read_text())[name]
    cg = ledger['cg_native_m'][:]
    if a: cg[0] *= -1
    refs = (30,2.5,12) if a else (38,1.8,11)
    lines = [name+' V2 independent probe', '0','0 0 0',' '.join(map(str,refs)), ' '.join(map(str,cg)), '0']
    def surface(label, comp, stations, foil=False, hinge=None):
        lines.extend(['SURFACE',label,f'{nc} 1 {ns} 1','COMPONENT',str(comp),'YDUPLICATE','0'])
        for x,y,z,c,i in stations:
            lines.extend(['SECTION',f'{x} {y} {z} {c} {i}'])
            if foil: lines.extend(['AFILE','section.dat'])
            if hinge is not None: lines.extend(['CONTROL',f'pitch 1 {hinge} 0 1 0 1'])
    if a:
        main = d['lifting_surfaces']['surfaces'][0]
        inc = main['incidence_rad']; x = -(-.2+.625*math.cos(inc)); z=1+.625*math.sin(inc)
        surface('main',1,[(x,0,z,2.5,math.degrees(inc)),(x,6,z,2.5,math.degrees(inc))],True)
        surface('tail',2,[(4.125,0,1,1.5,0),(4.125,2,1,1.5,0)],False,.7)
        sec=d['lifting_surfaces']['section_library']['W2']; xx=sec['u']; up=sec['upper_v']; lo=sec['lower_v']
        alpha=0;delta=math.degrees(d['claimed_flight_state']['controls_rad']['ELEVATOR']);v=18;thrust=400;arm=.15;cd0=125/(.5*1.225*v*v*30)
    else:
        for index,s in enumerate(d['lifting_surfaces'][:2]):
            surface(s['id'],index+1,[(*r['le_xyz'],r['chord'],r['incidence_deg']) for r in s['stations']],True)
        surface('tail_inner',3,[(4.5,0,.6,1.1,0),(4.5,.25,.6,1.1,0)])
        surface('tail_outer',3,[(4.5,.25,.6,1.6,0),(4.5,2.2,.6,1.6,0)],False,1.1/1.6)
        sec=d['section_definitions']['S1'];xx=sec['x_over_c'];up=sec['upper_z_over_c'];lo=sec['lower_z_over_c']
        alpha=6.1;delta=-3.4;v=15;thrust=448;arm=cg[2]-.9;cd0=.05
    points=list(zip(xx,up))[::-1]+list(zip(xx,lo))[1:]
    section='V2 proposed section\n'+'\n'.join(f'{x} {z}' for x,z in points)+'\n'
    return '\n'.join(lines)+'\n',section,dict(alpha=alpha,delta=delta,V=v,T=thrust,arm=arm,CD0=cd0,S=refs[0],c=refs[1],mass=ledger['mass_kg'])


def run(name,nc,ns):
    case=OUT/f'{name}_{nc}_{ns}';case.mkdir()
    geom,foil,s=geometry(name,nc,ns)
    (case/'aircraft.avl').write_text(geom,encoding='ascii');(case/'section.dat').write_text(foil,encoding='ascii')
    alphas=[s['alpha']-.25,s['alpha'],s['alpha']+.25]
    command=f'load aircraft.avl\noper\nd1 d1 {s["delta"]}\n'+''.join(f'a a {a}\nx\nft\nf{i}.txt\n' for i,a in enumerate(alphas))+'\nquit\n'
    (case/'commands.txt').write_text(command)
    result={'model':name,'mesh':[nc,ns],'state':s,'geometry_sha256':hashlib.sha256(geom.encode()).hexdigest()}
    try:
        p=subprocess.run([str(EXE)],input=command,text=True,capture_output=True,cwd=case,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        (case/'stdout.txt').write_text(p.stdout);(case/'stderr.txt').write_text(p.stderr)
        if p.returncode: raise RuntimeError('solver failed')
        rows=[]
        for i,alpha in enumerate(alphas):
            t=(case/f'f{i}.txt').read_text();r={k:parse(t,k) for k in ['CLtot','CDind','Cmtot','Alpha','pitch']}
            if abs(r['Alpha']-alpha)>1e-5 or abs(r['pitch']-s['delta'])>1e-5: raise ValueError('State mismatch')
            q=.5*1.225*s['V']**2; L=q*s['S']*r['CLtot'];D=q*s['S']*(r['CDind']+s['CD0']);a=math.radians(alpha)
            r.update(lift_N=L,drag_N=D,Rz_N=L+s['T']*math.sin(a)-s['mass']*9.80665,Rx_N=s['T']*math.cos(a)-D,My_Nm=q*s['S']*s['c']*r['Cmtot']+s['arm']*s['T'])
            rows.append(r)
        slopeL=(rows[2]['CLtot']-rows[0]['CLtot'])/.5;slopeM=(rows[2]['Cmtot']-rows[0]['Cmtot'])/.5
        result.update(status='completed',records=rows,CLalpha_per_deg=slopeL,Cmalpha_per_deg=slopeM,effective_margin_percent=-100*slopeM/slopeL)
    except subprocess.TimeoutExpired:
        result['status']='timeout_no_retry'
    (case/'summary.json').write_text(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    OUT.mkdir(exist_ok=False)
    jobs=[(n,*mesh) for n in ['gpt-6-astra','claude-opus-5-5'] for mesh in [(6,24),(10,48)]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda args:run(*args),jobs))
    (OUT/'summary.json').write_text(json.dumps({'scope':'Conditional V2 lifting-surface probe, no trim search; parasite drag assumed at CG; no propwash, body moments, stall, flexibility or dynamic validation. Symmetric tail sections represented by flat camber lines. Fable deferred for geometry reconciliation.','solver_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),'results':results},indent=2))
    print(json.dumps(results,indent=2))

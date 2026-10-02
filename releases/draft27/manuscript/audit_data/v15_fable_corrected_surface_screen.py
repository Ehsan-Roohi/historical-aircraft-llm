"""Correct evaluator component/hinge inputs; retain all prior outputs unchanged."""
import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from v15_fable_lateral_screen import geometry as old_geometry, foil_text
from v15_fable_avl_screen import ROOT, EXE, SOURCE, section
from avl_reference_gate import parse

OUT=ROOT/'analysis/results/v15_fable_corrected_surface02'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def parse_st(text):
    values={}
    for m in re.finditer(r'\b([A-Za-z][A-Za-z0-9_\']*)\s*=\s*([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)',text):
        # Keep the matrix's first Cnb; the final spiral-ratio expression ends
        # in '... Cnb = ratio' and must not overwrite the actual derivative.
        values.setdefault(m[1],float(m[2]))
    return values

def geometry(design,nc,ns):
    text=old_geometry(design,nc,ns)
    text,n=re.subn(r'(SURFACE\nupper_tip_pair\n[^\n]+\nCOMPONENT\n)3\n',r'\g<1>2\n',text)
    assert n==1
    # AVL hinge fraction .25 defines an aft flap; a whole-moving plane needs
    # normal rotation over the entire chord. The physical pivot stays metadata.
    assert text.count('pitch 1.0 0.25 0 1 0 1')==2
    text=text.replace('pitch 1.0 0.25 0 1 0 1','pitch 1.0 0.0 0 1 0 1')
    text=text.split('SURFACE\nfin_fixed\n')[0]
    nv=12 if ns==32 else 24
    def vertical(name,x,chord,top,bottom,nspan,control):
        lines=['SURFACE',name,f'{nc} 1 {nspan} 1','COMPONENT','5']
        for z in (top,bottom):
            lines+=section(x,0,z,chord)
            if control: lines+=['CONTROL','yaw 1.0 0.0 0 0 -1 1']
        return '\n'.join(lines)+'\n'
    # Shared upper z stations ensure fin trailing vortices and rudder panels
    # align. The lower rudder extension has no upstream fin.
    text+=vertical('fin_fixed',5.4,1.2,1.8,1.2,nv,False)
    text+=vertical('rudder_upper',6.6,.9,1.8,1.2,nv,True)
    text+=vertical('rudder_lower',6.6,.9,1.2,.8,round(nv*2/3),True)
    return text

def run(folder,commands):
    (folder/'commands.txt').write_text(commands,encoding='ascii')
    p=subprocess.run([str(EXE)],input=commands,cwd=folder,text=True,capture_output=True,timeout=600,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (folder/'stdout.txt').write_text(p.stdout,encoding='utf-8')
    (folder/'stderr.txt').write_text(p.stderr,encoding='utf-8')
    if p.returncode: raise RuntimeError(p.returncode)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mesh',choices=['coarse','fine'],required=True);ap.add_argument('--reparse-only',action='store_true');a=ap.parse_args()
    if a.reparse_only:
        folder=OUT/a.mesh
        p=folder/'summary.json';r=json.loads(p.read_text())
        old=folder/'summary_before_parser_fix.json'
        if not old.exists():old.write_bytes(p.read_bytes())
        r['AVL_stability_derivatives_raw_labels']=parse_st((folder/'stability.txt').read_text())
        r['parser_note']='First derivative occurrence retained; final spiral-ratio expression does not overwrite Cnb.'
        p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
        print(a.mesh,'saved-output parser corrected; no AVL rerun')
        return
    folder=OUT/a.mesh;folder.mkdir(parents=True,exist_ok=False)
    d=json.loads(json.loads(SOURCE.read_text(encoding='utf-8'))['response'])
    nc,ns={'coarse':(8,32),'fine':(12,64)}[a.mesh]
    geom=geometry(d,nc,ns)
    (folder/'aircraft.avl').write_text(geom,encoding='ascii')
    (folder/'section.dat').write_text(foil_text(),encoding='ascii')
    target=353.2*9.80665/(.5*1.225*13**2*42)
    trimfolder=folder/'trim';trimfolder.mkdir()
    for name in ['aircraft.avl','section.dat']: (trimfolder/name).write_bytes((folder/name).read_bytes())
    run(trimfolder,f'load aircraft.avl\noper\na a 5.85\nd2 d2 -3\na c {target:.12f}\nd2 pm 0\nx\nft\nforces.txt\n\nquit\n')
    raw=(trimfolder/'forces.txt').read_text()
    trim={k:parse(raw,k) for k in ['Alpha','pitch','CLtot','Cmtot','CYtot','Cltot','Cntot','CDind']}
    assert abs(trim['CLtot']-target)<2e-4 and abs(trim['Cmtot'])<2e-4
    trim['tail_absolute_incidence_deg']=-4+trim['pitch']
    assert -16<=trim['tail_absolute_incidence_deg']<=8
    print(a.mesh,'corrected trim',trim,flush=True)
    cases={'neutral':(0.,0.,0.)}
    for variable,idx,steps in [('beta',0,[3.,1.5]),('tip',1,[4.,2.]),('rudder',2,[5.,2.5])]:
        for step in steps:
            for sign in [-1,1]:
                values=[0.,0.,0.];values[idx]=sign*step
                cases[f'{variable}_{step}_{sign}']=values
    commands='load aircraft.avl\noper\n'
    for name,(beta,tip,yaw) in cases.items():
        commands+=f'a a {trim["Alpha"]}\nb b {beta}\nd1 d1 {tip}\nd2 d2 {trim["pitch"]}\nd3 d3 {yaw}\nx\nft\n{name}.txt\n'
        if name=='neutral':commands+='st\nstability.txt\n'
    commands+='\nquit\n';run(folder,commands)
    parsed={}
    for name in cases:
        p=folder/f'{name}.txt';t=p.read_text()
        parsed[name]={k:parse(t,k) for k in ['Alpha','Beta','CLtot','Cmtot','CYtot','Cltot','Cntot','CDind']}
        parsed[name]['sha256']=sha(p)
    slopes={}
    for variable,steps in [('beta',[3.,1.5]),('tip',[4.,2.]),('rudder',[5.,2.5])]:
        slopes[variable]={str(step):{k:(parsed[f'{variable}_{step}_1'][k]-parsed[f'{variable}_{step}_-1'][k])/math.radians(2*step) for k in ['CYtot','Cltot','Cntot']} for step in steps}
    st=(folder/'stability.txt').read_text()
    derivatives=parse_st(st)
    report={'scope':'Corrected rigid power-off surface model, quasi-steady prediction only; no measured derivatives, installed trim or modes','mesh':[nc,ns],'source_response_sha256':sha(SOURCE),'geometry_sha256':sha(folder/'aircraft.avl'),'solver_sha256':sha(EXE),'target_CL':target,'trim':trim,'cases':parsed,'slopes_per_rad':slopes,'AVL_stability_derivatives_raw_labels':derivatives,'corrections':['upper center/tip shared COMPONENT2','fin/rudder shared COMPONENT5 and matching upper vertical mesh','whole-moving tail normal rotation over full chord; .25 physical hinge is not an aft-flap fraction'],'missing':['body and gear','installed propulsion','viscous drag and stall','measured section data','unsteady derivatives','physical inertia and loaded-control proof'],'accepted_aircraft_modes':False}
    (folder/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(a.mesh,'13 corrected cases complete',flush=True)

if __name__=='__main__':main()

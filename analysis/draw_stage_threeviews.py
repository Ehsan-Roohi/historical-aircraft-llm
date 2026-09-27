"""Traceable orthographic engineering schematics; never invented solid geometry.

V1: archived solver chord planes. V2: solver chord planes plus declared fins,
propeller swept discs and explicitly connected frame members. Fable remains a
station-envelope drawing, not an accepted solver geometry. No code from model
responses is executed. All coordinates below use x aft, y right, z up.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import numpy as np
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/stage_threeviews'
MODELS=['gpt-6-astra','claude-fable-5-1','claude-opus-5-5']
NAMES=['Astra','Fable','Opus']
V1=['avl_fixed_control_slope04/astra_c12_s80','avl_control_grid01/fable','avl_fixed_control_slope06/opus_c12_s80']
V2=['v2_trim_solve01/gpt-6-astra/c14_s72_verify',None,'v2_trim_opus_capacity_recovery01/claude-opus-5-5/c12_s50_verify']

def avl(path,rotate_incidence=True):
    lines=path.read_text().splitlines(); surfaces=[]; current=None
    for i,line in enumerate(lines):
        if line.strip()=='SURFACE':
            current={'name':lines[i+1],'sections':[],'mirror':False};surfaces.append(current)
        elif line.strip()=='YDUPLICATE':current['mirror']=True
        elif line.strip()=='SECTION':current['sections'].append(list(map(float,lines[i+1].split()[:5])))
    polys=[]
    for s in surfaces:
        for sign in ([1,-1] if s['mirror'] else [1]):
            le=[];te=[]
            for x,y,z,c,a in s['sections']:
                a=math.radians(a) if rotate_incidence else 0;le.append([x,sign*y,z]);te.append([x+c*math.cos(a),sign*y,z-c*math.sin(a)])
            polys.append((s['name'],np.array(le+te[::-1])))
    return polys,np.array(list(map(float,lines[4].split())))

def declared_v2(i,d):
    """Return extra declared geometry, retaining incomplete-member omissions."""
    polys=[];members=[];discs=[];omissions=[]
    if i==0:
        s=d['lifting_surfaces']['surfaces'][2];x=-s['leading_edge_xyz_at_root'][0];z=s['station_z_m'];c=s['chord_m']
        polys.append(('fin',np.array([[x,0,z[0]],[x,0,z[-1]],[x+c,0,z[-1]],[x+c,0,z[0]]])))
        p=d['propulsion']['propeller'];hub=np.array(p['hub_xyz_m'],float);hub[0]*=-1;discs=[(hub,p['diameter_m']/2)]
        tr=d['structural_members']['node_sets'][0];xs=[-x for x in tr['X_m']];ys=tr['Y_m'];zs=tr['Z_m']
        for x in xs:
            pts=[[x,ys[0],zs[0]],[x,ys[1],zs[0]],[x,ys[1],zs[1]],[x,ys[0],zs[1]],[x,ys[0],zs[0]]];members.append(np.array(pts))
        for y in ys:
            for z in zs:members.append(np.array([[x,y,z] for x in xs]))
        inc=d['lifting_surfaces']['surfaces'][0]['incidence_rad']
        for u in [.25,.7]:
            sx=.2+(u-.25)*2.5*math.cos(inc);sz=1-(u-.25)*2.5*math.sin(inc)
            members.append(np.array([[sx,-6,sz],[sx,6,sz]]))
            for y in [-6,-4,-2,2,4,6]:
                for z in [2.3,-.4]:members.append(np.array([[sx,0,z],[sx,y,sz]]))
            members.append(np.array([[sx,0,-.4],[sx,0,2.3]]))
        gear=d['structural_members']['node_sets'][4]['points_xyz_m']
        wheels=[np.array(gear[k],float)*np.array([-1,1,1]) for k in ['WL','WR']]
        for pt in wheels:
            for x in [-1,1.5]:members.append(np.array([pt,[-x,.4*np.sign(pt[1]),-.4]]))
            t=np.linspace(0,2*np.pi,81);members.append(np.array([pt[0]+.3*np.cos(t),np.full(t.shape,pt[1]),pt[2]+.3*np.sin(t)]).T)
        members.append(np.array(wheels))
        members.append(np.array([[-x,y,z] for x,y,z in [gear['SKID_ROOT'],gear['SKID_CONTACT']]]))
        drive=d['propulsion']['drive']['shaft_endpoints_xyz_m'];members.append(np.array([[-x,y,z] for x,y,z in drive]))
        omissions=['Declared frame, main-wing braces and gear shown; remaining joints, ribs, pilot and engine solids omitted.']
    else:
        p=d['propulsion']
        if i==1:
            discs=[(np.array(h),p['propellers']['diameter_m']/2) for h in p['propellers']['hub_xyz']]
            for s in d['lifting_surfaces']:
                if 'tip_panels' in s['id']:continue
                stations=s['stations'];paired=isinstance(stations[0]['leading_edge_xyz'][1],str)
                for sign in ([1,-1] if paired else [1]):
                    le=[];te=[]
                    for st in stations:
                        x,y,z=st['leading_edge_xyz'];y=sign*float(y.replace('±','')) if isinstance(y,str) else y;c=st['chord']
                        a=math.radians(st.get('incidence_deg',0));
                        if 'tail' in s['id']:
                            x=5.65-.25*math.cos(a);z=.775+.25*math.sin(a)
                        le.append([x,y,z]);te.append([x+c*math.cos(a),y,z-c*math.sin(a)])
                    polys.append((s['id'],np.array(le+te[::-1])))
            # The two declared upper tip panels, neutral roll state.
            for sign in [-1,1]:
                polys.append(('tip station envelope',np.array([[.95,sign*4.25,1.85],[.95,sign*5.75,1.85],[2.8,sign*5.75,1.85],[2.8,sign*4.25,1.85]])))
            nodes=d['structural_members']['nodes'];rows=d['structural_members']['connectivity'];key='nodes'
            for x in [1.15,2.55]:
                for y in [-4.25,-2.6,-.9,.9,2.6,4.25]:members.append(np.array([[x,y,.14],[x,y,1.85]]))
            omissions=['Fable: rectangular station envelopes; rounded wing tips are NOT reconstructed.', 'Only explicit node chains drawn; ambiguous connectivity, drive conflicts and mass envelopes remain unresolved.']
        else:
            p=p['propeller'];discs=[(np.array(p['axis'][0]),p['radius_m'])]
            # Fin/rudder step at z=.68, using the stated breakdown, not a taper.
            polys.append(('fin/rudder',np.array([[4.8,0,.6],[4.8,0,2],[6.1,0,2],[6.1,0,.68],[5.6,0,.68],[5.6,0,.6]])))
            nodes=d['structural_members']['nodes'];rows=d['structural_members']['members'];key='connect'
            omissions=['Only explicit node chains drawn; unspecified cross-bracing, landing gear, pilot and nacelle solids omitted.']
        for row in rows:
            chains=row.get(key,[])
            if not isinstance(chains,list):continue
            for chain in chains:
                keys=chain.split('-')
                if all(k in nodes for k in keys):
                    pts=np.array([nodes[k] for k in keys],float);members.append(pts)
                    if i==2:members.append(pts*np.array([1,-1,1]))
    return polys,members,discs,omissions

def draw(i,stage):
    model='wright-flyer-1903' if stage=='Wright' else MODELS[i];sources=[];members=[];discs=[];notes=[]
    if stage=='Wright':
        source=ROOT/'analysis/results/wright_reconstruction_family03/flat_i+0_a0/wing.avl'
        polys,cg=avl(source,rotate_incidence=False);sources=[source,ROOT/'analysis/results/wright_reconstruction_family02/definition.json']
        notes=['Independent lifting-surface reconstruction from Christman/Kelley planform and side-view landmarks; not the historical aircraft.',
               'Rudders, propellers, airframe, tip droop and fabric shape omitted. Red + is the moment reference, NOT a verified historical CG.']
    elif stage=='V1':
        source=ROOT/'analysis/results'/V1[i]/'aircraft.avl';polys,cg=avl(source);sources=[source]
        notes=['Archived evaluator lifting surfaces only; airframe, fins and propulsion not reconstructed.']
    else:
        source=ROOT/'analysis/results/received_v2_audit01'/f'{model}.design.json';d=json.loads(source.read_text(encoding='utf8'));sources=[source]
        ledger=ROOT/'analysis/results/received_v2_audit01/summary.json';sources.append(ledger);cg=np.array(json.loads(ledger.read_text())[model]['cg_native_m']);
        if i==0:cg[0]*=-1
        polys=[]
        if V2[i]:
            solver=ROOT/'analysis/results'/V2[i]/'aircraft.avl';polys,_=avl(solver);sources.append(solver)
        extra,members,discs,notes=declared_v2(i,d);polys+=extra
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="780" viewBox="0 0 1800 780">', '<rect width="1800" height="780" fill="white"/>', '<style>text{font-family:Arial,sans-serif;fill:#203442;font-size:19px}</style>']
    def text(x,y,s,size=19):svg.append(f'<text x="{x}" y="{y}" style="font-size:{size}px">{escape(s)}</text>')
    projections=[(1,0,'PLAN','y (m)','x aft (m)'),(0,2,'SIDE','x aft (m)','z (m)'),(1,2,'FRONT','y (m)','z (m)')]
    curves=[]
    for hub,r in discs:
        t=np.linspace(0,2*np.pi,181);curves.append(np.array([np.full(t.shape,hub[0]),hub[1]+r*np.cos(t),hub[2]+r*np.sin(t)]).T)
    # Identical metres-to-pixels scale across all sheets and all projections.
    scale=38
    for panel,(u,v,title,xlabel,ylabel) in enumerate(projections):
        allpts=np.concatenate([p for _,p in polys]+members+curves+[cg[None,:]])
        mid=(allpts[:,[u,v]].min(axis=0)+allpts[:,[u,v]].max(axis=0))/2
        def project(p):return (300+600*panel+scale*(p[u]-mid[0]),350+(1 if title=='PLAN' else -1)*scale*(p[v]-mid[1]))
        def line(pts,color,width=1,dash=False,fill='none'):
            xy=' '.join(f'{x:.3f},{y:.3f}' for x,y in map(project,pts))
            svg.append(f'<polyline points="{xy}" fill="{fill}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
        for name,pts in polys:
            tail=any(k in name.lower() for k in ['tail','ht','fin','rudder','vt','p11','p12','p13','canard'])
            line(np.concatenate([pts,pts[:1]]),'#183345',1.7,fill='#efdbbd' if tail else '#d5e4ed')
        for pts in members:line(pts,'#52636d',1)
        for pts in curves:line(pts,'#337d65',1.8,True)
        x,y=project(cg);svg.append(f'<path d="M{x-7},{y}h14 M{x},{y-7}v14" stroke="#b52436" stroke-width="2.5"/>')
        text(60+600*panel,135,title,23)
        text(60+600*panel,570,f'{xlabel} / {ylabel}',17)
        svg.append(f'<path d="M{60+600*panel},605h76 m-76,-5v10 m76,-10v10" fill="none" stroke="#203442" stroke-width="2"/>')
        text(145+600*panel,611,'2 m',17)
    label='geometry unresolved' if stage=='V2' and i==1 else 'reference geometry / neutral controls'
    title='Wright Flyer I (1903)  |  documented reconstruction boundary' if stage=='Wright' else f'{NAMES[i]}  |  {stage}  |  {label}'
    text(60,60,title,29)
    legend='Blue: main wings  |  Ochre: canard  |  Red +: moment reference (not CG)' if stage=='Wright' else 'Blue: wing  |  Ochre: tail  |  Dashed green: propeller disc  |  Red +: CG'
    text(60,665,legend,19)
    text(60,698,'Coordinate reconstruction; not a construction drawing. Identical metric scale in all views; x aft, y right, z up.',17)
    text(60,729,notes[0],17)
    if len(notes)>1:text(60,758,notes[1],17)
    dest=OUT/stage;dest.mkdir(parents=True,exist_ok=True);stem=dest/model
    svg.append('</svg>');stem.with_suffix('.svg').write_text('\n'.join(svg),encoding='utf8')
    return {'model':model,'stage':stage,'figure':stem.with_suffix('.svg').relative_to(ROOT).as_posix(),'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'omissions':notes,'control_display':'neutral/reference, not the deformed trim state','units':'m','frame':'x aft, y right, z up'}

if __name__=='__main__':
    records=[draw(i,s) for s in ['V1','V2'] for i in range(3)]+[draw(0,'Wright')]
    (OUT/'manifest.json').write_text(json.dumps(records,indent=2),encoding='utf8')
    print('Generated 7 versioned three-view SVG sheets; raster previews rendered separately.')

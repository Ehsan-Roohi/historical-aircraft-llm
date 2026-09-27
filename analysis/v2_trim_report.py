"""Summarize archived trim and surface-force bookkeeping, no new solver runs."""
import json
import re
from v2_trim_solve import ROOT,OUT
from avl_reference_gate import parse


def main():
    runs=[]
    for directory in [OUT,OUT.parent/'v2_trim_opus_capacity_recovery01']:
        for name in ['gpt-6-astra','claude-opus-5-5']:
            p=directory/name/'summary.json'
            if p.exists():runs.append((directory,{'model':name,'meshes':json.loads(p.read_text())}))
    summary=[]
    for directory,model in runs:
        for mesh in model['meshes']:
            if mesh['status']!='numerical_trim_only':continue
            s=mesh['state_parameters'];t=mesh['trim'];nc,ns=mesh['mesh'];qs=.5*1.225*s['V']**2*s['S']
            path=directory/model['model']/f'c{nc}_s{ns}_verify/s0.txt'
            components=[]
            for block in re.split(r'(?=  Surface #)',path.read_text())[1:]:
                title=re.search(r'Surface #\s*\d+\s+([^\r\n]+)',block).group(1).strip()
                part=block.split('Forces referred to Ssurf, Cave')[0]
                components.append({'surface':title,'lift_N':qs*parse(part,'CLsurf'),'pitch_moment_Nm':qs*s['c']*parse(part,'Cmsurf')})
            clsum=sum(c['lift_N'] for c in components);cmsum=sum(c['pitch_moment_Nm'] for c in components)
            clbound=(len(components)+1)*5e-6*qs;cmbound=clbound*s['c']
            if abs(clsum-t['balance']['L_N'])>clbound+1e-7:raise ValueError('Surface lift closure')
            if abs(cmsum-t['balance']['Maero_Nm'])>cmbound+1e-7:raise ValueError('Surface moment closure')
            summary.append({'model':model['model'],'mesh':mesh['mesh'],'alpha_deg':t['alpha_deg'],
                            'elevator_TE_down_deg':t['elevator_TE_down_deg'],'balance':t['balance'],
                            'slope':mesh['fixed_control_slope'],'components':components,
                            'surface_sum_closure_within_print_precision':True})
    (OUT/'compact_report.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()

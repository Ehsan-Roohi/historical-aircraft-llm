"""Extract surface and strip loads at three frozen surface-model equilibria."""
import json
from pathlib import Path
from v15_fable_corrected_surface_screen import run,sha
from avl_reference_gate import parse
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/v15_tail_strip_loads01'
CASES={
 'original':ROOT/'analysis/results/v15_fable_aft_retrim01/fuel0_fine',
 'enlarged':ROOT/'analysis/results/v15_fable_tail_trade01/fine_s1.75_p65_x0.35_f0_fine',
 'plus2kg':ROOT/'analysis/results/v15_tail_reinforcement_sensitivity01/plus2kg_s1.75_p65_x0.35_f0_fine',
}
def main():
    OUT.mkdir(exist_ok=False)
    records=[]
    for name,src in CASES.items():
        folder=OUT/name;folder.mkdir()
        for fn in ('aircraft.avl','section.dat'):(folder/fn).write_bytes((src/fn).read_bytes())
        text=(src/'forces.txt').read_text()
        alpha=parse(text,'Alpha');pitch=parse(text,'pitch')
        run(folder,f'load aircraft.avl\noper\na a {alpha}\nd2 d2 {pitch}\nx\nft\nforces.txt\nfn\nsurfaces.txt\nfs\nstrips.txt\n\nquit\n')
        t=(folder/'forces.txt').read_text()
        assert abs(parse(t,'CLtot')-parse(text,'CLtot'))<2e-5
        assert abs(parse(t,'Cmtot'))<2e-5
        records.append(dict(case=name,alpha_deg=alpha,pitch_command_deg=pitch,
               source_geometry_sha256=sha(src/'aircraft.avl'),surface_sha256=sha(folder/'surfaces.txt'),strip_sha256=sha(folder/'strips.txt')))
        print(name,'frozen equilibrium reproduced; strip loads saved',flush=True)
    (OUT/'manifest.json').write_text(json.dumps(dict(scope='Rigid unpowered surface loads only, not design envelope or measurements',cases=records),indent=2)+'\n')
if __name__=='__main__':main()

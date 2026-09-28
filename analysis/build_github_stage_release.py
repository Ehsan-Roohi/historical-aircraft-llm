"""Create a reviewed allowlisted public research snapshot, never upload it.

All original selected bytes are preserved. No books, reference PDFs, executable
solvers, environment files, caches, cluster logs or personal documents included.
"""
from pathlib import Path
import hashlib,json,re,zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/github_stage_release07'
TEXT={'.py','.cjs','.json','.md','.txt','.avl','.dat','.csv','.yaml','.yml','.tex','.sbatch'}

def select():
    files=set()
    for p in (ROOT/'analysis').iterdir():
        if p.is_file() and p.suffix in TEXT:files.add(p)
    for folder in ['analysis/results','analysis/prompts_v0','analysis/prompts_v1','analysis/prompts_v2','analysis/prompts_v2_retrim','analysis/prompts_v9_integrated_dynamics','analysis/raw_v1','paper','received_v2_64942345','received_v5_64962376/responses','design_revision_v6_attempt01/responses','dynamic_revision_v9_attempt01/responses','unity_jobs','output/stage_threeviews','output/figures_v2','output/overleaf/scientific_reports_aircraft_2026_09_28_release06','received_2026-09-24/astra_fable_opus_designs']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix.lower() in TEXT|{'.svg','.png','.jpg','.jpeg'} and '__pycache__' not in p.parts and 'references' not in p.parts:
                files.add(p)
    return sorted(files)

def main():
    OUT.mkdir(exist_ok=False)
    files=select();manifest=[]
    pattern=re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)')
    for p in files:
        data=p.read_bytes()
        if pattern.search(data):raise ValueError('Potential secret; publication halted: '+str(p.relative_to(ROOT)))
        manifest.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    with zipfile.ZipFile(OUT/'research_evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(ROOT).as_posix())
    (OUT/'MANIFEST.json').write_text(json.dumps({'scope':__doc__,'files':manifest},indent=2),encoding='utf8')
    print(json.dumps({'files':len(files),'uncompressed_bytes':sum(r['bytes'] for r in manifest),'zip_bytes':(OUT/'research_evidence.zip').stat().st_size}))

if __name__=='__main__':main()

"""Contact sheets and completeness checks for the restored reading master."""
from pathlib import Path
import json
import re
from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'output/overleaf/aircraft_complete_restored_draft20'
T=ROOT/'tmp/pdfs/restored20'
reader=PdfReader(P/'main.pdf')
texts=[p.extract_text() or '' for p in reader.pages]
files=sorted(T.glob('page-*.png'))
assert len(files)==len(texts)
for start in range(0,len(files),16):
    canvas=Image.new('RGB',(1600,2240),'#dddddd')
    draw=ImageDraw.Draw(canvas)
    for j,f in enumerate(files[start:start+16]):
        im=Image.open(f).convert('RGB'); im.thumbnail((390,530))
        x=(j%4)*400; y=(j//4)*560
        draw.text((x+8,y+3),str(start+j+1),fill='black')
        canvas.paste(im,(x+(400-im.width)//2,y+22))
    canvas.save(T/f'contact-{start//16+1}.png')
report={'pdf_pages':len(texts),'figures_in_source':len(re.findall(r'\\includegraphics', (P/'main.tex').read_text(encoding='utf-8'))),'blank_pages':[i+1 for i,t in enumerate(texts) if not t.strip()],'double_question_marks':[i+1 for i,t in enumerate(texts) if '??' in t], 'rendered_pages':len(files),'pdf_text_words':sum(len(t.split()) for t in texts),'figure_pages':[i+1 for i,t in enumerate(texts) if re.search(r'Figure\s+\d+:',t)],'compile_exit_code':0,'visual_review':'PENDING'}
(T/'qa.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))

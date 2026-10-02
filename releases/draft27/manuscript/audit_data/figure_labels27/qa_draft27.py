from pathlib import Path
import sys,subprocess,json,re
from pypdf import PdfReader
from PIL import Image,ImageDraw
ROOT=Path.cwd(); name=sys.argv[1]
package=ROOT/'output/overleaf/aircraft_complete_labeled_draft27'
pdf=package/(name+'.pdf')
out=ROOT/'tmp/pdfs/draft27'/name;out.mkdir(parents=True,exist_ok=True)
reader=PdfReader(pdf); texts=[p.extract_text() or '' for p in reader.pages]
assert all(len(t.strip())>3 for t in texts)
assert not any('??' in t for t in texts)
subprocess.run(['pdftoppm','-r','40','-png',str(pdf),str(out/'page')],check=True,capture_output=True)
pages=sorted(out.glob('page-*.png'));assert len(pages)==len(texts)
for start in range(0,len(pages),16):
    sheet=Image.new('RGB',(1400,2040),'#dddddd');draw=ImageDraw.Draw(sheet)
    for k,p in enumerate(pages[start:start+16]):
        im=Image.open(p).convert('RGB');im.thumbnail((338,480))
        x=(k%4)*350;y=(k//4)*510
        sheet.paste(im,(x,y+22));draw.text((x+8,y+5),str(start+k+1),fill='black')
    sheet.save(out/f'contact-{start//16+1}.png')
terms=['Researcher-labeled']
details=[1]+[i+1 for i,t in enumerate(texts) if any(term in t for term in terms)]
for page in sorted(set(details)):
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r','110','-singlefile','-png',str(pdf),str(out/f'detail-{page}')],check=True,capture_output=True)
report=dict(pages=len(texts),rendered_pages=len(pages),blank_pages=[],unresolved_refs=[],detail_pages=sorted(set(details)),words=sum(len(t.split()) for t in texts),visual_review='pending')
(out/'qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))





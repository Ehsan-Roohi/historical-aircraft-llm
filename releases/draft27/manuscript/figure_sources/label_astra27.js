// Researcher display-only relabeling. The immutable V0 geometry is copied verbatim.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const sharp = require('sharp');
const dir = __dirname;
const src = fs.readFileSync(path.join(dir, 'astra_oblique_v0.svg'), 'utf8');
const geometry = src.slice(src.indexOf('  <!-- Mapping:'), src.indexOf('  <!-- Leaders and external labels -->'));
if (!geometry || !src.includes('A — rear supporting surface')) throw Error('Unexpected source');
const entries = [
 [1,'A','Rear supporting surface',20,118,'M225 157H285L359 190',405,173],
 [2,'F','Forward surface',950,118,'M965 160H946L863 206',773,215],
 [3,'R','Vertical rudder',20,230,'M210 237H296L409 233',415,252],
 [4,'Q','Propeller swept disk',20,328,'M229 335H271L314 303',340,329],
 [5,'S','Drive shaft and guard',20,437,'M239 444H291L493 335',508,338],
 [6,'O','Operator and seat',465,589,'M540 562V520L613 346',595,349],
 [7,'M','Motor and cooling',950,419,'M954 436H897L707 407',696,425],
 [8,'W','Wheels',785,554,'M799 532H703L591 507',620,493]
];
const escape = s => s.replace(/&/g,'&amp;');
let annotations = '';
for(const [n,letter,name,x,y,leader,cx,cy] of entries){
 annotations += `<g aria-label="${escape(name)}"><path d="${leader}" fill="none" stroke="#445c6b" stroke-width="1.7"/><circle cx="${cx}" cy="${cy}" r="15" fill="white" stroke="#152b38" stroke-width="2"/><text x="${cx}" y="${cy+6}" text-anchor="middle" font-size="18" font-weight="bold">${n}</text><text x="${x}" y="${y}" font-size="21" font-weight="bold">${n} · ${letter}</text><text x="${x}" y="${y+25}" font-size="20">${escape(name)}</text></g>`;
}
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700" role="img" aria-label="Astra V0 geometry with named component callouts"><rect width="1200" height="700" fill="white"/><g font-family="Arial,sans-serif" fill="#172936"><text x="20" y="32" font-size="24" font-weight="bold">Astra V0 — component geometry</text></g>${geometry}<g font-family="Arial,sans-serif" fill="#172936">${annotations}<path d="M20 619H1180" stroke="#9ba9b0"/><text x="20" y="649" font-size="19">Dashed brown prism: truss envelope, not resolved structural members.</text><text x="20" y="678" font-size="19">Schematic V0 proposal; unknown placement and interfaces remain unresolved.</text></g></svg>`;
async function main(){
 fs.writeFileSync(path.join(dir,'astra_oblique_v0_detail.svg'),svg);
 const png=path.join(dir,'..','figures','astra_oblique_v0_detail.png');
 await sharp(Buffer.from(svg)).resize({width:6000}).png().toFile(png);
 const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
 fs.writeFileSync(path.join(dir,'label_astra27_audit.json'),JSON.stringify({source:'astra_oblique_v0.svg',source_sha256:hash(src),geometry_block_sha256:hash(geometry),geometry_copied_verbatim:true,annotations_only:true,removed:'All legacy external leaders and cropped coordinate triad; no aircraft geometry removed',mapping:entries.map(([n,letter,name])=>({n,source_letter:letter,name})),source_evidence:'Source SVG named external labels and manuscript Readable key to Astra V0',svg_sha256:hash(svg),png_sha256:hash(fs.readFileSync(png)),pixels:[6000,3500],limitations:'Only eight principal components are numbered; smaller schematic equipment remains described in the adjacent manuscript key. This is display relabeling, not revised engineering.'},null,2));
 await sharp(Buffer.from(svg)).resize({width:1500}).png().toFile(path.join(dir,'label_astra27_preview.png'));
}
main().catch(e=>{console.error(e);process.exit(1)});

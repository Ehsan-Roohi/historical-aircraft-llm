// Researcher display revision: source aircraft geometry is kept byte-for-byte.
// Only original prose, annotation axes, and outside legend furniture are omitted.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');
const dir = __dirname;
const out = path.join(dir, '..', 'figures');
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const escape = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;');
const specs = [
  {name:'fable',title:'Fable V0: component identification',dx:-95,dy:-78,
   labels:[['Upper tip panel','roll control'],['Lower wing deck',''],['Upper tip panel','opposite side'],['Seated operator',''],['Engine group',''],['Propeller swept disc','one of two proposed'],['Tailplane + fin/rudder','unresolved interface'],['Skids and wheels','ground-gear proposal']],
   points:[[785,192],[822,405],[263,493],[454,364],[556,458],[740,447],[1005,598],[645,686]]},
  {name:'opus',title:'Opus V0: component identification',dx:12,dy:20,
   labels:[['Upper-wing roll flap',''],['Cockpit / nacelle',''],['Wing decks + struts',''],['Engine group',''],['Pusher swept disc',''],['Tailplane + elevator','and fin / rudder'],['Twin booms + controls','schematic routing'],['Skids and wheels','ground-gear proposal']],
   points:[[770,209],[662,509],[808,300],[588,449],[489,331],[348,274],[455,398],[561,580]]}
];
const rows=[];
async function main(){
 for(const s of specs){
  const sourcePath=path.join(dir,`${s.name}_oblique_v0.svg`);
  const original=fs.readFileSync(sourcePath,'utf8');
  let geometry;
  let omissions;
  if(s.name==='fable'){
   geometry=original.slice(original.indexOf('<g stroke="#333"'),original.indexOf('<g font-size="12" fill="#222">'));
   const axis='<path d="M110,560l45,17M110,560l28,-15M110,560v-50" stroke="#000"/>';
   if(!geometry.includes(axis))throw Error('Fable axis not found');
   geometry=geometry.replace(axis,'');
   omissions=['Original title and text labels','Original legend panel outside aircraft group','Unlabelled annotation axis triad'];
  }else{
   geometry=original.slice(original.indexOf('<!-- lower wing -->'),original.indexOf('<!-- labels -->'));
   geometry=geometry.replace(/<text\b[\s\S]*?<\/text>/g,'');
   omissions=['Original title and text labels','Original annotation axes','Original legend panel and gear-label leader (470,645)-(540,580)'];
  }
  // Geometric primitive list is unchanged relative to the selected source region.
  const primitives=geometry.match(/<(?:polygon|polyline|line|path|circle|ellipse)\b[^>]*\/?>/g)||[];
  if(primitives.length<30)throw Error('Insufficient retained geometry');
  for(const p of primitives)if(!original.includes(p))throw Error('Aircraft primitive changed');
  const markers=s.points.map(([x,y],i)=>`<g><circle cx="${x}" cy="${y}" r="17" fill="white" fill-opacity=".95" stroke="#15364b" stroke-width="2"/><text x="${x}" y="${y+7}" font-size="23" font-weight="bold" text-anchor="middle" fill="#15364b">${i+1}</text></g>`).join('');
  const key=s.labels.map(([a,b],i)=>{
   const y=128+i*65;
   return `<circle cx="1081" cy="${y-6}" r="17" fill="#15364b"/><text x="1081" y="${y+2}" font-size="23" text-anchor="middle" fill="white" font-weight="bold">${i+1}</text><text x="1111" y="${y}" font-size="25" fill="#15364b" font-weight="bold">${escape(a)}</text>${b?`<text x="1111" y="${y+25}" font-size="22" fill="#455b66">${escape(b)}</text>`:''}`;
  }).join('');
  const detail=`<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="800" viewBox="0 0 1500 800" font-family="Arial,Helvetica,sans-serif"><rect width="1500" height="800" fill="white"/><text x="25" y="39" font-size="29" font-weight="bold" fill="#15364b">${s.title}</text><g transform="translate(${s.dx} ${s.dy})">${geometry}${markers}</g><rect x="1046" y="68" width="444" height="610" rx="10" fill="#f3f6f8" stroke="#b8c6ce"/><text x="1064" y="95" font-size="23" fill="#455b66">NUMBERED COMPONENT KEY</text>${key}<path d="M25 710H1475" stroke="#bac5cb"/><text x="25" y="744" font-size="24" fill="#15364b">Source geometry preserved. Labels identify proposed assemblies, not validated installations.</text><text x="25" y="777" font-size="23" fill="#455b66">V0 concept only: schematic drive and control paths; unresolved clearances and ground geometry.</text></svg>`;
  const svgFile=path.join(dir,`${s.name}_oblique_v0_detail.svg`);
  const pngFile=path.join(out,`${s.name}_oblique_v0_detail.png`);
  fs.writeFileSync(svgFile,detail);
  const result=await sharp(Buffer.from(detail)).resize({width:6000}).png().toFile(pngFile);
  await sharp(Buffer.from(detail)).resize({width:1500}).png().toFile(path.join(dir,`${s.name}_detail27_preview.png`));
  if(result.width!==6000||result.height!==3200)throw Error('Unexpected size');
  rows.push({name:s.name,source_sha256:sha(original),svg_sha256:sha(detail),png_sha256:sha(fs.readFileSync(pngFile)),retained_primitive_count:primitives.length,retained_primitive_sha256:sha(primitives.join('\n')),source_geometry_attributes_unchanged:true,display_translation:[s.dx,s.dy],omitted_annotations:omissions,component_key:s.labels.map((x,i)=>({number:i+1,label:x.filter(Boolean).join('; '),source_point:s.points[i]})),pixels:[6000,3200],viewbox:[0,0,1500,800],minimum_key_font_svg_units:22,minimum_key_font_pt_at_240mm:22*240/1500*72/25.4,scientific_claim:'Identification only; no geometry repair, dimensions, motion validation, or flight certification added.'});
 }
 fs.writeFileSync(path.join(dir,'fable_opus_label_audit27.json'),JSON.stringify({status:'source-derived display annotations',mapping_provenance:'main.tex Fable detail key and Opus detail key, checked against original V0 SVG component comments and labels',rows},null,2)+'\n');
 console.log(JSON.stringify(rows.map(r=>({name:r.name,pixels:r.pixels,min_key_pt:r.minimum_key_font_pt_at_240mm,primitives:r.retained_primitive_count})),null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1;});

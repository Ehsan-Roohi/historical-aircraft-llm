// Render coordinate-generated SVGs without changing their geometry.
const fs=require('node:fs'),path=require('node:path');
const sharp=require('C:/Users/roohie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..');
(async()=>{for(const stage of ['V1','V2']) for(const model of ['gpt-6-astra','claude-fable-5-1','claude-opus-5-5']) {
 const stem=path.join(root,'output/stage_threeviews',stage,model);
 await sharp(stem+'.svg').png().toFile(stem+'.png');
} const w=path.join(root,'output/stage_threeviews/Wright/wright-flyer-1903');
await sharp(w+'.svg').png().toFile(w+'.png');
console.log('Seven previews rendered.');})().catch(e=>{console.error(e);process.exitCode=1;});

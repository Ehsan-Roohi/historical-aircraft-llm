// Re-rasterize archival V0 SVG plates. This improves line sampling only; it
// does not alter the frozen design or make dense annotation text larger.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');

const repository = path.resolve(__dirname, '..');
const publicSources = path.join(repository, 'figures', 'source_svg');
const sourceDir = fs.existsSync(publicSources) ? publicSources : __dirname;
const outputDir = process.env.JOA_OUTPUT_DIR || path.join(repository, 'figures', 'generated', 'v0');
const names = ['astra_oblique_v0','fable_oblique_v0','opus_oblique_v0'];
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

async function main() {
  fs.mkdirSync(outputDir, {recursive:true});
  const rows=[];
  for (const name of names) {
    const original = fs.readFileSync(path.join(sourceDir,`${name}.svg`));
    const sourceText = original.toString('utf8');
    if (!sourceText.includes('viewBox="0 0 1200 900"')) throw new Error(`Unexpected archival SVG: ${name}`);
    const svgPath = path.join(outputDir,`${name}.svg`);
    const pngPath = path.join(outputDir,`${name}.png`);
    fs.writeFileSync(svgPath,original);
    const rendered = await sharp(original).resize({width:6000}).png().toFile(pngPath);
    if (rendered.width!==6000 || rendered.height!==4500) throw new Error(`Unexpected rendered dimensions: ${name}`);
    rows.push({name,original_svg_sha256:digest(original),png_sha256:digest(fs.readFileSync(pngPath)),
               pixels:[rendered.width,rendered.height],
               caveat:'Archival 1200x900 SVG unchanged; physical annotation size is not improved'});
  }
  fs.writeFileSync(path.join(outputDir,'MANIFEST.json'),JSON.stringify({
    status:'archival V0 display derivatives, not design revisions',rows
  },null,2)+'\n');
  process.stdout.write(outputDir+'\n');
}
main().catch(error=>{console.error(error);process.exitCode=1;});

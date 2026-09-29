// Render existing audited SVG response plots for print; no values are changed.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');

const repository = path.resolve(__dirname, '..');
const sourceDir = path.join(repository, 'figures', 'source_svg');
const outputDir = process.env.JOA_OUTPUT_DIR || path.join(repository, 'figures', 'generated', 'responses');
const names = ['wright_response_v1', 'fixed_control_response_v1'];
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

async function main() {
  fs.mkdirSync(outputDir, {recursive:true});
  const rows = [];
  for (const name of names) {
    const source = path.join(sourceDir, `${name}.svg`);
    const bytes = fs.readFileSync(source);
    if (!bytes.toString('utf8').includes('<svg ')) throw new Error(`Invalid SVG ${name}`);
    const png = path.join(outputDir, `${name}.png`);
    const rendered = await sharp(bytes).resize({width:4800}).png().toFile(png);
    fs.copyFileSync(source, path.join(outputDir, `${name}.svg`));
    rows.push({name, source_svg_sha256:digest(bytes), png_sha256:digest(fs.readFileSync(png)),
               pixels:[rendered.width,rendered.height], status:'unaltered SVG content; print-size raster'});
  }
  fs.writeFileSync(path.join(outputDir,'MANIFEST.json'),
                   JSON.stringify({status:'supplementary display derivatives; not new calculations',rows},null,2)+'\n');
  process.stdout.write(outputDir+'\n');
}
main().catch(error=>{console.error(error);process.exitCode=1;});

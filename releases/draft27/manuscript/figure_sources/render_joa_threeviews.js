// Journal-display derivatives of frozen V2/Wright SVGs: typography only.
// No coordinate, geometry, mass, or model-version changes are made.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');

const root = path.resolve(__dirname, '..');
const publicSources = path.join(root, 'output', 'stage_threeviews');
const sourceRoot = fs.existsSync(publicSources) ? publicSources : path.join(__dirname, 'source_threeviews');
const targetRoot = process.env.JOA_OUTPUT_DIR || path.join(root, 'figures', 'generated', 'threeviews');
const plates = [
  ['V2', 'gpt-6-astra', 'astra_v2_threeview'],
  ['V2', 'claude-fable-5-1', 'fable_v2_threeview'],
  ['V2', 'claude-opus-5-5', 'opus_v2_threeview'],
  ['Wright', 'wright-flyer-1903', 'wright_threeview_reconstruction'],
];
const sha = blob => crypto.createHash('sha256').update(blob).digest('hex');

async function main() {
  fs.mkdirSync(targetRoot, { recursive: true });
  const records = [];
  for (const [stage, basename, name] of plates) {
    const source = path.join(sourceRoot, stage, basename + '.svg');
    const original = fs.readFileSync(source);
    const rendered = original.toString('utf8')
      .replaceAll('font-size:17px', 'font-size:23px')
      .replaceAll('font-size:19px', 'font-size:23px')
      .replaceAll('font-size:23px">PLAN', 'font-size:27px">PLAN')
      .replaceAll('font-size:23px">SIDE', 'font-size:27px">SIDE')
      .replaceAll('font-size:23px">FRONT', 'font-size:27px">FRONT');
    const svg = path.join(targetRoot, name + '.svg');
    const png = path.join(targetRoot, name + '.png');
    fs.writeFileSync(svg, rendered);
    const displayWidth = stage === 'Wright' ? 6000 : 5400;
    const expectedHeight = stage === 'Wright' ? 2600 : 2340;
    const meta = await sharp(Buffer.from(rendered)).resize({width: displayWidth}).png().toFile(png);
    if (meta.width !== displayWidth || meta.height !== expectedHeight) throw new Error(name + ': dimensions');
    records.push({name, stage, source: path.relative(root, source).replaceAll('\\', '/'),
      source_sha256: sha(original), svg_sha256: sha(fs.readFileSync(svg)),
      png_sha256: sha(fs.readFileSync(png)), width_px: meta.width,
      height_px: meta.height,
      caveat: 'V2/reconstruction typography only; not a later V12/V13 installed design'});
  }
  fs.writeFileSync(path.join(targetRoot, 'manifest.json'),
    JSON.stringify({scope: 'Journal display derivatives; geometry unchanged', records}, null, 2) + '\n');
  process.stdout.write('Rendered V2 plates at 5400 px and Wright supplement at 6000 px\n');
}
main().catch(error => {process.stderr.write(String(error) + '\n'); process.exitCode = 1;});

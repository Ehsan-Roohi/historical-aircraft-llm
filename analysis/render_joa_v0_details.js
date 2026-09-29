// Print-size detail views of immutable model-authored V0 SVG plates.
// These are viewport crops, not revised geometry or substituted model output.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');

const repository = path.resolve(__dirname, '..');
const publicSources = path.join(repository, 'figures', 'source_svg');
const sourceDir = fs.existsSync(publicSources) ? publicSources : __dirname;
const outputDir = process.env.JOA_OUTPUT_DIR || path.join(repository, 'figures', 'generated', 'v0_details');
const specs = [
  {name: 'astra_oblique_v0', box: [160, 70, 900, 620], badges: [
    [1, 405, 173], [2, 773, 215], [3, 415, 252], [4, 340, 329],
    [5, 508, 338], [6, 595, 349], [7, 696, 425], [8, 620, 493]]},
  {name: 'fable_oblique_v0', box: [140, 100, 1000, 680], badges: [
    [1, 771, 215], [2, 730, 450], [3, 300, 464], [4, 472, 357],
    [5, 553, 466], [6, 754, 429], [7, 1012, 592], [8, 677, 633]]},
  {name: 'opus_oblique_v0', box: [150, 100, 1000, 600], badges: [
    [1, 745, 236], [2, 635, 486], [3, 732, 321], [4, 620, 430],
    [5, 520, 297], [6, 338, 335], [7, 540, 385], [8, 670, 565]]},
];
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

async function main() {
  fs.mkdirSync(outputDir, {recursive: true});
  const rows = [];
  for (const {name, box, badges} of specs) {
    const original = fs.readFileSync(path.join(sourceDir, `${name}.svg`));
    const source = original.toString('utf8');
    const [x, y, width, height] = box;
    const root = source.match(/^<svg[^>]+>/)?.[0];
    if (!root || !root.includes('viewBox="0 0 1200 900"') ||
        !root.includes('width="1200"') || !root.includes('height="900"')) {
      throw new Error(`Unexpected source viewport: ${name}`);
    }
    const croppedRoot = root.replace('viewBox="0 0 1200 900"', `viewBox="${x} ${y} ${width} ${height}"`)
                            .replace('width="1200"', `width="${width}"`)
                            .replace('height="900"', `height="${height}"`);
    const withoutLabels = source.replace(/<text\b[\s\S]*?<\/text>/g, '');
    if (withoutLabels === source) throw new Error(`No archival text removed: ${name}`);
    const numbered = badges.map(([number, cx, cy]) =>
      `<g aria-label="component ${number}"><circle cx="${cx}" cy="${cy}" r="15" fill="white" stroke="#152b38" stroke-width="2.1"/><text x="${cx}" y="${cy + 6}" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="bold" fill="#152b38">${number}</text></g>`
    ).join('');
    const detail = withoutLabels.replace(root, croppedRoot).replace('</svg>', numbered + '</svg>');
    const svgFile = path.join(outputDir, `${name}_detail.svg`);
    const pngFile = path.join(outputDir, `${name}_detail.png`);
    fs.writeFileSync(svgFile, detail);
    const rendered = await sharp(Buffer.from(detail)).resize({width: 6000}).png().toFile(pngFile);
    if (rendered.width !== 6000 || rendered.height !== Math.round(6000 * height / width)) {
      throw new Error(`Unexpected output size: ${name}`);
    }
    rows.push({name, original_svg_sha256: digest(original), detail_svg_sha256: digest(Buffer.from(detail)),
               detail_png_sha256: digest(fs.readFileSync(pngFile)), source_viewbox: [0, 0, 1200, 900],
               detail_viewbox: box, numbered_components: badges.map(row => row[0]),
               pixels: [rendered.width, rendered.height],
               interpretation: 'Researcher display crop with source prose hidden and numbered overlay; no component relocation or new design data'});
  }
  fs.writeFileSync(path.join(outputDir, 'MANIFEST.json'), JSON.stringify({
    status: 'researcher-created display crops of immutable V0 model figures', rows
  }, null, 2) + '\n');
  process.stdout.write(outputDir + '\n');
}

main().catch(error => {console.error(error); process.exitCode = 1;});

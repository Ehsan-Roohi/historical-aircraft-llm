// Scalable evaluator schematic; no aircraft-specific geometry or measured load.
// The SVG is the source, and the high-resolution PNG is the pdfLaTeX display asset.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');

const repository = path.resolve(__dirname, '..');
const out = process.env.JOA_OUTPUT_DIR || path.join(repository, 'figures', 'generated', 'balance');
const publicComparison = path.join(repository, 'figures', 'source_svg', 'configuration_comparison_v3.svg');
const comparisonSource = fs.existsSync(publicComparison)
  ? publicComparison : path.join(__dirname, 'archived_configuration_comparison_v3.svg');
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">
<defs>
  <marker id="blueArrow" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M1 1 L10 6 L1 11Z" fill="#12698b"/></marker>
  <marker id="darkArrow" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M1 1 L10 6 L1 11Z" fill="#263d4b"/></marker>
  <marker id="redArrow" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M1 1 L10 6 L1 11Z" fill="#b93839"/></marker>
</defs>
<rect width="1200" height="560" fill="white"/>
<style>
 text {font-family:Arial,Helvetica,sans-serif;fill:#203747;font-size:24px}
 .panel {font-size:28px;font-weight:700}
 .airframe {fill:#e5eef1;stroke:#44616e;stroke-width:4;stroke-linejoin:round}
 .wing {fill:#d8eaf2;stroke:#44616e;stroke-width:4}
 .blue {stroke:#12698b;stroke-width:5;fill:none;marker-end:url(#blueArrow)}
 .dark {stroke:#263d4b;stroke-width:5;fill:none;marker-end:url(#darkArrow)}
 .red {stroke:#b93839;stroke-width:5;stroke-dasharray:13 8;fill:none;marker-end:url(#redArrow)}
 .redtext {fill:#a62f32;font-weight:700}
</style>
<text class="panel" x="42" y="55">a  Applied loads</text>
<text class="panel" x="642" y="55">b  Residuals about the same CG</text>
<line x1="600" y1="82" x2="600" y2="494" stroke="#c1cfd4" stroke-width="2"/>
<path class="airframe" d="M77 297 L115 277 L491 277 L542 297 L491 317 L115 317Z"/>
<path class="wing" d="M217 275 L229 228 L371 228 L383 275Z"/>
<path class="wing" d="M450 276 L460 255 L513 255 L524 276Z"/>
<circle cx="300" cy="297" r="9" fill="#263d4b"/>
<text x="313" y="323">CG</text>
<path class="blue" d="M300 226 L300 133"/><text x="258" y="147">L₁</text>
<path class="blue" d="M485 252 L485 172"/><text x="498" y="192">L₂</text>
<path class="blue" d="M101 352 L193 352"/><text x="104" y="388">T</text>
<path class="blue" d="M519 352 L427 352"/><text x="483" y="388">D</text>
<path class="dark" d="M300 305 L300 411"/><text x="312" y="405">W</text>
<path class="dark" d="M82 455 L164 455"/><path class="dark" d="M82 455 L82 388"/>
<text x="176" y="462">forward</text><text x="45" y="380">up</text>
<path class="airframe" d="M674 297 L712 277 L1088 277 L1139 297 L1088 317 L712 317Z"/>
<path class="wing" d="M814 275 L826 228 L968 228 L980 275Z"/>
<path class="wing" d="M1047 276 L1057 255 L1110 255 L1121 276Z"/>
<circle cx="897" cy="297" r="9" fill="#263d4b"/>
<text x="907" y="323">CG</text>
<path class="red" d="M897 297 L1048 297"/><text class="redtext" x="1000" y="277">R_x</text>
<path class="red" d="M897 296 L897 155"/><text class="redtext" x="911" y="168">R_z</text>
<path class="red" d="M954 229 A80 80 0 1 1 831 338"/><text class="redtext" x="814" y="404">R_m</text>
<text x="644" y="463" font-size="22">Dashed arrows: residuals, not extra loads.</text>
</svg>`;

async function main() {
  fs.mkdirSync(out, {recursive: true});
  const source = path.join(out, 'force_moment_balance.svg');
  const display = path.join(out, 'force_moment_balance.png');
  fs.writeFileSync(source, svg, 'utf8');
  const render = await sharp(Buffer.from(svg)).resize({width: 4800}).png().toFile(display);
  if (render.width !== 4800 || render.height !== 2240) throw new Error('Unexpected raster dimensions');
  const digest = crypto.createHash('sha256').update(svg).digest('hex');
  const originalComparison = fs.readFileSync(comparisonSource);
  const comparison = originalComparison.toString('utf8')
    .replaceAll('font-size="22"', 'font-size="32"')
    .replaceAll('font-size="25"', 'font-size="34"')
    .replaceAll('font-size="27"', 'font-size="30"')
    .replaceAll('Two decks overlap in plan', 'Two decks overlap')
    .replaceAll('Both surfaces carry lift', 'Both planes lift');
  const comparisonSvg = path.join(out, 'configuration_comparison_v3.svg');
  const comparisonPng = path.join(out, 'configuration_comparison_v3.png');
  fs.writeFileSync(comparisonSvg, comparison, 'utf8');
  const comparisonRender = await sharp(Buffer.from(comparison)).resize({width:6000}).png().toFile(comparisonPng);
  if (comparisonRender.width !== 6000 || comparisonRender.height !== 3950) throw new Error('Unexpected comparison dimensions');
  fs.writeFileSync(path.join(out, 'MANIFEST.json'), JSON.stringify({
    force_balance:{source_svg_sha256:digest,png_pixels:[render.width,render.height],status:'evaluator schematic, not measured aircraft'},
    comparison:{original_svg_sha256:crypto.createHash('sha256').update(originalComparison).digest('hex'),display_svg_sha256:crypto.createHash('sha256').update(comparison).digest('hex'),png_pixels:[comparisonRender.width,comparisonRender.height],status:'typography-only display derivative of frozen V1 lifting-surface plan'}
  }, null, 2) + '\n');
  process.stdout.write(display + '\n' + comparisonPng + '\n');
}
main().catch(err => {console.error(err); process.exitCode = 1;});

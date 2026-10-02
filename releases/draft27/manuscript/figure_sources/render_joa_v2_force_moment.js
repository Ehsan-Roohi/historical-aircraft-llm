// Print-sized V2 force/moment comparison. Arrows are schematic, not measured
// centres of pressure; numerical strings reproduce the frozen V2 plate.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');

const repository = path.resolve(__dirname, '..');
const out = process.env.JOA_OUTPUT_DIR || path.join(repository, 'figures', 'generated', 'v2forces');
const publicSources = path.join(repository, 'figures', 'source_svg');
const legacy = fs.existsSync(publicSources)
  ? path.join(publicSources, 'draw_v2_force_moment.py')
  : path.join(__dirname, 'archived_draw_v2_force_moment.py');
const compact = fs.existsSync(publicSources)
  ? path.join(publicSources, 'v2_compact_report.json')
  : path.join(__dirname, 'archived_v2_compact_report.json');
const blue = '#0e7198';
const amber = '#a9650e';
const ink = '#203746';
const grey = '#667b88';

function panel(y, data) {
  const claim = data.claim;
  const col = claim ? amber : blue;
  const dash = claim ? 'stroke-dasharray="10 7"' : '';
  const label = claim ? 'MODEL CLAIM ONLY — NO INDEPENDENT RETRIM' : 'INDEPENDENT CONDITIONAL RETRIM';
  const wing2 = data.biplane ? `<line x1="230" y1="${y+142}" x2="430" y2="${y+142}" class="wing"/><line x1="245" y1="${y+142}" x2="245" y2="${y+177}" class="strut"/><line x1="415" y1="${y+142}" x2="415" y2="${y+177}" class="strut"/>` : '';
  return `<g>
    <text class="title" x="38" y="${y+41}">${data.title}</text>
    <text class="status" style="fill:${col}" x="38" y="${y+73}">${label}</text>
    <line class="wing" x1="230" y1="${y+177}" x2="430" y2="${y+177}"/>${wing2}
    <line class="airframe" x1="74" y1="${y+223}" x2="552" y2="${y+223}"/>
    <line class="tail" x1="458" y1="${y+185}" x2="550" y2="${y+185}"/>
    <circle cx="327" cy="${y+223}" r="9" fill="#fff" stroke="#bd4141" stroke-width="4"/>
    <text class="small" style="fill:#bd4141" x="337" y="${y+247}">CG</text>
    <path d="M329 ${y+173} V${y+114}" stroke="${col}" stroke-width="5" fill="none" ${dash} marker-end="url(#arrow${claim?'Amber':'Blue'})"/>
    <text class="force" style="fill:${col}" x="278" y="${y+108}">Lw</text>
    <path d="M494 ${y+193} V${y+270}" stroke="${col}" stroke-width="5" fill="none" ${dash} marker-end="url(#arrow${claim?'Amber':'Blue'})"/>
    <text class="force" style="fill:${col}" x="500" y="${y+280}">Lt</text>
    <path d="M330 ${y+236} V${y+301}" stroke="${grey}" stroke-width="4" fill="none" ${dash} marker-end="url(#arrowGrey)"/>
    <text class="force" style="fill:${grey}" x="337" y="${y+309}">W</text>
    <path d="M151 ${y+285} H${76}" stroke="${col}" stroke-width="5" fill="none" ${dash} marker-end="url(#arrow${claim?'Amber':'Blue'})"/>
    <text class="force" style="fill:${col}" x="159" y="${y+292}">T</text>
    <path d="M202 ${y+322} H${266}" stroke="${grey}" stroke-width="4" fill="none" ${dash} marker-end="url(#arrowGrey)"/>
    <text class="force" style="fill:${grey}" x="164" y="${y+329}">D</text>
    <text class="small" x="38" y="${y+359}">Nose / forward ←</text>
    <rect x="600" y="${y+102}" width="559" height="261" rx="13" fill="#f5f8f9" stroke="#c0d0d7" stroke-width="2"/>
    <text class="cardhead" x="624" y="${y+137}">Applied forces (N)</text>
    <text class="value" x="624" y="${y+173}">Wing ${data.wing}    Tail ${data.tail}    Weight ${data.weight}</text>
    <text class="value" x="624" y="${y+208}">Thrust ${data.thrust}    Drag ${data.drag}    Tz ${data.tz}</text>
    <line x1="624" y1="${y+224}" x2="1132" y2="${y+224}" stroke="#c4d1d5" stroke-width="2"/>
    <text class="cardhead" x="624" y="${y+253}">Pitch about CG (N m; nose-up +)</text>
    <text class="value" x="624" y="${y+287}">Maero ${data.aero}    MT ${data.tm}</text>
    <text class="value" x="624" y="${y+320}">${data.residual}</text>
    <text class="value" x="624" y="${y+350}">Fixed-control SM: ${data.sm}</text>
    <line x1="38" y1="${y+386}" x2="1160" y2="${y+386}" stroke="#cfdbdf" stroke-width="2"/>
  </g>`;
}

const rows = [
  {title:'Astra V2  |  tractor, main wing, aft tail', biplane:false,
   wing:'+3444',tail:'−306',weight:'3138',thrust:'246',drag:'246',tz:'−0.44',
   aero:'−36.76',tm:'+36.83',residual:'Rz −0.063 N    Rm +0.065 N m',sm:'+19.47%'},
  {title:'Opus V2  |  biplane, aft tail, pusher', biplane:true,
   wing:'+3559',tail:'−78',weight:'3530',thrust:'446',drag:'443',tz:'+49.31',
   aero:'+195.88',tm:'−195.88',residual:'Rz −0.025 N    Rm +0.0003 N m',sm:'+7.76%'},
  {title:'Fable V2  |  biplane, split tail, twin pushers', biplane:true,claim:true,
   wing:'~+3061',tail:'~−203',weight:'~2894',thrust:'~412',drag:'~411',tz:'unknown',
   aero:'~+20*',tm:'~−19',residual:'Rz not verified    Rm not verified',sm:'not available'},
];

const defs = `<defs>
<marker id="arrowBlue" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="${blue}"/></marker>
<marker id="arrowAmber" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="${amber}"/></marker>
<marker id="arrowGrey" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="${grey}"/></marker>
</defs>`;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1340" viewBox="0 0 1200 1340">
${defs}<rect width="1200" height="1340" fill="white"/>
<style>text{font-family:Arial,Helvetica,sans-serif;fill:${ink}}
.title{font-size:29px;font-weight:700}.status{font-size:20px;font-weight:700}
.small{font-size:21px}.force{font-size:23px;font-weight:700}.value{font-size:21px}
.cardhead{font-size:21px;font-weight:700}.wing{stroke:${ink};stroke-width:9}
.airframe{stroke:${ink};stroke-width:6}.tail{stroke:${ink};stroke-width:8}
.strut{stroke:${grey};stroke-width:3}</style>
${panel(0,rows[0])}${panel(410,rows[1])}${panel(820,rows[2])}
<text class="small" x="38" y="1244">*Fable's ~+20 N m is its −810 + 830 N m claim; residual and margin unverified.</text>
<text class="small" x="38" y="1276">Arrows are schematic, not pressure-centre locations. Values are V2, not V12/V13.</text>
<text class="small" x="38" y="1308">Positive lift points upward; negative tail lift points downward. “~” marks claims.</text>
</svg>`;

async function main() {
  // Fail closed if the two independently evaluated V2 rows or the archived
  // Fable-claim plate no longer agree with the displayed values.
  const inputRows = JSON.parse(fs.readFileSync(compact, 'utf8'));
  const pick = (model, mesh) => inputRows.find(row => row.model === model && row.mesh.join(',') === mesh);
  const astra = pick('gpt-6-astra', '14,72');
  const opus = pick('claude-opus-5-5', '12,50');
  if (!astra || !opus) throw new Error('Frozen V2 mesh rows absent');
  const near = (actual, expected, tolerance=0.01) => Math.abs(actual-expected) <= tolerance;
  const sum = (row, prefix) => row.components.filter(part => part.surface.startsWith(prefix)).reduce((total, part) => total + part.lift_N, 0);
  if (!(near(sum(astra,'main'),3444.33789) && near(sum(astra,'tail'),-305.77176) &&
        near(astra.balance.W_N,3138.128) && near(astra.balance.T_N,245.5188841) &&
        near(astra.balance.D_N,245.51848655) && near(astra.balance.Tvertical_N,-0.44183696) &&
        near(astra.balance.Maero_Nm,-36.7628625) && near(astra.balance.Mthrust_Nm,36.8278326) &&
        near(astra.balance.Rz_N,-0.06324196) && near(astra.balance.My_Nm,0.06497012) &&
        near(astra.slope.effective_margin_percent,19.4733955) &&
        near(sum(opus,'LW')+sum(opus,'UW'),3558.770775) &&
        near(sum(opus,'tail_inner')+sum(opus,'tail_outer'),-77.715225) &&
        near(opus.balance.W_N,3530.394) && near(opus.balance.T_N,446.0852804) &&
        near(opus.balance.D_N,443.3512191) && near(opus.balance.Tvertical_N,49.3130197) &&
        near(opus.balance.Maero_Nm,195.8800725) && near(opus.balance.Mthrust_Nm,-195.879764) &&
        near(opus.balance.Rz_N,-0.02543029) && near(opus.balance.My_Nm,0.00030851) &&
        near(opus.slope.effective_margin_percent,7.7591558))) {
    throw new Error('Frozen V2 numerical source changed');
  }
  const legacySource = fs.readFileSync(legacy,'utf8');
  for (const fragment of ['~+3061 N wings','~-203 N tail','~2894 N W',
                          '~412 N T','~411 N D','*Wing -810 + tail +830 N m, model claim']) {
    if (!legacySource.includes(fragment)) throw new Error(`Archived Fable claim missing: ${fragment}`);
  }
  fs.mkdirSync(out, {recursive:true});
  const svgPath = path.join(out, 'v2_force_moment_comparison.svg');
  const pngPath = path.join(out, 'v2_force_moment_comparison.png');
  fs.writeFileSync(svgPath, svg, 'utf8');
  const rendered = await sharp(Buffer.from(svg)).resize({width:6000}).png().toFile(pngPath);
  if (rendered.width !== 6000 || rendered.height !== 6700) throw new Error('Unexpected image size');
  const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  fs.writeFileSync(path.join(out,'MANIFEST.json'), JSON.stringify({
    status:'V2 display derivative; evaluator schematic, not final installed aircraft',
    source_svg_sha256:sha(svgPath), png_sha256:sha(pngPath),
    frozen_v2_python_source_sha256:sha(legacy),
    frozen_v2_compact_report_sha256:sha(compact),
    png_pixels:[rendered.width,rendered.height],
    minimum_body_text_px:21,
    note:'At 6.5 in placement, 21 px on a 1200-unit SVG corresponds to 8.19 pt; all labels use at least 21 px.'
  },null,2)+'\n');
  process.stdout.write(pngPath+'\n');
}
main().catch(error => {console.error(error);process.exitCode=1;});

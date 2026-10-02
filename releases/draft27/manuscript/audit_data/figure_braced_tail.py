"""Vector three-view subassembly diagram from explicit evaluator dimensions."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/results/v15_braced_tail_figure01'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':13,'axes.labelsize':12,'pdf.fonttype':42})
fig=plt.figure(figsize=(10,8.5),layout='constrained')
gs=fig.add_gridspec(3,2,height_ratios=[1,1,1.8])
ax=fig.add_subplot(gs[0,:]);blue='#246a8c';amber='#a76520'
for sign in (-1,1):
    ax.add_patch(Rectangle((sign*.55 if sign>0 else -4.575,5.4),4.025,1,facecolor='#e1edf2',edgecolor=blue,lw=1.5))
    ax.plot([sign*.55,sign*4.575],[5.65,5.65],color='#343434',lw=3)
ax.plot([-.55,.55],[5.65,5.65],color='#343434',lw=2)
ax.set(xlim=(-5,5),ylim=(6.65,5.1),xlabel='Spanwise y (m)',ylabel='Aft x (m)',title='(a) Plan: enlarged tail and spar line')
ax=fig.add_subplot(gs[1,:])
for sign in (-1,1):
    ax.add_patch(Rectangle((.55 if sign>0 else -4.575,.725),4.025,.10,facecolor='#d2d2d2',edgecolor='#343434'))
    for z in (.425,1.125):ax.plot([0,sign*4.575],[z,.775],color=blue,lw=1.5)
ax.add_patch(Rectangle((-.02,.425),.04,.70,facecolor=amber))
ax.set(xlim=(-5,5),ylim=(.25,1.30),xlabel='Spanwise y (m)',ylabel='Height z (m)',title='(b) Front: upper/lower tension-only wires and central mast')
ax=fig.add_subplot(gs[2,0])
ax.add_patch(Rectangle((5.4,1.2),1.2,.6,facecolor='#ededed',edgecolor='#666',lw=1))
ax.text(6.0,1.52,'Existing fin',ha='center',fontsize=11)
ax.plot([5.65,5.65],[.425,1.125],color=amber,lw=3,label='Mast')
ax.add_patch(Rectangle((5.59,.725),.12,.10,facecolor='#343434'))
ax.plot([5.4,6.4],[.775,.775],color=blue,lw=1)
ax.annotate('Hinge axis',xy=(5.65,.775),xytext=(6.05,.5),arrowprops={'arrowstyle':'->'},fontsize=11)
ax.set(xlim=(5.2,6.85),ylim=(.25,1.95),xlabel='Aft x (m)',ylabel='Height z (m)',title='(c) Side: nominal placement')
ax.set_aspect('equal')
ax=fig.add_subplot(gs[2,1]);ax.axis('off')
ax.text(0,.98,'RESEARCHER CONCEPT',va='top',weight='bold',fontsize=13)
ax.text(0,.80,'Tail area: 8.05 m²\nOverall span: 9.15 m\nBox envelope: 120 × 100 mm\nMast: 40 mm square; ±0.35 m\nWires: 4 mm diameter',va='top',linespacing=1.3,fontsize=12)
ax.text(0,.25,'Connections, swept clearance and\nflight loads are not verified.\nIndependent axis scales in (a) and (b).',va='top',fontsize=12,color='#803d27')
for a in fig.axes[:3]:a.grid(alpha=.15);a.spines[['top','right']].set_visible(False)
fig.savefig(OUT/'braced_tail_concept.pdf')
fig.savefig(OUT/'braced_tail_concept.svg')
fig.savefig(OUT/'braced_tail_concept.png',dpi=300)
print('Three-view tail concept saved (vector PDF/SVG and PNG).')

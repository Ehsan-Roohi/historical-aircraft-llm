"""Draw a 320-dpi evidence-labelled V2 force/moment plate.

Side silhouettes are explanatory, not coordinate drawings or reconstructed
centres of pressure. Astra/Opus loads are independent conditional retrims;
Fable numbers are the model's own unverified claims.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/figures_v2/v2_force_moment_comparison.png"
records = json.loads((ROOT / "analysis/results/v2_trim_solve01/compact_report.json").read_text(encoding="utf-8"))
by_model = {(r["model"], tuple(r["mesh"])): r for r in records}

W, H = 3600, 2460
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
INK, BLUE, AMBER, GRAY, RED = "#183041", "#1576a6", "#ae6812", "#657682", "#bd4239"
FONT = Path("C:/Windows/Fonts/arial.ttf")
BOLD = Path("C:/Windows/Fonts/arialbd.ttf")
f42 = ImageFont.truetype(str(FONT), 42)
f37 = ImageFont.truetype(str(FONT), 37)
f32 = ImageFont.truetype(str(FONT), 32)
b56 = ImageFont.truetype(str(BOLD), 56)
b43 = ImageFont.truetype(str(BOLD), 43)
b37 = ImageFont.truetype(str(BOLD), 37)


def line(xy, fill, width=8, dashed=False):
    if not dashed:
        d.line(xy, fill=fill, width=width, joint="curve")
    else:
        x0, y0, x1, y1 = xy
        for i in range(0, 18, 2):
            a, b = i/18, min(1, (i+1)/18)
            d.line((x0+(x1-x0)*a, y0+(y1-y0)*a,
                    x0+(x1-x0)*b, y0+(y1-y0)*b), fill=fill, width=width)


def arrow(xy, fill, width=9, dashed=False):
    import math
    x0, y0, x1, y1 = xy
    line(xy, fill, width, dashed)
    theta = math.atan2(y1-y0, x1-x0)
    q = 26
    d.polygon([(x1, y1), (x1-q*math.cos(theta-.55), y1-q*math.sin(theta-.55)),
               (x1-q*math.cos(theta+.55), y1-q*math.sin(theta+.55))], fill=fill)


def txt(x, y, s, font=f37, fill=INK):
    d.text((x, y), s, font=font, fill=fill)


def panel(y, title, status, claim=False):
    txt(75, y+35, title, b56)
    txt(75, y+106, status, b37, AMBER if claim else BLUE)
    d.line((75, y+735, 3525, y+735), fill="#cbd5da", width=3)
    txt(125, y+630, "Nose / forward", f32, GRAY)
    arrow((415, y+652, 270, y+652), GRAY, 5)
    # The full-aircraft three-view, not this plate, defines exact geometry.
    line((260, y+383, 1840, y+383), INK, 10)
    line((585, y+304, 1230, y+304), INK, 21)
    line((1510, y+305, 1845, y+305), INK, 15)
    if "Astra" not in title:
        line((585, y+177, 1230, y+177), INK, 19)
        line((650, y+177, 650, y+304), GRAY, 5)
        line((1175, y+177, 1175, y+304), GRAY, 5)
    prop = 295 if "Astra" in title else 1390
    line((prop, y+270, prop, y+465), AMBER, 8)
    if "Fable" in title:
        line((prop+28, y+270, prop+28, y+465), AMBER, 4, True)
    d.ellipse((925, y+340, 960, y+375), fill="white", outline=RED, width=6)
    txt(915, y+396, "CG", b37, RED)


def loads(y, wing, tail, weight, thrust, drag, claim=False, prop=295):
    force = AMBER if claim else BLUE
    arrow((1280, y+305, 1280, y+180), force, 10, claim)
    txt(95, y+205, wing, b37, force)
    arrow((1690, y+307, 1690, y+510), force, 10, claim)
    txt(1510, y+515, tail, b37, force)
    arrow((1130, y+390, 1130, y+575), GRAY, 9, claim)
    txt(1010, y+575, weight, f37, GRAY)
    if prop == 295:
        arrow((310, y+448, 170, y+448), AMBER, 9, claim)
        txt(130, y+488, thrust, f37, AMBER)
    else:
        arrow((1390, y+448, 1250, y+448), AMBER, 9, claim)
        txt(1190, y+488, thrust, f37, AMBER)
    arrow((560, y+450, 680, y+450), GRAY, 7, claim)
    txt(465, y+485, drag, f32, GRAY)


def moments(y, aero, mt, rz, rm, sm, note):
    d.rounded_rectangle((2050, y+180, 3500, y+590), radius=24,
                        fill="#f4f7f8", outline="#c5d0d5", width=3)
    txt(2100, y+200, "Pitch about CG  (nose-up +)", b43)
    txt(2100, y+270, "Aerodynamic:  " + aero, f42)
    txt(2100, y+330, "Thrust line:       " + mt, f42)
    txt(2100, y+400, "Rz: " + rz + "    Rm: " + rm, f37, RED)
    txt(2100, y+455, "Fixed-control SM: " + sm, f37)
    txt(2100, y+530, note, f32, GRAY)


txt(75, 20, "Final V2 proposals: applied loads and opposing pitch moments", b56)
txt(75, 90, "Illustrative side views; force arrows are not measured centres of pressure.", f37, GRAY)

ya, yo, yf = 150, 920, 1690
panel(ya, "Astra V2  |  tractor, main wing, aft tail", "INDEPENDENT CONDITIONAL RETRIM")
loads(ya, "+3444 N wings", "-306 N tail", "3138 N W", "246 N T", "246 N D")
moments(ya, "-36.76 N m", "+36.83 N m", "-0.063 N", "+0.065 N m", "+19.47%",
        "Vertical thrust -0.44 N; values rounded")

panel(yo, "Opus V2  |  biplane, aft tail, pusher", "INDEPENDENT CONDITIONAL RETRIM")
loads(yo, "+3559 N wings", "-78 N tail", "3530 N W", "446 N T", "443 N D", prop=1390)
moments(yo, "+195.88 N m", "-195.88 N m", "-0.025 N", "+0.0003 N m", "+7.76%",
        "Vertical thrust +49.31 N; values rounded")

panel(yf, "Fable V2  |  biplane, split tail, twin pushers", "MODEL CLAIM ONLY  |  NO INDEPENDENT RETRIM", True)
loads(yf, "~+3061 N wings", "~-203 N tail", "~2894 N W", "~412 N T", "~411 N D", True, 1390)
moments(yf, "~+20 N m*", "~-19 N m", "not verified", "not verified", "not available",
        "*Wing -810 + tail +830 N m, model claim")

OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, dpi=(320, 320), optimize=True)
print(OUT.name)

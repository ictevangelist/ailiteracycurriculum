"""IDEAL Thinkers A3 road map v2: a real road snaking across the sheet, one pass per key stage."""
import html, re, sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(_HERE, "data.py")).read())

W, H = 420, 297
PASS_Y = [77, 143, 209]           # road centre lines (mm)
L, R, RAD = 44, 376, 33           # straight section ends and turn radius
S = (R - L) / 13.5                # stop spacing
CW, CH, OFF = 45, 25, 7.2         # card width, height, gap from road centre
STEP = 22.75                      # spacing between items along the road (signs and lessons alternate sides)

def slot_x(p, k):
    """k = 0..13: year sign, six lessons, year sign, six lessons."""
    d = (L + R) / 2 - 6.5 * STEP + k * STEP - L
    return L + d if p != 1 else R - d

def clampx(cx):
    return min(max(cx, 8 + CW / 2), W - 8 - CW / 2)

# ---------- road SVG ----------
path = (f"M 10 {PASS_Y[0]} H {R} A {RAD} {RAD} 0 0 1 {R} {PASS_Y[1]} "
        f"H {L} A {RAD} {RAD} 0 0 0 {L} {PASS_Y[2]} H 404")
kerbs = []
for y in range(6):
    p, half = y // 2, y % 2
    py = PASS_Y[p]
    if p != 1:
        mid = (slot_x(p, 6) + slot_x(p, 7)) / 2
        x1 = 10 if (p == 0 and half == 0) else (L if half == 0 else mid)
        x2 = mid if half == 0 else (R if p == 0 else 404)
    else:
        mid = (slot_x(p, 6) + slot_x(p, 7)) / 2
        x1 = R if half == 0 else mid
        x2 = mid if half == 0 else L
    kerbs.append(f'<line x1="{x1}" y1="{py}" x2="{x2}" y2="{py}" stroke="#{COL[y][0]}" stroke-width="12.4" />')

chev = []
for p in range(3):
    for k in range(0, 13, 2):
        x = (slot_x(p, k) + slot_x(p, k + 1)) / 2
        d = -1 if p == 1 else 1
        chev.append(f'<path d="M {x - 1.1 * d} {PASS_Y[p] - 1.6} L {x + 1.1 * d} {PASS_Y[p]} L {x - 1.1 * d} {PASS_Y[p] + 1.6}" fill="none" stroke="#F1C40F" stroke-width=".7" stroke-linecap="round" stroke-linejoin="round"/>')
svg = f"""<svg class="road" viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm">
  <path d="{path}" fill="none" stroke="#D5DBDB" stroke-width="12.4" stroke-linecap="butt"/>
  {''.join(kerbs)}
  <path d="{path}" fill="none" stroke="#FFFFFF" stroke-width="10"/>
  <path d="{path}" fill="none" stroke="#2C3E50" stroke-width="9.2"/>
  {''.join(chev)}
  <path id="bendR" d="M {R} {PASS_Y[0]} A {RAD} {RAD} 0 0 1 {R} {PASS_Y[1]}" fill="none"/>
  <path id="bendL" d="M {L} {PASS_Y[1]} A {RAD} {RAD} 0 0 0 {L} {PASS_Y[2]}" fill="none"/>
  <use href="#bendR" stroke="#2C3E50" stroke-width="3"/>
  <use href="#bendL" stroke="#2C3E50" stroke-width="3"/>
  <text class="paint"><textPath href="#bendR" startOffset="50%" text-anchor="middle" dominant-baseline="central">LOWER KEY STAGE 2 · YEARS 3 AND 4</textPath></text>
  <text class="paint"><textPath href="#bendL" startOffset="50%" text-anchor="middle" dominant-baseline="central">UPPER KEY STAGE 2 · YEARS 5 AND 6</textPath></text>
</svg>"""

# ---------- stops, cards and year signs ----------
items = []
for y, (name, q, fill, lessons) in enumerate(YEARS):
    main, dark, tint = COL[y]
    p, half = y // 2, y % 2
    py = PASS_Y[p]
    year, theme = name.split(": ", 1)
    base = 0 if half == 0 else 7          # item index of this year's sign
    for i, (code, big, activity, letters, links) in enumerate(lessons):
        k = base + 1 + i
        x = slot_x(p, k)
        m = re.match(r"\*\*(.+?)\*\*\s*(.*)", big)
        title, idea = m.group(1), m.group(2)
        challenge = "(IDEAL Challenge" in idea
        idea = ("Two sessions. " if "two sessions" in idea else "") + re.sub(r"\(IDEAL Challenge[^)]*\)\s*", "", idea)
        above = k % 2 == 0
        cx = clampx(x)
        top = py - OFF - CH if above else py + OFF
        # connector from stop to card
        y1, y2 = (py - 3.4, top + CH) if above else (py + 3.4, top)
        items.append(f'<div class="conn" style="left:{x - .2}mm;top:{min(y1, y2)}mm;height:{abs(y2 - y1)}mm;background:#{main}"></div>')
        items.append(f'<div class="stop{" gold" if challenge else ""}" style="left:{x - 3.4}mm;top:{py - 3.4}mm;--c:#{dark}">{i + 1}</div>')
        tag = ''
        ctag = (' <span class="tag">' + ic("FaStar", "star") + ('IDEAL Challenge') + '</span>') if challenge else ''

        items.append(f"""<div class="card{' challenge' if challenge else ''}" data-spot="{code.replace(' ', '')}" style="left:{cx - CW / 2}mm;top:{top}mm;--c:#{dark};--m:#{main};--t:#{tint}">
          <div class="ctop">{ic(LESSON_ICONS[y][i], 'lic')}<div class="ctitle"><span class="code">{code}{ctag}</span>{html.escape(title)}</div></div>
          {tag}<div class="idea">{html.escape(idea)}</div>
          <div class="cfoot"><span class="chips">{chips(letters)}<span class="strands">{''.join(ic(STRAND_ICON[s], 'sic') for s in STRANDS[code])}</span></span><span class="links">{html.escape(links)}</span></div></div>""")
    # year sign sits above the first stop of the year
    x0 = slot_x(p, base)
    sabove = base % 2 == 0
    stop_top = py - OFF - CH if sabove else py + OFF
    items.append(f"""<div class="sign" data-spot="year-{y + 1}" style="left:{clampx(x0) - CW / 2}mm;top:{stop_top}mm;--c:#{dark};--m:#{main}">
      <div class="sinner"><div class="sy">{year}</div><div class="st">{html.escape(theme)}</div><div class="sq">{html.escape(q)}</div></div></div>""")
    ptop = stop_top + CH if sabove else py + 1.5
    items.append(f'<div class="pole" style="left:{x0 - .45}mm;top:{ptop}mm;height:{OFF - 1.5}mm;background:#{dark}"></div>')
    items.append(f'<div class="marker" style="left:{x0 - 2.2}mm;top:{py - 2.2}mm;background:#{main}"></div>')

# key stage badges and the start / finish
KS = [("Key Stage 1", "Years 1 and 2"), ("Lower Key Stage 2", "Years 3 and 4"), ("Upper Key Stage 2", "Years 5 and 6")]
items.append(f'<div class="ks" style="left:10mm;top:{PASS_Y[0] + 7.2}mm"><b>{KS[0][0]}</b>{KS[0][1]}</div>')
items.append(f'<div class="start" style="left:10mm;top:{PASS_Y[0] - 4.6}mm">START</div>')
items.append(f"""<div class="finish" style="left:{404 - 1}mm;top:{PASS_Y[2] - 4.6}mm"></div>
<div class="dest" style="left:{W - 9 - 46}mm;top:{PASS_Y[2] - OFF - CH}mm">{ic('FaRoute', 'dic')}<div><span class="dk">Destination</span><b>Secondary school</b>Every pupil leaves with an AI learning promise for the next stage.</div></div>
<div class="pole" style="left:{W - 9 - 23 - .45}mm;top:{PASS_Y[2] - OFF}mm;height:{OFF - 4.6}mm;background:#F1C40F"></div>""")

FOOT = ("IDEAL Thinkers © 2026 Mark Anderson · ictevangelist.com · Licensed under CC BY-NC-SA 4.0: share and adapt for "
        "non commercial use with credit, sharing adaptations under the same licence.")

ideal_head = "".join(f'<div class="itile" style="background:#{x[3]}">{ic(x[4], "tic")}<div class="ik">{x[0]}</div><div class="iw">{x[1]}</div></div>' for x in IDEAL)
loop_html = "".join(f"""<div class="lstep" style="--c:#{x[3]}">{ic(x[4], 'lsi')}<div><div class="lname">{n + 1}. {x[0]}</div><div class="ldef">{x[1]}</div></div></div>""" for n, x in enumerate(LOOP))
grow = "".join(f'<div class="irow"><span class="ibadge" style="background:#{x[3]}">{x[0]}</span><span>{MOTTO[x[0]][0]}</span><span>{MOTTO[x[0]][1]}</span><span>{MOTTO[x[0]][2]}</span></div>' for x in IDEAL)
grow += '<div class="irow lwrow"><span class="ibadge lw">Learning Well</span><span><b>Try it first</b></span><span><b>Hint, not answer</b></span><span><b>Plan, use, prove</b></span></div>'
STRAND_ROWS = [("How AI works", "machines that guess; then feeds and chatbots; then training data, bias and generated media"),
               ("Staying in charge", "people check its guesses; then sounding sure is not being right; then who answers for AI decisions"),
               ("Safe, fair and honest", "keep things private; then privacy and honesty about AI help; then consent, fairness and cost"),
               ("Learning Well", "try it first; then hint, not answer; then plan, use, prove"),
               ("Design and create", "Robot Rules; then a healthier feed and a chatbot rulebook; then a class model and AI for good")]
strand_html = "".join(f'<div class="srow">{ic(STRAND_ICON[n], "lgi")}<span><b>{n}:</b> {html.escape(t)}</span></div>' for n, t in STRAND_ROWS)
shape = "".join(f'<span class="sh">{s}</span>' for s in SHAPE)

page = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>IDEAL Thinkers Road Map</title>
<link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>

@page {{ size: 420mm 297mm; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{ --navy: #2C3E50; --muted: #566573; --cloud: #ECF0F1; }}
html, body {{ width: 420mm; height: 297mm; overflow: hidden; }}
body {{ font-family: Poppins, sans-serif; color: var(--navy); background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.sheet {{ position: relative; width: 420mm; height: 297mm; overflow: hidden;
  background: radial-gradient(circle at 12% 30%, #F4F9FB 0, transparent 38%), radial-gradient(circle at 88% 70%, #FBF6F0 0, transparent 40%); }}
svg.road {{ position: absolute; inset: 0; }}
.ic svg, .lic svg, .star svg, .dic svg, .tic svg, .lsi svg, .iic svg {{ display: block; width: 100%; height: 100%; }}

.head {{ position: absolute; left: 10mm; right: 10mm; top: 9mm; display: flex; justify-content: space-between; align-items: flex-end; }}
.kicker {{ font-family: Poppins; font-weight: 700; font-size: 8.4pt; letter-spacing: .16em; color: #A04000; text-transform: uppercase; }}
h1 {{ font-family: "Exo 2"; font-weight: 800; font-size: 38pt; line-height: .95; margin-top: 1.4mm; letter-spacing: -.01em; }}
h1 span {{ color: #1F618D; }}
.sub {{ font-size: 11pt; font-weight: 500; color: var(--muted); margin-top: 1.6mm; }}
.sub b {{ color: var(--navy); font-weight: 600; }}
.ideal .lab {{ font-family: Poppins; font-size: 7.6pt; font-weight: 700; letter-spacing: .12em; color: var(--muted); text-transform: uppercase; margin-bottom: 1.4mm; text-align: right; }}
.itiles {{ display: flex; gap: 1.6mm; }}
.itile {{ width: 18mm; height: 15mm; border-radius: 2.4mm; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }}
.tic {{ position: absolute; top: 1.4mm; right: 1.6mm; width: 3.2mm; height: 3.2mm; opacity: .8; }}
.ik {{ font-family: "Exo 2"; font-weight: 800; font-size: 18pt; line-height: 1; }}
.iw {{ font-family: Poppins; font-weight: 600; font-size: 7pt; margin-top: .6mm; }}

.stop {{ position: absolute; width: 6.8mm; height: 6.8mm; border-radius: 50%; background: #fff; border: .7mm solid var(--c); color: var(--c);
  font-family: "Exo 2"; font-weight: 800; font-size: 9.5pt; display: flex; align-items: center; justify-content: center; z-index: 3; }}
.stop.gold {{ background: #F1C40F; border-color: #fff; color: var(--navy); box-shadow: 0 0 0 .5mm var(--c); }}
.conn {{ position: absolute; width: .4mm; z-index: 1; }}
.pole {{ position: absolute; width: .9mm; z-index: 1; }}

.card {{ position: absolute; width: {CW}mm; height: {CH}mm; background: #fff; border-radius: 2mm; padding: 1.2mm 1.8mm 1mm;
  display: flex; flex-direction: column; z-index: 2; border: .3mm solid rgba(44,62,80,.14); border-top: 1.1mm solid var(--m);
  box-shadow: 0 .6mm 1.6mm rgba(44,62,80,.12); overflow: hidden; }}
.ctop {{ display: flex; align-items: flex-start; gap: 1.3mm; }}
.lic {{ flex: none; width: 4mm; height: 4mm; color: var(--c); margin-top: .3mm; }}
.ctitle {{ font-family: "Exo 2"; font-weight: 700; font-size: 8.3pt; line-height: 1.06; color: var(--c); flex: 1; }}
.strands {{ display: flex; gap: .5mm; align-items: center; margin-left: .9mm; padding-left: .9mm; border-left: .25mm solid #D5DBDB; }}
.sic {{ width: 2.3mm; height: 2.3mm; color: var(--navy); opacity: .75; }}
.challenge .sic {{ color: #fff; opacity: .9; }}
.sic svg, .lgi svg {{ display: block; width: 100%; height: 100%; }}
.code {{ font-family: Poppins; font-weight: 700; font-size: 6.5pt; letter-spacing: .04em; color: var(--muted); display: block; margin-bottom: .2mm; }}
.idea {{ font-size: 6.9pt; line-height: 1.13; margin-top: .4mm; flex: 1; }}
.cfoot {{ display: flex; justify-content: space-between; align-items: center; margin-top: .5mm; }}
.chips {{ display: flex; gap: .6mm; align-items: center; }}
.chip {{ width: 3.5mm; height: 3.5mm; border-radius: .7mm; color: #fff; font-family: "Exo 2"; font-weight: 800; font-size: 6.4pt; display: flex; align-items: center; justify-content: center; }}
.all {{ font-family: Poppins; font-weight: 700; font-size: 6.5pt; color: #fff; background: var(--navy); border-radius: .8mm; padding: .3mm 1mm; white-space: nowrap; }}
.links {{ font-family: Poppins; font-weight: 600; font-size: 6.5pt; color: var(--muted); text-align: right; white-space: nowrap; }}
.challenge {{ background: var(--c); border-color: var(--c); border-top-color: #F1C40F; }}
.challenge .ctitle, .challenge .idea, .challenge .lic, .challenge .links, .challenge .code {{ color: #fff; }}
.challenge .idea {{ font-size: 6.6pt; line-height: 1.1; }}
.challenge .all {{ background: #F1C40F; color: var(--navy); }}
.tag {{ display: inline-flex; align-items: center; gap: .5mm; margin-left: .8mm; font-family: Poppins; font-weight: 700; font-size: 6.5pt; letter-spacing: .06em; text-transform: uppercase; color: #F9E79F; }}
.star {{ width: 2.4mm; height: 2.4mm; color: #F1C40F; }}

.sign {{ position: absolute; width: {CW}mm; height: {CH}mm; background: var(--c); border-radius: 2.2mm; padding: .9mm; z-index: 2; box-shadow: 0 .6mm 1.6mm rgba(44,62,80,.2); }}
.sinner {{ width: 100%; height: 100%; border: .45mm solid rgba(255,255,255,.85); border-radius: 1.5mm; padding: 1.3mm 2mm; color: #fff; display: flex; flex-direction: column; justify-content: center; }}
.sy {{ font-family: Poppins; font-weight: 800; font-size: 6.6pt; letter-spacing: .2em; text-transform: uppercase; color: #F9E79F; }}
.st {{ font-family: "Exo 2"; font-weight: 800; font-size: 11pt; line-height: 1.02; margin-top: .4mm; }}
.sq {{ font-size: 8pt; line-height: 1.18; margin-top: .6mm; }}

.ks {{ position: absolute; font-family: Poppins; font-size: 6.6pt; color: var(--muted); line-height: 1.25; width: 30mm; }}
.ks b {{ display: block; font-family: "Exo 2"; font-weight: 800; font-size: 8.4pt; color: var(--navy); letter-spacing: .02em; }}
.ks.inside {{ width: 23mm; }}
.marker {{ position: absolute; width: 4.4mm; height: 4.4mm; border-radius: .8mm; transform: rotate(45deg); border: .5mm solid #fff; z-index: 3; }}
.start {{ position: absolute; height: 9.2mm; display: flex; align-items: center; padding: 0 1.6mm; font-family: Poppins; font-weight: 800; font-size: 6.6pt; letter-spacing: .2em; color: #fff; background: #1E8449; border-radius: 1mm 0 0 1mm; z-index: 3; }}
.finish {{ position: absolute; width: 6mm; height: 9.2mm; z-index: 3; background-color: #fff;
  background-image: conic-gradient(#2C3E50 25%, #fff 0 50%, #2C3E50 0 75%, #fff 0); background-size: 3mm 3.06mm; border: .3mm solid #2C3E50; }}
text.paint {{ font-family: Poppins; font-weight: 800; font-size: 2.3px; letter-spacing: .32px; fill: #fff; stroke: #2C3E50; stroke-width: 1.1px; paint-order: stroke; }}
.dest {{ position: absolute; width: 46mm; height: 25mm; display: flex; gap: 2mm; align-items: center; background: #FEF9E7; border: .4mm solid #F1C40F; border-radius: 2mm; padding: 1.6mm 2mm; font-size: 6.8pt; line-height: 1.28; z-index: 2; }}
.dest b {{ display: block; font-family: "Exo 2"; font-weight: 800; font-size: 9pt; color: var(--navy); }}
.dk {{ display: block; font-family: Poppins; font-weight: 800; font-size: 6.5pt; letter-spacing: .16em; text-transform: uppercase; color: #A04000; }}
.dic {{ flex: none; width: 7mm; height: 7mm; color: #A04000; margin-top: .3mm; }}

.bottom {{ position: absolute; left: 10mm; right: 10mm; top: 242.2mm; height: 37.3mm; display: grid; grid-template-columns: 1.2fr 1.35fr .95fr; gap: 3mm; }}
.srow {{ display: flex; gap: 1.6mm; align-items: center; font-size: 6.6pt; line-height: 1.12; padding: .3mm 0; border-bottom: .25mm solid #D5DBDB; }}
.srow:last-child {{ border-bottom: 0; }}
.srow b {{ font-weight: 600; }}
.lgi {{ flex: none; width: 3.4mm; height: 3.4mm; color: var(--navy); }}
.stair {{ font-size: 6.6pt; line-height: 1.2; margin-top: .8mm; }}
.stair b {{ font-weight: 600; }}
.routine {{ position: absolute; left: 10mm; right: 10mm; top: 282.4mm; display: flex; justify-content: space-between; gap: 4mm; font-size: 6.6pt; color: var(--navy); }}
.routine b {{ font-weight: 600; }}
.routine .k {{ color: var(--muted); text-align: right; }}
.panel {{ background: var(--cloud); border-radius: 2.4mm; padding: 1.6mm 2.6mm; overflow: hidden; }}
.ph {{ font-family: "Exo 2"; font-weight: 800; font-size: 10.5pt; margin-bottom: .8mm; display: flex; align-items: baseline; gap: 2mm; }}
.ph span {{ font-family: Poppins; font-weight: 500; font-size: 6.8pt; color: var(--muted); }}
.loop {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.1mm; }}
.lstep {{ background: var(--c); color: #fff; border-radius: 1.6mm; padding: .9mm 1.6mm; display: flex; gap: 1.6mm; align-items: center; }}
.lsi {{ flex: none; width: 4.4mm; height: 4.4mm; }}
.lname {{ font-family: "Exo 2"; font-weight: 800; font-size: 8.4pt; line-height: 1; }}
.ldef {{ font-size: 6.6pt; line-height: 1.15; margin-top: .3mm; }}
.irow {{ display: grid; grid-template-columns: 12mm 1fr 1.15fr 1.35fr; gap: 1.6mm; align-items: center; font-size: 6.6pt; line-height: 1.05; padding: .1mm 0; border-bottom: .25mm solid #D5DBDB; }}
.irow:last-child {{ border-bottom: 0; }}
.irow.h {{ font-family: Poppins; font-weight: 700; font-size: 6.5pt; color: var(--muted); letter-spacing: .06em; text-transform: uppercase; padding-top: 0; }}
.irow b {{ font-weight: 600; color: #922B21; }}
.ibadge {{ color: #fff; border-radius: .8mm; font-family: "Exo 2"; font-weight: 800; font-size: 7pt; display: flex; align-items: center; justify-content: center; height: 3.6mm; }}
.ibadge.lw {{ background: #922B21; font-family: Poppins; font-weight: 600; font-size: 6pt; line-height: 1; text-align: center; height: auto; padding: .4mm .2mm; }}
.iic {{ width: 2.6mm; height: 2.6mm; }}
.shape {{ display: flex; flex-wrap: wrap; gap: .8mm; }}
.sh {{ background: #fff; border: .3mm solid #BDC3C7; border-radius: 1mm; padding: .3mm 1.2mm; font-size: 6.2pt; font-weight: 600; }}
.note {{ font-size: 6.2pt; line-height: 1.3; margin-top: 1.4mm; }}
.note b {{ font-weight: 600; }}
.key {{ margin-top: 1mm; font-family: Poppins; font-size: 5.8pt; color: var(--muted); line-height: 1.3; }}
.key b {{ color: var(--navy); }}
.foot {{ position: absolute; left: 10mm; right: 10mm; bottom: 4mm; font-family: Poppins; font-size: 6.5pt; color: var(--muted); display: flex; justify-content: space-between; }}
.foot b {{ color: var(--navy); }}
</style></head><body><div class="sheet">
{svg}
<div class="head">
  <div>
    <div class="kicker">The AI Literacy strand of the Primary Digital Cognition Curriculum</div>
    <h1>IDEAL <span>Thinkers</span></h1>
    <div class="sub"><b>Curriculum road map:</b> 36 lessons across Years 1 to 6 · Pedagogy first, technology second</div>
  </div>
  <div class="ideal" data-spot="IDEAL"><div class="lab">The IDEAL habits: how we use AI well</div><div class="itiles">{ideal_head}</div></div>
</div>
{''.join(items)}
<div class="bottom">
  <div class="panel" data-spot="What pupils learn"><div class="ph">What pupils learn <span>Five progression strands, KS1 to Upper KS2</span></div>{strand_html}</div>
  <div class="panel" data-spot="The habits grow with the children"><div class="ph">The habits they build <span>IDEAL, with Learning Well as how the L is taught</span></div>
    <div class="irow h"><span></span><span>Years 1 and 2</span><span>Years 3 and 4</span><span>Years 5 and 6</span></div>{grow}</div>
  <div class="panel" data-spot="Tools for teaching it"><div class="ph">Tools for teaching it <span>A simple model of AI that learns from examples</span></div><div class="loop">{loop_html}</div>
    <div class="stair"><b>STAIR</b> (Years 5 and 6): Specific, Tell, Actionable, Iterate, Role.</div></div>
</div>
<div class="routine"><span data-spot="Every lesson"><b>Every lesson, for teachers:</b> Remember When · Link It · Learn It · Try It · Own It · IDEAL Check · Exit Ticket. Retrieve first, reteach if needed. Unplugged first, no pupil accounts.</span><span class="k">Gold stop: IDEAL Challenge · Diamond: start of a year · DC Digital Citizenship · DL Digital Literacy · CS Computer Science</span></div>
<div class="foot"><span>{FOOT}</span><span><b>Mark Anderson FCCT</b> · ICT Evangelist</span></div>
</div></body></html>"""
open(os.path.join(os.environ.get("OUT_DIR", _HERE), "road.html"), "w").write(page)
print("ok")

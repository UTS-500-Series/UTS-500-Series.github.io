"""Equaliser module - page content.

Written from the Equaliser repository at commit e2f6864 (1 Oct 2026; the design files last
changed in c804e9e, 30 Sep): https://github.com/UTS-500-Series/Equaliser

The two parametric bands are drawn with values on Combined_EQ/Combined_EQ.kicad_sch. That
sheet's image and viewer data come from _kicad_sch.py, and every response figure on these
pages comes from _eq_response.py, which solves the same netlist (ideal op amps, linear pots)
and is checked against the team's own LTspice run. The high-pass, low-pass and gain sections
are still on sheets of their own; their images come from _kicad_sch.py too (SHEETS below).
Rerun both scripts when the repository changes:

    python3 build/_kicad_sch.py --module equaliser
    python3 build/_eq_response.py
"""
import json, math, os
import shell
from shell import fig, pic, table

SRC = 'https://github.com/UTS-500-Series/Equaliser'
COMMIT = 'e2f6864'
SCH = 'Combined_EQ/Combined_EQ.kicad_sch'      # read by _kicad_sch.py, relative to the repository
SHEETS = {'hpf': 'High_Pass_filter/HPF/HPF.kicad_sch',
          'lpf': 'Low_Pass_Filter/LPF/LPF.kicad_sch',
          'gain': 'Variable_Gain/GAIN/variablegain/variablegain.kicad_sch'}

POWER = {'+16V', '-16V', '+48V', 'VCC', 'VEE'}
GROUND = {'AGND', 'CHASSIS', 'B+/C+/F+/G+/GND'}


def net_class(n):
    if n in GROUND: return 'gnd'
    if n in POWER: return 'pwr'
    if n.startswith('Net-(R') or n in ('GAIN_ADJ', 'SC_LINK'): return 'ctl'
    return 'sig'


# One line per part for the viewer's detail panel. IC3 and its parts are the low-mid band,
# IC2 and its parts the high-mid band; the two are wired identically.
_BAND = {
    'low': dict(ic='IC3', sum='A', i1='B', i2='C', out='D', fin='R29', fb='R39', mix='RV8',
                feed='R30', damp='R31', sfb='R32', loop='R35', q='RV7', qg='R27', qs='R28',
                f='RV9', ri1='R36', ri2='R38', rb1='R34', rb2='R37', c1='C8', c2='C9',
                cc='C7', rd='R33', cap='12.7&nbsp;nF', name='low-mid'),
    'high': dict(ic='IC2', sum='E', i1='F', i2='G', out='H', fin='R16', fb='R22', mix='RV5',
                 feed='R17', damp='R18', sfb='R19', loop='R23', q='RV2', qg='R14', qs='R15',
                 f='RV6', ri1='R24', ri2='R26', rb1='R21', rb2='R25', c1='C3', c2='C6',
                 cc='C2', rd='R20', cap='2.3&nbsp;nF', name='high-mid'),
}
NOTES = {'J1': '500-series 15-pin card edge (EDAC 306). Only +16 V, -16 V, ground and +48 V '
               'reach it so far, and the op amps are not yet on those rails.'}
for b in _BAND.values():
    n = b['name']
    NOTES.update({
        b['ic']: 'OPA1644 quad op amp: the whole %s band. Unit %s sums, %s and %s integrate, '
                 '%s mixes the band back into the signal.' % (n, b['sum'], b['i1'], b['i2'], b['out']),
        b['fin']: 'Band input into the output stage\'s inverting input. With %s, gain of -1 for '
                  'the dry signal.' % b['fb'],
        b['fb']: 'Output-stage feedback. Sets the dry gain to -1 with %s.' % b['fin'],
        b['mix']: 'Boost/cut. Pin 1 is the band input, pin 3 the band output; the wiper feeds '
                  'the filter. Pin 1 end is full boost, centre is flat.',
        b['feed']: 'From the boost/cut wiper into the summer\'s + input: the filter\'s input.',
        b['damp']: 'Band-pass output back into the summer\'s + input. Sets the damping.',
        b['sfb']: 'Summer feedback.',
        b['loop']: 'Low-pass output back to the summer\'s - input: closes the state-variable loop.',
        b['q']: 'Width (Q). Its wiper goes to ground through %s; pin 1 end is narrowest.' % b['qg'],
        b['qg']: 'From the width pot\'s wiper to ground.',
        b['qs']: 'From the width pot to the summer\'s - input.',
        b['f']: 'Frequency, dual gang: one gang per integrator, so both move together. Pin 1 '
                'end is the top of the range.',
        b['ri1']: 'Integrator input resistor, first integrator. Sets the top frequency with %s.' % b['c1'],
        b['ri2']: 'Integrator input resistor, second integrator.',
        b['rb1']: 'Bottom of the first frequency gang to ground. Sets the bottom of the range.',
        b['rb2']: 'Bottom of the second frequency gang to ground.',
        b['c1']: '%s integrator capacitor. This value is what places the band.' % b['cap'],
        b['c2']: '%s integrator capacitor, matching %s.' % (b['cap'], b['c1']),
        b['cc']: '10 uF, couples the band-pass output into the output stage\'s + input.',
        b['rd']: '100k, holds the output stage\'s + input at ground for DC.',
    })


def resp():
    return json.load(open(os.path.join(shell.DATA_DIR, 'response.json')))


def response_chart():
    """Both bands at full boost and full cut, with the frequency knob at the bottom, middle and
    top of its travel, and the team's LTspice run on top. Drawn inline so it follows the
    site's theme."""
    d = resp()
    W, H, L, R, T, B = 680, 340, 48, 16, 16, 36
    fmin, fmax, dbmin, dbmax = 10, 100000, -12, 12
    X = lambda f: L + (math.log10(f) - 1) / (math.log10(fmax) - 1) * (W - L - R)
    Y = lambda db: T + (dbmax - db) / (dbmax - dbmin) * (H - T - B)
    grid, lab = [], []
    for f in (10, 100, 1000, 10000, 100000):
        grid.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d"/>' % (X(f), T, X(f), H - B))
        lab.append('<text x="%.1f" y="%d" text-anchor="middle">%s</text>'
                   % (X(f), H - B + 18, {10: '10', 100: '100', 1000: '1k', 10000: '10k', 100000: '100k'}[f]))
    for db in range(dbmin, dbmax + 1, 6):
        grid.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (L, Y(db), W - R, Y(db)))
        lab.append('<text x="%d" y="%.1f" text-anchor="end" dominant-baseline="middle">%s</text>'
                   % (L - 6, Y(db), '%+d' % db if db else '0 dB'))
    paths = []
    for c in d['curves']:
        col = 'var(--sig)' if c['band'] == 'low' else 'var(--ctl)'
        dash = ' stroke-dasharray="5 4"' if c['gain'] == 'cut' else ''
        p = 'M' + ' L'.join('%.1f %.1f' % (X(f), Y(db)) for f, db in c['points'])
        paths.append(f'<path d="{p}" fill="none" stroke="{col}" stroke-width="2"{dash} stroke-linejoin="round"/>')
    dots = ''.join('<circle cx="%.1f" cy="%.1f" r="2.2"/>' % (X(f), Y(db))
                   for f, db in d['ltspice']['points'][::8])
    key = lambda y, col, t, dash='': (
        f'<line x1="{L+12}" y1="{y}" x2="{L+36}" y2="{y}" stroke="{col}" stroke-width="2"{dash}/>'
        f'<text x="{L+42}" y="{y}" dominant-baseline="middle">{t}</text>')
    lo, hi = d['ranges']['low'], d['ranges']['high']
    return f"""<figure>
  <div style="background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px 10px 6px"><svg viewBox="0 0 {W} {H}" role="img" style="width:100%;height:auto;display:block"
       aria-label="Both bands at full boost and full cut: low-mid from {lo['f1']} to {lo['f0']} Hz, high-mid from {hi['f1']} to {hi['f0']} Hz, plus or minus {lo['boost']:.1f} dB">
    <g stroke="var(--rule)" stroke-width="1">{''.join(grid)}</g>
    <line x1="{L}" y1="{Y(0):.1f}" x2="{W-R}" y2="{Y(0):.1f}" stroke="var(--ink-3)" stroke-width="1"/>
    {''.join(paths)}
    <g fill="var(--ink)">{dots}</g>
    <g fill="var(--ink-3)" font-family="var(--mono)" font-size="11">{''.join(lab)}
      {key(T+10, 'var(--sig)', 'low-mid band')}
      {key(T+26, 'var(--ctl)', 'high-mid band')}
      {key(T+42, 'var(--ink-3)', 'full cut', ' stroke-dasharray="5 4"')}
      <circle cx="{L+24}" cy="{T+58}" r="2.6" fill="var(--ink)"/><text x="{L+42}" y="{T+58}" dominant-baseline="middle">team's LTspice run</text>
    </g>
  </svg></div>
  <figcaption><span>Each band at full boost (solid) and full cut (dashed), frequency knob at the
  bottom, middle and top of its travel &mdash; worked out from the <code>{SCH}</code> netlist</span>
  <a href="data/response.json" target="_blank" rel="noopener">Raw data &rarr;</a></figcaption>
</figure>"""


def blocks():
    """What exists and how it connects, drawn for this site."""
    box = lambda x, y, w, h, t, s='', dash='': (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="var(--surface)" stroke="var(--rule)"{dash}/>'
        f'<text x="{x+w/2}" y="{y+h/2-(6 if s else 0)}" text-anchor="middle" dominant-baseline="middle" '
        f'fill="var(--ink)" font-family="var(--display)" font-size="13">{t}</text>'
        + (f'<text x="{x+w/2}" y="{y+h/2+10}" text-anchor="middle" dominant-baseline="middle" '
           f'fill="var(--ink-3)" font-family="var(--mono)" font-size="10">{s}</text>' if s else ''))
    arrow = lambda x1, y1, x2, y2, dash='': (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="var(--sig)" stroke-width="2"{dash} marker-end="url(#eah)"/>')
    txt = lambda x, y, t, a='middle', c='var(--ink-3)': (
        f'<text x="{x}" y="{y}" text-anchor="{a}" fill="{c}" font-family="var(--mono)" font-size="11">{t}</text>')
    dsh = ' stroke-dasharray="5 4"'
    return f"""<figure>
  <div style="background:var(--surface-2);border:1px solid var(--rule);border-radius:8px;padding:10px">
  <svg viewBox="0 0 720 230" role="img" style="width:100%;height:auto;display:block"
       aria-label="The main sheet chains a low-mid band into a high-mid band. The high-pass, low-pass and gain stages are on separate sheets, and nothing is wired to the edge connector yet">
    <defs><marker id="eah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0L10 5L0 10z" fill="var(--sig)"/></marker></defs>
    {txt(14, 24, 'ON THE MAIN SHEET', 'start', 'var(--ctl)')}
    {txt(40, 76, 'in')}{arrow(56, 72, 128, 72, dsh)}
    {box(130, 40, 190, 64, 'Low-mid band', 'IC3 &middot; 191 Hz&ndash;1.26 kHz')}
    {arrow(320, 72, 388, 72)}
    {box(390, 40, 190, 64, 'High-mid band', 'IC2 &middot; 1.05&ndash;6.9 kHz')}
    {arrow(580, 72, 648, 72, dsh)}{txt(676, 76, 'out')}
    {txt(14, 148, 'ON SHEETS OF THEIR OWN, NOT YET JOINED', 'start', 'var(--ctl)')}
    {box(40, 164, 190, 52, 'High-pass filter', 'OPA1641', dsh)}
    {box(265, 164, 190, 52, 'Low-pass filter', 'OPA1641', dsh)}
    {box(490, 164, 190, 52, 'Gain stage', 'OPA1641', dsh)}
  </svg></div>
  <figcaption><span>What is drawn, and how much of it is joined up &mdash; dashed lines are not wired yet</span>
  <a href="schematic.html">The main schematic &rarr;</a></figcaption>
</figure>"""


def schematic(caption):
    return fig('schematic', caption + ' &mdash; <code>%s</code> at <code>%s</code>' % (SCH, COMMIT))


def _r():
    return resp()['ranges']


R = _r()
LO, HI = R['low'], R['high']
khz = lambda f: '%.3g&nbsp;kHz' % (f / 1000) if f >= 1000 else '%d&nbsp;Hz' % f

NAV = [("Start here", [("index.html", "01", "Overview"),
                       ("schematic.html", "02", "The main schematic")]),
       ("The circuit", [("bands.html", "03", "Parametric bands"),
                        ("filters.html", "04", "High- and low-pass filters"),
                        ("gain.html", "05", "Gain stage")]),
       ("Practical", [("simulation.html", "06", "Simulating it"),
                      ("status.html", "07", "What is left"),
                      ("files.html", "08", "Design files")])]

PAGES = {}

PAGES['index.html'] = ("Overview", f"""
<p class="eyebrow">Equaliser module</p>
<h1>The equaliser</h1>
<p class="lede">Two fully parametric bands, low-mid and high-mid, each with its own frequency,
width and boost/cut, plus a high-pass filter, a low-pass filter and a gain stage. The two bands
are drawn with values on one sheet; the other three sections are drawn on sheets of their own.</p>

<div class="note warn">
  <h4>Work in progress</h4>
  <p>Written from the <a href="{SRC}">Equaliser repository</a> at commit
  <code>{COMMIT}</code>. The bands are complete as circuits, with values, and their response on
  these pages is worked out from the schematic itself. Nothing is wired to the edge connector
  yet, the op amps are not on the rack's supply, and nothing has been built or measured.</p>
</div>

""" + blocks() + f"""

<h2>What exists</h2>
""" + table(["Section", "Where it is drawn", "Values", "Response"],
            [['<a href="bands.html">Low-mid band</a>', "Main sheet, IC3", "Yes",
              "%s&ndash;%s, &plusmn;%.1f&nbsp;dB; matches the team&rsquo;s LTspice run" % (khz(LO['f1']), khz(LO['f0']), LO['boost'])],
             ['<a href="bands.html">High-mid band</a>', "Main sheet, IC2", "Yes",
              "%s&ndash;%s, &plusmn;%.1f&nbsp;dB" % (khz(HI['f1']), khz(HI['f0']), HI['boost'])],
             ['<a href="filters.html">High-pass filter</a>', "Own sheet", "Yes", "Cutoff 4.6&ndash;20&nbsp;kHz as drawn"],
             ['<a href="filters.html">Low-pass filter</a>', "Own sheet", "Yes", "Will not work as drawn: a capacitor is missing"],
             ['<a href="gain.html">Gain stage</a>', "Own sheet", "Yes", "Will not work as drawn: its inputs are swapped"],
             ["Edge connector", "Main sheet, J1", "&mdash;", "Power pins only; no audio wired"],
             ["Board", "<code>Combined_EQ.kicad_pcb</code>", "&mdash;", "Card outline and J1 only"]],
            ["r", "", "", ""]) + """

<h2>Why the OPA164x</h2>
<p>Every section uses TI's OPA164x family: the quad OPA1644 for the bands, the single OPA1641
for the other three. That is a sensible choice for filters. It is a JFET-input part, so its
input bias current is picoamps rather than the NE5532's hundreds of nanoamps &mdash; which
matters when a pot wiper sits in the signal path. Bias current through a pot is offset, and
offset through a pot is a click every time the knob turns.</p>
<p>The cost is that the desk now carries three op-amp types (the compressor and preamp use the
NE5532), which the bill of materials and the spares box both need to account for. The OPA1644
footprint on the main sheet is TSSOP-14, a 0.65&nbsp;mm-pitch surface-mount package: fine to
hand-solder with flux and a fine tip, but worth knowing before ordering.</p>

<h2>How the repository is laid out</h2>
""" + table(["Folder", "What is in it"],
            [["<code>Combined_EQ/</code>", "The main schematic: both bands and J1. Its board has the card outline and J1 placed."],
             ["<code>Low_Bandpass_Filter/</code>", "The low-mid band on its own sheet, the team&rsquo;s LTspice model "
              "<code>LT_SPICE/BandA.asc</code> and its results, and a board with 15 footprints and no outline"],
             ["<code>High_Bandpass_Filter/</code>", "The high-mid band on its own sheet, and its LTspice model <code>BandB.asc</code>"],
             ["<code>High_Pass_filter/</code>", "The high-pass filter sheet and an LTspice model <code>hpf.asc</code>"],
             ["<code>Low_Pass_Filter/</code>", "The low-pass filter sheet and <code>lpf.asc</code>"],
             ["<code>Variable_Gain/</code>", "The gain stage sheet and <code>variable gain.asc</code>"],
             ["<code>Combined Equaliser/</code>", "An empty KiCad project, a leftover from setting up <code>Combined_EQ/</code>"],
             ["<code>EQ BOM.docx</code>", "A bill-of-materials table with its columns set up and no rows filled"]],
            ["r", ""]) + """
<p>The band sheets in <code>Low_Bandpass_Filter/</code> and <code>High_Bandpass_Filter/</code>
are the same circuits as the main sheet&rsquo;s two bands, part for part, with their own
reference designators. The main sheet is the one to keep editing; the separate copies will
drift if both are changed.</p>
""")

PAGES['schematic.html'] = ("The main schematic", """
<p class="eyebrow">Start here &mdash; 02</p>
<h1>The main schematic</h1>
<p class="lede">Both bands and the card edge connector are on one sheet. Click any part for its
role and the nets it touches, or switch to <em>Connections</em> to see the same netlist as a
graph.</p>

""" + schematic("The equaliser") + """

<h2>Reading it</h2>
""" + table(["Where", "What"],
            [["Top left", "The low-mid band: IC3 (drawn as one 14-pin block, units A&ndash;D), the frequency gang RV9, width RV7 and boost/cut RV8 along the bottom."],
             ["Top right", "The high-mid band, laid out the same way: IC2 (units E&ndash;H), RV6, RV2 and RV5."],
             ["Middle", "The one wire joining them: the low-mid band&rsquo;s output <code>Do</code> is the high-mid band&rsquo;s input."],
             ["Bottom left", "J1, the 15-pin card edge, with its pin labels from Radial&rsquo;s 500-series pinout."]],
            ["r", ""]) + """
<p>Within each band the op amp units talk through local labels: <code>A+</code>,
<code>A-</code> and <code>Ao</code> are unit A&rsquo;s inputs and output, and so on. The labels
<code>B+</code>, <code>C+</code>, <code>F+</code> and <code>G+</code> are drawn on ground, which is
right: those are the integrators&rsquo; + inputs.</p>

<div class="note">
  <h4>About this drawing</h4>
  <p>The sheet is saved by KiCad 9, which is not installed where the site is built, so this
  image is drawn by the site&rsquo;s own generator from the <code>.kicad_sch</code> file. The positions, symbols
  and wires are the file&rsquo;s; the lettering is close to KiCad&rsquo;s but not identical. The
  exported PDF is on <a href="files.html">Design files</a>.</p>
</div>

<h2>J1, as drawn</h2>
""" + table(["Pin", "Label", "Connected to"],
            [["1", "CHASSIS", "&mdash;"],
             ["2", "+OUT+4", "&mdash;"], ["3", "+OUT-2", "&mdash;"], ["4", "-OUT", "&mdash;"],
             ["5", "AGND", "&mdash;"],
             ["6", "SC_LINK", "&mdash;"],
             ["7", "-IN-2", "&mdash;"], ["8", "-IN+4", "&mdash;"], ["9", "+IN-2", "&mdash;"],
             ["10", "+IN+4", "&mdash;"], ["11", "GAIN_ADJ", "&mdash;"],
             ["12", "+16V", "A +16V power symbol only"],
             ["<strong>13</strong>", "<strong>GND</strong>", "<strong>The circuit&rsquo;s ground</strong>"],
             ["14", "-16V", "A &minus;16V power symbol only"],
             ["15", "+48V", "A +48V power symbol only"]],
            ["n", "", ""]) + """

<div class="note warn">
  <h4>Three things to join before this is a working card</h4>
  <p><strong>The op amps have no supply.</strong> IC2 and IC3 take their rails from
  <code>VCC</code> and <code>VEE</code> power symbols, but J1 brings in <code>+16V</code> and
  <code>-16V</code>. KiCad treats differently named power symbols as different nets, so as drawn
  nothing powers the op amps. Rename the op amps&rsquo; symbols to +16V and &minus;16V (or the
  connector&rsquo;s to VCC and VEE), and add decoupling: 100&nbsp;nF from each rail to ground
  at each op amp, and a bulk capacitor per rail where it comes in.</p>
  <p><strong>No audio goes in or out.</strong> The low-mid band&rsquo;s input (the free end of
  R29 and RV8 pin 1) and the high-mid band&rsquo;s output <code>Ho</code> end in bare wires.
  They need to reach J1&rsquo;s input and output pins, through whatever input and output
  stages the module will have, using the same pinout as the
  <a href="../compressor/connector.html">compressor&rsquo;s edge connector</a>.</p>
  <p><strong>Two grounds.</strong> The circuit&rsquo;s ground goes to pin 13, the rack&rsquo;s
  power ground. Pin 5, audio ground, is not connected to anything. Decide which the audio
  returns to before laying out.</p>
</div>

<h2>Parts on this sheet</h2>
""" + table(["Kind", "Parts", "Count"],
            [["Op amps", "IC2, IC3 OPA1644 (quad, TSSOP-14)", "2"],
             ["Resistors", "R14&ndash;R39, all on 0207 axial footprints", "26"],
             ["Capacitors", "C3, C6 2.3&nbsp;nF; C8, C9 12.7&nbsp;nF; C2, C7 10&nbsp;&micro;F. No footprints yet.", "6"],
             ["Pots", "RV6, RV9 10k dual gang; RV2, RV5, RV7, RV8 10k. No footprints yet.", "6"],
             ["Connector", "J1, 15-pin card edge", "1"]],
            ["r", "", "n"]))

PAGES['bands.html'] = ("Parametric bands", f"""
<p class="eyebrow">The circuit &mdash; 03</p>
<h1>The parametric bands</h1>
<p class="lede">Each band is a state-variable filter wired as a peaking equaliser: four op
amps, one quad package, and three knobs &mdash; frequency, width and boost/cut. The two bands
are the same circuit; only the two integrator capacitors differ.</p>

""" + response_chart() + f"""

<h2>What the knobs do</h2>
""" + table(["", "Low-mid", "High-mid"],
            [["Op amp", "IC3", "IC2"],
             ["Integrator caps", "C8, C9 12.7&nbsp;nF", "C3, C6 2.3&nbsp;nF"],
             ["Frequency pot", "RV9, dual gang", "RV6, dual gang"],
             ["Frequency range", "%s&ndash;%s" % (khz(LO['f1']), khz(LO['f0'])), "%s&ndash;%s" % (khz(HI['f1']), khz(HI['f0']))],
             ["Frequency at centre", khz(LO['f0.5']), khz(HI['f0.5'])],
             ["Boost/cut pot", "RV8", "RV5"],
             ["Boost/cut range", "&plusmn;%.1f&nbsp;dB" % LO['boost'], "&plusmn;%.1f&nbsp;dB" % HI['boost']],
             ["Width pot", "RV7", "RV2"],
             ["Q range", "%.1f&ndash;%.0f, %.1f at centre" % (LO['q1'], LO['q0'], LO['q0.5']),
              "%.1f&ndash;%.0f, %.1f at centre" % (HI['q1'], HI['q0'], HI['q0.5'])]],
            ["r", "n", "n"]) + f"""
<p>Every figure here is worked out from the schematic&rsquo;s netlist with linear pots and
ideal op amps (<a href="simulation.html">how</a>). Q is the centre frequency over the width
between the points at half the peak&rsquo;s height in dB. With the boost/cut knob centred, each band is
flat to within 0.01&nbsp;dB from 10&nbsp;Hz to 100&nbsp;kHz. The
two frequency ranges overlap slightly, between {khz(HI['f1'])} and {khz(LO['f0'])}, so between
them they cover {khz(LO['f1'])} to {khz(HI['f0'])} with no gap.</p>

<h2>How a band works</h2>
<p>A state-variable filter is a summing amplifier followed by two integrators in a loop. The
summer (unit A in the low-mid band) produces a high-pass output, the first integrator (B) a
band-pass, the second (C) a low-pass, and the low-pass is fed back to the summer to close the
loop. The reason it is used for parametric EQ is that its centre frequency and its width are
set by different parts, so one knob can move without disturbing the other.</p>
""" + table(["Job", "Low-mid parts", "What sets it"],
            [["Summer", "IC3A, R32 feedback, R35 from the low-pass", "Unity gain round the loop"],
             ["Integrators", "IC3B with C8, IC3C with C9", "Each gang of RV9 feeds one integrator through 10k (R36, R38), with 2k2 (R34, R37) at the bottom of the track"],
             ["Width", "R31 from the band-pass back to A+, RV7 with R27, R28", "How much band-pass is fed back: more feedback, wider band"],
             ["Mix", "IC3D, R29, R39, C7, R33, RV8", "Adds the band-pass to, or takes it from, the dry signal"]],
            ["r", "", ""]) + """

<h3>Frequency</h3>
<p>Each integrator&rsquo;s time constant is its 10k input resistor times its capacitor, so the
top of each range is 1&nbsp;/&nbsp;(2&pi;&nbsp;&times;&nbsp;10k&nbsp;&times;&nbsp;C): 1.25&nbsp;kHz
for 12.7&nbsp;nF and 6.9&nbsp;kHz for 2.3&nbsp;nF. Turning RV9 down taps the signal lower on a
10k track that ends in 2k2, which scales down what reaches the integrator. At the bottom of the
track the integrator sees only 2.2/12.2 of the signal through about 11.8k, the same as a
65k resistor, so the range spans about 6.5 to 1. Both gangs move together, which is what keeps
the width constant as the frequency changes.</p>

<h3>Boost and cut</h3>
<p>The output stage (IC3D) takes the dry signal into its &minus; input through R29, with R39 as
feedback, and the band-pass output into its + input through C7. With R29 and R39 equal, the dry
signal comes out at a gain of &minus;1, plus the band-pass. RV8 sits between the band&rsquo;s
input (pin 1) and its output (pin 3), and its wiper is what the filter listens to.</p>
<ul>
  <li>Wiper at the input end: the filter hears the input, and its band-pass is added to the
  output. The band <strong>boosts</strong>.</li>
  <li>Wiper at the output end: the filter hears the output, so the band-pass inside the loop
  pulls its own band back down. The band <strong>cuts</strong>, by the same amount.</li>
  <li>Wiper at centre: the input and the output are equal and opposite, so the wiper sits at
  zero and the filter hears nothing. The band is <strong>flat</strong>.</li>
</ul>
<p>Because each band inverts, the two bands together come out in phase with the input. Any
inverting stage added later (the <a href="gain.html">gain stage</a> is one) flips the module&rsquo;s
polarity, so count them before wiring J1&rsquo;s balanced pins.</p>

<h2>Checked against the team&rsquo;s simulation</h2>
<p>The low-mid band was simulated in LTspice on 30&nbsp;September
(<code>Low_Bandpass_Filter/LT_SPICE/BandA.asc</code>), with the frequency pot at the top of its
range, the width pot centred and full boost. That run peaks at
<strong>+9.52&nbsp;dB at 1.26&nbsp;kHz</strong>; the netlist calculation gives
<strong>+9.54&nbsp;dB at 1.26&nbsp;kHz</strong> for the same settings, and the dots on the chart
lie on the calculated curve. Two different methods, one using TI&rsquo;s OPA1644 model and one
ideal op amps, agree &mdash; which says the KiCad sheet and the LTspice file describe the same
circuit.</p>
""")

PAGES['filters.html'] = ("High- and low-pass filters", """
<p class="eyebrow">The circuit &mdash; 04</p>
<h1>The high- and low-pass filters</h1>
<p class="lede">Two second-order Sallen-Key filters, each on one OPA1641, each on a sheet of its
own. The high-pass works as drawn. The low-pass is missing a capacitor.</p>

<h2>High-pass filter</h2>
""" + pic("hpf.svg", "High-pass filter &mdash; High_Pass_filter/HPF/HPF.kicad_sch at " + COMMIT) + """
<p>R1 (5.6k) and R2 (10k) divide the input down by 3.9&nbsp;dB. C1 and C2 (270&nbsp;pF each)
then pass the signal to the op amp&rsquo;s + input; R4 plus one gang of RV1 goes from the + input
to ground, and R3 plus the other gang feeds the output back to the point between the
capacitors. R6 (16k) and R5 (27k) give the op amp a gain of 1.59, +4.0&nbsp;dB, which cancels the
input divider and sets the filter&rsquo;s Q at about 0.7.</p>
<p>RV1 is a 100k <strong>dual-gang</strong> pot, one gang in each resistor, so both resistors
rise and fall together and the knob sweeps the cutoff cleanly:</p>
""" + table(["RV1", "Resistance per side", "Cutoff (&minus;3&nbsp;dB)"],
            [["Fully one way", "30k", "20&nbsp;kHz"],
             ["Quarter", "55k", "11&nbsp;kHz"],
             ["Centre", "80k", "7.6&nbsp;kHz"],
             ["Three quarters", "105k", "5.8&nbsp;kHz"],
             ["Fully the other way", "130k", "4.6&nbsp;kHz"]],
            ["r", "n", "n"]) + """
<div class="note warn">
  <h4>Is 4.6&ndash;20&nbsp;kHz the range you want?</h4>
  <p>On a desk channel the high-pass usually trims rumble and handling noise, somewhere from
  20 to 300&nbsp;Hz. At 270&nbsp;pF this one removes everything below the top of the audio band.
  If a rumble filter is the aim, scale both capacitors up together: 27&nbsp;nF puts the same
  knob at 45&ndash;200&nbsp;Hz with nothing else changed.</p>
</div>

<h2>Low-pass filter</h2>
""" + pic("lpf.svg", "Low-pass filter &mdash; Low_Pass_Filter/LPF/LPF.kicad_sch at " + COMMIT) + """
<p>The signal goes through R1 (6.2k), along RV1&rsquo;s 100k track and through R2 (6.2k) to the
op amp&rsquo;s + input. RV1&rsquo;s wiper carries C1 (20&nbsp;nF) back from the output. R4 and R3
set the same gain of 1.59.</p>

<div class="note warn">
  <h4>The capacitor to ground is missing</h4>
  <p>A Sallen-Key low-pass needs two capacitors: one from the middle of the resistor chain back
  to the output (C1 here) and one from the op amp&rsquo;s + input to ground. The sheet has only
  the first. Without the second, no current flows in R2, the + input simply follows the wiper,
  and C1 is pure positive feedback through a stage with a gain above 1. That makes the circuit
  unstable: it will latch to a rail rather than filter.</p>
  <p>The team&rsquo;s LTspice model <code>lpf.asc</code> has the missing part: 10&nbsp;nF to ground.
  Adding it to the sheet makes this a working filter.</p>
</div>

<h3>The knob, once the capacitor is back</h3>
<p>RV1 is a single pot with its wiper as the tap between the two halves. Turning it does not
change the total resistance; it moves resistance from one side of C1 to the other. The cutoff
depends on the <em>product</em> of the two sides, and a product with a fixed sum is largest when
the two are equal. So the cutoff is lowest at the centre and rises towards either end:</p>
""" + table(["RV1 position", "0%", "25%", "50%", "75%", "100%"],
            [["Corner frequency, with 10&nbsp;nF to ground", "440&nbsp;Hz", "220&nbsp;Hz", "200&nbsp;Hz", "220&nbsp;Hz", "440&nbsp;Hz"]],
            ["r", "n", "n", "n", "n", "n"]) + """
<p>Both halves of the knob do the same thing, so no panel legend can be drawn for it, and the Q
moves as well. The high-pass already shows the fix: a <strong>dual-gang pot</strong> with one gang
in place of each resistor, so both sides rise and fall together.</p>
<p>As with the high-pass, the range is worth a second look. A desk low-pass usually trims hiss
somewhere above a few kilohertz; 200&ndash;440&nbsp;Hz removes most of a voice. Dividing both
capacitors by 20 (1&nbsp;nF and 470&nbsp;pF) moves it to about 4&ndash;9&nbsp;kHz.</p>
""")

PAGES['gain.html'] = ("Gain stage", """
<p class="eyebrow">The circuit &mdash; 05</p>
<h1>The gain stage</h1>
<p class="lede">One op amp, one pot, &plusmn;10&nbsp;dB. The idea is sound and the values are
right; as drawn, the op amp&rsquo;s two inputs are the wrong way round.</p>

""" + pic("gain.svg", "Variable gain stage &mdash; Variable_Gain/GAIN/variablegain/variablegain.kicad_sch at " + COMMIT) + """

<h2>What it is meant to do</h2>
<p>C1 (100&nbsp;&micro;F) blocks DC at the input. Then R1 (4.7k), the 10k track of RV1 and R2
(4.7k) run in series from the input to the op amp&rsquo;s output, and the wiper goes to the op
amp&rsquo;s input. C2 (220&nbsp;pF) sits between that input and the output.</p>
<p>Wired as an inverting amplifier, the wiper is a virtual earth, and the gain is the resistance
on the output side of the wiper over the resistance on the input side. Turning the knob moves
resistance from one side to the other:</p>
""" + table(["RV1 wiper", "Input side", "Output side", "Gain"],
            [["At the input end", "4.7k", "14.7k", "+9.9&nbsp;dB"],
             ["Centre", "9.7k", "9.7k", "0&nbsp;dB"],
             ["At the output end", "14.7k", "4.7k", "&minus;9.9&nbsp;dB"]],
            ["r", "n", "n", "n"]) + """
<p>That is a neat single-knob trim: unity at the centre detent, symmetrical either side. C2 rolls
the top off above about 50&nbsp;kHz at full gain. The team&rsquo;s
LTspice model <code>variable gain.asc</code> has the same values.</p>

<div class="note warn">
  <h4>Swap pins 2 and 3</h4>
  <p>On the sheet, the wiper goes to pin 3, the OPA1641&rsquo;s <strong>+</strong> input, and
  ground to pin 2, the <strong>&minus;</strong> input. The feedback through R2 and C2 then
  arrives at the + input: positive feedback, so the output swings to a rail and stays there.
  With the wiper on pin 2 and pin 3 grounded, the stage works as above.</p>
</div>

<p>The stage inverts, so if it ends up in the chain with the two bands, the module as a whole
inverts. That only matters for how J1&rsquo;s balanced pins are wired, but it does matter.</p>
""")

PAGES['simulation.html'] = ("Simulating it", f"""
<p class="eyebrow">Practical &mdash; 06</p>
<h1>Simulating it</h1>
<p class="lede">The low-mid band&rsquo;s LTspice model now runs, and it agrees with the KiCad
sheet. It still only runs on the machine it was drawn on.</p>

<h2>The team&rsquo;s LTspice models</h2>
""" + table(["File", "What it models", "Committed results"],
            [["<code>Low_Bandpass_Filter/LT_SPICE/BandA.asc</code>", "Low-mid band, OPA1644 model, pots as resistor pairs", "Yes, AC run of 30&nbsp;Sep, completed with no errors"],
             ["<code>High_Bandpass_Filter/LTSPICE/BandB.asc</code>", "High-mid band", "Yes"],
             ["<code>High_Pass_filter/hpf.asc</code>", "High-pass, generic op amp", "No"],
             ["<code>Low_Pass_Filter/lpf.asc</code>", "Low-pass, generic op amp", "No"],
             ["<code>Variable_Gain/variable gain.asc</code>", "Gain stage, generic op amp", "No"]],
            ["r", "", ""]) + """

<h2>The model is still linked by an absolute path</h2>
<p>Each op amp&rsquo;s <code>ModelFile</code> in <code>BandA.asc</code> points at a folder on the
machine the file was drawn on:</p>
<pre><code>C:\\Users\\ebul0\\Downloads\\sbom627d\\OPA164x.LIB</code></pre>
<p>On anyone else&rsquo;s machine the simulation stops with &ldquo;This sub-circuit name is not
defined&rdquo;. A copy of the library is already committed beside the schematic, at
<code>LT_SPICE/BandA/OPA164x.LIB</code>. Point the model at that with a relative path and it
will run anywhere. The <code>hpf</code>, <code>lpf</code> and gain models use LTspice&rsquo;s
built-in op amp, so they run as they are.</p>

<h2>How this site works out the response</h2>
<p>LTspice is not available where this site is built, so the response on the
<a href="bands.html">bands page</a> is worked out from the KiCad sheet directly by
<code>build/_eq_response.py</code>. It reads the netlist, splits each pot at its wiper into two
resistors, treats each op amp as a gain of a million, and solves the circuit at 401 frequencies
from 10&nbsp;Hz to 100&nbsp;kHz &mdash; the same nodal analysis SPICE does for an AC run.</p>
<p>Ideal op amps are a fair assumption here. The OPA1644 has 11&nbsp;MHz of gain-bandwidth; at
20&nbsp;kHz that still leaves it hundreds of times more gain than any stage asks for. What it
cannot show is noise, headroom or the op amps&rsquo; own distortion &mdash; those need the real
model, or a real board.</p>

<h2>Re-running BandA</h2>
<ol>
  <li>Open <code>Low_Bandpass_Filter/LT_SPICE/BandA.asc</code> in LTspice.</li>
  <li>Fix the model path as above.</li>
  <li>Run. The analysis is already set: <code>.ac dec 100 10 100k</code>.</li>
  <li>Plot <code>V(output)</code>. With the file&rsquo;s pot settings it should peak at
  +9.5&nbsp;dB near 1.26&nbsp;kHz.</li>
</ol>
<p>To try other knob positions, change the resistor pairs standing in for each pot (R4/R5
width, R9/R10 and R13/R14 frequency, R18/R19 boost/cut), keeping each pair&rsquo;s sum at
10k.</p>
""")

PAGES['status.html'] = ("What is left", """
<p class="eyebrow">Practical &mdash; 07</p>
<h1>What is left</h1>
<p class="lede">In rough order &mdash; each step unblocks the next.</p>
""" + table(["Step", "Why it comes here"],
            [["Fix the low-pass and gain sheets",
              "Add the low-pass&rsquo;s capacitor to ground, swap the gain stage&rsquo;s inputs. Both are one-minute edits."],
             ["Check the filter ranges",
              "The high-pass sits at 4.6&ndash;20&nbsp;kHz and the low-pass at 200&ndash;440&nbsp;Hz. Confirm that is intended before choosing parts."],
             ["Decide the signal chain",
              "Which order the high-pass, bands, low-pass and gain go in, and what drives J1&rsquo;s balanced input and output."],
             ["Bring every section onto the main sheet",
              "Then the copies in the section folders can go, so there is one place to edit."],
             ["Join the supply",
              "Op amps on <code>VCC</code>/<code>VEE</code>, connector on <code>+16V</code>/<code>-16V</code>: one name for each rail, plus decoupling."],
             ["Wire the audio to J1",
              "Input and output through the card edge, as on the compressor."],
             ["Give every part a footprint",
              "The capacitors and pots have none yet, and the pots set the panel layout."],
             ["Lay out the board",
              "<code>Combined_EQ.kicad_pcb</code> has the card outline and J1 already."],
             ["Fill in the bill of materials", "<code>EQ BOM.docx</code> has columns and no rows."]],
            ["r", ""]) + """

<h2>The panel is the binding constraint</h2>
<p>Counting what is drawn: three knobs per band, one each for the high-pass, the low-pass and the
gain. That is <strong>nine knobs</strong>, before any bypass switch. The compressor fits nine
functions on the same 38.10&nbsp;mm faceplate only by using concentric and pull-switch pots, and
three of the equaliser&rsquo;s knobs are dual-gang already, which rules out the simplest
concentric pairings. Worth settling on the
<a href="../faceplate/">faceplate</a> before footprints are chosen, because the pot type decides
the footprint.</p>
""")

import content_files
PAGES['files.html'] = content_files.page('equaliser', '08')

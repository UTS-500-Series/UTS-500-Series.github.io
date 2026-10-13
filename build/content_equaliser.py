"""Equaliser module - page content.

Written from the Equaliser repository at commit 4d106d3 (11 Oct 2026). The boards were
finalised and ordered in 4c10641 on 8 Oct, and 4d106d3 updates the parts list:
https://github.com/UTS-500-Series/Equaliser

The whole equaliser is drawn on Combined_EQ/Combined_EQ.kicad_sch. That sheet's image and
viewer data come from _kicad_sch.py, and every response figure on these pages comes from
_eq_response.py, which solves the same netlist (ideal op amps, linear pots); the low-mid band
is also checked against the team's own LTspice run. The four dual frequency pots sit on a
board of their own, wired pin for pin from J2 to J3, and the solver joins those headers.
Rerun both when the repository changes:

    python3 build/_kicad_sch.py --module equaliser
    python3 build/_eq_response.py
"""
import json, math, os
import shell
from shell import fig, pic, table

SRC = 'https://github.com/UTS-500-Series/Equaliser'
COMMIT = '4d106d3'
SCH = 'Combined_EQ/Combined_EQ.kicad_sch'      # read by _kicad_sch.py, relative to the repository

POWER = {'+16V', '-16V', 'VCC', 'VEE'}
GROUND = {'B+/C+/F+/G+/GND/M+/N+/O+/P+', 'CHASSIS'}


def net_class(n):
    if n in GROUND: return 'gnd'
    if n in POWER: return 'pwr'
    if n.startswith('Net-(R') or n.startswith('Net-(J'): return 'ctl'
    return 'sig'


# One line per part for the viewer's detail panel. IC3 and its parts are the low-mid band,
# IC2 and its parts the high-mid band; the two are wired identically.
_BAND = {
    'low': dict(ic='IC3', sum='A', i1='B', i2='C', out='D', fin='R29', fb='R39', mix='RV8',
                feed='R30', damp='R31', sfb='R32', loop='R35', q='RV7', qg='R27', qs='R28',
                f='RV9', ri1='R36', ri2='R38', rb1='R34', rb2='R37', c1=('C8', 'C39', 'C40'),
                c2=('C9', 'C42', 'C43'), cc='C7', rd='R33', cap='12.7&nbsp;nF', name='low-mid'),
    'high': dict(ic='IC2', sum='E', i1='F', i2='G', out='H', fin='R16', fb='R22', mix='RV5',
                 feed='R17', damp='R18', sfb='R19', loop='R23', q='RV2', qg='R14', qs='R15',
                 f='RV6', ri1='R24', ri2='R26', rb1='R21', rb2='R25', c1=('C3', 'C41'),
                 c2=('C6', 'C44'), cc='C2', rd='R20', cap='2.3&nbsp;nF', name='high-mid'),
}
NOTES = {
    'J1': '500-series 15-pin card edge. Audio in on pins 10 (+) and 8 (-), out on 2 (+) and 4 '
          '(-), supply on 12 and 14 through R6 and R5, ground on 5 and 13, chassis on 1.',
    'IC1': 'INA137 balanced line receiver. Turns the balanced input into one signal at half '
           'the level (-6 dB).',
    'IC4': 'OPA1644 quad. B buffers the bands\' output, D is the low shelf\'s low-pass filter '
           'and C the high shelf\'s high-pass filter. Unit A is unused: its pins 1-3 connect '
           'to nothing.',
    'IC8': 'OPA1644 quad. A and B are the shelves\' level stages, D inverts the dry signal and '
           'C sums everything into the output. It was IC5 before the board was laid out.',
    'U1': 'OPA1641 single op amp, wired as a follower: buffers the INA137\'s output into the '
          'low-mid band. It took over this job from IC4A.',
    'IC6': 'DRV134 balanced line driver. Turns the summed signal back into a balanced output, '
           'at twice the level (+6 dB).',
    'SW1': 'Bypass. One position takes the outputs from the DRV134, the other joins them '
           'straight to the inputs. Works unpowered.',
    'R1': '47R in the cold input leg: with C1 to chassis, keeps radio frequencies out.',
    'R3': '47R in the hot input leg: with C5 to chassis, keeps radio frequencies out.',
    'C1': '470 pF from the cold input to chassis. RF filter with R1.',
    'C5': '470 pF from the hot input to chassis. RF filter with R3.',
    'C4': '47 uF input coupling, cold leg. Blocks DC from the source.',
    'C10': '47 uF input coupling, hot leg. Blocks DC from the source.',
    'R2': '100k, holds the INA137\'s cold input at ground for DC.',
    'R4': '100k, holds the INA137\'s hot input at ground for DC.',
    'R5': '10R in series with the -16 V supply from J1 pin 14.',
    'R6': '10R in series with the +16 V supply from J1 pin 12.',
    'C18': '100 uF reservoir on -16 V.',
    'C20': '100 uF reservoir on +16 V.',
    'C11': '1 uF on -16 V.',
    'C12': '1 uF on +16 V.',
    'C23': '1 uF coupling from the high-mid band into buffer IC4B.',
    'R7': '100k, holds IC4B\'s input at ground for DC.',
    'C35': '100 pF from the cold output to ground.',
    'C36': '100 pF from the hot output to ground.',
    'R8': 'Low shelf filter, first resistor: 6.2k plus one gang of RV1.',
    'R9': 'Low shelf filter, second resistor: 6.2k plus the other gang of RV1.',
    'RV1': 'Low shelf frequency, 100k dual gang, each gang wired as a variable resistor. '
           'Towards pin 3 is a higher corner.',
    'C24': 'Low shelf filter: 10 nF from the middle of the resistor chain to the output. '
           'With C27, 20 nF.',
    'C27': 'Low shelf filter: 10 nF in parallel with C24.',
    'C46': 'Low shelf filter: 10 nF from IC4D\'s + input to ground. With C47, 20 nF.',
    'C47': 'Low shelf filter: 10 nF in parallel with C46.',
    'R10': 'Low shelf filter gain, with R11: 1 + 16k/27k = 1.59, which makes it Butterworth.',
    'R11': 'Low shelf filter feedback, with R10.',
    'R12': 'High shelf input divider, top. With R13, scales the signal by 0.64.',
    'R13': 'High shelf input divider, bottom.',
    'C25': '270 pF, first series capacitor of the high shelf filter.',
    'C26': '270 pF, second series capacitor of the high shelf filter.',
    'R40': 'High shelf filter: 30k plus one gang of RV4, from between the capacitors to the output.',
    'R42': 'High shelf filter: 30k plus the other gang of RV4, from IC4C\'s + input to ground.',
    'RV4': 'High shelf frequency, 100k dual gang, each gang wired as a variable resistor. '
           'Towards pin 3 is a higher corner.',
    'R41': 'High shelf filter gain, with R43: 1.59.',
    'R43': 'High shelf filter feedback, with R41.',
    'RV3': 'Low shelf level. Towards pin 3 boosts, centre is flat, towards pin 1 cuts.',
    'R45': 'Low shelf level stage, input end of RV3.',
    'R46': 'Low shelf level stage, output end of RV3.',
    'C29': '220 pF across the low shelf level stage.',
    'RV10': 'High shelf level. Towards pin 3 boosts, centre is flat, towards pin 1 cuts.',
    'R47': 'High shelf level stage, input end of RV10.',
    'R48': 'High shelf level stage, output end of RV10.',
    'C33': '220 pF across the high shelf level stage. Makes the flat response rise 0.5 dB '
           'around 12 kHz; 22 pF would not.',
    'R44': 'Dry-signal inverter input (IC8D), 10k.',
    'R49': 'Dry-signal inverter feedback, 10k: gain -1.',
    'R50': 'Dry signal into the summer, 10k.',
    'R51': 'High shelf level stage into the summer, 16k.',
    'R52': 'Low shelf level stage into the summer, 16k.',
    'R53': 'High shelf filter straight into the summer, 16k.',
    'R54': 'Low shelf filter straight into the summer, 16k.',
    'R55': 'Summer feedback, 10k.',
    'C28': '100 pF across the summer.',
    'J2': '17-pin header on the pot board. Pins 1-14 carry the four dual frequency pots '
          '(RV1, RV4, RV6, RV9) and their parts to J3, pin for pin; pin 15 is ground.',
    'J3': '17-pin header on the main board, wired pin for pin to J2 on the pot board.',
}
for fb, what in (('FB1', 'cold input'), ('FB2', 'hot input'), ('FB3', 'hot output'),
                 ('FB4', 'cold output')):
    NOTES[fb] = 'Ferrite bead in the %s, at the card edge.' % what
for c in ('C13', 'C14', 'C15', 'C16', 'C17', 'C19', 'C21', 'C22', 'C30', 'C31', 'C32', 'C34',
          'C37', 'C38', 'C45', 'C48'):
    NOTES[c] = '100 nF supply decoupling.'
for h in ('H1', 'H2', 'H3', 'H4'):
    NOTES[h] = 'M3 mounting hole.'
for b in _BAND.values():
    n = b['name']
    NOTES.update({
        b['ic']: 'OPA1644 quad op amp: the whole %s band. Unit %s sums, %s and %s integrate, '
                 '%s mixes the band back into the signal.' % (n, b['sum'], b['i1'], b['i2'], b['out']),
        b['fin']: 'Band input into the output stage\'s inverting input. With %s, gain of -1 for '
                  'the dry signal.' % b['fb'],
        b['fb']: 'Output-stage feedback. Sets the dry gain to -1 with %s.' % b['fin'],
        b['mix']: '%s boost/cut. Pin 1 is the band input, pin 3 the band output; the wiper feeds '
                  'the filter. Pin 1 end is full boost, centre is flat.' % n.capitalize(),
        b['feed']: 'From the boost/cut wiper into the summer\'s + input: the filter\'s input.',
        b['damp']: 'Band-pass output back into the summer\'s + input. Sets the damping.',
        b['sfb']: 'Summer feedback.',
        b['loop']: 'Low-pass output back to the summer\'s - input: closes the state-variable loop.',
        b['q']: '%s width (Q). Its wiper goes to ground through %s; pin 1 end is narrowest.' % (n.capitalize(), b['qg']),
        b['qg']: 'From the width pot\'s wiper to ground.',
        b['qs']: 'From the width pot to the summer\'s - input.',
        b['f']: '%s frequency, dual gang: one gang per integrator, so both move together. Pin 1 '
                'end is the top of the range.' % n.capitalize(),
        b['ri1']: 'Integrator input resistor, first integrator.',
        b['ri2']: 'Integrator input resistor, second integrator.',
        b['rb1']: 'Bottom of the first frequency gang to ground. Sets the bottom of the range.',
        b['rb2']: 'Bottom of the second frequency gang to ground.',
        b['cc']: '10 uF, couples the band-pass output into the output stage\'s + input.',
        b['rd']: '100k, holds the output stage\'s + input at ground for DC.',
    })
    for grp, which in ((b['c1'], 'first'), (b['c2'], 'second')):
        for c in grp:
            NOTES[c] = ('Part of the %s integrator capacitor, %s in all (%s in parallel). This '
                        'value is what places the band.' % (which, b['cap'], ' + '.join(grp)))


def resp():
    return json.load(open(os.path.join(shell.DATA_DIR, 'response.json')))


COLOURS = {'lowshelf': 'var(--warn)', 'lowmid': 'var(--sig)', 'highmid': 'var(--ctl)',
           'highshelf': 'var(--good)'}
LABELS = {'lowshelf': 'low shelf', 'lowmid': 'low-mid band', 'highmid': 'high-mid band',
          'highshelf': 'high shelf'}


def chart(curves, caption, keys, dots=None, dbmin=-12, dbmax=12, step=6, aria=''):
    """Response curves drawn inline so they follow the site's theme. `curves` is a list of
    (points, colour, dashed); `keys` a list of (colour, label, dashed)."""
    W, H, L, R, T, B = 680, 364, 48, 16, 16, 60      # the key sits in a row under the axis
    fmin, fmax = 10, 100000
    X = lambda f: L + (math.log10(f) - 1) / (math.log10(fmax) - 1) * (W - L - R)
    Y = lambda db: T + (dbmax - min(max(db, dbmin), dbmax)) / (dbmax - dbmin) * (H - T - B)
    grid, lab = [], []
    for f in (10, 100, 1000, 10000, 100000):
        grid.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d"/>' % (X(f), T, X(f), H - B))
        lab.append('<text x="%.1f" y="%d" text-anchor="middle">%s</text>'
                   % (X(f), H - B + 18, {10: '10', 100: '100', 1000: '1k', 10000: '10k', 100000: '100k'}[f]))
    db = dbmin
    while db <= dbmax + 1e-9:
        grid.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (L, Y(db), W - R, Y(db)))
        lab.append('<text x="%d" y="%.1f" text-anchor="end" dominant-baseline="middle">%s</text>'
                   % (L - 6, Y(db), ('%+g' % db) if db else '0 dB'))
        db += step
    paths = []
    for pts, col, dash in curves:
        p = 'M' + ' L'.join('%.1f %.1f' % (X(f), Y(d)) for f, d in pts)
        paths.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"%s stroke-linejoin="round"/>'
                     % (p, col, ' stroke-dasharray="5 4"' if dash else ''))
    dotsvg = ''.join('<circle cx="%.1f" cy="%.1f" r="2.2"/>' % (X(f), Y(d)) for f, d in (dots or []))
    keysvg, x, y = [], L, H - 12
    for col, text, dash in keys:
        if col == 'dot':
            keysvg.append('<circle cx="%d" cy="%d" r="2.6" fill="var(--ink)"/>' % (x + 12, y))
        else:
            keysvg.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"%s/>'
                          % (x, y, x + 24, y, col, ' stroke-dasharray="5 4"' if dash else ''))
        keysvg.append('<text x="%d" y="%d" dominant-baseline="middle">%s</text>' % (x + 30, y, text))
        x += 30 + 7 * len(text.replace('&rsquo;', "'")) + 22
    return f"""<figure>
  <div style="background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px 10px 6px"><svg viewBox="0 0 {W} {H}" role="img" style="width:100%;height:auto;display:block" aria-label="{aria}">
    <g stroke="var(--rule)" stroke-width="1">{''.join(grid)}</g>
    <line x1="{L}" y1="{Y(0):.1f}" x2="{W-R}" y2="{Y(0):.1f}" stroke="var(--ink-3)" stroke-width="1"/>
    {''.join(paths)}
    <g fill="var(--ink)">{dotsvg}</g>
    <g fill="var(--ink-3)" font-family="var(--mono)" font-size="11">{''.join(lab)}
      {''.join(keysvg)}
    </g>
  </svg></div>
  <figcaption><span>{caption}</span>
  <a href="data/response.json" target="_blank" rel="noopener">Raw data &rarr;</a></figcaption>
</figure>"""


def curves_for(sections, freqs):
    d = resp()
    return [(c['points'], COLOURS[c['section']], c['gain'] == 'cut') for c in d['curves']
            if c['section'] in sections and c['freq'] in freqs]


def overview_chart():
    secs = ['lowshelf', 'lowmid', 'highmid', 'highshelf']
    return chart(curves_for(secs, (0.5,)),
                 'Each section at full boost (solid) and full cut (dashed), its frequency knob '
                 'centred and every other knob centred &mdash; worked out from the '
                 '<code>%s</code> netlist' % SCH,
                 [(COLOURS[s], LABELS[s], False) for s in secs] + [('var(--ink-3)', 'full cut', True)],
                 aria='All four sections at full boost and full cut')


def bands_chart():
    d = resp()
    return chart(curves_for(['lowmid', 'highmid'], (0, 0.5, 1)),
                 'Each band at full boost (solid) and full cut (dashed), frequency knob at the '
                 'bottom, middle and top of its travel, measured at the module&rsquo;s output',
                 [(COLOURS['lowmid'], 'low-mid band', False), (COLOURS['highmid'], 'high-mid band', False),
                  ('var(--ink-3)', 'full cut', True), ('dot', 'team&rsquo;s LTspice run', False)],
                 dots=d['ltspice']['points'][::8],
                 aria='Both mid bands at full boost and full cut across their frequency ranges')


def shelves_chart():
    return chart(curves_for(['lowshelf', 'highshelf'], (0, 0.5, 1)),
                 'Each shelf at full boost (solid) and full cut (dashed), frequency knob at the '
                 'bottom, middle and top of its travel, measured at the module&rsquo;s output',
                 [(COLOURS['lowshelf'], 'low shelf', False), (COLOURS['highshelf'], 'high shelf', False),
                  ('var(--ink-3)', 'full cut', True)],
                 aria='Both shelves at full boost and full cut across their frequency ranges')


def flat_chart():
    d = resp()
    return chart([(d['flatcurve'], 'var(--sig)', False)],
                 'Every knob centred: the module should be a straight line at 0&nbsp;dB',
                 [('var(--sig)', 'all knobs centred, as drawn', False)],
                 dbmin=-2, dbmax=2, step=0.5, aria='The flat response with every knob centred')


def blocks():
    """The signal path, drawn for this site."""
    box = lambda x, y, w, h, t, s='', col='var(--rule)': (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="var(--surface)" stroke="{col}"/>'
        f'<text x="{x+w/2}" y="{y+h/2-(6 if s else 0)}" text-anchor="middle" dominant-baseline="middle" '
        f'fill="var(--ink)" font-family="var(--display)" font-size="13">{t}</text>'
        + (f'<text x="{x+w/2}" y="{y+h/2+10}" text-anchor="middle" dominant-baseline="middle" '
           f'fill="var(--ink-3)" font-family="var(--mono)" font-size="10">{s}</text>' if s else ''))
    line = lambda pts: ('<polyline points="%s" fill="none" stroke="var(--sig)" stroke-width="2" '
                        'marker-end="url(#eah)"/>' % ' '.join('%d,%d' % p for p in pts))
    txt = lambda x, y, t, a='middle', c='var(--ink-3)': (
        f'<text x="{x}" y="{y}" text-anchor="{a}" fill="{c}" font-family="var(--mono)" font-size="11">{t}</text>')
    return f"""<figure>
  <div style="background:var(--surface-2);border:1px solid var(--rule);border-radius:8px;padding:10px">
  <svg viewBox="0 0 720 300" role="img" style="width:100%;height:auto;display:block"
       aria-label="Input receiver, then the low-mid and high-mid bands in series, then the dry signal and the two shelves in parallel into a summer, then the line driver and the bypass switch">
    <defs><marker id="eah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0L10 5L0 10z" fill="var(--sig)"/></marker></defs>
    {txt(22, 46, 'IN')}{line([(36, 42), (58, 42)])}
    {box(60, 18, 130, 48, 'Input receiver', 'IC1 INA137 &middot; &minus;6 dB')}
    {line([(190, 42), (218, 42)])}
    {box(220, 18, 150, 48, 'Low-mid band', 'IC3 &middot; 191 Hz&ndash;1.26 kHz')}
    {line([(370, 42), (398, 42)])}
    {box(400, 18, 150, 48, 'High-mid band', 'IC2 &middot; 1.05&ndash;6.9 kHz')}
    {line([(550, 42), (600, 42), (600, 92), (60, 92), (60, 112)])}
    {txt(330, 86, 'buffered by IC4B, then split three ways')}
    {box(20, 114, 170, 44, 'Dry', 'IC8D, inverted')}
    {box(210, 114, 230, 44, 'Low shelf', 'IC4D low-pass &rarr; IC8A level')}
    {box(460, 114, 240, 44, 'High shelf', 'IC4C high-pass &rarr; IC8B level')}
    {line([(105, 158), (105, 190), (330, 190), (330, 202)])}
    {line([(325, 158), (325, 172), (340, 172), (340, 202)])}
    {line([(580, 158), (580, 190), (350, 190), (350, 202)])}
    {box(250, 204, 180, 40, 'Summer', 'IC8C')}
    {line([(430, 224), (468, 224)])}
    {box(470, 204, 140, 40, 'Line driver', 'IC6 DRV134 &middot; +6 dB')}
    {line([(610, 224), (628, 224)])}
    {box(630, 204, 76, 40, 'Bypass', 'SW1')}
    {txt(668, 270, 'OUT')}
    {line([(668, 244), (668, 258)])}
  </svg></div>
  <figcaption><span>The signal path. Every block is on the one sheet, <code>{SCH}</code></span>
  <a href="schematic.html">The schematic &rarr;</a></figcaption>
</figure>"""


def schematic(caption):
    return fig('schematic', caption + ' &mdash; <code>%s</code> at <code>%s</code>' % (SCH, COMMIT))


R = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site',
                                'equaliser', 'data', 'response.json')))['ranges']
LS, LM, HM, HS = R['lowshelf'], R['lowmid'], R['highmid'], R['highshelf']
khz = lambda f: ('%.3g&nbsp;kHz' % (f / 1000)).replace('.0&', '&') if f >= 1000 else '%d&nbsp;Hz' % f
dbs = lambda v: ('+%.1f' % v if v > 0 else '&minus;%.1f' % -v) + '&nbsp;dB'
FLATDB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site',
                                     'equaliser', 'data', 'response.json')))['flat']

NAV = [("Start here", [("index.html", "01", "Overview"),
                       ("schematic.html", "02", "The schematic")]),
       ("The circuit", [("io.html", "03", "Input, output &amp; power"),
                        ("bands.html", "04", "Parametric bands"),
                        ("filters.html", "05", "The shelves")]),
       ("Practical", [("board.html", "06", "Board &amp; parts"),
                      ("simulation.html", "07", "Simulating it"),
                      ("status.html", "08", "Building it"),
                      ("files.html", "09", "Design files")])]

PAGES = {}

PAGES['index.html'] = ("Overview", f"""
<p class="eyebrow">Equaliser module</p>
<h1>The equaliser</h1>
<p class="lede">A four-band equaliser: a low shelf, two fully parametric mid bands and a high
shelf, between a balanced input receiver and a balanced line driver, with a hard bypass. The
boards have been ordered and the module is being built.</p>

<div class="note">
  <h4>Ordered, and being built</h4>
  <p>Written from the <a href="{SRC}">Equaliser repository</a> at commit
  <code>{COMMIT}</code> (11&nbsp;October). The team finished the layout and ordered the boards
  on 8&nbsp;October (<code>4c10641</code>, &ldquo;finalised and ordered&rdquo;): a four-layer
  main card, plus a small top board for the four dual frequency pots. The Gerbers that went to
  the fab are in the repository as <code>500_Series_EQ.zip</code>. The supply fault the earlier
  sheet had is fixed. Every response figure on these pages is worked out from the schematic;
  nothing has been measured yet.</p>
  <p>Build notes for the boards as ordered are on <a href="status.html">building it</a>.</p>
</div>

<dl class="spec">
  <div><dt>Format</dt><dd>500 series</dd></div>
  <div><dt>Supply</dt><dd>&plusmn;16 V</dd></div>
  <div><dt>Bands</dt><dd>4</dd></div>
  <div><dt>Knobs</dt><dd>10, plus bypass</dd></div>
  <div><dt>Mid bands</dt><dd>&plusmn;{LM['boost']:.1f} dB</dd></div>
  <div><dt>Low shelf</dt><dd>&plusmn;{LS['boost1']:.1f} dB</dd></div>
  <div><dt>Op amps</dt><dd>4 &times; OPA1644, OPA1641</dd></div>
  <div><dt>Boards</dt><dd>2, ordered</dd></div>
</dl>

""" + blocks() + """

<h2>What it does</h2>
""" + table(["Section", "Frequency", "Boost / cut", "Width (Q)"],
            [['<a href="filters.html">Low shelf</a>', "%s&ndash;%s" % (khz(LS['f0']), khz(LS['f1'])),
              "%s / %s" % (dbs(LS['boost1']), dbs(LS['cut1'])), "&mdash;"],
             ['<a href="bands.html">Low-mid band</a>', "%s&ndash;%s" % (khz(LM['f1']), khz(LM['f0'])),
              "&plusmn;%.1f&nbsp;dB" % LM['boost'], "%.1f&ndash;%.1f" % (LM['q1'], LM['q0'])],
             ['<a href="bands.html">High-mid band</a>', "%s&ndash;%s" % (khz(HM['f1']), khz(HM['f0'])),
              "&plusmn;%.1f&nbsp;dB" % HM['boost'], "%.1f&ndash;%.1f" % (HM['q1'], HM['q0'])],
             ['<a href="filters.html">High shelf</a>', "%s&ndash;%s" % (khz(HS['f0']), khz(HS['f1'])),
              "%s / %s" % (dbs(HS['boost0']), dbs(HS['cut0'])), "&mdash;"]],
            ["r", "n", "n", "n"]) + """
<p>Shelf frequencies are the corner, where the shelf reaches half its depth; their boost and
cut are the most each reaches inside the audio band (at 20&nbsp;Hz for the low shelf with its
corner at the top of its range, at 20&nbsp;kHz for the high shelf with its corner at the
bottom).</p>
<p>The two mid bands are the state-variable circuits the team drew first, now in series on the
main sheet. The shelves grew out of the separate high-pass, low-pass and gain sheets: each
filter now feeds a level stage, and a summer adds or subtracts the filtered signal from the
dry one. With every level knob centred the module is flat to within """ + '%.1f' % FLATDB + """&nbsp;dB
from 20&nbsp;Hz to 20&nbsp;kHz.</p>

""" + overview_chart() + """

<h2>Why the OPA1644</h2>
<p>The filters, buffers and summer all run on TI&rsquo;s OPA1644, a quad JFET-input op amp.
Its input bias current is picoamps rather than the NE5532&rsquo;s hundreds of nanoamps, which
matters when a pot wiper sits in the signal path: bias current through a pot is offset, and
offset through a pot is a click every time the knob turns. The input buffer is its single
sibling, the OPA1641. Both are in SOIC packages (1.27&nbsp;mm pitch), which hand-solder
comfortably, and the parts list now orders exactly what the sheet says.</p>
<p>The input and output use TI&rsquo;s matched pair for balanced lines, the INA137 receiver and
the DRV134 driver. The receiver halves the level and the driver doubles it, so the module is
unity gain overall with 6&nbsp;dB of extra headroom inside.</p>

<h2>How the repository is laid out</h2>
""" + table(["Folder", "What is in it"],
            [["<code>Combined_EQ/</code>", "The design: the whole equaliser on one sheet, and its board"],
             ["<code>500_Series_EQ.zip</code>, <code>500_Series_EQ/</code>", "The Gerbers and drill files that were ordered (8&nbsp;October)"],
             ["<code>Components/</code>", "Vendor library files (symbols, footprints, 3D models) for the DRV134, INA137, OPA1644 and OPA1641, in every CAD format"],
             ["<code>BOM.xlsx</code>", "The team&rsquo;s parts list, with suppliers and part numbers"],
             ["<code>Capacitor BOM.xlsx</code>", "An earlier list of just the capacitors"],
             ["<code>Low_Bandpass_Filter/</code>", "The low-mid band on its own sheet and the team&rsquo;s LTspice model "
              "<code>LT_SPICE/BandA.asc</code> with its results"],
             ["<code>High_Bandpass_Filter/</code>", "The high-mid band on its own sheet, and <code>BandB.asc</code>"],
             ["<code>High_Pass_filter/</code>, <code>Low_Pass_Filter/</code>, <code>Variable_Gain/</code>",
              "The first drafts of the shelves&rsquo; parts, each on its own sheet with an LTspice model"],
             ["<code>Combined Equaliser/</code>", "An empty KiCad project, a leftover from setting up <code>Combined_EQ/</code>"],
             ["<code>EQ BOM.docx</code>", "An earlier bill-of-materials table, columns only"]],
            ["r", ""]) + """
<p>The sheets in the section folders are earlier drafts. Two of them still have the faults this
site pointed out (the low-pass sheet&rsquo;s missing capacitor, the gain sheet&rsquo;s swapped
inputs); both are fixed on the main sheet, which is the one to keep editing.</p>
""")

PAGES['schematic.html'] = ("The schematic", """
<p class="eyebrow">Start here &mdash; 02</p>
<h1>The schematic</h1>
<p class="lede">The whole equaliser is on one sheet, drawn as labelled blocks. Click any part
for its role and the nets it touches, or switch to <em>Connections</em> to see the same
netlist as a graph.</p>

""" + schematic("The equaliser") + """

<h2>Reading it</h2>
""" + table(["Where", "What"],
            [["Top left", "J2 (labelled TOP BOARD) and J3 (BOTTOM BOARD): the headers that carry the frequency pots between the two boards, pin for pin."],
             ["Top row", "Balanced input receiver (IC1, the input filtering and the U1 buffer), then the low-mid band (IC3) and the high-mid band (IC2), each drawn the same way."],
             ["Middle", "The buffer (IC4B), the low-pass and high-pass filters (IC4D, IC4C), the variable gain stages (IC8A, IC8B) and the summer (IC8C, with the dry inverter IC8D)."],
             ["Right", "The balanced line driver (IC6) and the bypass switch (SW1)."],
             ["Left and bottom", "IC4 and IC8 drawn as blocks with their supply pins, the mounting holes, J1 (the card edge) and the rail filtering."]],
            ["r", ""]) + """
<p>Blocks talk through global labels named after the op amp unit they belong to: <code>A+</code>,
<code>A-</code> and <code>Ao</code> are unit A&rsquo;s inputs and output, and so on through
<code>P</code>. The labels on ground (<code>B+</code>, <code>C+</code>, <code>F+</code>,
<code>G+</code>, <code>M+</code>&ndash;<code>P+</code>) are right: those are + inputs that sit at
ground.</p>

<div class="note">
  <h4>About this drawing</h4>
  <p>The sheet is saved by KiCad 9. This image is drawn by the site&rsquo;s own generator from
  the <code>.kicad_sch</code> file, and its netlist matches KiCad&rsquo;s own export net for
  net. The positions, symbols and wires are the file&rsquo;s; the lettering is close to
  KiCad&rsquo;s but not identical. The PDF KiCad exports is on <a href="files.html">Design
  files</a>.</p>
</div>

<h2>J1, as drawn</h2>
""" + table(["Pin", "Standard function", "Connected to"],
            [["1", "Chassis", "C1 and C5, the input RF capacitors"],
             ["2", "Output + (+4)", "SW1 through FB3, with C36 to ground"],
             ["3", "Output + (&minus;2)", "&mdash;"],
             ["4", "Output &minus;", "SW1 through FB4, with C35 to ground"],
             ["5", "Audio ground", "The circuit&rsquo;s ground"],
             ["6, 7", "Link, Input &minus; (&minus;2)", "&mdash;"],
             ["8", "Input &minus; (+4)", "FB1, R1, then the INA137&rsquo;s &minus; input"],
             ["9", "Input + (&minus;2)", "&mdash;"],
             ["10", "Input + (+4)", "FB2, R3, then the INA137&rsquo;s + input"],
             ["11", "Gain trim", "&mdash;"],
             ["12", "+16 V", "R6 (10&nbsp;&Omega;), then the +16&nbsp;V rail"],
             ["13", "PSU ground", "The circuit&rsquo;s ground"],
             ["14", "&minus;16 V", "R5 (10&nbsp;&Omega;), then the &minus;16&nbsp;V rail"],
             ["15", "+48 V", "&mdash;"]],
            ["n", "", ""]) + """
<p>That is the standard pinout, the same as the
<a href="../compressor/connector.html">compressor&rsquo;s</a> main input and output. One
difference: pins 5 and 13 are both on the one ground net here, and on the ordered board both
go into the ground plane, so the rack&rsquo;s supply return and audio ground are joined across
the whole card. The compressor keeps them apart and joins them at one point. It is unlikely to
matter on the bench; if the module hums in the rack and the others don&rsquo;t, it is the
first place to look.</p>

<h2>Parts on this sheet</h2>
""" + table(["Kind", "Parts", "Count"],
            [["Op amps", "IC2, IC3, IC4, IC8 OPA1644 (quad, SOIC-14); U1 OPA1641 (single, SOIC-8)", "5"],
             ["Line receiver and driver", "IC1 INA137, IC6 DRV134 (DIP-8)", "2"],
             ["Resistors", "R1&ndash;R55, 0207 axial", "55"],
             ["Capacitors", "C1&ndash;C48", "48"],
             ["Pots", "RV1, RV4 100k dual; RV6, RV9 10k dual; RV2, RV3, RV5, RV7, RV8, RV10 10k. Alps RK097 right-angle footprints; Bourns PTD901/PTD902 ordered", "10"],
             ["Ferrite beads", "FB1&ndash;FB4, one per audio pin", "4"],
             ["Switch", "SW1, DPDT slide", "1"],
             ["Connectors", "J1 card edge; J2, J3 17-pin headers between the boards", "3"],
             ["Mounting holes", "H1&ndash;H4, M3", "4"]],
            ["r", "", "n"]))

PAGES['io.html'] = ("Input, output &amp; power", """
<p class="eyebrow">The circuit &mdash; 03</p>
<h1>Input, output and power</h1>
<p class="lede">A balanced receiver at the front, a balanced driver at the back, a switch that
can join the two, and the supply that feeds it all.</p>

<h2>The input</h2>
<p>Each input leg comes off the card edge through a ferrite bead (FB2 hot, FB1 cold) and a
47&nbsp;&Omega; resistor (R3, R1) with 470&nbsp;pF to chassis (C5, C1). Bead, resistor and
capacitor together keep radio frequencies out: the RC corner is about 7&nbsp;MHz, far above
audio. Then a 47&nbsp;&micro;F capacitor in each leg (C10, C4) blocks any DC the source carries,
with 100k to ground after it (R4, R2) so the INA137&rsquo;s inputs have a DC path.</p>
<p><strong>IC1, the INA137,</strong> is a difference amplifier with laser-trimmed resistors
inside. It subtracts the cold leg from the hot one, which cancels anything common to both
(hum and noise picked up on the cable) and halves the result: &minus;6&nbsp;dB. Its output goes
straight into U1, an OPA1641 wired as a follower, which is what drives the first band. (On the
earlier sheet that buffer was IC4A; unit A of IC4 is now unused.)</p>
<div class="note">
  <h4>Matching the input capacitors</h4>
  <p>A balanced input rejects hum only as well as its two legs match. With 47&nbsp;&micro;F
  coupling capacitors the corner sits well below 1&nbsp;Hz, so even a 20% mismatch between C4
  and C10 makes no measurable difference at 50&nbsp;Hz. The parts list has them as bipolar electrolytics (Jaycar RY6820),
  which is right: a balanced source can sit either side of ground.</p>
</div>

<h2>The output</h2>
<p>The summer&rsquo;s output (<code>Po</code>) drives <strong>IC6, the DRV134</strong>, which
produces two outputs in antiphase at twice the level each side: +6&nbsp;dB, undoing the
receiver&rsquo;s &minus;6&nbsp;dB. Its sense pins are tied to its outputs at the chip, the usual
connection. From there each leg goes through SW1, gets 100&nbsp;pF to ground (C36, C35) and
leaves through a ferrite bead (FB3, FB4).</p>
<p>Counting inversions: the receiver does not invert, each band inverts once (two bands, so the
signal comes out of them the right way up), the dry inverter and the summer invert once each,
and the driver does not invert. The output is in phase with the input.</p>

<h2>Bypass</h2>
<p>SW1 is a double-pole slide switch. In one position the output pins take the DRV134&rsquo;s
outputs. In the other they are joined straight to the input legs, after the ferrite beads and
before the 47&nbsp;&Omega; resistors: a hard bypass, which works with the module unpowered.
Both poles are wired consistently (hot to hot, cold to cold in either position).</p>
<p>On the ordered board SW1 sits near the card edge connector, at the back of the module, so it
is set before the module goes into the rack rather than from the panel. See
<a href="board.html">board &amp; parts</a>.</p>

<h2 id="power">Power</h2>
<p>J1 pin 12 feeds <code>+16V</code> through R6 and pin 14 feeds <code>&minus;16V</code> through
R5, both 10&nbsp;&Omega;. Each rail has a 100&nbsp;&micro;F reservoir (C20, C18), 1&nbsp;&micro;F
(C12, C11) and 100&nbsp;nF next to every chip. The 10&nbsp;&Omega; resistors and the reservoirs
form a filter against noise on the rack&rsquo;s rails, as on the compressor.</p>
<p>From the datasheets&rsquo; typical figures, seventeen op amp channels at 1.8&nbsp;mA (IC4A
draws current even unused), the INA137 at 2.4&nbsp;mA and the DRV134 at 5.2&nbsp;mA come to
about 38&nbsp;mA per rail before any load, well inside the 130&nbsp;mA a 500-series slot
allows.</p>

<div class="note">
  <h4>The supply fault is fixed</h4>
  <p>Until the board was laid out, IC2 and IC5 (now IC8) had a &minus;16&nbsp;V symbol on pin 4
  (V+), which would have left the high-mid band, the shelves&rsquo; level stages and the summer
  unpowered. On the ordered sheet every op amp has pin 4 on +16&nbsp;V and pin 11 on
  &minus;16&nbsp;V, each with its own 100&nbsp;nF to ground.</p>
</div>

<div class="note warn">
  <h4>IC4A is left floating</h4>
  <p>With U1 doing the input buffering, IC4&rsquo;s unit A (pins 1&ndash;3) connects to nothing.
  An unused op amp with open inputs can drift to a rail or oscillate, which adds supply current
  and can couple noise into its neighbours in the same package. It is usually harmless, but if
  the built module shows a whistle or a hot IC4, tie it off by hand: bridge pin 1 to pin 2, and
  run a short wire from pin 3 to ground.</p>
</div>
""")

PAGES['bands.html'] = ("Parametric bands", f"""
<p class="eyebrow">The circuit &mdash; 04</p>
<h1>The parametric bands</h1>
<p class="lede">Each mid band is a state-variable filter wired as a peaking equaliser: four op
amps, one quad package, and three knobs &mdash; frequency, width and boost/cut. The two bands
are the same circuit; only the integrator capacitors differ.</p>

""" + bands_chart() + f"""

<h2>What the knobs do</h2>
""" + table(["", "Low-mid", "High-mid"],
            [["Op amp", "IC3", "IC2"],
             ["Integrator caps", "12.7&nbsp;nF each: C8, C39, C40 and C9, C42, C43", "2.3&nbsp;nF each: C3, C41 and C6, C44"],
             ["Frequency pot", "RV9, dual gang", "RV6, dual gang"],
             ["Frequency range", "%s&ndash;%s" % (khz(LM['f1']), khz(LM['f0'])), "%s&ndash;%s" % (khz(HM['f1']), khz(HM['f0']))],
             ["Frequency at centre", khz(LM['f0.5']), khz(HM['f0.5'])],
             ["Boost/cut pot", "RV8", "RV5"],
             ["Boost/cut range", "&plusmn;%.1f&nbsp;dB" % LM['boost'], "&plusmn;%.1f&nbsp;dB" % HM['boost']],
             ["Width pot", "RV7", "RV2"],
             ["Q range", "%.1f&ndash;%.0f, %.1f at centre" % (LM['q1'], LM['q0'], LM['q0.5']),
              "%.1f&ndash;%.0f, %.1f at centre" % (HM['q1'], HM['q0'], HM['q0.5'])]],
            ["r", "n", "n"]) + f"""
<p>Every figure here is worked out from the schematic&rsquo;s netlist with linear pots and
ideal op amps (<a href="simulation.html">how</a>), at each band&rsquo;s own output. Q is the
centre frequency over the width between the points at half the peak&rsquo;s height in dB. The
two frequency ranges overlap slightly, between {khz(HM['f1'])} and {khz(LM['f0'])}, so between
them they cover {khz(LM['f1'])} to {khz(HM['f0'])} with no gap.</p>
<p>The integrator capacitors are now built from standard values in parallel: 10&nbsp;nF +
2.2&nbsp;nF + 470&nbsp;pF makes the low-mid band&rsquo;s 12.67&nbsp;nF, and 2.2&nbsp;nF +
100&nbsp;pF the high-mid band&rsquo;s 2.3&nbsp;nF. The parts list has them as C0G ceramics,
which hold their value with temperature and voltage &mdash; what a filter capacitor needs.</p>

<h2>How a band works</h2>
<p>A state-variable filter is a summing amplifier followed by two integrators in a loop. The
summer (unit A in the low-mid band) produces a high-pass output, the first integrator (B) a
band-pass, the second (C) a low-pass, and the low-pass is fed back to the summer to close the
loop. It is used for parametric EQ because its centre frequency and its width are set by
different parts, so one knob can move without disturbing the other.</p>
""" + table(["Job", "Low-mid parts", "What sets it"],
            [["Summer", "IC3A, R32 feedback, R35 from the low-pass", "Unity gain round the loop"],
             ["Integrators", "IC3B and IC3C with their 12.7&nbsp;nF", "Each gang of RV9 feeds one integrator through 10k (R36, R38), with 2k2 (R34, R37) at the bottom of the track"],
             ["Width", "R31 from the band-pass back to A+, RV7 with R27, R28", "How much band-pass is fed back: more feedback, wider band"],
             ["Mix", "IC3D, R29, R39, C7, R33, RV8", "Adds the band-pass to, or takes it from, the dry signal"]],
            ["r", "", ""]) + """

<h3>Frequency</h3>
<p>Each integrator&rsquo;s time constant is its 10k input resistor times its capacitor, so the
top of each range is 1&nbsp;/&nbsp;(2&pi;&nbsp;&times;&nbsp;10k&nbsp;&times;&nbsp;C): 1.25&nbsp;kHz
for 12.7&nbsp;nF and 6.9&nbsp;kHz for 2.3&nbsp;nF. Turning RV9 away from pin 1 taps the signal
lower on a 10k track that ends in 2k2, which scales down what reaches the integrator. At the
far end the integrator sees only 2.2/12.2 of the signal through about 11.8k, the same as a
65k resistor, so the range spans about 6.5 to 1. Both gangs move together, which keeps the
width constant as the frequency changes.</p>

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

<div class="note warn">
  <h4>The knobs turn the opposite way to the shelves&rsquo;</h4>
  <p>If pin 3 is a pot&rsquo;s clockwise end, as is usual, then on both mid bands clockwise
  <strong>cuts</strong> (RV8, RV5), <strong>lowers</strong> the frequency (RV9, RV6) and
  <strong>widens</strong> the band (RV7, RV2). On both shelves clockwise boosts and raises the
  corner. Most desks boost and raise the frequency clockwise on every band. The ordered boards
  keep the wiring as drawn, so this is now a job for the faceplate legend: mark the mid
  bands&rsquo; boost, frequency and width the way they actually turn.</p>
</div>

<h2>Checked against the team&rsquo;s simulation</h2>
<p>The low-mid band was simulated in LTspice on 30&nbsp;September
(<code>Low_Bandpass_Filter/LT_SPICE/BandA.asc</code>), with the frequency pot at the top of its
range, the width pot centred and full boost. That run peaks at
<strong>+9.52&nbsp;dB at 1.26&nbsp;kHz</strong>; the netlist calculation of the band on the
main sheet gives <strong>+9.54&nbsp;dB at 1.26&nbsp;kHz</strong> for the same settings, and the
dots on the chart lie on the calculated curve. One method uses TI&rsquo;s OPA1644 model and the
other ideal op amps, and they agree.</p>
""")

PAGES['filters.html'] = ("The shelves", f"""
<p class="eyebrow">The circuit &mdash; 05</p>
<h1>The shelves</h1>
<p class="lede">A low shelf and a high shelf, built from the high-pass, low-pass and gain
circuits the team first drew on separate sheets. Each filter picks out the frequencies its
shelf acts on, a level stage sets how much, and a summer adds the result to the dry signal or
takes it away.</p>

""" + shelves_chart() + """

<h2>How a shelf is made</h2>
<p>After the two bands, buffer IC4B feeds three paths at once:</p>
<ul>
  <li><strong>Dry:</strong> IC8D inverts the signal (R44 and R49, both 10k).</li>
  <li><strong>Low shelf:</strong> IC4D low-pass filters it. The filtered signal goes to the
      summer directly through R54, and through the level stage IC8A, which inverts it, through
      R52.</li>
  <li><strong>High shelf:</strong> the same, with IC4C high-pass filtering, the level stage
      IC8B, and R53 and R51.</li>
</ul>
<p>The summer, IC8C, adds the five inputs with its 10k feedback resistor R55. The dry signal
comes in through 10k, so it reaches the output at unity, inverted back the right way up. Each
filter comes in twice through 16k: once directly, and once through its level stage, inverted.
With a level stage at a gain of exactly 1, those two copies are equal and opposite and cancel,
and the shelf does nothing. Turn the level knob up and the inverted copy wins, so the filtered
band is added to the dry signal: <strong>boost</strong>. Turn it down and the direct copy wins,
which subtracts: <strong>cut</strong>.</p>

<h3>The level stages</h3>
<p>Each level stage is the team&rsquo;s variable-gain circuit: R45 (4.7k), the 10k track of RV3
and R46 (4.7k) in series from input to output, with the wiper on the op amp&rsquo;s &minus;
input. The gain is the resistance on the output side of the wiper over the resistance on the
input side, from 4.7k/14.7k (&minus;9.9&nbsp;dB) to 14.7k/4.7k (+9.9&nbsp;dB), and exactly 1 at
the centre. That is the circuit from the gain sheet with its inputs the right way round.</p>

<h3>The filters</h3>
""" + table(["", "Low shelf (IC4D)", "High shelf (IC4C)"],
            [["Filter", "Sallen-Key low-pass", "Sallen-Key high-pass"],
             ["Capacitors", "20&nbsp;nF and 20&nbsp;nF (C24+C27, C46+C47)", "270&nbsp;pF and 270&nbsp;pF (C25, C26)"],
             ["Resistors", "6.2k + one gang of RV1, each side (R8, R9)", "30k + one gang of RV4, each side (R40, R42)"],
             ["Gain", "1.59 (R11 16k / R10 27k): Butterworth", "1.59 (R43 16k / R41 27k), after a 0.64 divider (R12, R13)"],
             ["&minus;3&nbsp;dB point", "75&nbsp;Hz to 1.28&nbsp;kHz", "4.5 to 19.6&nbsp;kHz"],
             ["Frequency pot", "RV1, 100k dual, both gangs as variable resistors", "RV4, 100k dual, the same"]],
            ["r", "", ""]) + f"""
<p>Both filters now do what the separate sheets were reaching for. The low-pass has its
capacitor to ground, and a dual-gang pot moves both resistors together, so the corner sweeps
cleanly instead of being lowest in the middle of the knob&rsquo;s travel. The ranges that looked
odd for a high-pass and a low-pass &mdash; a high-pass at 4.5&ndash;20&nbsp;kHz, a low-pass
below 1.3&nbsp;kHz &mdash; make sense for shelves: they pick out the top and bottom of the audio
band, which is what a shelf lifts or lowers.</p>

<h2>What they do</h2>
""" + table(["Frequency knob", "Low shelf corner", "Boost / cut at 20&nbsp;Hz", "High shelf corner", "Boost / cut at 20&nbsp;kHz"],
            [["Towards pin 1", khz(LS['f0']), "%s / %s" % (dbs(LS['boost0']), dbs(LS['cut0'])),
              khz(HS['f0']), "%s / %s" % (dbs(HS['boost0']), dbs(HS['cut0']))],
             ["Centre", khz(LS['f0.5']), "%s / %s" % (dbs(LS['boost0.5']), dbs(LS['cut0.5'])),
              khz(HS['f0.5']), "%s / %s" % (dbs(HS['boost0.5']), dbs(HS['cut0.5']))],
             ["Towards pin 3", khz(LS['f1']), "%s / %s" % (dbs(LS['boost1']), dbs(LS['cut1'])),
              khz(HS['f1']), "%s / %s" % (dbs(HS['boost1']), dbs(HS['cut1']))]],
            ["r", "n", "n", "n", "n"]) + f"""
<p>The corner is where the shelf has reached half its depth in dB. With its corner at the
bottom of the range the low shelf hasn&rsquo;t fully arrived by 20&nbsp;Hz, which is why its cut
reads less there.</p>

<div class="note warn">
  <h4>Three things the response shows</h4>
  <ul>
    <li><strong>The high shelf is weaker and lopsided.</strong> It reaches about
        {dbs(HS['boost0'])} / {dbs(HS['cut0'])} where the low shelf reaches
        &plusmn;{LS['boost1']:.1f}&nbsp;dB, and with its corner at the top of the range it barely
        acts below 20&nbsp;kHz. Its path has the R12/R13 divider (&times;0.64) ahead of the
        filter, which the low shelf&rsquo;s doesn&rsquo;t, so its two copies arrive at the summer
        smaller. If the two shelves should match, that divider is the place to look.</li>
    <li><strong>A dip beside each shelf.</strong> Boosting the low shelf dips the response by
        about 3&nbsp;dB just above the corner, and cutting it bumps it by about 1.4&nbsp;dB; the
        high shelf does the same below its corner by 1&ndash;2&nbsp;dB. That comes from adding a
        second-order (Q&nbsp;0.71) filter to the dry signal. Some classic equalisers have this on
        purpose. A lower-Q filter would make it smaller.</li>
    <li><strong>C33 tilts the flat response.</strong> With every knob centred the module rises
        to +{FLATDB:.1f}&nbsp;dB around 12&nbsp;kHz. C33 (220&nbsp;pF across the high shelf&rsquo;s
        level stage) rolls off the inverted copy of the high-passed signal but not the direct
        one, so they stop cancelling at the top of the band. At 22&nbsp;pF the module is flat to
        0.05&nbsp;dB. The board is ordered with 220&nbsp;pF, so fitting 22&nbsp;pF is a
        build-time choice, not a board change. C29 on the low shelf does the same thing in principle, but there is almost
        no low-passed signal up where it acts.</li>
  </ul>
</div>
""")

PAGES['board.html'] = ("Board &amp; parts", """
<p class="eyebrow">Practical &mdash; 06</p>
<h1>Board and parts</h1>
<p class="lede">Two boards, ordered on 8&nbsp;October: the four-layer main card, and a small top
board that carries the four dual frequency pots. They are drawn side by side in one KiCad
file.</p>

<figure>
  <div class="pane"><img src="files/combined-3d-top.png" alt="KiCad 3D render of both equaliser boards, the pot board on the left beside the main card" loading="lazy"></div>
  <figcaption><span>Both boards at <code>4d106d3</code>, from above. The narrow strip on the left with the four large pots is the top board; the rest is the main card. The pots are stand-in blocks: KiCad&rsquo;s library has no model for the RK097</span>
  <a href="files/combined-3d-top.png" target="_blank" rel="noopener">Open full size &rarr;</a></figcaption>
</figure>

<h2>What was ordered</h2>
""" + table(["", "Main card", "Top board"],
            [["Size", "136.85 &times; 105&nbsp;mm, plus the 8&nbsp;mm edge-connector tab", "22.5 &times; 105&nbsp;mm"],
             ["Carries", "Everything else, including the six single pots along its front edge", "RV1, RV4, RV6, RV9 (the frequency pots), the low shelf&rsquo;s 20&nbsp;nF caps, and the resistors at the ends of the pot tracks"],
             ["Joined by", "J3, 17-pin header", "J2, 17-pin header, wired pin for pin to J3"],
             ["Mounting", "H2, H3 (M3)", "H1, H4 (M3)"]],
            ["r", "", ""]) + """
""" + table(["", "Both boards"],
            [["Layers", "Four. Ground pour on In1 on each board; tracks on the front, back and In2"],
             ["Tracks", "832 segments and 71 vias"],
             ["Parts", "133 footprints. Through-hole except the five op amps (SOIC)"],
             ["Gerbers", "<code>500_Series_EQ.zip</code> in the repository, exported 8&nbsp;October with KiCad 9.0.7"]],
            ["r", ""]) + """

<h2>How the two boards fit together</h2>
<p>The repository doesn&rsquo;t say in words, but the drawing points one way. The top
board&rsquo;s holes H1 and H4 sit exactly 22.5&nbsp;mm (its own width) from the main
card&rsquo;s H2 and H3, and the parts list orders two 20&nbsp;mm M3 standoffs. So the top board
appears to stack 20&nbsp;mm above the main card, holes over holes, with its front edge in line
with the card&rsquo;s. That gives the panel two columns of knobs 20&nbsp;mm apart, which is what
fixes the earlier layout&rsquo;s ten shafts crammed into one line:</p>
""" + table(["Height on the card", "Main card column", "Top board column"],
            [["64.5&nbsp;mm", "RV3, low shelf level", ""], ["72&nbsp;mm", "", "RV1, low shelf frequency"],
             ["79.5&nbsp;mm", "RV7, low-mid width", ""], ["87&nbsp;mm", "", "RV9, low-mid frequency"],
             ["94.5&nbsp;mm", "RV8, low-mid boost/cut", ""],
             ["109&nbsp;mm", "RV2, high-mid width", ""], ["116.5&nbsp;mm", "", "RV6, high-mid frequency"],
             ["124&nbsp;mm", "RV5, high-mid boost/cut", ""], ["131.5&nbsp;mm", "", "RV4, high shelf frequency"],
             ["139&nbsp;mm", "RV10, high shelf level", ""]],
            ["n", "", ""]) + """
<p>Heights are the pot positions measured down the card in the board file, so they read in the
board&rsquo;s own coordinates; the faceplate needs them measured from the panel&rsquo;s top
edge. J2 runs along the top board and J3 across the main card, so the 17 links between them are
wires or a ribbon rather than a plug-in header pair.</p>

<h2>What KiCad&rsquo;s checks say</h2>
<p>We ran KiCad 10&rsquo;s design-rule check on the board as ordered. Nothing in it stops the
module working; three things are worth knowing:</p>
<ul>
  <li><strong>The card edge pads are wired on one face only.</strong> Each J1 pin has a pad on
      both faces of the card, and the tracks reach one of them. The compressor joins both faces
      with vias. In a rack whose connector touches both faces of each finger it makes no
      difference; with a meter, check each used pin reaches the circuit from the slot.</li>
  <li><strong>The top board&rsquo;s ground</strong> has no copper link to the main card&rsquo;s;
      it arrives through J2/J3 pin 15, so that wire must be fitted.</li>
  <li><strong>The outline</strong> is reported as malformed because the pot footprints draw
      their own edge marks and the two boards share an edge. The boards were ordered from it
      as it is; it only matters if the file is edited and re-checked.</li>
</ul>

<h2>Fit notes for the build</h2>
<ul>
  <li><strong>C18 and C20</strong> (100&nbsp;&micro;F) are on 5&nbsp;mm disc footprints and
      the parts list has 8&nbsp;mm electrolytic cans (Jaycar RE6334): spread their 3.5&nbsp;mm
      leads to the 5&nbsp;mm holes, minding the polarity, which the footprint
      doesn&rsquo;t mark.</li>
  <li><strong>C2 and C7</strong> (10&nbsp;&micro;F) are on a 2.5&nbsp;mm film footprint and
      the parts list has bipolar electrolytics (Jaycar RY6810), so their leads need the same
      treatment.</li>
  <li><strong>IC1, the INA137,</strong> has a DIP-8 footprint, and the parts list orders the
      SOIC version (INA137UA) with a SOIC-to-DIP adapter.</li>
  <li><strong>The pots</strong> are Bourns PTD901 (single) and PTD902 (dual) on Alps RK097
      footprints. Check one against its footprint before soldering all ten.</li>
</ul>

<h2>The parts list</h2>
<p><code>BOM.xlsx</code> (updated 11&nbsp;October) has part numbers for everything that was
ordered:</p>
""" + table(["Parts", "Ordered as", "Supplier"],
            [["Filter capacitors, 100&nbsp;pF to 10&nbsp;nF", "TDK FG28 C0G, 5% radial, 5&nbsp;mm pitch", "DigiKey"],
             ["Op amps", "OPA1644AID &times; 4, OPA1641AID &times; 1", "DigiKey"],
             ["Line receiver and driver", "INA137UA with a SOIC-to-DIP adapter, DRV134PA", "DigiKey"],
             ["Dual pots", "Bourns PTD902: 100k log, 100k linear, 10k linear &times; 2", "DigiKey"],
             ["Single pots", "Bourns PTD901 10k linear &times; 6", "DigiKey"],
             ["Ferrite beads", "Laird 28C0236-0JW-10 &times; 4", "DigiKey"],
             ["Standoffs", "M3 &times; 20&nbsp;mm aluminium hex &times; 2", "DigiKey"],
             ["100&nbsp;nF and 1&nbsp;&micro;F", "50&nbsp;V monolithic ceramic (RC5490, RC5499)", "Jaycar"],
             ["100&nbsp;&micro;F reservoirs", "35&nbsp;V low-ESR electrolytic (RE6334)", "Jaycar"],
             ["47&nbsp;&micro;F and 10&nbsp;&micro;F coupling", "Bipolar electrolytic (RY6820, RY6810)", "Jaycar"],
             ["Resistors", "0.5&nbsp;W metal film, packs of 8 (RR05xx)", "Jaycar"]],
            ["r", "", ""]) + """
<div class="note">
  <h4>One log pot</h4>
  <p>One of the two 100k duals is ordered log taper and the other linear; these pages assume
  linear throughout. On RV1 or RV4, wired as variable resistors, a log track moves where on the
  knob&rsquo;s travel each corner frequency falls, not the range itself. Whichever one gets the
  log pot, its legend marks need to come from turning it, not from the linear figures here.</p>
</div>
""")

PAGES['simulation.html'] = ("Simulating it", f"""
<p class="eyebrow">Practical &mdash; 07</p>
<h1>Simulating it</h1>
<p class="lede">The site solves the whole sheet; the team&rsquo;s LTspice model of the low-mid
band agrees with it.</p>

<h2>How this site works out the response</h2>
<p>LTspice is not available where this site is built, so every response on these pages is
worked out from the KiCad sheet directly by <code>build/_eq_response.py</code>. It reads the
netlist, splits each pot at its wiper into two resistors, treats each op amp as a gain of a
million, and solves the circuit at 401 frequencies from 10&nbsp;Hz to 100&nbsp;kHz &mdash; the
same nodal analysis SPICE does for an AC run. It starts at the INA137&rsquo;s output and ends at
the DRV134&rsquo;s input; the receiver&rsquo;s &minus;6&nbsp;dB and the driver&rsquo;s +6&nbsp;dB
cancel, so that is also the module&rsquo;s response from input to output.</p>
<p>The four frequency pots are on the top board, connected through J2 and J3; the solver joins
the two headers pin for pin, as the wiring between the boards does.</p>
<p>Ideal op amps are a fair assumption here. The OPA1644 has 11&nbsp;MHz of gain-bandwidth; at
20&nbsp;kHz that still leaves it hundreds of times more gain than any stage asks for. What it
cannot show is noise, headroom or the op amps&rsquo; own distortion &mdash; those need the real
model, or a real board.</p>

""" + flat_chart() + f"""
<p>With every knob centred the response should be a straight line. It is within
{FLATDB:.2f}&nbsp;dB from 20&nbsp;Hz to 20&nbsp;kHz, and the rise towards 12&nbsp;kHz is C33 (see
<a href="filters.html">the shelves</a>).</p>

<h2>The team&rsquo;s LTspice models</h2>
""" + table(["File", "What it models", "Committed results"],
            [["<code>Low_Bandpass_Filter/LT_SPICE/BandA.asc</code>", "Low-mid band, OPA1644 model, pots as resistor pairs", "Yes, AC run of 30&nbsp;Sep"],
             ["<code>High_Bandpass_Filter/LTSPICE/BandB.asc</code>", "High-mid band", "Yes"],
             ["<code>High_Pass_filter/hpf.asc</code>", "First draft of the high shelf&rsquo;s filter, generic op amp", "No"],
             ["<code>Low_Pass_Filter/lpf.asc</code>", "First draft of the low shelf&rsquo;s filter, generic op amp", "No"],
             ["<code>Variable_Gain/variable gain.asc</code>", "The level stage, generic op amp", "No"]],
            ["r", "", ""]) + """
<p>There is no LTspice model of the whole module yet. The shelves only work as shelves once
the dry path, the level stages and the summer are all present, so a model of the full sheet is
the one worth drawing next.</p>

<h2>The BandA model is linked by an absolute path</h2>
<p>Each op amp&rsquo;s <code>ModelFile</code> in <code>BandA.asc</code> points at a folder on the
machine the file was drawn on:</p>
<pre><code>C:\\Users\\ebul0\\Downloads\\sbom627d\\OPA164x.LIB</code></pre>
<p>On anyone else&rsquo;s machine the simulation stops with &ldquo;This sub-circuit name is not
defined&rdquo;. A copy of the library is already committed beside the schematic, at
<code>LT_SPICE/BandA/OPA164x.LIB</code>. Point the model at that with a relative path and it
will run anywhere.</p>
""")

PAGES['status.html'] = ("Building it", """
<p class="eyebrow">Practical &mdash; 08</p>
<h1>Building it</h1>
<p class="lede">The boards are ordered and the module is being built. Most of the questions
this page used to list were settled before ordering; what is left is for the bench and the
faceplate.</p>

<h2>Settled before ordering</h2>
""" + table(["Was", "Now"],
            [["IC2 and IC5 had V+ on &minus;16&nbsp;V", "Fixed: every op amp is powered from both rails"],
             ["Ten shafts in one line, 7.5&nbsp;mm apart", "The frequency pots moved to a top board, giving two columns of knobs (<a href=\"board.html\">board</a>)"],
             ["J2 and J3 unconnected, no footprint", "17-pin headers joining the two boards"],
             ["Parts list said TL084", "OPA1644 ordered, matching the sheet"],
             ["Board not routed", "Routed on four layers and ordered"]],
            ["r", ""]) + """

<h2>On the bench</h2>
""" + table(["Item", "What to do"],
            [["Wire J2 to J3", "All 17 pins, pin for pin, including pin 15 (the top board&rsquo;s only ground)"],
             ["C18, C20, C2, C7", "Electrolytics on footprints drawn for other parts: bend the leads, and fit C18/C20 the right way round (<a href=\"board.html\">fit notes</a>)"],
             ["Card edge", "Each J1 pin is wired on one face only: check continuity from the rack slot"],
             ["IC4A", "Unused, inputs open. Tie it off if the module whistles (<a href=\"io.html#power\">power</a>)"],
             ["C33", "Optional: 22&nbsp;pF instead of 220&nbsp;pF flattens the 12&nbsp;kHz rise (<a href=\"filters.html\">shelves</a>)"],
             ["Bypass", "SW1 is at the rack end of the card, so set it before the module goes in"]],
            ["r", ""]) + """

<h2>Bringing it up</h2>
<ol>
  <li>Before soldering the five op amps, power the board from a bench supply through the card
  edge and check the rails at their pads: +16&nbsp;V on pin 4 and &minus;16&nbsp;V on pin 11 of
  each OPA1644, pin 7 and pin 4 on U1.</li>
  <li>Fit everything, power up with every knob centred and SW1 on the EQ side, and feed a
  1&nbsp;kHz tone. The output should match the input level to within half a dB.</li>
  <li>Sweep each boost/cut knob and check its band moves. If pin 3 of each pot is its
  clockwise end, the mid bands boost anticlockwise (<a href="bands.html">bands</a>).</li>
  <li>Flip SW1 to bypass: the output should equal the input exactly, powered or not.</li>
</ol>

<h2>Still to draw</h2>
<p>The faceplate: ten knob holes in two columns from the pot positions above, plus the legend,
which has to follow the mid bands&rsquo; reversed directions. The compressor&rsquo;s
<a href="../compressor/printed.html">printed faceplate</a> is the pattern to copy.</p>
""")

import content_files
PAGES['files.html'] = content_files.page('equaliser', '09')

"""Preamp module - page content.

Written from the Pre-Amp repository at commit 5e6a308 (18 Sep 2026):
https://github.com/UTS-500-Series/Pre-Amp

The repository is one KiCad 10 sheet (Series-500.kicad_sch) and its board, built on Tormy Van
Cool's 500-series card template. The schematic image and the viewer data are generated from
that sheet by _kicad_sch.py, and every statement about connections here was read from its
netlist. The board has been ordered and is being built (Oct 2026).

The sheet itself carries no component values (every resistor is just "R"). The team's
instruction is that the build uses the values of the published design the sheet redraws:
ESP Project 66 for the preamp and Project 96 for the phantom feed. VALUES below maps those
values onto our reference designators; _kicad_sch.py draws them onto the image and the viewer,
and every figure on these pages is either ESP's or worked out from them. If values ever land in
the repository, take them from there instead and drop VALUES.
"""
from shell import fig, table

SRC = 'https://github.com/UTS-500-Series/Pre-Amp'
COMMIT = '5e6a308'
SCH = 'Series-500.kicad_sch'           # read by _kicad_sch.py, relative to the repository
P66 = 'https://sound-au.com/project66.htm'
P96 = 'https://sound-au.com/project96.htm'

# ESP's values on our references. ESP's own designators differ: P66's R1/R5 are our R12/R13,
# its R2 our R6/R7, R3 our R15/R16, R4 our R19/R20, R9 our R8, R14 our R5, VR1 our RV1, C1 our
# C6, C2/C3 our C7/C8, R10/R11 our R10/R14, R12/R13 our R9/R17, R15/R16 our R11/R18.
VALUES = {
    'R1': '6k8', 'R2': '6k8', 'R3': '10R', 'R4': '10R',
    'D1': '1N4740A', 'D2': '1N4740A', 'D3': '1N4740A', 'D4': '1N4740A',
    'C2': '22u 50V', 'C3': '22u 50V',
    'R12': '3k3', 'R13': '3k3', 'R6': '4k7', 'R7': '4k7', 'R15': '680R', 'R16': '680R',
    'R19': '2k2', 'R20': '2k2', 'R8': '22R', 'RV1': '10k rev log', 'R5': '100k',
    'C6': '1000u 16V', 'C7': '10u', 'C8': '10u',
    'R10': '22k', 'R14': '22k', 'R9': '100k', 'R17': '100k', 'R11': '100R', 'R18': '100R',
    'C4': '100n',
}

POWER = {'+16V', '-16V', '+48V'}
GROUND = {'AGND', 'Earth', 'CHASSIS'}
CONTROL = {'Net-(R5-Pad1)', 'Net-(C6-Pad1)', 'Net-(C1-Pad1)', 'GAIN_ADJ', 'SC_LINK'}


def net_class(n):
    if n in GROUND: return 'gnd'
    if n in POWER: return 'pwr'
    if n in CONTROL: return 'ctl'
    return 'sig'


# One line per part for the viewer's detail panel, with ESP's value where it gives one.
NOTES = {
 'J1': '500-series 15-pin card edge. Only power, ground and +48 V are wired.',
 'J2': 'Microphone hot, on a flying lead to the panel.',
 'J3': 'Microphone cold, on a flying lead to the panel.',
 'J4': 'Microphone ground, tied to AGND.',
 'J5': 'Output hot, on a flying lead.', 'J6': 'Output cold, on a flying lead.',
 'SW1': 'Phantom power on/off, panel mounted via a 2-pin header.',
 'C1': 'Decouples the switched +48 V before the feed resistors. ESP gives no value; it needs a 63 V rating.',
 'R1': '6.8k phantom feed resistor, hot leg. Match to R2 within 10 ohms.',
 'R2': '6.8k phantom feed resistor, cold leg. Match to R1 within 10 ohms.',
 'C2': '22 uF 50 V: blocks the 48 V phantom DC from the hot input. + end to the microphone.',
 'C3': '22 uF 50 V: blocks the 48 V phantom DC from the cold input. + end to the microphone.',
 'R3': '10 ohm series resistor, limits current into D1/D4 on a phantom surge.',
 'R4': '10 ohm series resistor, limits current into D2/D3 on a phantom surge.',
 'D1': '10 V 1 W zener (1N4740A) on +PreIN, back to back with D4.',
 'D4': '10 V 1 W zener (1N4740A) on +PreIN, back to back with D1.',
 'D2': '10 V 1 W zener (1N4740A) on -PreIN, back to back with D3.',
 'D3': '10 V 1 W zener (1N4740A) on -PreIN, back to back with D2.',
 'R12': '3.3k: holds -PreIN (Q1 base) at ground for DC; sets input impedance.',
 'R13': '3.3k: holds +PreIN (Q2 base) at ground for DC; sets input impedance.',
 'Q1': 'PNP input device, cold leg. Drives Q3 as a Sziklai pair.',
 'Q2': 'PNP input device, hot leg. Drives Q4 as a Sziklai pair.',
 'Q3': 'NPN half of the cold-leg pair. Its emitter is the stage output.',
 'Q4': 'NPN half of the hot-leg pair. Its emitter is the stage output.',
 'R6': '4.7k from +16 V to the cold-leg emitter node: sets the stage current, about 3.3 mA.',
 'R7': '4.7k from +16 V to the hot-leg emitter node: sets the stage current, about 3.3 mA.',
 'R15': '680 ohms across Q3 base-emitter: sets how hard Q1 drives Q3.',
 'R16': '680 ohms across Q4 base-emitter: sets how hard Q2 drives Q4.',
 'R19': '2.2k load for the cold-leg output node, to -16 V. The node sits near -8.8 V.',
 'R20': '2.2k load for the hot-leg output node, to -16 V. The node sits near -8.8 V.',
 'R8': '22 ohms, the fixed part of the gain network: sets maximum gain, about 56 dB.',
 'RV1': 'GAIN, 10k reverse log, wired as a variable resistor between the two halves, off board.',
 'R5': '100k across RV1: caps the network resistance, so sets minimum gain.',
 'C6': '1000 uF 16 V: keeps the gain network AC-only so the knob does not move the bias.',
 'C7': '10 uF: blocks the cold-leg output DC (about -8.8 V) before the op amp. + end to R10.',
 'C8': '10 uF: blocks the hot-leg output DC (about -8.8 V) before the op amp. + end to R14.',
 'R10': '22k difference amp input, non-inverting. Match with R14.',
 'R9': '100k, difference amp non-inverting leg to ground. Match with R17.',
 'R14': '22k difference amp input, inverting. Match with R10.',
 'R17': '100k difference amp feedback: gain 100/22 = 4.55. Match with R9.',
 'U1': 'A: the difference amp. B (pins 5-7) is not drawn and must be tied off.',
 'R11': '100 ohm output build-out resistor, hot leg.',
 'R18': '100 ohms, output cold leg to ground: makes the output impedance-balanced.',
 'C4': '100 nF ceramic across the rails, at U1.',
 'C5': 'Bulk decoupling, +16 V to AGND. ESP gives no value; 25 V or more.',
 'C9': 'Bulk decoupling, AGND to -16 V. ESP gives no value; 25 V or more.',
}


def source():
    return f"""<div class="note">
  <h4>Where this comes from</h4>
  <p>The circuit, the board and every connection on these pages are read from the team's own
  KiCad project in <a href="{SRC}">UTS-500-Series/Pre-Amp</a> at <code>{COMMIT}</code>. That
  board has been ordered and is being built.</p>
  <p>The sheet itself has no component values. The build uses the values of the design it
  redraws, Rod Elliott's <a href="{P66}">ESP Project 66</a> with the phantom feed from
  <a href="{P96}">Project 96</a>, so these pages give those values on our reference
  designators, and the schematic shows them. Values ESP's articles don't give are marked as
  such.</p>
</div>"""


def blocks():
    """Signal flow, drawn for this site from our schematic."""
    box = lambda x, y, w, h, t, s='': (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="var(--surface)" stroke="var(--rule)"/>'
        f'<text x="{x+w/2}" y="{y+h/2-(6 if s else 0)}" text-anchor="middle" dominant-baseline="middle" '
        f'fill="var(--ink)" font-family="var(--display)" font-size="13">{t}</text>'
        + (f'<text x="{x+w/2}" y="{y+h/2+10}" text-anchor="middle" dominant-baseline="middle" '
           f'fill="var(--ink-3)" font-family="var(--mono)" font-size="10">{s}</text>' if s else ''))
    arrow = lambda x1, y1, x2, y2, c='var(--sig)': (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="2" marker-end="url(#ah)"/>')
    txt = lambda x, y, t, a='middle', c='var(--ink-3)': (
        f'<text x="{x}" y="{y}" text-anchor="{a}" fill="{c}" font-family="var(--mono)" font-size="11">{t}</text>')
    return f"""<figure>
  <div style="background:var(--surface-2);border:1px solid var(--rule);border-radius:8px;padding:10px">
  <svg viewBox="0 0 720 240" role="img" style="width:100%;height:auto;display:block"
       aria-label="Signal flow: microphone in, phantom feed and protection, two Sziklai pairs joined by the gain network, a difference amplifier, impedance-balanced output">
    <defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0L10 5L0 10z" fill="var(--sig)"/></marker></defs>
    {txt(26, 76, 'J2 +')}{txt(26, 176, 'J3 &#8722;')}
    {arrow(48, 72, 88, 72)}{arrow(48, 172, 88, 172)}
    {box(90, 44, 120, 56, 'Block + clamp', 'C2 R3 D1 D4')}
    {box(90, 144, 120, 56, 'Block + clamp', 'C3 R4 D2 D3')}
    {arrow(210, 72, 258, 72)}{arrow(210, 172, 258, 172)}
    {box(260, 44, 130, 56, 'Sziklai pair', 'Q2 + Q4')}
    {box(260, 144, 130, 56, 'Sziklai pair', 'Q1 + Q3')}
    <line x1="325" y1="100" x2="325" y2="144" stroke="var(--ctl)" stroke-width="2" stroke-dasharray="4 3"/>
    <rect x="336" y="109" width="128" height="26" rx="5" fill="var(--surface)" stroke="var(--ctl)"/>
    {txt(400, 126, 'gain: R8 R5 RV1 C6', 'middle', 'var(--ctl)')}
    {arrow(390, 72, 478, 110)}{arrow(390, 172, 478, 132)}
    {box(480, 90, 130, 62, 'Difference amp', 'U1A')}
    {arrow(610, 121, 650, 121)}
    {txt(686, 116, 'J5 +')}{txt(686, 134, 'J6 &#8722;')}
    {txt(90, 24, '+48 V (J1 pin 15) via SW1, R1, R2', 'start', 'var(--warn)')}
  </svg></div>
  <figcaption><span>Signal flow &mdash; drawn for this site from <code>{SCH}</code></span>
  <a href="schematic.html">The schematic &rarr;</a></figcaption>
</figure>"""


def schematic(caption):
    return fig('schematic', caption + ' &mdash; <code>%s</code> at <code>%s</code>' % (SCH, COMMIT))


NAV = [("Start here", [("index.html", "01", "Overview"),
                       ("schematic.html", "02", "The schematic")]),
       ("The circuit", [("input.html", "03", "Input and phantom power"),
                        ("gain.html", "04", "Gain stage"),
                        ("output.html", "05", "Output stage"),
                        ("power.html", "06", "Power and J1")]),
       ("Practical", [("board.html", "07", "The board and building it"),
                      ("files.html", "08", "Design files")])]

PAGES = {}

PAGES['index.html'] = ("Overview", f"""
<p class="eyebrow">Preamp module</p>
<h1>The microphone preamp</h1>
<p class="lede">A discrete, balanced microphone preamp: two transistor pairs doing the gain,
one op amp turning it into a line output, switchable 48&nbsp;V phantom power, and a single gain
control between the two halves. The board has been ordered and is being built.</p>

{source()}

""" + blocks() + f"""

<h2>What it does</h2>
<p>A microphone delivers millivolts; the desk wants line level. The preamp supplies that gain
while adding as little noise as it can, because everything after it &mdash; the compressor, the
equaliser &mdash; can only ever be as quiet as what the preamp hands on.</p>
<p>The input stage is discrete: a PNP and an NPN transistor per leg, joined as a compound
(Sziklai) pair. The two pairs form a differential stage, with the gain network floating between
them. An NE5532 then takes the difference of the two pair outputs and drives the output.</p>

<h2>What it does, in numbers</h2>
""" + table(["", "Value", "Source"],
            [["Gain", "About 6&nbsp;dB to 56&nbsp;dB on one knob", "Maximum ESP's; minimum ours, from the values"],
             ["Input impedance", "4.4&nbsp;k&Omega; (6.6&nbsp;k&Omega; of bias resistors, with the phantom feed across it)", "Ours, from ESP's values"],
             ["Noise", "1.9&nbsp;nV/&radic;Hz, a 0.9&nbsp;dB noise figure from 200&nbsp;&Omega;, with 2N4403 input transistors", "ESP, measured"],
             ["Maximum input", "About 1.5&nbsp;V RMS before clipping", "ESP"],
             ["Output", "Impedance-balanced, 100&nbsp;&Omega; each leg", "ESP's values"],
             ["Supply", "&plusmn;16&nbsp;V, about 15&nbsp;mA per rail; 48&nbsp;V phantom from J1 pin 15", "Ours"]],
            ["r", "n", ""]) + f"""

<h2>How far along it is</h2>
""" + table(["", "State"],
            [["Schematic", "Complete as a circuit: one sheet, 46 parts, every part connected"],
             ["Component values", "ESP's Project 66 and 96 values, on our references (the sheet itself still reads R and C)"],
             ["PCB", "Ordered: all 46 footprints placed and every net routed on two layers"],
             ["Build", "In progress"],
             ["Edge connector", "Power, ground and +48&nbsp;V only; audio goes in and out on flying leads"]],
            ["r", ""]) + f"""
<p>Build notes, and the full value list, are on <a href="board.html">The board and building
it</a>.</p>

<h2>Parts</h2>
""" + table(["Kind", "Parts", "Count"],
            [["Transistors", "Q1, Q2 2N3906 (PNP); Q3, Q4 BC549 (NPN)", "4"],
             ["Op amp", "U1 NE5532, one half used", "1"],
             ["Resistors", "R1&ndash;R20", "20"],
             ["Capacitors", "C1&ndash;C9: six polarised, three not", "9"],
             ["Zeners", "D1&ndash;D4, 1N47xxA series", "4"],
             ["Controls", "RV1 gain, SW1 phantom, both off board on pin headers", "2"],
             ["Connectors", "J1 card edge; J2&ndash;J6 single-pin sockets for the audio leads", "6"]],
            ["r", "", "n"]) + f"""

<h2>Its lineage</h2>
<p>The topology &mdash; Sziklai input pairs with a floating gain control into a difference amp
&mdash; is the one Rod Elliott published as <a href="{P66}">ESP Project 66</a>, and the phantom
feed and input protection follow the scheme in <a href="{P96}">ESP Project 96</a>. These pages
document our drawing of it, with our reference designators, not ESP's, and its values are
ESP's. Our sheet draws the input PNPs as 2N3906; ESP uses the 2N4403 and names BC559/BC560 as
the substitute, at a noise figure of 1.2&nbsp;dB rather than 0.9&nbsp;dB.</p>
""")

PAGES['schematic.html'] = ("The schematic", """
<p class="eyebrow">Start here &mdash; 02</p>
<h1>The schematic</h1>
<p class="lede">The whole preamp is one sheet. Click any part for its value, its role and the
nets it touches, or switch to <em>Connections</em> to see the same netlist as a graph.</p>

""" + schematic("The preamp, with ESP&rsquo;s values written in by this site") + """

<h2>Reading it</h2>
<p>The sheet is laid out in three blocks:</p>
""" + table(["Where", "What"],
            [["Top left", "Microphone input (J2&ndash;J4), phantom feed (SW1, C1, R1, R2), DC blocking (C2, C3) and protection (R3, R4, D1&ndash;D4). Ends at the global labels <code>+PreIN</code> and <code>-PreIN</code>."],
             ["Top right", "J1, the 15-pin card edge, as drawn by the template. The unused pins carry no-connect flags."],
             ["Bottom", "The gain stage (Q1&ndash;Q4 and the gain network), the difference amp U1A and the output (R11, R18, J5, J6), with the &plusmn;16&nbsp;V rails across the top and bottom."]],
            ["r", ""]) + """
<p>The two halves are joined only by global labels: <code>+PreIN</code> and <code>-PreIN</code>
carry the protected input down to the transistor bases.</p>

<div class="note">
  <h4>About this drawing</h4>
  <p>KiCad 10 cannot be installed where the site is built, so this image is drawn by the
  site's own generator from the <code>.kicad_sch</code> file rather than exported by KiCad.
  The positions, symbols and wires are the file's; the lettering is close to KiCad's but not
  identical. The netlist is built the way KiCad joins pins, wires, junctions and labels, and
  was checked against an independent netlister.</p>
  <p>The values on the drawing are ESP's, put on by the site. In the repository&rsquo;s file
  the parts still read R and C; C1, C5 and C9 have no value in ESP&rsquo;s articles and stay
  blank. The KiCad PDF on <a href="files.html">Design files</a> is the file as it is.</p>
</div>

<h2>Named nets</h2>
""" + table(["Net", "Joins"],
            [["<code>+MicIN</code> / <code>-MicIN</code>", "J2 / J3, the phantom feed resistor R1 / R2, the blocking cap C2 / C3"],
             ["<code>+PreIN</code> / <code>-PreIN</code>", "After R3 / R4: the zener clamps, R13 / R12 to ground, and the base of Q2 / Q1"],
             ["<code>+PreOUT</code> / <code>-PreOUT</code>", "J5 through R11 from U1&rsquo;s output / J6 through R18 to ground"],
             ["<code>+48V</code>", "J1 pin 15 and SW1"],
             ["<code>+16V</code> / <code>-16V</code>", "J1 pins 12 / 14, the pair loads, U1 supply and decoupling"],
             ["<code>AGND</code>", "J1 pin 5, J4, the clamps, R9, R12, R13, R18 and decoupling"]],
            ["r", ""]))

PAGES['input.html'] = ("Input and phantom power", """
<p class="eyebrow">The circuit &mdash; 03</p>
<h1>Input and phantom power</h1>
<p class="lede">Everything between the microphone and the transistor bases: the 48&nbsp;V feed
for condenser microphones, the capacitors that keep it off the preamp, and the zeners that
catch what gets through when a cable is plugged in live.</p>

<h2>The microphone connection</h2>
<p>The microphone arrives on three single-pin sockets: J2 (hot, <code>+MicIN</code>), J3
(cold, <code>-MicIN</code>) and J4 (ground, straight to AGND). They are 2&nbsp;mm pin headers
on the board, so the XLR is wired to the card with flying leads rather than through the edge
connector.</p>

<h2>Phantom power</h2>
<p>Condenser microphones take their power down the same two wires as the audio. The same DC
voltage is put on both legs through a pair of equal resistors, so it is common-mode: invisible
to a balanced input, but available to the microphone.</p>
""" + table(["Part", "Connected", "Value", "Job"],
            [["SW1", "J1 pin 15 (+48&nbsp;V) to the feed node", "&mdash;", "Phantom on/off, on a 2-pin header for a panel switch"],
             ["C1", "Feed node to AGND", "Not given by ESP; 63&nbsp;V or more", "Decouples the switched 48&nbsp;V"],
             ["R1", "Feed node to <code>+MicIN</code>", "6.8&nbsp;k&Omega;", "Feed resistor, hot leg"],
             ["R2", "Feed node to <code>-MicIN</code>", "6.8&nbsp;k&Omega;", "Feed resistor, cold leg"]],
            ["r", "", "n", ""]) + """
<p>R1 and R2 must match closely. If they differ, the phantom voltage is no longer equal on both
legs, and the difference appears as signal. ESP's point in Project 96: two 0.1% 6.81&nbsp;k&Omega;
resistors at opposite ends of their tolerance can differ by 13.6&nbsp;&Omega;, so sorting
ordinary 1% 6.8&nbsp;k&Omega; resistors with a meter to within 10&nbsp;&Omega; does better for
less. Into a short circuit the pair passes 48&nbsp;V / 3.4&nbsp;k&Omega; = 14&nbsp;mA.</p>

<h2>Keeping 48&nbsp;V off the transistors</h2>
<p>C2 and C3, 22&nbsp;&micro;F, sit in series with each leg and block the phantom DC. The
microphone side of each sits at 48&nbsp;V whenever SW1 is on, so ESP calls for 50&nbsp;V or
more, with the positive ends to the microphone side. Into the 3.3&nbsp;k&Omega; bias resistors
they roll off at about 2&nbsp;Hz. ESP suggests 10&nbsp;&micro;F/50&nbsp;V polyester instead for
a cost-no-object build. After them, R3 and R4, 10&nbsp;&Omega; each, lead to
<code>+PreIN</code> and <code>-PreIN</code>.</p>

<h2>The clamps</h2>
<p>A microphone cable is a capacitor. Plug one in with phantom on, or switch phantom with one
connected, and C2 and C3 charge or discharge abruptly through the input. Each input net has two
zeners back to back to ground: D1 and D4 on <code>+PreIN</code>, D2 and D3 on
<code>-PreIN</code>. Whichever way the surge goes, one zener conducts forward and the other at
its zener voltage, so the base can never swing further than that. R3 and R4 limit the peak
current through them.</p>
<p>The zeners are 10&nbsp;V, 1&nbsp;W (1N4740A, from the <code>1N47xxA</code> family the sheet
draws). ESP chose 10&nbsp;V because no microphone gets near it, and 1&nbsp;W because the surge
through them is brief but large. Back to back, each pair clamps its input at about
&plusmn;10.7&nbsp;V.</p>

<h2>Biasing the bases</h2>
<p>R13 (<code>+PreIN</code>) and R12 (<code>-PreIN</code>), 3.3&nbsp;k&Omega; each, run from
each base to AGND. With C2 and C3 blocking DC from the microphone, these are what hold the bases
at 0&nbsp;V. Together they load the microphone with 6.6&nbsp;k&Omega;; the two feed resistors,
13.6&nbsp;k&Omega; across the pair, sit in parallel with that, so the microphone sees about
4.4&nbsp;k&Omega;. ESP set the input high on purpose: professional preamps sit at
2.2&nbsp;k&Omega; or more, and matching a 150&ndash;600&nbsp;&Omega; microphone would throw
away 6&nbsp;dB of signal without lowering the noise.</p>
<p>With nothing plugged in and the gain up, the preamp hisses. That is the 3.3&nbsp;k&Omega;
resistors' own thermal noise; a microphone's low impedance shorts most of it out.</p>

<div class="note warn">
  <h4>Switching phantom</h4>
  <p>Turning SW1 on or off charges or discharges C2 and C3 through the input, which comes out
  as a loud thump through everything downstream. Turn the desk down before switching, and never
  switch phantom with a ribbon microphone connected.</p>
</div>
""")

PAGES['gain.html'] = ("Gain stage", """
<p class="eyebrow">The circuit &mdash; 04</p>
<h1>The gain stage</h1>
<p class="lede">Two compound transistor pairs, one per input leg, with the gain control floating
between them. This is where the preamp's noise performance is decided.</p>

<h2>A Sziklai pair</h2>
<p>Each leg pairs a PNP with an NPN. The PNP (Q1 or Q2, 2N3906) takes the input at its base; its
collector drives the NPN's base (Q3 or Q4, BC549); the NPN's collector returns to the PNP's
emitter. The two behave as one high-gain PNP transistor, far more linear than either device alone
because the second corrects the first.</p>
""" + table(["Acts as", "Cold leg", "Hot leg"],
            [["Base (input)", "Q1 base, <code>-PreIN</code>", "Q2 base, <code>+PreIN</code>"],
             ["Emitter", "Q1 emitter + Q3 collector", "Q2 emitter + Q4 collector"],
             ["Collector (output)", "Q3 emitter", "Q4 emitter"]],
            ["r", "", ""]) + """

<h2>Biasing</h2>
""" + table(["Part", "Connected", "Value", "Job"],
            [["R6 / R7", "+16&nbsp;V to the emitter node", "4.7&nbsp;k&Omega;", "Feeds the pair: sets the stage current"],
             ["R15 / R16", "Across Q3 / Q4 base&ndash;emitter", "680&nbsp;&Omega;", "Sets how much of the current the PNP passes to the NPN"],
             ["R19 / R20", "Output node to &minus;16&nbsp;V", "2.2&nbsp;k&Omega;", "The pair's load; the output sits between the rails"]],
            ["r", "", "n", ""]) + """
<p>ESP prints the operating point on its figure for &plusmn;15&nbsp;V. The rack gives
&plusmn;16&nbsp;V, which moves it slightly; the right-hand column is our recalculation, and it is
what a built board should read:</p>
""" + table(["", "&plusmn;15&nbsp;V (ESP)", "&plusmn;16&nbsp;V (ours)"],
            [["Emitter node (Q1/Q2 emitter)", "+0.65&nbsp;V", "+0.65&nbsp;V"],
             ["Current per half, through R6 / R7", "3.05&nbsp;mA", "3.27&nbsp;mA"],
             ["Output node (Q3/Q4 emitter)", "&minus;8.3&nbsp;V", "&minus;8.8&nbsp;V"]],
            ["r", "n", "n"]) + """
<p>The two legs are drawn identically, part for part. For the stage to reject hum it must stay
that way on the board: matched transistors and matched resistors, leg to leg.</p>

<h2>The gain network</h2>
<p>The network joins the two emitter nodes. It is not referenced to ground: it floats between the
halves. The lower its resistance, the more signal current flows between the pairs, and the higher
the gain.</p>
""" + table(["Part", "Where", "Value", "Job"],
            [["R8", "From the Q1/Q3 emitter node", "22&nbsp;&Omega;", "Fixed minimum resistance: sets maximum gain"],
             ["RV1", "After R8, wiper tied to one end", "10&nbsp;k&Omega; reverse log", "The gain control, wired as a variable resistor"],
             ["R5", "In parallel with RV1", "100&nbsp;k&Omega;", "Caps the network resistance: sets minimum gain"],
             ["C6", "To the Q2/Q4 emitter node", "1000&nbsp;&micro;F, 10 or 16&nbsp;V", "Blocks DC, so turning the knob does not upset bias"]],
            ["r", "", "n", ""]) + """

<h2>How much gain</h2>
<p>ESP gives full gain as 56&nbsp;dB with this 22&nbsp;&Omega;, of which the output stage
contributes a fixed 13&nbsp;dB. At the other end of the knob the network is 22&nbsp;&Omega; plus
10&nbsp;k&Omega; in parallel with 100&nbsp;k&Omega;, about 9.1&nbsp;k&Omega;, which by our
estimate leaves roughly 6&nbsp;dB. So one knob covers about 50&nbsp;dB.</p>
<p>C6 has the largest footprint on the board (13&nbsp;mm radial). It is in series with a
resistance that falls to just R8 at full gain, so it has to be large: 1000&nbsp;&micro;F with
22&nbsp;&Omega; turns over at about 7&nbsp;Hz. It sees almost no DC, so ESP says an ordinary 10
or 16&nbsp;V electrolytic is fine.</p>
<p>RV1 is on a 3-pin header, so the pot mounts on the panel. Gain rises steeply as resistance
falls, so a linear pot crowds most of the range into the end of its travel. ESP specifies a
reverse-log pot, or a standard log pot wired backwards and labelled as attenuation; a rotary
switch in 6&nbsp;dB steps also works and makes settings repeatable.</p>

<h2>Polarity</h2>
<p>Each pair inverts. The cold-leg pair's output goes to the op amp's non-inverting input and the
hot leg's to the inverting input, so the second inversion undoes the first: the output is in
phase with the microphone's hot leg.</p>
""")

PAGES['output.html'] = ("Output stage", """
<p class="eyebrow">The circuit &mdash; 05</p>
<h1>The output stage</h1>
<p class="lede">One half of an NE5532, wired as a difference amplifier, turns the two pair
outputs into a single output and rejects whatever is common to both.</p>

<h2>The difference amplifier</h2>
<p>The pair outputs sit at about &minus;8.8&nbsp;V, so C7 and C8 block that DC first. Their
positive ends face the op amp, which is the more positive side.</p>
""" + table(["Part", "Connected", "Value", "Job"],
            [["C7, R10", "Q3 emitter to U1 pin 3 (+)", "10&nbsp;&micro;F, 22&nbsp;k&Omega;", "Cold-leg pair output in"],
             ["R9", "U1 pin 3 to AGND", "100&nbsp;k&Omega;", "Non-inverting leg to ground"],
             ["C8, R14", "Q4 emitter to U1 pin 2 (&minus;)", "10&nbsp;&micro;F, 22&nbsp;k&Omega;", "Hot-leg pair output in"],
             ["R17", "U1 pin 1 to pin 2", "100&nbsp;k&Omega;", "Feedback"]],
            ["r", "", "n", ""]) + """
<p>Gain is R17&nbsp;/&nbsp;R14 = 100/22 = 4.55, about 13&nbsp;dB, and it only rejects
common-mode signal if R9/R10 match R17/R14. Any mismatch lets hum through as if it were audio,
so ESP asks for 1% metal film throughout; the stage then manages well over 60&nbsp;dB of
rejection. Fixed gain here also sets the ceiling: about 1.5&nbsp;V RMS at the input before
clipping, which ESP puts at more than 150&nbsp;dB SPL with a typical microphone.</p>
<p>ESP&rsquo;s text doesn&rsquo;t state C7 and C8; 10&nbsp;&micro;F is the value builders
discuss for this circuit. Into 22&nbsp;k&Omega; it turns over below 1&nbsp;Hz, so anything from
4.7&nbsp;&micro;F up, rated 16&nbsp;V or more, will do.</p>

<h2>Balanced output</h2>
<p>U1's output leaves through R11, 100&nbsp;&Omega;, to <code>+PreOUT</code> (J5).
<code>-PreOUT</code> (J6) is R18, also 100&nbsp;&Omega;, to ground. Only one leg carries signal, but both present the same impedance if R11 equals
R18. That is an <strong>impedance-balanced</strong> output: the receiving input still rejects
hum picked up along the cable, because the hum arrives equally on both legs, and it takes one op
amp rather than two.</p>

<h2>The other half of U1</h2>
<p>The sheet draws U1's unit A and its power pins; unit B (pins 5, 6 and 7) is not drawn at all,
so on the ordered board those pins go nowhere. A floating op amp can oscillate and inject noise.
On the built board, tie it off by hand: bridge pin 7 to pin 6, and run a short wire from pin 5
to AGND, for example the AGND end of C5 or C9.</p>

<div class="note warn">
  <h4>Never into a phantom-powered input</h4>
  <p>There is no protection on the output. If J5 and J6 ever meet an input supplying phantom
  power, 48&nbsp;V lands on U1's output through R11.</p>
</div>
""")

PAGES['power.html'] = ("Power and J1", """
<p class="eyebrow">The circuit &mdash; 06</p>
<h1>Power and the edge connector</h1>
<p class="lede">The card takes &plusmn;16&nbsp;V, ground and +48&nbsp;V from the rack. Its audio
does not go through the edge connector at all.</p>

<h2>J1, as drawn</h2>
<p>J1 comes from the KiCad card template the project is built on, with its pin labels. Only the
rows in bold connect to anything; the rest carry no-connect flags.</p>
""" + table(["Pin", "Template label", "Connected to"],
            [["1", "CHASSIS", "&mdash;"],
             ["2", "+OUT+4", "&mdash;"], ["3", "+OUT-2", "&mdash;"], ["4", "-OUT", "&mdash;"],
             ["<strong>5</strong>", "<strong>AGND</strong>", "<strong>AGND</strong>"],
             ["6", "SC_LINK", "&mdash;"],
             ["7", "-IN-2", "&mdash;"], ["8", "-IN+4", "&mdash;"], ["9", "+IN-2", "&mdash;"],
             ["10", "+IN+4", "&mdash;"], ["11", "GAIN_ADJ", "&mdash;"],
             ["<strong>12</strong>", "<strong>+16V</strong>", "<strong>R6, R7, U1 pin 8, C4, C5</strong>"],
             ["13", "Earth", "An earth symbol only, not joined to AGND"],
             ["<strong>14</strong>", "<strong>-16V</strong>", "<strong>R19, R20, U1 pin 4, C4, C9</strong>"],
             ["<strong>15</strong>", "<strong>+48V</strong>", "<strong>SW1, the phantom switch</strong>"]],
            ["n", "", ""]) + """

<div class="note warn">
  <h4>The audio is on flying leads</h4>
  <p>The microphone comes in on J2&ndash;J4 and the output leaves on J5 and J6, all single-pin
  headers. That works for a bench build, but in the rack the preamp should take its input and
  send its output through the card edge like the other modules. The ordered board doesn't
  route them there, so for the rack, wire J2/J3 to J1 pins 10 and 8 and J5/J6 to pins 2 and 4
  by hand, the same pinout as the <a href="../compressor/connector.html">compressor's edge
  connector</a>.</p>
</div>

<h2>Decoupling</h2>
""" + table(["Part", "Connected", "Kind", "Value"],
            [["C5", "+16&nbsp;V to AGND", "Polarised, 8&nbsp;mm radial", "Not given by ESP; 25&nbsp;V or more"],
             ["C9", "AGND to &minus;16&nbsp;V", "Polarised, 8&nbsp;mm radial", "Not given by ESP; 25&nbsp;V or more"],
             ["C4", "+16&nbsp;V to &minus;16&nbsp;V", "Ceramic disc, near U1", "100&nbsp;nF"]],
            ["r", "", "", ""]) + """
<p>There is no series resistor or filter on either rail. ESP recommends a post-filter of
10&nbsp;&Omega; and 470&nbsp;&micro;F per rail, and in a rack, where the rails are shared with
every other module, that matters more, not less. The board as ordered has no place for the
resistor, so the 8&nbsp;mm footprints of C5 and C9 are the reservoir; the rack&rsquo;s own
filtering has to do the rest.</p>

<h2>Current</h2>
<p>The two pairs draw about 3.3&nbsp;mA each from each rail through R6, R7, R19 and R20, and
the NE5532 typically adds around 8&nbsp;mA: about 15&nbsp;mA per rail in all, far inside the
130&nbsp;mA a 500-series slot allows. Phantom comes from the separate 48&nbsp;V rail and does not
count against it; each condenser microphone draws up to about 10&nbsp;mA from it.</p>
""")

PAGES['board.html'] = ("The board and building it", f"""
<p class="eyebrow">Practical &mdash; 07</p>
<h1>The board and building it</h1>
<p class="lede">The board has been ordered from the layout in the repository and is being
built with ESP&rsquo;s values. This page has the full value list and what to watch for on the
bench.</p>

<h2>The PCB</h2>
<p>Read from <code>Series-500.kicad_pcb</code> at <code>{COMMIT}</code>:</p>
""" + table(["", "State"],
            [["Outline", "152.35 &times; 105.0&nbsp;mm, from the card template"],
             ["Footprints", "46 placed, one for every part on the sheet"],
             ["Tracks", "156 segments: 128 on the front, 28 on the back, no vias"],
             ["Connectivity", "Every net with two or more pads joined in copper, by our check"],
             ["Copper pours", "None"],
             ["Parts", "All through-hole: 0309 resistors at 12.7&nbsp;mm pitch, TO-92, DIP-8, radial capacitors"]],
            ["r", ""]) + """

<h2>Values for the build</h2>
<p>From ESP Project 66 (the preamp) and Project 96 (the phantom feed), on our references. Use
1% metal film for every resistor, as ESP asks, and avoid bead tantalum capacitors.</p>
""" + table(["Part", "Value", "Notes"],
            [["R1, R2", "6.8&nbsp;k&Omega;", "Phantom feed. Matched to within 10&nbsp;&Omega;"],
             ["R3, R4", "10&nbsp;&Omega;", "Zener current limit"],
             ["D1&ndash;D4", "1N4740A, 10&nbsp;V 1&nbsp;W zener", "Two per input, back to back"],
             ["C2, C3", "22&nbsp;&micro;F 50&nbsp;V electrolytic", "+ to the microphone side"],
             ["R12, R13", "3.3&nbsp;k&Omega;", "Input bias and impedance"],
             ["Q1, Q2", "2N3906 as drawn", "ESP uses the 2N4403, quieter; BC559/BC560 also work"],
             ["Q3, Q4", "BC549", "As ESP"],
             ["R6, R7", "4.7&nbsp;k&Omega;", "Stage current"],
             ["R15, R16", "680&nbsp;&Omega;", ""],
             ["R19, R20", "2.2&nbsp;k&Omega;", ""],
             ["R8", "22&nbsp;&Omega;", "Sets maximum gain"],
             ["RV1", "10&nbsp;k&Omega; reverse log", "Off board, on a 3-pin header"],
             ["R5", "100&nbsp;k&Omega;", "Sets minimum gain"],
             ["C6", "1000&nbsp;&micro;F 16&nbsp;V electrolytic", "13&nbsp;mm can"],
             ["C7, C8", "10&nbsp;&micro;F 16&nbsp;V or more", "Not in ESP&rsquo;s text; + to the op amp side"],
             ["R10, R14", "22&nbsp;k&Omega;", "Match the pair"],
             ["R9, R17", "100&nbsp;k&Omega;", "Match the pair"],
             ["R11, R18", "100&nbsp;&Omega;", "Output"],
             ["U1", "NE5532", "Unit B to be tied off by hand"],
             ["C4", "100&nbsp;nF ceramic", "Across the rails at U1"],
             ["C1", "Not given by ESP", "On the 48&nbsp;V line: 63&nbsp;V or more"],
             ["C5, C9", "Not given by ESP", "Rail reservoirs, 8&nbsp;mm can: 25&nbsp;V or more"]],
            ["r", "n", ""]) + """

<h2>Things to fix on the bench</h2>
""" + table(["Item", "Why", "What to do"],
            [["U1 unit B", "Pins 5&ndash;7 connect to nothing on the board", "Bridge pin 7 to pin 6, wire pin 5 to AGND (<a href=\"output.html\">output stage</a>)"],
             ["Audio on flying leads", "J2&ndash;J6 are single pins, not J1&rsquo;s audio pins", "Wire the XLR and output to them for the bench; for the rack, wire them to J1 pins 10, 8, 2 and 4 by hand"],
             ["Polarised parts", "C2, C3 face the microphone; C7, C8 face the op amp", "Check before soldering; the 48&nbsp;V side is the more positive"],
             ["Matched pairs", "R1/R2, R10/R14 with R9/R17, R11/R18", "Sort with a meter; phantom balance and hum rejection depend on it"]],
            ["r", "", ""]) + """

<h2>Checking a built board</h2>
<ol>
  <li>Power up with no microphone, phantom off and gain at minimum. Both emitter nodes should
  read about +0.65&nbsp;V and both output nodes (the Q3 and Q4 emitters) about
  &minus;8.8&nbsp;V. ESP notes that a reading far from these means a construction mistake, and
  a mismatch between the halves costs hum rejection.</li>
  <li>Turn the gain up with nothing plugged in. Some hiss is normal: it is R12 and R13&rsquo;s
  own noise, and it drops once a low-impedance microphone is connected.</li>
  <li>Plug in a dynamic microphone and check level and polarity at J5.</li>
  <li>Only then try phantom, with a condenser microphone and the output turned down.</li>
</ol>

<div class="note warn">
  <h4>Never into a phantom-powered input</h4>
  <p>ESP warns that 48&nbsp;V on the output destroys the op amp. When testing, plug the output
  into a line input, never a microphone input with phantom on.</p>
</div>
""")

import content_files
PAGES['files.html'] = content_files.page('preamp', '08')

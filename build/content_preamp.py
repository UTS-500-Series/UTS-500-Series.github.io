"""Preamp module - page content.

Written from the Pre-Amp repository at commit 5e6a308 (18 Sep 2026):
https://github.com/UTS-500-Series/Pre-Amp

The repository is one KiCad 10 sheet (Series-500.kicad_sch) and its board, built on Tormy Van
Cool's 500-series card template. The schematic image and the viewer data are generated from
that sheet by _kicad_sch.py, and every statement about connections here was read from its
netlist. The sheet carries no component values yet (every resistor is just "R"), so these
pages describe what each part does, not how big it is. Keep it that way until values land in
the repository: no figure on these pages should come from anywhere else.
"""
from shell import fig, table

SRC = 'https://github.com/UTS-500-Series/Pre-Amp'
COMMIT = '5e6a308'
SCH = 'Series-500.kicad_sch'           # read by _kicad_sch.py, relative to the repository
P66 = 'https://sound-au.com/project66.htm'
P96 = 'https://sound-au.com/project96.htm'

POWER = {'+16V', '-16V', '+48V'}
GROUND = {'AGND', 'Earth', 'CHASSIS'}
CONTROL = {'Net-(R5-Pad1)', 'Net-(C6-Pad1)', 'Net-(C1-Pad1)', 'GAIN_ADJ', 'SC_LINK'}


def net_class(n):
    if n in GROUND: return 'gnd'
    if n in POWER: return 'pwr'
    if n in CONTROL: return 'ctl'
    return 'sig'


# One line per part for the viewer's detail panel. Roles only: the sheet has no values.
NOTES = {
 'J1': '500-series 15-pin card edge. Only power, ground and +48 V are wired.',
 'J2': 'Microphone hot, on a flying lead to the panel.',
 'J3': 'Microphone cold, on a flying lead to the panel.',
 'J4': 'Microphone ground, tied to AGND.',
 'J5': 'Output hot, on a flying lead.', 'J6': 'Output cold, on a flying lead.',
 'SW1': 'Phantom power on/off, panel mounted via a 2-pin header.',
 'C1': 'Decouples the switched +48 V before the feed resistors.',
 'R1': 'Phantom feed resistor, hot leg. Must match R2.',
 'R2': 'Phantom feed resistor, cold leg. Must match R1.',
 'C2': 'Blocks the 48 V phantom DC from the hot input. Needs a 50 V or higher rating.',
 'C3': 'Blocks the 48 V phantom DC from the cold input. Needs a 50 V or higher rating.',
 'R3': 'Series resistor, limits current into D1/D4 on a phantom surge.',
 'R4': 'Series resistor, limits current into D2/D3 on a phantom surge.',
 'D1': 'Zener clamp on +PreIN, back to back with D4.',
 'D4': 'Zener clamp on +PreIN, back to back with D1.',
 'D2': 'Zener clamp on -PreIN, back to back with D3.',
 'D3': 'Zener clamp on -PreIN, back to back with D2.',
 'R12': 'Holds -PreIN (Q1 base) at ground for DC; sets input impedance.',
 'R13': 'Holds +PreIN (Q2 base) at ground for DC; sets input impedance.',
 'Q1': 'PNP input device, cold leg. Drives Q3 as a Sziklai pair.',
 'Q2': 'PNP input device, hot leg. Drives Q4 as a Sziklai pair.',
 'Q3': 'NPN half of the cold-leg pair. Its emitter is the stage output.',
 'Q4': 'NPN half of the hot-leg pair. Its emitter is the stage output.',
 'R6': 'From +16 V to the cold-leg emitter node: sets the stage current.',
 'R7': 'From +16 V to the hot-leg emitter node: sets the stage current.',
 'R15': 'Across Q3 base-emitter: sets how hard Q1 drives Q3.',
 'R16': 'Across Q4 base-emitter: sets how hard Q2 drives Q4.',
 'R19': 'Load for the cold-leg output node, to -16 V.',
 'R20': 'Load for the hot-leg output node, to -16 V.',
 'R8': 'Fixed resistance in the gain network: sets maximum gain.',
 'RV1': 'GAIN. Wired as a variable resistor between the two halves, off board.',
 'R5': 'Across RV1: caps the network resistance, so sets minimum gain.',
 'C6': 'Keeps the gain network AC-only so the knob does not move the bias.',
 'C7': 'Blocks the cold-leg output DC before the op amp.',
 'C8': 'Blocks the hot-leg output DC before the op amp.',
 'R10': 'Difference amp, non-inverting input resistor. Match with R14.',
 'R9': 'Difference amp, non-inverting leg to ground. Match with R17.',
 'R14': 'Difference amp, inverting input resistor. Match with R10.',
 'R17': 'Difference amp feedback. Match with R9.',
 'U1': 'A: the difference amp. B (pins 5-7) is not drawn and must be tied off.',
 'R11': 'Output build-out resistor, hot leg.',
 'R18': 'Output cold leg to ground: makes the output impedance-balanced. Match with R11.',
 'C4': 'Ceramic across the rails, at U1.', 'C5': 'Bulk decoupling, +16 V to AGND.',
 'C9': 'Bulk decoupling, AGND to -16 V.',
}


def source():
    return f"""<div class="note">
  <h4>Where this comes from</h4>
  <p>Everything in this section is read from the team's own KiCad project in
  <a href="{SRC}">UTS-500-Series/Pre-Amp</a> at <code>{COMMIT}</code>. The schematic on
  these pages is drawn from that file and the connections are its netlist. The sheet has no
  component values yet, so nothing here states one.</p>
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
       ("Practical", [("board.html", "07", "The board, and what is left"),
                      ("files.html", "08", "Design files")])]

PAGES = {}

PAGES['index.html'] = ("Overview", f"""
<p class="eyebrow">Preamp module</p>
<h1>The microphone preamp</h1>
<p class="lede">A discrete, balanced microphone preamp: two transistor pairs doing the gain,
one op amp turning it into a line output, switchable 48&nbsp;V phantom power, and a single gain
control between the two halves.</p>

{source()}

""" + blocks() + f"""

<h2>What it does</h2>
<p>A microphone delivers millivolts; the desk wants line level. The preamp supplies that gain
while adding as little noise as it can, because everything after it &mdash; the compressor, the
equaliser &mdash; can only ever be as quiet as what the preamp hands on.</p>
<p>The input stage is discrete: a PNP and an NPN transistor per leg, joined as a compound
(Sziklai) pair. The two pairs form a differential stage, with the gain network floating between
them. An NE5532 then takes the difference of the two pair outputs and drives the output.</p>

<h2>How far along it is</h2>
""" + table(["", "State"],
            [["Schematic", "Complete as a circuit: one sheet, 46 parts, every part connected"],
             ["Component values", "<strong>Not assigned</strong> &mdash; every resistor reads R, every capacitor C, the zeners 1N47xxA"],
             ["PCB", "All 46 footprints placed and every net routed on two layers; no ground pour"],
             ["Edge connector", "Power, ground and +48&nbsp;V only; audio goes in and out on flying leads"],
             ["Simulation, build", "None in the repository"]],
            ["r", ""]) + f"""
<p>What is still needed is on <a href="board.html">The board, and what is left</a>.</p>

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
document our drawing of it, with our reference designators, not ESP's.</p>
""")

PAGES['schematic.html'] = ("The schematic", """
<p class="eyebrow">Start here &mdash; 02</p>
<h1>The schematic</h1>
<p class="lede">The whole preamp is one sheet. Click any part for its role and the nets it
touches, or switch to <em>Connections</em> to see the same netlist as a graph.</p>

""" + schematic("The preamp") + """

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
""" + table(["Part", "Connected", "Job"],
            [["SW1", "J1 pin 15 (+48&nbsp;V) to the feed node", "Phantom on/off, on a 2-pin header for a panel switch"],
             ["C1", "Feed node to AGND", "Decouples the switched 48&nbsp;V"],
             ["R1", "Feed node to <code>+MicIN</code>", "Feed resistor, hot leg"],
             ["R2", "Feed node to <code>-MicIN</code>", "Feed resistor, cold leg"]],
            ["r", "", ""]) + """
<p>R1 and R2 must match closely. If they differ, the phantom voltage is no longer equal on both
legs, and the difference appears as signal.</p>

<h2>Keeping 48&nbsp;V off the transistors</h2>
<p>C2 and C3 sit in series with each leg and block the phantom DC. The microphone side of each
sits at 48&nbsp;V whenever SW1 is on, so they need at least a 50&nbsp;V rating, and if they are
electrolytics, their positive ends go to the microphone side. After them, R3 and R4 lead to
<code>+PreIN</code> and <code>-PreIN</code>.</p>

<h2>The clamps</h2>
<p>A microphone cable is a capacitor. Plug one in with phantom on, or switch phantom with one
connected, and C2 and C3 charge or discharge abruptly through the input. Each input net has two
zeners back to back to ground: D1 and D4 on <code>+PreIN</code>, D2 and D3 on
<code>-PreIN</code>. Whichever way the surge goes, one zener conducts forward and the other at
its zener voltage, so the base can never swing further than that. R3 and R4 limit the peak
current through them.</p>
<p>The zeners are drawn as <code>1N47xxA</code>, the 1&nbsp;W family, with the voltage not yet
chosen. It has to sit above the largest signal the input will ever see and well below what the
transistors' bases can take.</p>

<h2>Biasing the bases</h2>
<p>R13 (<code>+PreIN</code>) and R12 (<code>-PreIN</code>) run from each base to AGND. With C2
and C3 blocking DC from the microphone, these are what hold the bases at 0&nbsp;V, and with the
feed resistors they set the input impedance the microphone sees.</p>

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
""" + table(["Part", "Connected", "Job"],
            [["R6 / R7", "+16&nbsp;V to the emitter node", "Feeds the pair: sets the stage current"],
             ["R15 / R16", "Across Q3 / Q4 base&ndash;emitter", "Sets how much of the current the PNP passes to the NPN"],
             ["R19 / R20", "Output node to &minus;16&nbsp;V", "The pair's load; the output sits between the rails"]],
            ["r", "", ""]) + """
<p>The two legs are drawn identically, part for part. For the stage to reject hum it must stay
that way on the board: matched transistors and matched resistors, leg to leg.</p>

<h2>The gain network</h2>
<p>The network joins the two emitter nodes. It is not referenced to ground: it floats between the
halves. The lower its resistance, the more signal current flows between the pairs, and the higher
the gain.</p>
""" + table(["Part", "Where", "Job"],
            [["R8", "From the Q1/Q3 emitter node", "Fixed minimum resistance: sets maximum gain"],
             ["RV1", "After R8, wiper tied to one end", "The gain control, wired as a variable resistor"],
             ["R5", "In parallel with RV1", "Caps the network resistance: sets minimum gain"],
             ["C6", "To the Q2/Q4 emitter node", "Blocks DC, so turning the knob does not upset bias"]],
            ["r", "", ""]) + """
<p>C6 has the largest footprint on the board (13&nbsp;mm radial). It is in series with a
resistance that falls to just R8 at full gain, so it has to be large or it rolls off the bass at
high gain. It sees almost no DC, so its voltage rating can be low.</p>
<p>RV1 is on a 3-pin header, so the pot mounts on the panel. Gain rises steeply as resistance
falls, so a linear pot crowds most of the range into the end of its travel: a reverse-log pot, or
a stepped switch, spreads it out.</p>

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
<p>The pair outputs sit well below ground, so C7 and C8 block that DC first.</p>
""" + table(["Part", "Connected", "Job"],
            [["C7, R10", "Q3 emitter to U1 pin 3 (+)", "Cold-leg pair output in"],
             ["R9", "U1 pin 3 to AGND", "Non-inverting leg to ground"],
             ["C8, R14", "Q4 emitter to U1 pin 2 (&minus;)", "Hot-leg pair output in"],
             ["R17", "U1 pin 1 to pin 2", "Feedback"]],
            ["r", "", ""]) + """
<p>Gain is R17&nbsp;/&nbsp;R14, and it only rejects common-mode signal if R9/R10 match
R17/R14. Any mismatch lets hum through as if it were audio, so these four want tight tolerance
and should be chosen as two matched pairs.</p>

<h2>Balanced output</h2>
<p>U1's output leaves through R11 to <code>+PreOUT</code> (J5). <code>-PreOUT</code> (J6) is
R18 to ground. Only one leg carries signal, but both present the same impedance if R11 equals
R18. That is an <strong>impedance-balanced</strong> output: the receiving input still rejects
hum picked up along the cable, because the hum arrives equally on both legs, and it takes one op
amp rather than two.</p>

<h2>The other half of U1</h2>
<p>The sheet draws U1's unit A and its power pins; unit B (pins 5, 6 and 7) is not drawn at all,
so on the board those pins go nowhere. A floating op amp can oscillate and inject noise. Add unit
B to the sheet and tie it off: non-inverting input to AGND, output to inverting input.</p>

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
  send its output through the card edge like the other modules. Wiring J2/J3 and J5/J6 to J1's
  audio pins, using the same pinout as the <a href="../compressor/connector.html">compressor's
  edge connector</a>, is the change that makes it a drop-in 500-series card.</p>
</div>

<h2>Decoupling</h2>
""" + table(["Part", "Connected", "Kind"],
            [["C5", "+16&nbsp;V to AGND", "Polarised, 8&nbsp;mm radial"],
             ["C9", "AGND to &minus;16&nbsp;V", "Polarised, 8&nbsp;mm radial"],
             ["C4", "+16&nbsp;V to &minus;16&nbsp;V", "Ceramic disc, near U1"]],
            ["r", "", ""]) + """
<p>There is no series resistor or filter on either rail. The rack's rails are shared with every
other module, and a preamp at high gain amplifies whatever reaches its supply, so a small
resistor ahead of C5 and C9 on each rail would be cheap insurance.</p>

<h2>Current</h2>
<p>The two pairs draw from the rails through R6, R7, R19 and R20; U1 adds its own quiescent
current. With no values yet, the total cannot be worked out, but a circuit of this size is far
inside the 130&nbsp;mA per rail a 500-series slot allows. Phantom comes from the separate 48&nbsp;V
rail and does not count against it.</p>
""")

PAGES['board.html'] = ("The board, and what is left", f"""
<p class="eyebrow">Practical &mdash; 07</p>
<h1>The board, and what is left</h1>
<p class="lede">The layout is further along than the schematic: every part is placed and
routed, but none of them has a value yet.</p>

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
<p>The connectivity row is our own check of track ends against pad positions, not KiCad's
design-rule check. Run DRC in KiCad before ordering; it also catches clearance problems, which
this check does not look for.</p>

<h2>What is left</h2>
""" + table(["To do", "Why"],
            [["Choose and enter every component value", "The sheet has none. Nothing can be simulated, ordered or checked until it does"],
             ["Pick the zener voltage for D1&ndash;D4", "Above the largest input signal, below what the bases can take"],
             ["Match R1/R2, R9/R10 with R17/R14, and R11/R18", "Phantom balance, CMRR and output balance all depend on matching"],
             ["Add U1 unit B and tie it off", "Its pins currently float on the board"],
             ["Route the audio through J1", "So the card works in a rack slot like the other modules"],
             ["Consider rail filtering", "The rails are shared with the other modules"],
             ["Add a ground pour and run DRC", "Neither has been done"]],
            ["r", ""]) + """

<h2>Checking a built board</h2>
<ol>
  <li>Power up with no microphone, phantom off and gain at minimum. The emitter nodes of both
  pairs should read the same, and so should both output nodes (the Q3 and Q4 emitters). A
  mismatch between the halves costs hum rejection.</li>
  <li>Turn the gain up with nothing plugged in. Some hiss is normal: it is the input bias
  resistors' own noise, and it drops once a low-impedance microphone is connected.</li>
  <li>Plug in a dynamic microphone and check level and polarity at J5.</li>
  <li>Only then try phantom, with a condenser microphone and the output turned down.</li>
</ol>
""")

import content_files
PAGES['files.html'] = content_files.page('preamp', '08')

"""PCB layout guide - page content.

Shared by all three modules: a working order for laying out a two-layer 500-series card in
KiCad, from board setup to ordering. The examples use the compressor board in
Compressor/kicad_withpcb/compressor_with_pcb as it stood on 28 September 2026 (all 166
footprints roughly placed, no tracks). Menu names are for KiCad 9 and 10.
"""
from shell import table

ORG = 'https://github.com/UTS-500-Series'
BOARD = ORG + '/Compressor/tree/main/kicad_withpcb/compressor_with_pcb'

NAV = [("Start here", [("index.html", "01", "Where the board is")]),
       ("Before placing", [("setup.html", "02", "Set up the board"),
                           ("mechanics.html", "03", "Lock the mechanics")]),
       ("Layout", [("placement.html", "04", "Place the parts"),
                   ("grounds.html", "05", "Plan the grounds"),
                   ("routing.html", "06", "Route"),
                   ("pours.html", "07", "Pours and edge fingers")]),
       ("Finishing", [("checks.html", "08", "Silkscreen and checks"),
                      ("fab.html", "09", "Send it to a fab")])]


def zones():
    """The template outline at 4 px per mm with suggested compressor zones and the J1 pin
    order read from the footprint (pin 1 nearest the top of the card)."""
    pins = ['CHASSIS', 'OUT+', 'AUXOUT+', 'OUT&#8722;', 'AGND', 'LINK', 'AUXOUT&#8722;',
            'IN&#8722;', 'AUXIN&#8722;', 'IN+', 'AUXIN+', '+16V', 'PGND', '&#8722;16V', '+48V nc']
    fingers = ''.join('<rect x="585" y="%.1f" width="20" height="6"/>' % (78.4 + i * 15.84)
                      for i in range(15))
    labels = ''.join('<text x="614" y="%.1f">%d %s</text>' % (85 + i * 15.84, i + 1, p)
                     for i, p in enumerate(pins))
    return f"""<figure>
  <div style="background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px;overflow-x:auto">
  <svg viewBox="0 0 780 560" role="img" style="width:100%;min-width:560px;height:auto;display:block"
       aria-label="Top view of the 500-series board outline with suggested placement zones and the edge connector pin order">
  <defs><marker id="arz" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="var(--sig)"/></marker></defs>
  <g font-family="var(--mono)" transform="translate(60 60)">
  <path d="M0,0 H577.4 V66 H605.4 L609.4,70 V312 L605.4,316 H577.4 V420 H0 Z" fill="var(--surface-2)" stroke="var(--ctl)" stroke-width="2"/>
  <g font-size="12" fill="var(--ink)">
    <rect x="4" y="4" width="84" height="412" fill="var(--warn-bg)" stroke="var(--sig)" stroke-dasharray="4 3"/>
    <text x="46" y="190" text-anchor="middle" transform="rotate(-90 46 190)">FRONT EDGE &#183; controls, meters, switch headers</text>
    <g fill="none" stroke="var(--ink-3)" stroke-dasharray="4 3"><rect x="96" y="4" width="180" height="412"/><rect x="284" y="4" width="160" height="412"/><rect x="452" y="4" width="121" height="250"/></g>
    <rect x="452" y="262" width="121" height="154" fill="none" stroke="var(--sig)" stroke-dasharray="4 3"/>
    <text x="186" y="196" text-anchor="middle">Sidechain, detector,</text>
    <text x="186" y="212" text-anchor="middle">timing (U3, U4, C15),</text>
    <text x="186" y="228" text-anchor="middle">meter drivers U9, U10</text>
    <text x="364" y="196" text-anchor="middle">Gain cell:</text>
    <text x="364" y="212" text-anchor="middle">Q1&#8211;Q9 grouped,</text>
    <text x="364" y="228" text-anchor="middle">steering ref (U6)</text>
    <text x="512" y="118" text-anchor="middle">Input and</text>
    <text x="512" y="134" text-anchor="middle">output amps</text>
    <text x="512" y="150" text-anchor="middle">U1, U2, U5</text>
    <text x="512" y="330" text-anchor="middle">Power entry</text>
    <text x="512" y="346" text-anchor="middle">R50/51, D8/9,</text>
    <text x="512" y="362" text-anchor="middle">C16/17, &#8722;5V1</text>
  </g>
  <g fill="var(--sig)">{fingers}</g>
  <g font-size="10" fill="var(--sig)">{labels}</g>
  <line x1="0" y1="440" x2="609.4" y2="440" stroke="var(--sig)" marker-start="url(#arz)" marker-end="url(#arz)"/>
  <text x="304" y="456" text-anchor="middle" font-size="12" fill="var(--sig)">152.35 overall (144.35 to the shoulder)</text>
  <line x1="-24" y1="0" x2="-24" y2="420" stroke="var(--sig)" marker-start="url(#arz)" marker-end="url(#arz)"/>
  <text x="-30" y="210" text-anchor="middle" font-size="12" fill="var(--sig)" transform="rotate(-90 -30 210)">105.0</text>
  <text x="0" y="-14" font-size="12" fill="var(--ink-3)">&#8592; faceplate side</text>
  <text x="577" y="-14" font-size="12" fill="var(--ink-3)" text-anchor="end">rack socket side &#8594;</text>
  </g></svg></div>
  <figcaption><span>Suggested zones for the compressor, to scale on the template outline. Audio
  flows in and out at the connector and the controls are at the far end, so keep the audio
  amps near the fingers and send only slow control signals to the front.</span></figcaption>
</figure>"""


PAGES = {}

PAGES['index.html'] = ("Where the board is", f"""
<p class="eyebrow">PCB layout guide</p>
<h1>Laying out a 500-series board in KiCad</h1>
<p class="lede">A working order for turning a finished schematic into a two-layer card that
plugs into a 500-series rack. The examples use the compressor board as it stands, but every
step applies to the equaliser and preamp too.</p>

<div class="flow">
  <b>set up rules</b><i>&rarr;</i><b class="a">lock mechanics</b><i>&rarr;</i>
  <b>place</b><i>&rarr;</i><b>plan grounds</b><i>&rarr;</i><b>route</b><i>&rarr;</i>
  <b>pour</b><i>&rarr;</i><b class="c">check and order</b>
</div>

<h2>Where the compressor board is now</h2>
<p>As of 1 October 2026 the <a href="{BOARD}">compressor's main board</a> is placed, routed and
poured, and a separate front board carries the panel controls. Both pass DRC with no errors;
the <a href="../compressor/boards.html">compressor's boards page</a> describes them. The steps
in this guide are the ones it went through.</p>
<p>This guide was first written against the board as it stood on 28 September, with all 166
footprints spread roughly across the card and no tracks. These were the three things that had
to be fixed before placing, and how each was settled: the power nets moved to their own net
classes, the switches moved to a front board on a 2.54 mm ribbon header, and the vertical pots
went with them so their shafts point at the panel.</p>

<div class="note warn">
  <h4>Fix before placing (as it was on 28 September)</h4>
  <p><strong>The power nets are in the wrong net class.</strong> The project still carries the
  template's net class patterns, which put <code>+16V</code>, <code>-16V</code> and
  <code>AGND</code> in <em>Default</em> (0.25 mm tracks). <a href="setup.html">Setting up the
  board</a> moves them to <em>Power</em>.</p>
  <p><strong>The switch headers are 1.00 mm pitch sockets.</strong> That pitch is very hard to
  hand-solder and to find mating plugs for. Use 2.54 mm headers or a keyed 2.5 mm connector
  (JST XH, Molex KK), or move the switches onto a front board as the
  <a href="../faceplate/index.html">faceplate guide</a> suggests.</p>
  <p><strong>The pots are <em>Vertical</em> footprints</strong>, which point their shafts
  straight up out of the board. In a 500-series module the board sits at right angles to the
  faceplate, so decide how the pots reach the panel (<a href="mechanics.html">lock the
  mechanics</a>) before placing them.</p>
</div>
""")

PAGES['setup.html'] = ("Set up the board", """
<p class="eyebrow">Before placing</p>
<h1>Set up the board</h1>
<p class="lede">Do this once, before moving a single part. Everything later depends on the
rules being right, because DRC and the router use them.</p>

<ol>
  <li><strong>Open Board Setup</strong> (<em>File &rarr; Board Setup</em>). Under <em>Board
  Stackup &rarr; Physical Stackup</em>, confirm 2 copper layers and a 1.6 mm board. The card-edge
  socket expects 1.6 mm (0.062&Prime;), so don't change it.</li>
  <li><strong>Set design rules to suit a student fab.</strong> Under <em>Design Rules &rarr;
  Constraints</em>, set minimum track 0.2 mm, minimum clearance 0.2 mm, minimum via 0.6 mm with a
  0.3 mm drill, and copper to edge 0.5 mm. Every cheap fab (JLCPCB, PCBWay, Aisler) makes these
  without extra cost, and they leave margin.</li>
  <li><strong>Fix the net classes.</strong> Under <em>Net Classes</em>, keep <em>Default</em> at
  0.25 mm track and 0.2 mm clearance for signals. Set <em>Power</em> to 0.6 mm track, 0.3 mm
  clearance and 0.8 mm vias. Then delete the template's leftover patterns in the assignment
  table at the bottom, and add the ones below.</li>
  <li><strong>Set a grid.</strong> Use 1.27 mm (50 mil) for placing through-hole parts, since
  their leads sit on 2.54 mm. Drop to 0.635 mm or 0.25 mm only for routing in tight spots. Put
  the grid origin at the front bottom corner of the board; the template already uses
  (50.65, 160).</li>
</ol>
""" + table(["Pattern", "Net class"],
            [["<code>+16V*</code>, <code>-16V*</code>, <code>-5V1</code>", "Power"],
             ["<code>AGND</code>, <code>PGND</code>, <code>CHASSIS</code>", "Power"],
             ["everything else", "Default"]],
            ["", ""]) + """
<p>The <code>*</code> catches the unfiltered <code>+16V-IN</code> and <code>-16V-IN</code> nets
between the connector and R50/R51.</p>
""")

PAGES['mechanics.html'] = ("Lock the mechanics", """
<p class="eyebrow">Before placing</p>
<h1>Lock the mechanics first</h1>
<p class="lede">A 500-series card has three fixed things: the outline, the edge connector, and
whatever has to line up with the faceplate. Place and lock those before any circuitry, because
every other part fits around them.</p>
""" + zones() + """
<ol>
  <li><strong>Keep the template outline.</strong> The <code>Edge.Cuts</code> shape is the card
  and its finger tab. Don't redraw it. Its notes on <code>Dwgs.User</code> mark where to cut the
  front edge for an L-bracket, and where there's no room between the board and the panel. Turn
  that layer on while you work.</li>
  <li><strong>Lock J1.</strong> The edge connector footprint must stay exactly where the template
  put it (centre at 198.5, 98.9 on the compressor board). Select it and press <kbd>L</kbd> to
  lock it, so it can't be nudged by accident.</li>
  <li><strong>Decide how the controls reach the panel.</strong> The
  <a href="../faceplate/mounting.html">faceplate guide</a> covers the options. In short: either
  right-angle pots and switches sit on this board's front edge, or a small front board carries
  them and plugs into this one, or they mount on the panel and wire back to headers. For the
  compressor's two meters, two toggles, a button and five pots across four columns, a front
  board is the cleanest. That leaves only a header and the trimmers on the front edge of this
  board. The meter drivers U9 and U10 and their LEDs can then move to the front board too,
  which frees space in the zone map above.</li>
  <li><strong>Mark the keep-outs.</strong> Draw a <em>Rule Area</em> (<em>Place &rarr; Rule
  Area</em>) across the top and bottom 3 mm of the card, set to keep out footprints and tracks.
  Many racks have card guides that grip those edges. Draw another over the L-bracket strip at
  the front if you use one.</li>
  <li><strong>Know the height limit.</strong> The module slot is 38.1 mm wide and the board is
  not on its centreline, so the component side has more room than the solder side. Keep parts
  under about 15 mm tall on top, and leads trimmed to 2 mm underneath, until you've checked the
  offset in your rack. The 6.3 mm electrolytics and DIP sockets are fine; lay anything taller on
  its side.</li>
</ol>
""")

PAGES['placement.html'] = ("Place the parts", """
<p class="eyebrow">Layout</p>
<h1>Place the parts</h1>
<p class="lede">Placement is most of the work. A well-placed board nearly routes itself, and a
badly placed one can't be rescued by routing.</p>

<ol>
  <li><strong>Move by section, using cross-probing.</strong> Open the schematic and the board
  side by side. Drag a box around one section in the schematic, the input stage say, and the
  same parts highlight on the board. Switch to the board and press <kbd>M</kbd> to move the
  whole selected group to its zone. Repeat for each section. The compressor's single schematic
  keeps its section labels (<em>STEERING REFERENCE</em>, <em>GAIN-REDUCTION METER</em> and so
  on), which makes this quick.</li>
  <li><strong>Follow the signal.</strong> Lay each section out in the order the schematic reads,
  left to right, so connections are short and don't cross. Watch the ratsnest (the thin
  lines): if lots of them cross, rotate or swap parts until they untangle.</li>
  <li><strong>Put the power entry by pins 12 to 14.</strong> R50/R51, the reverse diodes D8/D9
  and the 100 &micro;F bulk capacitors C16/C17 go right next to the fingers, so supply noise
  from the rack is filtered before it spreads.</li>
  <li><strong>Put each 100 nF decoupling capacitor against its chip,</strong> one from pin 8 to
  ground and one from pin 4 to ground, within a few millimetres.</li>
  <li><strong>Keep matched parts together.</strong> The compressor README says Q1/Q2 are a
  matched pair and Q6 to Q9 a matched quad, glued together so they share a temperature. Place
  them touching, flat faces together and in the same orientation, away from anything warm such
  as the 10 &Omega; supply resistors and the LED drivers.</li>
  <li><strong>Keep the timing node short and clean.</strong> C15 and the U4 inputs sit on a
  very high-impedance node, where leakage changes the release time. Put them next to each
  other, away from the board edge, and clean the flux off after soldering.</li>
  <li><strong>Keep trimmers reachable.</strong> RV1, RV7 and RV8 are Bourns 3296W trimmers.
  Place them where a screwdriver can reach them with the module out of the rack and the front
  board fitted, and orient them the same way.</li>
  <li><strong>Tidy up.</strong> Align rows of resistors (<em>right-click &rarr;
  Align/Distribute</em>), keep all ICs facing the same way with pin 1 in the same corner, and
  space parts so a soldering iron fits between them.</li>
</ol>
""")

PAGES['grounds.html'] = ("Plan the grounds", """
<p class="eyebrow">Layout</p>
<h1>Plan the grounds before routing</h1>
<p class="lede">The compressor has three ground nets on purpose. Keeping them separate on
copper is what makes that worthwhile.</p>
""" + table(["Net", "Comes from", "How to lay it out"],
            [["<code>AGND</code>", "J1 pin 5",
              "The audio reference. Make it a copper pour covering most of the bottom layer, so "
              "every part has a short, low-impedance path to it."],
             ["<code>PGND</code>", "J1 pin 13",
              "The rack's power return. It joins AGND at one point only, through R48 (0 &Omega;). "
              "Place R48 near the power entry and route PGND as a single track from pin 13 to it, "
              "with no pour."],
             ["<code>CHASSIS</code>", "J1 pin 1",
              "The metalwork. It joins AGND through R52 (100 &Omega;) and C18 (10 nF). Keep both "
              "next to pin 1. Chassis also reaches the faceplate through pot bushings and the "
              "bracket."]],
            ["r", "", ""]) + """
<div class="note">
  <h4>Meter current</h4>
  <p>The two LM3914 drivers switch up to 20 LEDs on and off, which draws pulses of
  current. Give U9, U10, the LEDs and C38 their own ground track back towards the power entry,
  and join it to the main pour there. If those pulses flow through the pour under the audio
  stages, they can be heard as a faint buzz that follows the meters.</p>
</div>
""")

PAGES['routing.html'] = ("Route", """
<p class="eyebrow">Layout</p>
<h1>Route</h1>
<p class="lede">Route in order of importance. Use the <em>Interactive Router</em> (<kbd>X</kbd>)
in <em>Walk around</em> mode, and route by hand. The autorouter makes a mess of audio
boards.</p>

<ol>
  <li><strong>Power first.</strong> Run <code>+16V</code> and <code>-16V</code> on the top layer
  from the power entry to each chip in 0.6 mm tracks; the Power net class does this
  automatically. Pass each chip's decoupling capacitor on the way to its pin, so the capacitor is
  between the supply and the chip.</li>
  <li><strong>Then the balanced input and output.</strong> Route IN+ and IN&minus; together as a
  pair, the same length and side by side, from the fingers to R5/R6. Do the same for OUT+ and
  OUT&minus;. A balanced pair only rejects noise if both legs pick up the same noise.</li>
  <li><strong>Then the audio path through the gain cell,</strong> keeping each connection short.
  Avoid running audio tracks parallel to the meter or LED tracks.</li>
  <li><strong>Then control and sidechain,</strong> which are slow signals and can take the long
  runs to the front of the board.</li>
  <li><strong>Stay mostly on top.</strong> Every track on the bottom layer cuts the ground pour.
  Keep bottom tracks short, a few jumps under a row of parts, and never let them cut the pour
  into islands.</li>
  <li><strong>Use vias freely for ground.</strong> Wherever a ground pin on top needs to reach
  the pour, drop a via right next to it.</li>
</ol>
""")

PAGES['pours.html'] = ("Pours and edge fingers", """
<p class="eyebrow">Layout</p>
<h1>Pours and edge fingers</h1>
<p class="lede">A solid ground pour on the bottom, and a clean finger tab that the rack socket
can grip for years.</p>

<ol>
  <li><strong>Add the ground pour.</strong> <em>Place &rarr; Add Filled Zone</em> on
  <code>B.Cu</code>, net <code>AGND</code>, following the board outline. Set clearance to 0.3 mm
  and leave thermal relief on for through-hole pads, which makes them solderable. Press
  <kbd>B</kbd> to fill.</li>
  <li><strong>Optionally, pour the top as well.</strong> A second AGND zone on <code>F.Cu</code>
  fills the gaps between tracks. If you add it, stitch the two together with vias every 10 mm or
  so, and set the zone to remove floating islands.</li>
  <li><strong>Keep copper off the finger tab.</strong> Draw a rule area that keeps out zones over
  the tab, beyond the shoulder at x &asymp; 195, so only the fingers themselves have copper
  there.</li>
  <li><strong>Plate the fingers properly.</strong> The footprint already has the fingers as pads
  with no solder mask. When ordering, choose ENIG or hard gold plating and a 45&deg; bevel on the
  finger edge. HASL, the cheapest finish, leaves the fingers lumpy and wears the rack
  socket.</li>
</ol>
""")

PAGES['checks.html'] = ("Silkscreen and checks", """
<p class="eyebrow">Finishing</p>
<h1>Silkscreen and checks</h1>
<p class="lede">Label the board for whoever solders it, then make KiCad prove the board and the
schematic agree.</p>

<h2>Silkscreen</h2>
<ul>
  <li>Keep every reference designator visible and next to its part, the same way up where you
  can. Whoever solders the board uses these alongside the BOM.</li>
  <li>Mark polarity on every electrolytic, diode and LED, and pin 1 on every IC and header. The
  standard footprints do this, so don't delete those marks.</li>
  <li>Label the switch and front-board headers with what each pin is (<em>BYP</em>,
  <em>HPF</em>, <em>KEY</em>, <em>LINK</em>).</li>
  <li>Add the module name, board revision, date and team names in a clear area.
  <em>UTS 500 COMP rev A 2026</em> is enough. Put it on the bottom if the top is crowded.</li>
  <li>Keep silkscreen off pads. DRC flags this, and fabs clip it anyway.</li>
</ul>

<h2>Checks</h2>
<ol>
  <li><strong>Update from the schematic once more</strong> (<kbd>F8</kbd>) and confirm nothing
  changes. If it does, the board and schematic had drifted.</li>
  <li><strong>Run DRC</strong> (<em>Inspect &rarr; Design Rules Checker</em>) with <em>Test for
  parity between PCB and schematic</em> ticked. Aim for zero errors, and treat each warning as a
  question.</li>
  <li><strong>Look for unrouted nets.</strong> The DRC result lists them, and the status bar at
  the bottom of the board editor shows how many connections are still unrouted.</li>
  <li><strong>Open the 3D viewer</strong> (<kbd>Alt</kbd>+<kbd>3</kbd>) and look for parts that
  clash, face the wrong way or overhang the edge. Export a STEP for the faceplate work, as the
  <a href="../mechanical/pcb.html">mechanical design guide</a> describes.</li>
  <li><strong>Print it 1:1</strong> (<em>File &rarr; Print</em>, scale 1, top copper and
  silkscreen). Lay real parts on the paper, especially pots, switches, DIP sockets and the
  electrolytics, to catch footprints that are the wrong size. Hold the print against the
  faceplate drawing to check the controls line up.</li>
</ol>
""")

PAGES['fab.html'] = ("Send it to a fab", """
<p class="eyebrow">Finishing</p>
<h1>Send it to a fab</h1>
<p class="lede">Gerbers and a drill file are all a board house needs.</p>

<ol>
  <li><strong>Plot Gerbers.</strong> <em>File &rarr; Fabrication Outputs &rarr; Gerbers</em>.
  Include F.Cu, B.Cu, F.Silkscreen, B.Silkscreen, F.Mask, B.Mask and Edge.Cuts. Tick <em>Use
  Protel filename extensions</em> if the fab asks for it.</li>
  <li><strong>Generate the drill file</strong> from the same dialog (<em>Generate Drill
  Files</em>): Excellon format, millimetres, PTH and NPTH in one file.</li>
  <li><strong>Zip the folder and upload it.</strong> Every fab shows a rendered preview. Check
  the outline, the finger tab and the holes before paying.</li>
  <li><strong>Choose the options:</strong> 2 layers, 1.6 mm FR-4, 1 oz copper, ENIG finish or hard
  gold on the fingers, and gold fingers with a 45&deg; bevel. Five boards cost little more than
  two, and you'll want spares.</li>
</ol>

<p>The same outputs from a terminal:</p>
<pre><code>kicad-cli pcb export gerbers -o fab/ compressor_with_pcb.kicad_pcb
kicad-cli pcb export drill --format excellon -u mm -o fab/ compressor_with_pcb.kicad_pcb</code></pre>
""")

"""Faceplate fit guide - page content.

Shared by all three modules: how the faceplate, the controls, the circuit boards and the
500-series rack meet, and how to design each joint. Complements the mechanical design guide,
which covers modelling and drawings in Fusion 360.

Hole and bushing sizes are typical values; the compressor figures come from its panel/
folder and kicad_withpcb/ board as of 28 September 2026.
"""
from shell import table

VPR = 'https://medias.audiofanzine.com/files/api-vpr-500-spec-479213.pdf'
GDIY_OFFSET = 'https://groupdiy.com/threads/500-series-dimensions-pcb-offset.89219/'
ORG = 'https://github.com/UTS-500-Series'

NAV = [("Start here", [("index.html", "01", "How a module fits")]),
       ("Decide", [("mounting.html", "02", "How controls mount"),
                   ("positions.html", "03", "Get the positions right")]),
       ("Build", [("front-board.html", "04", "Design the front board"),
                  ("bracket.html", "05", "Bracket and fixings"),
                  ("holes.html", "06", "Holes and clearances")]),
       ("Finish", [("rack.html", "07", "Fit the rack"),
                   ("make.html", "08", "Make the panel"),
                   ("compressor.html", "09", "Compressor notes"),
                   ("checklist.html", "10", "Before ordering")])]


def stack():
    """Top-down view of one module at roughly 3 px per mm: knob, panel, pot, front board,
    connector, main board and rack socket."""
    return """<figure>
  <div style="background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px;overflow-x:auto">
  <svg viewBox="0 0 640 620" role="img" style="width:100%;min-width:480px;max-width:640px;height:auto;display:block;margin:0 auto"
       aria-label="Top-down view of a 500-series module showing knob, faceplate, front board, main board, the connector between the boards and the rack socket">
  <defs><marker id="ars" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="var(--sig)"/></marker></defs>
  <g font-family="var(--mono)" transform="translate(200 90)">
  <rect x="39" y="-45" width="36" height="45" fill="var(--surface)" stroke="var(--ink)" stroke-width="1.2"/>
  <text x="-12" y="-20" text-anchor="end" font-size="12" fill="var(--ink)">knob</text>
  <rect x="0" y="0" width="114.3" height="9.5" fill="var(--surface-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="-12" y="8" text-anchor="end" font-size="12" fill="var(--ink)">faceplate 3.18</text>
  <rect x="48" y="0" width="18" height="9.5" fill="none" stroke="var(--sig)" stroke-dasharray="2 2"/>
  <rect x="30" y="9.5" width="54" height="27" fill="var(--warn-bg)" stroke="var(--sig)" stroke-width="1.2"/>
  <text x="57" y="27" text-anchor="middle" font-size="10" fill="var(--sig)">pot</text>
  <rect x="6" y="36.5" width="102" height="4.8" fill="var(--ctl)"/>
  <text x="124" y="42" font-size="12" fill="var(--ctl)">front board (parallel to panel)</text>
  <rect x="24" y="41.3" width="12" height="16" fill="var(--surface)" stroke="var(--ink)"/>
  <text x="124" y="60" font-size="12" fill="var(--ink)">connector joins the two boards</text>
  <rect x="30" y="57.3" width="4.8" height="405" fill="var(--ctl)"/>
  <text x="48" y="250" font-size="12" fill="var(--ctl)">main board, component side &#8594;</text>
  <text x="48" y="266" font-size="12" fill="var(--ink-3)">(parts sit in this gap)</text>
  <rect x="26" y="440" width="13" height="22" fill="var(--sig)"/>
  <rect x="16" y="436" width="33" height="44" fill="none" stroke="var(--ink)" stroke-width="1.2" stroke-dasharray="5 3"/>
  <text x="60" y="462" font-size="12" fill="var(--ink)">rack edge socket</text>
  <line x1="0" y1="500" x2="114.3" y2="500" stroke="var(--sig)" marker-start="url(#ars)" marker-end="url(#ars)"/>
  <text x="57" y="518" text-anchor="middle" font-size="12" fill="var(--sig)">38.10 slot width</text>
  <line x1="57.15" y1="-60" x2="57.15" y2="490" stroke="var(--ink-3)" stroke-width=".8" stroke-dasharray="10 3 2 3"/>
  <text x="57" y="-66" text-anchor="middle" font-size="11" fill="var(--ink-3)">panel centreline</text>
  <line x1="32.4" y1="120" x2="57.15" y2="120" stroke="var(--sig)" marker-start="url(#ars)" marker-end="url(#ars)"/>
  <text x="-12" y="118" text-anchor="end" font-size="12" fill="var(--sig)">board offset:</text>
  <text x="-12" y="133" text-anchor="end" font-size="12" fill="var(--sig)">confirm in your rack</text>
  <line x1="-30" y1="9.5" x2="-30" y2="462" stroke="var(--sig)" marker-start="url(#ars)" marker-end="url(#ars)"/>
  <text x="-36" y="236" text-anchor="middle" font-size="12" fill="var(--sig)" transform="rotate(-90 -36 236)">150.83 behind the panel</text>
  </g></svg></div>
  <figcaption><span>Looking down on one module, roughly to scale. The main board runs back from
  the front board to the rack socket, off to one side of the panel centreline.</span></figcaption>
</figure>"""


PAGES = {}

PAGES['index.html'] = ("How a module fits", """
<p class="eyebrow">Faceplate fit guide</p>
<h1>A faceplate that fits the board and the rack</h1>
<p class="lede">How the faceplate, the controls, the circuit board and the 500-series rack
meet, and how to design each joint so the module goes together on the first try.</p>

<div class="note good">
  <h4>Recommendation</h4>
  <p><strong>For any module with more than one column of controls, put the pots, switches and
  LEDs on a small front board that sits flat behind the faceplate, and join it to the main board
  with a connector.</strong> The pot nuts hold the front board to the panel, the main board
  plugs into the front board, and the hole positions come straight from the front board's
  layout. The compressor needs this, because its controls sit in four columns.</p>
  <p>A module with a single column of pots can skip the front board and use right-angle pots on
  the main board's front edge.</p>
</div>
""" + stack() + """
<p>Four pieces meet here: the faceplate, the controls, the main board and the rack. The rack
fixes two of the positions for you. The faceplate screws to the rack rails through its two
countersunk holes, and the card-edge fingers plug into a socket at the back. Everything in
between has to line up with those two points.</p>
<p>Modelling the parts in Fusion 360 and producing drawings is covered by the
<a href="../mechanical/index.html">mechanical design guide</a>. Laying out the main board is
covered by the <a href="../layout/index.html">PCB layout guide</a>.</p>
""")

PAGES['mounting.html'] = ("How controls mount", """
<p class="eyebrow">Decide</p>
<h1>Choose how the controls mount</h1>
<p class="lede">Three ways to get a pot shaft through the panel, and when each one makes
sense.</p>
""" + table(["Approach", "How it works", "Good for", "Watch out for"],
            [["<strong>Front board</strong> (use)",
              "A small board parallel to the panel carries vertical pots, PCB-mount toggles and "
              "LEDs. Pot nuts clamp it to the panel. A connector or ribbon cable joins it to the "
              "main board.",
              "Several columns of controls, meters, anything dense. Hole positions come straight "
              "from the KiCad layout.",
              "Two boards to design and order. The joint between them needs planning."],
             ["<strong>Right-angle parts on the main board</strong>",
              "Pots and switches with bent legs (KiCad's <em>Horizontal</em> footprints) sit "
              "along the main board's front edge, shafts pointing forward through the panel. An "
              "L-bracket joins board and panel.",
              "One column of controls on a single line. Simple modules like a preamp.",
              "Every shaft sits at the same distance from the board, so all controls end up in "
              "one column. Shaft height has to match the board offset."],
             ["<strong>Panel-mounted, wired</strong> (prototype)",
              "Controls bolt to the panel and wires run to headers on the main board.",
              "A first prototype, or when parts arrive before the boards.",
              "Lots of hand wiring, easy to cross two wires, and long wires on audio-path pots "
              "can pick up hum."]],
            ["r", "", "", ""]) + """
<p>The compressor's pot footprints (Alps RK09K <em>Vertical</em>) are the right type for a
front board, and Altronics' 9 mm pots share them. Its toggles are PCB-mount Salecom mini
toggles on the same front board.</p>
""")

PAGES['positions.html'] = ("Get the positions right", f"""
<p class="eyebrow">Decide</p>
<h1>Get the positions right</h1>
<p class="lede">Every control is defined twice: as a hole in the panel and as a footprint on a
board. Only one of those can be the master. Make the KiCad layout the master, and derive the
panel holes from it.</p>

<ol>
  <li><strong>Use one coordinate system.</strong> Measure panel positions from the panel's
  top-left corner, x to the right and y down, in millimetres. The compressor's
  <code>panel/README.md</code> already uses this, and so do the drawing sheets in the mechanical
  guide.</li>
  <li><strong>Draw the panel into the front board layout.</strong> In the front board's KiCad
  file, draw the 38.10 &times; 133.35 panel outline on <code>User.Drawings</code> with its
  top-left corner on a grid point, and set that point as the grid origin (<em>Place &rarr; Grid
  Origin</em>). The board editor's coordinates now read exactly like the panel's.</li>
  <li><strong>Place each pot, switch and LED on its panel position.</strong> Press <kbd>E</kbd>
  on the footprint and type its position. Make sure the position means the shaft centre: for
  most pot footprints the origin is pin 1, not the shaft, so check the footprint and offset if
  needed.</li>
  <li><strong>Export the holes back out.</strong> When the layout is final, plot
  <code>User.Drawings</code> and the pot and switch courtyards as DXF (<em>File &rarr; Plot
  &rarr; DXF</em>) and use that as the panel sketch.</li>
</ol>

<div class="note warn">
  <h4>The one number to measure</h4>
  <p>Published figures disagree on how far the main board sits from the panel centreline: both
  11.13 mm and 7.92 mm appear on <a href="{GDIY_OFFSET}">GroupDIY</a>. A front board makes this
  matter less, because the front board takes its position from the panel and the main board's
  offset only has to match the connector between the boards. Still, check it in the rack you'll
  test in before ordering the main board: measure from the centre of a rail mounting hole to the
  edge socket's slot.</p>
</div>
""")

PAGES['front-board.html'] = ("Design the front board", """
<p class="eyebrow">Build</p>
<h1>Design the front board</h1>
<p class="lede">A small second board that carries everything the user touches or looks at.</p>

<ol>
  <li><strong>Make it a separate KiCad project,</strong> for example
  <code>compressor_front</code>. Its schematic holds the pots, switches, LEDs and one connector.
  Keep the connector's pin order identical to the matching connector on the main board, and name
  the nets the same in both schematics.</li>
  <li><strong>Size the outline</strong> to about 34 &times; 110 mm. It must clear the panel edges
  (the panel is 37.8 mm wide once trimmed) and stay about 10 mm clear of each mounting hole, so
  the countersunk screw heads and rack rails don't hit it.</li>
  <li><strong>Move the meters onto it.</strong> The two LED bargraphs need 14 LED lines between
  them. With U9, U10 and their resistors on the front board, only the two meter signals, power
  and ground cross between the boards. The same applies to anything that exists only to drive
  the panel.</li>
  <li><strong>Choose the board-to-board joint.</strong> For a prototype, a short 2.54 mm IDC
  ribbon cable forgives small position errors. For the finished module, a right-angle 2.54 mm
  header on the main board's front edge plugging into a straight socket on the front board makes
  a solid, wire-free L shape. Either way, keep the pin count down by moving panel-only circuitry
  forward, and put a ground pin between audio lines.</li>
  <li><strong>Set the LED height.</strong> The LEDs must reach the panel. Use LED spacers
  (plastic standoffs sold by LED size) cut to the gap between the front board and the panel, or
  flat-top LEDs that sit just behind the hole. Put the height in the BOM so whoever builds it
  gets it right.</li>
  <li><strong>Use PCB-mount switches.</strong> Mini toggles and the bypass button come in
  versions with PCB pins and a threaded bushing. The bushing goes through the panel and its nut
  helps clamp the board, like the pots.</li>
</ol>
""")

PAGES['bracket.html'] = ("Bracket and fixings", """
<p class="eyebrow">Build</p>
<h1>Bracket and fixings</h1>
<p class="lede">With a front board, the pot and switch nuts carry the panel. The main board
also needs a solid link to the panel, because people pull modules out of racks by their
knobs.</p>

<ul>
  <li><strong>L-bracket.</strong> A piece of aluminium angle, about 10 &times; 10 &times; 1.5 mm,
  screwed to the back of the panel and to the main board. The template board's
  <code>Dwgs.User</code> layer shows two cut lines for this: one for a bracket in direct contact
  with the board, and one leaving room for screws from the front.</li>
  <li><strong>Hidden fixings.</strong> To keep screw heads off the front of the panel, use
  press-in threaded studs (PEM) on the back of the panel, or tap blind holes if the panel is 3 mm
  or thicker.</li>
  <li><strong>Front board standoffs.</strong> If the pots alone don't hold the front board
  firmly, add two M3 standoffs between it and the panel, using the same hidden fixings.</li>
  <li><strong>Rack screws.</strong> The two countersunk holes take the rack's own screws. Leave at
  least 3 mm between the screw head (&Oslash;5.72) and any knob skirt, so a screwdriver can reach
  it.</li>
</ul>
""")

PAGES['holes.html'] = ("Holes and clearances", """
<p class="eyebrow">Build</p>
<h1>Holes and clearances</h1>
<p class="lede">Size every hole from the datasheet of the part you actually buy. The table gives
typical values to start from.</p>
""" + table(["Part", "Typical bushing", "Panel hole", "Notes"],
            [["9 mm pot (Alps RK09K)", "M7 &times; 0.75", "&Oslash;7.2 to 7.5",
              "Has a small anti-rotation tab. Drill a &Oslash;2.5 hole for it where the datasheet "
              "says, or snap the tab off."],
             ["Dual-concentric pot", "3/8&Prime; (9.53)", "&Oslash;9.8",
              "Bushing size varies by maker. Needs its own six-pin footprint."],
             ["Mini toggle", "1/4&Prime; (6.35) or M6", "&Oslash;6.5 to 6.8",
              "Check the bushing thread before drilling."],
             ["2 mm LED", "none", "&Oslash;2.2", "Flat-top parts sit flush behind the hole."],
             ["3 mm LED", "none", "&Oslash;3.2", "Or use a panel bezel clip sized for it."],
             ["Rack mounting", "none", "&Oslash;3.18, csk 82&deg; to &Oslash;5.72",
              "From the 500-series spec, countersunk on the front."]],
            ["r", "", "", ""]) + """
<div class="note warn">
  <h4>Check the bushing length against the panel</h4>
  <p>The compressor's Salecom S1315 and S1350 mini toggles take a &Oslash;6.5 hole, and their
  8.9 mm bushing leaves plenty of thread through a 3.18 mm panel. Its 9 mm pots are the tight
  one: a 5 mm bushing leaves under 2 mm, so counterbore the pot holes from the back or use a
  thinner panel. Sub-miniature toggles are worse still, with bushings around 4 mm. Confirm every
  size against the actual parts before cutting.</p>
</div>
""")

PAGES['rack.html'] = ("Fit the rack", f"""
<p class="eyebrow">Finish</p>
<h1>Fit the rack</h1>
<p class="lede">The rack sets the width, the depth and the ground. Numbers are from the
<a href="{VPR}">VPR Alliance 500-series specification</a>.</p>

<ul>
  <li><strong>Trim the width.</strong> Make the panel 37.6 to 37.8 mm wide rather than the
  nominal 38.10, so it slides in beside its neighbours after finishing. 132.6 mm is a common
  practical height.</li>
  <li><strong>Keep inside the slot.</strong> Nothing on either board, including knobs, may be
  wider than the panel. The module next door is right there.</li>
  <li><strong>Keep the card edges clear.</strong> Some racks have card guides that grip the main
  board's top and bottom edges. Keep about 3 mm there free of parts and copper.</li>
  <li><strong>Depth is set by the board.</strong> The fingers must reach the socket, 150.83 mm
  (5.938&Prime;) behind the panel. The template board's length already gives this as long as the
  main board's front edge sits where the template expects, so don't move the bracket line or
  shorten the board.</li>
  <li><strong>Ground the panel.</strong> The panel should connect to <code>CHASSIS</code> (J1 pin
  1), which the board ties to audio ground through R52 and C18. Anodising is an insulator, so a
  bare spot is needed: mask the anodise where the bracket or a ground lug under a pot nut
  touches the panel, and run that to a <code>CHASSIS</code> pad.</li>
</ul>
""")

PAGES['make.html'] = ("Make the panel", """
<p class="eyebrow">Finish</p>
<h1>Make the panel</h1>
<p class="lede">Three ways to get a physical panel, from a quick fit check to the real
thing.</p>
""" + table(["Method", "What you send", "Notes"],
            [["<strong>Machined aluminium</strong>",
              "Panel sketch as DXF (holes and outline only) plus a PDF drawing",
              "The real thing: 3 mm stock, anodised, legends engraved or UV printed. The "
              '<a href="../mechanical/faceplate.html">mechanical guide</a> covers modelling and '
              "the drawing."],
             ["<strong>Panel as a PCB</strong>",
              "Gerbers from a KiCad board that is just the panel",
              "Cheapest and fastest. Outline on <code>Edge.Cuts</code>, holes as NPTH pads, "
              "legends in silkscreen, black mask with white print. Thinner than spec (1.6 to "
              "2.0 mm), which is fine for testing but flexes more. Aluminium-core boards are "
              "stiffer."],
             ["<strong>3D print or laser-cut acrylic</strong>", "STL or DXF",
              "A fit check only. Make one before ordering metal to catch misplaced holes."]],
            ["r", "", ""]) + """
<p>Whichever you choose, generate it from the front board layout rather than retyping
coordinates. The compressor does this: its front board is the master, and
<code>panel/make_panel.py</code> copies its hole positions from the board.</p>
""")

PAGES['compressor.html'] = ("Compressor notes", f"""
<p class="eyebrow">Finish</p>
<h1>Compressor notes</h1>
<p class="lede">How the <a href="{ORG}/Compressor">compressor</a> followed this guide, as of
2 October 2026. Its <a href="../compressor/boards.html">boards page</a> has the full
description.</p>

<ul>
  <li><strong>Layout:</strong> the <code>toggle</code> layout, five single RK09K pots with four
  toggles beside them. The dual-concentric and pull-switch layouts were dropped.</li>
  <li><strong>Front board:</strong> 35 &times; 110 mm, carrying the pots, the Salecom S1315 and
  S1350 toggles, both meters and their LM3914/LM3915 drivers. It sits about 10.6 mm behind the
  panel with the pot bodies resting on it, held only by the bushing nuts.</li>
  <li><strong>Master:</strong> the panel and its holes are drawn on the front board's
  User.Drawings layer with the origin on the panel's top-left corner, and
  <code>panel/make_panel.py</code> takes its positions from there. The meter columns ended up
  9.9 mm apart so the drivers fit either side.</li>
  <li><strong>Connector:</strong> the old 1.00 mm switch sockets are gone. A 30-way ribbon runs
  from a shrouded 2 &times; 15 header on the main board to a plain one on the front board, so
  put the stripe on pin 1 at both ends.</li>
  <li><strong>Main board:</strong> front edge set back 24 mm, fixed to the panel with an L-bracket
  on two M3 holes. One of them is plated to CHASSIS, which grounds the panel.</li>
  <li><strong>Still open:</strong> the panel thickness for the pots' short bushings and the
  ribbon length in a real rack.</li>
</ul>
""")

PAGES['checklist.html'] = ("Before ordering", """
<p class="eyebrow">Finish</p>
<h1>Before ordering</h1>
<p class="lede">Six checks that catch nearly every fit problem before it costs money.</p>

<ol>
  <li>Hole sizes checked against the datasheets of the parts in the BOM.</li>
  <li>Front board printed 1:1 and laid over the panel drawing, with every hole centre on its
  part.</li>
  <li>Main board and front board connectors have the same pin order and net names.</li>
  <li>3D view of both boards together: no clashes, nothing wider than the panel, and the LEDs
  reach the panel.</li>
  <li>Board offset and depth checked in the actual rack.</li>
  <li>A printed or laser-cut test panel fitted before ordering metal.</li>
</ol>
""")

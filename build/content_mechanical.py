"""Mechanical design guide - page content.

Shared by all three modules: how to take each KiCad board into Fusion 360 as a 3D model,
design a 500-series faceplate round it, and export dimensioned outline drawings. The
drawing style follows a DiGiCo outline drawing the team uses as a reference.

Figures come from the VPR Alliance 500-series drawing and the compressor's panel README.
Fusion menu names are for the current release and move occasionally.
"""
from shell import table

VPR = 'https://medias.audiofanzine.com/files/api-vpr-500-spec-479213.pdf'
GDIY = 'https://groupdiy.com/threads/groupdiy-500-series-mechanical-specifications.89790/'
GDIY_OFFSET = 'https://groupdiy.com/threads/500-series-dimensions-pcb-offset.89219/'
ORG = 'https://github.com/UTS-500-Series'

NAV = [("Start here", [("index.html", "01", "Which software")]),
       ("The format", [("dimensions.html", "02", "Numbers to design to")]),
       ("Workflow", [("pcb.html", "03", "PCB into Fusion"),
                     ("faceplate.html", "04", "Model the faceplate"),
                     ("assembly.html", "05", "Assemble and check"),
                     ("drawings.html", "06", "Export drawings")]),
       ("Practical", [("modules.html", "07", "Per-module notes")])]


def envelope():
    """Faceplate front view at 3 px per mm, plus a schematic side view. Inline so it
    follows the site's theme: amber for dimensions, teal for the board."""
    return """<figure>
  <div style="background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px;overflow-x:auto">
  <svg viewBox="0 0 640 470" role="img" style="width:100%;min-width:520px;height:auto;display:block"
       aria-label="Faceplate front view, 38.10 by 133.35 mm with two countersunk mounting holes 125.43 mm apart, and a side view of the PCB behind the panel">
  <defs><marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="var(--sig)"/></marker></defs>
  <g font-family="var(--mono)">
  <text x="117" y="462" text-anchor="middle" font-size="12" fill="var(--ink-3)">FRONT VIEW</text>
  <rect x="60" y="40" width="114.3" height="400" fill="var(--surface-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <line x1="117.15" y1="30" x2="117.15" y2="450" stroke="var(--ink-3)" stroke-width=".8" stroke-dasharray="10 3 2 3"/>
  <g stroke="var(--ink)"><circle cx="117.15" cy="51.9" r="8.6" fill="none"/><circle cx="117.15" cy="51.9" r="4.8" fill="var(--surface)" stroke-width="1.2"/>
  <circle cx="117.15" cy="428.1" r="8.6" fill="none"/><circle cx="117.15" cy="428.1" r="4.8" fill="var(--surface)" stroke-width="1.2"/></g>
  <g fill="none" stroke="var(--ink-3)" stroke-dasharray="3 2"><circle cx="117.15" cy="190" r="10.5"/><circle cx="117.15" cy="251" r="10.5"/><circle cx="94.5" cy="313" r="10.5"/><circle cx="139.8" cy="313" r="10.5"/><circle cx="117.15" cy="373" r="10.5"/></g>
  <text x="117" y="130" text-anchor="middle" font-size="11" fill="var(--ink-3)">controls</text>
  <text x="117" y="144" text-anchor="middle" font-size="11" fill="var(--ink-3)">per module</text>
  <g stroke="var(--sig)" stroke-width=".7"><line x1="60" y1="40" x2="60" y2="14"/><line x1="174.3" y1="40" x2="174.3" y2="14"/>
  <line x1="60" y1="40" x2="22" y2="40"/><line x1="60" y1="440" x2="22" y2="440"/>
  <line x1="126" y1="51.9" x2="222" y2="51.9"/><line x1="126" y1="428.1" x2="222" y2="428.1"/><line x1="126" y1="40" x2="240" y2="40"/></g>
  <g stroke="var(--sig)" stroke-width="1" marker-start="url(#ar)" marker-end="url(#ar)"><line x1="60" y1="20" x2="174.3" y2="20"/><line x1="30" y1="40" x2="30" y2="440"/><line x1="212" y1="51.9" x2="212" y2="428.1"/></g>
  <g font-size="12" fill="var(--sig)"><text x="117" y="15" text-anchor="middle">38.10</text>
  <text x="24" y="240" text-anchor="middle" transform="rotate(-90 24 240)">133.35</text>
  <text x="206" y="240" text-anchor="middle" transform="rotate(-90 206 240)">125.43</text>
  <text x="244" y="44" font-size="11">3.96</text></g>
  <text x="182" y="72" font-size="11" fill="var(--ink)">2&#215; &#216;3.18</text>
  <text x="182" y="85" font-size="11" fill="var(--ink)">csk &#216;5.72 &#215; 82&#176;</text>

  <text x="455" y="462" text-anchor="middle" font-size="12" fill="var(--ink-3)">SIDE VIEW (not to scale)</text>
  <rect x="330" y="140" width="5" height="200" fill="var(--surface-2)" stroke="var(--ink)" stroke-width="1.5"/>
  <text x="332" y="130" text-anchor="middle" font-size="11" fill="var(--ink)">panel</text>
  <rect x="335" y="160" width="220" height="158" fill="none" stroke="var(--ctl)" stroke-width="1.5"/>
  <text x="445" y="244" text-anchor="middle" font-size="12" fill="var(--ctl)">PCB 1.6 thick,</text>
  <text x="445" y="259" text-anchor="middle" font-size="12" fill="var(--ctl)">perpendicular to panel</text>
  <rect x="555" y="250" width="10" height="58" fill="var(--warn-bg)" stroke="var(--sig)" stroke-width="1.2"/>
  <g font-size="11" fill="var(--sig)"><text x="572" y="270">edge</text><text x="572" y="284">fingers</text><text x="572" y="298">15&#215;3.96</text></g>
  <g stroke="var(--ink-3)" fill="none"><rect x="315" y="190" width="15" height="14"/><rect x="315" y="260" width="15" height="14"/></g>
  <text x="308" y="232" text-anchor="end" font-size="11" fill="var(--ink-3)">knobs</text>
  <g stroke="var(--sig)" stroke-width=".7"><line x1="335" y1="340" x2="335" y2="385"/><line x1="565" y1="318" x2="565" y2="385"/></g>
  <line x1="335" y1="378" x2="565" y2="378" stroke="var(--sig)" marker-start="url(#ar)" marker-end="url(#ar)"/>
  <text x="450" y="372" text-anchor="middle" font-size="12" fill="var(--sig)">150.83 (5.938&#8243;) spec depth</text>
  </g></svg></div>
  <figcaption><span>The faceplate envelope every module shares. Control holes (dashed) differ per module. Millimetres.</span></figcaption>
</figure>"""


PAGES = {}

PAGES['index.html'] = ("Which software", f"""
<p class="eyebrow">Mechanical design guide</p>
<h1>Modelling the modules in Fusion 360</h1>
<p class="lede">How to turn each KiCad board into a 3D model, design a faceplate around it,
and export dimensioned outline drawings: third-angle views, a title block, a tolerance note
and overall dimensions.</p>

<div class="note good">
  <h4>Recommendation</h4>
  <p><strong>Keep KiCad as the master for every PCB, and use Fusion 360 on the free
  Education licence for the faceplates, the module assemblies and the drawings.</strong>
  Boards travel from KiCad to Fusion as STEP files. Fusion's drawing workspace produces sheets
  with a border, title block, third-angle views and ordinate dimensions.</p>
  <p>If the team would rather stay free and open source, or wants changes to flow back into
  KiCad automatically, FreeCAD with the KiCad StepUp workbench is the strongest
  alternative.</p>
</div>

<div class="flow">
  <b class="c">KiCad board</b><i>&rarr; STEP &rarr;</i><b>Fusion assembly</b><i>&rarr;</i>
  <b class="a">faceplate</b><i>&rarr;</i><b>drawing</b><i>&rarr; PDF / DWG / DXF</i>
</div>

<h2>Alternatives compared</h2>
""" + table(["Tool", "Good at", "Weak at", "Verdict"],
            [["<strong>Fusion 360</strong> (Education)",
              "Assemblies, interference checks, the best drawing workspace of the free options, "
              "easy to learn, renders.",
              "Cloud only. One-way from KiCad: board changes need a re-export and Replace Component.",
              "Use"],
             ["<strong>FreeCAD + KiCad StepUp</strong>",
              "Free and open. Two-way link: push a board outline or moved footprints back into "
              "KiCad. TechDraw makes proper drawings.",
              "Rougher interface, more crashes, drawings take longer to make tidy.",
              "Best alternative"],
             ["<strong>KiCad on its own</strong>",
              "3D viewer and STEP export are built in. You can draw the faceplate as a PCB "
              "(aluminium or FR4 from a board house) with legends in silkscreen, which is cheap.",
              "No mechanical drawings, no assembly, no interference check against a panel.",
              "For a PCB panel"],
             ["<strong>Front Panel Designer</strong> (Schaeffer)",
              "Fastest way to draw and order a machined, engraved panel with a live price.",
              "Only panels, only Schaeffer's service in Germany, no PCB model, basic drawings.",
              "Panel only"],
             ["<strong>Onshape</strong> (Education)",
              "Runs in a browser on any laptop, real-time collaboration, good drawings.",
              "Same one-way STEP link as Fusion, fewer tutorials aimed at electronics.",
              "If Fusion won't install"]],
            ["", "", "", ""]) + """
<p>Fusion wins here because the deliverable is a set of clean, dimensioned drawings for three
related modules, and it gets a student team there with the least friction. FreeCAD becomes
the better choice if one person will own the mechanical side for the whole project and values
the two-way KiCad link over polish.</p>

<div class="note">
  <h4>Licence</h4>
  <p>Get the free Autodesk Education licence with your UTS email rather than the Personal
  one. Personal use caps active documents and restricts some export formats; Education has
  the full drawing and export toolset. Keep all three modules in one shared Fusion team
  project so the drawing template is shared too.</p>
</div>
""")

PAGES['dimensions.html'] = ("Numbers to design to", f"""
<p class="eyebrow">The format</p>
<h1>Numbers to design to</h1>
<p class="lede">These come from the <a href="{VPR}">VPR Alliance 500-series drawing</a> and
from the panel already worked out in the <a href="{ORG}/Compressor/tree/main/panel">compressor
repository</a>. The spec gives nominal sizes; builders routinely trim the panel slightly so it
drops into any rack.</p>
""" + table(["Feature", "Value (mm)", "Source and note"],
            [["Faceplate width", "38.10 (1.500&Prime;)",
              "VPR spec. Make it 37.6 to 37.8 mm in practice so neighbouring modules and powder "
              "coat don't bind."],
             ["Faceplate height", "133.35 (5.250&Prime;)",
              "VPR spec. 132.6 mm (5.22&Prime;) is a common practical height."],
             ["Faceplate thickness", "3.18 (0.125&Prime;)", "VPR spec. 3 mm aluminium stock is fine."],
             ["Mounting holes", "&Oslash;3.18, csk 82&deg; to &Oslash;5.72",
              "VPR spec, two places, countersunk on the front face."],
             ["Mounting hole pitch", "125.43 (4.938&Prime;)",
              "Compressor panel README. On the vertical centreline, 3.96 mm from each end."],
             ["Depth behind panel", "150.83 &plusmn;0.5 (5.938&Prime;)",
              "VPR spec, from the panel's mounting surface to the rear."],
             ["Edge connector", "15 pin, 3.96 (0.156&Prime;) pitch",
              "VPR spec, mates with an EDAC 306/307-015-520-102 type socket."],
             ["PCB thickness", "1.6 (0.062&Prime;)", "Standard board; the socket expects it."],
             ["PCB offset from panel centreline", "check",
              f'Published figures disagree: 11.13 mm and 7.92 mm both appear on '
              f'<a href="{GDIY_OFFSET}">GroupDIY</a>. Take it from the Pre-Amp template board, '
              'then confirm against the rack you will use.'],
             ["Power budget", "&plusmn;16 V @ 130 mA, +48 V @ 5 mA", "VPR spec, per module."]],
            ["", "", ""]) + envelope() + f"""
<p>More discussion of practical tolerances is in the
<a href="{GDIY}">GroupDIY mechanical specifications thread</a>.</p>
""")

PAGES['pcb.html'] = ("PCB into Fusion", f"""
<p class="eyebrow">Workflow, step A</p>
<h1>Get each PCB into Fusion</h1>
<p class="lede">You don't redraw the board in Fusion. KiCad writes a STEP file with the board
body and every component that has a 3D model, and Fusion treats that as a normal part you can
build around.</p>

<ol>
  <li><strong>Finish the board outline in KiCad.</strong> Everything on the
  <code>Edge.Cuts</code> layer becomes the board body. Start new boards from the Pre-Amp
  repository's <code>Series-500.kicad_pcb</code> template, which already carries the card-edge
  fingers. Its outline measures 152.35 &times; 105.0 mm.</li>
  <li><strong>Check the 3D models.</strong> Open <em>View &rarr; 3D Viewer</em>
  (<kbd>Alt</kbd>+<kbd>3</kbd>). Anything missing there will be missing in Fusion. Pots, jacks,
  switches and LEDs matter most, because those are the parts that go through the faceplate.
  Resistors and capacitors are nice to have.</li>
  <li><strong>Set an origin you can find again.</strong> <em>Place &rarr; Drill/Place File
  Origin</em>, and put it where the board meets the back of the faceplate, on the edge nearest
  the bottom mounting hole. Exporting relative to this point means the board lands in the same
  place in Fusion every time.</li>
  <li><strong>Export STEP.</strong> <em>File &rarr; Export &rarr; STEP</em>. Tick <em>Drill/place
  file origin</em> and <em>Substitute similarly named models</em>. Leave tracks and zones off;
  they add a lot of geometry and nothing you'll dimension.</li>
  <li><strong>Bring it into Fusion.</strong> In the Data Panel, <em>Upload</em> the STEP into the
  team project. Then, inside the module's assembly design, right-click it and choose <em>Insert
  into Current Design</em>. It arrives as a linked component.</li>
  <li><strong>When the board changes,</strong> export again and swap it in with right-click
  &rarr; <em>Replace Component</em> on the old one. Joints you made to it survive as long as the
  faces they reference still exist.</li>
</ol>

<p>The same export from a terminal:</p>
<pre><code>kicad-cli pcb export step --drill-origin --subst-models \\
  -o LBP.step LBP.kicad_pcb</code></pre>

<div class="note warn">
  <h4>Known gaps in our repositories</h4>
  <p>The Equaliser's custom <code>OPA1641</code> footprint points at
  <code>OPA1641AID.stp</code>, which isn't in the repository, so it will export as nothing.
  Either download the model from TI and put it next to the footprint, or point the footprint
  at KiCad's stock SOIC-8 model. The Pre-Amp's <code>eda306</code> edge connector footprint
  has no 3D model at all.</p>
</div>

<p>Fusion also has its own electronics workspace that can import KiCad files. Don't use it
for this: you would end up with two copies of each board that drift apart.</p>
""")

PAGES['faceplate.html'] = ("Model the faceplate", """
<p class="eyebrow">Workflow, step B</p>
<h1>Model the faceplate</h1>
<p class="lede">One parametric panel that every module starts from, with its control holes
taken straight off the board.</p>

<ol>
  <li><strong>Create a new design</strong> for the module (for example <em>EQ-500
  Assembly</em>) and set units to millimetres. Make a new component called <em>Faceplate</em>
  and activate it before sketching, so the panel isn't loose geometry in the root.</li>
  <li><strong>Add user parameters</strong> in <em>Modify &rarr; Change Parameters</em>:
  <code>panel_w = 37.8</code>, <code>panel_h = 132.6</code>, <code>panel_t = 3.18</code>,
  <code>hole_pitch = 125.43</code>. Every later dimension references these, so a trim for a
  tight rack is one edit.</li>
  <li><strong>Sketch and extrude the blank.</strong> Centre-point rectangle on the XZ plane,
  <code>panel_w &times; panel_h</code>, extruded <code>panel_t</code> backwards. Draw the vertical
  centreline as construction geometry.</li>
  <li><strong>Mounting holes.</strong> Two sketch points on the centreline, <code>hole_pitch</code>
  apart and symmetric about the middle. Use the <em>Hole</em> tool, type <em>Countersink</em>,
  &Oslash;3.18, countersink &Oslash;5.72 at 82&deg;, from the front face.</li>
  <li><strong>Control holes come from the board.</strong> This is the reason to model the PCB
  first. Start a sketch on the back face of the panel and use <em>Sketch &rarr; Project</em> on
  each pot and switch bushing in the inserted STEP. The projected circle's centre is exactly
  where that part sits on the real board. Put a <em>Hole</em> on each, sized for the hardware.
  The compressor uses 7.2 mm for its 9 mm pots, 6.5 mm for its mini toggles and 2.2 mm for 2 mm LEDs;
  check against the parts you actually buy.</li>
  <li><strong>Legends.</strong> Sketch text on the front face. For engraving, <em>Emboss</em> it
  0.2 mm into the panel. For a UV-printed or screen-printed finish, keep it as sketch text so it
  shows on the drawing but doesn't cut the model.</li>
  <li><strong>Appearance.</strong> Apply an anodised aluminium appearance so renders read
  correctly. It has no effect on the drawings.</li>
</ol>

<div class="note">
  <h4>If the PCB isn't laid out yet</h4>
  <p>Work the other way round: place holes on the panel first, export the panel's back-face
  sketch as DXF (right-click the sketch &rarr; <em>Save as DXF</em>), and import it into KiCad
  with <em>File &rarr; Import &rarr; Graphics</em> on a user layer so you can place pots on the
  hole centres.</p>
</div>
""")

PAGES['assembly.html'] = ("Assemble and check", """
<p class="eyebrow">Workflow, step C</p>
<h1>Assemble and check</h1>
<p class="lede">Put the panel, board, bracket and knobs together and let Fusion find the
collisions before the workshop does.</p>

<ol>
  <li><strong>Add the bracket and knobs.</strong> Model the L-bracket that joins PCB to panel,
  or rely on pot nuts if the pots are panel-mounted, and simple cylinders for knobs at their
  real skirt diameter and height.</li>
  <li><strong>Joint everything.</strong> Ground the faceplate, then use <em>Rigid</em> joints for
  the bracket and PCB. Place the PCB so its card-edge fingers sit at the 150.83 mm spec depth and
  at the centreline offset you confirmed from the rack.</li>
  <li><strong>Run <em>Inspect &rarr; Interference</em></strong> across all components. It catches
  pot bodies hitting the bracket, tall capacitors hitting the panel and knobs that overlap the
  mounting screws.</li>
  <li><strong>Check the envelope.</strong> Sketch a 38.1 mm wide box around the module in the top
  view. Nothing on the PCB may cross it, or it will foul the next module in the rack.</li>
</ol>
""")

PAGES['drawings.html'] = ("Export drawings", """
<p class="eyebrow">Workflow, step D</p>
<h1>Export the drawings</h1>
<p class="lede">An outline drawing is a sheet with a zoned border, a title block that states
units, tolerances and scale, a revision table, third-angle views of the whole product and only
overall dimensions. Fusion's Drawing workspace does all of that.</p>

<h2>Set up a template once</h2>
<ol>
  <li>From any module design, <em>File &rarr; New Drawing &rarr; From Design</em>. Choose
  <strong>Standard: ISO</strong>, <strong>Units: mm</strong>, <strong>Sheet size: A3</strong>.
  A whole 500-series module fits at 1:1 on A3.</li>
  <li>In the drawing's document settings, set <strong>Projection angle: Third angle</strong>, as
  AS 1100 prefers.</li>
  <li>Double-click the title block to fill it: title, part number, drawn by, checked, date,
  scale, sheet <em>n of m</em>. Add a general tolerance note: <em>Dimensions in millimetres. No
  decimal &plusmn;0.5, one decimal &plusmn;0.2, two decimal &plusmn;0.1. Angular &plusmn;30&prime;.
  Remove all burrs and sharp edges. Do not scale.</em></li>
  <li>Add a revision table and a notes block. Then <em>File &rarr; Save as Template</em> so all
  three modules share the same sheet.</li>
</ol>

<h2>Sheets for each module</h2>
""" + table(["Sheet", "Views", "Dimensions"],
            [["1. Outline", "Front, side, top and an isometric of the whole module with knobs",
              "Overall height, width and depth only, including knob protrusion."],
             ["2. Faceplate", "Front view at 1:1, section through one mounting hole",
              "Ordinate dimensions from the top-left corner to every hole centre, hole callouts, "
              "countersink note, finish and material."],
             ["3. PCB", "Top view of the board, side view showing the fingers",
              "Outline, finger position and pitch, mounting and bracket holes, maximum component "
              "height."]],
            ["r", "", ""]) + """

<h2>Build each sheet</h2>
<ol>
  <li><strong>Place views.</strong> <em>Base View</em> of the assembly in front orientation, then
  <em>Projected View</em> to drag out the side, top and isometric. In each view's settings
  choose <em>Visible edges</em> and hide tangent edges for a clean line style.</li>
  <li><strong>Dimension.</strong> Use <em>Dimension</em> for overall sizes and <em>Ordinate
  Dimension</em> for the hole pattern, with the origin at the panel's top-left corner. That
  matches the drill schedule already in the compressor's panel README, so the drawing and the
  table can be checked against each other.</li>
  <li><strong>Annotate.</strong> <em>Center Mark</em> and <em>Centerline</em> on every hole,
  <em>Hole and Thread Note</em> on the mounting holes so the countersink reads automatically,
  and a <em>Parts List</em> with balloons on sheet 1 if you want the parts on the drawing.</li>
  <li><strong>Export.</strong> <em>Output &rarr; PDF</em> for submission and review, <em>Output
  &rarr; DWG</em> or <em>DXF</em> if a panel shop or the UTS workshop wants CAD.</li>
</ol>

<div class="note warn">
  <h4>For cutting, send the sketch</h4>
  <p>For laser or CNC cutting, send the faceplate sketch DXF from step B, not the drawing DXF.
  The drawing DXF includes the border, title block and dimensions, which a cutter will try to
  cut.</p>
</div>
""")

PAGES['modules.html'] = ("Per-module notes", f"""
<p class="eyebrow">Practical</p>
<h1>Per-module notes</h1>
<p class="lede">Where each module's mechanical work starts from, as of 28 September 2026.</p>
""" + table(["Module", "Where it is", "First step"],
            [[f'<a href="{ORG}/Compressor">Compressor</a>',
              "Full panel defined in <code>panel/make_panel.py</code>, with "
              "<code>faceplate.dxf</code> and a dimensioned drawing. Schematic done, no PCB "
              "layout.",
              "In the faceplate sketch, <em>Insert &rarr; Insert DXF</em> the existing "
              "<code>faceplate.dxf</code> and extrude from it. Pick one of the three layouts "
              "first; the DXF is whichever was generated last."],
             [f'<a href="{ORG}/Equaliser">Equaliser</a>',
              "Both bands on one sheet (<code>Combined_EQ</code>), its board started from the "
              "same template outline as the Pre-Amp with only J1 placed. No panel yet.",
              "Give the pots and capacitors footprints, place them, then export STEP. Fix the "
              "missing OPA1641 model first."],
             [f'<a href="{ORG}/Pre-Amp">Pre-Amp</a>',
              "The repository is the Series 500 KiCad template board, 47 footprints. No panel.",
              "Export STEP now to get the card and connector envelope into Fusion. It doubles as "
              "the reference for the other two boards."]],
            ["r", "", ""]) + """
<div class="note">
  <h4>One source of truth per faceplate</h4>
  <p>If the compressor panel moves into Fusion, treat <code>make_panel.py</code> as retired, or
  keep the script as master and re-import its DXF whenever it changes. Editing both will
  drift.</p>
</div>
""")

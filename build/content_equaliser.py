"""Equaliser module - page content.

Written from the Equaliser repository at commit 4c6c1af (16 Sep 2026):
https://github.com/UTS-500-Series/Equaliser

Unlike the compressor, the equaliser has no design.py, so there are no interactive viewers
here - the schematics are static exports, and the only real numbers come from the LTspice
run committed in LBPF/BandA. Keep this page honest about that: it documents work in
progress, not a finished design.
"""
import json, math, os
import shell
from shell import pic, table

SRC = 'https://github.com/UTS-500-Series/Equaliser'
COMMIT = '4c6c1af'

NAV = [("Start here", [("index.html", "01", "Overview")]),
       ("Filter sections", [("parametric.html", "02", "Parametric band"),
                            ("lowpass.html", "03", "Low-pass filter")]),
       ("Practical", [("simulation.html", "04", "Simulating it"),
                      ("status.html", "05", "What is left")])]


def response_chart():
    """Band A's simulated response, drawn inline so it follows the site's theme."""
    d = json.load(open(os.path.join(shell.DATA_DIR, 'bandA-response.json')))
    pts = d['points']
    W, H, L, R, T, B = 640, 300, 48, 16, 16, 36
    fmin, fmax, dbmin, dbmax = 10, 100000, -2, 6
    X = lambda f: L + (math.log10(f) - 1) / (math.log10(fmax) - 1) * (W - L - R)
    Y = lambda db: T + (dbmax - db) / (dbmax - dbmin) * (H - T - B)
    grid, lab = [], []
    for f in (10, 100, 1000, 10000, 100000):
        grid.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d"/>' % (X(f), T, X(f), H - B))
        lab.append('<text x="%.1f" y="%d" text-anchor="middle">%s</text>'
                   % (X(f), H - B + 18, {10: '10', 100: '100', 1000: '1k', 10000: '10k', 100000: '100k'}[f]))
    for db in range(dbmin, dbmax + 1, 2):
        grid.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (L, Y(db), W - R, Y(db)))
        lab.append('<text x="%d" y="%.1f" text-anchor="end" dominant-baseline="middle">%+d</text>'
                   % (L - 6, Y(db), db) if db else
                   '<text x="%d" y="%.1f" text-anchor="end" dominant-baseline="middle">0 dB</text>' % (L - 6, Y(db)))
    path = 'M' + ' L'.join('%.1f %.1f' % (X(f), Y(db)) for f, db in pts if fmin <= f <= fmax)
    pk = _peak(pts)
    return f"""<figure>
  <div style="background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px 10px 6px"><svg viewBox="0 0 {W} {H}" role="img" style="width:100%;height:auto;display:block"
       aria-label="Simulated response of band A: peak of {pk[1]:.1f} dB at about {pk[0]:.0f} Hz">
    <g stroke="var(--rule)" stroke-width="1">{''.join(grid)}</g>
    <line x1="{L}" y1="{Y(0):.1f}" x2="{W-R}" y2="{Y(0):.1f}" stroke="var(--ink-3)" stroke-width="1"/>
    <path d="{path}" fill="none" stroke="var(--sig)" stroke-width="2.4" stroke-linejoin="round"/>
    <circle cx="{X(pk[0]):.1f}" cy="{Y(pk[1]):.1f}" r="4" fill="var(--sig)"/>
    <text x="{X(pk[0])+8:.1f}" y="{Y(pk[1])-8:.1f}" fill="var(--ink)" font-family="var(--mono)" font-size="12">+{pk[1]:.1f} dB, ~{pk[0]:.0f} Hz</text>
    <g fill="var(--ink-3)" font-family="var(--mono)" font-size="11">{''.join(lab)}</g>
  </svg></div>
  <figcaption><span>Band A, simulated &mdash; LTspice AC analysis, V(output), 401 points</span>
  <a href="data/bandA-response.json" target="_blank" rel="noopener">Raw data &rarr;</a></figcaption>
</figure>"""


def _peak(d):
    """The top of the bell is flat to within rounding across several points, so the single
    highest point is arbitrary. Report the geometric centre of the points within 0.05 dB of
    the maximum, to two significant figures."""
    top = max(p[1] for p in d)
    plateau = [p[0] for p in d if p[1] >= top - 0.05]
    f = math.exp(sum(map(math.log, plateau)) / len(plateau))
    return (float('%.2g' % f), top)


def _pk():
    d = json.load(open(os.path.join(shell.DATA_DIR, 'bandA-response.json')))['points']
    at = lambda f: min(d, key=lambda p: abs(math.log10(p[0]) - math.log10(f)))[1]
    return _peak(d), at


PAGES = {}

PAGES['index.html'] = ("Overview", f"""
<p class="eyebrow">Equaliser module</p>
<h1>The equaliser</h1>
<p class="lede">A multi-band equaliser for the desk, built from filter sections around the
OPA1641. Two sections are drawn and one has been simulated &mdash; this is a module in
progress, and these pages say exactly how far along it is.</p>

<div class="note warn">
  <h4>Work in progress</h4>
  <p>Written from the <a href="{SRC}">Equaliser repository</a> at commit
  <code>{COMMIT}</code>. The KiCad sheets have their topology drawn but <strong>no component
  values yet</strong>. The only real numbers on this site come from one LTspice run of one
  band. Nothing has been built or measured.</p>
</div>

<h2>What exists</h2>
""" + table(["Section", "Topology", "Drawn", "Values", "Simulated"],
            [['<a href="parametric.html">Parametric band</a>', "State-variable", "Yes &mdash; 4 op amps",
              "Not in KiCad", "Yes &mdash; one run"],
             ['<a href="lowpass.html">Low-pass filter</a>', "Sallen-Key, 2nd order", "Yes &mdash; 1 op amp",
              "Not in KiCad", "No"],
             ["Bill of materials", "&mdash;", "Template only", "&mdash;", "&mdash;"]],
            ["r", "", "", "", ""]) + """

<h2>Why the OPA1641</h2>
<p>Every section uses the OPA1641, not the NE5532 the compressor is built on. That is a
sensible choice for filters. It is a JFET-input part, so its input bias current is
picoamps rather than the NE5532's hundreds of nanoamps &mdash; which matters when the
frequency-setting resistors are tens of kilohms and a pot wiper sits on a high-impedance
node. Bias current through those resistors is offset, and offset through a pot is a click
every time the knob turns.</p>
<p>The cost is that the desk now carries two op-amp types, which the bill of materials and
the spares box both need to account for.</p>

<h2>How the repository is laid out</h2>
""" + table(["Folder", "What is in it"],
            [["<code>LBP/</code>", "The current parametric band schematic, edited 16 Sep"],
             ["<code>LBPF/</code>", "An earlier copy of the same band, plus the LTspice model "
              "<code>BandA.asc</code> and its results"],
             ["<code>LPF/LPF/</code>", "The low-pass filter schematic and a PDF of it"],
             ["<code>EQ BOM.docx</code>", "A bill-of-materials table with its columns set up and "
              "no rows filled"]],
            ["r", ""]) + """
<p>Worth knowing before editing: <code>LBP/</code> and <code>LBPF/</code> are two copies of
the same band that have now diverged. The simulation belongs to the <code>LBPF/</code> copy;
the schematic work since has gone into <code>LBP/</code>.</p>
""")

pk_, at_ = _pk()

PAGES['parametric.html'] = ("Parametric band", """
<p class="eyebrow">Filter section 02</p>
<h1>The parametric band</h1>
<p class="lede">A state-variable filter wired as a peaking equaliser: one band that can be
tuned in frequency, widened or narrowed, and boosted or cut.</p>

""" + pic("lbp.svg", "Low band pass state variable parametric equaliser &mdash; LBP/LBP.kicad_sch at "
          + COMMIT) + """

<h2>How a state-variable band works</h2>
<p>A state-variable filter is a summing amplifier followed by two integrators in a loop. It
produces low-pass, band-pass and high-pass outputs simultaneously from the same two
capacitors, and &mdash; the reason it is used for parametric EQ &mdash; its centre frequency
and its Q can be set independently. Frequency is set by the integrators' resistor-capacitor
time constants; Q by how much of the band-pass output is fed back to the summer.</p>
<p>For an equaliser, the band-pass output is added back to or subtracted from the dry
signal. Add it and the band peaks; subtract it and the band dips. Everywhere outside the band
the band-pass output is near zero, so the signal passes through untouched.</p>
<p>That is a description of the topology the sheet is titled as, not a trace of its
connections &mdash; with no values on the sheet yet, the wiring has not been checked against
a netlist the way the compressor's has.</p>

<h2>What the simulation shows</h2>
""" + response_chart() + f"""
<p>This is exactly the shape a peaking band should have. The response rises to
<strong>+{pk_[1]:.1f}&nbsp;dB at about {pk_[0]:.0f}&nbsp;Hz</strong> and falls back to within
{max(abs(at_(10)), abs(at_(20000))):.1f}&nbsp;dB of flat at both 10&nbsp;Hz and 20&nbsp;kHz, so
the band touches only the part of the spectrum it is tuned to.</p>
""" + table(["Frequency", "Simulated level"],
            [["%s Hz" % f if f < 1000 else "%g kHz" % (f / 1000), "%+.2f dB" % at_(f)]
             for f in (20, 100, 200, 500, 1000, 2000, 5000, 20000)], ["r", "n"]) + """

<h3>The three controls</h3>
<p>The simulation file carries three notes placed beside the parts they describe:</p>
""" + table(["Note in BandA.asc", "Placed beside", "Control"],
            [["&ldquo;Big = wide&rdquo;", "R5, 90&nbsp;k&Omega;", "Width, i.e. Q"],
             ["&ldquo;Big = higher freq&rdquo;", "C2 and R13", "Centre frequency"],
             ["&ldquo;big = gain&rdquo;", "R18 2&nbsp;k&Omega; and R19 8&nbsp;k&Omega;", "Boost or cut"]],
            ["r", "", ""]) + """
<p>R18 and R19 total 10&nbsp;k&Omega; and read as a potentiometer modelled as its two halves,
set 20% from one end &mdash; the usual way to put a pot position into SPICE. The pairing of
notes with parts is by position on the drawing, so treat it as a reading rather than a
certainty.</p>

<div class="note warn">
  <h4>The simulated values do not map onto the schematic</h4>
  <p>The simulation has <strong>22 resistors</strong>; the KiCad sheet has
  <strong>14</strong>. Pots split into halves account for some of the difference, but not all
  of it, and designators do not correspond &mdash; the simulation's R5 is not necessarily the
  sheet's R5. The values proven in LTspice have to be carried across by circuit position, not
  by reference designator.</p>
  <p>The result is also from the 2 September copy in <code>LBPF/</code>, and the schematic in
  <code>LBP/</code> has changed since, including a fifth op amp marked <code>TEMP</code>.</p>
</div>
""")

PAGES['lowpass.html'] = ("Low-pass filter", """
<p class="eyebrow">Filter section 03</p>
<h1>The low-pass filter</h1>
<p class="lede">A second-order Sallen-Key low-pass with a variable control &mdash; the
simplest active filter there is, and the only section that needs just one op amp.</p>

""" + pic("lpf.svg", "Low pass Sallen-Key variable equaliser &mdash; LPF/LPF/LPF.kicad_sch at "
          + COMMIT) + """

<h2>How it works</h2>
<p>The signal passes through two resistors in series into the op amp's non-inverting input,
with C2 from that input to ground. C1 feeds the <em>output</em> back to the point between
the resistors. At low frequencies C1 does nothing and the op amp simply buffers. Towards the
cutoff, C1's positive feedback props the response up, which is what lets two capacitors give
a sharper, flatter-topped roll-off than two plain RC stages would. Above cutoff the response
falls at 12&nbsp;dB per octave.</p>
<p>R3 and R4 set the stage's gain, 1&nbsp;+&nbsp;R3/R4. In a Sallen-Key that gain is not just
a level control: it sets how much positive feedback C1 applies, and so it sets the Q of the
filter. Gain near 1 gives a gentle roll-off; push it towards 3 and the filter peaks, then
oscillates.</p>
<p>With the resistors called R<sub>a</sub> and R<sub>b</sub>, the cutoff is</p>
<p style="text-align:center"><em>f</em><sub>c</sub> = 1 &frasl; (2&pi; &radic;(R<sub>a</sub> R<sub>b</sub> C1 C2))</p>

<h2>The variable control does not sweep cutoff</h2>
<p>RV1 sits between R1 and R2 with its wiper carrying C1's feedback tap. Turning it does not
change the total resistance &mdash; it slides the tap point along the chain, moving resistance
from one side of C1 to the other. So R<sub>a</sub>&nbsp;+&nbsp;R<sub>b</sub> stays constant
while their <em>product</em> changes, and a product with a fixed sum is largest when the two
are equal.</p>
<p>The consequence: <strong>cutoff falls to its lowest at the centre of the pot's travel and
rises again towards either end.</strong> This holds for any values. As a check, with example
values R1&nbsp;=&nbsp;R2&nbsp;=&nbsp;1&nbsp;k&Omega;, RV1&nbsp;=&nbsp;10&nbsp;k&Omega; and both
capacitors 10&nbsp;nF:</p>
""" + table(["RV1 position", "0%", "25%", "50%", "75%", "100%"],
            [["Cutoff", "4.80 kHz", "2.92 kHz", "2.65 kHz", "2.92 kHz", "4.80 kHz"]],
            ["r", "n", "n", "n", "n", "n"]) + """
<p>With R1 and R2 equal, the two halves of the knob do the same thing &mdash; a panel legend
cannot be drawn for it. The Q moves as well, because the resistor ratio feeds into the
feedback. The values above are illustrative, since the sheet has none yet; the shape of the
problem is not.</p>
<p>If the aim is a knob that sweeps cutoff, the usual fix is a <strong>dual-gang pot</strong>
with one gang in place of each resistor, so R<sub>a</sub> and R<sub>b</sub> rise and fall
together and Q stays put.</p>
""")

PAGES['simulation.html'] = ("Simulating it", f"""
<p class="eyebrow">Practical</p>
<h1>Simulating it</h1>
<p class="lede">Band A was simulated in LTspice and the results are in the repository. As
committed, though, the simulation will not run on anyone else's machine &mdash; and the most
recent attempt failed on the original one too.</p>

<h2>The failure</h2>
<p>The newest log, <code>LBPF/BandA/BandA.log</code>, stops on the same error for all four op
amps:</p>
<pre><code>This sub-circuit name is not defined.</code></pre>
<p>The results plotted on the <a href="parametric.html">parametric band page</a> come from an
<em>earlier</em> run: <code>BandA.raw</code> is stamped 29&nbsp;Aug 18:28, and the failing log
19:10 the same evening. Something changed in between.</p>

<h2>Two things to fix</h2>
<h3>1. The model is linked by an absolute Windows path</h3>
<p>Every op amp's <code>ModelFile</code> in <code>BandA.asc</code>, and the symbol
<code>OPA164x.asy</code>, point at a folder on the machine the file was drawn on:</p>
<pre><code>C:\\Users\\...\\Downloads\\sbom627d\\OPA164x.LIB</code></pre>
<p>A copy of the library is already committed beside the schematic, at
<code>LBPF/BandA/OPA164x.LIB</code>. Point the model at that with a relative path and the
simulation will find it on any machine.</p>
<h3>2. The subcircuit name</h3>
<p>The log names the subcircuit <code>OPA164</code>; the library defines
<code>.SUBCKT OPA164x</code>. Once the path resolves, confirm the name LTspice asks for matches
exactly.</p>
<p>The first is certain. The second is what the log reports, but the symbol's own value field
reads <code>OPA164x</code>, so the mismatch may disappear once the path is fixed &mdash; re-run
and read the log before editing names.</p>

<h2>Re-running it</h2>
<ol>
  <li>Open <code>LBPF/BandA.asc</code> in LTspice.</li>
  <li>Fix the model path as above.</li>
  <li>Run. The analysis is already set: <code>.ac dec 100 10 100k</code>, 100 points per decade
  from 10&nbsp;Hz to 100&nbsp;kHz.</li>
  <li>Plot <code>V(output)</code>. It should reproduce the +5.2&nbsp;dB peak near 520&nbsp;Hz.
  If it does not, the circuit changed after the 18:28 run.</li>
</ol>
<p>Committing the regenerated <code>.raw</code> with the fix means the plot on this site can be
refreshed from a result that is known to come from the current file.</p>
""")

PAGES['status.html'] = ("What is left", """
<p class="eyebrow">Practical</p>
<h1>What is left</h1>
<p class="lede">In rough order &mdash; each step unblocks the next.</p>
""" + table(["Step", "Why it comes here"],
            [["Get the simulation running again",
              "It is the only source of proven values, and it currently fails."],
             ["Merge <code>LBP/</code> and <code>LBPF/</code>",
              "Two diverging copies of one band. Decide which is current and delete the other."],
             ["Resolve the <code>TEMP</code> op amp in <code>LBP/</code>",
              "A fifth op amp added on 16 Sep; the simulated band uses four."],
             ["Decide what the low-pass knob should do",
              "As drawn it does not sweep cutoff. A dual-gang pot fixes that."],
             ["Carry simulated values onto the schematics",
              "By circuit position &mdash; designators in the simulation do not match the sheet."],
             ["Draw the supply and decoupling",
              "The sheets show the signal path; the OPA1641s need rails and bypass capacitors."],
             ["Decide the band count and panel layout",
              "A 38&nbsp;mm panel runs out of room fast: each parametric band wants three controls."],
             ["Fill in the bill of materials", "<code>EQ BOM.docx</code> has columns and no rows."]],
            ["r", ""]) + """

<h2>The panel is the binding constraint</h2>
<p>One parametric band needs frequency, width and gain &mdash; three controls. The compressor
fits nine functions on the same 38.10&nbsp;mm faceplate only by using concentric and
pull-switch pots. Two parametric bands plus a low-pass control is seven knobs before any
switches, so the number of bands is a panel decision as much as a circuit one, and it is worth
making before values are chosen for sections that may not fit.</p>
""")

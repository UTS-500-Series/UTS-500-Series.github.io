"""Preamp module - page content.

Written from ESP's articles, not from our KiCad redraw:
  Project 66, Low Noise Balanced Microphone Preamp   https://sound-au.com/project66.htm
  Project 96, 48V Phantom Feed Supply                https://sound-au.com/project96.htm
Both (c) Rod Elliott. The prose here is our own description; ESP's figures are linked, not
copied. Every measured figure is ESP's and is labelled as such. Figures we derived (the
+/-16 V operating points, the input impedance with phantom fitted) are labelled as ours.
"""
from shell import table

P66 = 'https://sound-au.com/project66.htm'
P96 = 'https://sound-au.com/project96.htm'
FIG1 = 'https://sound-au.com/p66-f1.gif'


def credit():
    return f"""<div class="note">
  <h4>Whose design this is</h4>
  <p>This is <a href="{P66}">ESP Project 66</a> by Rod Elliott, with phantom power from
  <a href="{P96}">Project 96</a>. We did not design it. These pages explain it in our own
  words for the desk; the schematic itself is <a href="{FIG1}">ESP's Figure 1</a>. ESP allows
  construction for personal use, not commercial manufacture.</p>
</div>"""


def blocks():
    """Signal flow, drawn for this site."""
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
  <svg viewBox="0 0 640 230" role="img" style="width:100%;height:auto;display:block"
       aria-label="Signal flow: balanced input to two Sziklai pairs joined by a gain control, then a difference amplifier to the balanced output">
    <defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0L10 5L0 10z" fill="var(--sig)"/></marker></defs>
    {txt(34, 72, '+IN')}{txt(34, 172, '&#8722;IN')}
    {arrow(56, 68, 118, 68)}{arrow(56, 168, 118, 168)}
    {box(120, 40, 140, 56, 'Sziklai pair', 'Q3 + Q4')}
    {box(120, 140, 140, 56, 'Sziklai pair', 'Q1 + Q2')}
    <line x1="190" y1="96" x2="190" y2="140" stroke="var(--ctl)" stroke-width="2" stroke-dasharray="4 3"/>
    <rect x="200" y="105" width="96" height="26" rx="5" fill="var(--surface)" stroke="var(--ctl)"/>
    {txt(248, 122, 'gain: R9 VR1', 'middle', 'var(--ctl)')}
    {arrow(260, 68, 348, 108)}{arrow(260, 168, 348, 128)}
    {box(350, 88, 140, 60, 'Difference amp', 'U1A, gain 4.55')}
    {arrow(490, 110, 560, 110)}
    {txt(596, 106, 'OUT+')}{txt(596, 124, 'OUT&#8722;', 'middle')}
    {txt(34, 30, 'P48 via P96', 'start', 'var(--warn)')}
  </svg></div>
  <figcaption><span>Signal flow &mdash; drawn for this site from ESP's Figure 1</span>
  <a href="{FIG1}" target="_blank" rel="noopener">ESP's schematic &rarr;</a></figcaption>
</figure>"""


NAV = [("Start here", [("index.html", "01", "Overview")]),
       ("The circuit", [("input.html", "02", "Input stage"),
                        ("gain.html", "03", "Gain control"),
                        ("output.html", "04", "Output stage")]),
       ("In the desk", [("phantom.html", "05", "48 V phantom power"),
                        ("rack.html", "06", "In a 500-series slot"),
                        ("build.html", "07", "Building it")])]

PAGES = {}

PAGES['index.html'] = ("Overview", f"""
<p class="eyebrow">Preamp module</p>
<h1>The microphone preamp</h1>
<p class="lede">A discrete, very low-noise balanced microphone preamp: two transistor pairs
doing the gain, one op amp turning it into a balanced line output, and a single knob covering
most of a 60&nbsp;dB range.</p>

{credit()}

""" + blocks() + """

<h2>What it does</h2>
<p>A microphone delivers millivolts. The desk wants line level. The preamp's whole job is to
supply that gain while adding as little noise as possible, because everything after it
&mdash; the compressor, the equaliser &mdash; can only ever be as quiet as what the preamp
hands on.</p>
<p>Most preamps do this with an op amp or a dedicated mic preamp IC. This one uses discrete
transistors at the input, which is where noise is decided, and only brings in an op amp once
the signal is large enough that the op amp's own noise no longer matters.</p>

<h2>Specifications</h2>
<p>All measured figures are ESP's, from their workshop unit.</p>
""" + table(["Parameter", "Value", "Source"],
            [["Equivalent input noise", "0.27&nbsp;&micro;V RMS (20&nbsp;kHz, 200&nbsp;&Omega; source)", "ESP, measured"],
             ["Noise density", "1.9&nbsp;nV/&radic;Hz", "ESP, measured"],
             ["Noise figure", "0.9&nbsp;dB (vs 200&nbsp;&Omega;)", "ESP, measured"],
             ["Maximum gain", "56&nbsp;dB with R9 at 22&nbsp;&Omega; (60&nbsp;dB nominal)", "ESP"],
             ["Output stage gain", "4.55, 13&nbsp;dB", "100k / 22k"],
             ["Maximum input", "about 1.5&nbsp;V RMS before clipping", "ESP"],
             ["Input impedance", "6.6&nbsp;k&Omega;; 4.4&nbsp;k&Omega; with phantom feed fitted", "ESP; ours"],
             ["CMRR", "well over 60&nbsp;dB", "ESP"],
             ["Bandwidth", "beyond 100&nbsp;kHz", "ESP"],
             ["Supply", "&plusmn;15&nbsp;V in the article; &plusmn;16&nbsp;V in the rack", "ESP; 500-series"]],
            ["r", "n", ""]) + """
<p>For scale: 1.9&nbsp;nV/&radic;Hz matches the SSM2017, a dedicated professional mic preamp
IC, which ESP uses as their point of comparison.</p>
""")

PAGES['input.html'] = ("Input stage", f"""
<p class="eyebrow">The circuit &mdash; 02</p>
<h1>The input stage</h1>
<p class="lede">Two compound transistor pairs, one per input leg. This is where the preamp's
noise performance is won.</p>

<h2>Why a compound pair</h2>
<p>A single transistor is not very linear. Pair a PNP with an NPN in a Sziklai connection
&mdash; here a 2N4403 driving a BC549 &mdash; and the two behave as one transistor with far
higher gain and much lower distortion, because the second device corrects the first. ESP
describes the pairs as far more linear than any single transistor, and it is why distortion
at high gain disappears below the noise floor.</p>
<p>In each pair the combination acts as a single PNP:</p>
""" + table(["Acts as", "Is really", "Sits at (&plusmn;15&nbsp;V)"],
            [["Base", "Q1 base &mdash; the input", "0&nbsp;V"],
             ["Emitter", "Q1 emitter, joined to Q2 collector", "+0.65&nbsp;V"],
             ["Collector", "Q2 emitter &mdash; the output", "&minus;8.3&nbsp;V"]],
            ["r", "", "n"]) + """
<p>Those voltages are ESP's, printed in green on their Figure 1. They are also a useful check
on how the stage is wired, because the currents they imply agree with each other:</p>
""" + table(["Resistor", "Voltage across it", "Current"],
            [["R2, +15&nbsp;V to the emitter node", "14.35&nbsp;V over 4.7&nbsp;k&Omega;", "3.05&nbsp;mA"],
             ["R4, the output node to &minus;15&nbsp;V", "6.7&nbsp;V over 2.2&nbsp;k&Omega;", "3.05&nbsp;mA"],
             ["R3, across Q2's base-emitter", "0.65&nbsp;V over 680&nbsp;&Omega;", "0.96&nbsp;mA"]],
            ["r", "n", "n"]) + """
<p>The same 3.05&nbsp;mA flows in at the top and out at the bottom, as it must. R3 sets how
hard Q1 works to drive Q2.</p>

<h2>A differential pair of pairs</h2>
<p>The two halves are identical, one on each leg of the balanced input. Anything common to both
legs &mdash; hum picked up along a microphone cable &mdash; moves both halves together and
cancels. Only the difference between the legs, which is the microphone's signal, gets
amplified.</p>

<h2>Input impedance: 6.6&nbsp;k&Omega;, on purpose</h2>
<p>R1 and R5, 3.3&nbsp;k&Omega; each, set the load the microphone sees. That is higher than
the microphone's own impedance by design. Matching the load to a 150&ndash;600&nbsp;&Omega;
microphone would throw away 6&nbsp;dB of signal, and noise does not fall with it. Professional
preamps sit at 2.2&nbsp;k&Omega; or more; this one sits at 6.6&nbsp;k&Omega; and barely loads
the microphone at all.</p>

<div class="note">
  <h4>It hisses with nothing plugged in &mdash; that is normal</h4>
  <p>At high gain with no microphone connected, the output is noisy. That noise is R1 and R5
  themselves: every resistor generates thermal noise, and 3.3&nbsp;k&Omega; generates a fair
  amount. Plug a microphone in and its low impedance sits across those resistors and shorts
  most of it out. ESP points to this as a neat demonstration that resistors make noise just by
  existing.</p>
</div>

<h2>Choosing the transistors</h2>
<p>The 2N4403 is a switching transistor that happens to be very quiet, and it is not always
easy to find. ESP says BC559 or BC560 can replace it with a slight increase in noise &mdash; a
noise figure of 1.2&nbsp;dB rather than 0.9&nbsp;dB.</p>
""")

PAGES['gain.html'] = ("Gain control", f"""
<p class="eyebrow">The circuit &mdash; 03</p>
<h1>The gain control</h1>
<p class="lede">One pot, connected between the two halves rather than in the signal path, sets
gain across most of a 60&nbsp;dB range.</p>

<h2>A floating control</h2>
<p>The gain network joins the emitter nodes of the two compound pairs. It is not referenced to
ground: it floats between the halves, which is what ESP means by a common-mode gain control.
The smaller the resistance between the emitters, the more the two halves are coupled, and the
higher the gain.</p>
""" + table(["Part", "Value", "Job"],
            [["R9", "22&nbsp;&Omega;", "The fixed minimum resistance &mdash; sets maximum gain"],
             ["VR1", "10&nbsp;k&Omega;", "The gain control, wired as a variable resistor"],
             ["R14", "100&nbsp;k&Omega;", "Across VR1 &mdash; limits the maximum resistance, so minimum gain"],
             ["C1", "1,000&nbsp;&micro;F", "Keeps the network AC-only, so turning the knob does not disturb DC bias"]],
            ["r", "n", ""]) + """

<h2>How much gain</h2>
<p>ESP gives full gain as 1,000 times, 60&nbsp;dB &mdash; or 56&nbsp;dB in practice with R9 at
22&nbsp;&Omega;. The output stage contributes a fixed 13&nbsp;dB of that; the input stage does
the rest.</p>
<p>C1 has to be large because it sits in series with a resistance as low as 22&nbsp;&Omega;.
Anything smaller and it starts to limit gain at low frequencies. It sees almost no DC, so ESP
notes an ordinary 10 or 16&nbsp;V electrolytic is fine.</p>

<h2>The pot's taper matters</h2>
<p>Gain rises steeply as resistance falls towards zero, so a linear pot would cram almost all
of the useful range into the last few degrees of rotation. ESP recommends a <strong>reverse
log</strong> pot, which spreads the range across the knob &mdash; or a rotary switch with
6&nbsp;dB steps covering the range, which also makes settings repeatable and stereo pairs
matchable.</p>
<p>A reverse log 10&nbsp;k&Omega; pot is the one part ESP flags as hard to find. For a desk
where two channels might need to match, the switch is worth considering on that ground alone.</p>
""")

PAGES['output.html'] = ("Output stage", f"""
<p class="eyebrow">The circuit &mdash; 04</p>
<h1>The output stage</h1>
<p class="lede">A standard op-amp difference amplifier turns the input stage's two outputs
into one balanced line output, and rejects whatever is common to both.</p>

<h2>How it works</h2>
<p>Each input-stage output sits at about &minus;8.3&nbsp;V, so C2 and C3 block that DC before
it reaches the op amp. R10 and R11, 22&nbsp;k&Omega;, feed the two op-amp inputs; R12 and R13,
100&nbsp;k&Omega;, set the gain at 100/22&nbsp;=&nbsp;4.55, about 13&nbsp;dB.</p>
<p>A difference amplifier only works well if its resistor pairs match. Any mismatch between
R10/R11 or R12/R13 lets common-mode signal through as if it were audio. ESP recommends 1%
metal film throughout, and the stage achieves well over 60&nbsp;dB of CMRR &mdash; better than
any microphone cable needs.</p>

<h2>Headroom</h2>
<p>Because the output stage has fixed gain, it also fixes how large a signal the preamp can
take. ESP gives the ceiling as about 1.5&nbsp;V RMS at the input before clipping, which with a
typical microphone corresponds to more than 150&nbsp;dB SPL. Practically, the preamp will not
be the thing that overloads.</p>

<h2>Balanced output</h2>
<p>OUT+ comes from the op amp through R15, 100&nbsp;&Omega;. OUT&minus; is taken to ground
through R16, also 100&nbsp;&Omega;. So only one leg carries signal, but both legs present the
same 100&nbsp;&Omega; impedance. That is an <strong>impedance-balanced</strong> output: the
receiving input still rejects hum picked up along the cable, because the hum arrives equally
on both legs, and it costs one op amp rather than two.</p>

<h2>Which op amp</h2>
<p>ESP's text suggests a TL071 or similar; their Figure 1 shows an NE5532. Either works here:
by this point the signal is large and op-amp noise is swamped. The NE5532 is the natural choice
for this desk, which already stocks it for the compressor. It is a dual, so the unused half
needs tying off &mdash; see <a href="build.html">Building it</a>.</p>

<div class="note warn">
  <h4>Never into a phantom-powered input</h4>
  <p>ESP warns that this preamp must not be connected to a mixer input supplying phantom power:
  48&nbsp;V on the output destroys the op amp. If the output could ever meet a phantom-powered
  input, protect it with zener diodes, series resistors and coupling capacitors.</p>
</div>
""")

PAGES['phantom.html'] = ("48 V phantom power", f"""
<p class="eyebrow">In the desk &mdash; 05</p>
<h1>48&nbsp;V phantom power</h1>
<p class="lede">Condenser microphones need power, and they get it down the same cable as the
audio. Project 66 does not provide it. <a href="{P96}">Project 96</a> shows how to add it
&mdash; and the preamp cannot survive without the protection that comes with it.</p>

<h2>What phantom power is</h2>
<p>The same DC voltage, 48&nbsp;V, is applied to both audio legs through a pair of equal
resistors. Because both legs rise together, the voltage is invisible to a balanced input
&mdash; it is purely common-mode &mdash; while a condenser microphone can draw its operating
current from it. Dynamic microphones, wired balanced, simply ignore it.</p>
""" + table(["Parameter", "Value"],
            [["Feed resistors", "6.81&nbsp;k&Omega;, 0.1%, one per leg"],
            ["Maximum current", "14&nbsp;mA, into a short circuit"],
             ["Typical microphone", "around 10&nbsp;mA"]],
            ["r", "n"]) + """
<p>The 14&nbsp;mA is simply 48&nbsp;V through the two feed resistors in parallel. That series resistance is also why phantom power is weak by design: a microphone that needs
around 10&nbsp;V to operate is left with only a few milliamps to work with.</p>

<h2>Why Project 66 cannot take it as drawn</h2>
<p>Project 66's inputs connect straight to the transistor bases. There is no capacitor in the
way. Put 48&nbsp;V on those inputs and it goes directly into Q1 and Q3. ESP says as much in
the Project 66 article: adding phantom power to the input needs a protection scheme like the
one in Project 96's Figure 2.</p>

<h2>What goes in front of the preamp</h2>
<p>Project 96 has two halves. Its Figure 1 is a mains power supply that makes the 48&nbsp;V
rail &mdash; a 25&ndash;30&nbsp;V AC transformer, a voltage doubler, and a discrete regulator.
<strong>A 500-series module does not need that half</strong>, because the rack supplies
48&nbsp;V (see <a href="rack.html">In a 500-series slot</a>). It is Figure 2, the distribution
circuit, that belongs on the preamp card:</p>
""" + table(["Part", "Value", "Job"],
            [["Feed resistors", "6.8&nbsp;k&Omega;, matched to within 10&nbsp;&Omega;", "Carry 48&nbsp;V to each leg"],
             ["Coupling capacitors", "22&nbsp;&micro;F, 50&nbsp;V or higher", "Block 48&nbsp;V from the preamp input"],
             ["Protection zeners", "10&nbsp;V, 1&nbsp;W, one per leg", "Clamp the transient when a cable is plugged in live"],
             ["Series resistors", "10&nbsp;&Omega;", "Limit the zeners' peak current"]],
            ["r", "n", ""]) + """

<h3>Matching the feed resistors</h3>
<p>The two feed resistors must be equal or the phantom voltage is no longer purely common-mode,
and the preamp's hum rejection suffers. ESP makes a sharp point here: two 0.1% resistors at
opposite ends of their tolerance can differ by 13.62&nbsp;&Omega;. Sorting ordinary 1%
6.8&nbsp;k&Omega; resistors with a multimeter to within 10&nbsp;&Omega; does better, and costs
less. Project 96 also shows a Wheatstone bridge for matching to about 1&nbsp;&Omega;.</p>

<h3>The coupling capacitors</h3>
<p>Their positive ends face the microphone, where the 48&nbsp;V is. ESP chose 22&nbsp;&micro;F
to reach 12&nbsp;Hz into a typical 1.2&nbsp;k&Omega; preamp input. Project 66's input is higher,
3.3&nbsp;k&Omega; per leg, so the same capacitors roll off lower still &mdash; our figure,
about 2&nbsp;Hz. For a cost-no-object build ESP suggests 10&nbsp;&micro;F/50&nbsp;V polyester
capacitors instead, which avoid any colouration from electrolytics.</p>

<h3>The zeners</h3>
<p>A microphone cable is a capacitor. Plug one in, or switch phantom on, and the cable and the
coupling capacitors charge or discharge abruptly &mdash; ESP describes the resulting surge
through the zeners as the reason they must be rugged, and 1&nbsp;W parts are the industry norm.
Without them, that transient lands on the input transistors.</p>

<h2>What changes when phantom is fitted</h2>
""" + table(["", "Without phantom", "With phantom"],
            [["Input impedance", "6.6&nbsp;k&Omega;", "4.4&nbsp;k&Omega;"],
             ["Coupling capacitor roll-off", "&mdash;", "about 2&nbsp;Hz"],
             ["Microphone types", "Dynamic", "Dynamic and condenser"]],
            ["r", "n", "n"]) + """
<p>Both new figures are ours. The input impedance falls because the two 6.8&nbsp;k&Omega;
feed resistors, 13.6&nbsp;k&Omega; in series across the input, now sit in parallel with the
preamp's own 6.6&nbsp;k&Omega;. 4.4&nbsp;k&Omega; is still double the 2.2&nbsp;k&Omega; that professional preamps treat as
the minimum, so loading is not a concern.</p>

<div class="note warn">
  <h4>Switching it</h4>
  <p>Turning phantom on or off charges or discharges the coupling capacitors through the input,
  and the result is a loud bang through everything downstream. ESP's distribution board offers a
  &ldquo;silent&rdquo; switch for exactly this reason. Without one, turn the desk's output down
  before switching. Standard studio practice, beyond what the articles cover: never switch phantom
  with a ribbon microphone connected.</p>
</div>
""")

PAGES['rack.html'] = ("In a 500-series slot", """
<p class="eyebrow">In the desk &mdash; 06</p>
<h1>In a 500-series slot</h1>
<p class="lede">ESP designed Project 66 as a standalone board on &plusmn;15&nbsp;V. The desk
runs every module in the 500-series format instead, which changes the supply, fixes the panel
size, and decides where phantom power comes from.</p>

<h2>The format</h2>
<p>500-series is a standard for small audio modules that slot into a shared rack or
&ldquo;lunchbox&rdquo;. The rack provides power and audio connections; each module is a card with
a front panel. Any module fits any slot.</p>
""" + table(["Constraint", "Value"],
            [["Panel", "1.5&nbsp;in &times; 5.25&nbsp;in &mdash; 38.10 &times; 133.35&nbsp;mm"],
             ["Connector", "15-pin, 0.156&nbsp;in card edge"],
             ["Supply", "&plusmn;16&nbsp;V, 130&nbsp;mA per rail"],
             ["Phantom", "+48&nbsp;V, provided by the rack on the standard's pin 15"],
             ["Audio", "Balanced in and out"]],
            ["r", "n"]) + """

<h2>&plusmn;16&nbsp;V rather than &plusmn;15&nbsp;V</h2>
<p>An extra volt on each rail is harmless for every part here, but it shifts the input stage's
operating point slightly. Recalculating ESP's figures for &plusmn;16&nbsp;V &mdash; these are
ours, not measured:</p>
""" + table(["", "&plusmn;15&nbsp;V (ESP)", "&plusmn;16&nbsp;V (ours)"],
            [["Current per input half", "3.05&nbsp;mA", "3.27&nbsp;mA"],
             ["Emitter node", "+0.65&nbsp;V", "+0.65&nbsp;V"],
             ["Output node", "&minus;8.3&nbsp;V", "&minus;8.8&nbsp;V"]],
            ["r", "n", "n"]) + """
<p>About 7% more current, with the output node still comfortably inside both rails. No value
needs changing.</p>

<h2>Current budget</h2>
<p>The two input halves draw about 6.5&nbsp;mA from each rail between them. The op amp adds its
own quiescent current &mdash; an NE5532 is typically around 8&nbsp;mA for the whole package, a
TL071 far less. Either way the preamp needs <strong>well under 20&nbsp;mA per rail</strong>
against 130&nbsp;mA available. Phantom power is drawn from the separate 48&nbsp;V rail and does
not count against this.</p>

<h2>Keeping the rails quiet</h2>
<p>A preamp at 56&nbsp;dB of gain amplifies whatever reaches its supply along with the signal.
ESP recommends a post-filter of 10&nbsp;&Omega; and 470&nbsp;&micro;F after the regulators. In a
rack the rails are shared with every other module, which makes that filter more worthwhile, not
less. At this preamp's current the 10&nbsp;&Omega; costs about 0.15&nbsp;V &mdash; nothing.</p>

<div class="note warn">
  <h4>This desk's chassis does not carry 48&nbsp;V</h4>
  <p>The 500-series standard puts +48&nbsp;V on pin 15. This desk's chassis wiring leaves pin 15
  unconnected &mdash; it is listed as P48-NC. As built, a preamp slot receives
  <strong>no phantom power</strong>. Either pin 15 is wired to a 48&nbsp;V supply in the chassis,
  or phantom is generated on the preamp card from the &plusmn;16&nbsp;V rails, which costs
  current, board space and a converter's noise right beside a 56&nbsp;dB gain stage. Wiring the
  chassis is the cleaner of the two.</p>
</div>

<h2>Connector pins</h2>
<p>The preamp uses the same audio pins as the rest of the desk:</p>
""" + table(["Pin", "Signal", "Preamp use"],
            [["10", "IN+", "Microphone hot"], ["8", "IN&minus;", "Microphone cold"],
             ["2", "OUT+", "R15, the driven output leg"], ["4", "OUT&minus;", "R16, the impedance-balanced leg"],
             ["5", "AGND", "Signal ground"], ["12 / 14", "+16&nbsp;V / &minus;16&nbsp;V", "Supply"],
             ["13", "PGND", "Power ground"], ["15", "P48", "Phantom &mdash; not connected in this chassis"]],
            ["n", "", ""]) + """

<h2>The panel</h2>
<p>The preamp needs very little front-panel space: a gain control &mdash; a reverse-log pot, or a
6&nbsp;dB-step switch &mdash; and a phantom switch. That is a comfortable fit on a 38&nbsp;mm panel,
which leaves room for anything else the desk decides a preamp slot should have.</p>
""")

PAGES['build.html'] = ("Building it", f"""
<p class="eyebrow">In the desk &mdash; 07</p>
<h1>Building it</h1>
<p class="lede">Practical notes, mostly ESP's, plus the three changes the desk needs.</p>

<h2>Parts</h2>
""" + table(["Part", "Advice", "Why"],
            [["Resistors", "1% metal film throughout", "The difference amplifier's CMRR depends on matching; metal film is also the quietest common type"],
             ["2N4403", "BC559 or BC560 if unavailable", "Slightly noisier: 1.2&nbsp;dB noise figure rather than 0.9&nbsp;dB"],
             ["Capacitors", "No bead tantalums", "ESP: they go leaky and crackle"],
             ["C1, 1,000&nbsp;&micro;F", "10 or 16&nbsp;V electrolytic is fine", "Almost no DC across it"],
             ["Other electrolytics", "25&nbsp;V or higher", "They see the full rails"],
             ["C6, 100&nbsp;nF", "Multilayer ceramic, at the op-amp pins", "Local decoupling only works when it is local"],
             ["VR1", "Reverse log 10&nbsp;k&Omega;, or a stepped switch", 'See <a href="gain.html">Gain control</a>']],
            ["r", "", ""]) + """

<h2>Changes for this desk</h2>
""" + table(["Change", "Reason"],
            [["Add Project 96's Figure 2 distribution circuit at the input",
              "Phantom power, and the protection the input needs to survive it"],
             ["Add a 10&nbsp;&Omega; / 470&nbsp;&micro;F post-filter on each rail",
              "The rack's rails are shared with other modules"],
             ["Tie off the unused half of the NE5532",
              "ESP's figure uses one half. A floating op amp can oscillate and inject noise: "
              "ground its non-inverting input and connect its output to its inverting input"]],
            ["r", ""]) + """

<h2>Checking it works</h2>
<ol>
  <li>Power up with no microphone and gain at minimum. Measure the emitter nodes:
  about +0.65&nbsp;V. Measure the output nodes: about &minus;8.8&nbsp;V on &plusmn;16&nbsp;V.
  ESP notes a radically different reading means a construction mistake.</li>
  <li>Check both halves read the same. A mismatch between them costs common-mode rejection.</li>
  <li>Turn the gain up with nothing plugged in. It should hiss &mdash; that is R1 and R5, and it is
  normal.</li>
  <li>Plug a dynamic microphone in. The hiss should drop.</li>
  <li>Only then test phantom power, with a condenser microphone, and with the output turned
  down.</li>
</ol>
""")

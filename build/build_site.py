#!/usr/bin/env python3
"""Builds the whole documentation site into ../site.

  python3 build/build_site.py

Each module in modules.py renders into site/<slug>/, sharing one stylesheet and one copy of
the viewer. The home page lists the modules and says plainly which are real and which are
templates.
"""
import os, sys, shutil, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SITE = os.path.join(ROOT, 'site')
sys.path.insert(0, HERE)

import shell
from modules import MODULES, GUIDES

BADGE = {'built':    ('Built',    'ok'),
         'designed': ('Designed', 'ok'),
         'progress': ('In progress', 'warn'),
         'planned':  ('Template', 'warn'),
         'guide':    ('Guide',    'ok')}


def copy_module_assets(mod):
    """Artwork that another repository generates. Copied in, not linked, so the site stays
    buildable and publishable with no sibling checkouts present."""
    if not mod.repo:
        return
    repo = os.path.join(ROOT, '..', mod.repo)
    for src, dst in [('panel/faceplate-mockup.svg', 'img/panel-mockup.svg'),
                     ('panel/faceplate-mockup-bone.svg', 'img/panel-bone.svg'),
                     ('panel/faceplate-drawing.svg', 'img/panel-drawing.svg'),
                     # the simulation's plots and the parts list, where a module has them
                     ('kicad/sim/results/compression.png', 'img/sim-compression.png'),
                     ('kicad/sim/results/attack_release.png', 'img/sim-attack_release.png'),
                     ('kicad/sim/results/frequency.png', 'img/sim-frequency.png'),
                     ('kicad/sim/results/meters.png', 'img/sim-meters.png'),
                     ('bom/altronics.csv', 'parts/altronics.csv')]:
        s = os.path.join(repo, src)
        if os.path.exists(s):
            d = os.path.join(SITE, mod.slug, dst)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(s, d)
            print('    copied %s' % dst)


def build_module(mod):
    out = os.path.join(SITE, mod.slug)
    os.makedirs(out, exist_ok=True)
    shell.DATA_DIR = os.path.join(out, 'data')       # fig() inlines from here at import time
    copy_module_assets(mod)                          # before the import: pages read the copies
    content = importlib.import_module(mod.content)
    mod.bind(content.NAV, content.PAGES)
    for fname in mod.order:
        title, body = mod.pages[fname]
        open(os.path.join(out, fname), 'w').write(shell.shell(mod, fname, title, body))
    print('  %-10s %2d pages -> site/%s/' % (mod.slug, len(mod.order), mod.slug))


def cards_for(mods):
    cards = []
    for m in mods:
        label, tone = BADGE[m.status]
        pages = len(m.order)
        cards.append(f"""  <a class="mod {tone}" href="{m.slug}/index.html">
    <span class="mod-tag">{label}</span>
    <h3>{m.name}</h3>
    <p>{m.tagline}</p>
    <span class="mod-more">{pages} pages &rarr;</span>
  </a>""")
    return chr(10).join(cards)


def home():
    return shell.head('%s &mdash; module documentation' % shell.SUITE,
                      'Documentation for the UTS Mini Mixing Desk 500-series modules.',
                      up='') + f"""
<div class="shell home">
<main class="main"><div class="wrap">
<img class="home-mark" src="brand/mark.svg" width="72" height="72" alt="">
<p class="eyebrow">500-series</p>
<h1>{shell.SUITE}</h1>
<p class="lede">A rack of 500-series modules built from ordinary parts. This site documents
each one section by section &mdash; what the circuit does, how it does it, and why it was
built that way.</p>

<div class="mods">
{cards_for(MODULES)}
</div>

<h2>Guides</h2>
<p>Shared by every module.</p>
<div class="mods">
{cards_for(GUIDES)}
</div>

<h2>How far along each module is</h2>
<p>The compressor has been designed and both of its boards are laid out and routed: a main
card and a front board behind the faceplate, joined by a ribbon. The whole circuit has been
simulated in ngspice and its values corrected from that, and it has a parts list drawn from
Altronics' stock. Nothing has been ordered or built yet. Its pages are generated from a netlist that the KiCad schematic is verified
against, pin by pin, so the figures in it come from the design rather than from memory.</p>
<p>The equaliser is <strong>in progress</strong>: its two parametric bands are drawn with
values on one sheet, and their response is worked out from that sheet and matches the team's
LTspice run. The high-pass, low-pass and gain stages are on sheets of their own, and nothing is
wired to the card edge yet.</p>
<p>The preamp is also <strong>in progress</strong>: its schematic is drawn and its board is
placed and routed, but no component values have been chosen. Its pages are written from its
KiCad sheet, with the schematic drawn from that file.</p>

<h2>The format</h2>
<p>Every module shares the same constraints, which is most of what makes a rack of them
work together.</p>
<div class="tw"><table>
<thead><tr><th class="r">Constraint</th><th class="n">Value</th></tr></thead>
<tbody>
<tr><td class="r">Panel</td><td class="n">38.10 &times; 133.35 &times; 3.18 mm</td></tr>
<tr><td class="r">Connector</td><td class="n">15-pin, 0.156&Prime; card edge</td></tr>
<tr><td class="r">Supply</td><td class="n">&plusmn;16 V, 130 mA per rail</td></tr>
<tr><td class="r">Audio</td><td class="n">Balanced in and out</td></tr>
</tbody></table></div>

<footer>
  {shell.SUITE} &middot; documentation site &middot; one section per module<br>
  Performance figures are calculated or simulated from the designs, not measured on hardware.
</footer>
</div></main>
</div></body></html>
"""


if __name__ == '__main__':
    print('building %s' % SITE)
    for m in MODULES + GUIDES:
        build_module(m)
    open(os.path.join(SITE, 'index.html'), 'w').write(home())
    print('  home page -> site/index.html')
    total = sum(len(m.order) for m in MODULES + GUIDES) + 1
    print('%d pages across %d modules and %d guide(s)' % (total, len(MODULES), len(GUIDES)))

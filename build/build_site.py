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
from modules import MODULES

BADGE = {'built':    ('Built',    'ok'),
         'designed': ('Designed', 'ok'),
         'planned':  ('Template', 'warn')}


def copy_module_assets(mod):
    """Artwork that another repository generates. Copied in, not linked, so the site stays
    buildable and publishable with no sibling checkouts present."""
    if not mod.repo:
        return
    panel = os.path.join(ROOT, '..', mod.repo, 'panel')
    img = os.path.join(SITE, mod.slug, 'img')
    for src, dst in [('faceplate-mockup.svg', 'panel-mockup.svg'),
                     ('faceplate-mockup-bone.svg', 'panel-bone.svg'),
                     ('faceplate-drawing.svg', 'panel-drawing.svg')]:
        s = os.path.join(panel, src)
        if os.path.exists(s):
            os.makedirs(img, exist_ok=True)
            shutil.copyfile(s, os.path.join(img, dst))
            print('    copied %s' % dst)


def build_module(mod):
    out = os.path.join(SITE, mod.slug)
    os.makedirs(out, exist_ok=True)
    shell.DATA_DIR = os.path.join(out, 'data')       # fig() inlines from here at import time
    content = importlib.import_module(mod.content)
    mod.bind(content.NAV, content.PAGES)
    copy_module_assets(mod)
    for fname in mod.order:
        title, body = mod.pages[fname]
        open(os.path.join(out, fname), 'w').write(shell.shell(mod, fname, title, body))
    print('  %-10s %2d pages -> site/%s/' % (mod.slug, len(mod.order), mod.slug))


def home():
    cards = []
    for m in MODULES:
        label, tone = BADGE[m.status]
        pages = len(m.order)
        cards.append(f"""  <a class="mod {tone}" href="{m.slug}/index.html">
    <span class="mod-tag">{label}</span>
    <h3>{m.name}</h3>
    <p>{m.tagline}</p>
    <span class="mod-more">{pages} pages &rarr;</span>
  </a>""")
    return shell.head('%s &mdash; module documentation' % shell.SUITE,
                      'Documentation for the UTS Mini Mixing Desk 500-series modules.',
                      up='') + f"""
<div class="shell home">
<main class="main"><div class="wrap">
<p class="eyebrow">500-series</p>
<h1>{shell.SUITE}</h1>
<p class="lede">A rack of 500-series modules built from ordinary parts. This site documents
each one section by section &mdash; what the circuit does, how it does it, and why it was
built that way.</p>

<div class="mods">
{chr(10).join(cards)}
</div>

<h2>What "template" means</h2>
<p>Only the compressor has been designed. Its pages are generated from a netlist that the
KiCad schematic is verified against, pin by pin, so the figures in it come from the design
rather than from memory.</p>
<p>The preamp and equaliser sections are <strong>templates</strong>. They carry no circuit
values, no part numbers and no performance figures, because none exist yet. What they do
carry is the shape of the work: which sections a module needs, and which decisions have to
be made before any of it can be drawn. They are checklists, not documentation.</p>

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
  Performance figures are calculated from the designs, not measured on hardware.
</footer>
</div></main>
</div></body></html>
"""


if __name__ == '__main__':
    print('building %s' % SITE)
    for m in MODULES:
        build_module(m)
    open(os.path.join(SITE, 'index.html'), 'w').write(home())
    print('  home page -> site/index.html')
    total = sum(len(m.order) for m in MODULES) + 1
    print('%d pages across %d modules' % (total, len(MODULES)))

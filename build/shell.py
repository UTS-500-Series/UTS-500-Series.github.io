#!/usr/bin/env python3
"""Shared page shell and content helpers for the UTS 500-series documentation site.

One site, one section per module. Each module renders into site/<slug>/ with its own
left-hand nav; style.css, viewer.js and the cytoscape bundle live once at site/ and are
shared, which is why every shared asset href carries a '../' prefix while per-module
figures (img/, data/) stay relative to the page.
"""
import os, json

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&'
         'family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">')

SUITE = "UTS Mini Mixing Desk"

# Set by build_site.py before a module's content is imported, because fig() inlines the
# viewer payload at import time and each module keeps its own data/ directory.
DATA_DIR = None


def fig(name, caption, note=""):
    """Interactive viewer: the real schematic with clickable parts, plus the same sheet
    as a netlist graph. Sheet data is inlined so it works from file:// too."""
    with open(os.path.join(DATA_DIR, '%s.json' % name)) as f:
        payload = f.read()
    return f"""<div class="iv" id="iv-{name}">
  <div class="iv-bar">
    <button class="iv-tab on" data-view="schematic">Schematic</button>
    <button class="iv-tab" data-view="graph">Connections</button>
    <span class="iv-sp"></span>
    <input class="iv-find" type="search" placeholder="find R14, VBIAS…" aria-label="Find part or net">
    <button class="iv-btn iv-zout" title="Zoom out">&minus;</button>
    <button class="iv-btn iv-zin" title="Zoom in">+</button>
    <button class="iv-btn iv-lay" title="Change graph layout">Flow</button>
    <button class="iv-btn iv-zres" title="Fit">Fit</button>
  </div>
  <div class="iv-body"></div>
  <div class="iv-key">
    <span class="iv-trace"></span>
    <span class="iv-sp"></span>
    <span class="k sig">audio</span><span class="k ctl">control</span>
    <span class="k pwr">supply</span><span class="k gnd">ground</span>
    <span class="k dot">junction</span>
  </div>
  <div class="iv-foot">
    <span>{caption}</span>
    <a href="img/{name}.svg" target="_blank" rel="noopener">Open the plain schematic &rarr;</a>
  </div>
  <script type="application/json">{payload}</script>
</div>{note}"""


def pic(name, caption, note=""):
    """Static figure. The panel drawings are not schematic sheets, so they get a plain
    image rather than the interactive viewer."""
    return f"""<figure>
  <div class="pane tall"><img src="img/{name}" alt="{caption}" loading="lazy"></div>
  <figcaption><span>{caption}</span><a href="img/{name}" target="_blank" rel="noopener">Open full size &rarr;</a></figcaption>
</figure>{note}"""


def table(headers, rows, cls=None):
    cls = cls or [''] * len(headers)
    h = ''.join('<th class="%s">%s</th>' % (c, x) for x, c in zip(headers, cls))
    b = ''.join('<tr>%s</tr>' % ''.join('<td class="%s">%s</td>' % (c, x)
                for x, c in zip(r, cls)) for r in rows)
    return '<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, b)


def head(title, description, up='../'):
    """Everything from <!doctype> to the opening <body>. `up` is the hop back to site/."""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{FONTS}
<link rel="stylesheet" href="{up}style.css">
<script>
/* Runs before paint so a stored preference does not flash narrow first. */
try {{
  if (localStorage.getItem('uts-width') === 'wide')
    document.documentElement.dataset.width = 'wide';
}} catch (e) {{}}
</script>
<script src="{up}vendor/cytoscape.min.js" defer></script>
<script src="{up}viewer.js" defer></script>
</head><body>"""


def shell(mod, fname, title, body):
    """One documentation page inside a module section."""
    nav = []
    for group_head, group in mod.nav:
        nav.append('<h4>%s</h4>' % group_head)
        for href, num, label in group:
            on = ' class="on"' if href == fname else ''
            nav.append('<a href="%s"%s><i>%s</i><span>%s</span></a>' % (href, on, num, label))
    order, titles = mod.order, mod.titles
    i = order.index(fname)
    prev = ('<a href="%s">&larr; %s</a>' % (order[i-1], titles[order[i-1]])) if i > 0 else '<span></span>'
    nxt = ('<a href="%s">%s &rarr;</a>' % (order[i+1], titles[order[i+1]])) if i < len(order)-1 else '<span></span>'
    return head('%s &middot; %s &mdash; %s' % (title, SUITE, mod.name),
                mod.description) + f"""
<div class="shell">
<aside class="side">
  <a class="brand" href="../index.html"><b>{SUITE}</b><span>{mod.name} module</span></a>
  <button class="menu" onclick="document.querySelector('nav').classList.toggle('open')">Contents</button>
  <nav>{''.join(nav)}</nav>
  <div class="side-foot">
    <button class="wbtn" id="wbtn" type="button" aria-pressed="false">
      <span class="wbtn-ico" aria-hidden="true"></span><span class="wbtn-txt">Wide layout</span>
    </button>
  </div>
</aside>
<main class="main"><div class="wrap">
{body}
<div class="next">{prev}{nxt}</div>
<footer>
  {SUITE} &mdash; {mod.name} &middot; {mod.footer}<br>
  <a href="../index.html">All modules</a>
</footer>
</div></main>
</div></body></html>
"""

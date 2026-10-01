"""The "Design files" page every module carries: its KiCad schematics and boards, exported.

Built from site/<slug>/files/manifest.json, which export_kicad.py writes alongside the
exports themselves, so this page needs neither KiCad nor the module repositories to build.
"""
import json, os
from shell import table

VIEWS = [('top', 'Top'), ('angle', 'Angled'), ('bottom', 'Bottom')]


def _fig(path, caption, cls=''):
    return f"""<figure>
  <div class="pane{cls}"><img src="{path}" alt="{caption}" loading="lazy"></div>
  <figcaption><span>{caption}</span><a href="{path}" target="_blank" rel="noopener">Open full size &rarr;</a></figcaption>
</figure>"""


def _schematic(s, m):
    pdf = [f for f in s['files'] if f.endswith('.pdf')]
    svgs = [f for f in s['files'] if f.endswith('.svg')]
    blob = '%s/blob/%s/%s' % (m['repo'], m['commit'], s['source'].replace(' ', '%20'))
    out = [f"""<h3>{s['label']}</h3>
<p><a href="{blob}"><code>{s['source']}</code></a>. The PDF has every sheet;
<a href="files/{pdf[0]}">download it</a>.</p>"""]
    if len(svgs) == 1:
        out.append(_fig('files/' + svgs[0], s['label']))
    else:
        label = lambda f: f[len(s['name']):-4].lstrip('-') or 'root sheet'
        out.append('<p>One SVG per sheet: %s</p>' % ' &middot; '.join(
            '<a href="files/%s">%s</a>' % (f, label(f)) for f in svgs))
    return '\n'.join(out)


def _board(b, m):
    st = b['stats']
    blob = '%s/blob/%s/%s' % (m['repo'], m['commit'], b['source'].replace(' ', '%20'))
    head = f"<h3>{b['label']}</h3>\n<p><a href=\"{blob}\"><code>{b['source']}</code></a></p>"
    if not b['files']:
        why = 'no parts placed' if not st['footprints'] else \
              '%d footprints imported but no board outline drawn' % st['footprints']
        return head + f"\n<p>Not laid out yet: {why}, so there is nothing to render.</p>"
    name = b['name']
    counts = table(["", "Count"],
                   [["Footprints", st['footprints']], ["Track segments", st['segments']],
                    ["Vias", st['vias']], ["Copper pours", st['zones']]], ["", "r"])
    renders = '<div class="renders">%s</div>' % ''.join(
        _fig('files/%s-3d-%s.png' % (name, v), '3D render, %s' % label.lower(), ' flush')
        for v, label in VIEWS)
    return '\n'.join([head, counts, renders,
                      # 'tall' caps the height, so an upright board doesn't run to several screens
                      _fig('files/%s-front.svg' % name, 'Front: copper, mask, silkscreen and outline', ' tall'),
                      _fig('files/%s-back.svg' % name, 'Back, mirrored as seen from underneath', ' tall'),
                      '<p>Every layer, one per page: <a href="files/%s-layers.pdf">%s-layers.pdf</a>.</p>'
                      % (name, name)])


def page(slug, number):
    """(title, body) for site/<slug>/files.html."""
    here = os.path.dirname(os.path.abspath(__file__))
    m = json.load(open(os.path.join(here, '..', 'site', slug, 'files', 'manifest.json')))
    commit = '<a href="%s/commit/%s"><code>%s</code></a>' % (m['repo'], m['commit'], m['commit'])
    body = [f"""<p class="eyebrow">Practical &mdash; {number}</p>
<h1>Design files</h1>
<p class="lede">The KiCad schematics and boards, exported straight from the repository so they can
be read, printed or downloaded without KiCad.</p>
<p>Exported from <a href="{m['repo']}">{m['repo'].rsplit('/', 1)[1]}</a> at {commit}
({m['date']}) with KiCad {m['kicad']}. These are snapshots: the repository is the source, and
<code>build/export_kicad.py</code> regenerates this page when it changes.</p>
<h2>Schematics</h2>"""]
    body += [_schematic(s, m) for s in m['schematics']]
    body.append('<h2>Boards</h2>')
    body += [_board(b, m) for b in m['boards']]
    return ("Design files", '\n'.join(body) + '\n')

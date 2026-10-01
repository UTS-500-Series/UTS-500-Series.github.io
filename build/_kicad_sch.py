#!/usr/bin/env python3
"""Draws a KiCad schematic sheet as SVG, and builds its viewer data, with no KiCad installed.

The compressor's images are exported by kicad-cli and its netlist comes from design.py. The
preamp has neither: its repository is a plain KiCad 10 project, and KiCad 10 cannot be
installed where this site is usually built. So this reads the .kicad_sch file directly:

  * the netlist, joined the way eeschema joins it: pins, wires, junctions, labels and power
    symbols that share a point, and wire ends that land on another wire
  * the drawing: symbol bodies and pins from the sheet's own embedded library, placed with
    each symbol's rotation and mirror, then wires, junctions, labels, fields and text

Both come out in sheet millimetres, so the viewer's clickable boxes line up with the image.

    python3 build/_kicad_sch.py --module preamp

needs the module's repository checked out beside this one (see `repo` in modules.py). It
writes site/<slug>/img/schematic.svg and site/<slug>/data/schematic.json, plus a plain
site/<slug>/img/<name>.svg for each extra sheet the content module lists in SHEETS. All are
committed, so building the site never needs the repository.

The drawing is ours, not KiCad's: fonts and a few text placements differ from eeschema's
own export. Connectivity does not depend on the drawing - it is read from the same
coordinates eeschema uses. Standard library only.
"""
import argparse, collections, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)


# ---------------------------------------------------------------- s-expressions

TOKEN = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)


class Str(str):
    """A quoted string, so a value like "1" is not mistaken for a keyword."""


def parse(text):
    stack, cur = [], []
    for m in TOKEN.finditer(text):
        op, cl, q, atom = m.groups()
        if op:
            stack.append(cur); cur = []
        elif cl:
            done, cur = cur, stack.pop(); cur.append(done)
        elif q is not None:
            cur.append(Str(re.sub(r'\\(.)', r'\1', q)))
        elif atom:
            cur.append(atom)
    return cur[0]


def kids(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def kid(node, key):
    k = kids(node, key)
    return k[0] if k else None


def num(v):
    return float(v)


def hidden(node):
    """KiCad 8+ writes (hide yes); older files write a bare `hide` atom inside effects."""
    for n in [node, kid(node, 'effects')]:
        if n is None:
            continue
        if 'hide' in n[1:]:
            return True
        h = kid(n, 'hide')
        if h is not None and (len(h) == 1 or h[1] == 'yes'):
            return True
    return False


# ---------------------------------------------------------------- geometry

def place(px, py, X, Y, rot, mirror):
    """Library point (y up) to sheet point (y down) for a symbol at X,Y."""
    x, y = px, -py
    a = math.radians(rot)
    c, s = round(math.cos(a)), round(math.sin(a))
    x, y = x * c + y * s, -x * s + y * c
    if mirror == 'x':
        y = -y
    if mirror == 'y':
        x = -x
    return (X + x, Y + y)


def R2(p):
    return (round(p[0], 2), round(p[1], 2))


def onseg(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) > 1e-3:
        return False
    return (min(x1, x2) - 1e-3 <= x <= max(x1, x2) + 1e-3 and
            min(y1, y2) - 1e-3 <= y <= max(y1, y2) + 1e-3)


# ---------------------------------------------------------------- the sheet

class Sheet:
    def __init__(self, path):
        self.root = parse(open(path, encoding='utf-8').read())
        self.libs = {str(s[1]): s for s in kids(kid(self.root, 'lib_symbols') or [], 'symbol')}
        self.symbols = []
        for sy in kids(self.root, 'symbol'):
            if kid(sy, 'lib_id') is None:
                continue
            at = kid(sy, 'at')
            mir = kid(sy, 'mirror')
            unit = kid(sy, 'unit')
            props = {str(p[1]): p for p in kids(sy, 'property')}
            self.symbols.append({
                'node': sy, 'lib': str(kid(sy, 'lib_id')[1]),
                'X': num(at[1]), 'Y': num(at[2]), 'rot': num(at[3]) if len(at) > 3 else 0,
                'mirror': str(mir[1]) if mir else None,
                'unit': int(num(unit[1])) if unit else 1,
                'props': props,
                'ref': str(props['Reference'][2]) if 'Reference' in props else '?',
                'value': str(props['Value'][2]) if 'Value' in props else '',
                'fp': str(props['Footprint'][2]) if 'Footprint' in props else '',
            })

    def units(self, lib, unit):
        """The drawn sub-symbols for one unit: unit 0 is shared by every unit."""
        out = []
        for sub in kids(self.libs[lib], 'symbol'):
            m = re.match(r'.*_(\d+)_(\d+)$', str(sub[1]))
            u, style = int(m.group(1)), int(m.group(2))
            if style <= 1 and u in (0, unit):
                out.append(sub)
        return out

    def pins(self, s):
        for sub in self.units(s['lib'], s['unit']):
            for p in kids(sub, 'pin'):
                at = kid(p, 'at')
                yield p, str(kid(p, 'number')[1]), num(at[1]), num(at[2])

    def is_power(self, s):
        return kid(self.libs[s['lib']], 'power') is not None or s['ref'].startswith('#')

    # ------------------------------------------------------------ netlist

    def netlist(self):
        parent = {}

        def find(a):
            parent.setdefault(a, a)
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def join(a, b):
            parent[find(a)] = find(b)

        points = []
        for s in self.symbols:
            power = self.is_power(s)
            for _, pn, px, py in self.pins(s):
                pt = R2(place(px, py, s['X'], s['Y'], s['rot'], s['mirror']))
                if power:
                    if 'PWR_FLAG' not in s['lib']:
                        points.append((pt, ('NET', s['value'])))
                else:
                    points.append((pt, ('PIN', s['ref'], pn)))
        for k in ('label', 'global_label', 'hierarchical_label'):
            for l in kids(self.root, k):
                at = kid(l, 'at')
                points.append((R2((num(at[1]), num(at[2]))), ('NET', str(l[1]))))
        for j in kids(self.root, 'junction'):
            at = kid(j, 'at')
            p = R2((num(at[1]), num(at[2])))
            points.append((p, ('J', p)))
        wires = [[R2((num(p[1]), num(p[2]))) for p in kids(kid(w, 'pts'), 'xy')]
                 for w in kids(self.root, 'wire')]
        for i, w in enumerate(wires):
            find(('W', i))
            for pt, key in points:
                if onseg(pt, w[0], w[1]):
                    join(key, ('W', i))
            for j, w2 in enumerate(wires):
                if j != i and any(onseg(e, w[0], w[1]) for e in w2):
                    join(('W', j), ('W', i))
        at = collections.defaultdict(list)
        for pt, key in points:
            find(key)
            at[pt].append(key)
        for ks in at.values():
            for k in ks[1:]:
                join(k, ks[0])

        pins, names = collections.defaultdict(set), collections.defaultdict(set)
        for k in list(parent):
            r = find(k)
            if k[0] == 'PIN':
                pins[r].add((k[1], k[2]))
            elif k[0] == 'NET' and k[1]:          # an empty label names nothing
                names[r].add(k[1])
        nets = {}
        for r, ps in pins.items():
            if names[r]:
                name = '/'.join(sorted(names[r]))
            else:
                # eeschema's own convention for an unnamed net: Net-(<ref>-Pad<n>)
                ref, pn = min(ps, key=lambda p: (natkey(p[0]), natkey(p[1])))
                name = 'Net-(%s-Pad%s)' % (ref, pn)
            nets[name] = ps
        return nets

    # ------------------------------------------------------------ drawing

    def extent(self):
        xs, ys = [], []
        for w in kids(self.root, 'wire'):
            for p in kids(kid(w, 'pts'), 'xy'):
                xs.append(num(p[1])); ys.append(num(p[2]))
        for s in self.symbols:
            for _, _, px, py in self.pins(s):
                x, y = place(px, py, s['X'], s['Y'], s['rot'], s['mirror'])
                xs.append(x); ys.append(y)
            for p in s['props'].values():
                if not hidden(p) and str(p[2]):
                    at = kid(p, 'at'); xs.append(num(at[1])); ys.append(num(at[2]))
        for k in ('label', 'global_label', 'text'):
            for l in kids(self.root, k):
                at = kid(l, 'at'); xs.append(num(at[1])); ys.append(num(at[2]))
                if k == 'text':             # notes run rightwards from their anchor
                    xs.append(num(at[1]) + len(str(l[1])) * font_size(l) * 0.6)
        for w in kids(self.root, 'polyline'):
            for p in kids(kid(w, 'pts'), 'xy'):
                xs.append(num(p[1])); ys.append(num(p[2]))
        return min(xs), min(ys), max(xs), max(ys)

    @property
    def origin(self):
        x0, y0, _, _ = self.extent()
        return (math.floor(x0 - 8), math.floor(y0 - 8))

    def svg(self):
        # crop to the drawing: the viewer overlays its hotspots in a 0,0-based box, so the
        # sheet is shifted by self.origin and viewer_data() shifts the boxes to match
        x0, y0, x1, y1 = self.extent()
        ox, oy = self.origin
        W, H = math.ceil(x1 - ox + 8), math.ceil(y1 - oy + 8)
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
               f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
               f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>',
               f'<g transform="translate({-ox:.2f} {-oy:.2f})" '
               'font-family="Helvetica, Arial, sans-serif" stroke-linecap="round" '
               'stroke-linejoin="round">']
        for s in self.symbols:
            out.append(self._symbol(s))
        for w in kids(self.root, 'wire'):
            pts = [(num(p[1]), num(p[2])) for p in kids(kid(w, 'pts'), 'xy')]
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="0.15"/>'
                       % (' '.join('%.2f,%.2f' % p for p in pts), WIRE))
        for k in ('polyline',):
            for w in kids(self.root, k):
                pts = [(num(p[1]), num(p[2])) for p in kids(kid(w, 'pts'), 'xy')]
                out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="0.15" '
                           'stroke-dasharray="1 0.6"/>' % (' '.join('%.2f,%.2f' % p for p in pts), NOTE))
        for j in kids(self.root, 'junction'):
            at = kid(j, 'at')
            out.append('<circle cx="%.2f" cy="%.2f" r="0.46" fill="%s"/>' % (num(at[1]), num(at[2]), WIRE))
        for n in kids(self.root, 'no_connect'):
            at = kid(n, 'at'); x, y, d = num(at[1]), num(at[2]), 0.63
            out.append('<path d="M%.2f %.2fL%.2f %.2fM%.2f %.2fL%.2f %.2f" stroke="#0000C8" '
                       'stroke-width="0.15"/>' % (x-d, y-d, x+d, y+d, x-d, y+d, x+d, y-d))
        for l in kids(self.root, 'label'):
            if str(l[1]):
                out.append(self._label(l, False))
        for l in kids(self.root, 'global_label'):
            out.append(self._label(l, True))
        for t in kids(self.root, 'text'):
            at = kid(t, 'at')
            out.append(text(str(t[1]).replace('\\n', '\n'), num(at[1]), num(at[2]),
                            num(at[3]) if len(at) > 3 else 0, t, NOTE))
        out.append('</g></svg>')
        return '\n'.join(o for o in out if o)

    def _symbol(self, s):
        X, Y, rot, mir = s['X'], s['Y'], s['rot'], s['mirror']
        P = lambda x, y: place(x, y, X, Y, rot, mir)
        lib = self.libs[s['lib']]
        power = self.is_power(s)
        body = []
        for sub in self.units(s['lib'], s['unit']):
            for g in sub[2:]:
                if not isinstance(g, list):
                    continue
                body.append(self._graphic(g, P))
            for p, pn, px, py in self.pins(s):
                body.append(self._pin(p, pn, px, py, P, lib, power))
        for name, p in s['props'].items():
            if hidden(p) or name not in ('Reference', 'Value') or not str(p[2]):
                continue
            if power and name == 'Reference':
                continue
            body.append(field(s, p))
        return '<g data-ref="%s">%s</g>' % (esc(s['ref']), ''.join(b for b in body if b))

    def _graphic(self, g, P):
        stroke = kid(g, 'stroke')
        sw = num(kid(stroke, 'width')[1]) if stroke is not None and kid(stroke, 'width') else 0
        sw = sw or 0.254
        fill = kid(g, 'fill')
        ft = str(kid(fill, 'type')[1]) if fill is not None and kid(fill, 'type') else 'none'
        fc = {'background': BODY_FILL, 'outline': BODY}.get(ft, 'none')
        style = 'fill="%s" stroke="%s" stroke-width="%.3f"' % (fc, BODY, sw)
        k = g[0]
        if k == 'rectangle':
            a, b = kid(g, 'start'), kid(g, 'end')
            (ax, ay), (bx, by) = P(num(a[1]), num(a[2])), P(num(b[1]), num(b[2]))
            return '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" %s/>' % (
                min(ax, bx), min(ay, by), abs(bx - ax), abs(by - ay), style)
        if k == 'polyline':
            pts = [P(num(p[1]), num(p[2])) for p in kids(kid(g, 'pts'), 'xy')]
            tag = 'polygon' if fc != 'none' else 'polyline'
            return '<%s points="%s" %s/>' % (tag, ' '.join('%.2f,%.2f' % p for p in pts), style)
        if k == 'circle':
            c, r = kid(g, 'center'), num(kid(g, 'radius')[1])
            cx, cy = P(num(c[1]), num(c[2]))
            return '<circle cx="%.2f" cy="%.2f" r="%.2f" %s/>' % (cx, cy, r, style)
        if k == 'arc':
            a, m, b = (P(num(kid(g, n)[1]), num(kid(g, n)[2])) for n in ('start', 'mid', 'end'))
            return arc(a, m, b, style)
        if k == 'bezier':
            pts = [P(num(p[1]), num(p[2])) for p in kids(kid(g, 'pts'), 'xy')]
            if len(pts) == 4:
                return '<path d="M%.2f %.2fC%.2f %.2f %.2f %.2f %.2f %.2f" %s/>' % (
                    *pts[0], *pts[1], *pts[2], *pts[3], style)
        if k == 'text':
            at = kid(g, 'at')
            x, y = P(num(at[1]), num(at[2]))
            return text(str(g[1]), x, y, 0, g, BODY)
        return ''

    def _pin(self, p, pn, px, py, P, lib, power):
        if hidden(p):
            return ''
        at = kid(p, 'at')
        L = num(kid(p, 'length')[1]) if kid(p, 'length') else 2.54
        a = math.radians(num(at[3]) if len(at) > 3 else 0)
        ex, ey = px + L * round(math.cos(a)), py + L * round(math.sin(a))
        (x1, y1), (x2, y2) = P(px, py), P(ex, ey)
        out = ['<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.15"/>'
               % (x1, y1, x2, y2, BODY)]
        if power or L == 0:
            return ''.join(out)
        dx, dy = x2 - x1, y2 - y1
        vertical = abs(dy) > abs(dx)
        pnum = kid(lib, 'pin_numbers')
        if pnum is None or not hidden(pnum):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            if vertical:
                out.append(text(pn, mx - 0.4, my, 90, None, PINTXT, size=1.0, anchor='middle'))
            else:
                out.append(text(pn, mx, my - 0.4, 0, None, PINTXT, size=1.0, anchor='middle'))
        pnames = kid(lib, 'pin_names')
        name = str(kid(p, 'name')[1])
        if name not in ('', '~') and (pnames is None or not hidden(pnames)):
            off = num(kid(pnames, 'offset')[1]) if pnames is not None and kid(pnames, 'offset') else 0.508
            ux, uy = (dx / L, dy / L) if L else (0, 0)
            nx, ny = x2 + ux * (off + 0.2), y2 + uy * (off + 0.2)
            if vertical:
                out.append(text(name, nx, ny + 0.4 if uy > 0 else ny - 0.4, 90, None, PINNAME,
                                size=1.0, anchor='end' if uy > 0 else 'start', dy=0.35))
            else:
                out.append(text(name, nx, ny, 0, None, PINNAME, size=1.0,
                                anchor='start' if ux > 0 else 'end', dy=0.35))
        return ''.join(out)

    def _label(self, l, glob):
        at = kid(l, 'at')
        x, y, ang = num(at[1]), num(at[2]), num(at[3]) if len(at) > 3 else 0
        name = str(l[1])
        size = font_size(l)
        if not glob:
            # a local label sits just above its wire, its baseline on the wire end
            anchor = 'end' if ang in (180, 270) else 'start'
            rot = 90 if ang in (90, 270) else 0
            return text(name, x, y - 0.3 if not rot else y, rot, None, LABEL, size=size,
                        anchor=anchor, dx=0 if rot else 0, dy=0, ox=-0.3 if rot else 0)
        # global label: a flag outline round the text, pointing at the wire
        w = len(name) * size * 0.62 + size * 1.4
        h = size * 1.6
        d = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[int(ang) % 360]
        # the label's anchor is the flag's point, and the body extends away from the wire
        if d[1] == 0:
            sx = d[0]
            pts = [(x, y), (x + sx * h / 2, y - h / 2), (x + sx * w, y - h / 2),
                   (x + sx * w, y + h / 2), (x + sx * h / 2, y + h / 2)]
            t = text(name, x + sx * (h / 2 + size * 0.3), y, 0, None, LABEL, size=size,
                     anchor='start' if sx > 0 else 'end', dy=size * 0.35)
        else:
            sy = -d[1]
            pts = [(x, y), (x - h / 2, y + sy * h / 2), (x - h / 2, y + sy * w),
                   (x + h / 2, y + sy * w), (x + h / 2, y + sy * h / 2)]
            t = text(name, x + size * 0.35, y + sy * (h / 2 + size * 0.3), 90, None, LABEL,
                     size=size, anchor='end' if sy > 0 else 'start')
        return ('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.15"/>'
                % (' '.join('%.2f,%.2f' % p for p in pts), GLABEL)) + t


# KiCad's default schematic colours, so this reads like the compressor's exported sheets
WIRE, BODY, BODY_FILL = '#009600', '#840000', '#FFFFC2'
FIELD, PINTXT, PINNAME, LABEL, GLABEL, NOTE = '#006464', '#A90000', '#006464', '#000000', '#840000', '#000084'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def font_size(node):
    e = kid(node, 'effects') if node is not None else None
    f = kid(e, 'font') if e is not None else None
    sz = kid(f, 'size') if f is not None else None
    return num(sz[1]) if sz else 1.27


def text(s, x, y, ang, node, colour, size=None, anchor=None, dx=0, dy=None, ox=0):
    """One text item. KiCad positions text by its justification box; SVG by anchor and
    baseline, so centre-justified text is shifted down by a third of its height."""
    size = size or font_size(node)
    just = kid(kid(node, 'effects'), 'justify') if node is not None and kid(node, 'effects') else None
    j = [str(v) for v in just[1:]] if just else []
    if anchor is None:
        anchor = 'start' if 'left' in j else 'end' if 'right' in j else 'middle'
    if dy is None:
        dy = 0 if 'bottom' in j else size if 'top' in j else size * 0.35
    ang = ang % 360
    if ang in (180, 270):            # eeschema keeps text readable: never upside down
        ang -= 180
        anchor = {'start': 'end', 'end': 'start'}.get(anchor, anchor)
    lines = s.split('\n')
    tsp = ''.join('<tspan x="%.2f" dy="%.2f">%s</tspan>' % (0, 0 if i == 0 else size * 1.4, esc(t))
                  for i, t in enumerate(lines))
    if len(lines) == 1:
        tsp = esc(s)
    if ang:
        return ('<text transform="translate(%.2f %.2f) rotate(%d)" x="0" y="%.2f" font-size="%.2f" '
                'text-anchor="%s" fill="%s">%s</text>'
                % (x + ox + dy, y + dx, -ang, 0, size, anchor, colour, tsp))
    return ('<text x="%.2f" y="%.2f" font-size="%.2f" text-anchor="%s" fill="%s">%s</text>'
            % (x + dx, y + dy, size, anchor, colour, tsp)).replace('<tspan x="0.00"', '<tspan x="%.2f"' % (x + dx))


def field(s, p):
    """A symbol's reference or value. Its position is stored in sheet coordinates but its
    angle and justification belong to the library frame, so a field on a rotated symbol is
    placed the way eeschema does it: lay the text box out in the library frame, carry the
    box through the symbol's rotation and mirror, and centre the text in the result."""
    at = kid(p, 'at')
    s_ = str(p[2]); size = font_size(p)
    X, Y, rot, mir = s['X'], s['Y'], s['rot'], s['mirror']
    T = lambda vx, vy: [a - b for a, b in zip(place(vx, -vy, X, Y, rot, mir), (X, Y))]
    ex, ey = T(1, 0), T(0, 1)                   # symbol transform, y-down, orthogonal
    rx, ry = num(at[1]) - X, num(at[2]) - Y
    lx, ly = rx * ex[0] + ry * ex[1], rx * ey[0] + ry * ey[1]   # inverse = transpose
    just = kid(kid(p, 'effects'), 'justify') if kid(p, 'effects') else None
    j = [str(v) for v in just[1:]] if just else []
    L, h = len(s_) * size * 0.6, size
    along = (0, L) if 'left' in j else (-L, 0) if 'right' in j else (-L / 2, L / 2)
    across = (-h, 0) if 'bottom' in j else (0, h) if 'top' in j else (-h / 2, h / 2)
    vert = int(round(num(at[3]) if len(at) > 3 else 0)) % 180 == 90
    if vert:     # vertical text reads upwards, so "along" runs towards -y
        xs, ys = [lx + a for a in across], [ly - a for a in along]
    else:
        xs, ys = [lx + a for a in along], [ly + a for a in across]
    corners = [(x, y) for x in xs for y in ys]
    pts = [(X + x * ex[0] + y * ey[0], Y + x * ex[1] + y * ey[1]) for x, y in corners]
    cx = sum(q[0] for q in pts) / 4; cy = sum(q[1] for q in pts) / 4
    if abs(ex[1]) > 0.5:                       # a 90 or 270 degree symbol turns its fields
        vert = not vert
    return text(s_, cx, cy, 90 if vert else 0, None, FIELD, size=size, anchor='middle',
                dy=size * 0.35)


def arc(a, m, b, style):
    """SVG arc through three points."""
    (x1, y1), (x2, y2), (x3, y3) = a, m, b
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(d) < 1e-9:
        return '<polyline points="%.2f,%.2f %.2f,%.2f" %s/>' % (x1, y1, x3, y3, style)
    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
    r = math.hypot(x1 - ux, y1 - uy)
    cross = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    sweep = 1 if cross > 0 else 0
    return '<path d="M%.2f %.2fA%.2f %.2f 0 0 %d %.2f %.2f" %s/>' % (x1, y1, r, r, sweep, x3, y3, style)


def natkey(s):
    return [(1, int(t)) if t.isdigit() else (0, t) for t in re.findall(r'\d+|\D+', str(s))]


# ---------------------------------------------------------------- viewer data

def viewer_data(sheet, name, w, h, notes, net_class):
    from _data import kind
    nets = sheet.netlist()
    pinnet = {(r, p): n for n, ps in nets.items() for r, p in ps}
    comps = collections.OrderedDict()
    ox, oy = sheet.origin
    for s in sorted(sheet.symbols, key=lambda s: natkey(s['ref'])):
        if sheet.is_power(s):
            continue
        pts = [place(px, py, s['X'], s['Y'], s['rot'], s['mirror']) for _, _, px, py in sheet.pins(s)]
        xs = [p[0] for p in pts] + [s['X']]; ys = [p[1] for p in pts] + [s['Y']]
        pad = 1.6
        b = [min(xs) - pad - ox, min(ys) - pad - oy,
             max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad]
        c = comps.get(s['ref'])
        if c:                                   # multi-unit part: union the boxes
            o = c['box']
            bx0, by0 = min(o[0], b[0]), min(o[1], b[1])
            bx1, by1 = max(o[0] + o[2], b[0] + b[2]), max(o[1] + o[3], b[1] + b[3])
            c['box'] = [round(v, 2) for v in (bx0, by0, bx1 - bx0, by1 - by0)]
        else:
            comps[s['ref']] = {'ref': s['ref'], 'value': s['value'],
                               'fp': s['fp'].split(':')[-1],
                               'kind': kind(s['ref'], s['lib'].split(':')[-1]),
                               'note': notes.get(s['ref'], ''),
                               'box': [round(v, 2) for v in b], 'pins': {}}
        for _, pn, _, _ in sheet.pins(s):
            if (s['ref'], pn) in pinnet:
                comps[s['ref']]['pins'][pn] = pinnet[(s['ref'], pn)]
    for c in comps.values():
        c['pins'] = {k: c['pins'][k] for k in sorted(c['pins'], key=natkey)}
    netlist = [{'name': n, 'cls': net_class(n),
                'pins': sorted(([r, p] for r, p in ps), key=lambda q: (natkey(q[0]), natkey(q[1]))),
                'offsheet': 0}
               for n, ps in sorted(nets.items(), key=lambda kv: natkey(kv[0]))]
    return {'sheet': name, 'w': w, 'h': h, 'components': list(comps.values()), 'nets': netlist}


def main():
    from modules import BY_SLUG
    ap = argparse.ArgumentParser()
    ap.add_argument('--module', default='preamp', help='module slug, see modules.py')
    ap.add_argument('--repo', help='path to the module repository, if not beside this one')
    args = ap.parse_args()
    mod = BY_SLUG[args.module]
    repo = args.repo or os.path.join(ROOT, '..', mod.repo)
    here = os.path.join(ROOT, 'site', mod.slug)
    os.makedirs(os.path.join(here, 'img'), exist_ok=True)
    os.makedirs(os.path.join(here, 'data'), exist_ok=True)
    # the content module holds the sheet name, part notes and net colours, but importing it
    # renders its pages, which inline this script's own output: give it something to inline
    import shell
    shell.DATA_DIR = os.path.join(here, 'data')
    out = os.path.join(here, 'data', 'schematic.json')
    if not os.path.exists(out):
        open(out, 'w').write('{}')
    content = __import__(mod.content)
    src = os.path.join(repo, content.SCH)
    if not os.path.exists(src):
        sys.exit('%s not found. Check out the module repository beside this one.' % src)
    sheet = Sheet(src)
    svg = sheet.svg()
    open(os.path.join(here, 'img', 'schematic.svg'), 'w').write(svg)
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    data = viewer_data(sheet, 'schematic', float(vb.group(1)), float(vb.group(2)),
                       content.NOTES, content.net_class)
    open(out, 'w').write(json.dumps(data, separators=(',', ':')))
    print('schematic  %d parts %d nets  %s x %s mm'
          % (len(data['components']), len(data['nets']), vb.group(1), vb.group(2)))
    # sections drawn on sheets of their own, shown as plain images: name -> path in the repo
    for name, path in getattr(content, 'SHEETS', {}).items():
        open(os.path.join(here, 'img', name + '.svg'), 'w').write(Sheet(os.path.join(repo, path)).svg())
        print('%-10s %s' % (name, path))


if __name__ == '__main__':
    main()

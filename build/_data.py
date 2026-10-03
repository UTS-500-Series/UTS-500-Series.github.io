#!/usr/bin/env python3
"""Builds data/<sheet>.json for the compressor's interactive viewer.

Two things come out of this:
  * component boxes in sheet millimetres, read from the real .kicad_sch files, so the
    clickable overlay lines up with the sheet SVGs kicad-cli exports (page coordinates)
  * the netlist as a bipartite graph (component nodes + net nodes), which is the honest
    way to draw a netlist - a net joins N pins, not 2

Run it against one module:

    python3 build/_data.py --module compressor            # viewer data only
    python3 build/_data.py --module compressor --images   # and the sheet SVGs (needs KiCad)

The module's own repository has to be checked out beside this one. The netlist is read from
the split sheets in kicad/ themselves, joined across sheets by their global labels and power
symbols, the way eeschema joins them; the sheets are drawn from the routed board's
schematic, so this is the circuit that gets built. Nets the sheets leave unnamed take their
name from tools/design.py where its net has exactly the same pins, so the viewer uses the
names the pages do. The data needs no KiCad installed; --images exports each sheet with
kicad-cli into site/<slug>/img/<sheet>.svg, which the viewer draws under its hotspots. The JSON it writes is committed to this
repository, so building and publishing the site never needs the module repositories."""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from modules import BY_SLUG
from _kicad_sch import Sheet, place

POWER  = {'+16V', '-16V', '-5V1', '+16V-IN', '-16V-IN', '+48V-IN', 'VBIAS', 'VREF5', 'VREFA'}
GROUND = {'AGND', 'PGND', 'CHASSIS'}
CONTROL = {'STA','STB','CTRL','CTRL-B','RECT','SC-AMP','SCBUF','SCF','SCSEL','RV3O',
           'RATW','LINKN','ATKO','D7K','RELO','S1','S2','XN','U3BO','KEY','LINK',
           'NINV3A','NINV3B','NINV4A','INV3A','INV4B','LED-A',
           # names the board's sheets give some of the same nets
           'TIMING','GR_METER','GR_REF','LVL_METER','RATIO_CW','RATIO_W','THR_W','ATK_W',
           'REL_W','KEY_SRC','LINK_SW','HPF_A','HPF_B'}

def net_class(n):
    if n in GROUND: return 'gnd'
    if n in POWER: return 'pwr'
    if n in CONTROL: return 'ctl'
    return 'sig'

def natkey(s):
    """Sort key that reads digit runs as numbers: J1 pin 2 sorts before pin 10, and
    C9 before C10. Plain string sort gives 1, 10, 11, ... 2, 3 for anything numbered."""
    return [(1, int(t)) if t.isdigit() else (0, t) for t in re.findall(r'\d+|\D+', str(s))]

KIND = {'R':'res','C':'cap','D':'dio','Q':'tr','U':'ic','RV':'pot','SW':'sw','J':'conn','LED':'led'}
# The refdes prefix is a poor classifier: the meter LEDs are D20-D39 and would draw as plain
# diodes, and an 18-pin display driver would draw as an op-amp triangle. The library symbol
# says what the part actually is, so prefer it and keep the prefix only as a fallback.
SYMKIND = {'R':'res', 'C':'cap', 'C_Polarized':'cap', 'D':'dio', 'D_Zener':'zen', 'LED':'led',
           'BC549':'tr', 'NE5532':'ic', 'LM3914N':'dip', 'R_Potentiometer':'pot',
           'Conn_01x15':'conn', 'OPA1644AIPWR':'ic', 'R_Potentiometer_Dual_Separate':'pot'}
def kind(ref, sym=''):
    if sym in SYMKIND: return SYMKIND[sym]
    if sym.startswith('SW_'): return 'sw'
    m = re.match(r'^(LED|RV|SW|[A-Z]+)', ref)
    return KIND.get(m.group(1), 'other') if m else 'other'

NOTES = {
 'R1':'Sets input CMRR with R2-R4. 0.1% part.','R2':'Sets input CMRR. 0.1% part.',
 'R3':'Sets input CMRR. 0.1% part.','R4':'Difference-amp feedback. 0.1% part.',
 'R7':'Top of the input pad.','R8':'Bottom of the input pad - sets through gain. 75 ohm.',
 'RV1':'Unity-gain trim. The only audio trim in the module.',
 'R14':'Emitter degeneration for Q1.','R15':'Emitter degeneration for Q2.',
 'R16':'Collector load - turns steered current back into voltage.',
 'R17':'Collector load - turns steered current back into voltage.',
 'R18':'Sets the ~3 mA tail current.',
 'R21':'0.1% - pairs with R23 for thump rejection.','R22':'0.1% - pairs with R24.',
 'R23':'0.1% recovery-amp feedback.','R24':'0.1% recovery-amp reference leg.',
 'R45':'Series resistor into the stereo-link bus.',
 'R48':'0 ohm star-ground link. Fit exactly one.',
 'R61':'0.1% - sets the steering rest offset.','R62':'0.1% - sets the steering rest offset.',
 'R68':'Scales the control voltage down to the ~250 mV the steering pair needs.',
 'R74':'Balances U4B bias current against the release network.',
 'Q1':'Signal transconductor. Matched pair with Q2, thermally bonded.',
 'Q2':'Signal transconductor. Matched pair with Q1, thermally bonded.',
 'Q3':'Constant tail current source - about 3 mA, fixed.',
 'Q4':'Emitter follower buffering collector CP.','Q5':'Emitter follower buffering collector CN.',
 'Q6':'Steering - dump side. Matched quad Q6-Q9.','Q7':'Steering - signal side. Matched quad Q6-Q9.',
 'Q8':'Steering - dump side. Matched quad Q6-Q9.','Q9':'Steering - signal side. Matched quad Q6-Q9.',
 'C1':'Input DC block, bipolar.','C2':'Input DC block, bipolar.',
 'C9':'Recovery-amp coupling.','C10':'Recovery-amp coupling.',
 'C14':'Sidechain high-pass with R38, 80-160 Hz across the threshold knob (simulated).',
 'C15':'Timing capacitor - its voltage IS the control signal. Film, low leakage.',
 'D5':'Precision rectifier diode, inside U3B feedback loop.',
 'D6':'Precision rectifier diode, inside U3B feedback loop.',
 'D7':'Separates attack from release - charge in, no discharge back.',
 'D8':'Reverse-polarity clamp, cathode up.','D9':'Reverse-polarity clamp, cathode up.',
 'D10':'5.1 V zener - the reference the tail current source hangs off.',
 'U1':'A: input receiver. B: recovery amplifier.',
 'U2':'A: makeup gain. B: output inverter.',
 'U3':'A: sidechain amp. B: rectifier first half.',
 'U4':'TL072. A: rectifier summer. B: control buffer - low bias current, so the timing cap holds.',
 'U7':'A: level-meter peak detector. B: gain-reduction meter driver.',
 'U9':'LM3914: gain-reduction meter, linear steps.','U10':'LM3914: output-level meter, linear steps.',
 'U5':'A: aux key receiver. B: aux output buffer.',
 'U6':'A: STA reference buffer. B: sidechain input buffer.',
 'RV2':'MAKEUP - 0 to +21 dB.','RV3':'THRESHOLD - wired as a rheostat.',
 'RV4':'RATIO.','RV5':'ATTACK - 2 to 71 ms (simulated).','RV6':'RELEASE - 49 ms to 3.5 s (simulated).',
 'SW1':'Hard bypass - routes the rack straight through.',
 'SW2':'Detector source: this channel, or the aux key input.',
 'SW3':'Shorts out the sidechain high-pass filter.','SW4':'Stereo link to pin 6.',
 'LED1':'Gain-reduction indicator. Brightness tracks compression.',
 'J1':'500-series 15-pin card edge.',
 'J2':'30-way ribbon header to the front board: pots, switches and meters.',
}

# Pinned references that changed between design.py and the board: the meter drivers and their
# decoupling were renumbered when the front board was split off.
OFF_BOARD = 'On the front board, reached through the ribbon header J2.'

DESIGN_REFS = {'U8': 'U9', 'U9': 'U10', 'C39': 'C41', 'C40': 'C42'}
OPAMP_HALVES = {'1': '7', '2': '6', '3': '5', '7': '1', '6': '2', '5': '3'}


PAPER = {'A4': (297, 210), 'A3': (420, 297), 'A2': (594, 420), 'A1': (841, 594), 'A': (279.4, 215.9),
         'B': (431.8, 279.4)}


def paper(sheet):
    """The page size in mm, which is the viewBox kicad-cli gives the sheet's SVG."""
    p = [str(v) for v in next(c for c in sheet.root if isinstance(c, list) and c[0] == 'paper')[1:]]
    w, h = (float(p[1]), float(p[2])) if p[0] == 'User' else PAPER[p[0]]
    return (h, w) if 'portrait' in p else (w, h)


def off_board(sym):
    o = next((c for c in sym['node'] if isinstance(c, list) and c[0] == 'on_board'), None)
    return o is not None and str(o[1]) == 'no'


def root_sheets(root):
    """(slug, file) for each sheet on the root schematic, in sheet-name order ("3 VCA")."""
    t = open(root).read()
    out = []
    for blk in re.findall(r'\n\t\(sheet\n.*?\n\t\)', t, re.S):
        name = re.search(r'"Sheetname" "([^"]+)"', blk).group(1)
        f = re.search(r'"Sheetfile" "([^"]+)"', blk).group(1)
        out.append((natkey(name), f[:-len('.kicad_sch')], f))
    return [(slug, f) for _, slug, f in sorted(out)]


def export_images(root, sheets, here):
    """Each sheet as kicad-cli draws it, page-sized, so its coordinates are sheet millimetres."""
    from export_kicad import KICAD_CLI
    if not KICAD_CLI:
        sys.exit('--images needs kicad-cli: install KiCad, or put kicad-cli on PATH')
    stem = os.path.basename(root)[:-len('.kicad_sch')]
    t = open(root).read()
    names = {re.search(r'"Sheetfile" "([^"]+)"', b).group(1)[:-len('.kicad_sch')]:
             re.search(r'"Sheetname" "([^"]+)"', b).group(1)
             for b in re.findall(r'\n\t\(sheet\n.*?\n\t\)', t, re.S)}
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([KICAD_CLI, 'sch', 'export', 'svg', '--no-background-color',
                            '--exclude-drawing-sheet', '-o', tmp, root], capture_output=True, text=True)
        if r.returncode:
            sys.exit('kicad-cli sch export svg failed:\n%s%s' % (r.stdout, r.stderr))
        for slug in sheets:
            shutil.copyfile(os.path.join(tmp, '%s-%s.svg' % (stem, names[slug])),
                            os.path.join(here, 'img', slug + '.svg'))
            print('%-10s img/%s.svg' % (slug, slug))


def joined(sheets):
    """The whole design's nets: each sheet's own nets, joined across sheets by name. The
    sheets connect only through global labels and power symbols, so a shared name is a
    shared net. Returns {net id: set of (ref, pin)} and {net id: set of names}."""
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    local = {}
    for slug, sh in sheets.items():
        for n, ps in sh.netlist().items():
            node = (slug, n)
            find(node)
            local[node] = ps
            if not n.startswith('Net-('):
                for nm in n.split('/'):
                    parent[find(node)] = find(('name', nm))
    pins, names = {}, {}
    for node, ps in local.items():
        r = find(node)
        pins.setdefault(r, set()).update(ps)
        names.setdefault(r, set())
        if not node[1].startswith('Net-('):
            names[r].update(node[1].split('/'))
    return pins, names


def design_names(design, pins, parts):
    """Names for the nets the sheets leave unnamed, from design.py where its net and the
    sheet's net have the same pins. Resistor ends and op amp halves may be drawn the other
    way round from design.py, so each part is flipped if that makes more nets agree."""
    want = {}
    for p in design.PARTS:
        if p[0].startswith('#'):
            continue
        ref = DESIGN_REFS.get(p[0], p[0])
        for pn, n in p[6].items():
            want[(ref, pn)] = n
    flips = {}

    def dn(rp):
        r, pn = rp
        return want.get((r, flips.get(r, {}).get(pn, pn)))

    def agree():
        return sum(len({dn(p) for p in ps} - {None}) == 1 for ps in pins.values())
    for ref, sym in sorted(parts.items()):
        f = ({'1': '2', '2': '1'} if sym in ('R', 'C') else
             OPAMP_HALVES if sym in ('NE5532', 'TL072') else None)
        if f is None:
            continue
        before = agree(); flips[ref] = f
        if agree() <= before:
            del flips[ref]
    # parts in parallel (a feedback resistor and its capacitor) can only be turned round
    # together, so try those as one
    netof = {p: r for r, ps in pins.items() for p in ps}
    across = {}
    for ref, sym in parts.items():
        if sym in ('R', 'C') and (ref, '1') in netof and (ref, '2') in netof:
            across.setdefault(frozenset((netof[(ref, '1')], netof[(ref, '2')])), []).append(ref)
    for refs in across.values():
        if len(refs) > 1:
            before = agree()
            for ref in refs:
                if ref in flips: del flips[ref]
                else: flips[ref] = {'1': '2', '2': '1'}
            if agree() <= before:
                for ref in refs:
                    if ref in flips: del flips[ref]
                    else: flips[ref] = {'1': '2', '2': '1'}
    by_design = {}
    for rp in want:
        by_design.setdefault(want[rp], set()).add(rp)
    out = {}
    for r, ps in pins.items():
        ds = {dn(p) for p in ps} - {None}
        if len(ds) == 1:
            d = ds.pop()
            mine = {p for p in ps if dn(p) == d}
            if len(mine) == len({p for p in by_design[d] if p[0] in parts}):
                out[r] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--module', default='compressor', help='module slug, see modules.py')
    ap.add_argument('--images', action='store_true', help='also export the sheet SVGs with kicad-cli')
    args = ap.parse_args()
    mod = BY_SLUG.get(args.module)
    if mod is None:
        sys.exit('unknown module %r - known: %s' % (args.module, ', '.join(BY_SLUG)))
    if not mod.repo:
        sys.exit('%s has no source repository yet: nothing to generate viewer data from'
                 % mod.slug)
    repo = os.path.abspath(os.path.join(ROOT, '..', mod.repo))
    if not os.path.isdir(repo):
        sys.exit('%s not found. Check out the module repository beside this one:\n  %s'
                 % (mod.repo, repo))
    here = os.path.join(ROOT, 'site', mod.slug)
    proj = os.path.join(repo, 'kicad')
    root = [f for f in os.listdir(proj) if f.endswith('.kicad_sch')
            and os.path.exists(os.path.join(proj, f[:-len('.kicad_sch')] + '.kicad_pro'))][0]
    sheets = {slug: Sheet(os.path.join(proj, f)) for slug, f in root_sheets(os.path.join(proj, root))}
    if args.images:
        export_images(os.path.join(proj, root), sheets, here)

    parts = {}
    for sh in sheets.values():
        for s in sh.symbols:
            if not sh.is_power(s):
                parts[s['ref']] = s['lib'].split(':')[-1]
    pins, names = joined(sheets)
    import importlib.util
    spec = importlib.util.spec_from_file_location('design', os.path.join(repo, 'tools', 'design.py'))
    design = importlib.util.module_from_spec(spec); spec.loader.exec_module(design)
    from_design = design_names(design, pins, parts)
    netname, members = {}, {}
    for r, ps in pins.items():
        if names[r]:
            n = '/'.join(sorted(names[r], key=natkey))
        elif r in from_design:
            n = from_design[r]
        else:
            ref, pn = min(ps, key=lambda p: (natkey(p[0]), natkey(p[1])))
            n = 'Net-(%s-Pad%s)' % (ref, pn)
        for p in ps:
            netname[p] = n
        members[n] = ps

    total = 0
    for slug, sh in sheets.items():
        w, h = paper(sh)
        comps = {}
        for s in sh.symbols:
            if sh.is_power(s):
                continue
            pts = [place(px, py, s['X'], s['Y'], s['rot'], s['mirror']) for _, _, px, py in sh.pins(s)]
            xs = [p[0] for p in pts] + [s['X']]; ys = [p[1] for p in pts] + [s['Y']]
            pad = 1.6
            b = [min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad]
            c = comps.get(s['ref'])
            if c:                               # multi-unit part: union the boxes
                o = c['box']
                x0, y0 = min(o[0], b[0]), min(o[1], b[1])
                x1, y1 = max(o[0] + o[2], b[0] + b[2]), max(o[1] + o[3], b[1] + b[3])
                c['box'] = [round(v, 2) for v in (x0, y0, x1 - x0, y1 - y0)]
            else:
                c = comps[s['ref']] = {'ref': s['ref'], 'value': s['value'],
                                       'fp': s['fp'].split(':')[-1],
                                       'kind': kind(s['ref'], s['lib'].split(':')[-1]),
                                       # the panel parts are drawn here but marked
                                       # "not on board": they are on the front board
                                       'note': ' '.join(x for x in (NOTES.get(s['ref'], ''),
                                                OFF_BOARD if off_board(s) else '') if x),
                                       'box': [round(v, 2) for v in b], 'pins': {}}
            # each sheet sees only the pins drawn on it: an NE5532 has unit A on one sheet,
            # unit B on another and its supply pins on a third
            for _, pn, _, _ in sh.pins(s):
                if (s['ref'], pn) in netname:
                    c['pins'][pn] = netname[(s['ref'], pn)]
        comps = [comps[r] for r in sorted(comps, key=natkey)]
        for c in comps:
            c['pins'] = {k: c['pins'][k] for k in sorted(c['pins'], key=natkey)}
        onsheet = {(c['ref'], pn) for c in comps for pn in c['pins']}
        used = sorted({n for c in comps for n in c['pins'].values()}, key=natkey)
        netlist = []
        for n in used:
            here_pins = sorted(([r, p] for r, p in members[n] if (r, p) in onsheet),
                               key=lambda q: (natkey(q[0]), natkey(q[1])))
            netlist.append({'name': n, 'cls': net_class(n), 'pins': here_pins,
                            'offsheet': len(members[n]) - len(here_pins)})
        data = {'sheet': slug, 'w': w, 'h': h,
                'components': comps, 'nets': netlist}
        out = os.path.join(here, 'data', slug + '.json')
        open(out, 'w').write(json.dumps(data, separators=(',', ':')))
        total += len(comps)
        print('%-10s %3d parts %3d nets %6.1f KB' % (slug, len(comps), len(netlist), os.path.getsize(out) / 1024))
    named = sum(1 for r in pins if not names[r] and r in from_design)
    print('total %d components, %d nets (%d unnamed on the sheets, named from design.py)'
          % (total, len(pins), named))


if __name__ == '__main__':
    main()

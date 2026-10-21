#!/usr/bin/env python3
"""The equaliser as built: its two boards split apart and stacked, in 3D.

  python3 build/eq_stack.py [--repos DIR]

Combined_EQ.kicad_pcb draws the 22.5 mm top board beside the main card's front edge, and the
two were ordered as one panel. On the built module the top board is cut off and stands over
the main card's front end on two 20 mm M3 standoffs, from its H1/H4 to the card's H2/H3. Both
boards keep their component side up, so the top board's frequency pots, soldered to its
underside, hang down between the boards and point out of the front alongside the main card's,
in two columns 7.5 mm apart in height, as in the photo of the built module.

Writes into site/equaliser/files/: stack-3d-{angle,front-angle,front}.png (KiCad renders) and
stack.glb (for the 3D viewer on the board page). Needs kicad-cli (KiCad 10) and the KiCad 3D
model library, like export_kicad.py, CadQuery for the standoffs, and Node for npx.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import export_kicad as ek

SPLIT = 58.15                # x where the top board's edge meets the main card's
SHIFT = 22.5                 # the top board's width: H1/H4 land on H2/H3
STANDOFF = 20.0
THICK = 1.6
HOLES = [(73.15, 60.0), (73.15, 155.0)]          # main card H2, H3 (pcb mm)
BODY_STEP = "COLOUR_RGB('',0.313304153717,0.484529207832,0.410020903123)"
BODY_MASK = "COLOUR_RGB('',0.075,0.2,0.12)"
UNDERSIDE = ('RV1', 'RV4', 'RV6', 'RV9')         # the top board's pots, fitted underneath


def xs(block):
    """The x coordinates that place a top-level board item, or None to drop it."""
    head = re.match(r'\((\w+)', block).group(1)
    if head == 'footprint':
        return [float(re.search(r'\n\t\t\(at ([-\d.]+) ', block).group(1))]
    if head in ('segment', 'arc', 'via'):
        return [float(v) for v in re.findall(r'\((?:start|end|at) ([-\d.]+) ', block)]
    if head == 'zone':
        return [float(v) for v in re.findall(r'\(xy ([-\d.]+) ', block)]
    if head.startswith('gr_'):
        return [float(v) for v in re.findall(r'\((?:start|end|center|mid|xy) ([-\d.]+) ', block)]
    if head == 'dimension':
        return None
    return []                                       # nets, setup and the like: both boards


def split(text):
    """(main, top): the board file cut in two at SPLIT."""
    spans = [sp for head in ('footprint', 'segment', 'arc', 'via', 'zone', 'gr_line', 'gr_arc',
                             'gr_rect', 'gr_circle', 'gr_poly', 'gr_text', 'dimension')
             for sp in ek._blocks(text, head)]
    spans.sort()
    main, top, last = [], [], 0
    for s, e in spans:
        b, x = text[s:e], xs(text[s:e])
        main.append(text[last:s]); top.append(text[last:s])
        last = e
        if x is None:
            continue
        if not x or min(x) >= SPLIT - 1e-6:
            main.append(b)
        if not x or max(x) <= SPLIT + 1e-6:
            top.append(b)
    main.append(text[last:]); top.append(text[last:])
    return ''.join(main), ''.join(top)


def underside(text):
    """Turn the named pots' models over onto the underside of the board. The pot turns about
    its shaft's own axis line, so its middle pin stays in the middle hole and the shaft still
    points out of the front edge."""
    out, last = [], 0
    for s, e in ek._blocks(text, 'footprint'):
        fp = text[s:e]
        if re.search(r'\(property "Reference" "(%s)"' % '|'.join(UNDERSIDE), fp):
            fp = re.sub(r'\(offset \(xyz 0 0 0\)\)', '(offset (xyz 0 -5 %g))' % -THICK, fp)
            fp = re.sub(r'\(rotate \(xyz 0 0 0\)\)', '(rotate (xyz 180 0 0))', fp)
        out += [text[last:s], fp]
        last = e
    out.append(text[last:])
    return ''.join(out)


def add_model_footprint(text, n, model, offset):
    """Add a footprint at the origin that carries one 3D model and nothing else."""
    fp = '''	(footprint "Site:Stack"
		(layer "F.Cu")
		(uuid "00000000-0000-0000-0000-0000000%05d")
		(at 0 0)
		(property "Reference" "%s" (at 0 0 0) (layer "F.Fab") (hide yes)
			(uuid "00000000-0000-0000-0001-0000000%05d")
			(effects (font (size 1 1) (thickness 0.15))))
		(property "Value" "Stack" (at 0 0 0) (layer "F.Fab") (hide yes)
			(uuid "00000000-0000-0000-0002-0000000%05d")
			(effects (font (size 1 1) (thickness 0.15))))
		(attr board_only exclude_from_pos_files exclude_from_bom)
		(model "%s"
			(offset (xyz %g %g %g))
			(scale (xyz 1 1 1))
			(rotate (xyz 0 0 0))
		)
	)
''' % ((n, 'STACK%d' % n, n, n, model) + offset)
    text = text.rstrip()
    return text[:-1] + fp + ')\n'


def standoffs(path):
    """The two 20 mm hex standoffs with their screws, as one STEP in the main card's frame."""
    import cadquery as cq
    a = cq.Assembly(name='standoffs')
    brass = cq.Color(0.70, 0.58, 0.30)
    steel = cq.Color(0.45, 0.46, 0.48)
    for i, (x, y) in enumerate(HOLES):
        s = (cq.Workplane('XY').polygon(6, 5.0 / 0.866).extrude(STANDOFF)
             .faces('>Z or <Z').chamfer(0.3).translate((x, -y, THICK)))
        a.add(s, name='standoff%d' % i, color=brass)
        for z0 in (THICK + STANDOFF + THICK, -2.0):          # pan heads, top and underside
            head = cq.Workplane('XY').circle(2.75).extrude(2.0).edges('>Z' if z0 > 0 else '<Z').fillet(0.8)
            a.add(head.translate((x, -y, z0)), name='screw%d_%g' % (i, z0), color=steel)
    a.save(path, exportType='STEP')


def cli(*args):
    r = subprocess.run([ek.KICAD_CLI] + list(args), capture_output=True, text=True)
    if r.returncode:
        sys.exit('kicad-cli %s failed:\n%s%s' % (' '.join(args[:3]), r.stdout, r.stderr))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repos', default=os.path.join(ROOT, '..'))
    a = ap.parse_args()
    if not ek.KICAD_CLI:
        sys.exit('kicad-cli not found')
    src = os.path.join(os.path.abspath(a.repos), 'Equaliser', 'Combined_EQ', 'Combined_EQ.kicad_pcb')
    out = os.path.join(ROOT, 'site', 'equaliser', 'files')
    swapped = ek.with_models(src, ek.PROJECTS['equaliser'][1]['models'])
    folder = os.path.dirname(src)
    main_pcb = os.path.join(folder, '.site-stack-main.kicad_pcb')
    top_pcb = os.path.join(folder, '.site-stack-top.kicad_pcb')
    with tempfile.TemporaryDirectory(dir=os.path.dirname(folder)) as tmp:
        try:
            main_text, top_text = split(open(swapped).read())
            open(top_pcb, 'w').write(underside(top_text))
            top_step = os.path.join(tmp, 'top.step')
            cli('pcb', 'export', 'step', '--force', '--user-origin', '0x0mm', '--include-silkscreen',
                '--include-pads', '-o', top_step, top_pcb)
            # KiCad gives an exported board a pale green body; match the main card's mask
            step = open(top_step).read().replace(BODY_STEP, BODY_MASK)
            open(top_step, 'w').write(step)
            stand = os.path.join(tmp, 'standoffs.step')
            standoffs(stand)
            main_text = add_model_footprint(main_text, 1, top_step, (SHIFT, 0, THICK + STANDOFF))
            main_text = add_model_footprint(main_text, 2, stand, (0, 0, 0))
            open(main_pcb, 'w').write(main_text)
            views = [('angle', ['--side', 'top', '--perspective', '--rotate', '-55,0,120', '--zoom', '0.8']),
                     ('front-angle', ['--side', 'top', '--perspective', '--rotate', '-60,0,135',
                                      '--zoom', '0.8']),
                     ('front', ['--side', 'left', '--zoom', '1.9'])]
            for view, args in views:
                cli('pcb', 'render', '--quality', 'high', '-w', '1600', '-h', '1000', *args,
                    '-o', os.path.join(out, 'stack-3d-%s.png' % view), main_pcb)
                print('  stack-3d-%s.png' % view)
            raw = os.path.join(tmp, 'stack.glb')
            cli('pcb', 'export', 'glb', '--force', '--include-silkscreen', '--include-pads',
                '-o', raw, main_pcb)
            # KiCad's GLB runs to 12 MB; meshopt compression (decoded by the viewer) takes it
            # under 2 MB without simplifying any part
            glb = os.path.join(out, 'stack.glb')
            subprocess.run(['npx', '--yes', '@gltf-transform/cli@4', 'optimize', raw, glb,
                            '--compress', 'meshopt', '--simplify', 'false',
                            '--texture-compress', 'false', '--palette', 'false'], check=True, capture_output=True)
            print('  stack.glb, %.1f MB' % (os.path.getsize(glb) / 1e6))
        finally:
            for p in (swapped, main_pcb, top_pcb):
                if p != src and os.path.exists(p):
                    os.remove(p)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Exports every module's KiCad schematics and boards into site/<slug>/files/.

  python3 build/export_kicad.py [--repos DIR] [--only SLUG]

Needs KiCad installed (kicad-cli) and the module repositories checked out under --repos,
which defaults to this repository's parent folder. Each repository is looked up by its GitHub
name (Compressor, Pre-Amp, Equaliser). Nothing else in the build needs KiCad: the exports and
the manifest.json describing them are committed, and content_files.py builds the "Design
files" page from the manifest alone. Re-run this whenever a module's KiCad project changes.

Per schematic: one PDF of every sheet, and one SVG per sheet.
Per board with footprints on it: 3D renders of the top, the bottom and an angled view, and
front and back layer plots (copper, silkscreen and outline) as SVG, plus every layer in one
multi-page PDF. A board with no footprints or no outline is listed but not exported.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SITE = os.path.join(ROOT, 'site')

KICAD_CLI = next((p for p in [shutil.which('kicad-cli'),
                              '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli']
                  if p and os.path.exists(p)), None)

# slug -> GitHub repository, then (name, path) for each schematic and board to export.
# `name` becomes the file stem on the site; paths are relative to the repository.
PROJECTS = {
    'compressor': ('Compressor', {
        'sch': [('compressor', 'kicad_withpcb/compressor_with_pcb/compressor_with_pcb.kicad_sch',
                 'Single-sheet schematic the main board is drawn from'),
                ('front-board', 'kicad_withpcb/compressor_front/compressor_front.kicad_sch',
                 'Front board schematic: the panel controls, meters and ribbon header'),
                ('compressor-sections', 'kicad/UTS Mini Mixing Desk - Compressor.kicad_sch',
                 'Hierarchical schematic, one sheet per section, that these pages document')],
        'pcb': [('main-board', 'kicad_withpcb/compressor_with_pcb/compressor_with_pcb.kicad_pcb',
                 'Main board: the card that plugs into the rack'),
                # 35 x 110 mm and drawn upright, so turn it on its side to fill a wide render
                ('front-board', 'kicad_withpcb/compressor_front/compressor_front.kicad_pcb',
                 'Front board: sits behind the faceplate, joined to the main board by a ribbon',
                 {'top': '0,0,90', 'bottom': '0,0,90', 'angle': '-40,0,120'})],
    }),
    'preamp': ('Pre-Amp', {
        'sch': [('preamp', 'Series-500.kicad_sch', 'The preamp schematic')],
        'pcb': [('preamp', 'Series-500.kicad_pcb', 'The preamp card')],
    }),
    'equaliser': ('Equaliser', {
        'sch': [('lbp', 'Low_Bandpass_Filter/LBP.kicad_sch', 'Low band-pass (parametric) section'),
                ('lpf', 'Low_Pass_Filter/LPF/LPF.kicad_sch', 'Low-pass filter section'),
                ('hbp', 'High_Bandpass_Filter/HBP/HBP.kicad_sch', 'High band-pass section')],
        'pcb': [('lbp', 'Low_Bandpass_Filter/LBP.kicad_pcb', 'Low band-pass board'),
                ('lpf', 'Low_Pass_Filter/LPF/LPF.kicad_pcb', 'Low-pass board'),
                ('hbp', 'High_Bandpass_Filter/HBP/HBP.kicad_pcb', 'High band-pass board')],
    }),
}

FRONT = 'F.Cu,F.SilkS,F.Mask,Edge.Cuts'
BACK = 'B.Cu,B.SilkS,B.Mask,Edge.Cuts'
ALL_LAYERS = 'F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,F.Fab,B.Fab,F.CrtYd,B.CrtYd,Edge.Cuts'
RENDERS = [('top', ['--side', 'top'], None),
           ('bottom', ['--side', 'bottom'], None),
           ('angle', ['--side', 'top', '--perspective'], '-40,0,30')]


def cli(*args):
    r = subprocess.run([KICAD_CLI] + list(args), capture_output=True, text=True)
    if r.returncode:
        sys.exit('kicad-cli %s failed:\n%s%s' % (' '.join(args[:3]), r.stdout, r.stderr))


def git(repo, *args):
    return subprocess.run(['git', '-C', repo] + list(args), capture_output=True,
                          text=True, check=True).stdout.strip()


def export_sch(src, name, out):
    files = []
    cli('sch', 'export', 'pdf', '-o', os.path.join(out, name + '.pdf'), src)
    files.append(name + '.pdf')
    with tempfile.TemporaryDirectory() as tmp:
        cli('sch', 'export', 'svg', '--no-background-color', '--exclude-drawing-sheet',
            '-o', tmp, src)
        stem = os.path.splitext(os.path.basename(src))[0]
        for p in sorted(glob.glob(os.path.join(tmp, '*.svg'))):
            # KiCad names sheets "<project>-<sheet>.svg"; the root sheet is just "<project>.svg"
            sheet = os.path.basename(p)[:-4]
            sheet = sheet[len(stem):].lstrip('-') if sheet.startswith(stem) else sheet
            dst = '%s%s.svg' % (name, '-' + re.sub(r'[^a-z0-9]+', '-', sheet.lower()).strip('-')
                                if sheet else '')
            shutil.copyfile(p, os.path.join(out, dst))
            files.append(dst)
    return files


def board_stats(src):
    text = open(src).read()
    n = lambda tag: len(re.findall(r'^\s*\(%s\b' % tag, text, re.M))
    return {'footprints': n('footprint'), 'segments': n('segment'), 'vias': n('via'),
            'zones': n('zone'), 'outline': text.count('(layer "Edge.Cuts")')}


def export_pcb(src, name, out, rotate=None):
    """`rotate` optionally maps a render view to its own --rotate, for boards drawn upright."""
    files = []
    for view, args, rot in RENDERS:
        rot = (rotate or {}).get(view, rot)
        dst = '%s-3d-%s.png' % (name, view)
        cli('pcb', 'render', '--quality', 'high', '-w', '1600', '-h', '1000', '--zoom', '1.15',
            *args, *(['--rotate', rot] if rot else []), '-o', os.path.join(out, dst), src)
        files.append(dst)
    for side, layers, extra in [('front', FRONT, []), ('back', BACK, ['--mirror'])]:
        dst = '%s-%s.svg' % (name, side)
        cli('pcb', 'export', 'svg', '--mode-single', '-l', layers, '--fit-page-to-board',
            '--exclude-drawing-sheet', *extra, '-o', os.path.join(out, dst), src)
        files.append(dst)
    dst = name + '-layers.pdf'
    cli('pcb', 'export', 'pdf', '--mode-multipage', '-l', ALL_LAYERS, '--cl', 'Edge.Cuts',
        '-o', os.path.join(out, dst), src)
    files.append(dst)
    return files


def export_module(slug, repos):
    repo_name, spec = PROJECTS[slug]
    repo = os.path.join(repos, repo_name)
    if not os.path.isdir(repo):
        sys.exit('%s: no checkout at %s' % (slug, repo))
    out = os.path.join(SITE, slug, 'files')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    manifest = {'repo': 'https://github.com/UTS-500-Series/' + repo_name,
                'commit': git(repo, 'rev-parse', '--short', 'HEAD'),
                'date': git(repo, 'log', '-1', '--format=%cs'),
                'kicad': subprocess.run([KICAD_CLI, 'version'], capture_output=True,
                                        text=True).stdout.strip(),
                'schematics': [], 'boards': []}
    for name, path, label in spec['sch']:
        src = os.path.join(repo, path)
        manifest['schematics'].append({'name': name, 'source': path, 'label': label,
                                       'files': export_sch(src, name, out)})
        print('    %-22s schematic' % name)
    for name, path, label, *rotate in spec['pcb']:
        src = os.path.join(repo, path)
        stats = board_stats(src)
        # Footprints with no outline have only been dropped in from the schematic, and
        # KiCad renders them against a default slab the size of the drawing sheet.
        laid_out = stats['footprints'] and stats['outline']
        files = export_pcb(src, name, out, *rotate) if laid_out else []
        manifest['boards'].append({'name': name, 'source': path, 'label': label,
                                   'stats': stats, 'files': files})
        print('    %-22s board, %s' % (name, 'exported' if files else 'not laid out, skipped'))
    json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w'), indent=1)
    print('  %-10s %s at %s -> site/%s/files/' % (slug, repo_name, manifest['commit'], slug))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repos', default=os.path.join(ROOT, '..'),
                    help='folder holding the module checkouts (default: this repo\'s parent)')
    ap.add_argument('--only', choices=sorted(PROJECTS))
    a = ap.parse_args()
    if not KICAD_CLI:
        sys.exit('kicad-cli not found: install KiCad, or put kicad-cli on PATH')
    for slug in [a.only] if a.only else PROJECTS:
        export_module(slug, os.path.abspath(a.repos))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Works out the equaliser's frequency response from its KiCad netlist, with no SPICE installed.

    python3 build/_eq_response.py [--repo ../Equaliser]

The equaliser's two parametric bands are drawn on Combined_EQ/Combined_EQ.kicad_sch with real
values. This reads that sheet's netlist with _kicad_sch.py, turns every resistor, capacitor and
potentiometer into an admittance, models each op amp as a gain of 10^6, and solves the circuit
at each frequency (modified nodal analysis, the method SPICE's AC analysis uses). It writes
site/equaliser/data/response.json, which is committed, so building the site never needs the
repository.

The same file carries the team's own LTspice result (Low_Bandpass_Filter/LT_SPICE/BandA.raw),
read straight from the binary .raw file, so the page can show the two agree.

Ideal op amps mean this is the response the resistors and capacitors set, not the OPA1644's:
fine inside the audio band, where the OPA1644's 11 MHz of gain-bandwidth is plenty. Pots are
linear, and split at their wiper into two resistors. Standard library only.
"""
import argparse, array, cmath, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from _kicad_sch import Sheet

SCH = 'Combined_EQ/Combined_EQ.kicad_sch'
RAW = 'Low_Bandpass_Filter/LT_SPICE/BandA.raw'
GND = 'B+/C+/F+/G+/GND'       # the labels B+, C+, F+, G+ sit on ground, so the net takes all names
IN = 'Net-(R29-Pad1)'         # the low-mid band's input: R29 and RV8 pin 1, not yet wired to J1
# OPA1644 units as (+, -, out). IC3 is the low-mid band, IC2 the high-mid.
OPAMPS = [('A+', 'A-', 'Ao'), (GND, 'B-', 'Bo'), (GND, 'C-', 'Co'), ('D+', 'D-', 'Do'),
          ('E+', 'E-', 'Eo'), (GND, 'F-', 'Fo'), (GND, 'G-', 'Go'), ('H+', 'H-', 'Ho')]
A0 = 1e6
FREQS = [round(10 * 10 ** (i / 100), 3) for i in range(401)]      # 10 Hz to 100 kHz


def value(s):
    s = s.replace('nF', 'n').replace('µ', 'u').strip()
    for c, mul in (('p', 1e-12), ('n', 1e-9), ('u', 1e-6), ('k', 1e3), ('K', 1e3), ('M', 1e6)):
        if c in s:
            a, b = s.split(c, 1)        # "2k2" is 2.2k, "12.7n" is 12.7n
            return (float(a) if '.' in a else float((a or '0') + '.' + (b or '0'))) * mul
    return float(s)


class Circuit:
    def __init__(self, path):
        sheet = Sheet(path)
        pin = {p: n for n, ps in sheet.netlist().items() for p in ps}
        self.elems = []                 # (kind, net a, net b, ohms or farads, pot key)
        seen = set()
        for s in sheet.symbols:
            if sheet.is_power(s) or (s['ref'], s['unit']) in seen:
                continue
            seen.add((s['ref'], s['unit']))
            ref, lib = s['ref'], s['lib']
            if lib == 'Device:R':
                self.elems.append(('R', pin[(ref, '1')], pin[(ref, '2')], value(s['value']), None))
            elif lib == 'Device:C':
                self.elems.append(('C', pin[(ref, '1')], pin[(ref, '2')], value(s['value']), None))
            elif 'Potentiometer' in lib:
                # a dual-gang part draws each gang as its own unit: pins 1-3, then 4-6
                a, w, b = ('4', '5', '6') if s['unit'] == 2 else ('1', '2', '3')
                R = value(s['value'])
                self.elems.append(('top', pin[(ref, a)], pin[(ref, w)], R, ref))
                self.elems.append(('bot', pin[(ref, w)], pin[(ref, b)], R, ref))
        nets = {n for e in self.elems for n in e[1:3]} | {o[2] for o in OPAMPS}
        self.nodes = sorted(nets - {GND})
        self.idx = {n: i for i, n in enumerate(self.nodes)}

    def solve(self, f, pots, inp, out):
        """V(out) / V(inp) at f. `pots` maps a pot's reference to its wiper position, 0 at
        pin 1 (or 4) and 1 at pin 3 (or 6); unlisted pots sit at the centre."""
        N = len(self.nodes); M = N + len(OPAMPS) + 1
        G = [[0j] * M for _ in range(M)]
        b = [0j] * M
        s = 2j * math.pi * f
        I = self.idx.get

        def stamp(n1, n2, y):
            i, j = I(n1), I(n2)
            if i is not None: G[i][i] += y
            if j is not None: G[j][j] += y
            if i is not None and j is not None:
                G[i][j] -= y; G[j][i] -= y
        for kind, n1, n2, v, ref in self.elems:
            if kind == 'R':
                stamp(n1, n2, 1 / v)
            elif kind == 'C':
                stamp(n1, n2, s * v)
            else:
                k = min(max(pots.get(ref, 0.5), 1e-4), 1 - 1e-4)
                stamp(n1, n2, 1 / (v * (k if kind == 'top' else 1 - k)))
        for r, (p, m, o) in enumerate(OPAMPS, N):
            G[I(o)][r] += 1                     # the op amp sources current into its output
            G[r][I(o)] += 1                     # Vout = A0 (V+ - V-)
            if I(p) is not None: G[r][I(p)] -= A0
            if I(m) is not None: G[r][I(m)] += A0
        r = M - 1                               # the 1 V source driving the input
        G[I(inp)][r] += 1; G[r][I(inp)] += 1; b[r] = 1
        return gauss(G, b)[I(out)]

    def curve(self, pots, out):
        return [[f, round(20 * math.log10(abs(self.solve(f, pots, IN, out))), 3)] for f in FREQS]


def gauss(A, b):
    n = len(b)
    A = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        for r in range(c + 1, n):
            if A[r][c]:
                k = A[r][c] / A[c][c]
                A[r] = [x - k * y for x, y in zip(A[r], A[c])]
    x = [0j] * n
    for r in range(n - 1, -1, -1):
        x[r] = (A[r][n] - sum(A[r][c] * x[c] for c in range(r + 1, n))) / A[r][r]
    return x


def ltspice(path, node='V(output)'):
    """One node's AC magnitude from an LTspice binary .raw file (UTF-16 header, then every
    variable as a complex double, point by point)."""
    data = open(path, 'rb').read()
    marker = 'Binary:\n'.encode('utf-16-le')
    head = data[:data.index(marker)].decode('utf-16-le')
    nvars = int(head.split('No. Variables:')[1].split()[0])
    npts = int(head.split('No. Points:')[1].split()[0])
    names = [l.split('\t')[2] for l in head.split('Variables:\n')[1].splitlines() if l.count('\t') >= 3]
    col = names.index(node)
    a = array.array('d')
    a.frombytes(data[data.index(marker) + len(marker):][:nvars * npts * 16])
    pts = []
    for k in range(npts):
        base = k * nvars * 2
        v = complex(a[base + 2 * col], a[base + 2 * col + 1])
        pts.append([round(a[base], 3), round(20 * math.log10(abs(v)), 3)])
    return head.split('Date:')[1].splitlines()[0].strip(), pts


def peak(curve):
    f, db = max(curve, key=lambda p: abs(p[1]))
    return f, db


def q(curve):
    """Centre over the width between the points at half the peak's dB."""
    f0, pk = peak(curve)
    inside = [f for f, db in curve if abs(db) >= abs(pk) / 2]
    return f0 / (max(inside) - min(inside))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=os.path.join(ROOT, '..', 'Equaliser'))
    a = ap.parse_args()
    c = Circuit(os.path.join(a.repo, SCH))
    flat = {'RV5': 0.5, 'RV8': 0.5}
    # Wiper at pin 1 is full boost on RV8/RV5, the top of the frequency range on RV9/RV6,
    # and the narrowest band on RV7/RV2.
    bands = {'low': {'out': 'Do', 'gain': 'RV8', 'freq': 'RV9', 'q': 'RV7'},
             'high': {'out': 'Ho', 'gain': 'RV5', 'freq': 'RV6', 'q': 'RV2'}}
    out = {'source': 'Equaliser repo, %s, computed by build/_eq_response.py' % SCH,
           'curves': [], 'ranges': {}}
    for name, b in bands.items():
        rng = {}
        for k in (0, 0.5, 1):
            cv = c.curve({**flat, b['gain']: 0, b['freq']: k}, b['out'])
            f0, pk = peak(cv)
            rng['f%g' % k] = round(f0)
            out['curves'].append({'band': name, 'freq': k, 'gain': 'boost', 'points': cv})
            cut = c.curve({**flat, b['gain']: 1, b['freq']: k}, b['out'])
            out['curves'].append({'band': name, 'freq': k, 'gain': 'cut', 'points': cut})
            rng['boost'], rng['cut'] = round(pk, 2), round(peak(cut)[1], 2)
        for k in (0, 0.5, 1):
            rng['q%g' % k] = round(q(c.curve({**flat, b['gain']: 0, b['q']: k}, b['out'])), 2)
        rng['flat'] = round(max(abs(db) for _, db in c.curve(flat, b['out'])), 3)
        out['ranges'][name] = rng
    # the LTspice file sets its pots as resistor pairs: frequency at the top end, Q at mid,
    # full boost - the same settings as the low band's f0 boost curve above
    date, pts = ltspice(os.path.join(a.repo, RAW))
    out['ltspice'] = {'source': '%s, LTspice AC run of %s' % (RAW, date), 'points': pts}
    dst = os.path.join(ROOT, 'site', 'equaliser', 'data', 'response.json')
    json.dump(out, open(dst, 'w'), separators=(',', ':'))
    for name, r in out['ranges'].items():
        print('%-5s %s' % (name, r))
    print('ltspice peak %.2f dB at %.0f Hz' % peak(pts)[::-1])


if __name__ == '__main__':
    main()

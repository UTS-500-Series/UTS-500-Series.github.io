#!/usr/bin/env python3
"""Works out the equaliser's frequency response from its KiCad netlist, with no SPICE installed.

    python3 build/_eq_response.py [--repo ../Equaliser]

The whole equaliser is drawn on Combined_EQ/Combined_EQ.kicad_sch with real values. This reads
that sheet's netlist with _kicad_sch.py, turns every resistor, capacitor and potentiometer into
an admittance, models each op amp as a gain of 10^6, and solves the circuit at each frequency
(modified nodal analysis, the method SPICE's AC analysis uses). It writes
site/equaliser/data/response.json, which is committed, so building the site never needs the
repository.

The solve runs from the INA137's output to the DRV134's input: everything between them is op
amps, resistors, capacitors and pots. The INA137 halves the level and the DRV134 doubles it, so
that span is also the module's response from J1's input to its output.

The same file carries the team's own LTspice result for the low-mid band
(Low_Bandpass_Filter/LT_SPICE/BandA.raw), read straight from the binary .raw file, so the page
can show the two agree.

Ideal op amps mean this is the response the resistors and capacitors set, not the OPA1644's:
fine inside the audio band, where the OPA1644's 11 MHz of gain-bandwidth is plenty. Pots are
linear, and split at their wiper into two resistors. Standard library only.
"""
import argparse, array, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from _kicad_sch import Sheet

SCH = 'Combined_EQ/Combined_EQ.kicad_sch'
RAW = 'Low_Bandpass_Filter/LT_SPICE/BandA.raw'
QUAD = {'A': ('3', '2', '1'), 'B': ('5', '6', '7'), 'C': ('10', '9', '8'), 'D': ('12', '13', '14')}
SINGLE = ('3', '2', '6')                # OPA1641: +, -, out
A0 = 1e6
FREQS = [round(10 * 10 ** (i / 100), 3) for i in range(401)]      # 10 Hz to 100 kHz

# The ten knobs. Positions run from 0 at a pot's pin 1 (or 4) to 1 at pin 3 (or 6); with the
# usual pin 3 = clockwise, 1 is fully clockwise.
SECTIONS = {
    'lowshelf':  {'name': 'Low shelf',  'freq': 'RV1', 'gain': 'RV3'},
    'lowmid':    {'name': 'Low-mid',    'freq': 'RV9', 'gain': 'RV8', 'q': 'RV7'},
    'highmid':   {'name': 'High-mid',   'freq': 'RV6', 'gain': 'RV5', 'q': 'RV2'},
    'highshelf': {'name': 'High shelf', 'freq': 'RV4', 'gain': 'RV10'},
}
FLAT = {s['gain']: 0.5 for s in SECTIONS.values()}


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
        nets = sheet.netlist()
        # the frequency pots sit on a board of their own, wired pin for pin from J2 to J3:
        # join each J2 pin's net to the matching J3 pin's net
        alias = {}
        for n, ps in nets.items():
            for r, p in ps:
                if r == 'J3':
                    other = [m for m, qs in nets.items() if ('J2', p) in qs]
                    if other and other[0] != n:
                        alias[n] = other[0]
        self.pin = pin = {p: alias.get(n, n) for n, ps in nets.items() for p in ps}
        count = {}
        for n in pin.values():
            count[n] = count.get(n, 0) + 1
        self.gnd = pin[('J1', '13')]
        self.elems = []                 # (kind, net a, net b, ohms or farads, pot key)
        self.opamps = []                # (+, -, out) for every OPA1644 unit
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
            elif 'OPA1644' in lib or 'OPA1641' in lib:
                for unit in (QUAD.values() if 'OPA1644' in lib else [SINGLE]):
                    nn = tuple(pin.get((ref, x)) for x in unit)
                    # skip a unit with nothing on its inputs (IC4A is left unused)
                    if None not in nn and count[nn[0]] > 1 and count[nn[1]] > 1:
                        self.opamps.append(nn)
        self.IN = pin[('U1', '3')]      # the INA137's output, into buffer U1
        self.OUT = pin[('IC6', '4')]    # the DRV134's input
        self.LOWMID = pin[('IC3', '14')]  # the low-mid band's own output
        self.HIGHMID = pin[('IC2', '8')]  # the high-mid band's own output
        nets = {n for e in self.elems for n in e[1:3]} | {o[2] for o in self.opamps} | {self.IN}
        self.nodes = sorted(nets - {self.gnd})
        self.idx = {n: i for i, n in enumerate(self.nodes)}

    def solve(self, f, pots, inp, out):
        """V(out) / V(inp) at f. `pots` maps a pot's reference to its wiper position, 0 at
        pin 1 (or 4) and 1 at pin 3 (or 6); unlisted pots sit at the centre."""
        N = len(self.nodes); M = N + len(self.opamps) + 1
        G = [[0j] * M for _ in range(M)]
        b = [0j] * M
        s = 2j * math.pi * f
        I = self.idx.get

        def stamp(n1, n2, y):
            i, j = I(n1), I(n2)
            if i == j: return
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
        for r, (p, m, o) in enumerate(self.opamps, N):
            G[I(o)][r] += 1                     # the op amp sources current into its output
            G[r][I(o)] += 1                     # Vout = A0 (V+ - V-)
            if I(p) is not None: G[r][I(p)] -= A0
            if I(m) is not None: G[r][I(m)] += A0
        r = M - 1                               # the 1 V source driving the input
        G[I(inp)][r] += 1; G[r][I(inp)] += 1; b[r] = 1
        return gauss(G, b)[I(out)]

    def curve(self, pots, out=None):
        return [[f, round(20 * math.log10(abs(self.solve(f, pots, self.IN, out or self.OUT))), 3)]
                for f in FREQS]


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
    return max(curve, key=lambda p: abs(p[1]))


def q(curve):
    """Centre over the width between the points at half the peak's dB."""
    f0, pk = peak(curve)
    inside = [f for f, db in curve if abs(db) >= abs(pk) / 2]
    return f0 / (max(inside) - min(inside))


def shelf(curve, low):
    """A shelf's depth at the edge of the audio band (20 Hz or 20 kHz) and its corner: the
    frequency, coming in from that edge, where it has fallen to half that depth in dB."""
    edge = 20 if low else 20000
    pts = [p for p in curve if (p[0] >= edge if low else p[0] <= edge)]
    pts = pts if low else pts[::-1]
    end = pts[0][1]
    corner = next(f for f, db in pts if abs(db) < abs(end) / 2)
    return round(end, 2), round(corner)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=os.path.join(ROOT, '..', 'Equaliser'))
    a = ap.parse_args()
    c = Circuit(os.path.join(a.repo, SCH))
    out = {'source': 'Equaliser repo, %s, computed by build/_eq_response.py' % SCH,
           'curves': [], 'ranges': {}}
    for key, sec in SECTIONS.items():
        # which end of the gain pot boosts, worked out rather than assumed
        lo = c.curve({**FLAT, sec['gain']: 0})
        boost_at = 0 if max(abs(d) for _, d in lo) == max(d for _, d in lo) else 1
        rng = {'boost_at': boost_at, 'freq_pot': sec['freq'], 'gain_pot': sec['gain']}
        for k in (0, 0.5, 1):
            for gain, g in (('boost', boost_at), ('cut', 1 - boost_at)):
                cv = c.curve({**FLAT, sec['gain']: g, sec['freq']: k})
                out['curves'].append({'section': key, 'freq': k, 'gain': gain, 'points': cv})
                if 'q' in sec:
                    # a band's own figures from its own output, clear of the shelves' ripple
                    f0, pk = peak(c.curve({**FLAT, sec['gain']: g, sec['freq']: k}, getattr(c, key.upper())))
                    if gain == 'boost':
                        rng['f%g' % k] = round(f0)
                    rng[gain] = round(pk, 2)
                else:
                    depth, corner = shelf(cv, key == 'lowshelf')
                    if gain == 'boost':
                        rng['f%g' % k] = corner
                    rng['%s%g' % (gain, k)] = depth
        if 'q' in sec:
            for k in (0, 0.5, 1):
                rng['q%g' % k] = round(q(c.curve({**FLAT, sec['gain']: boost_at, sec['q']: k},
                                                 getattr(c, key.upper()))), 2)
        out['ranges'][key] = rng
    flat = c.curve(FLAT)
    out['flat'] = round(max(abs(db) for f, db in flat if f <= 20000), 3)
    out['flatcurve'] = flat
    # every knob at full boost, frequencies centred: the most the module can add
    out['allboost'] = c.curve({sec['gain']: out['ranges'][k]['boost_at'] for k, sec in SECTIONS.items()})
    # the LTspice file sets its pots as resistor pairs: frequency at the top end, Q at mid,
    # full boost. Compare it with the low-mid band's own output at the same settings.
    lm = SECTIONS['lowmid']
    band = c.curve({**FLAT, lm['gain']: out['ranges']['lowmid']['boost_at'], lm['freq']: 0}, c.LOWMID)
    date, pts = ltspice(os.path.join(a.repo, RAW))
    out['ltspice'] = {'source': '%s, LTspice AC run of %s' % (RAW, date), 'points': pts,
                      'netlist': band}
    dst = os.path.join(ROOT, 'site', 'equaliser', 'data', 'response.json')
    json.dump(out, open(dst, 'w'), separators=(',', ':'))
    for name, r in out['ranges'].items():
        print('%-9s %s' % (name, r))
    print('flat to %.3f dB; all boost peaks %.2f dB at %.0f Hz' % (out['flat'], *peak(out['allboost'])[::-1]))
    print('low-mid band alone %.2f dB at %.0f Hz; ltspice %.2f dB at %.0f Hz'
          % (*peak(band)[::-1], *peak(pts)[::-1]))


if __name__ == '__main__':
    main()

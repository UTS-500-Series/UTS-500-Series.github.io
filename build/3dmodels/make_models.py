#!/usr/bin/env python3
"""3D models for the parts KiCad's library doesn't model, or that Alps only publish where the
cloud can't reach: the 9 mm pots, the Salecom mini toggles and Jaycar's 2 mm tower LEDs.

    pip install cadquery
    python3 make_models.py            # writes the .step files next to this script

Every model is drawn in its footprint's own 3D frame, so in KiCad each one goes on with
offset 0 0 0, scale 1 1 1, rotate 0 0 0. KiCad's 3D frame: origin at the footprint origin,
x to the right, y UP the footprint (so a pad at footprint (0, 2.5) is at model y = -2.5),
z up off the board, millimetres. Colours are carried in the STEP files.

  Alps_RK09K_Vertical_6mm_Knurled.step     compressor front board, footprint
      compressor_front:Potentiometer_Alps_RK09K_Single_Vertical. 9 mm pot, shaft up,
      no threaded bushing (as bought from Altronics), 6 mm knurled split shaft.
  Alps_RK097_Single_Horizontal.step         equaliser, Potentiometer_THT:Potentiometer_Alps_RK097_Single_Horizontal
  Alps_RK097_Dual_Horizontal.step           equaliser, Potentiometer_THT:Potentiometer_Alps_RK097_Dual_Horizontal
      9 mm right-angle pots (Bourns PTD901/PTD902 on the build): metal cover, M7 bushing
      with its nut, 6 mm knurled split shaft, pointing out over the card's front edge.
  SW_Toggle_Mini_SPDT_Salecom_S1315.step    compressor front board, same-named footprint
  SW_Toggle_Mini_DPDT_Salecom_S1350.step    compressor front board, same-named footprint
      Red body, steel frame, 1/4-40 threaded bushing with nut and washer, chrome bat lever.
      Same envelope as the repository's simple models (body 0-9.2 mm, frame to 10.4 mm,
      bushing to 19.3 mm).
  LED_Jaycar_2mm_Tower_{orange,green,red}.step   compressor front board, footprint
      LED_THT:LED_D2.0mm_W4.0mm_H2.8mm_FlatTop. 2.0 mm tower on a 3.25 x 2.5 mm base, as
      measured. Drawn standing on long leads where the faceplate holds it (base 11.0 mm
      off the board) so a render of the board shows the LEDs where they sit when built.
"""
import math, os
import cadquery as cq

OUT = os.path.dirname(os.path.abspath(__file__))

STEEL = cq.Color(0.46, 0.47, 0.49)    # KiCad's renderer lights metal brightly, so these run dark
CHROME = cq.Color(0.62, 0.63, 0.66)
ZINC = cq.Color(0.52, 0.52, 0.50)
DARK = cq.Color(0.12, 0.12, 0.13)
BROWN = cq.Color(0.28, 0.22, 0.18)
RED = cq.Color(0.62, 0.08, 0.07)
TIN = cq.Color(0.80, 0.80, 0.78)
LED = {'orange': cq.Color(1.0, 0.45, 0.05), 'green': cq.Color(0.15, 0.80, 0.20),
       'red': cq.Color(0.90, 0.05, 0.05)}


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_z(cx, cy, r, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center(cx, cy).circle(r).extrude(z1 - z0)


def knurled_shaft(length, knurl, r=3.0, teeth=18, depth=0.3, slot=1.0):
    """6 mm shaft along +z from 0 to `length`: plain, then `knurl` mm of serrations at the end,
    split by a slot across the top. A small chamfer on the tip."""
    plain = cq.Workplane('XY').circle(r - 0.05).extrude(length - knurl)
    pts = []
    for i in range(teeth * 2):
        a = math.pi * i / teeth
        rr = r if i % 2 == 0 else r - depth
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    k = cq.Workplane('XY').workplane(offset=length - knurl).polyline(pts).close().extrude(knurl)
    k = k.edges('>Z').chamfer(0.3)
    s = plain.union(k)
    s = s.cut(box(-r - 1, r + 1, -slot / 2, slot / 2, length - knurl + 1.5, length + 1))
    return s


def threaded(r, z0, z1, pitch=0.635, groove=0.25):
    """A bushing with a thread suggested by shallow rings."""
    b = cyl_z(0, 0, r, z0, z1)
    z = z0 + 0.6
    while z < z1 - 0.5:
        ring = cyl_z(0, 0, r + 1, z, z + pitch / 2).cut(cyl_z(0, 0, r - groove, z, z + pitch / 2))
        b = b.cut(ring)
        z += pitch
    return b.faces('>Z').chamfer(0.25)


def hex_nut(af, thick, hole, z0):
    n = cq.Workplane('XY').workplane(offset=z0).polygon(6, af / math.cos(math.pi / 6)).extrude(thick)
    n = n.edges('|Z').fillet(0.25).cut(cyl_z(0, 0, hole / 2, z0 - 1, z0 + thick + 1))
    return n.faces('>Z or <Z').chamfer(0.3)


def save(assy, name):
    path = os.path.join(OUT, name)
    assy.save(path, exportType='STEP')
    print('wrote', name)


# ---------------------------------------------------------------- Alps RK09K, vertical
def rk09k():
    a = cq.Assembly(name='RK09K')
    cx, cy = 7.5, -2.5                       # shaft centre (footprint 7.5, 2.5)
    base = box(1, 13, -7.4, 2.4, 0.6, 4.6).edges('|Z').fillet(0.4)
    a.add(base, name='housing', color=DARK)
    # pressed-steel cover, wrapped down both long sides to the two mounting tabs
    cover = box(1.1, 12.9, -7.5, 2.5, 4.6, 5.4).edges('|Z').fillet(0.5)
    cover = cover.union(box(5.5, 8.5, 2.2, 2.5, -2.6, 5.4)).union(box(5.5, 8.5, -7.5, -7.2, -2.6, 5.4))
    cover = cover.cut(box(6.2, 7.8, 2.0, 2.6, -2.7, -0.8)).cut(box(6.2, 7.8, -7.6, -7.0, -2.7, -0.8))
    a.add(cover, name='cover', color=STEEL)
    # bearing boss and the shaft (20 mm from the mounting surface), no threaded bushing
    a.add(cyl_z(cx, cy, 3.6, 5.4, 7.0).faces('>Z').chamfer(0.4), name='boss', color=DARK)
    a.add(knurled_shaft(19.0, 8.0).translate((cx, cy, 7.0)), name='shaft', color=ZINC)
    # three terminals out of the side at x = 0, bent down through the board
    for y in (0, -2.5, -5.0):
        t = box(-0.4, 1.2, y - 0.45, y + 0.45, 1.6, 2.0).union(box(-0.4, 0.0, y - 0.35, y + 0.35, -3.0, 2.0))
        a.add(t, name='pin%g' % y, color=TIN)
    return a


# ---------------------------------------------------------------- Alps RK097, horizontal
def rk097(dual):
    a = cq.Assembly(name='RK097')
    # a 9.5 mm square face standing 1 mm off the board, as on the built equaliser
    ax, z = -2.5, 5.75                       # shaft axis: y = -2.5, 5.75 mm above the board
    back = 4.55 if dual else 2.05
    y0, y1, z0, z1 = -7.25, 2.25, 1.0, 10.5
    # moulded housing, one section per gang, with the steel cover over the front gang(s)
    a.add(box(-5.0, back, y0, y1, z0, z1).edges('|X').fillet(0.6), name='housing', color=BROWN)
    cover = box(-5.4, back - 0.9, y0 - 0.15, y1 + 0.15, z0 + 0.6, z1 + 0.15).edges('|X').fillet(0.7)
    cover = cover.cut(box(-5.0, back - 0.8, y0 + 0.05, y1 - 0.05, z0 + 0.6, z1 - 0.05))
    cover = cover.union(box(-5.4, -5.0, y0 - 0.15, y1 + 0.15, z0, z1 + 0.15))      # front plate
    # the front plate's two fixing ears, top left and bottom right as seen from the front
    for yy, zz in ((y1 - 1.3, z1 - 1.3), (y0 + 1.3, z0 + 1.3)):
        ear = cq.Workplane('YZ').workplane(offset=-5.6).center(yy, zz).circle(0.9).extrude(0.2)
        ear = ear.cut(cq.Workplane('YZ').workplane(offset=-5.7).center(yy, zz).circle(0.45).extrude(0.4))
        cover = cover.union(ear)
    a.add(cover, name='cover', color=STEEL)
    if dual:
        a.add(box(-0.1, 0.1, y0 - 0.16, y1 + 0.16, z0 + 0.6, z1 + 0.16), name='seam', color=DARK)
    # feet that stand it on the board
    for y in (y0 + 0.3, y1 - 1.3):
        a.add(box(-4.8, -3.8, y, y + 1.0, 0.0, z0), name='foot%g' % y, color=BROWN)
    # M7 x 0.75 bushing (7 mm long) and its nut, then the shaft out to x = -25
    rot = lambda w: w.rotate((0, 0, 0), (0, 1, 0), -90).translate((-5.4, ax, z))
    a.add(rot(threaded(3.5, 0, 6.6, pitch=0.75)), name='bushing', color=CHROME)
    a.add(rot(hex_nut(9.0, 2.0, 7.0, 3.0)), name='nut', color=CHROME)
    a.add(rot(knurled_shaft(13.0, 7.0)).translate((-6.6, 0, 0)), name='shaft', color=ZINC)
    # terminals: three per gang, straight down
    for x in ([0.0, 2.5] if dual else [0.0]):
        for y in (0, -2.5, -5.0):
            a.add(box(x - 0.4, x + 0.4, y - 0.25, y + 0.25, -3.0, z0 + 0.2), name='pin%g_%g' % (x, y), color=TIN)
    return a


# ---------------------------------------------------------------- Salecom mini toggles
def toggle(w):
    """w = body width across x (6.9 SPDT, 11.4 DPDT)."""
    a = cq.Assembly(name='toggle')
    h = 12.7
    a.add(box(-w / 2, w / 2, -h / 2, h / 2, 0.0, 9.2).edges('|Z').fillet(0.4), name='body', color=RED)
    frame = box(-w / 2 - 0.1, w / 2 + 0.1, -h / 2 - 0.1, h / 2 + 0.1, 9.2, 10.4)
    # the frame's side straps, crimped over the body
    frame = frame.union(box(-w / 2 - 0.1, -w / 2, -2.0, 2.0, 4.0, 9.2)).union(box(w / 2, w / 2 + 0.1, -2.0, 2.0, 4.0, 9.2))
    a.add(frame, name='frame', color=STEEL)
    a.add(threaded(3.1, 10.4, 19.3), name='bushing', color=CHROME)
    a.add(cyl_z(0, 0, 4.4, 15.6, 16.2).cut(cyl_z(0, 0, 3.15, 15, 17)), name='washer', color=STEEL)
    a.add(hex_nut(8.0, 2.0, 6.3, 16.2), name='nut', color=CHROME)
    # bat lever: pivots inside the bushing, leaned 12 degrees towards -y (one throw position)
    lever = (cq.Workplane('XY').circle(1.45).workplane(offset=9.0).circle(1.25).loft()
             .union(cq.Workplane('XY').sphere(1.6).translate((0, 0, 9.2))))
    lever = lever.translate((0, 0, -1.5)).rotate((0, 0, 0), (1, 0, 0), 12).translate((0, 0, 19.3))
    a.add(lever, name='lever', color=CHROME)
    a.add(cyl_z(0, 0, 1.6, 18.6, 19.5), name='collar', color=CHROME)
    cols = [0.0] if w < 8 else [-2.415, 2.415]
    for x in cols:
        for y in (-4.7, 0.0, 4.7):
            pin = box(x - 0.4, x + 0.4, y - 0.5, y + 0.5, -2.4, 0.0).edges('<Z').chamfer(0.3)
            a.add(pin, name='pin%g_%g' % (x, y), color=TIN)
    return a


# ---------------------------------------------------------------- Jaycar 2 mm tower LED
def tower_led(colour):
    """Footprint LED_D2.0mm_W4.0mm_H2.8mm_FlatTop: pad 1 (K) at 0,0, pad 2 at 2.54,0."""
    a = cq.Assembly(name='LED')
    cx = 1.27
    zb = 11.0                                    # where the faceplate holds the base
    base = box(cx - 1.625, cx + 1.625, -1.25, 1.25, zb, zb + 1.5).edges('|Z').fillet(0.2)
    base = base.cut(box(cx - 1.7, cx - 1.45, -1.3, 1.3, zb - 0.1, zb + 1.6))   # cathode flat
    tower = cyl_z(cx, 0, 1.0, zb + 1.5, zb + 3.0).faces('>Z').fillet(0.2)
    col = LED[colour]
    a.add(base.union(tower), name='lens', color=cq.Color(col.toTuple()[0], col.toTuple()[1], col.toTuple()[2], 0.85))
    for x in (0.0, 2.54):
        a.add(box(x - 0.25, x + 0.25, -0.25, 0.25, -2.4, zb + 0.2), name='lead%g' % x, color=TIN)
    return a


if __name__ == '__main__':
    save(rk09k(), 'Alps_RK09K_Vertical_6mm_Knurled.step')
    save(rk097(False), 'Alps_RK097_Single_Horizontal.step')
    save(rk097(True), 'Alps_RK097_Dual_Horizontal.step')
    save(toggle(6.9), 'SW_Toggle_Mini_SPDT_Salecom_S1315.step')
    save(toggle(11.4), 'SW_Toggle_Mini_DPDT_Salecom_S1350.step')
    for c in LED:
        save(tower_led(c), 'LED_Jaycar_2mm_Tower_%s.step' % c)

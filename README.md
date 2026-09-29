# UTS Mini Mixing Desk — documentation

The documentation site for the desk's 500-series modules. One section per module, published
to GitHub Pages.

Live site: **https://uts-500-series.github.io/**

This repository is the organisation site: GitHub Pages requires that repo to be named
`<org>.github.io` exactly, which is why this one is not called `docs`. It publishes at the
domain root rather than under a subpath. Every link in `site/` is relative, so the pages
also render correctly if this is ever demoted to an ordinary project site.

## What is real and what is not

| Module | Status | Source |
|---|---|---|
| Compressor | **Designed** — schematic complete, verified, not built | [`../compressor`](../compressor) |
| Preamp | **Published design** — ESP Project 66, with Project 96 phantom power | [ESP P66](https://sound-au.com/project66.htm), [P96](https://sound-au.com/project96.htm) |
| Equaliser | **In progress** — sections drawn, one band simulated, no values on the schematics | [`UTS-500-Series/Equaliser`](https://github.com/UTS-500-Series/Equaliser) |

Only the compressor has a design. Its pages are generated from `design.py` in the compressor
repository, which the KiCad schematic is verified against pin by pin, so its figures come
from the design rather than from memory.

The equaliser section is written from its own repository and says plainly which numbers are real: the only measured-looking figures come from one committed LTspice run, and its schematic images (`site/equaliser/img/`) are KiCad exports cropped to their content by hand. Regenerate and re-crop them when the sheets change.

The preamp section explains **ESP Project 66** by Rod Elliott, with phantom power from Project 96, and credits it throughout. It is written from ESP's articles, not from the KiCad redraw in `../preamp`. Measured figures are ESP's; the ±16 V operating points and the input impedance with phantom fitted are our own calculations and are labelled so. ESP's schematic is linked, not copied onto the site.

## Layout

```
build/     the generator (Python 3, standard library only)
site/      the generated site — this is what gets published
```

```
build/
  build_site.py         driver: builds every module, then the home page
  shell.py              shared page shell, nav, and the fig/pic/table helpers
  modules.py            the module registry — add a module here first
  content_compressor.py the compressor's pages
  content_preamp.py     ┐ built from scaffold.py, which deliberately emits
  content_equaliser.py  ┘ no values for hardware that does not exist
  content_mechanical.py the mechanical design guide (Fusion 360, faceplates, drawings)
  content_layout.py     the PCB layout guide (KiCad, setup to Gerbers)
  content_faceplate.py  the faceplate fit guide (panel, front board, bracket, rack)
  scaffold.py           the not-yet-designed-module template
  _data.py              viewer data, generated from a module's KiCad project
```

`site/` holds one folder per module plus a shared `style.css`, `viewer.js` and
`vendor/cytoscape.min.js`. The generated `data/` and `img/` files are committed, so the site
builds and publishes with no module repositories checked out.

`site/brand/` holds the logo and favicons. They are copied from the
[Logos](https://github.com/UTS-500-Series/Logos) repository, which has the source files and
every other size; edit them there and copy them across.

## Guides

Sections that cover every module rather than one live in `GUIDES` in `build/modules.py`.
They are built exactly like a module and listed under their own heading on the home page.
There are three:

- **Mechanical design** (`site/mechanical/`): taking each KiCad board into Fusion 360,
  designing a faceplate round it, and exporting dimensioned drawings.
- **PCB layout** (`site/layout/`): laying out a two-layer 500-series card in KiCad, from
  design rules and placement to grounds, routing and ordering.
- **Faceplate fit** (`site/faceplate/`): how the faceplate, controls, front board, main board
  and rack fit together, with hole sizes and a pre-order checklist.

## Building

```bash
python3 build/build_site.py
```

That rewrites every page in `site/`. It needs nothing installed and no network.

## Regenerating a module's interactive schematics

Only needed when a module's schematic changes. This step **does** need that module's
repository checked out beside this one:

```bash
python3 build/_data.py --module compressor
```

It reads the netlist and the `.kicad_sch` files from `../compressor`, and rewrites
`site/compressor/data/*.json`. The sheet images are separate — export them from KiCad and
copy them into `site/compressor/img/`:

```bash
kicad-cli sch export svg --no-background-color --exclude-drawing-sheet -o /tmp/svg \
  "../compressor/kicad/UTS Mini Mixing Desk - Compressor.kicad_sch"
```

`build_site.py` also copies the faceplate artwork out of `../compressor/panel/` when that
repository is present, so the front-panel page follows whatever layout and finish was last
generated.

## Adding a module

1. Add it to `MODULES` in `build/modules.py`.
2. Create `build/content_<slug>.py`. If the module is not designed yet, build it from
   `scaffold.py` the way the preamp does; if it is, follow `content_compressor.py`.
3. Run `python3 build/build_site.py`.

## Publishing

The published folder is `site/`, which is not one of the two roots GitHub's simple Pages UI
offers, so the included workflow is required:

1. **Settings → Pages → Build and deployment → Source: GitHub Actions**
2. Push to `main`. `.github/workflows/pages.yml` publishes `site/`.

`.nojekyll` is present so Pages serves the files as-is.

## The interactive schematics

Only the compressor has these &mdash; they are generated from a real KiCad project, and
the template modules have none.

Each section page carries a live viewer rather than a flat image:

- **Schematic** — the real KiCad drawing, exported from the project in the parent folder.
  Scroll to zoom, drag to pan. Every part has an invisible hotspot over it: click one and the
  panel shows its value, footprint, a short note on what it does, and every net it touches.
  Clicking a net highlights every other part on it.
- **Connections** — the same sheet drawn as a schematic-style graph with
  [cytoscape.js](https://js.cytoscape.org/): real part symbols, orthogonal wires and grid
  paper. Three things make it read like a drawing rather than a netlist dump:
  power and ground get **their own glyph on every pin**, exactly as a real schematic does,
  rather than one hub node with thirty wires fanning out; a **two-pin net is just a wire**
  between the parts, labelled with its name; and a net with **three or more pins gets a
  junction dot**. Drag parts about, click anything to trace it.
- **Tracing** — hover any wire or part and its whole net lights up while everything else
  fades back, with the net name shown in the strip below. Following one connection through a
  crossing is the thing a static picture cannot help with, so it does not cost a click.
  Clicking makes the same highlight stick and fills the detail panel.
- **Colour** — wires carry the same colour language as the rest of the site: amber for audio,
  teal for control, wine for supply rails, grey for ground. There is a legend under the graph.
- **Labels** — every part shows its designator and value, every wire its net name, and each
  wire end the pin number it lands on.
- **Nothing overlaps** — parts are placed on a layered grid rather than by a force
  simulation, so collisions are impossible by construction rather than by luck. Wires turn in
  the gutters between columns, which keeps every vertical run in empty space. The `Roomy` /
  `Compact` button changes the spacing; both are checked.

### How the no-overlap guarantee works

A force layout looks organic and overlaps constantly — nodes land on each other, labels
collide, wires run through parts. This lays out deterministically instead:

1. split the graph into connected pieces (a sheet is often several)
2. rank each piece by breadth-first distance from its best-connected node → column
3. order nodes within a column by the average row of their neighbours, a couple of barycentre
   sweeps, which pulls connected things level and cuts crossings
4. one node per cell, with cells sized from the widest label **as actually rendered** — the
   spacing grows and re-places until a measurement says nothing collides

Wires then turn in the gutter beside their source column, fanned a few pixels apart so two
wires never draw the same vertical line. Because gutters are empty by construction, wires
cannot cross parts.

Measured on every sheet, both spacings — node overlaps **0**, wires over parts **0**:

| Sheet | Nodes | Wires |
|---|---|---|
| Connector | 16 | 15 |
| Input | 26 | 27 |
| VCA | 56 | 60 |
| Output | 37 | 43 |
| Sidechain | 54 | 66 |
| Power | 128 | 88 |
| Meters | 95 | 97 |

The check is in the page, not just in this file: `document.querySelector('.iv')._ivDebug()`
returns the live counts from the browser console.

> Wires still **cross** each other — that is unavoidable in any graph that is not planar, and
> no amount of layout work removes it. What is guaranteed is that nothing is *hidden*: no part
> sits on another, no label is obscured, and no wire disappears behind a component. Hover any
> wire to trace it through a crossing.
- **Search** — type a designator (`R14`) or a net (`VBIAS`) to jump to it in either view.

## Wide layout

The sidebar carries a **Wide layout** toggle. Pages sit at a reading width by default; the
toggle widens them to **1240 px** so schematics, graphs and tables have room. It is a wider cap,
not an uncapped page — on a large monitor unbounded prose runs to unreadable line lengths.
Change `--wide-max` at the top of `style.css` to taste. The choice is
remembered in `localStorage` and applied in the page `<head>` before first paint, so it does
not flash narrow on load, and the schematic viewer re-fits itself when the column changes width
underneath it.

It only lifts the cap — it never changes padding. On a narrow window the cap was not binding
anyway, so adding padding there would make the toggle actively worse. The control hides itself
below 900 px for the same reason.

The plain SVG is still one click away under each viewer, for printing or for reading at full
size.

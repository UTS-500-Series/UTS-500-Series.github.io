# UTS Mini Mixing Desk — documentation

The documentation site for the desk's 500-series modules. One section per module, published
to GitHub Pages.

Live site: *(add the Pages URL once it is deployed)*

## What is real and what is not

| Module | Status | Source |
|---|---|---|
| Compressor | **Designed** — schematic complete, verified, not built | [`../compressor`](../compressor) |
| Preamp | Template — no circuit exists | — |
| Equaliser | Template — no circuit exists | — |

Only the compressor has a design. Its pages are generated from `design.py` in the compressor
repository, which the KiCad schematic is verified against pin by pin, so its figures come
from the design rather than from memory.

The preamp and equaliser sections are **templates**. They contain no circuit values, no part
numbers and no performance figures, because none exist. What they do contain is the shape of
the work — the sections a module needs, and the decisions that have to be made before any of
it can be drawn. Read them as checklists.

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
  scaffold.py           the not-yet-designed-module template
  _data.py              viewer data, generated from a module's KiCad project
```

`site/` holds one folder per module plus a shared `style.css`, `viewer.js` and
`vendor/cytoscape.min.js`. The generated `data/` and `img/` files are committed, so the site
builds and publishes with no module repositories checked out.

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

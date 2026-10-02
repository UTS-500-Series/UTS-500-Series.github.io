#!/usr/bin/env python3
"""Which modules the site covers, and where each one's source repository sits.

`repo` is a path relative to this repository's parent, used only when regenerating viewer
data with _data.py. The site itself is self-contained: the generated data/ and img/ files
are committed here, so building the pages never needs the module repositories present.
"""


class Module:
    def __init__(self, slug, name, tagline, status, description, footer,
                 content, repo=None, brand=None):
        self.slug, self.name, self.tagline = slug, name, tagline
        self.brand = brand or '%s module' % name   # subtitle under the suite name in the sidebar
        self.status = status                  # 'built' | 'designed' | 'progress' | 'planned' | 'guide'
        self.description = description
        self.footer = footer
        self.content = content                # python module holding NAV and PAGES
        self.repo = repo                      # sibling checkout, or None if none exists
        self.nav = self.pages = None

    def bind(self, nav, pages):
        self.nav, self.pages = nav, pages
        self.order = [p for _, g in nav for p, _, _ in g]
        self.titles = {p: t for _, g in nav for p, _, t in g}
        missing = [p for p in self.order if p not in pages]
        assert not missing, '%s: nav lists pages with no content: %s' % (self.slug, missing)
        return self

    @property
    def designed(self):
        return self.status != 'planned'


MODULES = [
    Module('compressor', 'Compressor',
           'Feedback compressor built round a discrete current-steering gain cell. '
           'Both boards laid out and routed, simulated, and a parts list from Altronics.',
           'designed',
           'How the UTS Mini Mixing Desk compressor module works, section by section.',
           'documentation generated from the KiCad project',
           content='content_compressor', repo='Compressor'),

    Module('preamp', 'Preamp',
           'Discrete low-noise balanced mic preamp with switchable phantom power. '
           'Drawn and laid out; no values yet.',
           'progress',
           'How the UTS Mini Mixing Desk microphone preamp works, from its KiCad schematic.',
           'written from the Pre-Amp repository at 5e6a308',
           content='content_preamp', repo='Pre-Amp'),

    Module('equaliser', 'Equaliser',
           'Two state-variable parametric bands on OPA1644s, plus high-pass, low-pass and gain '
           'stages. Bands drawn with values; card not wired yet.',
           'progress',
           'How the UTS Mini Mixing Desk equaliser module works, and how far along it is.',
           'written from the Equaliser repository at e2f6864',
           content='content_equaliser', repo='Equaliser'),
]

# Sections that cover all three modules rather than one. Built exactly like a module and
# listed separately on the home page.
GUIDES = [
    Module('mechanical', 'Mechanical design',
           'Bringing each KiCad board into Fusion 360, designing a faceplate round it, and '
           'exporting dimensioned drawings.',
           'guide',
           'How to model the UTS Mini Mixing Desk modules and faceplates in Fusion 360 and '
           'export dimensioned drawings.',
           'a guide shared by all three modules',
           content='content_mechanical', brand='Mechanical design guide'),

    Module('layout', 'PCB layout',
           'Laying out a two-layer 500-series card in KiCad, from board setup to ordering.',
           'guide',
           'How to lay out a UTS Mini Mixing Desk module board in KiCad, from design rules '
           'to Gerbers.',
           'a guide shared by all three modules',
           content='content_layout', brand='PCB layout guide'),

    Module('faceplate', 'Faceplate fit',
           'How the faceplate, controls, boards and rack fit together, with hole sizes and '
           'a checklist.',
           'guide',
           'How to design a 500-series faceplate that fits the module boards and the rack.',
           'a guide shared by all three modules',
           content='content_faceplate', brand='Faceplate fit guide'),
]

BY_SLUG = {m.slug: m for m in MODULES + GUIDES}

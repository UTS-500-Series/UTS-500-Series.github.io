#!/usr/bin/env python3
"""Which modules the site covers, and where each one's source repository sits.

`repo` is a path relative to this repository's parent, used only when regenerating viewer
data with _data.py. The site itself is self-contained: the generated data/ and img/ files
are committed here, so building the pages never needs the module repositories present.
"""


class Module:
    def __init__(self, slug, name, tagline, status, description, footer,
                 content, repo=None):
        self.slug, self.name, self.tagline = slug, name, tagline
        self.status = status                  # 'built' | 'designed' | 'planned'
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
           'Feedback compressor built round a discrete current-steering gain cell.',
           'designed',
           'How the UTS Mini Mixing Desk compressor module works, section by section.',
           'documentation generated from the KiCad project',
           content='content_compressor', repo='compressor'),

    Module('preamp', 'Preamp',
           'Microphone preamplifier with phantom power. Not yet designed.',
           'planned',
           'Planned documentation for the UTS Mini Mixing Desk preamp module.',
           'template &mdash; no circuit exists yet',
           content='content_preamp'),

    Module('equaliser', 'Equaliser',
           'Multi-band equaliser. Not yet designed.',
           'planned',
           'Planned documentation for the UTS Mini Mixing Desk equaliser module.',
           'template &mdash; no circuit exists yet',
           content='content_equaliser'),
]

BY_SLUG = {m.slug: m for m in MODULES}

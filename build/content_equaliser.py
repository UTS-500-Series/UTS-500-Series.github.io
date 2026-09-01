"""Equaliser module - page content.

A template, not documentation: see scaffold.py. Nothing in this file states a circuit value,
because no circuit exists.
"""
import scaffold

NAV, PAGES = scaffold.build(
    name='equaliser', slug='equaliser',
    tagline='A multi-band equaliser for the desk: a small number of bands, each able to lift '
            'or cut, on the same 1.5 inch panel as everything else.',
    blurb='The equaliser is the module most constrained by its front panel. Every band needs '
          'at least a frequency and a gain control, and a 38 mm wide faceplate runs out of '
          'room long before the circuit does &mdash; so the panel layout has to be settled '
          'before the circuit is worth drawing.',
    sections=[
        ('input.html', 'Input buffer', 'The input buffer',
         'Receiving the balanced input and presenting the filter sections with a source '
         'impedance they can work against.',
         ['The filters load the source; how much buffering they need depends on the topology '
          'chosen below.']),

        ('bands.html', 'The filter bands', 'The filter bands',
         'The equaliser proper: how many bands, what each one can do, and the topology '
         'behind them.',
         ['How many bands, and which are fixed-frequency versus sweepable?',
          'Baxandall shelving, or a state-variable / gyrator bandpass for the mids? The '
          'first is cheap and gentle; the second gives real control at the cost of parts '
          'and panel space.',
          'Constant-Q or proportional-Q? They sound different and cost differently.',
          'Whether any band needs a bypass so the module can be compared against itself.']),

        ('output.html', 'Output stage', 'The output stage',
         'Recombining the bands and driving the balanced output.',
         ['Series filter chain or parallel summing? This follows directly from the band '
          'topology.',
          'Where unity gain sits with all controls centred.']),

        ('power.html', 'Power &amp; references', 'Power and references',
         'Rail entry, decoupling and grounding.',
         ['Op-amp count drives the current budget, and a multi-band equaliser uses a lot of '
          'them &mdash; the compressor already draws about 90 mA of the 130 mA allowed.']),
    ],
    decisions=[
        ('How many bands', 'Drives the op-amp count, the current budget and the panel layout '
         'all at once.'),
        ('Filter topology per band',
         'Shelving, gyrator and state-variable sections have different part counts, different '
         'tuning behaviour and different panel needs.'),
        ('Panel layout before circuit',
         'This is the one module where the faceplate is the binding constraint. Concentric '
         'controls buy space at the cost of feel; deciding late means redrawing the circuit.'),
        ('Whether the desk wants matched stereo pairs',
         'Matched EQ channels need tolerance parts in every frequency-determining position.'),
    ],
    specs=[('Number of bands', 'to be decided'), ('Frequency ranges', 'to be decided'),
           ('Boost / cut range', 'to be decided'), ('Filter Q', 'to be decided'),
           ('Panel width', '1.5 in / 38.1 mm, 500-series'),
           ('Supply', '&plusmn;16 V, 130 mA per rail, 500-series')])

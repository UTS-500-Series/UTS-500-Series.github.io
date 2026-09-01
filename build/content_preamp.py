"""Preamp module - page content.

A template, not documentation: see scaffold.py. Nothing in this file states a circuit value,
because no circuit exists.
"""
import scaffold

NAV, PAGES = scaffold.build(
    name='preamp', slug='preamp',
    tagline='A microphone preamplifier for the desk: balanced mic input, switchable phantom '
            'power, and enough clean gain to bring a dynamic microphone up to line level.',
    blurb='The preamp is the first module in the chain and sets the noise floor for '
          'everything after it. That makes its input stage the part that matters most: the '
          'compressor can be rebuilt without touching the desk\'s noise performance, but the '
          'preamp cannot.',
    sections=[
        ('input.html', 'Mic input &amp; phantom', 'The microphone input',
         'The balanced input, phantom power and how the two coexist without the 48 V '
         'reaching anything that objects to it.',
         ['Transformer or electronically balanced input? A transformer is quieter into low '
          'source impedances and gives galvanic isolation, but costs more than the rest of '
          'the module put together.',
          'Phantom power has to come from 48 V, and the 500-series connector carries it on '
          'pin 15 &mdash; which this desk\'s chassis wiring currently leaves unconnected.',
          'Input protection: phantom switching produces large transients into the first stage.']),

        ('gain.html', 'The gain stage', 'The gain stage',
         'Where the 60-odd dB of gain is made, and how it is kept quiet.',
         ['How much gain, and is it continuous or switched in steps?',
          'Single stage or split across two? A single stage is simpler; two lets the first '
          'stage stay at fixed low-noise gain.',
          'Whether the same NE5532 and BC549 palette as the compressor is adequate here, or '
          'whether the noise target needs a lower-noise input device.']),

        ('output.html', 'Output stage', 'The output stage',
         'Driving the balanced output back into the rack, and the metering tap.',
         ['Balanced output on the same topology as the compressor, or transformer?',
          'Where the level meter should sense from.']),

        ('power.html', 'Power &amp; references', 'Power and references',
         'Rail entry, decoupling and grounding &mdash; plus the 48 V supply, which the '
         'compressor does not need and which changes this sheet substantially.',
         ['Is 48 V generated on the module or supplied by the rack?',
          'Current budget: the rack allows 130 mA per rail, and phantom power is not free.']),
    ],
    decisions=[
        ('Transformer or electronic input',
         'Sets the cost, the size, the noise floor and the whole shape of the input sheet.'),
        ('Where 48 V comes from',
         'Generating it on-module means a converter and its noise; taking it from the rack '
         'means the chassis wiring has to carry it, which today it does not.'),
        ('Gain range and how it is set',
         'A switched attenuator and a continuous pot lead to completely different circuits.'),
        ('Whether the desk needs matched channels',
         'Stereo work needs channel-to-channel gain matching, which forces switched gain '
         'and tolerance parts.'),
    ],
    specs=[('Gain range', 'to be decided'), ('Equivalent input noise', 'to be measured'),
           ('Maximum input level', 'to be decided'), ('Input impedance', 'to be decided'),
           ('Phantom power', '48 V, 500-series standard'),
           ('Panel width', '1.5 in / 38.1 mm, 500-series'),
           ('Supply', '&plusmn;16 V, 130 mA per rail, 500-series')])

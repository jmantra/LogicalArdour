# roman.py

"""
This module is an integeral part of the program
MMA - Musical Midi Accompaniment.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

Bob van der Poel <bob@mellowood.ca>

Roman numeral chord to standard notations.
"""

from MMA.common import *
from MMA.keysig import keySig


# Table of scales ... a list of 7 notes for each possible Major/Minor scale

majTable = {'C': ('C', 'D', 'E', 'F', 'G', 'A', 'B'),
            'C#': ('C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'C'),
            'D': ('D', 'E', 'F#', 'G', 'A', 'B', 'C#'),
            'Db': ('Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb', 'C'),
            'D#': ('D#', 'F', 'G', 'G#', 'A#', 'C', 'D'),
            'Eb': ('Eb', 'F', 'G', 'Ab', 'Bb', 'C', 'D'),
            'E': ('E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'),
            'F': ('F', 'G', 'A', 'Bb', 'C', 'D', 'E'),
            'F#': ('F#', 'G#', 'A#', 'B', 'C#', 'D#', 'F'),
            'Gb': ('Gb', 'Ab', 'Bb', 'B', 'Db', 'Eb', 'F'),
            'G': ('G', 'A', 'B', 'C', 'D', 'E', 'F#'),
            'G#': ('G#', 'A#', 'C', 'C#', 'D#', 'F', 'G'),
            'Ab': ('Ab', 'Bb', 'C', 'Db', 'Eb', 'F', 'G'),
            'A': ('A', 'B', 'C#', 'D', 'E', 'F#', 'G#'),
            'A#': ('A#', 'C', 'D', 'D#', 'F', 'G', 'A'),
            'Bb': ('Bb', 'C', 'D', 'Eb', 'F', 'G', 'A'),
            'B': ('B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#')}

minTable = {'C': ('C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb'),
            'C#': ('C#', 'D#', 'E', 'F#', 'G#', 'A', 'B'),
            'Db': ('Db', 'Eb', 'E', 'Gb', 'Ab', 'A', 'B'),
            'D': ('D', 'E', 'F', 'G', 'A', 'Bb', 'C'),
            'D#': ('D#', 'F', 'F#', 'G#', 'A#', 'B', 'C#'),
            'Eb': ('Eb', 'F', 'Gb', 'Ab', 'Bb', 'B', 'Db'),
            'E': ('E', 'F#', 'G', 'A', 'B', 'C', 'D'),
            'F': ('F', 'G', 'Ab', 'Bb', 'C', 'Db', 'Eb'),
            'F#': ('F#', 'G#', 'A', 'B', 'C#', 'D', 'E'),
            'Gb': ('Gb', 'Ab', 'A', 'B', 'Db', 'D', 'E'),
            'G': ('G', 'A', 'A#', 'C', 'D', 'D#', 'F'),
            'G#': ('G#', 'A#', 'B', 'C#', 'D#', 'E', 'F#'),
            'Ab': ('Ab', 'Bb', 'B', 'Db', 'Eb', 'E', 'Gb'),
            'A': ('A', 'B', 'C', 'D', 'E', 'F', 'G'),
            'A#': ('A#', 'C', 'C#', 'D#', 'F', 'F#', 'G#'),
            'Bb': ('Bb', 'C', 'Db', 'Eb', 'F', 'Gb', 'Ab'),
            'B': ('B', 'C#', 'D', 'E', 'F#', 'G', 'A')}

uroman = {'I': 0, 'II': 1, 'III': 2, 'IV': 3, 'V': 4, 'VI': 5, 'VII': 6}
lroman = {'i': 0, 'ii': 1, 'iii': 2, 'iv': 3, 'v': 4, 'vi': 5, 'vii': 6}
arabic = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6}

doubleflat = {'Cbb': 'Bb', 'Dbb': 'C', 'Ebb': 'D', 'Fbb': 'Eb',
              'Gbb': 'F', 'Abb': 'G', 'Bbb': 'A'}

doublesharp = {'C##': 'D', 'D##': 'E', 'E##': 'F#', 'F##': 'G',
               '#': 'A', 'A##': 'B', 'B##': 'C#'}

convertable = {'m' + chr(176): 'dim3', 'm0': 'dim3', 'mo': 'dim3', 'mO': 'dim3',
               'm' + chr(176) + '7': 'dim7', 'm07': 'dim7', 'mo7': 'dim7', 'mO7': 'dim7',
               'm' + chr(248) + '7': 'm7b5', 'm-07': 'm7b5', 'm-o7': 'm7b5', 'm-O7': 'm7b5'}


def rvalue(s):
    """ Convert a roman or arabic numeral to value (-1). """

    if s in uroman:
        return uroman[s]
    elif s in lroman:
        return lroman[s]
    elif s in arabic:
        return arabic[s]
    else:
        if s[0].isdigit:
            error("Unknown Arabic value '%s'. Use 1 to 7." % s)
        else:
            error("Unknown Roman numeral '%s'. Use 'I' to 'VII' in all u/l case." % s)


def convert(sym):
    """ Convert a roman numeral to a standard chord name. """

    keysig, minor = keySig.kName

    # figure number of roman numerals leading symbol

    sym = list(sym)
    rm = ''
    while(sym) and sym[0] in ('I', 'V', 'i', 'v'):
        rm += sym.pop(0)
    sym = ''.join(sym)

    if rm[0].islower():
        isminor = True
    else:
        isminor = False
    offset = rvalue(rm)

    # convert the roman to a pitch ... just a table lookup

    if minor:
        pitch = minTable[keysig][offset]
    else:
        pitch = majTable[keysig][offset]

    """
        Adjust the pitch if the remainder starts with a #  or b. (Note, '&'
        was converted to 'b' early in the chord parser.

        This permits technically incorrect things like 'Ib' which end up (in C)
        as 'Cb'. Useful with dim chords. We also need to worry about doubles!
    """

    if sym.startswith('b') or sym.startswith('#'):
        pitch += sym[0]
        sym = sym[1:]

        if pitch.endswith('#b') or pitch.endswith('b#'):  # 'b#' cancel each other
            pitch = pitch[:-2]

        elif pitch.endswith('##'):
            pitch = doublesharp[pitch]

        elif pitch.endswith('bb'):
            pitch = doubleflat[pitch]

    """ Now translate the quality. This is whatever was left after
        stripping off the number and sharp/flat. Two uglies:
          - some names are different in RN and standard, ie 07 .. dim7
          - lowercase == minor, so we add in 'm' to start of the
            leftover quality, unless it's there already. "v07" becomes "Xdim7",
            and "Vm0" (wrong!) still works and becomes Xdim3"
          - special trap for double 'm's. Hide conversion of "vm7" which becomes
            "Xmm7" and then "Xm7".
    """

    if isminor and not sym.startswith('m'):
        sym = 'm' + sym

    if sym in convertable:
        sym = convertable[sym]

    return pitch + sym

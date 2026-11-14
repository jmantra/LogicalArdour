
# notelen.py

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


"""

from . import gbl
from MMA.common import *

noteLenTable = {
    '0': 1,                   # special 0==1 midi tick
    '1': gbl.BperQ * 4,       # whole note
    '2': gbl.BperQ * 2,       # 1/2
    '23': gbl.BperQ * 4 // 3,  # 1/2 triplet
    '4': gbl.BperQ,           # 1/4
    '43': gbl.BperQ * 2 // 3,  # 1/4 triplet
    '8': gbl.BperQ // 2,       # 1/8
    '81': None,               # short 1/8, set by swing skew
    '82': None,               # long 1/8, set by swing skew
    '16': gbl.BperQ // 4,      # 1/16
    '32': gbl.BperQ // 8,      # 1/32
    '64': gbl.BperQ // 16,     # 1/64
    '6': gbl.BperQ // 6,       # 1/16 note triplet
    '3': gbl.BperQ // 3,       # 1/8 note triplet
    '5': gbl.BperQ // 5}       # 1/8 note quintuplet


def getNoteLen(n):
    """ Convert a Note to a midi tick length.

    Notes are 1==Whole, 4==Quarter, etc.
    Notes can be dotted or double dotted.
    Notes can be combined: 1+4 == 5 beats, 4. or 4+8 == dotted 1/4
                           1-4 == 3 beats, 1-0 == 4 beats less a midi tick
    Tuples can be set using (count,base).
    """

    length = 0

    if n.endswith('T') or n.endswith('t'):
        n = n[:-1]
        if not n:
            error("Specifying a note length in MIDI Ticks requires a value")
        n = stoi(n)
        if n == 0:
            n = 1
        if n < 1:
            error("MIDI note length cannot be negative.")
        return n

    n = n.replace('-', '+-')    # change "2-4" to "2+-4" for easier parsing
    n = n.replace('++-', '+-')  # and in case we already used "+-", take out 2nd "+"

    for a in str(n).split('+'):
        if a.endswith('..'):
            dot = 2
            a = a[:-2]
        elif a.endswith('.'):
            dot = 1
            a = a[:-1]
        else:
            dot = 0

        try:
            if a.startswith('-'):
                mult = -1
                a=a[1:]
            else:
                mult = 1
            if ':' in a:
                i = getTupleValue(a)
            else:
                i = noteLenTable[a]
            i *= mult

        except:
            # This also catches things like "4..." 
            error("Unknown note duration %s" % n)

        if dot == 2:
            i += i / 2 + i / 4
        elif dot == 1:
            i += i / 2
        length += i

    return int(length)

def getTupleValue(a):
    """ Grab a tuplet value from note 'xx:yy' We've already verified that
        the string has a ':'
    """

    dd, nn = a.split(':')
    if nn not in ('1', '2', '4', '8', '16', '32', '64'):
        error("Illegal duration value for tuplet. Must be a note "
              "(1,2,4...), not %s." % nn)
    
    nn = noteLenTable[nn]

    # validate the divisor a bit
    dd = stoi(dd)
    if dd<1 or dd>128:
        error("The count value for the tuplet '%s' is out of range." % a)
    return  nn // dd

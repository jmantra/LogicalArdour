# midiM.py

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

This module contains the MIDI value & command (un)packing routines.

These are necessary to create the big-endian values MIDI expects.

"""

import sys
from struct import pack, unpack
from MMA.common import *
from . import gbl

PY3 = sys.version_info[0] == 3

# this is for the join() in packBtyes(). By predefining
# we only call the bytearry() function once. Yes, it is quicker.
BCAT = bytearray(b'')
ctr={"tuple":0, "str":0, "int":0, "bytes":0}

def packBytes(*args):
    """ Return a packed string of bytes as a single string.
        args - an arbitrary number of strings, ints, lists [int[,int]..]
               or tuples (int[,int]..) 
        return - a single string.

        Note: strings are just concatenated into the string, tuples & ints
              are packed into single value bytes. In the future there
               _may_ be a reason to use struct.pack on string data, but I
              don't see it at this time.

              When calling, make sure tuples/lists are all ints. Having
              a string in a tuple will crash the whole mess!
    """

    ret = []

    for a in args:
        ty = type(a)

        if ty == int:
            ret.append(pack('B', a))  # integers

        # In py2 bytes will also grab string since they are the same
        elif ty in (bytes, bytearray):
            ret.append(a)

        elif ty in (tuple, list):
            ctr["tuple"]+=1
            ret.append(pack('%sB' % len(a), *a))  # tuples/lists

        # In py3 this will handle str. The else will not be done
        # but we'll leave it just in case :)
        elif ty == str:
            if PY3:
                ret.append(pack('%ss' % len(a), a.encode(encoding=gbl.encoding)))
            else:
                ret.append(a)

        else:
            error("Call Bob: Unknown type '%s' for midi string encode." % ty)

    return BCAT.join(ret)



def intToWord(x):
    """ Convert INT to a 2 byte MSB LSB value. Used in MIDI headers. """

    return pack('>H', x)


def intTo3Byte(x):
    """ Convert INT to a 3 byte MSB...LSB value. """

    return pack('>L', int(x))[1:]


def byte3ToInt(x):

    x = pack('1B', 0) + x
    return unpack('>L', x)[0]


def intToLong(x):
    """ Convert INT to a 4 byte MSB...LSB value. """

    return pack('>L', x)


def intToVarNumber(x):
    """ Convert INT to a variable length MIDI value. """
    
    lst = [ x & 0x7f ]
    while 1:
        x = x >> 7
        if x:
            lst.insert(0, (x & 0x7f) | 0x80)
        else:
            return pack("%sB" % len(lst), *lst)


def intTo14(x):
    """ Convert INT to a 2 byte 14 bit number

        Value to be converted must be 0...16383. A
        ValueError is raised if out of range.
    """

    if x < 0 or x > 0x3fff:
        raise ValueError

    return pack("2B", 0x007f & x, x >> 7)

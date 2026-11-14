
# mdefine.py

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

This class is used to parse lines of MDEFINE and stores
the sequences for later recall.

"""

import MMA.midiC
import MMA.midiM

from . import gbl
from   MMA.common import *


def mdefine(ln):
    """ Set a midi seq pattern. """

    if not ln:
        error("MDefine needs arguments")

    name = ln[0]
    if name.startswith('_'):
        error("Names with a leading underscore are reserved")

    if name.upper() == 'Z':
        error("The name 'Z' is reserved")

    mdef.create(name, ' '.join(ln[1:]))


def trackMdefine(name, ln):
    """ Set a midi seq pattern. Ignore track name."""

    mdefine(ln)


class Mdefine:

    def __init__(self):
        self.defs = {}

    def get(self, name):
        """ Return a predefined MIDI pattern."""

        try:
            return self.defs[name]
        except:
            error("The MDEFINE pattern %s has not been defined" % name)

    def create(self, name, ln):
        """ Parse a MDEFINE line.

            The line must be in the form:

                NAME <beat> <ctrl> <dat> [; ...]

        """

        name = name.upper()

        ln = ln.rstrip('; ')     # dump trailing ';' and whitespace
        ln = ln.split(';')
        evs = []
        for l in ln:
            l = l.split()

            if len(l) == 1:
                evs.extend(self.get(l[0].upper()))
                continue

            if len(l) != 3:
                error("MDEFINE sequence must have 3 values: Beat, Ctrl, Datum")

            off = stof(l[0], "Value for offset must be integer/float")

            c = MMA.midiC.ctrlToValue(l[1])
            if c < 0:
                c = stoi(l[1])
                if c < 0 or c > 0x7f:
                    error("Controller values must be 0x00 to 0x7f")

            d = stoi(l[2])
            if d < 0 or d > 0x7f:
                error("MIDI Control Datum value must be 0x00 to 0x7f")

            evs.append([off, MMA.midiM.packBytes(c, d)])

        self.defs[name] = evs

mdef = Mdefine()

# patBass.py

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


import MMA.notelen
import MMA.harmony
import MMA.ornament

from . import gbl
from MMA.common import *
from MMA.pat import PC, Pgroup


class Bass(PC):
    """ Pattern class for a bass track. """

    vtype = 'BASS'

    def getPgroup(self, ev):
        """ Get group for bass pattern.

            Fields - start, length, note, volume

        """

        if len(ev) != 4:
            error("There must be n groups of 4 in a pattern definition, "
                  "not <%s>" % ' '.join(ev))

        a = Pgroup()

        a.offset = self.setBarOffset(ev[0])
        a.duration = MMA.notelen.getNoteLen(ev[1])
        a.addoctave = 0

        # parse the offset (field 3) ... n[n][#s&b+-]
        offset = ev[2]

        # move leading +/- to end of string (leading +/- is an option)
        while offset[0:1] in ['-', '+']:
            offset = offset[1:] + offset[:1]

        # grab digit(s) for the offset into the scale (we use base 1)
        point = 0
        while(offset[point:point+1].isdigit()): 
            point += 1
        n = int(offset[0:point])   # from 0..point are all "valid" digits
        if n < 1:
            error("Note offset in Bass must be greater that 0, not '%s'." % n)
        while n > 7:
            n -= 7
            a.addoctave += 12
        a.noteoffset = n - 1
        
        # grab accidental (#,S,s or &,B,b) .. no double sharp/flat
        emsg = offset[point:]
        n = offset[point:point+1]
        if n == '#' or n == 'S': 
            a.accidental = 1
            point += 1
        elif n == 'B' or n == '&':
            a.accidental = -1
            point += 1
        else:
            a.accidental = 0

        # Trailing octave modifiers
        for n in offset[point:]:
            if n == '+':
                a.addoctave += 12
            elif n == '-':
                a.addoctave -= 12
            else:
                error("Only '- + # b &' are permitted after a noteoffset, not '%s'" % emsg)

        # and, finally, the volume
        a.vol = stoi(ev[3], "Note volume in Bass definition not int")

        return a

    def restart(self):
        self.ssvoice = -1

    def trackBar(self, pattern, ctable):
        """ Do the bass bar.

        Called from self.bar()

        """

        sc = self.seq

        for p in pattern:
            ct = self.getChordInPos(p.offset, ctable)
            
            if ct.bassZ:
                continue

            note = ct.chord.scaleList[p.noteoffset] + p.addoctave + p.accidental

            if not self.harmonyOnly[sc]:
                notelist = [(note, p.vol)]
            else:
                notelist = []

            if self.harmony[sc]:
                h = MMA.harmony.harmonize(self.harmony[sc], note, ct.chord.noteList)
                harmlist = list(zip(h, [p.vol * self.harmonyVolume[sc]] * len(h)))
            else:
                harmlist = []

            offset = p.offset
            if self.ornaments['type']:
                offset = MMA.ornament.doOrnament(self, notelist,
                                        self.getChordInPos(offset, ctable).chord.scaleList, p)
                notelist = []

            self.sendChord(notelist + harmlist, p.duration, offset)

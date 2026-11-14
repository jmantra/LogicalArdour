# patDrum.py

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
import MMA.translate

from . import gbl
from MMA.common import *
from MMA.pat import PC, Pgroup


class Drum(PC):
    """ Pattern class for a drum track. """

    vtype = 'DRUM'

    def __init__(self, ln):
        """ init for drum track. """

        self.toneList = [38]

        PC.__init__(self, ln)   # This order is important!

        self.setChannel('10')
        if not gbl.mtrks[self.channel].trackname:
            gbl.mtrks[self.channel].addTrkName(0, 'Drum')

    def saveGroove(self, gname):
        """ Save special/local variables for groove. """

        PC.saveGroove(self, gname)  # do this 1st. Creates storage.
        self.grooves[gname]['TONES'] = self.toneList[:]

    def restoreGroove(self, gname):
        """ Restore special/local/variables for groove. """

        self.toneList = self.grooves[gname]['TONES']
        PC.restoreGroove(self, gname)

    def setSeqSize(self):
        """ Expand existing pattern list. """

        self.toneList = seqBump(self.toneList)
        PC.setSeqSize(self)

    def clearSequence(self):
        """ Set some initial values. Called from init and clear seq. """

        PC.clearSequence(self)
        self.toneList = seqBump([38])

    def setTone(self, ln):
        """ Set a tone list. Only valid for DRUMs.
        ln[] is not nesc. the right length.
        """

        ln = lnExpand(ln, '%s Tone' % self.name)
        if not len(ln):
            error("Expecting argument for %s TONE." % self.name)
        tmp = []

        for n in ln:
            tmp.append(MMA.translate.dtable.get(n))

        self.toneList = seqBump(tmp)

    def restart(self):
        self.ssvoice = -1

    def getPgroup(self, ev):
        """ Get group for a drum pattern.

            Fields - start, length, volume
        """

        if len(ev) != 3:
            error("There must be at exactly 3 items in each "
                  "group of a drum define, not <%s>" % ' '.join(ev))

        a = Pgroup()

        a.offset = self.setBarOffset(ev[0])
        a.duration = MMA.notelen.getNoteLen(ev[1])
        a.vol = stoi(ev[2], "Type error in Drum volume")

        return a

    def trackBar(self, pattern, ctable):
        """ Do a drum bar.

        Called from self.bar()

        """

        
        sc = self.seq

        for p in pattern:
            tb = self.getChordInPos(p.offset, ctable)
            if tb.drumZ:
                continue

            self.sendNote(
                p.offset,
                self.getDur(p.duration),
                self.toneList[sc],
                self.adjustVolume(p.vol, p.offset))

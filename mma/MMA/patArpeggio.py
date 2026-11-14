# patArpeggio.py

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

import random

import MMA.notelen
import MMA.harmony

from . import gbl
from MMA.common import *
from MMA.pat import PC, Pgroup


class Arpeggio(PC):
    """ Pattern class for an arpeggio track. """

    vtype = 'ARPEGGIO'
    arpOffset = -1
    arpDirection = 1
    lastRange = 999
    lastDirection = 999

    def getPgroup(self, ev):
        """ Get group for apreggio pattern.

            Fields - start, length, volume
        """

        a = Pgroup()
        if len(ev) != 3:
            error("There must be exactly 3 items in each group "
                  "for apreggio define, not '%s'" % ' '.join(ev))

        a.offset = self.setBarOffset(ev[0])
        a.duration = MMA.notelen.getNoteLen(ev[1])
        a.vol = stoi(ev[2], "Type error in Arpeggio definition")

        return a

    def restart(self):
        self.ssvoice = -1
        self.arpOffset = -1
        self.arpDirection = 1
        lastRange = 999
        lastDirection = 999

    def trackBar(self, pattern, ctable):
        """ Do a arpeggio bar.

        Called from self.bar()

        """

        sc = self.seq

        direct = self.direction[sc]
        if direct != self.lastDirection:
            self.arpOffset = -1
            self.arpDirection = 1
            self.lastDirection = direct

        crange = self.chordRange[sc]
        if crange != self.lastRange:
            self.arpOffset = -1
            self.arpDirection = 1
            self.lastRange = crange

        for p in pattern:
            tb = self.getChordInPos(p.offset, ctable)

            if tb.arpeggioZ:
                continue

            if direct == 'DOWN':
                self.arpDirection = -1

            if self.chordLimit[0]:
                tb.chord.limit(*self.chordLimit)

            if self.compress[sc]:
                tb.chord.compress()

            if self.invert[sc]:
                tb.chord.invert(random.randrange(self.invert[sc][0], self.invert[sc][1]+1))

            # This should be optimized, it recreates the chord for every pattern.
            # Problem is that one would need to check all the LIMIT, COMPRESS, etc
            # settings each for each bar as well, so it's probably just as easy to
            # leave it as is. Besides, this works.

            octave = 0  # octave adjuster
            ourChord = []
            
            # for the range, stack up chords
            for l in range(int(crange)):
                ourChord.extend([x+octave for x in tb.chord.noteList])
                octave += 12

            # fractional range, add partial chord
            fr = crange - int(crange)
            if fr:      # for fractional  lengths
                fr = int(tb.chord.noteListLen * fr)
                if fr < 2:   # important, min of 2 notes in arp.
                    fr = 2
                ourChord.extend([x+octave for x in tb.chord.noteList[:fr]])

            if direct == 'BOTH':
                if self.arpOffset < 0:
                    self.arpOffset = 1
                    self.arpDirection = 1
                elif self.arpOffset >= len(ourChord):
                    self.arpOffset = len(ourChord) - 2
                    self.arpDirection = -1

            elif direct == 'UP':
                if self.arpOffset >= len(ourChord) or self.arpOffset < 0:
                    self.arpOffset = 0
                    self.arpDirection = 1

            elif direct == 'DOWN':
                if self.arpOffset < 0 or self.arpOffset >= len(ourChord):
                    self.arpOffset = len(ourChord) - 1
                    self.arpDirection = -1

            if direct == 'RANDOM':
                note = random.choice(ourChord)
            else:
                note = ourChord[self.arpOffset]

            self.arpOffset += self.arpDirection

            if not self.harmonyOnly[sc]:
                notelist = [(note, p.vol)]
            else:
                notelist = []

            if self.harmony[sc]:
                h = MMA.harmony.harmonize(self.harmony[sc], note, ourChord)
                vol = p.vol * self.harmonyVolume[sc]
                harmlist = list(zip(h, [vol] * len(h)))
            else:
                harmlist = []

            offset = p.offset
            if self.ornaments['type']:
                offset = MMA.ornament.doOrnament(self, notelist,
                               self.getChordInPos(offset, ctable).chord.scaleList, p)
                notelist = []

            self.sendChord(notelist + harmlist, p.duration, offset)

            tb.chord.reset()    # important, other tracks chord object

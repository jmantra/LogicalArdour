# patScale.py

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

import MMA.harmony
import MMA.notelen
import MMA.ornament
from MMA.pat  import PC, Pgroup

from . import gbl
from MMA.common import *
import MMA.debug

import copy


class Scale(PC):
    """ Pattern class for a Scale track. """

    vtype = 'SCALE'

    lastNote = -1
    lastChord = None
    lastStype = None
    lastDirect = 1
    lastRange = 0
    sOffset = 0
    notes = None
    dirfact = 1

    def __init__(self, ln):
        
        PC.__init__(self, ln)
        
    def saveGroove(self, gname):
        """ Save special/local variables for groove. """

        PC.saveGroove(self, gname)  # create storage. Do this 1st.

    def restoreGroove(self, gname):
        """ Restore special/local/variables for groove. """

        PC.restoreGroove(self, gname)

    def getPgroup(self, ev):
        """ Get group for scale patterns.

            Fields - start, length, volume
        """

        if len(ev) != 3:
            error("There must be at exactly 3 items in each group "
                  "in a Scale definition, not <%s>." % ' '.join(ev))

        a = Pgroup()

        a.offset = self.setBarOffset(ev[0])
        a.duration = MMA.notelen.getNoteLen(ev[1])
        a.vol = stoi(ev[2], "Type error in Scale definition")

        return a

    def setScaletype(self, ln):
        """ Set scale type. """

        ln = lnExpand(ln, "%s ScaleType" % self.name)
        tmp = []

        for n in ln:
            n = n.upper()
            if not n in ( 'CHROMATIC', 'SCALE', 'AUTO', 'CHORD'):
                error("%s Scaletype: Only Chromatic, Scale, Auto and "
                      "Chord are valid, not '%s'" % (self.name, n))

            tmp.append(n)

        self.scaleType = seqBump(tmp)

        if MMA.debug.debug:
            dPrint("Set %s ScaleType to: %s" %
                  (self.name, ' '.join(self.scaleType)))
        
    def restart(self):
        self.ssvoice = -1
        self.lastNote = -1
        self.lastChord = None
        self.lastStype = None
        self.lastDirect = 1
        self.lastRange = 0
        self.sOffset = 0
        self.notes = None
        self.dirfact = 1

        
    def trackBar(self, pattern, ctable):
        """ Do a scale bar.

            Called from self.bar()
        """

        sc = self.seq
        direct = self.direction[sc]
        
        # If the range or direction has changed, we just start
        # with a new scale.

        t = self.chordRange[sc]
        if t != self.lastRange:
            self.lastRange = t
            self.lastChord = None

        if self.lastDirect != direct:
            self.lastDirect = direct
            self.lastChord = None

        for p in pattern:

            tb = self.getChordInPos(p.offset, ctable)

            if tb.scaleZ:
                continue

            thisChord = tb.chord.tonic + tb.chord.chordType
            stype = self.scaleType[sc]

            if thisChord != self.lastChord or stype != self.lastStype:
                self.lastChord = thisChord
                self.lastStype = stype

                if stype == 'CHROMATIC':
                    notelist = [ tb.chord.rootNote + x for x in range(0,12)]
                
                elif stype == 'CHORD':
                    notelist = tb.chord.noteList[:]

                else:
                    notelist = list(tb.chord.scaleList)
                
                """ Get the current scale and append enuf copies
                together for RANGE setting. If Range happens
                to be 0 or 1 we end up with a single copy.
                """

                ln=self.chordRange[sc]    # RANGE 1...x (def. == 1)

                o=0
                self.notes = []

                while ln >= 1:
                    for a in notelist:
                        self.notes.append(a+o)
                    o+=12
                    ln-=1

                if ln>0 and ln<1:  # for fractional scale lengths
                    ln = int(len(notelist) * ln)
                    if ln < 2:   # important, must be at least 2 notes in a scale
                        ln=2
                    for a in notelist[:ln]:
                        self.notes.append(a+o)

                if direct == 'DOWN':
                    self.dirfact = -1
                    if self.lastNote == -1:
                        self.sOffset = len(self.notes)-1
                else:
                    self.sOffset = 0
                    self.dirfact = 1

                if self.lastNote > -1:
                    if self.lastNote in self.notes:
                        self.sOffset = self.notes.index(self.lastNote)

                    else:
                        self.sOffset=len(self.notes)-1
                        for     i, a in enumerate(self.notes):
                            if a>self.lastNote:
                                self.sOffset = i
                                break


            # Keep offset into note list in range

            # only > end of list if BOTH or UP

            if self.sOffset >= len(self.notes):
                if direct == 'BOTH':
                    self.dirfact = -1
                    self.sOffset = len(self.notes)-2
                else:        ## UP
                    self.sOffset = 0

            # only < start of list if DOWN or BOTH

            elif self.sOffset < 0:
                if direct == 'BOTH':
                    self.dirfact = 1
                    self.sOffset = 1
                else:        ## DOWN
                    self.sOffset = len(self.notes)-1

            if direct == 'RANDOM':
                note = random.choice(self.notes)
            else:
                note = self.notes[self.sOffset]
                self.sOffset += self.dirfact

            self.lastNote = note

            duration = p.duration
            vol = p.vol
            offset = p.offset

            if not self.harmonyOnly[sc]:
                nlist = [(note, p.vol)]
            else:
                nlist = []

            if self.harmony[sc]:
                ch = self.getChordInPos(p.offset, ctable).chord.noteList
                h = MMA.harmony.harmonize(self.harmony[sc], note, ch)
                harmlist =  list(zip(h, [p.vol * self.harmonyVolume[sc]] * len(h)))
            else:
                harmlist = []

            offset = p.offset
            if self.ornaments['type']:
                offset = MMA.ornament.doOrnament(self, nlist,
                                        self.getChordInPos(offset, ctable).chord.scaleList, p)
                nlist = []

            self.sendChord(nlist+harmlist, p.duration, offset)


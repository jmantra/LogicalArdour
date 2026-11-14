# patAria.py

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
from MMA.keysig import keySig
import MMA.chords
import MMA.debug
from . import gbl
from MMA.common import *
from MMA.pat import PC, Pgroup


class Aria(PC):
    """ Pattern class for an aria (auto-melody) track. """

    vtype = 'ARIA'
    notes = []
    selectDir = [1]
    noteptr = 0
    dirptr = 0
    lastChord = None
    deplete = [0]

    def setSeqSize(self):
        """ Expand existing pattern list. """

        self.deplete = seqBump(self.deplete)
        PC.setSeqSize(self)

    def restoreGroove(self, gname):
        """ Grooves are not saved/restored for aria tracks. But, seqsize is honored! """
        self.setSeqSize()

    def saveGroove(self, gname):
        """ No save done for grooves. """
        pass

    def getPgroup(self, ev):
        """ Get group for aria pattern.

            Fields - start, length, velocity

        """

        if len(ev) != 3:
            error("%s: There must be n groups of 3 in a pattern definition, "
                  "not <%s>" % (self.name, ' '.join(ev)))

        a = Pgroup()

        a.offset = self.setBarOffset(ev[0])
        a.duration = MMA.notelen.getNoteLen(ev[1])
        a.vol = stoi(ev[2], "Note volume in Aria definition not int")

        return a

    def setScaletype(self, ln):
        """ Set scale type. """

        ln = lnExpand(ln, "%s ScaleType" % self.name)
        tmp = []
        dlpt = []

        for n in ln:
            n = n.upper()
            if n.endswith('-'):
                dlpt.append(1)
                n = n[:-1]
            else:
                dlpt.append(0)

            if not n in ('CHROMATIC', 'SCALE', 'AUTO', 'CHORD', 'KEY'):
                error("%s ScaleType: Only Chromatic, Scale (Auto) Chord "
                      "and Key are valid." % self.name)
            tmp.append(n)

        self.scaleType = seqBump(tmp)
        self.deplete = seqBump(dlpt)
        self.restart()

        if MMA.debug.debug:
            msg = ["Set %s ScaleType:" % self.name]
            for a in self.scaleType:
                msg.append(a)
            dPrint(' '.join(msg))

    def setDirection(self, ln):
        """ Set direction for melody creation.

            This function replaces the pattern function of the same name ...
            the command name is shared, the function is different. Note we
            need to use a different storage name as well since
            self.direction is managed in the PC class.
        """

        if not len(ln):
            error("%s Direction: There must be at least one value." % self.name)

        self.selectDir = []
        for a in ln:
            if set(a.upper()) == set('R'):    # is direction 'r', 'rr', 'rrr', etc.
                if len(a) > 4:
                    error("%s Direction: too much randomness"
                          "(Maximum of 4 r's, got %d)." % (self.name, len(a)))
                self.selectDir.append(a.upper())
            else:   # not random, has to be an integer -4 ... 4
                a = stoi(a, "Expecting integer value or 'r', 'rr', 'rrr' or 'rrrr'.")
                if a < -4 or a > 4:
                    error("%s Direction: args must be 'r' or -4 to 4, not '%s'" % (self.name, a))
                self.selectDir.append(a)

        self.restart()

        if MMA.debug.debug:
            msg = ["Set %s Direction:" % self.name]
            for a in self.selectDir:
                msg.append(str(a))
            dPrint(' '.join(msg))

    def restart(self):
        self.ssvoice = -1
        self.notes = []

    def trackBar(self, pattern, ctable):
        """ Do the aria bar.

        Called from self.bar()

        """

        sc = self.seq
        unify = self.unify[sc]

        for p in pattern:
            ct = self.getChordInPos(p.offset, ctable)

            if ct.ariaZ:
                continue

            thisChord = ct.chord.tonic + ct.chord.chordType
            stype = self.scaleType[sc]
            chrange = self.chordRange[sc]

            # Generate notelist if nesc. Note that in the keysig, scale and
            # range funcs restart() is called ... self.notes is reset.

            if stype == 'CHORD' and (not self.notes or self.lastChord != thisChord):
                notelist = ct.chord.noteList
                self.notes = []

            elif stype == 'CHROMATIC' and (not self.notes or self.lastChord != thisChord):
                notelist = [ct.chord.rootNote + x for x in range(0, 12)]
                self.notes = []

            elif stype == 'KEY' and not self.notes:
                k = keySig.getKeysig()
                ch, t = k.split()
                if t.lower() == 'minor':
                    ch += "m"
                notelist = list(MMA.chords.ChordNotes(ch).scaleList)

            elif (stype == 'SCALE' or stype == 'AUTO') and \
                    (not self.notes or self.lastChord != thisChord):
                notelist = list(ct.chord.scaleList)
                self.notes = []

            self.lastChord = thisChord

            # we have the base list of notes (scale, chord, etc) and
            # now we make it the right length & octave.
            if not self.notes:
                o = 0
                while chrange >= 1:
                    for a in notelist:
                        self.notes.append(a + o)
                    o += 12
                    chrange -= 1

                if chrange > 0 and chrange < 1:  # for fractional scale lengths
                    chrange = int(len(notelist) * chrange)
                    if chrange < 2:   # important, must be at least 2 notes in a scale
                        chrange = 2
                    for a in notelist[:chrange]:
                        self.notes.append(a + o)

            # grab a note from the list

            if self.dirptr >= len(self.selectDir):
                self.dirptr = 0

            # the direction ptr is either an int(-4..4) or a string of 'r', 'rr, etc.

            a = self.selectDir[self.dirptr]

            if isinstance(a, int):
                self.noteptr += a
            else:
                a = random.choice(range(-len(a), len(a) + 1))
                self.noteptr += a

            if self.noteptr >= len(self.notes):

                if a > 0:
                    self.noteptr = 0
                else:
                    self.noteptr = len(self.notes) - 1
            elif self.noteptr < 0:
                if a < 0:
                    self.noteptr = len(self.notes) - 1
                else:
                    self.noteptr = 0

            note = self.notes[self.noteptr]

            # delete note just selected if that's the mode
            if self.deplete[sc]:
                self.notes.remove(note)
            self.dirptr += 1

            # output

            if not self.harmonyOnly[sc]:
                notelist = [(note, p.vol)]
            else:
                notelist = []

            if self.harmony[sc]:
                h = MMA.harmony.harmonize(self.harmony[sc], note, ct.chord.noteList)
                harmlist = list(zip(h, [p.vol * self.harmonyVolume[sc]] * len(h)))
            else:
                harmlist = []

            self.sendChord(notelist + harmlist, p.duration, p.offset)

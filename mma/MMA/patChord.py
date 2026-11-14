
# patChord.py

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
import MMA.ornament
from . import gbl
from MMA.common import *
from MMA.pat import PC, Pgroup
import MMA.debug

import copy


class Voicing:
    def __init__(self):
        self.mode = None
        self.range = 12
        self.center = 4
        self.random = 0
        self.percent = 0
        self.bcount = 0
        self.dir = 0


class Chord(PC):
    """ Pattern class for a chord track. """

    vtype = 'CHORD'
    sortDirection = 0   # used for tracking direction of strummed chords

    def __init__(self, ln):
        self.voicing = Voicing()
        PC.__init__(self, ln)

    def saveGroove(self, gname):
        """ Save special/local variables for groove. """

        PC.saveGroove(self, gname)  # create storage. Do this 1st.
        self.grooves[gname]['VMODE'] = copy.deepcopy(self.voicing)

    def restoreGroove(self, gname):
        """ Restore special/local/variables for groove. """

        self.voicing = self.grooves[gname]['VMODE']
        PC.restoreGroove(self, gname)

    def clearSequence(self):
        """ Set some initial values. Called from init and clear seq. """

        PC.clearSequence(self)
        self.voicing = Voicing()
        # .direction was set in PC.clear.. we're changing to our default
        self.direction = seqBump(['UP'])

    def setVoicing(self, ln):
        """ set the Voicing Mode options.  Only valid for CHORDS. """

        notopt, ln = opt2pair(ln, toupper=True)

        if notopt:
            error("Voicing: Each Voicing option must be a OPT=VALUE pair.")

        for mode, val in ln:
            if mode == 'MODE':
                valid = ("-", "OPTIMAL", "NONE", "ROOT", "COMPRESSED",
                         "INVERT", "KEY", "KEY2", "ROOTKEY", "DROP2",
                         "DROP2KEY", "DROP3", "DROP3KEY", "DROP23",
                         "DROP23KEY" )

                if not val in valid:
                    error("Valid Voicing Modes are: %s" % " ".join(valid))

                if val in ('-', 'NONE', 'ROOT'):
                    val = None

                # If we're setting a voicing mode check to see if we've
                # previously set invert or compress ... warning
                if val and (any(self.invert) or any(self.compress)):
                    warning("Setting both VoicingMode and "
                            "Invert/Compress is not a good idea")
                        
                # When we set voicing mode we always reset this. This forces
                # the voicingmode code to restart its rotations.

                self.lastChord = []

                self.voicing.mode = val

            elif mode == 'RANGE':
                val = stoi(val, "VOICING RANGE %s: Arg must be a value" % self.name)

                if val < 1 or val > 30:
                    error("Voicing Range: Arg out-of-range; must be 1 to 30, not '%s'." % val)

                self.voicing.range = val

            elif mode == 'CENTER':

                val = stoi(val, "Argument for %s VOICING CENTER must be a value."
                           % self.name)

                if val < 1 or val > 12:
                    error("VOICING CENTER: arg out-of-range; must be 1 to 12, not '%s'." % val)

                self.voicing.center = val

            elif mode == 'RMOVE':
                val = stoi(val, "Argument for %s VOICING RANDOM must be a value" % self.name)

                if val < 0 or val > 100:
                    error("VOICING RANDOM: arg must be 0 to 100, not %s" % val)

                self.voicing.random = val
                self.voicing.bcount = 0

            elif mode == 'MOVE':
                val = stoi(val, "Argument for %s VOICING MOVE  must be a value" % self.name)

                if val < 0:
                    error("VOICING MOVE: bar count must >= 0, not %s" % val)
                if val > 20:
                    warning("VOICING MOVE: bar count '%s' is quite large" % val)

                self.voicing.bcount = val
                self.voicing.random = 0

            elif mode == 'DIR':
                val = stoi(val, "Argument for %s VOICING DIR must be a value" % self.name)

                if not val in (1, 0, -1):
                    error("VOICING MOVE: Dir must be -1, 0 or 1, not '%s'." % val)

                self.voicing.dir = val

            else:
                error("Voicing does not have a '%s' option" % mode)
                
        if MMA.debug.debug:
            v = self.voicing
            dPrint("Set %s Voicing MODE=%s RANGE=%s CENTER=%s RMOVE=%s MOVE=%s DIR=%s " %
                  (self.name, v.mode, v.range, v.center, v.random, v.bcount, v.dir))

    def setDupRoot(self, ln):
        """ set/unset root duplication. Only for CHORDs """

        ln = lnExpand(ln, '%s DupRoot' % self.name)
        tmp = []

        for n in ln:
            ll = []
            for v in n.split(','):
                v = stoi(v, "%s DupRoot: Argument must be a value, not '%s'."
                            % (self.name, v))

                if v < -9 or v > 9:
                    error("%s DupRoot: '%s' out-of-range; must be -9 to 9." % (self.name, v))

                if v:
                    ll.append(v * 12)

            tmp.append(ll)

        self.dupRoot = seqBump(tmp)

        if MMA.debug.debug:
            dPrint("%s DupRoot set to: %s" % (self.name, self.getDupRootSetting()))

    def getDupRootSetting(self):
        """ Need to convert nested list ints to string. """

        ret = ""
        for l in self.dupRoot:
            if not l:
                l = [0]
            ret += ','.join([str(x // 12) for x in l]) + "  "
        return ret.strip()

    def getPgroup(self, ev):
        """ Get group for chord pattern.

        Tuples: [start, length, volume (,volume ...) ]
        """

        if len(ev) < 3:
            error("There must be at least 3 items in each group "
                  "of a chord pattern definition, not <%s>" % ' '.join(ev))

        a = Pgroup()

        a.offset = self.setBarOffset(ev[0])
        a.duration = MMA.notelen.getNoteLen(ev[1])

        vv = ev[2:]
        if len(vv) > 8:
            error("Only 8 volumes are permitted in Chord definition, not %s" % len(vv))

        a.vol = [0] * 8
        for i, v in enumerate(vv):
            v = stoi(v, "Expecting integer in volume list for Chord definition")
            a.vol[i] = v

        for i in range(i + 1, 8):  # force remaining volumes
            a.vol[i] = v

        return a

    def restart(self):
        self.ssvoice = -1
        self.lastChord = None

    def chordVoicing(self, chord, vMove):
        """ Mangle chord notes for voicing options. """

        sc = self.seq
        vmode = self.voicing.mode

        if vmode == "OPTIMAL":  # Optimal voicing algorithm by Alain Brenzikofer.

            # Initialize with a voicing around centerNote
            chord.center1(self.lastChord)

            # Adjust range and center
            if not (self.voicing.bcount or self.voicing.random):
                chord.center2(self.voicing.center, self.voicing.range // 2)

            # Move voicing
            elif self.lastChord:
                if (self.lastChord != chord.noteList) and vMove:
                    chord.center2(self.voicing.center, self.voicing.range // 2)
                    vMove = 0

                    # Update voicingCenter
                    sum = 0
                    for n in chord.noteList:
                        sum += n
                    c = sum // chord.noteListLen

                    # If using random voicing move it it's possible to
                    # get way off the selected octave. This check ensures
                    # that the centerpoint stays in a tight range.
                    # Note that if using voicingMove manually (not random)
                    # it is quite possible to move the chord centers to very
                    # low or high keyboard positions!

                    if self.voicing.random:
                        if c < -4:
                            c = 0
                        elif c > 4:
                            c = 4
                    self.voicing.center = c

        elif vmode == "KEY":
            chord.keycenter()

        elif vmode == "KEY2":
            chord.key2center()

        elif vmode == "ROOTKEY":
            chord.rootkey()

        elif vmode == "COMPRESSED":
            chord.compress()

        elif vmode == "INVERT":
            if chord.rootNote < -2:
                chord.invert(1)
            elif chord.rootNote > 2:
                chord.invert(-1)
            chord.compress()

        elif vmode == "DROP2":
            chord.drop2()

        elif vmode == "DROP2KEY":
            chord.drop2key()
            
        elif vmode == "DROP3":
            chord.drop3()
            
        elif vmode == "DROP3KEY":
            chord.drop3key()
            
        elif vmode == "DROP23":
            chord.drop23()
            
        elif vmode == "DROP23KEY":
            chord.drop23key()

        self.lastChord = chord.noteList[:]

        return vMove

    def trackBar(self, pattern, ctable):
        """ Do a chord bar. Called from self.bar() """

        sc = self.seq
        unify = self.unify[sc]

        # Set voicing move ONCE at the top of each bar.
        # The voicing code resets vmove to 0 the first
        # time it's used. That way only one movement is
        # done in a bar.

        vmove = 0

        if self.voicing.random:
            if random.randrange(100) <= self.voicing.random:
                vmove = random.choice((-1, 1))
        elif self.voicing.bcount and self.voicing.dir:
            vmove = self.voicing.dir


        for p in pattern:
            tb = self.getChordInPos(p.offset, ctable)

            if tb.chordZ:
                continue

            dupRoot = self.dupRoot[sc]

            vmode = self.voicing.mode
            vols = p.vol[0:tb.chord.noteListLen]

            # Limit the chord notes. This works even if THERE IS A VOICINGMODE!

            if self.chordLimit[0]:
                tb.chord.limit(*self.chordLimit)

            # Compress chord into single octave if 'compress' is set
            # We do it here, before octave, transpose and invert!
            # Ignored if we have a VOICINGMODE.

            if self.compress[sc] and not vmode:
                tb.chord.compress()

            # Do the voicing stuff.

            if vmode:
                vmove = self.chordVoicing(tb.chord, vmove)

            # Invert.

            if self.invert[sc]:
                tb.chord.invert(random.randrange(self.invert[sc][0], self.invert[sc][1]+1))

            # Voicing adjustment for 'jazz' or altered chords. If a chord (most
            # likely something like a M7 or flat-9 ends up with any 2 adjacent
            # notes separated by a single tone an unconfortable dissonance results.
            # This little check compares all notes in the chord and will cut the
            # volume of one note to reduce the disonance. Usually this will be
            # the root note volume being decreased.

            nl = tb.chord.noteList
            l = len(nl)
            for j in range(l - 1):
                r = nl[j]
                for i in range(j + 1, l):
                    if nl[i] in (r - 1, r + 1, r - 13, r + 13) and vols[i] >= vols[0]:
                        vols[j] = vols[i] // 2
                        break

            loo = list(zip(nl, vols))    # this is a note/volume array of tuples

            # DupRoot adds additional root tones in
            # different octaves to fatten chord sounds.

            if dupRoot:

                # Volume for the dups is adjusted by taking the
                # average of the non-zero volumes in the chord
                # and adjusting with the harmonyVolume.

                v = [x for x in vols if x > 0]
                if v:   # just in case we have a no-volume chord
                    v = int((sum(v) // len(v)) * self.harmonyVolume[sc])

                    root = tb.chord.rootNote  # true root of chord
                    for nn in dupRoot:
                        loo.append(((nn + root), v))

            # For strum we need to know the direction. Note that the direction
            # is saved for the next loop (needed for alternating in BOTH).

            sd = self.direction[sc]
            if sd == 'BOTH':
                if self.sortDirection:
                    self.sortDirection = 0
                else:
                    self.sortDirection = 1
            elif sd == 'DOWN':
                self.sortDirection = 1
            elif sd == 'RANDOM':
                self.sortDirection = random.randint(0, 1)
            else:
                self.sortDirection = 0

            if self.getStrum(sc):
                loo.sort()    # sort for strum only. If no strum it doesn't matter
                if self.sortDirection:
                    loo.reverse()

            # ornametation applies to the top note only. However,
            # we might need to step though the list of notes to find
            # a sounding note (volumes set to 0).
            offset = p.offset
            if self.ornaments['type']:
                while 1:
                    lo = loo.pop()
                    if lo[1]:
                        offset = MMA.ornament.doOrnament(self, [lo],
                                self.getChordInPos(p.offset, ctable).chord.scaleList, p)
                        break
                    elif not loo:
                        break
                    else:
                        continue
            
            # Handle a non-ornamented chord or the remainer of an ornamented one
            self.sendChord(loo, p.duration, offset)

            tb.chord.reset()    # important, other tracks chord object

        # Adjust the voicingMove counter at the end of the bar

        if self.voicing.bcount:
            self.voicing.bcount -= 1

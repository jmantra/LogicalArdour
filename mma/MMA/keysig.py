# keysig.py

"""
The program "MMA - Musical Midi Accompaniment" and the associated
modules distributed with it are protected by copyright.

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

Keysignature is used in the solo/melody tracks and for midinote.
A single instance class is created here and can be accessed from any
other module.

"""

from . import gbl
from   MMA.common import *
import MMA.debug

majKy = { "C" :  0, "G" :  1, "D" :  2,
          "A" :  3, "E" :  4, "B" :  5,
          "F#":  6, "C#":  7, "F" : -1,
          "Bb": -2, "Eb": -3, "Ab": -4,
          "Db": -5, "Gb": -6, "Cb": -7 }

minKy = { "A" :  0, "E" :  1, "B" :  2,
          "F#":  3, "C#":  4, "G#":  5,
          "D#":  6, "A#":  7, "D" : -1,
          "G" : -2, "C" : -3, "F" : -4,
          "Bb": -5, "Eb": -6, "Ab": -7 }

notevalues={
        'B#': 0, 'C' : 0, 'C#': 1, 'Db': 1,
        'D' : 2, 'D#': 3, 'Eb': 3, 'E' : 4,
        'Fb': 4, 'E#': 5, 'F' : 5, 'F#': 6,
        'Gb': 6, 'G' : 7, 'G#': 8, 'Ab': 8,
        'A' : 9, 'A#': 10,'Bb': 10,'B' : 11,
        'Cb':11 }


class KeySig:

    def __init__(self):
        self.kSig = 0
        self.kName = ['C', 0]
        self.setAccList()
        self.keyNoteValue = notevalues['C']

    def create(self, ln):
        """ Set the keysignature. Used by solo & aria tracks. Formats are:
              1. A,D,E, Eb,  etc followed by optional minor/major
                   flat can be b or &, sharp is #
              2. Number of sharps/flats plus option minor/major
                   id 3b or 2#
        """

        mi = 0   # assume Major

        if len(ln) < 1 or len(ln) > 2:
            error("KeySig: Needs 1 or 2 arguments.")

        # got 2 args, parse off minor/major

        if len(ln) == 2:
            l = ln[1][0:3].upper()
            if l == 'MIN':
                mi = 1
            elif l == 'MAJ':
                mi = 0
            else:
                error("KeySig: 2nd arg must be 'Major' or 'Minor', not '%s'" % ln[1])

        self.kName[1] = mi  # remember maj/min setting

        # get the key

        kname = ln[0][0]
        kname = kname.upper()
        if len(ln[0]) > 1:
            kname += ln[0][1:]

        if kname[0] in "ABCDEFG":
            if len(kname) == 2 and kname[1] == '&':
                kname = kname[0] + 'b'
            if mi and kname in minKy:
                self.kSig = minKy[kname]
                midikey = minKy[kname]
            elif not mi and kname in majKy:
                self.kSig = majKy[kname]
                midikey = majKy[kname]
            else:
                if mi:
                    t = 'minor'
                else:
                    t = 'major'
                error("KeySigs: keysignature '%s %s' is unknown/impossible." % (kname, t))
            self.kName[0] = kname  # save name ('C', "Eb", etc)

        elif kname[0] in "01234567":
            c = int(kname[0])

            if kname == '0':
                kname = '0#'
                
            if len(kname) < 2:
                error("KeySig: numerical keysig needs sharp/flat indicator.")

            f = kname[1].upper()

            if not f in ("B", "&", "#"):
                error("KeySig: 2nd char in KeySig must be 'b' or '#', not '%s'" % f)

            self.kSig = midikey = int(c)

            if f in ('B', '&'):
                self.kSig = -self.kSig
                midikey = -midikey
                
            if mi:
                z = minKy
            else:
                z = majKy
            for a in z:
                if z[a] == self.kSig:
                    self.kName[0] = a
                    break

        else:
            error("KeySig: unknown keysignature '%s'." % ln[0])

        # Set the midi meta track with the keysig. This doen't do anything
        # in the playback, but other programs may use it.

        if midikey < 0:
            midikey = 256 + midikey

        gbl.mtrks[0].addKeySig(gbl.tickOffset, midikey, mi)

        self.setAccList()

        self.keyNoteValue = notevalues[self.kName[0]]

        # Check for aria tracks. If found, reset the note list to null.
        for t in gbl.tnames:
            if gbl.tnames[t].vtype == 'ARIA':
                gbl.tnames[t].restart()

        if MMA.debug.debug:
            dPrint("KeySig: %s" % self.getKeysig())

    def getKeysig(self):
        """ Create a key sig string. """

        return "%s %s" % (self.kName[0], ('Major', 'Minor')[self.kName[1]])

    def setAccList(self):
        """ Create a keysig table. This table is created in __init__ and
            when a keysig changes. There is an entry for each note,
            either -1,0,1 corresponding to flat,natural,sharp. We populate
            the table for each bar from the keysig value.

            Melody/solo tracks are given a copy of the table when they can
            then modify.
         """

        acc = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0}

        # Current key negative values are flat, positive sharp
        ks = self.kSig

        if ks < 0:
            for a in range(abs(ks)):
                acc[['b', 'e', 'a', 'd', 'g', 'c', 'f'][a]] = -1

        else:
            for a in range(ks):
                acc[['f', 'c', 'g', 'd', 'a', 'e', 'b'][a]] = 1

        self.accList = acc

keySig = KeySig()    # single instance


def getTranspose(ln, err):
    """ Calc transpose. Used by global TRANSPOSE and Lyric Transpose= """

    # interval notation accepts Up-Perfect-Four (with hypens)
    if len(ln) == 1 and ln[0].count('-') == 2:
        ln = ln[0].split('-')
        
    # Simple semi-tone transpose. Just make sure it's 0 to 12
    if len(ln) == 1:
        value = stoi(ln[0], "%s: Argument must be an integer, not '%s'" % (err, ln[0]))
        if value < -12 or value > 12:
            error("%s: %s out-of-range; must be -12..12" % (err, value))

    # interval transposition uses "up/down interval
    # this needs exactly 3 args. eg: "Up Perfect 3"
    # Note: This does NOT properly set key name spellings (ie: C# vrs Db)
    elif len(ln) == 3:

        
        # see if the input is a unique abrev. At some point we should put
        # this in common.py ... if we decide to do more abrev. matching.
        def getAbrev(i, tb):
            mcount = 0
            i = i.upper()
            for f in tb:
                if f.startswith(i):
                    mcount += 1
                    match = f
            if mcount > 1:
                error("%s: '%s' is not a unique abreviation." % (err, i))
            if mcount < 1:
                error("%s: '%s' is unregonized for interval notation." % (err,i))
            return match

        num2text = {"1": "UNISON",
                    "2": "SECOND",
                    "3": "THIRD",
                    "4": "FOURTH",
                    "5": "FIFTH",
                    "6": "SIXTH",
                    "7": "SEVENTH",
                    "8": "OCTAVE"}
        
        ttable = {"PERFECT UNISON":     0,
                  "DIMINISHED SECOND":  0,
                  "AUGMENTED UNISON":   1,
                  "MINOR SECOND":       1,
                  "MAJOR SECOND":       2,
                  "DIMINISHED THIRD":   2,
                  "AUGMENTED SECOND":   3,
                  "MINOR THIRD":        3,
                  "MAJOR THIRD":        4,
                  "DIMINISHED FOURTH":  4,
                  "AUGMENTED THIRD":    5,
                  "PERFECT FOURTH":     5,
                  "AUGMENTED FOURTH":   6,
                  "DIMINISHED FIFTH":   6,
                  "PERFECT FIFTH":      7,
                  "DIMINISHED SIXTH":   7,
                  "AUGMENTED FIFTH":    8,
                  "MINOR SIXTH":        8,
                  "MAJOR SIXTH":        9,
                  "DIMINISHED SEVENTH": 9,
                  "AUGMENTED SIXTH":   10,
                  "MINOR SEVENTH":     10,
                  "MAJOR SEVENTH":     11,
                  "DIMINISHED OCTAVE": 11,
                  "PERFECT OCTAVE":    12 }

        # Each token might be an abrev. Convert them to full spellings.

        # 1st, get direction
        dir = getAbrev(ln[0], ('UP', 'DOWN'))
        if dir == 'UP':
            mul = 1
        elif dir == 'DOWN':
            mul = -1
        else:
            error("%s: Interval transpose needs 'UP/DOWN' as first arg, not '%s'." % (err, dir))

        # Get the interval

        if ln[2] in num2text:
            ln[2] = num2text[ln[2]]
            
        interval = '%s %s' % (getAbrev(ln[1], set([ a.split()[0] for a in ttable.keys()])),
                getAbrev(ln[2], set([ a.split()[1] for a in ttable.keys()])))
       
        if interval in ttable:
            value = ttable[interval]
        else:
            error("%s: Unknown/invalid interval '%s'. Valid keys are: %s." % \
                  (err, interval, ', '.join(ttable.keys())))

        value *= mul
        
    else:
        error("%s: Use single value for semitones (-3, 4) or proper "
              "interval ('Up Maj 3'), not '%s'." % (err, ' '.join(ln)))

    return value

def transpose(ln):
    """ Set transpose value. """

    if len(ln) and ln[0].upper() == 'ADD':
        ln = ln[1:]
        gbl.transpose += getTranspose(ln, "Transpose")
        if gbl.transpose < -12 or gbl.transpose > 12:
            error("Transose: Add option results in setting of '%s', must be -12 to 12." %
                  gbl.transpose)
    else:
        gbl.transpose = getTranspose(ln, "Transpose")

    if MMA.debug.debug:
        dPrint("Set Transpose to %s" % gbl.transpose)

# lyric.py

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
from   MMA.common import *
import MMA.paths
import MMA.debug

class Lyric:
    textev = None    # set if TEXT EVENTS (not recommended)
    barsplit = None    # set if lyrics NOT split into sep. events for bar
    versenum = 1       # current verse number of lyric
    dupchords = 0       # set if we want chords as lyric events
    transpose = 0       # tranpose chord names (for dupchords only)
    karmode = 0       # in kar mode use textevents, split at hyphens
    enabled = True    # set true/false 
    pushedLyrics = []

    transNames = (('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'),
                 ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'))

    transKey = 0   # 0==flat, 1=sharp

    chordnames = {
        'B#': 0, 'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
        'Fb': 4, 'E#': 5, 'F': 5, 'F#': 6,
        'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10, 'B': 11,
        'Cb': 11}

    def __init__(self):
        pass

    def setting(self):
        """ Called from macro. """

        a = "Event="

        if self.textev:
            a += "Text"
        else:
            a += "Lyric"

        a += " Split="
        if self.barsplit:
            a += "Bar"
        else:
            a += "Normal"

        a += " Verse=%s" % self.versenum

        a += " Chords="
        if self.dupchords:
            a += "On"
        else:
            a += "Off"

        a += " Transpose=%s" % self.transpose

        a += " CNames="
        if self.transKey:
            a += "Sharp"
        else:
            a += "Flat"

        a += " KAR="
        if self.karmode:
            a += "On"
        else:
            a += "Off"

        return a

    def option(self, ln):
        """ Set a lyric option. """

        ln, opts = opt2pair(ln)

        for o, v in opts:
            o = o.upper()
            v = v.upper()

            if o == 'EVENT':
                if v == 'TEXT':
                    self.textev = 1
                    warning("Lyric: Placing lyrics as TEXT EVENTS is not recommended")

                elif v == 'LYRIC':
                    self.textev = None
                    if MMA.debug.debug:
                        dPrint("Lyric: lyrics set as LYRIC events.")

                else:
                    error("Lyric: Valid options for EVENT are TEXT or LYRIC.")

            elif o == 'SPLIT':
                if v == 'BAR':
                    self.barsplit = 1
                    if MMA.debug.debug:
                        dPrint("Lyric: lyrics distributed thoughout bar.")

                elif v == 'NORMAL':
                    self.barsplit = None
                    if MMA.debug.debug:
                        dPrint("Lyric: lyrics appear as one per bar.")

                else:
                    error("Lyric: Valid options for SPLIT are BAR or NORMAL.")

            elif o == 'VERSE':
                if v.isdigit():
                    self.versenum = int(v)

                elif v == 'INC':
                    self.versenum += 1

                elif v == 'DEC':
                    self.versenum -= 1

                else:
                    error("Lyric: Valid options for VERSE are <nn>, INC or DEC")

                if self.versenum < 1:
                    error("Lyric: Attempt to set Verse to %s. Values must be > 0" % self.versenum)

                if MMA.debug.debug:
                    dPrint("Lyric: Verse number set to %s" % self.versenum)

            elif o == 'CHORDS':
                self.dupchords = getTF(v, "Lyric Chords")
                if MMA.debug.debug:
                    if self.dupchords:
                        dPrint("Lyric: Chords are duplicated as lyrics.")
                    else:
                        dPrint("Lyric: Chords are NOT duplicated as lyrics.")

            elif o == 'TRANSPOSE':
                addTrans = False
                for t in v.split(','):
                    if t.upper() == 'ADD': # keyword
                        addTrans=True
                    else:  # either int or up-maj-3, etc.
                        v = MMA.keysig.getTranspose([t], "Lyric Transpose")

                if addTrans:
                    self.transpose += v
                else:
                    self.transpose = v

                if MMA.debug.debug:
                    dPrint("Lyric: Chord names transposed %s steps." % self.transpose)

            elif o == 'ADDTRANSPOSE':
                self.transpose += MMA.keysig.getTranspose([v], "Lyric AddTranspose")

                if MMA.debug.debug:
                    dPrint("Lyric: Chord names transposed %s steps." % self.transpose)

            elif o == 'CNAMES':
                if v in ('#', 'SHARP'):
                    self.transKey = 1

                elif v in ('B', '&', 'FLAT'):
                    self.transKey = 0

                else:
                    error("Lyric CNames: expecting 'Sharp' or 'Flat', not '%s'" % v )

                if MMA.debug.debug:
                    msg = "Lyric: Chord names favor "
                    if self.transKey:
                        msg += "#."
                    else:
                        msg += "b."
                    dPrint(msg)

            elif o == 'KARMODE':
                k = getTF(v, "Lyric Kar")
                if k:
                    self.karmode = 1
                    if not hasattr(self, 'setkar'):
                        self.setkar = 1
                        meta = gbl.mtrks[0]
                        # this converts the "created" text to kar format
                        mt = meta.miditrk
                        if 0 in mt:   # don't bother if no events at 0
                            txt = None
                            for t, ev in enumerate(mt[0]):
                                if ev[1] == 1:
                                    ev = ev[3:]
                                    if ev.startswith(b"Created by MMA"):
                                        txt = b"@I " + ev
                                        del mt[0][t]
                                        break
                            if txt:
                                meta.addText(0, txt)
                        # other kar fields
                        meta.addText(0, b"@KMIDI KARAOKE FILE")
                        meta.addText(0, b"@V0100")
                        # change extension to .kar
                        MMA.paths.createOutfileName('.kar')
 
                if MMA.debug.debug:
                    msg = "Lyric: Karmode "
                    if self.karmode:
                        msg += "ENABLED."
                    else:
                        msg += "DISABLED."
                    dPrint(msg)

            else:
                error("Usage: Lyric expecting EVENT, SPLIT, VERSE, CHORDS, TRANSPOSE,"
                      "CNAMES, KARMODE, ENABLE or SET, not '%s'" % o)

        # All the opt=value options have been taken care of. ln can now only
        # contain "On", "OFF" or "Set ..." Anything else is an error.

        while 1:
            if not ln:
                return

            if ln[0].upper() == 'OFF':
                enable = False
                ln.pop(0)

            elif ln[0].upper() == 'ON':
                enable = True
                ln.pop(0)

            elif ln[0].upper() == "SET":
                s = ' '.join(ln[1:]).strip()

                if not s.startswith('['):
                    s = '[' + s + ']'

                self.pushedLyrics.append(s)
                ln = []

            else:
                error("Lyric: Unknown option '%s'." % ln[0])

    def leftovers(self):
        """ Just report leftovers on stack."""

        if self.pushedLyrics:
            warning("Lyrics remaining on stack")

    def extract(self, ln, rpt):
        """ Extract lyric info from a chord line and place in META track.

            Returns line and lyric as 2 strings.

            The lyric is returned for debugging purposes, but it has been
            processed and inserted into the MIDI track.
        """

        a = ln.count('[')
        b = ln.count(']')

        if a != b:
            error("Mismatched []s for lyrics found in chord line")

        if self.pushedLyrics:
            if a or b:
                error("Lyrics not permitted inline and as LYRIC SET")

            ln = ln + self.pushedLyrics.pop(0)
            a = b = 1   # flag that we have lyrics, count really doesn't matter

        ln, lyrics = pextract(ln, '[', ']')

        # If the CHORDS=TRUE option is set, make a copy of the chords and
        # insert as lyric. This permits illegal chord lines, but they will
        # be caught by the parser. NOTE: Also discards [] or SET lyrics.

        if self.dupchords:
            ly = []
            for v in ln.split():   # do each chord symbol or '/' mark

                if v != '/':
                    v = v.replace('&', 'b')    # remember, "&" is optional

                    if v == 'z' or v == 'z!':  # convert plain z to "NC"
                        v = 'N.C.'

                    if 'z' in v:               # strip out the 'zCDA..' after the chord
                        v = v.split('z')[0]

                    v = v.lstrip("+-")         # strip off leading "+" and "-"

                    if self.transpose:   # transpose will be set to 0, 1, -1, etc.
                        t = None         # Needed in case line is not a chord ('/', "NC")!

                        try:             # try for 2 char chord name (F#, Gb, etc)
                            cn = v[0:2]
                            t = self.chordnames[cn] + self.transpose
                        except:
                            try:         # try 1 char chord name (C, D, etc)
                                cn = v[0:1]
                                t = self.chordnames[cn] + self.transpose
                            except:
                                pass     # not a chord pitch

                        if t is not None:    # use None, 0 is okay
                            while t >= 12:
                                t -= 12
                            while t <= -12:
                                t += 12

                            v = self.transNames[self.transKey][t] + v[len(cn):]

                ly.append(v)

            i = int(gbl.QperBar - len(ly))
            if i > 0:
                ly.extend(['/'] * i)
            lyrics.insert(0, ' '.join(ly) + '\\r')

        v = self.versenum

        if len(lyrics) == 1:
            v = 1

        if v > len(lyrics):
            lyrics = ''
        else:
            lyrics = lyrics[v-1]

        if not len(lyrics):
            return (ln, [])

        lyrics = lyrics.replace('\\r', ' \\r ')
        lyrics = lyrics.replace('\\n', ' \\n ')
        lyrics = lyrics.replace('     ', ' ')

        if self.karmode:
            lyrics = lyrics.replace('\-', chr(1))
            lyrics = lyrics.replace('-', chr(0)+' ')

        if self.barsplit:
            lyrics = [lyrics]
        else:
            lyrics = lyrics.split()

        beat = 0
        bstep = gbl.QperBar / float(len(lyrics))

        for t, a in enumerate(lyrics):  # do by syllable
            a, b = pextract(a, '<', '>', onlyone=True)

            if self.dupchords:
                a=a.split("@")[0]  # ignore chord position marker
            
            if b and b[0]:
                beat = stof(b[0], "Expecting value in <%s> in lyric" % b)
                if beat < 1 or beat > gbl.QperBar+1:
                    error("Offset in lyric <> must be 1 to %s" % gbl.QperBar)
                beat -= 1
                bstep = (gbl.QperBar-beat)/float((len(lyrics)-t))

            a = a.replace('\\r', '\r')
            a = a.replace('\\n', '\n')

            if a and a != ' ':
                if a and self.karmode and (chr(0) in a or chr(1) in a):
                    a = a.replace(chr(0), '')
                    a = a.replace(chr(1), '-')
                elif not a.endswith('-') and not a.endswith('\n') and not a.endswith('\r'):
                    a += ' '

                # Call midi module to add lyric syllable to the MIDI track
                p = getOffset(beat * gbl.BperQ)
                if self.enabled:
                    if self.textev or self.karmode:
                        gbl.mtrks[0].addText(p, a)
                    else:
                        gbl.mtrks[0].addLyric(p, a)

            beat += bstep
        return (ln, lyrics)

# Create a single instance of the Lyric Class.

lyric = Lyric()

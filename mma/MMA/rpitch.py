# rpitch.py

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

from MMA.common import *
from . import gbl
import MMA.debug 

import random

class Rpitch:
    def __init__(self):
        self.scale = 'CHROMATIC'
        self.rate = .25   # 25%, apply to all notes
        self.beats = []  # list of beats to enable rnd
        self.offsets = []
        self.bars = []

def getOpts(self):
    """ Return string of current settings. """

    r = self.rPitch

    if not r:
        return "None"

    scale = r.scale
    rate = int(r.rate * 100)
    bars = ','.join([str(a + 1) for a in r.bars])
    if r.beats:
        beats = ','.join([str((a+1)//gbl.BperQ) for a in r.beats])
    else:
        beats = ''
    offsets = r.offsets
    if not offsets:
        offsets = 'None'
    else:
        offsets = ','.join([str(a) for a in offsets])

    return "Rate=%s ScaleType=%s Offsets=%s Bars=%s Beats=%s" % (rate, scale, offsets, bars, beats)

def setRPitch(name, ln):
    """ Set the pitch modifer.

        options:    Scale or ScaleType - chromatic, scale, chord
                    Rate - a percentage to apply. Default = 100%
                    Offsets - value to use. The values are offsets
                       and are applied to the current note.
                    Beats - the EXACT beats to limit rnd to.
    
    """

    self = gbl.tnames[name]
    self.rPitch = rp = Rpitch()
    
    msg = "%s RPitch" % self.name

    if self.vtype == 'DRUM':
        error("RPitch cannot be appied to a drum track %s." % self.name)

    if self.vtype == 'PLECTRUM':
        warning("RPitch is ignored by %s track." % self.name)
        return
    
    if not ln or len(ln) == 1 and ln[0].upper() in ("NONE", "OFF"):
        self.rPitch = None

    else:
        ln, opts = opt2pair(ln, toupper=True)

        if ln:
            error("%s all settings must be Cmd=Opt pairs, not '%s'" % (msg, ln))

        for o,c in opts:
            if o == 'SCALETYPE' or o == 'SCALE':
                if not c in ('CHROMATIC', 'SCALE', 'CHORD'):
                    error("%s Rpitch ScaleType: Only Chromatic, Scale and Chord "
                      "are valid." % self.name)
                rp.scale = c
                
            elif o == 'BARS':
                l = []
                if c:
                    for a in c.split(','):
                        a = stoi(a)
                        if a < 0:
                            error("%s Bars must be positive values, not '%s'." % (msg, a))
                        if a < 1 or a > gbl.seqSize:
                            warning("%s Bars: setting of %s may be ignored since "
                            "SeqSize is %s." % (msg, a, gbl.seqSize))
                        l.append(a - 1)
                rp.bars = l[:]

            elif o == 'BEATS':
                rp.beats = []
                for t in c.split(','):
                    v = stoi(t)
                    if v < 1 or v > gbl.QperBar:
                        error("%s Beat values must be in range 1 to %s, not '%s'." %
                              (msg, gbl.QperBar, v))
                    rp.beats.append((v - 1) * gbl.BperQ)  # save as tick offsets
                          
            elif o == 'RATE':
                v = stoi(c)
                if v < 0:
                    error("% must be positive, not '%s'." % (msg, v))
                rp.rate = v / 100.

            elif o == 'OFFSETS':
                l = []
                if c.upper() == 'NONE' or c == '0':
                    l = []
                else:
                    for a in c.split(','):
                        if a.startswith('-'):
                            a = a[1:]
                            neg = -1
                        else:
                            neg = 1
                        if '-' in a:
                            a,b=a.split('-',1)
                            a = stoi(a) * neg
                            b = stoi(b)
                            if b < a:
                                a,b=b,a
                            l.extend(range(a,b+1))
                        else:
                            a = stoi(a) * neg
                            l.append(a)
                for a in l:
                    if a < -12 or a > 12:
                        warning("%s value of %s is large." % (msg, a))
                        break
                rp.offsets = l[:]

            else:
                error("%s '%s' is an  unknown option." % (msg, o))

    if not rp.offsets:
        warning("%s No offsets have been set, command will have no effect." % msg)
        
    if MMA.debug.debug:
         MMA.debug.trackSet(self.name, "RPitch")

def doRpitch(self, position, note):
    """ Apply rpitch setting to note. Returns modified note.
        position -- current point in bar in ticks
        note -- note value (0-127) to modify
    """

    mode = self.rPitch.scale
    ch = self.rPitch.offsets

    if not ch:      # no offset table. User was warned
        return note

    # ..rate is stored as value .01 to .99 and random() returns in same range
    if random.random() > self.rPitch.rate:
        return note

    # we have a bar list but the current bar isn't there, just return.
    if self.rPitch.bars and gbl.seqCount not in self.rPitch.bars:
        return note

    # both beats and position are stored as tick values
    if self.rPitch.beats and position not in self.rPitch.beats:
        return note

    # just add/sub a value. 'ch' is a list of chord/scale offsets to use
    if mode == 'CHROMATIC':
        note += random.choice(ch)

    else:
        notelist = None
        if mode == 'SCALE' and self.currentChord and self.currentChord.chord.scaleList:
            notelist = list(self.currentChord.chord.scaleList)
        elif mode == 'CHORD' and self.currentChord and self.currentChord.chord.noteList:
            notelist = list(self.currentChord.chord.noteList)

        if notelist:  # will be a scale or chord list
            # select the offset to use from the offsets list
            change = random.choice(ch)
            if change < 0:
                neg = -1
                change = abs(change)
            else:
                neg = 1

            # Make sure scale list is long enuf. to select from
            # Simple: just keep doubling up the list. Note we need
            # to add the octave adjustment each time, and to keep incrementing it!
            o = 12
            while len(notelist) <= change:
                notelist.extend( [ i + o for i in notelist])
                o += 12
            note += ( notelist[change] * neg )

    # default fallthough
    while note > 127:
        note -= 12
    while note < 0:
        note += 12

    return note

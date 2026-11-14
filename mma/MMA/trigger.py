# trigger.py

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

All trigger functions.

"""

from MMA.common import *
import MMA.debug
from . import gbl
import MMA.truncate

import random
import copy 

# Each track class has a pointer to a unique copy of this object
class Trigger:
    def __init__(self):
        self.mode = None
        self.truncate = False
        self.count = 1
        self.bars = []
        self.beats = []
        self.seq = None
        self.measures = []
        self.cnames = []
        self.ctonics = []
        self.ctypes = []
        self.override = False


def makeTriggerSequence(self, ctable, pattern):
    """ Create a new sequence based on a trigger setting. 
        This is called only from bar().
    """

    trigger = self.trigger
    
    if trigger.bars and gbl.seqCount not in trigger.bars:
        return []

    if trigger.measures and gbl.barLabel not in trigger.measures:
        return []

    # Use the internal trigger sequence if it's set.
    # otherwise, use the pattern(s) from the
    # sequence set for the track.
    if trigger.seq:
        pattern = trigger.seq

    # Not redundant! 
    if not pattern:
        return []
    
    tpats = []

    # If we have trigger set to "AUTO" then we create a set of offsets
    # based on the chord changes in ctable.
    if trigger.mode == 'AUTO':
        trigs = []
        for c in ctable:
            if c.name != 'z' and c.name != c.lastchord:
                trigs.append(c.chStart)

    # This works with 'z' chords only, not 'XXzYY'
    elif trigger.mode == 'REST':
        trigs = []
        for c in ctable:
            if c.name == 'z' and c.name != c.lastchord:
                trigs.append(c.chStart)                    

    # different 'beat' combinations
    elif trigger.mode == 'BEATS':

        # If chord names are set set if the beat and the
        # chord NAME at that point
        if trigger.cnames:
            trigs = []
            for t in trigger.beats:
                for c in ctable:
                    if t >= c.chStart and t < c.chEnd and \
                             c.chord.name in trigger.cnames:
                        trigs.append(t)
                        break

        # Chord tonic names (C, D, E ... G)
        elif trigger.ctonics:
            trigs = []
            for t in trigger.beats:
                for c in ctable:
                    if t >= c.chStart and t < c.chEnd and \
                            c.chord.tonic in trigger.ctonics:
                        trigs.append(t)
                        break

        elif trigger.ctypes:
            trigs = []
            for t in trigger.beats:
                for c in ctable:
                    if t >= c.chStart and t < c.chEnd and \
                           c.chord.chordType in trigger.ctypes:
                        trigs.append(t)
                        break
                    
        # use the user defined beat list
        else:
            trigs = trigger.beats
        
    else:
        return []

    # make copies of pattern(s) for each beat.
    # the number of patterns to copy are determined by the 'count'
    # option (default==1).
    
    c = min(len(pattern), trigger.count)
    if c < 1:  # either no pattern or no count
        return []

    for t in trigs:
        for i in range(c):
            base = copy.deepcopy(pattern[i])
            base.offset += t 
            if base.offset >= gbl.barLen:
                continue
            tpats.append(base)

    # normalize the durations of the new patterns so they
    # terminate at the next pattern or the end of the bar
    if trigger.truncate:
        for i in range(len(tpats)):
           if i < len(tpats) - 1:  # another chord follows, truncate at start of next chord
               maxd = tpats[i+1].offset - tpats[i].offset
           else: # last chord, truncate at end of bar
               # Note to braindead self, the TRUNCATE option is
               # used to shorten a bar's duration. So the end of
               # bar can be 'gbl.barlen' or 'truncate.length'
               if MMA.truncate.length:
                   barEnd = MMA.truncate.length
               else:
                   barEnd = gbl.barLen
               maxd = barEnd - tpats[i].offset
           tpats[i].duration = min(tpats[i].duration, maxd)
    return tpats


def setTrigger(name, ln):
    """ Set a trigger for a track. 

        A trigger is simply a list of offsets which are processed
        by the trackBar() functions for each track.

        This is called from the parser. We grab the track class from 'name'.

    """

    self = gbl.tnames[name]

    if self.vtype in ('MELODY', 'SOLO'):
        error("Trigger is not valid in %s track." % self.vtype)

    self.trigger = trigger = Trigger()  # always reset to default

    sequence = None

    if not ln:        # empty line is same as singleton 'off'
        ln = ['OFF']

    argCount = len(ln)
    trigger.mode = 'ON'

    # extract a possible sequence. Only 1st is extracted and
    # saved for use by the 'SEQUENCE = ' command. The stuff in {}
    # is replaced by an empty {}.
    l = ' '.join(ln)
    if '{' in l and '}' in l:
        ln, sequence = pextract(l, '{', '}', onlyone=True, insert='{}')
        ln = ln.split()
        sequence = sequence[0]

    ln, opts = opt2pair(ln)

    ##########################
    # do opts with args

    for cmd, opt in opts:
        cmd = cmd.upper()
        if cmd == 'BEATS':
            trigger.mode = 'BEATS'
            for t in opt.split(','):
                trigger.beats.append(self.setBarOffset(t))
            trigger.beats.sort()

        elif cmd == 'BARS':
            for t in opt.split(','):
                v = stoi(t)
                if v < 1 or v > gbl.seqSize:
                    warning("%s Trigger Bars: setting of %s may be "
                            "ignored since SeqSize is %s." %
                            (self.name, v, gbl.seqSize))
                trigger.bars.append(v - 1)

        elif cmd == 'CNAMES':
            for a in opt.split(','):
                trigger.cnames.append(a)

        elif cmd == 'CTYPES':
            for a in opt.split(','):
                trigger.ctypes.append(a)

        elif cmd == 'CTONICS':
            for a in opt.split(','):
                trigger.ctonics.append(a)

        elif cmd == 'COUNT':
            trigger.count = stoi(opt)
            if trigger.count <= 0:
                error("%s Trigger Count must be greater than 0, not '%s'." %
                      (self.name, trigger.count))

        elif cmd == 'MEASURES':
            for a in opt.split(','):
                if not a.isdigit():
                    warning("%s Trigger: Measures should be bar labels, not '%s'."
                            "This trigger will be ignored." % (self.name, a))
                    continue
                trigger.measures.append(a.lstrip('0'))

        elif cmd == 'OVERRIDE':
            trigger.override = getTF(opt, "Trigger 'OverRide'")

        elif cmd == 'TRUNCATE':
            trigger.truncate = getTF(opt, "Trigger 'Turncate'")

        elif cmd == 'SEQUENCE':
            if not sequence and opt:
                sequence = opt
            if sequence:
                sequence = sequence.rstrip('; ')
                trigger.seq = self.defPatRiff(sequence)
            else:
                error("%s Trigger Sequence expecting {patterns...}." % self.name)

        elif cmd == 'STICKY':
            self.sticky = getTF(opt, "Trigger 'Sticky'")

        else:
            error("%s Trigger '%s' is an unknown command." % (self.name, cmd))

    # opts without args
    for cmd in ln:
        cmd = cmd.upper()
        if cmd == 'AUTO':
            trigger.mode = 'AUTO'

        elif cmd == 'OFF': # It's all been set to default at top, so leave it alone
            if argCount > 1:
                error("Trigger: 'OFF' argument must be the only arg.")

        elif cmd == 'REST':
            trigger.mode = 'REST'

        else:
            error("%s Trigger '%s' is an unknown command." % (self.name, cmd))

    if MMA.debug.debug:
        MMA.debug.trackSet(self.name, "TRIGGER")

def getTriggerOptions(self):
    """ Called from setTrigger() and macro. Returns string with current options. """

    trigger = self.trigger

    mode = ''

    if trigger.mode in ('AUTO', 'REST'):
        mode = trigger.mode
    
    if not trigger.beats:
        beats = '[]'
    else:
        beats =  ','.join([str(1 + (i / float(gbl.BperQ))) for i in trigger.beats])

    if trigger.cnames:
        cnames = ','.join([i for i in trigger.cnames])
    else:
        cnames = '[]'

    if trigger.ctypes: 
        ctypes = ','.join([i for i in trigger.ctypes])
    else:
        ctypes = '[]'

    if trigger.ctonics:
        tonics = ','.join([i for i in trigger.ctonics])
    else:
        tonics = '[]'

    if not trigger.bars:
        bars = '[]'
    else:
        bars = ','.join([str(a + 1) for a in trigger.bars])

    if trigger.seq:
        seq =  "Sequence={%s}" % self.formatPattern(trigger.seq)
    else:
        seq = "Sequence={}"

    if trigger.measures:
        measures = ','.join([i for i in trigger.measures])
    else:
        measures = '[]'
        
    return "%s Beats=%s CNames=%s CTypes=%s CTonics=%s Bars=%s " \
              "Count=%s Truncate=%s Override=%s Measures=%s %s" % \
          ( mode, beats, cnames, ctypes, tonics, bars, trigger.count,
            trigger.truncate, trigger.override, measures, seq)


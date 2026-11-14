# tempo.py

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
from MMA.common import *
from MMA.midiM import packBytes, byte3ToInt
from MMA.timesig import timeSig
from struct import unpack
from MMA.parseCL import setChordTabs
import MMA.debug
import MMA.midi

# this is a TIME option to compensate for tempos with an
# non-4 in the denominator. Needs to be reset for every
# TIME change.


######################################
# Tempo/timing

timeTable = {
    # duple times
    '2/2': (4,    (1, 3)),
    '2/4': (2,    (1, 2)),
    '6/4': (6,    (1, 4)),
    '6/8': (6,    (1, 4)),   # need this way to keep compatible with 'stdpats68'

    # triple
    '3/2': (6,    (1, 3, 5)),
    '3/4': (3,    (1, 2, 3)),
    '3/8': (1.5,  (1, 1.5, 2)),
    '9/8': (4.5,  (1, 2.5, 4)),

    # quadruple
    '4/4': (4,    (1, 2, 3, 4) ),
    '12/8':(6,    (1, 2.5, 4, 5.5)),

    # quintuple
    '5/4': (5,    (1, 2, 3, 4, 5) ),
    '5/8': (2.5,  (1, 1.5, 2, 2.5, 3 ) ),

    # septuple
    '7/4': (7,    (1, 2, 3, 4, 5, 6, 7) )
 }

def setTime(ln):
    """ Set the 'time' value. This is NOT a time sig, it
        is the number of quarters/beat.

        We do restrict the time setting to the range of 1..12.
        No particular reason, but we do need some limit? Certainly
        it has to be greater than 0.
    """

    
    tabList = []
    defaultTabs = (1,2,3,4,5,6,7,8,9,10,11,12)
    sigSet = False

    ln, options = opt2pair(ln, toupper=True)

    for cmd, opt in options:
        if cmd == 'TABS':
            tabList = [ stof(i) for i in opt.split(',')]
            if tabList != sorted(tabList):
                error("Time: Tabs must be in order, not %s." % tabList)
            if len(tabList) != len(set(tabList)):
                error("Time: Tabs must not contain duplicates, %s" % tabList)
            if tabList[0] != 1:
                error("Time: First tab must be 1, not %s." % tabList[0])

        else:
            error("TIME: Unknown option '%s'." % cmd)

    if len(ln) != 1:
        error("Time: Too many options. Use TIME BperBar [Tabs=xx].")

    # is this a timesig?

    n = ln[0]
    if n.upper() == 'COMMON':
        n = '4/4'
    elif n.upper() == 'CUT':
        n = '2/2'

    if n in timeTable:
        i = timeTable[n]
        timeSig.setSig([n])
        n = i[0]
        if not tabList:
            tabList = i[1]
        sigSet = True
    else:
        if '/' in n:  # unknown time sig
            error("Time: Unknown timesignature '%s'. You may need "
                  "to set TIME and TIMESIG separately." % n)
        n = stof(n)

        if n < 1 or n > 12:
            error("Time: Value must be 1..12.")

    # If no change, just ignore this.

    origTime = gbl.QperBar
    if origTime != n:
        gbl.QperBar = n
        gbl.barLen =  int(gbl.QperBar * gbl.BperQ)

        # Time changes zap all predfined sequences

        for a in gbl.tnames.values():
            if a.riff:
                warning("Time: Change from %s to %s deleting %s riffs." %
                        (origTime, n, a.name))
                a.riff = []
            a.clearSequence()

    if not tabList:
        tabList = (1,2,3,4,5,6,7,8,9,10,11,12)[:int(gbl.QperBar)]

    # need to do this after setting time.
    if (tabList[-1]-1) * gbl.BperQ >= gbl.barLen:
        error("Time: Last tab must be < %s, not '%s'." %
              (float(gbl.barLen/gbl.BperQ)+1, tabList[-1]))

    setChordTabs(tabList)

    if MMA.debug.debug:
        if sigSet:
            sig =  "TimeSig %s " % timeSig.getAscii()
        else:
            sig = ''
        dPrint ("Time: Time %s %sTabs=%s." %
               (gbl.QperBar, sig,  ','.join([str(x) for x in tabList])))
        
    
def tempo(ln):
    """ Set tempo.

        Note: All tempo stuff is inserted into the meta track.
    """

    startOffset = 0
    restore = 0
    origTempo = gbl.tempo

    ln, opts = opt2pair(ln, toupper=True)

    # Parse off options

    for cmd, opt in opts:
        if cmd == 'OFFSET':
            startOffset = stotick(opt, 'B', "TEMPO Offset: '%s' is not recognized."
                                  % opt) // gbl.BperQ
            if startOffset < 0:
                error("TEMPO Offset: Must be => 0, not '%s'" % startOffset)

        elif cmd == 'RESTORE':
            restore = stotick(opt, 'B', "TEMPO Restore: '%s' is not recognized."
                                  % opt) + gbl.tickOffset
            print(restore, opt, gbl.tickOffset)
            if restore < 0:
                error("TEMPO Restore: Must be => 0, not '%s'" % restore)

        else:
           error("Tempo '%s' is an unknown command." % cmd)

    if not ln or len(ln) > 2:
        error("Tempo: Use [*,+,-]BperM [BARS]")

    # Get new value.

    a = ln[0][0]
    if a in "+-*":
        v = stof(ln[0][1:], "Tempo: Expecting value for rate adjustment, not '%s'" % ln[0])
        if a == '-':
            v = gbl.tempo - v
        elif a == '+':
            v += gbl.tempo
        elif a == '*':
            v *= gbl.tempo

    else:
        v = stof(ln[0], "Tempo: Expecting rate, not '%s'" % ln[0])
        
    if v <= 1:
        error("Tempo: Value must be greater than 1.")

    # is this immediate or over time?

    if len(ln) == 1:
        gbl.tempo = int(v) 

        gbl.mtrks[0].addTempo(gbl.tickOffset + startOffset, gbl.tempo)
        lastChange = gbl.tickOffset + startOffset

        if MMA.debug.debug:
            dPrint("Tempo: Set to %s, offset=%s beats" % (gbl.tempo, startOffset/gbl.BperQ))

    else:              # Do a tempo change over bar count
        numbeats = stotick(ln[1], 'B', "TEMPO Offset: '%s' is not recognized."
                                  % ln[1]) // gbl.BperQ

        if numbeats < 1:
            error("Tempo: Beat count must be greater than 0")

        # Vary the rate in the meta track

        tincr = (v - gbl.tempo) / float(numbeats)    # incr per beat
        bstart = gbl.tickOffset + startOffset            # start
        boff = 0
        tempo = gbl.tempo

        for n in range(numbeats):
            tempo += tincr
            if tempo:
                gbl.mtrks[0].addTempo(bstart + boff, int(tempo))
            boff += gbl.BperQ

        if tempo != v:
            gbl.mtrks[0].addTempo(bstart + boff, int(v))

        lastChange = bstart+boff

        gbl.tempo = int(v)

        if MMA.debug.debug:
            dPrint("Tempo: Set future value to %s over %s beats" %
                (int(tempo), numbeats))

    # Restore the original tempo after specified beats.
    if restore:
        gbl.mtrks[0].addTempo(restore, origTempo)
        gbl.tempo = origTempo   # not really right, this tempo will be in effect later
        lastChange = restore
        if MMA.debug.debug:
            dPrint("Tempo: Restored to %s in %s beats" %
               (origTempo, (restore-gbl.tickOffset)/gbl.BperQ))
        
    if gbl.tempo <= 0:
        error("Tempo: Setting must be greater than 0.")

    # Check meta track for any tempo changes past the last one
    # we've just inserted.

    for p, v in MMA.midi.tempoChanges:
        if p > lastChange:
            warning("Tempo change may be invalid since there are more changes after this point.")
            break

def beatAdjust(ln):
    """ Delete or insert some beats into the sequence.

        This just adjusts the current song position. Nothing is
        lost or added to the actual file.
    """

    if len(ln) != 1:
        error("BeatAdjust: Expecting single value.")

    adj = stotick(ln[0], 'B', "BeatAdjust: Expecting a value (not %s)." % ln[0])
    gbl.tickOffset += adj
    gbl.totTime += (adj / gbl.BperQ) / gbl.tempo   # adjust total time

    if MMA.debug.debug:
        dPrint("BeatAdjust: inserted %s ticks at bar %s." % (adj, gbl.barNum + 1))

def cut(ln):
    """ Insert a all-note-off into ALL tracks. """

    if not len(ln):
        ln = ['0']

    if len(ln) != 1:
        error("Cut: Expecting single offset or empty argument.")

    """ Loop though all the tracks. Note that trackCut() checks
        to make sure that there is a need to insert in specified track.
        In this loop we create a list of channels as we loop though
        all the tracks, skipping over any duplicate channels or
        tracks with no channel assigned.
    """

    l = []
    for t in sorted(gbl.tnames.keys()):
        c = gbl.tnames[t].channel
        if not c or c in l:
            continue
        l.append(c)
        trackCut(t, ln)


def trackCut(name, ln):
    """ Insert a ALL NOTES OFF at the given offset. """

    if not len(ln):
        ln = ['0']

    if len(ln) != 1:
        error("Cut %s: Offset missing." % name)

    offset = stof(ln[0], "Cut %s: Expecting value, (not '%s') for offset." % (name, ln[0]))

    if offset < -gbl.QperBar or offset > gbl.QperBar:
        warning("Cut %s: %s is a large beat offset" % (name, offset))

    moff = int(gbl.tickOffset + (gbl.BperQ * offset))

    if moff < 0:
        error("Cut %s: Offset comes before start of track." % name)

    # Insert allnoteoff directly in track. This skips the normal
    # queueing in pats because it would never take if at the end
    # of a track.

    m = gbl.tnames[name].channel
    if m and len(gbl.mtrks[m].miditrk) > 1:
        gbl.mtrks[m].addNoteOff(moff)

        if MMA.debug.debug:
            dPrint("Cut %s: Beat %s, Bar %s" % (name, offset, gbl.barNum + 1))


def fermata(ln):
    """ Apply a fermata timing to the specified beat. """

    if len(ln) != 3:
        error("Fermata: use 'offset' 'duration' 'adjustment'")

    offset = stof(ln[0], "Fermata: Expecting a value (not '%s') for offset" % ln[0])

    if offset < -gbl.QperBar or offset > gbl.QperBar:
        warning("Fermata: %s is a large beat offset" % offset)

    dur = stof(ln[1], "Fermata: Expecting a value (not '%s') for duration" % ln[1])

    if dur <= 0:
        error("Fermata: duration must be greater than 0")

    if dur > gbl.QperBar:
        warning("Fermata: %s is a large duration." % dur)

    adj = stof(ln[2], "Fermata: expecting a value (not '%s') for adjustment." % ln[2])

    if adj < 100:
        warning("Fermata: Adjustment less than 100 is shortening beat value.")

    if adj == 100:
        error("Fermata: using value of 100 makes no difference, must be an error.")

    moff = int(gbl.tickOffset + (gbl.BperQ * offset))

    if moff < 0:
        error("Fermata: Offset comes before track start.")

    if offset >= 0:
        warning("Fermata: Better results when placed after event (negative offset).")

    fermataDuration = int(gbl.BperQ * dur)  # Duration in ticks
    mend = moff + fermataDuration

    # This next section is needed to figure out the start tempo (which
    # is not always gbl.tempo!), the needed tempo at the end of the fermata
    # section (again, not always gbl.tempo!) and to delete any tempo changes
    # in the section. All this due to the effects of tempo changes over a
    # a set of bars.

    # Extract ALL tempo changes from the meta track and save in a list.
    # Also, delete any tempo changes found in the miditrack in our range.

    tempos = []
    tcmd = packBytes((0xff, 0x51, 0x03))   # midi TEMPO
    mt = gbl.mtrks[0].miditrk  # The meta track

    # 1st we copy existing tempos into a new list
    for t in mt:
        for ev in mt[t]:
            if ev[0:3] == tcmd:
                tempos.append((t, ev[3:]))  # save the 24 bit value

    # now we delete any tempos in the fermata range. This avoids broken loops
    for t, ev in tempos:
        if t >= moff and t <= mend:
            gbl.mtrks[0].delDup(t, tcmd)

    # find last tempo before fermata bock and last tempo in block
    tempos.sort()
    oldTempo = gbl.tempo
    newTempo = gbl.tempo

    for f, t in tempos:   # f==offsets, t==encoded tempos
        if f <= moff:
            oldTempo = 60000000 // byte3ToInt(t)
        if f >= moff and f <= mend:
            newTempo = 60000000 // byte3ToInt(t)

    gbl.mtrks[0].addTempo(moff, int(oldTempo / (adj / 100)))
    gbl.mtrks[0].addTempo(mend, newTempo)

    # Move selected events in the effected area to it's start/end.
    #   To start -> note on, program change
    #   to end   -> note off
    # Done only if the fermata comes after desired location ...
    # otherwise there aren't any events to zap!

    if offset < 0:
        for n, tr in gbl.mtrks.items():  # do each track
            if n <= 0:
                continue        # skip meta track

            trk = gbl.mtrks[n].miditrk
            startEvents = []
            endEvents = []

            for f in sorted(trk):          # all in this track (sort keeps orig order)
                if f > moff and f < mend:  # well, only in the fermata range
                    remain = []
                    for ev in trk[f]:      # all events in the offset
                        if not ev:         # skip empty events
                            continue
                        # Get event type. The [0:1] is needed to
                        # maintain this as a byte() for python3, otherwise
                        # py3 will think it's an int() and barfs
                        evtype = unpack('B', ev[0:1])[0] >> 4
                        if evtype == 0x9:         # note event
                            if ev[2] == 0:    # off to end
                                endEvents.append(ev)
                            else:
                                startEvents.append(ev)  # on to start
                            continue
                        if evtype == 0xb or evtype == 0xc:  # program/controller change
                            startEvents.append(ev)          # all to start (??)
                            continue
                        remain.append(ev)
                    trk[f] = remain        # remaining events for this offset

            if startEvents:
                if moff in trk:
                    trk[moff].extend(startEvents)
                else:
                    trk[moff] = startEvents

            if endEvents:
                if mend in trk:
                    trk[mend] = endEvents + trk[mend]
                else:
                    trk[mend] = endEvents

    if MMA.debug.debug:
        dPrint("Fermata: Beat %s, Duration %s, Change %s, Bar %s" % 
              (offset, dur, adj, gbl.barNum + 1))
        if offset < 0:
            dPrint("         NoteOn Events moved in tick range %s to %s" 
                  % (moff + 1, mend - 1))

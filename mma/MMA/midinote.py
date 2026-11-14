# midinote.py

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

This module does all the midinote stuff.

"""


import MMA.notelen
import MMA.midiC
from   MMA.midiM import packBytes
import MMA.debug
from . import gbl
from   MMA.common import *
from   MMA.keysig import keySig


def parse(name, ln):
    """ Called from parser for a <Track MidiNote> This figures the right routine."""

    if not len(ln):
        error("MidiNote: Needs arguments")

    trk = gbl.tnames[name]

    # parse out the cmd=value options pairs

    ln, opts = opt2pair(ln)

    for o, v in opts:
        o = o.upper()
        v = v.upper()
        if o == 'TRANSPOSE':
            if v in ('0', 'OFF'):
                trk.transpose = 0
            elif v in ('1', 'ON'):
                trk.transpose = gbl.transpose
            else:
                error("MIDINote: TRANSPOSE expecting ON or OFF, not %s." % v)

        elif o == 'OFFSETS':
            if v == 'BEATS':
                trk.useticks = 0
            elif v == 'TICKS':
                trk.useticks = 1
            else:
                error("MIDINote: OFFSETS expecting BEATS or TICKS, not %s." % v)

        elif o == 'DURATION':
            if v == 'NOTES':
                trk.tickdur = 0
            elif v == 'TICKS':
                trk.tickdur = 1
            else:
                error("MIDINote: DURATION expecting NOTES or TICKS, not %s." % v)

        elif o == 'ARTICULATE':
            if v in ('1,' 'ON'):
                trk.articulate = 1
            elif v in ('0', 'OFF'):
                trk.articulate = 0
            else:
                error("MIDINote: ARTICULATE expecting ON or OFF, not %s." % v)

        elif o == 'OCTAVE':
            trk.oadjust = stoi(v)
            if trk.oadjust < -4 or trk.oadjust > 4:
                error("MIDINote: Octave adjustment must be -4..4, not '%s'." % trk.oadjust)

        elif o == 'VOLUME':
            trk.vadjust = stof(v) / 100
            if trk.vadjust <= 0:
                error("MIDINote: Volume %% adjustment must be > 0, not '%s'." % trk.vadjust)

        elif o == 'ADJUST':
            trk.tadjust = stoi(v)

        else:
            error("MIDINote: unknown option pair %s=%s." % (o, v))
    
    # end of option pairs.

    if ln:  # process rest of the stuff ... real midi events.

        trk.setForceOut()

        a = ln[0].upper()

        if a[0] in (".0123456789"):
            insertNote(trk, ln)

        elif a == "NOTE":
            insertNote(trk, ln[1:])

        elif a == "PB":
            insertPB(trk, ln[1:])

        elif a == "PBR":
            insertPBrange(trk, ln[1:])

        elif a == "CTRL":
            insertControl(trk, ln[1:])

        elif a == "CHAT":
            insertChTouch(trk, ln[1:])

        elif a == "CHATR":
            insertChTouchRange(trk, ln[1:])

        else:
            error("MidiNote: Unknown command '%s'." % a)

    if MMA.debug.debug:
        if opts:
            dPrint("MIDINOTE: %s" % mopts(trk))


def mopts(trk):
    """ Return options string to macro and setoption-debug. """

    if trk.useticks:
        a1 = 'Ticks'
    else:
        a1 = 'Beats'

    if trk.tickdur:
        a2 = 'Ticks';
    else:
        a2 = 'Notes'

    if trk.transpose:
        a3 = 'On'
    else:
        a3 = 'Off'

    if trk.articulate:
        a4 = 'On'
    else:
        a4 = 'Off'

    return "Offsets=%s Duration=%s Transpose=%s Articulate=%s Adjust=%s Volume=%s Octave=%s" \
        % (a1, a2, a3, a4, trk.tadjust, trk.vadjust * 100, trk.oadjust)


def getoffset(trk, v):
    """ Convert a string (value) to an offset. Convert to beats if nesc."""

    offset = stof(v)
    if trk.useticks:
        if offset != int(offset):
            error("MidiNote: Offset set to ticks, float '%s' given. Integer must be used." %
                  offset)
        offset += trk.tadjust

    else:
        if offset < 1:
            warning("MidiNote: Offset %s generates notes before start of current bar." % offset)

        if offset >= gbl.QperBar + 1:
            warning("MidiNote: Offset %s is past end of current bar." % offset)

        offset = (offset-1) * gbl.BperQ

    return int(offset)  # conversion to int is nescessary


def note2val(trk, acctable, orig):
    """ Convert a note name to a value. In this case the OCTAVE setting
        is used!
    """

    t = list(orig)
    n = t.pop(0)
    try:
        val = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}[n]
    except:
        error("MidiNote: Expecting valid note name, not '%s'." % orig)

    val += trk.octave[gbl.seqCount]  # add in current octave

    # Modify the note with either the keysignature or given accidental.

    if t:   # override modifier if #,& or n
        if t[0] == '#':
            acctable[n] = 1
            t.pop(0)
        elif t[0] == '&':
            acctable[n] = -1
            t.pop(0)
        elif t[0] == 'n':
            acctable[n] = 0
            t.pop(0)

    val += acctable[n]

    # adjust for octave - or +

    while t and (t[0] == '-' or t[0] == '+'):
        if t[0] == '+':
            val += 12
        else:
            val -= 12
        t.pop(0)

    if t:  # anything left? Error.
        error("MidiNote: Unknown note specifier '%s' in '%s'." % (''.join(t), orig))

    return val


def insertNote(trk, ln):
    """ Insert specified (raw) MIDI notes into track. """

    if len(ln) != 4:
        error("Use: %s MidiNote: <offset> <note> <velocity> <duration>" % trk.name)

    acctable = keySig.accList   # keysig modifier, use for chord

    offset = getoffset(trk, ln[0])

    # Set a flag if this is a drum track.

    if trk.vtype == 'DRUM':
        isdrum = 1
    elif trk.vtype in ('MELODY', 'SOLO') and trk.drumType:
        isdrum = 1
    else:
        isdrum = 0

    notes = []
    for n in ln[1].split(','):
        if n[0] in '0123456789':
            n = stoi(n)
        else:
            if isdrum:
                if n == '*':
                    if trk.vtype in ('MELODY', 'SOLO'):
                        n = trk.drumTone
                    else:
                        n = trk.toneList[gbl.seqCount]
                else:
                    n = MMA.midiC.drumToValue(n)
                    if n < 0:
                        error("MidiNote: unknown drum tone '%s' in %s." % (n, trk.name))
            else:
                n = note2val(trk, acctable, n)

        if n < 0 or n > 127:
            error("MidiNote: Notes must be in the range 0...127, not %s" % n)

        if trk.transpose and not isdrum:
            n += gbl.transpose
            while n < 0:
                n += 12
            while n > 127:
                n -= 12

        if trk.oadjust and not isdrum:
            n += (trk.oadjust * 12)
            while n < 0:
                n += 12
            while n > 127:
                n -= 12

        notes.append(n)

    velocity = stoi(ln[2])

    if velocity < 1 or velocity > 127:
        error("MidiNote: Note velocity must be in the range 1...127, not %s" % velocity)

    velocity *= trk.vadjust

    if velocity < 1:
        velocity = 1
    elif velocity > 127:
        velocity = 127

    velocity = int(velocity)   # trk.adjust can be a float

    if trk.tickdur:
        duration = stoi(ln[3])
    else:
        duration = MMA.notelen.getNoteLen(ln[3])
        if trk.articulate:
            duration = (duration * trk.artic[gbl.seqCount]) // 100
            if duration < 1:
                duration = 1

    channel = trk.channel
    track = gbl.mtrks[channel]

    for n in notes:
        onEvent = packBytes((0x90 | channel-1, n, velocity))
        offEvent = packBytes(onEvent[:-1], 0)

        track.addToTrack(gbl.tickOffset + offset, onEvent)
        track.addToTrack(gbl.tickOffset + offset + duration, offEvent)

    if MMA.debug.debug:
        dPrint("MidiNote Note %s: inserted note %s at offset %s." % (trk.name, notes, offset))


def insertPB(trk, ln):
    """ Insert a pitch controller event. """

    if len(ln) != 2:
        error("MidiNote: PB expecting 2 arguments.")

    offset = getoffset(trk, ln[0])
    v = stoi(ln[1])

    if v < -8192 or v > 8191:
        error("MidiNote: PB value must be -8192..+8191, not '%s'." % v)

    v += 8192  # convert to 0..16383, max 14 bit value

    channel = trk.channel
    track = gbl.mtrks[channel]
    track.addToTrack(gbl.tickOffset + offset, packBytes((0xe0 | channel-1, v % 128, v // 128)))

    if MMA.debug.debug:
        dPrint("MidiNote PB %s: inserted bend %s at offset %s." % (trk.name, v-8192, offset))


def insertPBrange(trk, ln):
    """ Insert a range of PB events. """

    if len(ln) != 3:
        error("MidiNote: PBR expecting 3 arguments <count> <start,end> <v1,v2>.")

    count = stoi(ln[0])
    try:
        s1, s2 = ln[1].split(',')
    except:
        error("MidiNote PBR: event range must be 'v1,v2', not '%s'." % ln[1])
    s1 = getoffset(trk, s1)
    s2 = getoffset(trk, s2)
    tinc = (s2-s1) / float(count)

    try:
        v1, v2 = ln[2].split(',')
    except:
        error("MidiNote PBR: pitch blend range must be 'v1,v2', not '%s'." % ln[2])
    v1 = stoi(v1)
    v2 = stoi(v2)

    if v1 < -8192 or v1 > 8191 or v2 < -8192 or v2 > 8191:
        error("MidiNote: PBR values must be -8192..+8191, not '%s'." % ln[2])

    v1 += 8192  # convert to 0..16383, max 14 bit value
    v2 += 8192
    vinc = (v2-v1) / float(count)

    channel = trk.channel
    track = gbl.mtrks[channel]

    ev = packBytes(0xe0 | channel-1)
    offset = s1
    bend = v1
    for i in range(count+1):
        v = int(bend)
        track.addToTrack(gbl.tickOffset + int(offset), packBytes(ev, v % 128, v // 128))
        offset += tinc
        bend += vinc

    if MMA.debug.debug:
        dPrint("MidiNote PBR %s: inserted bends %s to %s at offsets %s to %s." % 
            (trk.name, v1-8192, v2-8192, s1, s2))


def insertControl(trk, ln):
    """ Insert a controller event. """

    if len(ln) != 3:
        error("MidiNote: Controller expecting 3 arguments.")

    offset = getoffset(trk, ln[0])

    v = MMA.midiC.ctrlToValue(ln[1])
    if v < 0:
        v = stoi(ln[1])
        if v < 0 or v > 0x7f:
            error("MidiNote: Controller values must be 0x00 to 0x7f, not '%s'." % ln[1])

    d = stoi(ln[2])
    if d < 0 or d > 0x7f:
        error("MidiNote: Control Datum value must be 0x00 to 0x7f, not '%s'." % ln[2])

    channel = trk.channel
    track = gbl.mtrks[channel]

    # bypass the addctl() defined in midi.py just to keep all the calls in this
    # module similar. We should have add**() command in midi.py for the above stuff
    # and redo this.???

    track.addToTrack(gbl.tickOffset + offset, packBytes((0xb0 | channel-1, v, d)) )

    if MMA.debug.debug:
        dPrint("MidiNote Ctrl %s: inserted Controller %s value %s at offset %s." % 
            (trk.name, v, d, offset))


def insertChTouch(trk, ln):
    """ Insert a channel aftertouch) event. """

    if len(ln) != 2:
        error("MidiNote: ChAT expecting 2 arguments.")

    offset = getoffset(trk, ln[0])

    v = stoi(ln[1])

    if v < 0 or v > 127:
        error("MidiNote: ChAT value must be 0 .. 127, not '%s'." % v)

    channel = trk.channel
    track = gbl.mtrks[channel]

    track.addToTrack(gbl.tickOffset + offset, packBytes((0xd0 | channel-1, v)))
 
    if MMA.debug.debug:
        dPrint("MidiNote ChAT %s: inserted channel aftertouch %s at offset %s." % 
            (trk.name, v, offset))


def insertChTouchRange(trk, ln):
    """ Insert a range of channel aftertouch events. """

    if len(ln) != 3:
        error("MidiNote: ChATR expecting 3 arguments <count> <start,end> <v1,v2>.")

    count = stoi(ln[0])
    try:
        s1, s2 = ln[1].split(',')
    except:
        error("MidiNote ChATR: event range must be 'v1,v2', not '%s'." % ln[1])
    s1 = getoffset(trk, s1)
    s2 = getoffset(trk, s2)
    tinc = (s2-s1) / float(count)

    try:
        v1, v2 = ln[2].split(',')
    except:
        error("MidiNote ChATR: range must be 'v1,v2', not '%s'." % ln[2])
    v1 = stoi(v1)
    v2 = stoi(v2)

    if v1 < 0 or v1 > 127 or v2 < 0 or v2 > 127:
        error("MidiNote: ChATR values must be 0.. 127, not '%s'." % ln[2])

    vinc = (v2-v1) / float(count)

    channel = trk.channel
    track = gbl.mtrks[channel]

    ev = packBytes(0xd0 | channel-1)
    offset = s1
    bend = v1
    for i in range(count+1):
        v = int(bend)
        track.addToTrack(gbl.tickOffset + int(offset), packBytes(ev, v))
        offset += tinc
        bend += vinc

    if MMA.debug.debug:
        dPrint("MidiNote ChATR %s: inserted events %s to %s at offsets %s to %s." %
            (trk.name, v1, v2, s1, s2))

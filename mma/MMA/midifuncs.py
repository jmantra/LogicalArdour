# midifuncs.py

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

Low level entry points, mostly called directly from the parser.
"""

import struct
from . import gbl
import MMA.mdefine
from   MMA.common import *
import MMA.debug

# Storage for midi channel init commands (MidiInit). Commands are added
# from the functions setMidiInt and trackSetMidiInit in this module.
# They are dumped out in parse.py as channels are assigned to tracks.

channelInit = {}
for c in range(1, 17):
    channelInit[c] = []

masterMidiVolume = 0x3fff   # assume device is set to max volume

# non-track functions

def midiMarker(ln):
    """ Parse off midi marker. """

    if len(ln) == 2:
        offset = stof(ln[0])
        msg = ln[1]
    elif len(ln) == 1:
        offset = 0
        msg = ln[0]
    else:
        error("Usage: MidiMark [offset] Label")

    offset = int(gbl.tickOffset + (gbl.BperQ * offset))
    if offset < 0:
        error("MidiMark offset points before start of file")

    gbl.mtrks[0].addMarker(offset, msg)


def setMidiCue(ln):
    """ Insert MIDI cue (text) event into meta track."""

    if not ln:
        error("MidiCue requires text.")

    gbl.mtrks[0].addCuePoint(gbl.tickOffset, ' '.join(ln))


def rawMidi(ln):
    """ Send hex bytes as raw midi stream. """

    mb = []
    for a in ln:    # loop needed to verify, otherwise we'd use list comprehension
        a = stoi(a)
        if a < 0 or a > 0xff:
            error("All values must be in the range 0 to 0xff, not '%s'" % a)
        mb.append(a)
    mb = MMA.midiM.packBytes((mb))   # save value for debug
    gbl.mtrks[0].addToTrack(gbl.tickOffset, mb)

    if MMA.debug.debug:
        dPrint("MIDI: Inserted raw midi in metatrack: %s" %
              ' '.join([str(a) for a in struct.unpack("%sB" % len(mb), mb)]))



def setMidiFileType(ln):
    """ Set some MIDI file generation flags. """

    if not ln:
        error("USE: MidiFile [SMF=0/1] [RUNNING=0/1]")

    for l in ln:
        try:
            mode, val = l.upper().split('=')
        except:
            error("Each arg must contain an '=', not '%s'" % l)

        if mode == 'SMF':
            if val == '0':
                gbl.midiFileType = 0
            elif val == '1':
                gbl.midiFileType = 1
            else:
                error("Use: MIDIFile SMF=0/1")

        elif mode == 'RUNNING':
            if val == '0':
                gbl.runningStatus = 0
            elif val == '1':
                gbl.runningStatus = 1
            else:
                error("Use: MIDIFile RUNNING=0/1")

        else:
            error("Use: MIDIFile [SMF=0/1] [RUNNING=0/1]")

    if MMA.debug.debug:
        if gbl.runningStatus:
            a = 'ON'
        else:
            a = 'OFF'
        dPrint("MIDIFile: SMF=%s RUNNING=%s" % (gbl.midiFileType, a))


def setChPref(ln):
    """ Set MIDI Channel Preference. """

    if not ln:
        error("Use: ChannelPref TRACKNAME=CHANNEL [...]")

    for i in ln:
        if '=' not in i:
            error("Each item in ChannelPref must have an '='")

        n, c = i.split('=')

        c = stoi(c, "Expecting an integer for ChannelPref, not '%s'" % c)

        if c < 1 or c > 16:
            error("Channel for ChannelPref must be 1..16, not %s" % c)

        gbl.midiChPrefs[n.upper()] = c

    if MMA.debug.debug:
        dPrint("ChannelPref: %s" % 
              ' '.join(["%s=%s" % (n, c) for n, c in gbl.midiChPrefs.items()]))


def setMidiCopyright(ln):
    """ Add a copyright message to the file. This is inserted into
        the meta track at offset 0.
    """

    if not ln:
        error("MidiCopyright needs text message.")

    gbl.mtrks[0].addCopyright(0, ' '.join(ln))


def setMidiName(ln):
    """ Set global/meta track name. This will overwrite the song name set in main."""

    if not ln:
        error("Use: TrackName text")

    gbl.mtrks[0].addTrkName(0, ' '.join(ln))


def setMidiText(ln):
    """ Set midi text into meta track."""

    if not ln:
        error("Use: MidiText text")

    gbl.mtrks[0].addText(gbl.tickOffset, ' '.join(ln))


def setMidiCresc(ln):
    doMidiTrackCresc(ln, 1, "MidiCresc")


def setMidiDecresc(ln):
    doMidiTrackCresc(ln, -1, "MidiDeCresc")


def doMidiTrackCresc(ln, dir, func):
    """ Low level MIDI (de)cresc channel volume.

        This is mostly the same as the track function, but since
        we are dealing with a 14bit rather 7bit value it's maybe
        easier to have it separate.
    """

    global masterMidiVolume
    step = 10

    ln, opts = opt2pair(ln, toupper=True)
    for o, v in opts:
        if o == 'STEP':
            step = stoi(v)
            if step < 1:
                error("%s: Step rate must be >0." % func)

        else:
            error("%s: Unknow option '%s'." % (func, o))

    if len(ln) not in (2, 3):
        error("%s: usage -  [<start>] <end> <count>" % (func))

    if len(ln) == 2:
        # No start, insert the current master volume
        ln.insert(0, str(masterMidiVolume))

    v1 = MMA.volume.calcMidiVolume14(ln[0])
    if v1 < 0 or v1 > 0x3fff:
        error("%s: Volume must be 0..16383." % (v1))

    v2 = MMA.volume.calcMidiVolume14(ln[1])
    if v2 < 0 or v2 > 0x3fff:
        error("%s: Volume must be 0..16383." % (v1))

    count = stof(ln[2])
    if count <= 0:
        error("%s: count must be >0" % (func))

    if dir == -1 and v1 < v2:
        warning("%s: dest volume > start" % (func))
    elif dir == 1 and v1 > v2:
        warning("%s: dest volume < start" % (func))

    ldur = int(count * gbl.barLen)
    start = gbl.tickOffset
    end = gbl.tickOffset + ldur

    #if v1 > v2:
    #    v1, v2 = v2, v1
    #volspan = v2 - v1
    if step > ldur:
        step = ldur
    changer = ((v2 - v1 ) // (ldur // step))
    
    v = v1
    t = 0
    for d in range(start, end, step):
        if v < 0 or v > 0x3fff:
            break
        gbl.mtrks[0].addMasterVolume(d, v)
        v += changer
        t += 1

    masterMidiVolume = v2
    gbl.mtrks[0].addMasterVolume(end, v2)

    if MMA.debug.debug:
        dPrint("MIDI(de)Cresc: Added %s changes" % t)


def setMidiVolume(ln):
    """ Set midi master volume."""

    global masterMidiVolume

    if len(ln) != 1:
        error("MidiVolume: Needs exactly one argument.")

    v = MMA.volume.calcMidiVolume14(ln[0])

    if v < 0 or v > 0x3fff:
        error("MidiVolume: Volume setting must be 0...16383.")

    gbl.mtrks[0].addMasterVolume(gbl.tickOffset, v)
    masterMidiVolume = v

    if MMA.debug.debug:
        dPrint("MidiVolume: Master volume set to %s." % v)


def setChannelInit(ln):
    """ Set a command for all midi channels. This is stored and
        added to a track when a channel is assigned. If the channel
        is never assigned, the command never takes effect.
    """

    channels = []

    ln, opts = opt2pair(ln)

    for o, v in opts:
        if o.upper() == 'CHANNELS':
            for c in v.split(','):
                if '-' in c:
                    c1, c2 = c.split('-')
                    c1 = stoi(c1)
                    c2 = stoi(c2)
                    if c2 < c1:
                        c1, c2 = c2, c1
                    if c1 <= 0 or c2 > 16:
                        error("ChannelInit: Valid channels range 1..16, not %s-%s." % (c1, c2))
                    channels.extend(range(c1, c2+1))
                else:
                    c = stoi(c)
                    if c <= 0 or c > 16:
                        error("ChannelInit: Valid channels are 1..16, not %s." % c)
                    channels.append(c)
            channels = list(set(channels))
        else:
            error("ChannelInit: %s is not a valid option." % o)

    if not channels:
        channels = range(1, 17)

    if not len(ln):
        error("ChannelInit: A command is required.")

    ln[0] = ln[0].upper()
    if ln[0] not in MMA.parse.trackFuncs:
        error("ChannelInit: Track function %s does not exist." % ln[0])

    for c in channels:
        channelInit[c].append(ln)

    if MMA.debug.debug:
        dPrint("ChannelInit: '%s' queued to channels %s" % 
            (' '.join(ln), ','.join([str(c) for c in channels])))


def doChannelInit(channel, name):
    """ Add the ChannelInit stuff to the start of this track.
        Pull from the storage and process the string as if it were a line
        from a file. We are calling up functions in the parse module to do this.
        But, parse.py is not imported... can't since it causes a problem with
        trackFuncs table not existing. So, this might cause a future problem!!!
    """

    for l in MMA.midifuncs.channelInit[channel]:
        MMA.parse.trackFuncs[l[0]](name, l[1:])
    MMA.midifuncs.channelInit[channel] = []

################################################
## Track functions


def trackMidiVolume(name, ln):
    """ LowLevel MIDI command. Set Channel Volume. """

    if len(ln) != 1:
        error("%s MidiVolume: Needs exactly 1 arg." % name)

    v = MMA.volume.calcMidiVolume(ln[0])
    if v < 0 or v > 127:
        error("%s MidiVolume: Volumes need to be 0..127, not %s." % (name, v))

    gbl.tnames[name].midiPending.append(("CVOLUME", gbl.tickOffset, v))
    gbl.tnames[name].cVolume = v

    if MMA.debug.debug:
        MMA.debug.trackSet(name, 'MIDIVolume')


def trackMidiCresc(name, ln):
    """ MIDI cresc. """

    doMidiCresc(name, ln, 1, "MidiCresc")


def trackMidiDecresc(name, ln):
    """ MIDI cresc. """

    doMidiCresc(name, ln, -1, "MidiDecresc")


def doMidiCresc(name, ln, dir, func):
    """ Low level MIDI (de)cresc channel volume."""

    tptr = gbl.tnames[name]

    if len(ln) not in (2, 3):
        error("%s %s: usage -  [<start>] <end> <count>" % (name, func))

    if len(ln) == 2:
        # If passing only one param we're doing a change from the
        # current volume. Unfort, that setting might be buffered
        # in a channelinit list or in the pending queue. So, we
        # force a channel, force init stuff and check the pending
        # buffer (from the end).
        
        if not tptr.channel:
            tptr.setChannel()
        doChannelInit(tptr.channel, name)
        currentVol = tptr.cVolume
        for c, off, v in reversed(tptr.midiPending):
            if c == 'CVOLUME':
                currentVol = v
                break

        ln.insert(0, str(currentVol))

    v1 = MMA.volume.calcMidiVolume(ln[0])
    if v1 < 0 or v1 > 127:
        error("%s %s: Volume must be 0..127." % (name, v1))
    v2 = MMA.volume.calcMidiVolume(ln[1])
    if v2 < 0 or v2 > 127:
        error("%s %s: Volume must be 0..127." % (name, v1))

    count = stof(ln[2])
    if count <= 0:
        error("%s %s: count must be >0" % (name, func))

    if dir == -1 and v1 < v2:
        warning("%s %s: dest volume > start" % (name, func))
    elif dir == 1 and v1 > v2:
        warning("%s %s: dest volume < start" % (name, func))

    t = abs(v2-v1)
    step = (count * gbl.barLen) // t  # step rate
    p = gbl.tickOffset

    if v2 < v1:
        dir = -1
    else:
        dir = 1

    for v in range(v1, v2+dir, dir):
        gbl.tnames[name].midiPending.append(("CVOLUME", int(p), v))
        p += step

    if MMA.debug.debug:
        dPrint("%s MidiVolume: Added %s changes" % (name, t))

def trackGlis(name, ln):
    """ Enable/disable portamento. """

    if len(ln) != 1:
        error("%s MidiGlis: NN, off=0, 1..127==on" % name)

    v = stoi(ln[0], "Expecting integer for Portamento")

    if v < 0 or v > 127:
        error("MidiGlis %s: Value for Glis/Portamento must be 0..127." % name)

    gbl.tnames[name].midiPending.append(("GLIS", gbl.tickOffset, v))

    if MMA.debug.debug:
        dPrint("Set %s MIDIGlis to %s" % (name, v))


def trackWheel(name, ln):
    """ Set a pitch bend (wheel) set for a given track. """

    tdata = gbl.tnames[name]

    startOffset = None
    endOffset = 0
    setOnly = None
    duration = None
    startValue = None
    endValue = None
    step = 10
    reset = True
    cycle = False
    rate = None

    ln, opts = opt2pair(ln, toupper=True)

    if ln:
        if len(ln) == 1 and ln[0] == 'RESET':
            opts.append(('SET', 'CENTER'))
        else:
            error("%s MidiWheel: Unrecognized command(s) '%s'." % (name, ' '.join(ln)))

    for o, v in opts:
        if o == 'OFFSET':
            startOffset = stotick(v, 'B', "MidiWheel Offset: '%s' is not recognized." % v) \
                + gbl.tickOffset
            if startOffset < 0:
                error("%s MidiWheel Offset: current pointer is '%s ticks' so start "
                      "'%s ticks' is before song start." % (name, gbl.tickOffset, startOffset))

        # No idea why 'Count' is valid?
        elif o == 'DURATION' or o == 'COUNT':
            duration = stotick(v, 'B', "MidiWheel Duration: '%s' is not recognized." % v)
            if duration <= 0:
                error("%s MidiWheel Duration: Must be > 0, not '%s Ticks'." %
                      (name, duration))

        elif o == 'SET':
            if v == 'CENTER':
                setOnly = 0x2000
            else:
                setOnly = stoi(v)

        elif o == 'START':
            if v == 'CENTER':
                startValue = 0x2000
            else:
                startValue = stoi(v)

        elif o == 'END':
            if v == 'CENTER':
                endValue = 0x2000
            else:
                endValue = stoi(v)

        elif o == 'STEP':
            step = stoi(v)
            if step < 1:
                error("%s MidiWheel Step: must be > 0." % name)

        elif o == 'RESET':
            if v in ('NO', '0', 'OFF'):
                reset = 0
            elif v in ('YES', '1', 'ON'):
                reset = 1
            else:
                error("%s MidiWheel Reset: Use ON or OFF, not '%s'." % (name, v))

        elif o == 'RATE':
            rate = MMA.notelen.getNoteLen(v)

        elif o == 'CYCLE':
            if v in ('NO', '0', 'OFF'):
                cycle = False
            elif v in ('YES', '1', 'ON'):
                cycle = True
            else:
                error("%s MidiWheel Cycle: Use ON or OFF, not '%s'." % (name, v))
        else:
            error("%s MidiWheel: Unrecognized command '%s'." % (name, o))

    if setOnly is not None:
        if len(opts) > 2 or len(opts) > 1 and startOffset is None:
            warning("MidiWheel %s Set: some options may be ignored." % name)
        if startOffset is None:
            startOffset = gbl.tickOffset
        tdata.midiPending.append(("WHEEL", startOffset, setOnly))

        if MMA.debug.debug:
            dPrint("MidiWheel %s: detuned to %s at %s ticks." %
                (name, setOnly, startOffset))
        return

    if startOffset is None:
        startOffset = gbl.tickOffset

    if duration is None:
        error("%s MidiWheel: Duration must be set." % name)

    endOffset = startOffset + duration

    if startValue is None or endValue is None:
        error("%s MidiWheel: No start/end value set." % name)

    if startValue < 0 or startValue > 16383:
        error("%s MidiWheel: Start must be 0 ... 16383, not '%s'." % (name, startValue))

    if endValue < 0 or endValue > 16383:
        error("%s MidiWheel: End must be 0 ... 16383, not '%s'." % (name, endValue))

    if rate is None:
        repeat = 1
        ldur = duration
    else:
        ldur = rate              # duration of each loop
        repeat = duration // ldur  # times to loop

    if startValue < endValue:
        pitchspan = endValue - startValue
    else:
        pitchspan = startValue - endValue

    if step > ldur:
        step = ldur
    changer = pitchspan // (ldur/step)

    if startValue > endValue:
        changer *= -1

    value = startValue
    off = startOffset

    for r in range(repeat):
        for d in range(0, ldur, step):
            if value < 0:
                value = 0
            if value > 0x3fff:
                value = 0x3fff

            tdata.midiPending.append(("WHEEL", int(off+d), int(value)))
            value += changer
        off += ldur
        if cycle:
            changer *= -1

        if not cycle:
            value = startValue

    if reset:
        tdata.midiPending.append(("WHEEL", off+5, 0x2000))  # reset at end

    if MMA.debug.debug:
        if not reset:
            rset = "No RESET." 
        else:
            rset = ''
        dPrint("MidiWheel %s: detuned %s to %s from %s to %s. %s" % 
            (name, startValue, endValue, startOffset, endOffset, rset))


# Lookup table constants for MIDI PAN values.
panNames = {'LEFT': 0,       'LEFT100': 0,   'LEFT90': 6,
            'LEFT80': 13,    'LEFT70': 19,   'LEFT60': 25,
            'LEFT50': 31,    'LEFT40': 39,   'LEFT30': 44,
            'LEFT20': 50,    'LEFT10': 57,   'CENTER': 64,
            'RIGHT10': 70,   'RIGHT20': 77,  'RIGHT30': 83,
            'RIGHT40': 88,   'RIGHT50': 96,  'RIGHT60': 102,
            'RIGHT70': 108,  'RIGHT80': 114, 'RIGHT90': 121,
            'RIGHT100': 127, 'RIGHT': 127 }

def trackPan(name, ln):
    """ Set the Midi Pan value for a track."""

    def getv(v):
        try:
            return panNames[v.upper()]
        except:
            return stoi(v, "Expecting integer value 0..127 or mnemonic (Left*, Center, Right*).")


    tdata = gbl.tnames[name]

    if len(ln) not in (1, 3):
        error("MidiPan %s: needs 1 arg [Value] OR 3 [Initvalue DestValue Beats/Measures]." % name)


    if len(ln) == 3:
        beats = stotick(ln[2], 'B', "MidiPan Duration: '%s' is not recognized."
                        % ln[2]) // gbl.BperQ
        if beats < 1:
            error("MidiPan %s: Beat/Measure value must be positive count, "
                  "not '%s'." % (name,beats))

        initPan = getv(ln[0])
        newPan = getv(ln[1])
    else:
        beats = 0
        initPan = 0
        newPan = getv(ln[0])

    ticks = beats * gbl.BperQ   # convert beats to midi ticks

    if newPan < 0 or newPan > 127:
        error("MidiPAN: final value must be 0..127")

    if newPan < initPan:
        span = initPan-newPan
        changer = -1
    else:
        span = newPan-initPan
        changer = 1

    if span > 0:
        step = ticks/span
    else:
        beats = 0

    if beats:
        v = initPan
        off = gbl.tickOffset
        for a in range(span+1):
            tdata.midiPending.append(("PAN", int(off), v))
            off += step
            v += changer

    else:
        tdata.midiPending.append(("PAN", gbl.tickOffset, newPan))

    if MMA.debug.debug:
        if beats:
            dPrint("Set %s MIDIPan from %s to %s over %s beats." % 
                (name, initPan, newPan, beats))
        else:
            dPrint("Set %s MIDIPan to %s" % (name, newPan))


def trackMidiText(name, ln):
    """ Insert midi text event. """

    if not ln:
        error("Use: %s Text" % name)

    ln = ' '.join(ln)
    gbl.tnames[name].midiPending.append(("MIDITEXT", gbl.tickOffset, ln))

    if MMA.debug.debug:
        dPrint("Set %s MIDIText '%s'." % (name, ln))


def trackMidiCue(name, ln):
    """ Insert MIDI cue (text) event."""

    if not ln:
        error("MidiCue %s: Needs arg(s)." % name)

    ln = ' '.join(ln)
    gbl.tnames[name].midiPending.append(("MIDICUE", gbl.tickOffset, ln))

    if MMA.debug.debug:
        dPrint("Set %s MIDICue '%s'." % (name, ln))


def trackMidiExt(ln):
    """ Helper for trackMidiSeq() and trackMidiVoice()."""

    ids = 1
    while 1:
        sp = ln.find("{")

        if sp < 0:
            break

        ln, s = pextract(ln, "{", "}", 1)
        if not s:
            error("Did not find matching '}' for '{'")

        pn = "_%s" % ids
        ids += 1

        MMA.mdefine.mdef.create(pn, s[0])
        ln = ln[:sp] + ' ' + pn + ' ' + ln[sp:]

    return ln.split()


def trackMidiSeq(name, ln):
    """ Set reoccurring MIDI command for track. """

    if not ln:
        error("Use %s MidiSeq Controller Data" % name)

    if ln[0][0] != '{':      # add {} wrapper if missing
        ln.insert(0, '{')
        ln.extend('}')

    if len(ln) == 1 and ln[0] == '-':
        gbl.tnames[name].setMidiSeq('-')
    else:
        gbl.tnames[name].setMidiSeq(trackMidiExt(' '.join(ln)))


def trackMidiVoice(name, ln):
    """ Set single shot MIDI command for track. """

    if not ln:
        error("Use %s MidiVoice Controller Data" % name)

    if ln[0][0] != '{':      # add {} wrapper if missing
        ln.insert(0, '{')
        ln.extend('}')

    if len(ln) == 1 and ln[0] == '-':
        gbl.tnames[name].setMidiVoice('-')
    else:
        gbl.tnames[name].setMidiVoice(trackMidiExt(' '.join(ln)))


def trackMidiClear(name, ln):
    """ Set MIDI command to send at end of groove. """

    if not ln:
        error("Use %s MIDIClear Controller Data" % name)

    if len(ln) == 1 and ln[0] == '-':
        gbl.tnames[name].setMidiClear('-')
    else:
        ln = ' '.join(ln)
        if '{' in ln or '}' in ln:
            error("{}s are not permitted in %s MIDIClear command" % name)
        gbl.tnames[name].setMidiClear(trackMidiExt('{' + ln + '}'))


def trackMidiName(name, ln):
    """ Set channel track name."""

    if len(ln) != 1:
        error("MidiTName %s: Use exactly one arg." % name)

    gbl.tnames[name].midiPending.append(('TNAME', 0, ln[0]))

    if MMA.debug.debug:
        dPrint("Set %s MIDI Track Name to %s" % (name, ln[0]))

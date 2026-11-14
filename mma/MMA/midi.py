# midi.py

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

from   MMA.midiM import intToWord, intTo3Byte, intToLong, intToVarNumber, intTo14, packBytes
import MMA.midiC
import MMA.debug
import MMA.sync
from . import gbl
from   MMA.common import *
from   MMA.miditables import NONETONE

splitChannels = []
tempoChanges = []    # A list of tempo changes, use to check from tempo.py

# some constants we use to catorgize event types
MIDI_NOTE = 1
MIDI_PRG = 2


def setSplitChannels(ln):
    """ Parser routine, sets up list of track to split. Overwrites existing. """

    global splitChannels
    splitChannels = []

    for a in ln:
        try:   # is this a legit channel number
            ch = int(a, 0)
        except ValueError:  # assume track name then
            ch = None

        if ch is None:
            if not a in gbl.tnames:
                a = a.upper()
                MMA.alloc.trackAlloc(a, 0)    # ensure that track is allocated
            if not a in gbl.tnames:
                error("MidiSplit: Track '%s' is not valid." % a)
            if not gbl.tnames[a].channel:
                gbl.tnames[a].setChannel()
            ch = gbl.tnames[a].channel

        if ch < 1 or ch > 16:
            error("MidiSplit: Expecting value 1 to 16, not %s" % a)
        if ch not in splitChannels:
            splitChannels.append(ch)

    if MMA.debug.debug:
        msg = ["SplitChannels: "]
        for a in splitChannels:
            msg.append(str(a))
        dPrint(' '.join(msg))


####################

def writeTracks(out):
    """ Write the accumulated MIDI tracks to file. """

    keys = list(gbl.mtrks.keys())   # a list of channels. Should rename?
    keys.sort()

    """ For type 0 MIDI files all data is contained in 1 track.
        We take all our tracks and copy them to track 0, then
        set up keys[] so that only track 0 remains.
    """

    if gbl.midiFileType == 0:
        trk0 = gbl.mtrks[0].miditrk
        for n in keys[1:]:
            trk = gbl.mtrks[n].miditrk
            for k, v in trk.items():
                if k in trk0:
                    trk0[k].extend(v)
                else:
                    trk0[k] = v
        keys = [0]

    # Write header

    tcount = len(keys)

    out.write(mkHeader(tcount, gbl.BperQ, gbl.midiFileType))

    if gbl.barRange:   # compensate for -B/-b options
        stripRange()

    # Write data chunks for each track

    for n in keys:
        # Call special function to split a track (set by MidiSplit)
        if n in splitChannels and gbl.midiFileType:
            tcount += writeSplitTrack(n, out)   
        else:
            # use normal function
            gbl.mtrks[n].writeMidiTrack(out)

    """ We may have changed the track count! So, we need to
        fix the file header. This is offset 10/11 which contains
        the number of tracks. The counter tcount has been
        tracking this, so just seek, replace and seek back.
    """

    if tcount != len(keys):
        out.seek(0)
        out.write(mkHeader(tcount, gbl.BperQ, gbl.midiFileType))
        out.seek(0, 2)  # return to eof


def writeSplitTrack(channel, out):
    """ Split a track. In drum tracks this puts different instruments
        into individual tracks (useful!); for instrument tracks it puts
       each pitch into a track (probably not useful).
    """

    tr = gbl.mtrks[channel].miditrk   # track to split

    # A dict to store the split midi tracks. We'll end up with
    # a track for each pitch which appears in the track and
    # a track (labeled -1) to store every other-than-note-on/off data.

    notes = {}

    onEvent = 0x90 + (channel-1)
    offEvent = 0x80 + (channel-1)
    for offset in tr.keys():
        for x in range(len(tr[offset])-1, -1, -1):
            ev = tr[offset][x]
            if len(ev) == 3 and (ev[0] in (onEvent, offEvent)):
                n = ev[1]
            else:
                n = -1      # special value for non-note on events

            if not n in notes:   # create a new mtrk if needed
                notes[n] = Mtrk(10)

            if offset in notes[n].miditrk:  # copy event to new track
                notes[n].miditrk[offset].append(ev)
            else:
                notes[n].miditrk[offset] = [ev]

    if MMA.debug.debug:
        dPrint(" Data has been split into %s tracks." % len(notes))

    # Insert a channel name in all the new tracks.

    for a in notes.keys():
        if a == -1:
            continue
        if channel == 10:
            m = "%s" % MMA.midiC.valueToDrum(a)
        else:
            m = "%s-%s" % (gbl.mtrks[channel].trackname, a)

        notes[a].addTrkName(0, m)

    for a in sorted(notes.keys()):
        notes[a].writeMidiTrack(out)

    """ The split tracks have been written. Return the number of additional tracks
        so that the caller can properly update the midi file header. Note that
        len(notes)-1 IS CORRECT ... we've already figured on writing 1 track.
    """

    return len(notes)-1


def mkHeader(count, tempo, Mtype):

    return packBytes("MThd", intToLong(6), intToWord(Mtype), intToWord(count), intToWord(tempo))


# Midi track class. All the midi creation is done here.
#  We create a class instance for each track. mtrks{}.

class Mtrk:

    def __init__(self, channel):
        self.miditrk = {}
        self.channel = channel-1
        self.trackname = ''
        self.lastOffEvent = [None] * 129  # cell for each note, saved delta
        self.lastPrg = 0

    def delDup(self, offset, cmd):
        """ Delete a duplicate event. Used by timesig, etc.    """

        tr = self.miditrk
        lg = len(cmd)
        if offset in tr:
            tmp = []
            for ev in tr[offset]:
                if ev[0:lg] != cmd:  # not target, copy it
                    tmp.append(ev)
            tr[offset] = tmp           # new set of events (may be empty)

    def addTimeSig(self, offset,  nn, dd, cc, bb):
        """ Create a midi time signature.

            delta - midi delta offset
            nn = sig numerator, beats per measure
            dd - sig denominator, 2=quarter note, 3=eighth,
            cc - midi clocks/tick
            bb - # of 32nd notes in quarter (normally 8)

            This is only called by timeSig.create(). Don't
            call this directly since the timeSig.create() checks for
            duplicate settings.
        """

        cmd = packBytes(0xff, 0x58)
        # we might have several different timesigs on the same offset,
        # so take time to delete any. 
        self.delDup(offset, cmd)
        self.addToTrack(offset, packBytes(cmd, (0x04, nn, dd, cc, bb)))

    def addKeySig(self, offset, n, mi):
        """ Set the midi key signature. """

        cmd = packBytes(0xff, 0x59)
        self.delDup(offset, cmd)
        self.addToTrack(offset, packBytes(cmd, (0x02, n, mi)))

    def addMarker(self, offset, msg):
        """ Create a midi MARKER event."""

        self.addToTrack(offset, packBytes((0xff, 0x06), intToVarNumber(len(msg)), msg))

    def addCopyright(self, offset, msg):
        """ Insert copyright. """

        # should never happen since the caller sets offset=0
        if offset != 0:
            error("Copyright message must be at offset 0, not %s." % offset)

        # We need to bypass addToTrack to force copyright to the start of the track.

        # Create the copyright event
        ev = packBytes((0xff, 0x02), intToVarNumber(len(msg)), msg)

        tr = self.miditrk   # this is the meta track

        # We keep a pointer (ipoint) which points to the position of
        # the last copyright string. If there isn't one, we create
        # it in the expect; else it's just incremented

        try:
            self.ipoint += 1
        except AttributeError:
            self.ipoint = 0

        if offset in tr:
            tr[offset].insert(self.ipoint, ev)
        else:
            tr[offset] = [ev]

    def addText(self, offset, msg):
        """ Create a midi TextEvent."""

        self.addToTrack(offset, packBytes((0xff, 0x01), intToVarNumber(len(msg)), msg))

    def addLyric(self, offset, msg):
        """ Create a midi lyric event. """

        self.addToTrack(offset, packBytes((0xff, 0x05), intToVarNumber(len(msg)), msg))

    def addCuePoint(self, offset, msg):
        """ Create a MIDI cue pointr event. """

        self.addToTrack(offset, packBytes((0xff, 0x07), intToVarNumber(len(msg)), msg ))

    def addTrkName(self, offset, msg):
        """ Creates a midi track name event. """

        offset = 0  # ignore user offset, always put this at 0

        self.trackname = msg

        cmd = packBytes((0xff, 0x03))
        self.delDup(offset, cmd)
        self.addToTrack(offset, packBytes(cmd, intToVarNumber(len(msg)), msg))

    def addProgChange(self, offset, program, oldprg):
        """ Create a midi program change (handles extended voicing).

            program - The MIDI program (voice) value
            oldprg  - existing MIDI program
        """

        # We truck around a special pseudo voice 'NONE' or 127.127.127 which
        # is a signal that we don't want mma to set the voicing. Might be
        # useful when know the track that mma is using and we have preset
        # an external synth.

        if program == NONETONE:
            return

        v1, lsb1, msb1 = MMA.midiC.voice2tup(oldprg)
        v2, lsb2, msb2 = MMA.midiC.voice2tup(program)

        if msb1 != msb2:   # only if CTRL32 has changed
            self.addToTrack(offset, packBytes((0xb0 | self.channel, 0x20, msb2)))

        if lsb1 != lsb2:   # only if CTRL0 has changed
            self.addToTrack(offset, packBytes((0xb0 | self.channel, 0x00, lsb2)))

        # Always do voice change. Maybe not necessary, but let's be safe.

        self.addToTrack(offset, packBytes((0xc0 | self.channel, v2)), MIDI_PRG)

    def addGlis(self, offset, v):
        """ Set the portamento. LowLevel MIDI.

            This does 2 things:
                1. turns portamento on/off,
                2. sets the LSN rate.
        """

        if v == 0:
            self.addToTrack(offset, packBytes((0xb0 | self.channel, 0x41, 0x00)))

        else:
            self.addToTrack(offset, packBytes((0xb0 | self.channel, 0x41, 0x7f)))
            self.addToTrack(offset, packBytes((0xb0 | self.channel, 0x05, v)))

    def addWheel(self, offset, v):
        """ Set lsb/msb for the modulation wheel. """

        self.addToTrack(offset, packBytes((0xe0 | self.channel), intTo14(v)))

    def addPan(self, offset, v):
        """ Set the lsb of the pan setting."""

        self.addToTrack(offset, packBytes((0xb0 | self.channel, 0x0a, v)))

    def addCtl(self, offset, l):
        """ Add arbitary control sequence to track."""

        self.addToTrack(offset, packBytes(0xb0 | self.channel, l))

    def addNoteOff(self, offset):
        """ Insert a "All Note Off" into the midi stream.

            Called from the cutTrack() function.
        """

        self.addToTrack(offset, packBytes((0xb0 | self.channel, 0x7b, 0)), MIDI_NOTE )

    def addMasterVolume(self, offset, v):
        """ System Exclusive master volume message. Meta track. """

        # We send to packBytes as a long list, no tuples. Just a bit
        # easier to maintain a long list like this.
        self.addToTrack(offset, packBytes(
                0xf0,       # Start sysex
                0x07,       # message size (needed for SMF)
                0x7f,       # realtime
                0x7f,       # disregard channel
                0x04,       # device control
                0x01,       # master volume
                intTo14(v), # params (14 bit)
                0xf7 ))     # EOX

    def addChannelVol(self, offset, v):
        """ Set the midi channel volume."""

        tr = self.miditrk
        cvol = packBytes(0xb0 | self.channel, 0x07)  # 2 byte channel vol

        # Before adding a new channel volume event we check to see if there
        # are any future channel volume events and delete them.
        
        for off in tr:
            if off >= offset:
                tr[off] = [e for e in tr[off] if e[0:2] != cvol]
        
        self.addToTrack(offset, packBytes(cvol, v))

    def addTempo(self, offset, bpm):
        """ Create a midi tempo meta event.

             bpm - beats per minute

             Return - packed midi string
        """

        cmd = packBytes((0xff, 0x51, 0x03))
        self.delDup(offset, cmd)

        self.addToTrack(offset, packBytes(cmd, intTo3Byte(60000000 // bpm)))
        tempoChanges.append([offset, bpm])
        
    def writeMidiTrack(self, out):
        """ Create/write the MIDI track.

            We convert timing offsets to midi-deltas.
        """

        tr = self.miditrk

        """ If the -1 command line option is set we need to add a terminate
            to the end of each track. This is done to make looping
            software like seq24 happy. We do this by truncating all
            data in the file past the current tick pointer and inserting
            an all-notes-off at that position.
        """

        if MMA.sync.endsync and self.channel >= 0:
            eof = gbl.tickOffset
            for offset in list(tr.keys()):
                if offset > eof:
                    del tr[offset]
            self.addToTrack(eof, packBytes((0xb0 | self.channel, 0x7b, 0)))

        """ To every MIDI track we generate we add (if the -0 flag
            was set) an on/off beep at offset 0. This makes for
            easier sync in multi-tracks.
        """

        if MMA.sync.synctick and self.channel >= 0:
            t, v = MMA.sync.syncTone
            self.addToTrack(0, packBytes((0x90 | self.channel, t, v)))
            self.addToTrack(1, packBytes((0x90 | self.channel, t, 0)))

        if MMA.debug.debug:
            ttl = 0
            lg = 1
            for t in tr:
                a = len(tr[t])
                if a > lg:
                    lg = a
                ttl += a
            if self.channel == -1:
                nm = "META"
            else:
                nm = self.trackname
            dPrint( "<%s> Unique ts: %s; Ttl events %s; Average ev/ts %.2f" %
                (nm, len(tr), ttl, float(ttl)/len(tr)))

        last = 0

        # Convert all events to MIDI deltas and store in
        # the track array/list

        tdata = []        # empty track container
        lastSts = None    # Running status tracker

        for a in sorted(tr.keys()):
            delta = a-last

            if not tr[a]:
                continue  # this skips the delta offset update!

            for d in tr[a]:
                """ Running status check. For each packet compare
                    the first byte with the first byte of the previous
                    packet. If it is can be converted to running status
                    we strip out byte 0. Note that valid running status
                    byte are 0x80..0xef. 0xfx are system messages
                    and are not suitable for running status.
                """

                if len(d) > 1:
                    if d[0] == lastSts:
                        d = d[1:]
                    else:
                        lastSts = d[0]
                        if lastSts < 0x80 or lastSts > 0xef or not gbl.runningStatus:
                            lastSts = None

                tdata.extend([intToVarNumber(delta), d])
                delta = 0
            last = a

        # Add an EOF to the track (included in total track size)

        tdata.append(intToVarNumber(0))
        tdata.append(packBytes((0xff, 0x2f, 0x00)))

        tdata = bytearray(b'').join(tdata)
        totsize = len(tdata)

        out.write(b"MTrk")
        out.write(intToLong(totsize))
        out.write(tdata)

    def getLastOffset(self):
        """ Go though the data and find the last offset. 
            Used in re-allocating tracks. A completely
            empty track will return 0, but that's okay
            and shouldn't happen in any event.
        """

        offset = 0  
        for a in self.miditrk:
            if a > offset:
                offset = a
        return offset
    
    def addPairToTrack(self, boffset, startRnd, endRnd, duration, note, v, unify ):
        """ Add a note on/off pair to a track.

            boffset      - offset into current bar
            startRnd, endRnd  - rand val start adjustment
            duration  - note len
            note      - midi value of note
            v      - midi velocity
            unify      - if set attempt to unify/compress on/offs

            This function tries its best to handle overlapping events.
            Easy to show effect with a table of note ON/OFF pairs. Both
            events are for the same note pitch.

            Offsets     |     200  |      300  |  320  |  420
            ---------|--------|--------|-------|--------
            Pair1     |     on      |       |  off  |
            Pair2     |      |      on   |       |  off

            The logic here will delete the OFF event at 320 and
            insert a new OFF at 300. Result is that when playing
            Pair1 will turn off at 300 followed by the same note
            in Pair2 beginning sounded right after. Why the on/off?
            Remember: Velocities may be different!

            However, if the unify flag is set we should end up with:

            Offsets     |     200  |      300  |  320  |  420
            ---------|--------|--------|-------|--------
            Pair1     |     on      |       |       |
            Pair2     |      |       |       |  off

        """

        # Start/end offsets

        onOffset = getOffset(boffset, startRnd, endRnd)

        # If the ON or OFF offset is <0 we change it to 0 for a couple of
        # reasons:
        #   1. It'll be converted anyway in 'addToTrack', but that doesn't
        #      get back to us here.
        #   2. If we don't that wrong offset will be reported in lastOffEvent.

        if onOffset < 0:
            onOffset = 0
        offOffset = onOffset + duration
        if offOffset < 0:
            offOffset = 0

        # ON/OFF events

        onEvent = packBytes(0x90 | self.channel, note, v)
        offEvent = packBytes(onEvent[:-1], 0)

        noOnFlag = False

        f = self.lastOffEvent[note] 

        if f is not None and f >= onOffset and f <= offOffset:
            # evlist is a delta-offset list. It should have a note off event
            # for the this note. Just in case, we do check; but it's probably
            # not necessary. The off event is deleted and the unify stuff is done
            if offEvent in self.miditrk[f]:
                self.miditrk[f].remove(offEvent)
                if not unify:
                    self.addToTrack(onOffset, offEvent, MIDI_NOTE)
                else:
                    noOnFlag = True

        if not noOnFlag:
            self.addToTrack(onOffset, onEvent, MIDI_NOTE)
        self.addToTrack(offOffset, offEvent, MIDI_NOTE)

        # Save the NOTE OFF time for the next loop.

        self.lastOffEvent[note] = offOffset

    def addNoteOnToTrack(self, boffset, note, v, startRnd=None, endRnd=None):
        """ Add a single note on or note off when v=0 to a track.
            boffset      - offset into current bar
            duration  - note len
            note      - midi value of note
            v      - midi velocity, set to 0 for note off
            startRnd/endRnd  - rand val start adjustment

            Added by louisjb for plectrum.
        """

        # Start offsets

        onOffset = getOffset(boffset, startRnd, endRnd)
        onEvent = packBytes((0x90 | self.channel, note, v))

        # this avoids situations where the new note is placed
        # before a NoteOff event. This could be due to a bad
        # sequence specification or, more likely, due to
        # RTIME setting the start point of this note before
        # the current beat in a tight sequence.
        f = self.lastOffEvent[note]
        if f is not None and f >= onOffset:
            offEvent = packBytes(onEvent[:-1], 0)
            if offEvent in self.miditrk[f]:
                self.miditrk[f].remove(offEvent)

        # ON/OFF events (off is on with v = 0)


        self.addToTrack(onOffset, onEvent, MIDI_NOTE)
        if v==0:
            self.lastOffEvent[note] = onOffset
        return onOffset

    def addToTrack(self, offset, event, evType=None):
        """ Add an event to a track.

            MIDI data is saved as created in track structures.
            Each track has a miditrk dictionary entry which used
            the time offsets and keys and has the various events
            as data. Each event is a packed string of bytes and
            the events are stored as a list in the order they are
            created. Our storage looks like:

                 miditrk[OFFSET_VALUE] = [event1, event2, ...]

            evType is an optional arg. Two values are used:
                 MIDI_PR - a program (voice) change. Save the timestamp.
                 MIDI_NOTE - note on/off ... check to see it doesn't happen
                             before the last program change.

        """

        if evType == MIDI_NOTE and offset < self.lastPrg:
            offset = self.lastPrg
        elif evType == MIDI_PRG:
            self.lastPrg = offset

        # Important. It's possible that a negative delay could generate
        # a negative offset.

        if offset < 0:
            offset = 0

        tr = self.miditrk

        # note: timing test verifies if/then is slightly faster try/except here
        # that's because the else case is used most.
        if offset in tr:
            tr[offset].append(event)
        else:
            tr[offset] = [event]

def stripRange():
    """ Strip out range limited data. Only of -B/b option. """

    bp = gbl.barPtrs   # list generated at compile time

    if gbl.barRange[-1] == 'ABS':
        gbl.barRange.pop()  # delete abs marker (set by -B)
        for a in bp:        # convert comment numbers to abs numbers
            bp[a][0] = str(a)
    validRange = []

    for a in gbl.barRange:   # list of bars we want to produce
        for b in bp:
            if a == bp[b][0]:
                validRange.append([bp[b][1], bp[b][2]])

    if not validRange:
        dPrint("   Range directive -b/B would result in empty file.\n"
              "   Entire file is being created. Check the range.")
        return

    # Collaspe/merge the valid range pointers
    validRange.sort()   # barptrs was dict, so this list is not in order
    tmp = []
    a, b = validRange[0]
    for i in range(1, len(validRange)):
        if b+1 == validRange[i][0]:
            b = validRange[i][1]
        else:
            tmp.append([a, b])
            a, b = validRange[i]
    tmp.append([a, b])
    validRange = tmp  # list of event times to keep

    """ Create list of event times to discard. Each item in the list:
        is [ start-time, end-time]
     """

    disList = []
    lowestEv = bp[1][1]
    for a in validRange:
        disList.append([lowestEv, a[0]-1])
        lowestEv = a[1]

    """ Determine the last event time in the buffer. This is not nesc. the
        same as the last barptr ... tempos and midinote can write past the
        last bar. We need to test each track and find the highest event time.
    """

    lastev = -1
    for a in gbl.mtrks:
        z = sorted(gbl.mtrks[a].miditrk)
        if z[-1] > lastev:
            lastev = z[-1]

    disList.append([validRange[-1][1]+1, lastev])

    """ 1st pass. For each track take all the cut parts and adjust their
        offsets to the end offset of the previous keep section. Strip out
        all note on events, lyric and text events in the effected bits.
    """

    for start, end in disList:
        for n in gbl.mtrks:
            tr = gbl.mtrks[n].miditrk
            newEvents = []
            for ev in sorted(tr.keys()):   # sort is important!
                if ev >= start and ev <= end:
                    for e in tr[ev]:
                        e0 = e[0] & 0xf0
                        # skip note on events
                        if e0 == 0x90 and e[2]:
                            continue
                        # skip lyric and text events
                        if e[0] == 0xff:
                            if e[1] == 0x05 or e[1] == 0x01:
                                continue
                        # skip if event is note off and it already is present
                        # Note: mma never generates a 0x80 (note-off) event, but
                        # the test is included here since midi-inc may have them.
                        if (e0 == 0x90 and e[2] == 0) or (e0 == 0x80):
                            for x in newEvents:
                                if x == e:
                                    e = None
                                    break
                        if e:
                            newEvents.append(e)
                    del (tr[ev])

            """ We now have a new list of events for the 'start' offset (it might
                just be an empty list) AND we have deleted the events for 'start'
                to 'end'. Just a matter of inserted a new event list.
            """

            if newEvents:
                tr[start] = newEvents

    """ 2nd pass. Adjust offsets of stuff to keep. """

    offset = 0
    for vals in range(len(validRange)):   # each valid range
        start = validRange[vals][0]
        end = validRange[vals][1]+1
        offset += (start - disList[vals][0])
        for a in gbl.mtrks:               # each track
            tr = gbl.mtrks[a].miditrk
            for ev in sorted(tr.keys()):  # each event list
                if ev >= start and ev <= end:
                    newoffset = ev-offset
                    if ev != newoffset:  # don't append/copy creating duplicates
                        if newoffset in tr:
                            tr[newoffset].extend(tr[ev])
                        else:
                            tr[newoffset] = tr[ev]
                        del tr[ev]

    """ After all this compressing the end of file marker is past the
        end of the real data. This could bugger up the -1 option, so fix
        it. Go though all the tracks again and find the end.
    """

    lastev = -1
    for a in gbl.mtrks:
        z = sorted(gbl.mtrks[a].miditrk)
        if z and z[-1] > lastev:
            lastev = z[-1]
    gbl.tickOffset = lastev

    dPrint("  File has been truncated for -b/-B option. Bar count/time incorrect.")

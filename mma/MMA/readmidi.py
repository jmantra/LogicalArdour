# readmidi.py

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

Bob's quick and dirty functions to read a midi file. 
  The entire file is read into memory and then parsed
  into different events.
  
This should work with any midi file. Python 2/3 compatible.
  
Note that many midi events are NOT read. The code here just
  skips over them since they are not useful to MMA.
        
Any and all errors raise a 'RuntimeError'. If you need to, catch
  these from your calling program.
  
  Example:
     Create the class
        mf = MidiData()
     Set some class variables
        mf.velocityAdjust = 200
     Read the file
        try:
          mf.readfile("fever.mid")
        except RuntimeError as e:
          print("ERROR: %s" % e)
        sys.exit(0)
  
The main things to look at after reading the file are:

    events[]      - dict of lists, keys are channel numbers.
                    each item is a list of lists in the format:
                       [offset, event-type, [data] ]
    textEvents[]  - list, each item is [offset, text]
    lyricEvents[] - list, each item is [offset, text]

Other useful info includes: beatDivision, numTracks
  
You might look at beatDivision and adjust the offsets using
  code like this:
     if beatDivision != gbl.BperQ:
        mf.adjustBeats( gbl.BperQ / float(beatDivision))

"""

import sys
from . import gbl

class MidiData:
    def __init__(self):
        # set these before reading the file
        self.ignorePC = True     # skip (don't save) program changes
        self.octaveAdjust = 0    # octave adjustment values (should be -12,24,etc)
        self.velocityAdjust = 100  # Percentage to apply to velocities

        # storage
        self.events = {}
        for c in range(0, 16):
            self.events[c] = []
        self.textEvents = []
        self.lyricEvents = []

        # internal use, not for user
        self.midifile = None
        self.offset = 0

        # useful things to examine after reading
        self.MidiFormat = None
        self.numTracks = None
        self.beatDivision = None
        self.firstNote = None  # offset of 1st note in file

    def mvarlen(self):
        """ Convert variable length midi value to int. """

        x = 0
        for i in range(4):

            try:
                b = self.midifile[self.offset]
                self.offset += 1
            except:
                raise RuntimeError("Invalid MIDI file include (varlen->int)")

            if b < 0x80:
                x = (x << 7) + b
                break
            else:
                x = (x << 7) + (b & 0x7f)

        return int(x)

    def strs(self, count):
        """ Return a string of count chars. """

        s = self.midifile[self.offset:self.offset+count]
        s = s.decode(encoding=gbl.encoding)
        self.offset += count
        return s

    def chars(self, count):
        """ Return 'count' chars from file (updates global pointer). """

        b = list(self.midifile[self.offset:self.offset+count])
        self.offset += count
        return b

    def m1i(self):
        """ Get 1 byte (updates global pointer). """

        try:
            b = self.midifile[self.offset]
            self.offset += 1
        except:
            raise RuntimeError("Invalid MIDI file include (byte, offset=%s)" % self.offset)

        return b


    def m32i(self):
        """ Convert 4 bytes to integer. """

        x = 0
        for i in range(4):
            try:
                b = self.midifile[self.offset]
                self.offset += 1
            except:
                raise ("Invalid MIDI file include (i32->int, offset=%s)" % self.offset)

            x = (x << 8) + b

        return int(x)


    def m16i(self):
        """ Convert 2 bytes to integer. """

        x = 0
        for i in range(2):
            try:
                b = self.midifile[self.offset]
                self.offset += 1
            except:
                raise ("Invalid MIDI file include (i16->int, offset=%s)" % self.offset)
            x = (x << 8) + b

        return int(x)

    def adjustBeats(self, adjustment):
        """ Adjust all the offsets in the generated data to compensate
            between midi timing standards. MMA uses 194 ticks/beat. 
        """

        for ch in self.events:
            for e in self.events[ch]:
                e[0] = int(e[0] * adjustment)
        for e in self.textEvents:
            e[0] = int(e[0] * adjustment)
        for e in self.lyricEvents:
            e[0] = int(e[0] * adjustment)

        self.beatDivision = int(self.beatDivision * adjustment)
        self.firstNote = int(self.firstNote * adjustment)

        return None

    ### Main reader

    def readFile(self, filename):
        """ Read the midi file into memory and parse it. """

        try:
            inpath = open(filename, "rb")
        except:
            raise RuntimeError("Unable to open MIDI file '%s' for reading." % filename )

        try:
            self.midifile = inpath.read()
        except:
            raise RuntimeError("Unable to read MIDI file '%s'." % filename)

        self.midifile = bytearray(self.midifile)  # needed for python2, does nothing in 3
        inpath.close()

        # legit midi file?
        
        hd = self.strs(4)
        if hd != 'MThd':
            raise RuntimeError("Expecting 'MThd', %s not a standard midi file" % filename)

        if self.m32i() != 6:
            raise RuntimeError("Expecting a 32 bit value of 6 in header")

        self.MidiFormat = self.m16i()

        if self.MidiFormat not in (0, 1):
            raise ("MIDI file format %s not recognized" % self.MidiFormat)

        self.numTracks = self.m16i()
        self.beatDivision = self.m16i()

        self.firstNote = 0xffffff

        # Now read the data, track by track

        for tr in range(self.numTracks):
            tm = 0

            # Validity for each track

            hdr = self.strs(4)
            if hdr != 'MTrk':
                raise RuntimeError("Malformed MIDI file in track header")
            trlen = self.m32i()  # track length, not used ... advances ptr

            lastevent = None

            while 1:
                tm += self.mvarlen()        # adjust total offset by delta

                ev = self.m1i()

                if ev < 0x80:
                    if not lastevent:
                        raise RuntimeError ("Illegal running status in %s at %s" %
                              (self.midifile, self.offset))
                    self.offset -= 1
                    ev = lastevent

                sValue = ev >> 4        # Shift MSBs to get a 4 bit value 
                channel = ev & 0x0f

                if sValue == 0x8:        # note off event
                    note = self.m1i()
                    vel = self.m1i()

                    if self.octaveAdjust and channel != 9:  # drums are 9 when 0..15 (not 10!)
                        note += self.octaveAdjust
                        while note < 0:
                            note += 12
                        while note > 127:
                            note -= 12
                    self.events[channel].append([tm, ev & 0xf0, note, vel])

                elif sValue == 0x9:        # note on event
                    if tm < self.firstNote:
                        self.firstNote = tm
                    note = self.m1i()
                    vel = self.m1i()

                    if self.octaveAdjust and channel != 9:
                        note += self.octaveAdjust
                        while note < 0:
                            note += 12
                        while note > 127:
                            note -= 12

                    if self.velocityAdjust != 100:
                        vel = (vel * self.velocityAdjust) // 100
                        if vel < 0:
                            vel = 1
                        if vel > 127:
                            vel = 127

                    self.events[ev & 0xf].append([tm, ev & 0xf0, note, vel])

                elif sValue == 0xa:        # key pressure
                    self.events[ev & 0xf].append([tm, ev & 0xf0, self.chars(2)])

                elif sValue == 0xb:        # control change
                    self.events[ev & 0xf].append([tm, ev & 0xf0, self.chars(2)])

                elif sValue == 0xc:        # program change
                    if self.ignorePC:      # default is to ignore these
                        self.offset += 1
                    else:                  # set with option ignorePC=1
                        self.events[ev & 0xf].append([tm, ev & 0xf0, self.chars(1)])

                elif sValue == 0xd:        # channel pressure
                    self.events[ev & 0xf].append([tm, ev & 0xf0, self.chars(1)])

                elif sValue == 0xe:        # pitch blend
                    self.events[ev & 0xf].append([tm, ev & 0xf0, self.chars(2)])

                elif sValue == 0xf:       # system, mostly ignored
                    if ev == 0xff:        # meta events
                        a = self.m1i()

                        if a == 0x00:    # sequence number
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x01:  # text (could be lyrics)
                            self.textEvents.append([tm, self.strs(self.mvarlen())])
  
                        elif a == 0x02:  # copyright
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x03:  # seq/track name
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x04:  # instrument name
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x05:  # lyric
                            self.lyricEvents.append([tm, self.strs(self.mvarlen())])

                        elif a == 0x06:  # marker
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x07:  # cue point
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x21:  # midi port
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x2f:  # end of track
                            l = self.mvarlen()
                            self.offset += l
                            break

                        elif a == 0x51:  # tempo
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x54:  # SMPTE offset
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x58:  # time sig
                            l = self.mvarlen()
                            self.offset += l

                        elif a == 0x59:  # key sig
                            l = self.mvarlen()
                            self.offset += l

                        else:        # probably 0x7f, proprietary event
                            l = self.mvarlen()
                            self.offset += l

                    elif ev == 0xf0:    # system exclusive
                        l = self.mvarlen()
                        self.offset += l

                    elif ev == 0xf2:    # song position pointer, 2 bytes
                        self.offset += 2

                    elif ev == 0xf3:    # song select, 1 byte
                        self.offset += 1

                    else:        # all others are single byte commands
                        pass

                if ev >= 0x80 and ev <= 0xef:
                    lastevent = ev

        return None

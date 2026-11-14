# pat.py

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


import copy
import random

import MMA.notelen
import MMA.translate
import MMA.midi
import MMA.midiC
import MMA.mdefine
import MMA.volume
import MMA.alloc
import MMA.seqrnd
import MMA.truncate
import MMA.ornament
import MMA.trigger
import MMA.rpitch
import MMA.debug

from . import gbl
from MMA.common import *
from MMA.miditables import NONETONE, drumKits

pats = {}        # Storage for all pattern defines

class Pgroup:
    pass


defaultDrum = 0
defaultVoice = 0
currentChord = None

def getIncDec(v):
    """ See if 'v' starts with -/+. Strip and return. """

    if v.startswith('-'):
        incr = -1
        v = v[1:]
    elif v.startswith('+'):
        incr = 1
        v = v[1:]
    else:
        incr = 0

    return incr, v


def getIncDecValue(orig, inc, new):
    """ Set value based on original, increment and new values. """

    if inc == -1:
        return orig - new
    elif inc == 1:
        return orig + new
    else:
        return new


def getRndPair(l, trk, min, max):
    """ Parse off a pair (or single) value for random settings (rvolume, etc.). """

    if not l:
        error("%s: expecting a value or value pair." % trk)

    if l.count(',') > 1:
       error("%s: Random pairs can only have one ','." % trk)

    if l.count(',') == 1:
        n1, n2 = l.split(',')
        try:
            n1 = int(n1)
            n2 = int(n2)
        except:
            error("%s: Expecting integers, not '%s' or '%s'." % (trk, n1, n2))
    else:
        try:
            n1 = int(l)
        except:
            error("%s: Expecting integer, not '%s'." % (trk, n1))
        n2 = n1 * -1

    if n2 < n1:
        n1, n2 = n2, n1

    if n1 < min or n1 > max or n2 < min or n2 > max:
        error("%s: Max range is %s to %s." % (trk, min, max))

    return (n1, n2)


class PC:
    """ Pattern class.

        Define classes for processing drum, chord, arp, and chord track.
        These are mostly the same, so we create a base class and derive
        the others from it.

        We have a class for each track type. They are all derived
        from the base PC class. Some classes have their own __init__().
        They call back here after doing their own special stuff.

    """

    def __init__(self, nm):

        self.inited = 0
        self.name = nm
        self.channel = 0
        self.grooves = {}
        self.saveVols = {}
        self.ssvoice = -1  # Track the voice set for the track
        self.smidiVoice = ()  # Track MIDIVoice cmds to avoid dups
        self.midiSent = 0   # if set, MIDICLEAR invoked.

        """ Midi commands like Pan, Glis, etc. are stacked until musical
            data is actually written to the track. Each item in
            the midiPending list is a name (PAN, GLIS, etc), timeoffset, value.
        """

        self.midiPending = []

        self.riff = []

        self.disable = 0
        self.sticky = False
        self.clearSequence()

        self.nextVolume = None
        self.cVolume = 127  # assume device is set to max.
        self.inited = 1

        # Double test is needed! We disable a track only
        # when there is a list of tracks which are NOT
        # disabled. The variable name is slightly misleading.
        if gbl.muteTracks and nm not in gbl.muteTracks:
            self.disable = 1


    ##########################################
    ## These are called from parse() to set options

    def setCompress(self, ln):
        """ set/unset the compress flag. """

        ln = lnExpand(ln, '%s Compress' % self.name)

        tmp = []

        for n in ln:
            n = getTF(n, "%s Compress" % (self.name))
            if n:
                n = 1
            else:
                n = 0
            if n and self.vtype == 'CHORD' and self.voicing.mode:
                vwarn = 1

            tmp.append(n)

        self.compress = seqBump(tmp)

        if self.vtype not in ("CHORD", "ARPEGGIO"):
            warning("Compress is ignored in %s tracks" % self.vtype)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "Compress")

    def setRange(self, ln):
        """ set range. """

        ln = lnExpand(ln, '%s Range' % self.name)

        tmp = []

        for n in ln:
            n = stof(n)
            if n == 0:
                n = 1
            if n <= 0 or n >= 6:
                error("Range %s out-of-range; must be between 0..6, not %s" % (self.name, n))

            tmp.append(n)

        self.chordRange = seqBump(tmp)

        if self.vtype not in ("SCALE", "ARPEGGIO", "ARIA"):
            warning("%s Range: ignored in '%s' tracks" % (self.name, self.vtype))

        if self.vtype == 'ARIA':
            self.restart()

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "Range")

    def setVoicing(self, ln):
        """ set the Voicing Mode options.

            This is an error trap stub. The real code is in patChord.py
            and patSolo.py (settings are only valid for those types).
        """

        error("Voicing is not supported for %s tracks" % self.vtype)

    def setForceOut(self):
        """ Set the force output flag. This does 2 things: assigns
            a midi channel and sends the voicing setting to the track.
        """

        if not self.channel:
            self.setChannel()
        self.clearPending()

        self.insertVoice(gbl.seqCount)

    def setDelay(self, ln):
        """ Set a delay for this track. """

        ln = lnExpand(ln, '%s Delay' % self.name)

        tmp = []
        for n in ln:
            if n[0] == '-':
                mul = -1
                n = n[1:]
            elif n[0] == '+':
                mul = 1
                n = n[1:]
            else:
                mul = 1
            tmp.append(MMA.notelen.getNoteLen(n) * mul)

        self.delay = seqBump(tmp)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "Delay")

    def setDupRoot(self, ln):
        """ set/unset root duplication.

            This is a stub. Only valid for CHORDs and that is where the code is."""

        warning("RootDup has no effect in %s tracks" % self.vtype)

    def setChords(self, ln):
        """ Set track specific chord(s). """

        # An empty arg. or a single '-' turns off this stuff.
        if not ln:
            self.chord = seqBump([[]])
            return

        # Bracket the chord data. It can be passed as "C D E" or
        # "{ C D E } {i ii iii}". Also permitted is an empty {} or
        # a single "/" (repeat last) with or without {}.

        # make the entire line into a long string.
        ln = ' '.join(ln)

        clist = []
        while 1:   # loop on entire string
            if not ln:
                break

            if ln[0] == '/':  # handle single repeat
                if clist:
                    clist.append(clist[-1])
                    ln = ln[1:].strip()
                    continue
                else:
                    error("%s CHORDS: cannot start with a '/'." % self.name)

            if ln[0] != '{':
                ln = '{ ' + ln + '}'
                continue

            ln, s = pextract(ln, '{', '}', onlyone=True)
            if not s:
                error("%s CHORDS: Multiple bar chords need {}s." % self.name)

            s = s[0].split()
            if len(s) == 1 and s[0] == '/':    # this would be a {/}
                ln = '/' + ln
                continue    # loop back and handle repeat above

            if s and s[0] == '/':
                error("%s CHORDS: Chord list cannot start with '/'." % self.name)

            clist.append(s)

        if len(clist) > gbl.seqSize:
            warning("%s CHORDS: Too many bars(%s) for seq size(%s). Chord list truncated."
                    % (self.name, len(clist), gbl.seqSize))

        self.chord = seqBump(clist)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "Chords")

    def setChordLimit(self, ln):
        """ set/unset the chordLimit flag. """

        mode = 0
        forceLen = 0
        tname = self.name
        
        ln, options = opt2pair(ln, toupper=True)
        for cmd, opt in options:
            if cmd == 'DROP':
                mode = stoi(opt, "Expecting integer value for %s DROP, not '%s'"
                            % (tname, opt))
                if mode<1 or mode>7:
                    # We assume that you are smart enough to simply drop the '9',
                    # '11', '13' from the chord if you don't want it :)
                    error("%s LIMIT Drop value must be 1..7, not '%s'."
                          % (tname, mode))

            elif cmd == 'FORCE':
                forceLen = getTF(opt, "%s LIMIT FORCE expecting True/False, not '%s'"
                                 % (tname, opt))
                
            else:
                error("LIMIT: Option '%s' not known." % cmd)
                
        if len(ln) != 1:
            error("%s LIMIT: Use <value 0-8> DROP=arg (too many args)."
                  % tname)

        n=ln[0].upper()
        if n in ("OFF", "FALSE"):
            n = 0
        else:
            n = stoi(n, "%s LIMIT argument for must be a value, not '%s'." % (tname, n))

        if n != 0 and (n < 3 or n > 8):
            error("%s LIMIT '%s' out-of-range; must be 0 or 3 to 8" % (self.name, n))

        self.chordLimit = [n, mode, forceLen]

        if self.vtype not in ("CHORD", "ARPEGGIO"):
            warning("%s LIMIT is ignored in %s tracks" % (tname, self.vtype))

        if MMA.debug.debug:
            MMA.debug.trackSet(tname, "Limit")

    def setChannel(self, ln=None):
        """ Set the midi-channel number for a track.

        - Checks for channel duplication
        - Auto assigns channel number if ln==''


        If no track number was passed, then we try to
        auto-alloc a track. First, we see if a preference
        was set via MidiChPref. If these is no preference,
        or if the preferred channel is already allocated
        we go though the list, top to bottom, to find
        an available channel.
        """

        if not ln:
            try:
                c = gbl.midiChPrefs[self.name]
            except:
                c = 0

            if not c or gbl.midiAvail[c]:
                c = -1
                for a in range(16, 0, -1):
                    if a != 10 and not gbl.midiAvail[a]:
                        c = a
                        break

            if c < 0:
                # parse all tracks and find lowest allocated offset
                lowOff = gbl.tickOffset
                lowCh = -1
                for ch in range(1, 17):
                    if ch == 10:
                        pass
                    t = gbl.mtrks[ch].getLastOffset()
                    if t < lowOff:
                        lowOff = t
                        lowCh = ch
                c = lowCh

        else:
            c = stoi(ln, "%s Channel assignment expecting Value, not %s" %
                    (self.name, ln))

            if c < 0 or c > 16:
                error("%s Channel must be 0..16, not %s" % (self.name, ln))

        if c == 10:
            if self.vtype == 'DRUM':
                pass
            elif self.vtype in ('SOLO', 'MELODY') and self.drumType:
                pass
            else:
                error("Channel 10 is reserved for DRUM, not %s" % self.name)

        if self.vtype == 'DRUM' and c != 10:
            error("DRUM tracks must be assigned to channel 10")

        # Disable the channel.

        if c == 0:
            if gbl.midiAvail[self.channel]:
                gbl.midiAvail[self.channel] -= 1
            s = "%s channel disabled" % self.name
            if gbl.midiAvail[self.channel]:
                s += " Other tracks are still using channel %s" % self.channel
            else:
                s += " Channel %s available" % self.channel
            warning(s)
            self.channel = 0
            self.disable = 1
            return

        if c != 10:
            for a, tr in gbl.tnames.items():
                if a == self.name:    # okay to reassign same number
                    continue

                if tr.channel == c:
                    warning("Channel %s is being reassigned to %s" % (c, tr.name))

        self.channel = c
        if not self.name in gbl.midiAssigns[c]:
            gbl.midiAssigns[c].append(self.name)

        gbl.midiAvail[c] += 1

        if not c in gbl.mtrks:
            gbl.mtrks[c] = MMA.midi.Mtrk(c)
            if MMA.debug.debug:
                dPrint("MIDI channel %s buffer created" % c)

        # If a track name has not be set via MidiTName (this will be
        # queued since the track just got a midi assignment here) we
        # put a default track name into the queue.

        if c != 10:
            f = 0
            for a, i in enumerate(self.midiPending):
                if i[0] == 'TNAME':
                    f = 1
            if not f:
                self.midiPending.append(('TNAME', 0, self.name.title()))

        if MMA.debug.debug:
            dPrint("MIDI Channel %s assigned to %s" % (self.channel, self.name))

    def setChShare(self, ln):
        """ Share midi-channel setting. """

        if self.channel:    # If channel already assigned, ignore
            warning("Channel for %s has previously been assigned "
                    "(can't ChShare)" % self.name)
            return

        """ Get name of track to share with and make sure it exists.
            If not, trackAlloc() will create the track. Do some
            sanity checks and ensure that the shared track has
            a channel assigned.
        """

        sc = ln.upper()

        MMA.alloc.trackAlloc(sc, 1)

        if not sc in gbl.tnames:
            error("Channel '%s' does not exist. No such name" % sc)

        if sc == self.name:
            error("%s can't share MIDI channel with itself" % sc)

        if not gbl.tnames[sc].channel:
            gbl.tnames[sc].setChannel()

        schannel = gbl.tnames[sc].channel

        if not schannel:
            error("CHShare attempted to assign MIDI channel for %s, but "
                  "none avaiable" % self.name)

        """ Actually do the assignment. Also copy voice from
            base track to this one ... it's going to use that voice anyway?
        """

        self.channel = schannel
        self.voice = gbl.tnames[sc].voice[:]

        # Update the avail. lists

        gbl.midiAssigns[self.channel].append(self.name)
        gbl.midiAvail[self.channel] += 1

    def setSticky(self, ln):
        """ Set track as sticky. Sticky tracks are ignored by groove commands. """

        if len(ln) != 1:
            error("%s Sticky needs single argument ('True/False')." % self.name)
         
        arg = ln[0].upper()
        self.sticky = getTF(arg, "%s Sticky" % (self.name))

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "Sticky")

        
    def setStrum(self, ln):
        """ Set Strum time. """

        ln = lnExpand(ln, '%s Strum' % self.name)
        tmp = []

        for n in ln:
            if ',' in n:
                a, b = n.split(',', 1)
                a = stoi(a, "Argument for %s Strum must be an integer" % self.name)
                b = stoi(b, "Argument for %s Strum must be an integer" % self.name)
            else:
                a = stoi(n, "Argument for %s Strum must be an integer" % self.name)
                b = a

            if a > b:
                b, a = a, b

            if a < -300 or a > 300 or b < -300 or b > 300:
                error("STRUM: %s out-of-range. All values must be -300..300" % n)

            if a == 0 and b == 0:
                tmp.append(None)
            else:
                tmp.append((a, b))

        self.strum = seqBump(tmp)

        if self.vtype == "DRUM":
            warning("Strum has no effect in %s tracks" % self.name)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "Strum")

    def setStrumAdd(self, ln):
        """ Additional options for strum. """

        ln = lnExpand(ln, '%s StrumAdd' % self.name)
        tmp = []

        for i in ln:
            v = stoi(i, "Argument for %s StrumAdd must be an integer" % self.name)
            tmp.append(v)

        self.strumAdd = seqBump(tmp)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "StrumAdd")

    def getStrum(self, sc):
        """ Returns the strum factor. Note that if strum==(0,0) a 0 is returned."""
        

        if not self.strum[sc]:
            return 0
        
        a, b = self.strum[sc]  # split out tuple. Always 2 values (or empty)
        if a == b:
            return a
        
        return random.randint(a, b)

    def setTone(self, ln):
        """ Set Tone. Error trap, only drum tracks have tone. """
        
        error("Tone command not supported for %s track" % self.name)

    def setOn(self):
        """ Turn ON track. """

        if gbl.muteTracks and self.name not in gbl.muteTracks:
            warning("Attempt to enable muted track %s ignored." % self.name)

        else:
            self.disable = 0
            self.ssvoice = -1

        if MMA.debug.debug:
            dPrint("%s Enabled" % self.name)

    def setOff(self):
        """ Turn OFF track. """

        self.disable = 1

        if MMA.debug.debug:
            dPrint("%s Disabled" % self.name)

    def setRVolume(self, ln):
        """ Set the volume randomizer for a track. """

        msg = "%s Rvolume" % self.name
        ln = lnExpand(ln, msg)
        tmp = []
        for n in ln:
            n1, n2 = getRndPair(n, msg, -100, 100)
            tmp.append([n1 / 100., n2 / 100.])

        self.rVolume = seqBump(tmp)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "RVolume")

         
    def setRSkip(self, ln):
        """ Set the note random skip factor for a track. """

        msg = "%s RSkip" % self.name
        ln, options = opt2pair(ln)

        if not ln:
            error("%s: Needs weighting list and optional beats=[]." % msg)

        self.rSkipBeats = []
        for cmd, opt in options:
            if cmd.upper() == 'BEATS':
                beats = opt.split(',')
                if not beats:
                    error("%s Beats: Expecting list of affected beats." % msg)
                self.rSkipBeats = []
                for b in beats:
                    b = stof(b)
                    if b < 1:
                        error("%s: Beats must be => 1, not '%s'" % (msg, b))
                    if b >= gbl.QperBar + 1:
                        error("%s: Beats must less than %s, not '%s'" % (msg, gbl.QperBar + 1, b))
                    self.rSkipBeats.append(int((b - 1) * gbl.BperQ))

            else:
                error("%s: Unknown option %s." % (msg, cmd))

        ln = lnExpand(ln, msg)
        tmp = []

        for n in ln:
            n = stoi(n, "%s: Expecting integer" % msg)

            if n < 0 or n > 99:
                error("%s: arg must be 0..99" % msg)

            tmp.append(n / 100.)

        self.rSkip = seqBump(tmp)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "RSkip")


    def setRDuration(self, ln):
        """ Set the duration randomizer for a track. """

        msg = "%s RDuration" % self.name
        ln = lnExpand(ln, msg)
        tmp = []

        for n in ln:
            n1, n2 = getRndPair(n, msg, -100, 100)
            tmp.append([n1 / 100., n2 / 100.])

        self.rDuration = seqBump(tmp)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "RDuration")


    def setRTime(self, ln):
        """ Set the timing randomizer for a track. """

        msg = "%s RTime" % self.name
        ln = lnExpand(ln, msg)
        tmp = []

        for n in ln:
            n1, n2 = getRndPair(n, msg, -100, 100)
            tmp.append([n1, n2])

        self.rTime = seqBump(tmp)

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "RTime")

    def setDirection(self, ln):
        """ Set scale direction. """

        ln = lnExpand(ln, "%s Direction" % self.name)
        tmp = []

        for n in ln:
            n = n.upper()
            if not n in ('UP', 'DOWN', 'BOTH', 'RANDOM'):
                error("Unknown %s Direction '%s'" % (self.name, n))
            tmp.append(n)

        self.direction = seqBump(tmp)

        if self.vtype == 'SCALE':
            self.lastChord = None
            self.lastNote = -1

        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "Direction")

    def setScaletype(self, ln):
        """ Set scale type.

            This is a error stub. The real code is in the permitted track code.
        """

        warning("ScaleType has no effect in %s tracks" % self.vtype)

    def setInvert(self, ln):
        """ Set inversion for track.

            This can be applied to any track,
            but has no effect in drum tracks. It inverts the chord
            by one rotation for each value.
        """

        msg = "%s Invert" % self.name
        ln = lnExpand(ln, msg)

        tmp = []

        for n in ln:
            if not ',' in n:
                try:
                    n1 = n2 = int(n)
                except:
                    error("Invert %s doesn't recognize '%s'." % (self.name, n))
            else:
                n1, n2 = getRndPair(n, msg, -10, 10)
            if n1 == 0 and n2 == 0:
                tmp.append([])
            else:
                tmp.append([n1, n2])

        if self.vtype == 'CHORD' and self.voicing.mode and any(tmp):
            warning("%s: Setting both Voicing Mode and Invert is not a good idea" % 
                    self.name)

        if self.vtype not in ("CHORD", "ARPEGGIO"):
            warning("Invert is ignored in %s tracks" % self.vtype)

        self.invert = seqBump(tmp)
        
        if MMA.debug.debug:
            MMA.debug.trackSet(self.name, "Invert")

    def setOctave(self, ln):
        """ Set the octave for a track. Use 0-10, -x, +x. """

        ln = lnExpand(ln, '%s Octave' % self.name)
        ln = seqBump(ln)  # Needed for +/- values to complete
        tmp = []
        i = 0
        for n in ln:
            incr, n = getIncDec(n)
            n = stoi(n, "Argument for %s Octave must be an integer" % self.name)
            n = getIncDecValue(self.octave[i] // 12, incr, n)

            if n < 0 or n > 10:
                error("Octave %s out-of-range; must be 0..10" % n)
            tmp.append(n * 12)
            i += 1

        self.octave = seqBump(tmp)

        if MMA.debug.debug:
            dPrint("Set %s Octave to: %s" % 
                  (self.name, ' '.join([str(i // 12) for i in self.octave])))


    def setMOctave(self, ln):
        """ Set the octave for a track based on MIDI octave values. Use -1..9. """

        ln = lnExpand(ln, '%s MOctave' % self.name)
        tmp = []

        for n in ln:
            n = stoi(n, "Argument for %s MOctave must be an integer" % self.name)
            if n < -1 or n > 9:
                error("MOctave %s out-of-range; must be -1..9" % n)
            tmp.append((n + 1) * 12)

        self.octave = seqBump(tmp)

        if MMA.debug.debug:
            dPrint("Set %s MOctave to: %s" % 
                  (self.name, ' '.join([str((i // 12) - 1) for i in self.octave])))


    def setSpan(self, start, end):
        """ Set span.

            Note: The start/end parm has been verified in parser.

        """

        if self.vtype == 'DRUM':
            warning("Span has no effect in Drum tracks")

        self.spanStart = start
        self.spanEnd = end

        if MMA.debug.debug:
            dPrint("Set %s Span to %s...%s" % (self.name, self.spanStart, self.spanEnd))

    def setSeqSize(self):
        """ Expand existing pattern list.

            Track functions may have their own and do a callback.
        """

        self.sequence = seqBump(self.sequence)
        if self.midiVoice:
            self.midiVoice = seqBump(self.midiVoice)
        if self.midiSeq:
            self.midiSeq = seqBump(self.midiSeq)
        self.invert = seqBump(self.invert)
        self.artic = seqBump(self.artic)
        self.chord = seqBump(self.chord)
        self.volume = seqBump(self.volume)
        self.voice = seqBump(self.voice)
        self.rVolume = seqBump(self.rVolume)
        self.rSkip = seqBump(self.rSkip)
        self.rTime = seqBump(self.rTime)
        self.rDuration = seqBump(self.rDuration)
        self.seqRndWeight = seqBump(self.seqRndWeight)
        self.strum = seqBump(self.strum)
        self.strumAdd = seqBump(self.strumAdd)
        self.octave = seqBump(self.octave)
        self.harmony = seqBump(self.harmony)
        self.harmonyOnly = seqBump(self.harmonyOnly)
        self.harmonyVolume = seqBump(self.harmonyVolume)
        self.direction = seqBump(self.direction)
        self.delay = seqBump(self.delay)
        self.scaleType = seqBump(self.scaleType)
        self.compress = seqBump(self.compress)
        self.chordRange = seqBump(self.chordRange)
        self.dupRoot = seqBump(self.dupRoot)
        self.unify = seqBump(self.unify)
        self.accent = seqBump(self.accent)

    def setVoice(self, ln):
        """ Set the voice for a track.

            Note, this just sets flags, the voice is set in bar().
            ln[] is not nesc. set to the correct length.

            the voice can be gm-string, user-def-string, or value.
            A value can be xx.yy.vv, yy.vv or vv
        """

        ln = lnExpand(ln, '%s Voice' % self.name)

        # It we have a drum track, permit setting voice with the
        # the name of a drumkit. Note, kitnames all end with "KIT"
        # but the actual kits are stored without.
        if self.vtype == 'DRUM':
            tmp = [ x.upper() for x  in ln ]
            newline = []
            for a in tmp:
                if a.endswith('KIT'):
                    a = a[:-3]
                    if a in drumKits:
                        a = str(drumKits[a])
                newline.append(a)
            ln = newline

        tmp = []
        for n in ln:
            voc = MMA.midiC.decodeVoice(n)
            tmp.append(voc)

        self.voice = seqBump(tmp)

        if self.channel and len(gbl.midiAssigns[self.channel]) > 1:
            a = []
            for n in gbl.midiAssigns[self.channel]:
                if n != self.name:
                    a.append(n)

            if len(a) > 1:      # a bit for grammar
                t1 = "Tracks"
                v1 = "are"
            else:
                t1 = "Track"
                v1 = "is"

            warning("%s %s %s shared with %s. Changing voice may create conflict"
                    % (t1, ', '.join(a), v1, self.name))

        if MMA.debug.debug:
            if self.vtype == 'DRUM':
               dPrint("Set %s Tone to: %s" % 
                      (self.name, ' '.join([MMA.midiC.valueToDrum(i) for i in self.voice])))
            else:
                dPrint("Set %s Voice to: %s" % 
                       (self.name, ' '.join([MMA.midiC.valueToInst(i) for i in self.voice])))


    def setMidiClear(self, ln):
        """ Set MIDIclear sequences. """

        if ln[0] in 'zZ-':
            self.midiClear = None
        else:
            self.midiClear = MMA.mdefine.mdef.get(ln[0])

        if MMA.debug.debug:
            dPrint("%s MIDIClear: %s" % (self.name, self.midiSeqFmt(self.midiClear)))

    def doMidiClear(self):
        """ Reset MIDI settings. """

        if self.midiSent:
            if not self.midiClear:
                warning("%s: Midi data has been inserted with MIDIVoice/Seq "
                        "but no MIDIClear data is present" % self.name)

            else:
                for i in self.midiClear:
                    gbl.mtrks[self.channel].addCtl(gbl.tickOffset, i[1])

            self.midiSent = 0

    def doChannelReset(self):
        """ Reset the midi voicing to 'sane'. Called when track ended.

            Note that standard MIDI voicing is left alone, only extended
            voicing is affected.

        """

        if self.ssvoice > 127 and self.ssvoice != NONETONE:
            gbl.mtrks[self.channel].addProgChange(gbl.tickOffset, 0, self.ssvoice)

    def setMidiSeq(self, ln):
        """ Set a midi sequence for a track.

        This is sent for every bar. Syntax is:
        <beat> <ctrl> hh .. ; ...

        or a single '-' to disable.
        """

        """ lnExpand() works here! The midi data has been converted to
             pseudo-macros already in the parser. """

        ln = lnExpand(ln, "%s MidiSeq" % self.name)

        seq = []
        for a in ln:
            if a in 'zZ-':
                seq.append(None)
            else:
                seq.append(MMA.mdefine.mdef.get(a.upper()))

        if seq.count(None) == len(seq):
            self.midiSeq = []
        else:
            self.midiSeq = seqBump(seq)

        if MMA.debug.debug:
            dPrint("%s MIDISeq: %s" % 
                  (self.name, ' '.join(['{ %s }' % self.midiSeqFmt(l) for l in seq])))


    def setMidiVoice(self, ln):
        """ Set a MIDI sequence for a track.

        This is sent whenever we send a VOICE. Syntax is:
        <beat> <ctrl> hh .. ; ...

        or a single '-' to disable.
        """

        # lnExpand() works here! The midi data has been converted to
        # pseudo-macros already in the parser. 
        ln = lnExpand(ln, '%s MIDIVoice' % self.name)

        seq = []
        for a in ln:
            if a in 'zZ':  # some bars in seq might not want midi stuff
                seq.append(None)
            else:
                seq.append(MMA.mdefine.mdef.get(a.upper()))

        if seq.count(None) == len(seq):  # see if all bars in seq are None
            self.midiVoice = []          # yes, kill the whole voice thing
        else:
            self.midiVoice = seqBump(seq)  # set voice for all bars in seq
 
        if MMA.debug.debug:
            dPrint("%s MIDIVoice: %s" %
                  (self.name, ' '.join(['{ %s }' % self.midiSeqFmt(l) for l in seq])))


    def midiSeqFmt(self, lst):
        """ Used by setMidiVoice/Clear/Seq for debugging format. """

        if lst is None:
            return ''
        ret = ''
        for i in lst:
            ret += "%s %s 0x%02x ; " % (i[0],
                          MMA.midiC.valueToCtrl(i[1][0]), i[1][1])
        return ret.rstrip("; ")

    def setVolume(self, ln):
        """ Set the volume for a pattern.
            ln - list of volume names (pp, mf, etc)
            ln[] not nesc. correct length
        """

        ln = lnExpand(ln, '%s Volume' % self.name)
        ln = seqBump(ln)  # needed for -/+ setting to apply to all seqs

        tmp = [None] * len(ln)
        self.futureVols = []   # clear off dangling (de)cresc for voice.


        for i, n in enumerate(ln):
            a = MMA.volume.calcVolume(n, self.volume[i])
            if self.vtype == 'DRUM' or \
                    (self.vtype in ('MELODY', 'SOLO') and self.drumType):
                a = MMA.translate.drumVolTable.get(self.toneList[i], a)
            else:
                a = MMA.translate.voiceVolTable.get(self.voice[i], a)
            tmp[i] = a

        self.volume = seqBump(tmp)

        if MMA.debug.debug:
            dPrint("Set %s Volume to: %s" %
                  (self.name, ' '.join([str(int(a * 100))  for a in self.volume])))

    def setCresc(self, dir, ln):
        """ Set Crescendo for a track.     """

        if len(ln) == 3:
            self.setVolume([ln[0]])
            ln = ln[1:]

        if len(ln) != 2:
            error("Cresc expecting 2 or 3 args.")

        vol = self.volume[0]

        if self.volume.count(vol) != len(self.volume):
            warning("(De)Crescendo being used with track with variable sequence volumes")

        self.futureVols = MMA.volume.fvolume(dir, vol, ln)

        if MMA.debug.debug:
            dPrint("Set %s Cresc to: %s" % 
                  (self.name, ' '.join([str(int(a * 100)) for a in self.futureVols])))


    def setSwell(self, ln):
        """ Set a swell (cresc<>decresc) for track. """

        if len(ln) == 3:            # 3 args, 1st is intial setting
            self.setVolume([ln[0]])
            ln = ln[1:]

        if len(ln) != 2:
            error("%s Swell expecting 2 or 3 args." % self.name)

        if self.volume.count(self.volume[0]) != len(self.volume):
            warning("%s Swell being used with track with variable sequence volumes."
                    % self.name)

        count = stoi(ln[1])
        if count < 2:
            error("%s Swell bar count must be 2 or greater." % self.name)

        count += 1
        c = count // 2
        if count % 2:   # even number of bars (we bumped count)
            offset = 1
            c += 1
        else:           # odd number
            offset = 0
        c = str(c)

        self.futureVols = MMA.volume.fvolume(0, self.volume[0],
                                             [ln[0], c])

        self.futureVols.extend(MMA.volume.fvolume(0, self.futureVols[-1],
             [str(int(self.volume[0] * 100)), c])[offset:])

        if MMA.debug.debug:
            dPrint("Set %s Swell to: %s" % 
                  (self.name, ' '.join([str( int(a * 100)) for a in self.futureVols])))

    def setMallet(self, ln):
        """ Mallet (repeat) settngs. """

        if self.vtype == "PLECTRUM":
            warning("%s: Mallet has no effect, ignored." % self.name)
            return

        for l in ln:
            try:
                mode, val = l.upper().split('=')
            except:
                error("%s Mallet: each option must contain a '=', not '%s'" % (self.name, l))

            if mode == 'RATE':
                if val == '0' or val.upper() == 'NONE':
                    self.mallet = 0
                else:
                    self.mallet = MMA.notelen.getNoteLen(val)

            elif mode == 'DECAY':
                val = stof(val, "Mallet Decay must be a value, not '%s'" % val)

                if val < -50 or val > 50:
                    error("%s Mallet: Decay rate must be -50..+50" % self.name)

                self.malletDecay = val / 100.

            else:
                error("%s Mallet: %s is not a option." % (self.name, mode))

        if MMA.debug.debug:
            dPrint("%s Mallet Rate:%s Decay:%s" %
                (self.name, self.mallet, self.malletDecay))

    def setAccent(self, ln):
        """ Set the accent values. This is a list of lists, a list for each seq. """

        tmp = []

        """ 2 ways to call this:

            Track Accent 1 20 3 -10   -- Sets accent for all bars in sequence to
                   the same values. The parser normalizes this by adding a {}
                   around the args.
            Track Accent {1 20 3 -10} -- Same as above
            Track Accent {1 20} / {/} {3 20} -- Different for each bar in seq.

            At this point ln is a string. We extract each set of {}s and build a
            new ln[].

            Note that the "/" can or not have {}s.

            An empty string resets to no accents.
        """

        ln = ' '.join(ln)
        if not ln.startswith('{'):
            ln = '{' + ln + "}"

        l = []
        while ln:
            if ln[0] == "/":  # / not delimited with {}
                ln = "{/}" + ln[1:]

            if ln[0][0] != '{':
                error("%s Accent: Unmatched or missing '{} delimters" % self.name)

            ln, b = pextract(ln, "{", "}", onlyone=True)

            if len(b) == 1 and b[0] == '/':   # convert ['/'] to '/' for lnExpand()
                l.append('/')
            else:
                l.append(b[0].split())

        ln = lnExpand(l, '%s Accent' % self.name)

        for l in ln:
            tt = []
            if len(l) // 2 * 2 != len(l):
                error("Use: %s Accent Beat Percentage [...]" % self.name)

            for b, v in zip(l[::2], l[1::2]):
                b = self.setBarOffset(b)
                v = stoi(v, "Beat offset must be a value, not '%s'" % v)
                if v < -100 or v > 100:
                    error("Velocity adjustment (as percentage) must "
                          "be -100..100, not '%s'" % v)

                tt.append((b, v / 100.))
            tmp.append(tt)

        self.accent = seqBump(tmp)

        if MMA.debug.debug:
            accList = []
            for s in self.accent:
                accList.append('{')
                for b, v, in s:
                    accList.append("%s %s" % (1 + (b / float(gbl.BperQ)), int(v * 100)))
                accList.append('}')
            dPrint("%s Accent: %s" % (self.name, ' '.join(accList)))

    def setArtic(self, ln):
        """ Set the note articuation value. """

        ln = lnExpand(ln, '%s Articulate' % self.name)
        ln = seqBump(ln)
        tmp = []
        incr = 0
        i = 0

        for n in ln:
            incr, n = getIncDec(n)
            a = stoi(n, "Expecting value in articulation setting")
            a = getIncDecValue(self.artic[i], incr, a)

            if self.vtype == 'PLECTRUM':
                if a < 0 or a > 500:
                    error("%s: Articulation setting must be 0 .. 500 (midi ticks), not %s" %
                          (self.name, a))
            else:
                if a < 1 or a > 500:
                    error("%s: Articulation setting must be 1..500, not %s" % (self.name, a))

                if a > 200:
                    warning("%s: Articulation '%s' is a large value." % (self.name, a))

            tmp.append(a)
            i += 1

        self.artic = seqBump(tmp)

        if MMA.debug.debug:
            dPrint("Set %s Articulate to: %s" % 
                  (self.name, ' '.join([str(a) for a in self.artic])))


    def setUnify(self, ln):
        """ Set unify. """

        ln = lnExpand(ln, "%s Unify" % self.name)
        tmp = []

        for n in ln:
            tmp.append(getTF(n, "Unify"))
                       
        self.unify = seqBump(tmp)

        if MMA.debug.debug:
            dPrint("Set %s Unify to: %s" %
              (self.name, ' '.join([str(a) for a in self.unify])))

    ##################################################
    ## Save/restore grooves

    def saveGroove(self, gname):
        """ Define a groove.

            Called by the 'DefGroove Name'. This is called for
            each track.

            If 'gname' is already defined it is overwritten.

            Note that tracks may have their own function for local/specific variables.
            They call here first to create storage, then do their own.
        """

        self.grooves[gname] = {
            'ACCENT': self.accent[:],
            'ARTIC': self.artic[:],
            'CHORD': copy.deepcopy(self.chord),
            'COMPRESS': self.compress[:],
            'DELAY': self.delay[:],
            'DIR': self.direction[:],
            'DUPROOT': copy.deepcopy(self.dupRoot),
            'HARMONY': (self.harmony[:], self.harmonyOnly[:], self.harmonyVolume[:]),
            'INVERT': copy.deepcopy(self.invert),
            'LIMIT': self.chordLimit[:],
            'RANGE': self.chordRange[:],
            'OCTAVE': self.octave[:],
            'RSKIP': self.rSkip[:],
            'RSKIPBEATS': self.rSkipBeats[:],
            'RTIME': copy.deepcopy(self.rTime),
            'RDURATION': copy.deepcopy(self.rDuration),
            'RVOLUME': copy.deepcopy(self.rVolume),
            'RPITCH': copy.deepcopy(self.rPitch),
            'SCALE': self.scaleType[:],
            'SEQ': self.sequence[:],
            'SEQRND': self.seqRnd,
            'SEQRNDWT': self.seqRndWeight[:],
            'STRUM': self.strum[:],
            'STRUMADD': self.strumAdd[:],
            'VOICE': self.voice[:],
            'VOLUME': self.volume[:],
            'UNIFY': self.unify[:],
            'MIDISEQ': self.midiSeq[:],
            'MIDIVOICE': self.midiVoice[:],
            'MIDICLEAR': self.midiClear[:],
            'SPAN': (self.spanStart, self.spanEnd),
            'MALLET': (self.mallet, self.malletDecay),
            'ORNAMENT': copy.deepcopy(self.ornaments)}

    def restoreGroove(self, gname):
        """ Restore a defined groove.

            Some tracks will override to restore their own variables. They
            then call back to this to finish the job.
        """

        if self.vtype != 'PLECTRUM' or MMA.patPlectrum.plectrumReset == True:
            self.doMidiClear()
            
        g = self.grooves[gname]

        self.sequence = g['SEQ']
        self.volume = g['VOLUME']
        self.accent = g['ACCENT']
        self.rTime = g['RTIME']
        self.rDuration = g['RDURATION']
        self.rVolume = g['RVOLUME']
        self.rPitch = g['RPITCH']
        self.rSkip = g['RSKIP']
        self.rSkipBeats = g['RSKIPBEATS']
        self.strum = g['STRUM']
        self.strumAdd = g['STRUMADD']
        self.octave = g['OCTAVE']
        self.voice = g['VOICE']
        self.harmony, self.harmonyOnly, self.harmonyVolume = g['HARMONY']
        self.direction = g['DIR']
        self.delay = g['DELAY']
        self.scaleType = g['SCALE']
        self.invert = g['INVERT']
        self.chord = g['CHORD']
        self.artic = g['ARTIC']
        self.seqRnd = g['SEQRND']
        self.seqRndWeight = g['SEQRNDWT']
        self.compress = g['COMPRESS']
        self.chordRange = g['RANGE']
        self.dupRoot = g['DUPROOT']
        self.chordLimit = g['LIMIT']
        self.unify = g['UNIFY']
        self.midiClear = g['MIDICLEAR']
        self.midiSeq = g['MIDISEQ']
        self.midiVoice = g['MIDIVOICE']
        self.spanStart, self.spanEnd = g['SPAN']
        self.mallet, self.malletDecay = g['MALLET']
        self.ornaments = g['ORNAMENT']

        # It's quite possible that the track was created after
        #  the groove was saved. This means that the data restored
        #  was just the default stuff inserted when the track
        #  was created ... which is fine, but the sequence size
        #  isn't necs. right. We can probably test any list, and octave[]
        #  is as good as any.

        if len(self.octave) != gbl.seqSize:
            self.setSeqSize()

    ####################################
    ## Sequence functions

    def clearSequence(self):
        """ Clear sequence for track.

            This is also called from __init__() to set the initial defaults for each track.

        """

        if self.vtype != 'SOLO' or not self.inited:
            if self.vtype == 'PLECTRUM':
                self.artic = [0]
            else:
                self.artic = [90]
            self.chord = [[]]
            self.sequence = [None]
            self.seqRnd = 0
            self.seqRndWeight = [1]
            self.scaleType = ['AUTO']
            self.rVolume = [[0, 0]]
            self.rPitch = None
            self.rSkip = [0]
            self.rSkipBeats = []
            self.rTime = [[0, 0]]
            self.rDuration = [[0, 0]]
            self.octave = [4 * 12]
            if self.vtype == 'DRUM':
                self.voice = [defaultDrum]
            else:
                self.voice = [defaultVoice]
            self.chordRange = [1]
            self.harmony = [None]
            self.harmonyOnly = [None]
            self.harmonyVolume = [.8]
            self.strum = [None]
            self.strumAdd = [0]
            self.volume = [MMA.volume.vols['M']]
            self.compress = [0]
            self.dupRoot = [[]]
            self.chordLimit = [0,0]
            self.invert = [[]]
            self.lastChord = []
            self.accent = [[]]
            self.unify = [0]
            self.midiClear = []
            self.midiSeq = []
            self.midiVoice = []
            self.spanStart = 0
            self.spanEnd = 127
            self.trigger = MMA.trigger.Trigger()
            self.mallet = 0
            self.malletDecay = 0
            self.futureVols = []
            self.direction = ['BOTH']
            self.delay = [0]

            # ornamentation
            self.ornaments = MMA.ornament.default()

            # for midinote (see midinote.py)
            self.transpose = 0   # transpose off=0, on=1
            self.useticks = 1   # offsets   beats=0, ticks=1  defaults to ticks
            self.tickdur = 1   # duration  notes=0, ticks=1  defaults to ticks
            self.articulate = 0   # honor articulate, defaults to Off
            self.tadjust = 0   # time adjustment factor
            self.vadjust = 1   # volume adjustment factor (percentage)
            self.oadjust = 0   # octave (12 pitches) adjustment

        if self.riff:
            if len(self.riff) > 1:
                warning("%s sequence clear deleting %s riffs" % (self.name, len(self.riff)))
            else:
                warning("%s sequence clear deleting unused riff" % self.name)

        self.riff = []

        self.setSeqSize()

    ############################
    ### Pattern functions
    ############################

    def definePattern(self, name, ln):
        """ Define a Pattern.

        All patterns are stored in pats{}. The keys for this
        are tuples -- (track type, pattern name).

        """

        name = name.upper()
        slot = (self.vtype, name)

        # This is just for the debug code

        if name.startswith('_'):
            redef = "dynamic define"
        elif slot in pats:
            redef = name + ' redefined'
        else:
            redef = name + ' created'

        if not self.vtype in ('SOLO', 'MELODY'):
            ln = ln.rstrip('; ')    # Delete optional trailing    ';' & WS

        pats[slot] = self.defPatRiff(ln)

        if MMA.debug.pshow:
            dPrint("%s pattern %s: %s" % (self.name.title(), redef,
                  self.formatPattern(pats[slot])))

    def dupRiff(self, ln):
        """ Duplicate an existing set of riffs from one solo track to another."""

        # Try to copy From another track to here.

        if ln and ln[0].upper() == 'FROM':
            if len(ln) != 2:
                error("%s DupRiff: FROM option needs exactly one track to copy from." 
                      % self.name)

            t = ln[1].upper()
            if not t in gbl.tnames:
                error("%s DupRiff: Source track '%s' does not exist." % (self.name, t))
            
            tr = gbl.tnames[t]
            
            if self.vtype != tr.vtype:
                error("%s DupRiff: Can't copy from %s, incompatible types (%s != %s)."
                          % (self.name, t, self.vtype, tr.vtype))

            if self.riff:
                error("%s DupRiff: This track had pending data." % self.name)

            if not tr.riff:
                error("%s DupRiff: Source track '%s' has no data to copy." %
                      (self.name, t))

            self.riff = copy.deepcopy(tr.riff)

            if MMA.debug.debug:
                dPrint("%s DupRiff copied from %s." % (self.name, t))

        else:
            if ln and ln[0].upper() == 'TO':  # Optional keyword
                ln = ln[1:]

            if not len(ln):
                error("%s DupRiff: No destination track specified.")

            if not self.riff:
                error("%s DupRiff: No data to copy." % self.name)

            for t in ln:
                t = t.upper()

                if not t in gbl.tnames:
                    error("%s DupRiff: Destination track %s does not exist."
                          % (self.name, t))

                tr = gbl.tnames[t]

                if self.vtype != tr.vtype:
                    error("%s DupRiff: Can't copy to %s, incompatible types (%s != %s)."
                          % (self.name, t, self.vtype, tr.vtype))

                if tr.riff:
                    error("%s DupRiff: Destination track %s has pending data."
                          % (self.name, tr.name))

                tr.riff = copy.deepcopy(self.riff)

                if MMA.debug.debug:
                    dPrint("%s DupRiff copied to %s." % (self.name, tr.name))

    def setRiff(self, ln):
        """ Define and set a Riff. """

        solo = self.vtype in ("MELODY", "SOLO")

        if solo:
            self.riff.append(ln)
        else:
            ln = ln.rstrip('; ')
            if len(ln) == 1 and (ln[0] in ('Z', 'z', '-')):
                self.riff.append([])
            else:
                self.riff.append(self.defPatRiff(ln))

        if MMA.debug.pshow:
            msg = ["%s Riff:" % self.name]
            if solo:
                msg.append(self.riff[-1])
            else:
                msg.append(self.formatPattern(self.riff[-1]))
            dPrint(' '.join(msg))


    def defPatRiff(self, ln):
        """ Worker function to define pattern. Shared by definePattern()
        and setRiff().
        """
        
        def mulPatRiff(oldpat, fact):
            """ Multiply a pattern. """

            fact = stoi(fact, "The multiplier arg must be an integer not '%s'" % fact)

            if fact < 1 or fact > 100:
                error("The multiplier arg must be in the range 2 to 100")

            """ Make N copies of pattern, adjusted so that the new copy has
                all note lengths and start times  adjusted.
                  eg: [[1, 2, 66], [3, 2, 88]]  * 2
                  becomes [[1,4,66], [2,4,88], [3,4,66], [4,4,88]].
            """

            new = []
            add = 0
            step = gbl.barLen // fact

            for n in range(fact):
                orig = copy.deepcopy(oldpat)
                for z in orig:
                    z.offset = (z.offset // fact) + add
                    z.duration //= fact
                    if z.duration < 1:
                        z.duration = 1

                    new.append(z)
                add += step

            return tuple(new)

        def shiftPatRiff(oldpat, fact):

            fact = stof(fact, "The shift arg must be a value, not '%s'" % fact)

            # Adjust all the beat offsets

            new = copy.deepcopy(oldpat)
            max = gbl.barLen
            for n in new:
                n.offset += fact * gbl.BperQ
                if n.offset < 0 or n.offset > max:
                    error("Pattern shift with factor %f has resulted in an "
                          "illegal offset" % fact)

            return tuple(new)

        ### Start of main function...

        # Convert the string to list...
        #  "1 2 3; 4 5 6" --->    [ [1,2,3], [4,5,6] ]

        p = []
        ln = ln.upper().split(';')
        for l in ln:
            p.append(l.split())

        plist = []

        for ev in p:
            more = []
            for i, e in enumerate(ev):
                if e in ('SHIFT', '*'):
                    if i == 0:
                        error("Pattern definition can't start with SHIFT or *")
                    more = ev[i:]
                    ev = ev[:i]
                    break

            if len(ev) == 1:
                nm = (self.vtype, ev[0])

                if nm in pats:
                    if nm[0].startswith('_'):
                        error("You can't use a pattern name beginning with an underscore")
                    pt = pats[nm]

                else:
                    error("%s is not an existing %s pattern" % (nm[1], nm[0].title()))

            else:
                pt = [self.getPgroup(ev)]

            while more:
                cmd = more.pop(0)
                if cmd not in ('SHIFT', '*'):
                    error("Expecting SHIFT or *, not '%s'" % cmd)

                if not more:
                    error("Expecting factor after %s" % cmd)
                if cmd == 'SHIFT':
                    pt = shiftPatRiff(pt, more.pop(0))
                elif cmd == '*':
                    pt = mulPatRiff(pt, more.pop(0))

            plist.extend(pt)

        plist.sort( key=lambda plist: plist.offset)

        if MMA.swing.mode:
            plist = MMA.swing.pattern(plist, self.vtype)

        return plist


    def formatPattern(self, pat):
        pp = []
        if not pat:
            return ' z '

        for p in pat:
            s = []
            s.append("%g" % (1 + (p.offset / float(gbl.BperQ))))
            if self.vtype != 'PLECTRUM':
                s.append("%st" % p.duration)

            if self.vtype == 'CHORD':
                for a in p.vol:
                    s.append("%g" % a)

            elif self.vtype == 'PLECTRUM':
                s.append("%s" % p.strum)
                for a in p.vol:
                    s.append("%g" % a)

            elif self.vtype == 'BASS':
                f = str(p.noteoffset + 1)

                if p.accidental == 1:
                    f += "#"
                elif p.accidental == -1:
                    f += "b"

                if p.addoctave > 0:
                    f += "+" * (p.addoctave // 12)
                elif p.addoctave < 0:
                    f += "-" * (p.addoctave // -12)

                s.append("%s %g" % (f, p.vol))

            elif self.vtype in ('ARPEGGIO', 'SCALE', 'DRUM', 'WALK'):
                s.append("%g " % p.vol)

            pp.append(' '.join(s))
        return "; ".join(pp)

    def insertVoice(self, sc):
        """ Called from bar() and setForceOut(). Adds voice stuff to track."""

        """ 1st pass for MIDIVOICE. There's a separate slot for
            each bar in the sequence, plus the data can be sent
            before or after 'voice' commands. This first loop
            sends MIDIVOICE data with an offset of 0. Note, we
            don't set the value for 'self.smidiVoice' until we
            do this again, later. All this is needed since some
            MIDIVOICE commands NEED to be sent BEFORE voice selection,
            and others AFTER.
        """

        if self.midiVoice:
            v = self.midiVoice[sc]
            if v and v != self.smidiVoice:
                for i in v:
                    if not i[0]:
                        gbl.mtrks[self.channel].addCtl(gbl.tickOffset, i[1])

        # Set the voice in the midi track if not previously done.

        v = self.voice[sc]
        if v != self.ssvoice:

            gbl.mtrks[self.channel].addProgChange(gbl.tickOffset, v, self.ssvoice)
            self.ssvoice = v

            # Mark ssvoice also in shared tracks

            for a in gbl.midiAssigns[self.channel]:
                try:
                    gbl.tnames[a].ssvoice = v
                except KeyError:
                    pass

            if MMA.debug.debug:
                if self.vtype == 'DRUM':
                    dPrint("%s Tone '%s' inserted at %s" % 
                           (self.name, MMA.midiC.valueToDrum(v) , gbl.tickOffset))
                else:
                    dPrint("%s Voice '%s' inserted at %s" % 
                           (self.name, MMA.midiC.valueToInst(v) , gbl.tickOffset))

        """ Our 2nd stab at MIDIVOICE. This time any sequences
            with offsets >0 are sent. AND the smidiVoice and midiSent
            variables are set.
        """

        if self.midiVoice:
            v = self.midiVoice[sc]
            if v and v != self.smidiVoice:
                for i in v:
                    if i[0]:
                        gbl.mtrks[self.channel].addCtl(gbl.tickOffset, i[1])
                self.smidiVoice = v
                self.midiSent = 1  # used by MIDICLEAR

    #########################
    ## Music processing
    #########################

    def bar(self, ctable):
        """ Process a bar of music for this track. """

        # Future vol == de(cresc). Done if track is on or off!

        if self.futureVols:
            self.volume = seqBump([self.futureVols.pop(0)])
        if self.futureVols:
            self.nextVolume = self.futureVols[0]
        else:
            self.nextVolume = None

        # If track is off don't do anything else.

        if self.disable:
            if self.riff:
                self.riff.pop(0)
            return

        """ Decide which seq to use. This is either the current
            seqCount, or if SeqRnd has been set for the track
            it is a random pattern in the sequence.

            The class variable self.seq is set to the sequence to use.
        """

        if self.seqRnd:
            self.seq = MMA.seqrnd.getrndseq(self.seqRndWeight)
        else:
            self.seq = gbl.seqCount

        sc = self.seq

        # Get pattern for this sequence. Either a Riff, Pattern or trigger
        if self.riff:
            pattern = self.riff.pop(0)
        else:
            pattern = self.sequence[sc]
            if self.trigger.mode:
                pattern = MMA.trigger.makeTriggerSequence(self, ctable, pattern)
                if not pattern and self.trigger.override:
                    pattern = self.sequence[sc]
            if not pattern:
                return

        """ MIDI Channel assignment. If no channel is assigned try
            to find an unused number and assign that.
        """

        if not self.channel:
            self.setChannel()

        MMA.midifuncs.doChannelInit(self.channel, self.name)

        # If there is track specific chord data, substitute it for the ctable
        # data already passed.

        if self.chord[sc]:
            ctable = MMA.parse.parseChordLine(self.chord[sc])

        # We are ready to create musical data. 1st do pending midi commands.
        # It probably doesn't matter if we do this now or later??? 

        self.clearPending()

        # This absolutely needs to be done BEFORE any note ON stuff!
        self.insertVoice(sc)

        # Do MIDISeq for this voice

        if self.midiSeq:
            l = self.midiSeq[sc]
            if l:
                for i in l:
                    gbl.mtrks[self.channel].addCtl(getOffset(i[0]), i[1])
                self.midiSent = 1

        # Special for TRUNCATE. If bar(s) are being truncated patterns
        # need to be resized to fit the new size. (Note: SOLO patterns
        # are not touched since they are not yet compiled. They will error 
        # if they are too long!!)
        # We use the 'side' and 'length' settings to figure out where
        # to start/end slicing the pattern.
        # NOTE: use a deepcopy of the pattern!

        if MMA.truncate.length and self.vtype not in ("SOLO", "MELODY"):
            new = []
            pstart = MMA.truncate.side
            pend = pstart + MMA.truncate.length

            # Go though original pattern and duplicate events (with
            # adjusted offsets) for the new beats. Note that the size/len
            # of pattern is NOT related to the seqsize!

            for a in copy.deepcopy(pattern):
                if a.offset >= pstart and a.offset < pend:
                    a.offset -= pstart
                    new.append(a)

            pattern = new # replace existing pattern with newly created one.

        if pattern:
            self.trackBar(pattern, ctable)

    def clearPending(self):
        self.midiPending.sort()  # probably not needed, but it's cheap insurance
        while self.midiPending:
            c, off, v = self.midiPending.pop(0)

            if c == 'TNAME':
                gbl.mtrks[self.channel].addTrkName(off, v)
                if MMA.debug.debug:
                    dPrint("%s Track name inserted at offset %s" % 
                          (self.name, off))

            elif c == 'GLIS':
                gbl.mtrks[self.channel].addGlis(off, v)
                if MMA.debug.debug:
                    dPrint("%s Glis at offset %s set to %s" % 
                          (self.name, off, ord(chr(v))))

            elif c == 'PAN':
                gbl.mtrks[self.channel].addPan(off, v)
                if MMA.debug.debug:
                    dPrint("%s Pan at offset %s set to %s" % 
                          (self.name, off, v))

            elif c == 'CVOLUME':
                gbl.mtrks[self.channel].addChannelVol(off, v)
                if MMA.debug.debug:
                    dPrint("%s ChannelVolume at offset %s set to %s" % 
                          (self.name, off, v))

            elif c == 'MIDITEXT':
                gbl.mtrks[self.channel].addText(off, v)
                if MMA.debug.debug:
                    dPrint("%s MidiText inserted at %s." % (self.name, off))

            elif c == 'MIDICUE':
                gbl.mtrks[self.channel].addCuePoint(off, v)
                if MMA.debug.debug:
                    dPrint("%s MidiCue inserted at %s." % (self.name, off))

            elif c == 'WHEEL':
                gbl.mtrks[self.channel].addWheel(off, v)
                if MMA.debug.debug:
                    dPrint("%s Wheel inserted at %s." % (self.name, off))

            else:
                error("Unknown midi command pending. Call Bob")

    def getChordInPos(self, offset, ctabs):
        """ Compare an offset to a list of ctables and return
            the table entry active for the given beat.

            The chord start/end offsets generated by parseChordLine() will be in
            the range 0... (BperQ*QperBar). So, negative offset in patterns need
            to be reset to 0; and a hit at the end of the bar could be missed if we
            don't assume that anything out-of-range is in the last chord. Sort of
            ugly, but it's quick and it works.

            Returns a CTable structure.
        """

        for c in ctabs:
            if offset < c.chEnd:
                break
        self.currentChord = c  # for others who might need chord (RPITCH)
        
        return c

    def adjustVolume(self, v, beat):
        """ Adjust a note volume based on the track and global volume
            setting. This is an expensive operation applied to each
            and every generated note.
        """

        # If the volume (velocity) is OFF, just return OFF
        if not v:
            return 0

        sc = self.seq

        # Random skip and random skipbeats, return OFF
        if self.rSkip[sc] and (not self.rSkipBeats or beat in self.rSkipBeats) \
                and random.random() < self.rSkip[sc]:
            return 0

        # If the track is set to OFF, return OFF
        trackAdjust = self.volume[sc]
        if not trackAdjust:
            return 0

        # single bar cresc adjust, adjust track volume adjuster value
        if self.nextVolume: 
            bt = beat
            if bt < 1:  # might have negative offsets, cres code ignores
                bt = 0
            trackAdjust += (self.nextVolume - trackAdjust) * \
                bt / gbl.barLen

        trackAdjust *= MMA.volume.vTRatio

        fullAdjust = MMA.volume.volume

        # Is everything off?
        if not fullAdjust:
            return 0

        # global single bar cresc adjust
        if MMA.volume.nextVolume:
            bt = beat
            if bt < 1:  # might have negative offsets, cres code ignores
                bt = 0
            fullAdjust += (MMA.volume.nextVolume - fullAdjust) * \
                bt / gbl.barLen

        fullAdjust *= MMA.volume.vMRatio

        v *= (trackAdjust + fullAdjust)

        for b, a in self.accent[sc]:
            if b == beat:
                v += (v * a)

        # Random volume adjustment
        if self.rVolume[sc]:
            trackAdjust = int(v * self.rVolume[sc][0])
            fullAdjust = int(v * self.rVolume[sc][1])
            if trackAdjust or fullAdjust:
                if fullAdjust < trackAdjust:
                    trackAdjust, fullAdjust = fullAdjust, trackAdjust
                v += random.randrange(trackAdjust, fullAdjust)

        # normalize
        if v > 127:
            v = 127
        elif v < 1:
            v = 1

        # all was done in fp, don't forget to round!
        return int(v)

    def adjustNote(self, n):
        """ Adjust a note for a given octave/transposition.
            Ensure that the note is in range.
        """

        n += self.octave[self.seq] + gbl.transpose

        while n < self.spanStart:  # spanStart will be 0 from init
            n += 12
        while n > self.spanEnd:  # spanEnd will be 127 from init
            n -= 12

        return n


    def setBarOffset(self, v, emsg=''):
        """ Convert a string into a valid bar offset in midi ticks. """

        m = v.find('-')
        p = v.find('+')

        # determine split point and sign
        if m > -1 and p > -1:  # both - and +, get lowest
            if m > p:
                sp = p
                sign = 1
            else:
                sp = m
                sign = -1

        elif m > -1:   # only -, easy
            sp = m
            sign = -1

        elif p > -1:  # only +, easy
            sp = p
            sign = 1

        else:
            sp = None  # easier, no split

        if sp:   # get offset, and note length modifier
            note = v[sp + 1:]
            v = v[:sp]
            notepart = MMA.notelen.getNoteLen(note) * sign
        else:
            notepart = 0

        v = stof(v, "%sValue for %s bar offset must be integer/float, not '%s'" %
                 (emsg, self.name, v))
        v = ((v - 1) * gbl.BperQ) + notepart

        if v < 0:
            if v < -gbl.BperQ:
                error("%sValue for %s bar offset must be 0 or greater, not '%s'" %
                      (emsg, self.name, v/gbl.BperQ+1))
            else:
                warning("Offset in '%s' is '%s ticks' before bar start!" % (self.name, -v))

        if v >= gbl.barLen:
            error("%sValue for %s bar offset must be less than %s, not '%s'." %
                  (emsg, self.name, gbl.QperBar + 1, v/gbl.BperQ+1))

        return int(v)

    def getDur(self, d):
        """ Return the adjusted duration for a note.

            Articulate and RDuration are used.
        """

        sc = self.seq

        d = (d * self.artic[sc]) // 100

        if self.rDuration[sc]:
            a1 = int(d * self.rDuration[sc][0])
            a2 = int(d * self.rDuration[sc][1])
            if a1 or a2:
                d += random.randrange(a1, a2)
        if d <= 0:
            d = 1   # force a value if we end with 0 or less.

        return int(d)

    def sendNote(self, offset, duration, note, velocity):
        """ Send a note to the MIDI machine. This is called from all
            track classes and handles niceties like mallet-repeat, rpitch
            and delay.
        """

        if not velocity:
            return

        sc = self.seq

        if self.rPitch:
            note = MMA.rpitch.doRpitch(self, offset, note)
        rptr = self.mallet
        if rptr and duration > rptr:
            ll = self.getDur(rptr)
            offs = 0
            vel = velocity
            for q in range(duration // rptr):
                gbl.mtrks[self.channel].addPairToTrack(
                    offset + offs + self.delay[sc],
                    self.rTime[sc][0], self.rTime[sc][1],
                    ll,
                    note,
                    vel,
                    None)

                offs += rptr
                if self.malletDecay:
                    vel = int(vel + (vel * self.malletDecay))
                    if vel < 1:
                        vel = 1
                    if vel > 127:
                        vel = 127

        else:
            gbl.mtrks[self.channel].addPairToTrack(
                offset + self.delay[sc],
                self.rTime[sc][0], self.rTime[sc][1],
                duration,
                note,
                velocity,
                self.unify[sc])

    def sendChord(self, chord, duration, offset):
        """ Send a chord to midi with strum delay. Called
            from Chord, Bass, Walk, Arpeggio and Scale.

            chord = list of [note, volume]s
            p = pattern for current beat

            This compensates out the strum value so that the additional (harmony)
            notes all end at the same time.

            Adjusts the RDURATION setting.
        """

        sc = self.seq
        strumAdjust = self.getStrum(sc)
        strumAdd = self.strumAdd[sc]

        if strumAdjust:
            minDuration = duration // 3
            if minDuration < gbl.Bper128:   # this is 12 ticks
                minDuraiton = gbl.Bper128

        strumOffset = 0  # 1st note in list is not offset-strummed

        duration = self.getDur(duration)
        for n, vol in chord:
            self.sendNote(
                int(offset + strumOffset),
                duration,
                self.adjustNote(n),
                self.adjustVolume(vol, offset))

            if strumAdjust:
                strumAdjust += strumAdd
                strumOffset += strumAdjust
                duration -= strumAdjust
                if duration < minDuration:
                    duration = minDuration

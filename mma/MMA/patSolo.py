# patSolo.py

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

import MMA.notelen
import MMA.translate
import MMA.harmony
import MMA.volume
import MMA.alloc
import MMA.swing
import MMA.truncate

from . import gbl

from MMA.common import *
from MMA.pat import PC, Pgroup
from MMA.keysig import keySig
import MMA.debug

import re
import random


# Each note in a solo gets a NoteEvent.
class NoteEvent:
    def __init__(self, pitch, velocity, isgrace):
        self.duration = None
        self.pitch = pitch
        self.articulation = None
        self.velocity = velocity
        self.defvelocity = velocity
        self.isgrace = isgrace             # signal grace note, no harmony and change offset

accValues = {'#': 1, "&": -1, 'n': 0}

# used when extracting solo notes.
defaultVelocity = 90

##############################


class Melody(PC):
    """ The melody and solo tracks are identical, expect that
        the solo tracks DO NOT get saved in grooves and are only
        initialized once.
    """

    vtype = 'MELODY'
    drumType = None

    endTilde = []
    drumTone = 38
    arpRate = 0
    arpDecay = 0
    arpDirection = 'UP'
    stretch = 1
    followChord = 0
    followKey = 1
    rootChord = 0   # start off with a C chord as default

    def __init__(self, ln):
        """ We need special init here incase this is converted to drumType.
            If we don't have a toneList, we're screwed.
        """

        self.toneList = [self.drumTone]
        PC.__init__(self, ln)   # This order is important!

    def setDrumType(self):
        """ Set this track to be a drum track. """

        if self.channel:
            error("You cannot change a track to DRUM once it has been used")

        self.drumType = 1
        self.setChannel('10')  # MMA assumes all drums are on channel 10
        self.voice = seqBump([MMA.pat.defaultDrum])
        
    def setVoicing(self, ln):
        """ Set the voicing option for a solo/melody track. Only permitted
            option is FOLLOWCHORD.
        """

        notopt, ln = opt2pair(ln, toupper=True)

        if notopt:
            error("Voicing %s: Each option must be a OPT=VALUE pair." % self.name)

        for opt, val in ln:
            if opt == 'FOLLOWCHORD':
                if val in ('0', 'OFF'):
                    val = None
                elif val in ('1', 'ON'):
                    val = 1
                else:
                    error("%s Voicing FollowChord: expecting On or Off." % self.name)
                self.followChord = val

            elif opt == 'FOLLOWKEY':
                if val in ('0', 'OFF'):
                    val = None
                elif val in ('1', 'ON'):
                    val = 1
                else:
                    error("%s Voicing FollowKey: expecting On or Off." % self.name)

                self.followKey = val

            elif opt == 'ROOT':
                try:
                    self.rootChord = MMA.chords.cdAdjust[val.upper()]
                except KeyError:
                    error("Voicing %s: Chord name %s not valid." % (self.name, val))

            else:
                error("Voicing %s: Only valid options are 'FollowChord', 'FollowKey' and 'Root'."
                      % self.name)

    def formatPattern(self, pat):
        """ Format an existing pattern. Overrides class def! """

        if not pat:
            return ''
        else:
            return pat

    def saveGroove(self, gname):
        """ Save special/local variables for groove. """

        PC.saveGroove(self, gname)  # create storage. Do this 1st.
        self.grooves[gname]['FOLLOWCHORD'] = self.followChord
        self.grooves[gname]['FOLLOWKEY'] = self.followKey
        self.grooves[gname]['ROOT'] = self.rootChord
        self.grooves[gname]['TONES'] = self.toneList[:]

    def restoreGroove(self, gname):
        """ Restore special/local/variables for groove. """

        self.followChord = self.grooves[gname]['FOLLOWCHORD']
        self.followKey = self.grooves[gname]['FOLLOWKEY']
        self.rootChord = self.grooves[gname]['ROOT']
        self.toneList = self.grooves[gname]['TONES']
        PC.restoreGroove(self, gname)

    def setSeqSize(self):
        """ Expand existing pattern list. """

        self.toneList = seqBump(self.toneList)
        PC.setSeqSize(self)

    def clearSequence(self):
        """ Set some initial values. Called from init and clear seq. """

        PC.clearSequence(self)
        self.toneList = seqBump([self.drumTone])

    def defPatRiff(self, ln):
        """ Create a solo pattern. This is used for solo sequenes only.

            All we do is to return the string set as a pattern. Pretty simple.

        """

        return ln

    def setStretch(self, ln):
        """ Set a stretch (or compress) value for each note set in a solo. """

        s = stof(ln[0])

        if s < 1 or s > 500:
            error("%s Stretch: value must be a percentage in range 1 to 500, not '%s'"
                  % (self.name, s))

        self.stretch = s / 100.

    def setArp(self, ln):
        """ Set the arpeggiate options. """

        if len(ln)==1 and ln[0].upper()=='OFF':
            ln[0] = "Rate=0"
        
        notopt, ln = opt2pair(ln, 1)

        if notopt:
            error("%s Arpeggiate: expecting cmd=opt pairs, not '%s'."
                  % (self.name, ' '.join(notopt)))

        for cmd, opt in ln:
            if cmd == 'RATE':
                if opt == '0' or opt == 'NONE':
                    self.arpRate = 0
                else:
                    self.arpRate = self.getNoteLen(opt)

            elif cmd == 'DECAY':
                v = stof(opt, "Arpeggiate Decay must be a value, not '%s'" % opt)
                if v < -50 or v > 50:
                    error("%s Arpeggiate: Decay rate must be -50..+50" %
                          self.name)
                self.arpDecay = v / 100

            elif cmd == 'DIRECTION':
                valid = ("UP", "DOWN", "BOTH", "RANDOM")
                if opt not in valid:
                    error("%s Arpeggiate Direction: Unknown setting '%s', use %s."
                          % (self.name, opt, ', '.join(valid)))
                self.arpDirection = opt

        if MMA.debug.debug:
            dPrint("%s Arpeggiate: Rate=%s Decay=%s Direction=%s" % 
                  (self.name, self.arpRate, self.arpDecay, self.arpDirection))

    def getNoteLen(self, n):
        """ This is a special interface to MMA.notelen.getNoteLen() which
            adjusts the length (in MIDI ticks) by the "stetch" value for
            this class.
        """

        return MMA.notelen.getNoteLen(n) * self.stretch

    def restart(self):
        self.ssvoice = -1

    def setTone(self, ln):
        """ A solo track can have a tone, if it is DRUMTYPE."""

        if not self.drumType:
            error("You must set a Solo track to DrumType before setting Tone")

        if len(ln) > 1:
            error("Only 1 value permitted for Drum Tone in Solo tracks")

        self.drumTone = MMA.translate.dtable.get(ln[0])

    def getChord(self, c, velocity, isdrum, isgrace):
        """ Extract a set of notes for a single beat.

            This is a function just to make getLine() a bit shorter
            and more readble.
        """

        c = re.split("[, ]+", c)

        if not c:
            error("You must specify the first note in a solo line")

        """ Convert the note part into a series of midi values
            Notes can be a single note, or a series of notes. And
            each note can be a letter a-g (or r), a '#,&,n' plus
            a series of '+'s or '-'s. Drum solos must have each
            note separated by ' ' or ','s: "Snare1,KickDrum1,44".

            Each chunk could be:
             - a midi value (44)
             - a drum note ( KickDrum1)
             - a single note (g#) (g&-)
             - Or groups with spaces/commas (f 100) (44 , KickDrum) (a,b c)
        """

        events = []   # array for each note event

        for cc in c:
            if not cc or not cc[0]:
                continue
            if '/' in cc:
                if cc.count('/') > 1:
                    error("%s: Only 1 '/velocity' permitted. You can separate "
                          "notes in the chord with ',' or ' ' and it'll work." %
                          self.name)
                cc, newvel = cc.split('/')
                if not newvel:
                    error("%s: expecting 'volume' after '/'" % self.name)

                if not cc:
                    error("%s: Volume '/' must immediately follow note." % self.name)

                thisvel = stoi(newvel)

                if thisvel < 0 or thisvel > 127:
                    error("%s: Velocity must be 0..127, not '%s'." % (self.name, newvel))
            else:
                thisvel = velocity

            if cc[0] == 'r':
                if isgrace:
                    warning("%s: Grace note is a rest (ignored)." % self.name)

                if events or len(cc) > 1:
                    error("%s: Rests and notes cannot be combined." % self.name)
                else:
                    events.append(NoteEvent(None, 0, isgrace))  # note event with no pitch

            elif cc[0] in "1234567890":
                n = stoi(cc, "%s: Note values must be integer or literal." %
                         self.name)
                if n < 0 or n > 127:
                    error("%s: Midi notes must be 0..127, not '%s'" %
                          (self.name, n))

                # if using value we fake-adjust octave,
                # it (and transpose) is set later.

                if not isdrum:
                    n -= self.octave[self.seq]

                events.append(NoteEvent(n, thisvel, isgrace))

            elif isdrum:       # drum must be a value, * or drum-name
                if cc == '*':
                    events.append(NoteEvent(self.drumTone, thisvel, isgrace))
                else:
                    events.append(NoteEvent(int(MMA.translate.dtable.get(cc)), thisvel, isgrace))

            else:   # must be a note(s) in std. notation
                cc = list(cc)
                while cc:
                    name = cc.pop(0)

                    if not name in self.midiNotes:
                        error("%s: Encountered illegal note name '%s'"
                              % (self.name, name))

                    n = self.midiNotes[name]  # name is string, n is value

                    # Parse out a "#', '&' or 'n' accidental.

                    if cc and cc[0] in accValues:
                        i = cc.pop(0)
                        self.acc[name] = accValues[i]

                    n += self.acc[name]  # accidental adjust (from above or keysig)

                    # Parse out +/- (or series) for octave

                    while cc and cc[0] in '+-':
                        a = cc.pop(0)
                        if a == '+':
                            n += 12
                        else:
                            n -= 12

                    events.append(NoteEvent(n, thisvel, isgrace))

        return events

    def getLine(self, pat):
        """ Extract a melodyline for solo/melody tracks.

            This is only called from trackbar(), but it's nicer
            to isolate it here.


            RETURNS: notes structure. This is a dictionary. Each key represents
                     an offset in MIDI ticks in the current bar. The data for
                     each entry is an array of note events:

                 notes[offset] - [nev [,...] ] See top of file for noteEvent()
                                  class which sets the fields.
        """

        sc = self.seq

        """ Get a COPY of the keysignature note table (a dict).
            As a bar is processed the table is updated. There is one difference
            here---in real music an accidental for a note in a given octave does
            not effect the following same-named notes in different octaves.
            In this routine IT DOES.

            FollowKey=Off is usually (user) set when using a sequence pattern.
        """

        if self.followKey:   # this is the default
            self.acc = keySig.accList.copy()
        else:    # disable the feature. Useful for sequence patterns!
            self.acc = {'a': 0, 'c': 0, 'b': 0, 'e': 0, 'd': 0, 'g': 0, 'f': 0}

        # list of notename to midivalues

        self.midiNotes = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11, 'r': None}

        """ The initial string is in the format "1ab;4c;;4r;". The trailing
            ';' is important and needed. If we don't have this requirement
            we can't tell if the last note is a repeat of the previous. For
            example, if we have coded "2a;2a;" as "2a;;" and we didn't
            have the 'must end with ;' rule, we end up with "2a;" and
            then we make this into 2 notes...or do we? Easiest just to
            insist that all bars end with a ";".
        """

        if not pat.endswith(';'):
            error("All Solo strings must end with a ';'")

        # Get the end of the bar in ticks. If we're doing a truncate
        # use the temporary bar length, otherwise figure it out.

        if MMA.truncate.length:
            barEnd = MMA.truncate.length
        else:
            barEnd = gbl.barLen

        duration = self.getNoteLen('4')    # default note length
        velocity = defaultVelocity         # intial/default velocity for solo notes
        articulation = 1            # additional articulation for solo notes

        notes = {}   # NoteEvent list, keys == offset

        if self.drumType:
            isdrum = 1
            lastc = str(self.drumTone)
        else:
            isdrum = None
            lastc = ''             # last parsed note

        # convert pat to a list
        pat = [x.strip() for x in pat.split(';')[:-1]]

        # set initial offset into bar. This compensates for the previous
        # bar ending in a ~ and this one starting with ~.
        # This special case bumps the initial bar offset

        if pat[0].startswith("~"):
            if not self.endTilde or self.endTilde[1] != gbl.tickOffset:
                error("Previous line did not end with '~'")
            else:
                pat[0] = pat[0][1:].strip()
                offset = self.endTilde[0]
        else:
            offset = 0

        lastOffset = None

        # Strip off trailing ~. This permits long notes to end past the
        # current barend. Note, flag set for the next bar to test for
        # a leading ~.

        if pat[-1].endswith("~"):
            self.endTilde = [1, gbl.tickOffset + barEnd]
            pat[-1] = pat[-1][:-1].strip()
        else:
            self.endTilde = []

        ##################################################
        # Now we can parse each chunk of the solo string.

        for a in pat:
            """ If we find a "<>" we just ignore that. It's useful when
                multiple continuation bars are needed with ~.
            """

            accentVol = None
            accentDur = None
            isgrace = False

            if a == '<>':
                continue

            """ Next, strip out all '<SPECIAL=xx>' settings.

              VOLUME: If no option is set, we assume VOLUME. The default
                      velocity setting was set before the loop (==90) and is
                      changed here for the duration of the current bar/riff.
                      The set velocity will still be modified by the global
                      and track volume adjustments.

              DURATION: Duration or articulation setting is defaulted to 100.
                        Changing it here will do so for the duration of the
                        bar/riff. Note, the track ARTICULATION is still applied.

              ISGRACE: grace note indication and offset. Offset is optional.

              OFFSET: change the current offset into the bar. Can be negative
                      which forces overlapping notes.

            """

            a, vls = pextract(a, "<", ">")

            if vls:
                if len(vls) > 1:
                    error("Only 1 <modifier> is permitted per note-set")

                vls = vls[0].split(',')
                for vv in vls:

                    vv = vv.upper().strip()

                    # We have an default offset for grace notes of 2.
                    # So, if what have a GRACE without a offset, convert
                    # the command to that.
                    if vv == 'GRACE':
                        vv = 'GRACE=2'

                    if not '=' in vv:
                        vv = "VOLUME=" + vv

                    vc, vo = vv.split('=', 1)  # note: it's already uppercase!

                    if vc == 'VOLUME':
                        if vo in MMA.volume.vols:   # arg was a volume 'FF, 'mp', etc.
                            velocity = defaultVelocity * MMA.volume.vols[vo]
                        else:
                            error("%s: No volume '%s'." % (self.name, vo))

                    elif vc == 'GRACE':
                        isgrace = stof(vo, "%s: Expecting a value, not %s." % (self.name, vo))
                        if isgrace <= 0:
                            error("%s: Offset modifier must be greater than 0."
                                  % self.name)

                    elif vc == 'OFFSET':
                        offset = stoi(vo, "%s: Offset expecting integer, not %s."
                                      % (self.name, vo))

                        if offset < 0:
                            error("%s: Offset must be positive." % self.name)

                        if offset >= barEnd:
                            error("%s: Offset has been set past the end of the bar."
                                  % self.name)

                    elif vc == 'ARTICULATE':
                        articulation = stoi(vo, "%s: Articulation expecting integer,"
                                            " not %s." % (self.name, vo))

                        if articulation < 1 or articulation > 200:
                                error("%s: Articulation must be 1..200, not %s." %
                                      (self.name, vo))
                        articulation /= 100.

                    else:
                        error("%s: Unknown command '%s'." % (self.name, vv))

            if offset >= barEnd:
                error("Attempt to start Solo note '%s' after end of bar" % a)

            """ Split the chord chunk into a note length and notes. Each
                part of this is optional and defaults to the previously
                parsed value.
            """

            i = 0
            while i < len(a):
                if not a[i] in '1234567890.+-tT:':
                    break
                else:
                    i += 1

            if i:
                duration = self.getNoteLen(a[0:i].replace(' ', ''))
                a = a[i:].strip()

            # next item might be an accent string.

            i = 0
            while i < len(a):
                if not a[i] in "!-_^&":
                    break
                else:
                    i += 1

            if i:
                c = a[0:i]
                accentVol = 1
                accentDur = 1

                accentDur -= c.count('!') * .2
                accentDur += c.count('-') * .2
                accentDur += c.count('_') * .2
                accentVol += c.count('^') * .2
                accentVol -= c.count('&') * .2

                if accentDur < .1:
                    accentDur = .1
                if accentDur > 2:
                    accentDur = 2
                if accentVol < .1:
                    accentVol = .1
                if accentVol > 2:
                    accentVol = 2
                a = a[i:]

            # Now we get to look at pitches.

            if not a or a == '' or a == ' ':
                a = lastc
            evts = self.getChord(a, velocity, isdrum, isgrace)  # get chord

            if not evts:
                error("No pitches specifed for notes.")

            for e in evts:
                e.velocity = self.adjustVolume(e.defvelocity, offset)
                if accentVol:
                    e.velocity *= accentVol
                e.duration = duration

                if accentDur:
                    e.articulation = articulation * accentDur
                else:
                    e.articulation = articulation

            lastc = a     # save last chord for next loop

            # add note event(s) to note{}
            if not offset in notes:
                notes[offset] = []
            notes[offset].extend(evts)

            lastOffset = offset

            if not e.isgrace:
                offset += duration

        if offset <= barEnd:
            if self.endTilde:
                error("Tilde at end of bar has no effect")

        else:
            if self.endTilde:
                self.endTilde[0] = offset - barEnd
            else:
                warning("%s, end of last note overlaps end of bar by %g "
                        "beat(s)." % (self.name, (offset - barEnd) / float(gbl.BperQ)))

        if MMA.swing.mode:
            notes = MMA.swing.swingSolo(notes)

 
        return notes

    def followAdjust(self, notes, ctable):
        """ Convert pitches to reflect current chord. """

        sc = self.seq

        for offset in notes:
            nn = notes[offset]

            if len(nn) == 1 and nn[0].pitch is not None:
                tb = self.getChordInPos(offset, ctable)

                if tb.chordZ:
                    continue

                nn[0].pitch += (tb.chord.rootNote + self.rootChord)

        return notes

    def addHarmony(self, notes, ctable):
        """ Add harmony to solo notes. We need to be careful
            since the chords can contain grace and NULL notes.
        """

        sc = self.seq

        harmony = self.harmony[sc]
        harmOnly = self.harmonyOnly[sc]

        for offset in notes:
            nn = notes[offset]

            pitch = None
            count = 0
            for n in nn:
                if n.isgrace or n.pitch is None:
                    continue
                pitch = n.pitch
                duration = n.duration
                articulation = n.articulation
                velocity = n.defvelocity
                count += 1  # signals multiple notes, don't harmonize

                if harmOnly:
                    n.pitch = None

            # The chord might have no notes, have more than one, or be all grace
            if pitch is None or count != 1:
                continue

            tb = self.getChordInPos(offset, ctable)

            if tb.chordZ:
                continue

            h = MMA.harmony.harmonize(harmony, pitch, tb.chord.bnoteList)

            for n in h:
                e = NoteEvent(n,
                        self.adjustVolume(velocity * self.harmonyVolume[sc], offset),
                        False)
                e.duration = duration
                e.articulation = articulation
                nn.append(e)

    def trackBar(self, pat, ctable):
        """ Do the solo/melody line. Called from self.bar() """

        sc = self.seq

        notes = self.getLine(pat)

        # adjust all the notes for the given chord if we are in "FOLLOW CHORD" mode.

        if self.followChord and not self.drumType:
            notes = self.followAdjust(notes, ctable)

        if self.harmony[sc] and not self.drumType:
            self.addHarmony(notes, ctable)

        unify = self.unify[sc]

        rptr = self.mallet

        for offset in sorted(notes.keys()):
            nn = notes[offset]
            
            # the "None" test is important. Arp doesn't like rests.
            if self.arpRate and nn[0].pitch is not None:
                self.trackArp(nn, offset)
                continue

            # For each chord we process 2x. First time finds all the grace
            # notes and sends them to the midi machine; 2nd time normal notes.
            # Has to be done this was so we don't force grace note adjustments
            # (durations) onto normal notes. Grace notes ignore strum!

            # grace
            for nev in nn:
                n = nev.pitch
                if n is None or not nev.isgrace:     # skip rests and non-grace
                    continue

                if not self.drumType:        # no octave/transpose for drums
                    n = self.adjustNote(n)

                # Note that each grace note has it's own offset and duration
                self.sendNote(int(offset - (nev.duration // nev.isgrace)),
                              self.getDur(int(nev.duration * nev.articulation)),
                              n, int(nev.velocity))

            # normal notes.

            strumAdjust = self.getStrum(sc)
            strumAdd = self.strumAdd[sc]
            strumOffset = 0

            dur = None  # default duration for notes in chord

            for nev in nn:
                n = nev.pitch
                if n is None or nev.isgrace:     # skip rests and grace
                    continue

                if not self.drumType:        # no octave/transpose for drums
                    n = self.adjustNote(n)

                off = offset + strumOffset
                
                # Set duration for this chord. Only do it once so they are
                # all the same length. The call to getDur() adjusts for RDURATION.
                if dur is None:
                    dur = self.getDur(int(nev.duration * nev.articulation))

                self.sendNote(off, dur, n, int(nev.velocity))

                strumAdjust += strumAdd
                strumOffset += strumAdjust

    def trackArp(self, nn, offset):
        """ Special trackbar() for arpeggiator. """

        if self.drumType:
            error("%s Arpeggiate: Incompatible with DRUMTYPE. Try MALLET?" % self.name)

        notes = [[self.adjustNote(x.pitch), x.velocity] for x in nn]
        notes.sort()

        random = self.direction == 'RANDOM'

        if self.arpDirection == "DOWN":
            notes.reverse()

        elif self.arpDirection == "BOTH":
            z = notes[:]
            z.reverse()
            notes.extend(z[1:-1])

        duration = self.arpRate             # duration of each note
        count = nn[0].duration // duration   # total number to play
        if count < 1:
            count = 1

        while 1:
            nn = range(len(notes))
            if random:
                random.randomize(nn)
            for i in nn:
                n = notes[i]

                self.sendNote(offset,
                              self.getDur(duration), n[0],
                              self.adjustVolume(n[1], offset))
                count -= 1
                if not count:
                    break

                offset += duration

                if self.arpDecay:
                    n[1] = int(n[1] + (n[1] * self.arpDecay))
                    if n[1] < 1:
                        n[1] = 1
                    if n[1] > 127:
                        n[1] = 127

            if not count:
                break


class Solo(Melody):
    """ Pattern class for a solo track. """

    vtype = 'SOLO'

    # Grooves are not saved/restored for solo tracks.

    def restoreGroove(self, gname):
        self.setSeqSize()

    def saveGroove(self, gname):
        pass

    def forceRestoreGroove(self, gname):
        PC.restoreGroove(self, gname)

    def forceSaveGroove(self, gname):
        PC.saveGroove(self, gname)

#######################

""" When solos are included in a chord/data line they are
    assigned to the tracks listed in this list. Users can
    change the tracks with the setAutoSolo command.
"""

autoSoloTracks = ['SOLO', 'SOLO-1', 'SOLO-2', 'SOLO-3']


def setAutoSolo(ln):
    """ Set the order and names of tracks to use when assigning
        automatic solos (specified on chord lines in {}s).
    """

    global autoSoloTracks

    if not len(ln):
        error("You must specify at least one track for autosolos")

    autoSoloTracks = []
    for n in ln:
        n = n.upper()
        MMA.alloc.trackAlloc(n, 1)
        if gbl.tnames[n].vtype not in ('MELODY', 'SOLO'):
            error("All autotracks must be Melody or Solo tracks, not %s"
                  % gbl.tnames[n].vtype)

        autoSoloTracks.append(n)

    if MMA.debug.debug:
        dPrint("AutoSolo track names: %s" % ' '.join([a for a in autoSoloTracks]))


###############

def extractSolo(ln, rptcount):
    """ Parser calls this to extract solo strings. """

    a = ln.count('{')
    b = ln.count('}')

    if a != b:
        error("Mismatched {}s for solo found in chord line")

    if a:
        if rptcount > 1:
            error("Bars with both repeat count and solos are not permitted")

        ln, solo = pextract(ln, '{', '}')

        if len(solo) > len(autoSoloTracks):
            error("Too many melody/solo riffs in chord line. %s used, "
                  "only %s defined" % (len(solo), len(autoSoloTracks)))

        firstSolo = solo[0][:]  # save for autoharmony tracks

        """ We have the solo information. Now we loop though each "solo" and:
              1. Ensure or Create a MMA track for the solo
              2. Push the solo data into a Riff for the given track.
        """

        for s, trk in zip(solo, autoSoloTracks):
            if not s:
                continue    # skip placeholder/empty tracks
            MMA.alloc.trackAlloc(trk, 1)
            t = gbl.tnames[trk]
            if t.riff:
                error("%s: Attempt to add {} solo when the track "
                      "has pending RIFF data." % t.name)
            t.setRiff(s.strip())

        """ After all the solo data is interpreted and sent to the
            correct track, we check any leftover tracks. If any of these
            tracks are  empty of data AND are harmonyonly the note
            data from the first track is interpeted again for that
            track. Tricky: the max() is needed since harmonyonly can
            have different setting for each bar...this way
            the copy is done if ANY bar in the seq has harmonyonly set.
        """

        for t in autoSoloTracks[1:]:
            if t in gbl.tnames and not gbl.tnames[t].riff \
                    and set(gbl.tnames[t].harmonyOnly) != {None}:
                gbl.tnames[t].setRiff(firstSolo[:])

                if MMA.debug.debug:
                    dPrint("%s duplicated to %s for HarmonyOnly." % (trk, t))

    return ln

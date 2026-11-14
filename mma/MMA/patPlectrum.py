# patPlectrum.py

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
Louis James Barman

"""


import MMA.notelen

from . import gbl
from MMA.common import *
from MMA.pat import PC, Pgroup
import MMA.debug 
import copy

# By default notes are NOT stopped with a groove change
# for plectrum tracks. Set this to True to change the
# default or do so via Tweaks PlectrumRest=
# New for version 20.03.
plectrumReset = False   

class PlecStruct:
    pass

class Fnoise():   # fretnoise options
    def __init__(self):
        self.track = None
        self.strings = []
        self.duration = 192   # 1/4 note default duration in ticks
        self.octave = 0  # octave adjustment
        self.max = 1  # max number of noises per beat
        self.beats = []  # beat filter, []=all
        self.bars = []   # bar filter, []=all

class Plectrum(PC):
    """ Pattern class for a Raw MIDI track. """

    vtype = 'PLECTRUM'

    def __init__(self, nm):
        PC.__init__(self, nm)

        # We have vibrating strings (a string in python refers to text not a guitar string)
        self._vibrating = []
        self._lastOff = []
        self._tuning = []
        self.strumCenter = 0  # default to use 'start'
        self._capoFretNo = 0  # The number that the capo is on (0 for open strings)
        self.setPlectrumTuning(['e-', 'a-', 'd', 'g', 'b', 'e+'])
        self.fretNoise = None
        self.lastChord = None
        self._chordShapes = {}

    def saveGroove(self, gname):
        """ Save special/local variables for groove. """

        PC.saveGroove(self, gname)  # create storage. Do this 1st.
        self.grooves[gname]['CAPO'] = self._capoFretNo
        self.grooves[gname]['TUNING'] = self._tuning[:]
        self.grooves[gname]['PSTRUM'] = self.strumCenter

    def restoreGroove(self, gname):
        """ Restore special/local/variables for groove. """

        self._capoFretNo = self.grooves[gname]['CAPO']
        self._tuning = self.grooves[gname]['TUNING'][:]
        self.strumCenter = self.grooves[gname]['PSTRUM']
        PC.restoreGroove(self, gname)

    def clearSequence(self):
        """ Set some initial values. Called from init and clear seq. """

        PC.clearSequence(self)
        self._capoFretNo = 0
        if self.channel != 0:  # not sure if this is nesc. But safer!
            self.grooveFinish(0)

    def doMidiClear(self):
        """ Reset MIDI settings, special hook for stopping strings. """

        if self.channel != 0:
            self.grooveFinish(0)
        PC.doMidiClear(self)

    def getFretNoiseOptions(self):
        """ Return options. Used in setPlectrumFretNoise() and macros. """

        o = self.fretNoise

        if o.bars:
            bars = ','.join([str(i + 1) for i in o.bars])
        else:
            bars = 'ALL'

        if not o.beats:
            beats = 'All'
        else:
            beats = ','.join([str(1 + (i / float(gbl.BperQ))) for i in o.beats])

        return "%s FretNoise Track=%s Duration=%sT Octave=%s Strings=%s Max=%s Beats=%s Bars=%s" \
            % (self.name, o.track, o.duration, 
             o.octave / 12, 
               ','.join([str(abs(x-len(self._tuning))) for x in o.strings]), 
             o.max,
             beats, bars )


    def setPlectrumFretNoise(self, l):
        """ Set up the fretnoise stuff. """
        
        if not l or len(l)==1 and ( l[0].upper()=='OFF' or l[0].upper()=='NONE'):
            self.fretNoise = None
            if MMA.debug.debug:
                dPrint("%s FretNoise Off" % self.name)
            return

        self.fretNoise = Fnoise()  # new fret noise object
        scount = len(self._tuning)

        notopt, optpair = opt2pair(l, toupper=True)

        if notopt:
            error("%s FretNoise: All options are Key=Value, not '%s'." % \
                  (self.name, ' '.join(notopt)))

        o= self.fretNoise
        for cmd, opt in optpair:

            if cmd == 'BEATS':
               o.beats = []
               if opt != 'ALL':
                   for t in opt.split(','):
                       z = self.name  # this is for error msg in setBarOffset()
                       self.name = "%s FretNoise Beats" % z
                       o.beats.append(self.setBarOffset(t))
                       self.name = z

            elif cmd == 'BARS':
                o.bars = []
                if opt != 'ALL':
                    for t in opt.split(','):
                        i = stoi(t)
                        if i < 1 or i > gbl.seqSize:
                            warning("%s FretNoise Bars: setting of %s may be "
                                "ignored since SeqSize is %s." %
                                (self.name, i, gbl.seqSize))
                        o.bars.append(i - 1)

            elif cmd == 'DURATION':
                o.duration = MMA.notelen.getNoteLen(opt)

            elif cmd == 'MAX':
                i = stoi(opt)
                if i < 1 or i > scount:
                    error("%s FretNoise Max must be 1..%s, not '%s'." % \
                          (self.name, scount, opt))
                o.max = i

            elif cmd == 'STRINGS':
                o.strings = []
                for i in opt.split(','):
                    #i = stoi(i) - 1
                    i = abs(stoi(i)-scount)  # convert 1-6 to 6-1
                    if i < 0 or i > scount:
                        error("%s FretNoise STRING must be 1-%s, not %s." % \
                              (self.name, scount, i))
                    if i not in o.strings:
                        o.strings.append(i)

            elif cmd == 'TRACK':
                MMA.alloc.trackAlloc(opt, 1)
                if gbl.tnames[opt].vtype != 'BASS':
                    error("%s FretNoise Track must be a BASS track, not %s." % \
                          (self.name, gbl.tnames[opt].vtype))
                o.track = opt
                if not gbl.tnames[opt].channel:
                    gbl.tnames[opt].setForceOut()

            elif cmd == 'OCTAVE':
                i = stoi(opt)
                if i < -8 or i > 8:
                    error("%s FretNoise Octave: adjustment must be -8 to 8, not '%s'." 
                          % (self.name, i))
                o.octave = i * 12

            else:
                error("%s FretNoise: Unknown option '%s'." % (self.name, cmd))


        # no strings specified, set to the top 3
        if not o.strings:
            o.strings = range(0, 3)
            # Adjust to fit tuning
            o.strings=o.strings[0:scount]
                
        if not o.track:
            error("%s Fretnoise: No track was set. Use 'Track=some-bass-track' option." % self.name)

        if MMA.debug.debug:
            dPrint(self.getFretNoiseOptions())
        

    def setStrum(self, l):
        """ Called frm parser CENTER option. Sets strum to bar center, start or end.

            NOTE: This overrides the class setStrum() function.
        """

        if len(l) != 1:
            error("Strum: %s permits exactly one strum setting" % self.name)

        l = l[0].lower()

        if l == 'start':
            self.strumCenter = 0
        elif l == 'center':
            self.strumCenter = 1
        elif l == 'end':
            self.strumCenter = 2
        else:
            error("Strum: %s options are 'Start', 'Center' or 'End'. '%s' is illegal" %
                  (self.name, l.title()))

    def setPlectrumTuning(self, stringPitchNames):
        """ This is called from the parser TUNING option to set the
            instrument tuning.

            For standard guitar tuning use setTuning("e- a- d g b e+")

        """
        
        if self.channel != 0:   # if tuning changes while strings are still sounding
            self.grooveFinish(0)

        self._tuning = []
        self._vibration = []
        self.fretNoise = None  # turn off fret noise (could be string count diff)

        for pitchName in stringPitchNames:
            midiPitch = noteNameToMidiPitch(pitchName)
            if midiPitch is None:
                error("%s TUNING: Illegal/unknown string name '%s'." % (self.name, pitchName))

            self._tuning.append(midiPitch)
            vibration = PlecStruct()
            vibration.note = None       # None means the string not vibrating
            vibration.offset = None 
            self._vibrating.append(vibration)

        self._lastOff = [None] * len(self._vibrating)

    def setPlectrumCapo(self, capoFretNo):
        """ Set a capo value. Called from main parser. """

        self._capoFretNo = stoi(capoFretNo, "%s Capo: expecting integer, not '%s'."
                                % (self.name, capoFretNo))

    def setPlectrumShape(self,shape):
        """Defines a chord shape.

            PLECTRUM SHAPE [ chord [ f1 f2 ... fn ] ]

            Defines a shape (fingering) for a specific chord.
            The number of values supplied must match the number
            of strings defined in the current tuning.

            If a shape is defined for a particular chord, this shape
            will be used for the notes to sound. Capo and barre
            settings will be ignored for this chord.

            Allowable values are integers between 0 and 24, and a
            minus sign (or 'x' or 'n') for a muted string.

            Without arguments, removes all current shape definitions.
            With only the chord name, removes the shape definition
            for this chord.

        """

        if len(shape) == 0:
            # Forget all definitions.
            self._chordShapes = {}
            return
        
        chord = shape.pop(0)
        if len(shape) == 0:
            # Forget definition for this chord.
            if chord in self._chordShapes:
                self._chordShapes.pop(chord)
            else:
                warning("%s: Chord %s was not shaped" % (self.name, chord))
            return

        if len(shape) != len(self._tuning):
            error("%s: Shape requires values for %d strings (%d provided)" %
                  (self.name, len(self._tuning), len(shape)))

        self._chordShapes[chord] = []
        for i, n in enumerate(shape):
            if n == '-' or n.lower() == 'x' or n.lower == 'n':
                self._chordShapes[chord].append(None)
            else:
                try:
                    pos = int(n)
                except:
                    pos = None
                if pos is None or pos < -127 or pos > 127:
                    error("%s: Shape requires values between -127 and 127, or '-' for a muted string" % (self.name))
                self._chordShapes[chord].append(pos)
                
    def decodePlectrumPatterns(self, a, patterns):
        """ Decode plectrum patterns for a guitar here are examples """

        a.pluckVol = []
        if patterns[0].find(':') != -1 or len(patterns) == 1:
            # set all strings to note plucked
            for stringNo in range(len(self._tuning)):
                a.pluckVol.append(-1)

            if len(patterns) == 1 and patterns[0].find(':') == -1:
                # put in the missing : if there is just one pattern
                patterns[0] = ":" + patterns[0]

            for patString in patterns:
                if patString.find(':') == -1:
                    error("%s: Not all string definitions have a : in them '%s'" %
                          (self.name, ' '.join(patterns)))

                start = 0
                end = len(self._tuning) - 1

                pat = patString.split(':')

                if pat[0]:
                    emsg = "%s: Note String Number in Plectrum definition not int" % self.name
                    if pat[0].find('-') != -1:
                        startString, endString = pat[0].split('-')
                        if startString:
                            start = stoi(startString, emsg) - 1
                        if endString:
                            end = stoi(endString, emsg) - 1
                    else:
                        start = stoi(pat[0], emsg) - 1
                        end = start

                if start > end:
                    start, end = end, start

                for n in range(start, end + 1):
                    # we number strings from the other end
                    stringNo = len(self._tuning) - n - 1
                    if stringNo < 0 or stringNo >= len(self._tuning):
                        error("%s: string number %d does not exists" % (self.name, stringNo + 1))
                        return
                    if a.pluckVol[stringNo] != -1:
                        error("%s: Duplicate string %d definition" % (self.name, stringNo + 1))
                        return

                    a.pluckVol[stringNo] = stoi(pat[1], "%s: Note volume not int" % self.name)

        else:
            # this is without a the string specifier so all strings must be listed.
            if len(patterns) != len(self._tuning):
                error("%s: There must be %s strings listed definition, "
                      "not '%s'" % (self.name, len(self._tuning), ' '.join(patterns)))
                return
            for stringNo in range(len(self._tuning)):
                val = patterns[stringNo]
                if val == '-':
                    val = '-1'   # -1 means ignore this string
                a.pluckVol.append(stoi(val, "%s: Note volume not int" % self.name))

    def getPgroup(self, ev):
        """ Get group for rawmid pattern.

            Fields - start, length, note, volume

        """

        if len(ev) < 3:  # we need offset, strum and at least one pattern
            error("%s: There must be n groups of 3 or more in a pattern definition, "
                  "not '%s'" % (self.name, ' '.join(ev)))

        a = Pgroup()
        a.vol = 0        # as is this
        a.offset = self.setBarOffset(ev[0])
        a.strum = stoi(ev[1], "%s: Expecting int value for strum" % self.name)

        self.decodePlectrumPatterns(a, ev[2:])

        """ For the doc generators ... we need a setting for duration, even
            though this track doesn't really have one. Using the value of 0
            pretty much matches the results for a drum track. The author of
            this file used "pluckVol" and the docs are expecting a "vol" variable
            so we just duplicate it ... easier than changing all the uses here.
        """

        a.duration = 0   # this is a dummy value to keep docs happy
        a.vol = a.pluckVol

        return a

    def restart(self):
        self.ssvoice = -1

    def doFretNoise(self, stringNo, note, offset):
        """ Add in a fret noise note. """

        if self._lastOff[stringNo] is None or \
           self._lastOff[stringNo].note == note:
            return

        trk = gbl.tnames[self.fretNoise.track]

        # Let user override fretnoise for track by setting a RIFF,
        # or TRIGGER is the bass track.
        if trk.disable or \
           trk.riff or \
           trk.trigger.mode:
            return

        o = self.fretNoise

        # skip if incorrect beat/bar setting
        if (o.beats and offset not in o.beats) \
            or (o.bars and gbl.seqCount not in o.bars):
            return

        # use the plectrum track's seq (the BASS doesn't set it)
        trk.seq = self.seq

        # Use same volume as the string on
        volume = self._lastOff[stringNo].volume

        # We bypass the sendChord() so volume isn't adjusted. Do it anyway!
        volume = trk.adjustVolume(volume, offset)

        # bypassing voice set, do it here
        trk.insertVoice(self.seq)

        # bypass even more
        trk.clearPending()

        # octave adjustment
        note += o.octave
        while note > 127:
            note -= 12
        while note < 0:
            note += 12
        # Add the noise.
        trk.sendNote(offset, o.duration, note, volume)


    def endVibration(self, stringNo, offset):
        """ kill the vibration on the string by sending out a note off """

        vibration = self._vibrating[stringNo]

        # first test if this string has been played before
        if vibration.note is None:
            return

        lastOffset = vibration.offset
        o = offset - self.artic[self.seq]   # move off point back before the next ON

        # ensure we turn this string OFF after the ON offset for this note
        while o+gbl.tickOffset <= lastOffset:
            o += 1

        gbl.mtrks[self.channel].addNoteOnToTrack(o, vibration.note, 0)  # v=0 ==note off

        # save the turn-off point for fret noise function
        self._lastOff[stringNo] = copy.copy(vibration) # this gets the note, volume
        self._lastOff[stringNo].offset = o + gbl.tickOffset # offset into track


        vibration.note = None
        vibration.offset = None


    def grooveFinish(self, offset):
        """ End all vibrations (ie output all outstanding note off). """

        for stringNo in range(len(self._vibrating)):
            self.endVibration(stringNo, offset)

    def fretboardNote(self, stringNo, chordList, startIdx, previousFret, chordBarreFretNo):
        """ Returns a single note that is is on the chord for one string
            Unlike a guitar string number the lowest string is string Number 0
        """

        openString = self._tuning[stringNo] + self._capoFretNo + chordBarreFretNo

        fretNotes = {}
        for n, note in enumerate(chordList[startIdx:]):
            fretNo = note - openString % 12
            while fretNo < 0:
                fretNo += 12
            fretNo %= 12

            fret = PlecStruct()
            fret.pitch = self.adjustNote(openString + fretNo)
            fret.fretNo = fretNo
            fret.chordIndex = n + startIdx
            fretNotes[fretNo] = fret

        # Try to guess where the next finger position in the chord goes
        # without trying to stretch the hand too much.
        if previousFret:
            if previousFret.fretNo in fretNotes:
                return fretNotes[previousFret.fretNo]
            if (previousFret.fretNo - 1) in fretNotes:
                return fretNotes[previousFret.fretNo - 1]
            if (previousFret.fretNo - 2) in fretNotes:
                return fretNotes[previousFret.fretNo - 2]
            if (previousFret.fretNo + 1) in fretNotes and previousFret.fretNo <= 3:
                return fretNotes[previousFret.fretNo + 1]

        lowest = min(fretNotes.keys())

        return fretNotes[lowest]

    def fretboardNotes(self, chordList, chordBarreFretNo):
        notes = []

        if len(chordList) >= 5 or len(self._tuning) >= 8:
            # I don't know how to handle five or more notes in a chord
            # or more than 8 strings (eg a harp)
            # so just do a single pass and see what happens
            previousFret = None
            for stringNo in range(len(self._tuning)):
                fret = self.fretboardNote(stringNo, chordList, 0, previousFret, chordBarreFretNo)
                previousFret = fret
                notes.append(fret)

        else:
            #find the triad chord (the first three notes of the chord) first
            previousFret = None
            for stringNo in range(len(self._tuning)):
                fret = self.fretboardNote(stringNo, chordList[:3], 0,
                                          previousFret, chordBarreFretNo)
                previousFret = fret
                notes.append(fret)

            if len(chordList) == 4:
                # Now put in missing 7th (or what ever it is called) but
                # start searching from the top string

                for stringNo in reversed(range(len(self._tuning))):

                    fret = self.fretboardNote(stringNo, chordList, 3, None, chordBarreFretNo)
                    if fret.fretNo <= 4:
                        notes[stringNo] = fret

                        # now go back up to the top string to make sure there is no bunching
                        stringNo += 1
                        while stringNo < len(self._tuning):
                            notes[stringNo] = self.fretboardNote(stringNo, chordList, 0,
                                                                 None, chordBarreFretNo)
                            stringNo += 1
                        break

        # look for and mark duplicates
        notes[0].duplicate = False
        for stringNo in range(1, len(self._tuning)):
            if notes[stringNo - 1].pitch == notes[stringNo].pitch:
                notes[stringNo].duplicate = True
            else:
                notes[stringNo].duplicate = False

        return notes

    def fretboardShapes(self, chordName, chordList):
        shape = self._chordShapes[chordName]
        notes = []
        stringNo = -1
        for fretNo in shape:
            stringNo += 1
            fret = PlecStruct()
            try:
                fretNo = int(fretNo)
            except:
                fretNo = None

            openString = self._tuning[stringNo]
            fret.fretNo = fretNo
            fret.chordIndex = stringNo
            fret.duplicate = False
            if fretNo is None:
                fret.pitch = openString
            else:
                fret.pitch = self.adjustNote(openString + fretNo)
            notes.append(fret)

        return notes

    def trackBar(self, pattern, ctable):
        """ Do a plectrum bar.

            Called from self.bar()

        """

        sc = self.seq
        
        for p in pattern:
            try:
                ct = self.getChordInPos(p.offset, ctable)
                chordName = ct.chord.name
                chordList = ct.chord.noteList   # catch no noteList attribute
            except AttributeError:
                continue

            if ct.plectrumZ:
                continue

            if len(self._tuning) != len(p.pluckVol):
                error("%s: Pattern and tuning lengths (%s, %s) do not match. "
                      "Was tuning changed?" % (self.name, len(p.pluckVol), len(self._tuning)))

            chordBarreFretNo = 0
            if ct.name.startswith('+'):
                chordBarreFretNo += 12
            if ct.name.startswith('-'):
                chordBarreFretNo += -12

            chordBarreFretNo += ct.chord.barre

            if MMA.debug.debug or MMA.debug.plecShow:
                self.printChordShape(ct, chordBarreFretNo)

            plectrumNoteOnList = []  # for debugging only

            # Find how many strings have been plucked this time
            pluckStringCount = 0
            for vol in p.pluckVol:
                if vol == -1:
                    continue
                pluckStringCount += 1

            pluckStringIndex = 0

            if chordName in self._chordShapes:
                notes = self.fretboardShapes(chordName, chordList)
            else:
                notes = self.fretboardNotes(chordList, chordBarreFretNo)

            fretNoiseCount = 0
            for stringNo, vol in enumerate(p.pluckVol):
                if p.strum:
                    if self.strumCenter == 0:
                        # start strum at end of beat
                        strumOffset = p.offset + p.strum * pluckStringIndex
                    elif self.strumCenter == 1:
                        # the centre of the strum is on the beat
                        strumOffset = p.offset + p.strum * \
                            (pluckStringIndex - pluckStringCount / 2.0)
                    else:
                        # start strum at end of beat
                        strumOffset = p.offset + p.strum * \
                            (pluckStringCount - pluckStringIndex - 1)

                    if p.strum < 0:
                        strumOffset += -p.strum * pluckStringCount
                else:
                    strumOffset = p.offset

                if vol == -1:
                    # silence this stringNo if the note on this string has changed
                    # even if this stringNo has not been plucked or muted
                    if notes[stringNo].pitch != self._vibrating[stringNo].note:
                        self.endVibration(stringNo, strumOffset)

                    continue   # this string has not been plucked or damped

                pluckStringIndex += 1
                
                self.endVibration(stringNo, strumOffset)
                if vol >= 1:

                    note = notes[stringNo].pitch

                    if notes[stringNo].duplicate:
                        if MMA.debug.debug:
                            dPrint("%s: Ignoring duplicate note %d." % (self.name, note))
                        continue

                    if notes[stringNo].fretNo is None:
                        if MMA.debug.debug:
                            dPrint("%s: Ignoring muted note %d." % (self.name, note))
                        continue

                    outputVolume = self.adjustVolume(vol, p.offset)

                    ontime = gbl.mtrks[self.channel].addNoteOnToTrack(strumOffset, note,
                                                             outputVolume,
                                                             self.rTime[sc][0],
                                                             self.rTime[sc][1])

                    self._vibrating[stringNo].note = note
                    self._vibrating[stringNo].offset = ontime  # save the start time
                    self._vibrating[stringNo].volume = outputVolume # and volume
                    if outputVolume == 0:
                        self._vibrating[stringNo].note = None

                    # Do fretnoise stuff if enabled
                    
                    if self.lastChord != ct.name and self.fretNoise  \
                       and outputVolume and stringNo in self.fretNoise.strings:
                        if fretNoiseCount < self.fretNoise.max:
                            self.doFretNoise(stringNo, note, strumOffset)
                            fretNoiseCount += 1

                    plectrumNoteOnList.append(note)  # for debugging only

                self.lastChord = ct.name

            if MMA.debug.debug:
                dPrint("%s: channel=%s offset=%s chordList=%s NoteOn=%s." % 
                    (self.name, self.channel, p.offset + gbl.tickOffset,
                        chordList, plectrumNoteOnList))

    def printChordShape(self, chordTable, chordBarreFretNo=0):

        chordList = chordTable.chord.noteList

        # catch the case when there is no noteList attribute
        if hasattr(self, 'previousChordList'):
            if chordList == self.previousChordList and \
                    chordBarreFretNo == self.previousFretNo \
                    and not ( chordTable.name in self._chordShapes \
                              and self._chordShapes[chordTable.name] != self.previousShape ) :
                return
        self.previousChordList = chordList
        self.previousFretNo = chordBarreFretNo
        if  chordTable.name in self._chordShapes:
            self.previousShape = self._chordShapes[chordTable.name]
        else:
            self.previousShape = None

        capoFretNo = self._capoFretNo
        if chordTable.name in self._chordShapes:
            notes = self.fretboardShapes(chordTable.name, chordList)
            capoFretNo = 0
            chordBarreFretNo = 0
        else:
            notes = self.fretboardNotes(chordList, chordBarreFretNo)
        notes.reverse()

        printStart = 0
        startFretNo = capoFretNo + chordBarreFretNo
        if startFretNo < 0:
            printStart = startFretNo

        dPrint("%s %s chord %s" % (self.name, chordTable.name,  chordList))
        for stringNo, openNote in enumerate(reversed(self._tuning)):
            openNote = self.adjustNote(openNote)  # puts into middle octave 60==5*12
            note = notes[stringNo].pitch

            msg = ["%s   %3d" % (self.name, openNote + capoFretNo)]
            finger = note - openNote
            for fretNo in range(printStart, 20):
                if fretNo == 0 and notes[stringNo].fretNo is None and capoFretNo == 0:
                    msg.append("X")
                elif fretNo == 0 and capoFretNo == 0:
                    msg.append("|")
                elif fretNo == capoFretNo and chordBarreFretNo == 0:
                    if notes[stringNo].fretNo is None:
                        msg.append("X")
                    else:
                        msg.append("$")
                elif fretNo == finger:
                    msg.append("*")
                elif fretNo == capoFretNo:
                    msg.append("$")
                elif fretNo == startFretNo:
                    msg.append(":")
                elif fretNo == 0:
                    msg.append("|")
                else:
                    msg.append("-")

            msg.append("%d" % (notes[stringNo].chordIndex))
            if notes[stringNo].fretNo is not None:
                msg.append("  %d" % (note))
            if notes[stringNo].duplicate:
                msg.append("  duplicate")

            dPrint(' '.join(msg))
        dPrint('\n')

def noteNameToMidiPitch(s):
    """ Convert a name ('e', 'g#') to a MIDI pitch. """

    tb = {'c': 0, 'c#': 1, 'd&': 1, 'd': 2, 'd#': 3, 'e&': 3,
          'e': 4, 'f&': 4, 'e#': 5, 'f': 5, 'f#': 6, 'g&': 6,
          'g': 7, 'g#': 8, 'a&': 8, 'a': 9, 'a#': 10, 'b&': 10,
          'b': 11, 'b&': 11, 'c&': 11, 'b#': 0}

    # strip and count trailing '+' and '-'

    if '-' in s and '+' in s:
        return None

    adjust = 0
    while s.endswith('-'):
        adjust -= 12
        s = s[:-1]
    while s.endswith('+'):
        adjust += 12
        s = s[:-1]

    try:
        value = tb[s]  # puts into middle octave 60==5*12
    except:
        return None

    return value + adjust


#not used. Leave for debugging??
def MidiPitch2NoteName(value):
    nameLookUp = ['c', 'c#', 'd', 'e&', 'e', 'f', 'f#', 'g', 'g#', 'a', 'b&', 'b']

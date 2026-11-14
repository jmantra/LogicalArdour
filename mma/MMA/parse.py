# parse.py

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


This module does all file parsing. Most commands
are passed to the track classes; however, things
like TIME, SEQRND, etc. which just set global flags
are completely handled here.

"""

import random

from . import gbl
from MMA.common import *

import MMA.debug
import MMA.notelen
import MMA.chords
import MMA.file
import MMA.midi
import MMA.midifuncs
import MMA.midiIn
import MMA.midinote
import MMA.grooves
import MMA.docs
import MMA.auto
import MMA.func
import MMA.translate
import MMA.patSolo
import MMA.mdefine
import MMA.volume
import MMA.seqrnd
import MMA.patch
import MMA.paths
import MMA.player
import MMA.sequence
import MMA.swing
import MMA.sync
import MMA.truncate
import MMA.ornament
import MMA.trigger
import MMA.tempo
import MMA.tweaks
import MMA.options
import MMA.rpitch
import MMA.regplug
import MMA.after
import MMA.lyric

from MMA.timesig import timeSig
from MMA.parseCL import parseChordLine
from MMA.macro import macros
from MMA.alloc import trackAlloc
from MMA.keysig import keySig

beginData = []      # Current data set by a BEGIN statement
beginPoints = []    # since BEGINs can be nested, we need ptrs for backing out of BEGINs

########################################
# File processing. Mostly jumps to pats
########################################

def parseFile(n, depth=[0]):
    """ Open and process a file. Errors exit. """

    depth[0] += 1
    if depth[0]>50:
        error("USE/INCLUDE recursion error. "
              "Use and Include are limited to a depth of 50. "
              "Check current file and rc files for error.")
        
    fp = gbl.inpath

    f = MMA.file.ReadFile(n)

    parse(f)
    gbl.inpath = fp

    if MMA.debug.debug:
        dPrint("File '%s' closed." % n)

    depth[0] -= 1
                
def parse(inpath):
    """ Process a mma input file. """

    global beginData, lastChord
    
    gbl.inpath = inpath
    curline = None

    while 1:
        MMA.after.check()
        
        curline = inpath.read()

        if curline is None:   # eof, exit parser
            break

        l = macros.expand(curline)
        if not l:
            continue

        """ Handle BEGIN and END here. This is outside of the Repeat/End
            and variable expand loops so SHOULD be pretty bullet proof.
            Note that the beginData stuff is global to this module ... the
            Include/Use directives check to make sure we're not doing that
            inside a Begin/End.

            beginData[] is a list which we append to as more Begins are
            encountered.

            The placement here is pretty deliberate. Variable expand comes
            later so you can't macroize BEGIN ... I think this makes sense.

            The tests for 'begin', 'end' and the appending of the current
            begin[] stuff have to be here, in this order.
        """

        action = l[0].upper()      # 1st arg in line

        if action == 'BEGIN':
            if not l[1:]:
                error("Use: Begin STUFF")
            beginPoints.append(len(beginData))
            beginData.extend(l[1:])
            continue

        if action == 'END':
            if len(l) > 1:
                error("No arguments permitted for END")
            if not beginData:
                error("No 'BEGIN' for 'END'")
            beginData = beginData[:beginPoints.pop(-1)]
            continue

        if beginData:
            l = beginData + l
            action = l[0].upper()

        if MMA.debug.showExpand and action != 'REPEAT':
            dPrint(l)

        if action in simpleFuncs:
            simpleFuncs[action](l[1:])
            continue            

        """ We have several possibilities ...
            1. The command is a valid assigned track name,
            2. The command is a valid track name, but needs to be
               dynamically allocated,
            3. It's really a chord action
        """

        if not action in gbl.tnames:  # no track allocated?
            trackAlloc(action, 0)     # Try to create. Always returns.

        if action in gbl.tnames:     # BASS/DRUM/APEGGIO/CHORD
            name = action
            if len(l) < 2:
                error("Expecting argument after '%s'" % name)
            action = l[1].upper()

            # Got trackname and action
            if action in trackFuncs:  # perfect, execute
                trackFuncs[action](name, l[2:])
                continue

            elif action in simpleFuncs:  # opps, not track func
                error("%s is not a track function. Use global form." % action)
            else:  # opps, not any kind of func
                error("%s is not a %s track function." % (action, name))


        ### Gotta be a chord data line!

        """ A data line can have an optional bar number at the start
            of the line. Makes debugging input easier. The next
            block strips leading integers off the line. Note that
            a line number on a line by itself it okay.
        """

        
        if action.isdigit():   # isdigit() matches '1', '1234' but not '1a'!
            gbl.barLabel = l[0].lstrip('0')
            l = l[1:]
            if not l:        # ignore empty lines
                continue
        else:
            gbl.barLabel = ''

        ##  A bar can have an optional repeat count. This must
        ##  be at the end of bar in the form '* xx'.
        if len(l) > 1 and l[-2] == '*':
            rptcount = stoi(l[-1], "Expecting integer after '*'")
            l = l[:-2]
        else:
            rptcount = 1

        # Dataplugins all start with '@'. Code is in the plugin code.
        # A data plugin modifies the existing data line and returns it.
        if l[0].startswith('@'):
            p = l[0].upper()
            if p not in dataFuncs:
                error("Unknown data plugin '%s' called." % p)
            l = dataFuncs[p](l[1:])

        # Extract solo(s) from line ... this is anything in {}s.
        # The solo data is pushed into RIFFs and discarded from
        # the current line.
        l = ' '.join(l)
        l = MMA.patSolo.extractSolo(l, rptcount)

        # set lyrics from [stuff] in the current line.
        # NOTE: lyric.extract() inserts previously created
        #       data from LYRICS SET and inserts the chord names
        #       if that flag is active.
        l, lyrics = MMA.lyric.lyric.extract(l, rptcount)
        l = l.split()

        # At this point we have only chord info. A number
        # of sanity checks are made:
        #   1. Make sure there is some chord data,
        #   2. Ensure the correct number of chords.
        if not l:
            error("Expecting music (chord) data. Even lines with "
                  "lyrics or solos still need a chord. If you "
                  "don't want a chord use 'z'.")

        # We now have a chord line. It'll look something like:
        #
        #      ['Cm', '/', 'z', 'F#@4.5'] or ['/' 'C@3' ]
        #
        #    For each bar we create a list of CTables, one for each
        #    chord in the line. Each entry has the start/end (in beats), chordname, etc.
        #

        ctable = parseChordLine(l)   # parse the chord line

        # Create MIDI data for the bar

        for rpt in range(rptcount):   # for each bar in the repeat count ( Cm * 3)
            """ Handle global (de)cresc by popping a new volume off stack. """

            if MMA.volume.futureVol:
                MMA.volume.volume = MMA.volume.futureVol.pop(0)
            if MMA.volume.futureVol:
                MMA.volume.nextVolume = MMA.volume.futureVol[0]
            else:
                MMA.volume.nextVolume = None

            # Set up for rnd seq. This may set the current seq point.
            # If return is >=0 then we're doing track rnd.

            rsq, seqlist = MMA.seqrnd.setseq()

            """ Process each track. It is important that the track classes
                are written so that the ctable passed to them IS NOT MODIFIED.
                This applies especially to chords. If the track class changes
                the chord, then the function called MUST restore it before returning!!!
            """

            for a in gbl.tnames.values():
                if rsq >= 0:
                    seqSave = gbl.seqCount
                    if a.name in seqlist:   # for seqrnd with tracklist
                        gbl.seqCount = rsq
                a.bar(ctable)    # process entire bar!

                if rsq >= 0:   # for track rnd
                    gbl.seqCount = seqSave

            # Adjust counters

            """ After processsing each bar we update a dictionary of bar
                pointers. This table is used when the MIDI data is written
                when -b or -B is set to limit output.
            """

            if MMA.truncate.length:
                nextOffset = MMA.truncate.length
                MMA.truncate.countDown()
            else:
                nextOffset = gbl.barLen

            # barPtrs is used by the -B/b options to strip unwanted sections. 
            gbl.barPtrs[gbl.barNum + 1] = [gbl.barLabel, gbl.tickOffset,
                                           gbl.tickOffset + nextOffset - 1]

            gbl.totTime += float(nextOffset / gbl.BperQ) / gbl.tempo

            gbl.tickOffset += nextOffset

            if gbl.printProcessed:
                if gbl.barLabel:
                    gbl.barLabels.append(gbl.barLabel)
                else:
                    gbl.barLabels.append('?')

            gbl.barNum += 1
            gbl.seqCount = (gbl.seqCount + 1) % gbl.seqSize

            if gbl.barNum > gbl.maxBars:
                error("Capacity exceeded. Maxbar setting is %s. Use -m option"
                      % gbl.maxBars)

            MMA.grooves.nextGroove()   # using groove list? Advance.

            # Enabled with the -r command line option

            if MMA.debug.showrun:
                if lyrics:       # we print lyric as a list 
                    ly = lyrics  # with the []s
                else:
                    ly = ''      # no lyric
                dPrint("%3d: %s %s" % (gbl.barNum, ' '.join(l), ly))

            # if repeat count is set with dupchord we push
            # the chord back and get lyric.extract to add the
            # chord to the midi file again. A real lyric is
            # just ignored ... 2 reasons: the lyric is mangled and
            # and it makes sense to only have it once!
            if rptcount>1 and MMA.lyric.lyric.dupchords:
                _,lyrics = MMA.lyric.lyric.extract(' '.join(l), 0)

            # The barNum and other pointers have been incremented
            # and a bar of data has been processed. If we are repeating
            # due to a "*" we do a AGAIN test. Without a rpt this would
            # be done at the start of a data line. 
            if rptcount>1 and  MMA.after.needed():
                MMA.after.check(recurse=True)

##################################################################

def allTracks(ln):
    """ Apply command to all specified tracks or track types. """

    types1 = ('BASS', 'CHORD', 'ARPEGGIO', 'SCALE', 'DRUM', 'WALK', 'PLECTRUM')
    types2 = ('MELODY', 'SOLO', 'ARIA')
    allTypes = types1 + types2

    ttypes = []

    if len(ln) < 1:
        error("AllTracks: Requires arguments: [Track | Track-Name] command.")

    i = 0
    while i < len(ln) and ln[i].upper() in allTypes:
        ttypes.append(ln[i].upper())
        i += 1

    if ttypes == []:
        ttypes = types1

    if i >= len(ln):
        error("AllTracks: A command is required after the Track or Track-Name.")

    cmd = ln[i].upper()
    args = i + 1

    if not cmd in trackFuncs:
        error("AllTracks: command '%s' doen't exist" % cmd)

    for n in gbl.tnames:
        if not gbl.tnames[n].vtype in ttypes:
            continue

        trackFuncs[cmd](n, ln[args:])


#######################################
# Do-nothing functions

def comment(ln):
    pass


def repeatend(ln):
    error("Repeatend/EndRepeat without Repeat")


def repeatending(ln):
    error("Repeatending without Repeat")


def endmset(ln):
    error("EndMset/MSetEnd without Mset")


def ifend(ln):
    error("ENDIF without IF")


def ifelse(ln):
    error("ELSE without IF")


#######################################
# Repeat/jumps


def repeat(ln):
    """ Repeat/RepeatEnd/RepeatEnding.

        Read input until a RepeatEnd is found. The entire
        chunk is pushed back into the input stream the
        correct number of times. This accounts for endings and
        nested repeats.
    """

    def repeatChunk():
        q = []
        qnum = []
        nesting = 0

        while 1:
            l = gbl.inpath.read()

            if not l:
                error("EOF encountered processing Repeat")

            act = l[0].upper()

            if act == 'REPEAT':
                nesting += 1

            elif act in ('REPEATEND', 'ENDREPEAT') and nesting:
                nesting -= 1

            elif act == 'REPEATENDING' and nesting:
                pass

            elif act in ('REPEATEND', 'ENDREPEAT', 'REPEATENDING'):
                return (q, qnum, act, l[1:])

            q.append(l)
            qnum.append(gbl.lineno)

    stack = []
    stacknum = []
    main = []
    mainnum = []
    ending = 0

    if ln:
        error("REPEAT takes no arguments")

    main, mainnum, act, l = repeatChunk()

    while 1:
        if act in ('REPEATEND', 'ENDREPEAT'):
            if l:
                l = macros.expand(l)
                if len(l) == 2:
                    l = [x.upper() for x in l]
                    if 'NOWARN' in l:
                        l.remove('NOWARN')
                        warn = 0
                else:
                    warn = 1

                if len(l) != 1:
                    error("%s: Use [NoWarn] Count" % act)

                count = stoi(l[0], "%s takes an integer arg" % act)

                if count == 2 and warn:
                    warning("%s count of 2 duplicates default. Did you mean 3 or more?" % act)

                elif count == 1 and warn:
                    warning("%s count of 1 means NO REPEAT" % act)

                elif count == 0 and warn:
                    warning("%s count of 0, Skipping entire repeated section" % act)

                elif count < 0:
                    error("%s count must be 0 or greater" % act)

                elif count > 10 and warn:
                    warning("%s is a large value for %s" % (count, act))

            else:
                count = 2

            if not ending:
                count += 1
            for c in range(count - 1):
                stack.extend(main)
                stacknum.extend(mainnum)
            gbl.inpath.push(stack, stacknum)
            break

        elif act == 'REPEATENDING':
            ending = 1

            if l:
                l = macros.expand(l)
                if len(l) == 2:
                    l = [x.upper() for x in l]
                    if 'NOWARN' in l:
                        l.remove('NOWARN')
                        warn = 0
                else:
                    warn = 1

                if len(l) != 1:
                    error("REPEATENDING: Use [NoWarn] Count")

                count = stoi(l[0], "RepeatEnding takes an integer arg")

                if count < 0:
                    error("RepeatEnding count must be postive, not '%s'" % count)

                elif count == 0 and warn:
                    warning("RepeatEnding count of 0, skipping section")

                elif count == 1 and warn:
                    warning("RepeatEnding count of 1 duplicates default")

                elif count > 10 and warn:
                    warning("%s is a large value for RepeatEnding" % count)
            else:
                count = 1

            rpt, rptnum, act, l = repeatChunk()

            for c in range(count):
                stack.extend(main)
                stacknum.extend(mainnum)
                stack.extend(rpt)
                stacknum.extend(rptnum)

        else:
            error("Unexpected line in REPEAT")


def goto(ln):
    if len(ln) != 1:
        error("Usage: GOTO Label")
    gbl.inpath.goto(ln[0].upper())


def eof(ln):
    """ Stop reading CURRENT file """

    gbl.inpath.toEof()

def forceError(ln):
    """ Force an error. """

    if len(ln)<1:
        ln=["Unspecified cause."]
    error('User error: ' + ' '.join(ln))
    
#######################################
# File and I/O


def include(ln):
    """ Include a file. """

    global beginData

    if beginData:
        error("INCLUDE not permitted in Begin/End block")

    if len(ln) != 1:
        error("Use: Include FILE")

    fn = MMA.paths.findIncFile(ln[0])

    if not fn:
        error("Could not find include file '%s'" % ln[0])

    parseFile(fn)

def usefile(ln):
    """ Include a library file. """

    global beginData

    if beginData:
        error("USE not permitted in Begin/End block")

    if len(ln) != 1:
        error("Use: Use FILE")

    fn = MMA.paths.findLibFile(ln[0])

    if not fn:
        error("Unable to locate library file '%s'" % ln[0])

    """ USE saves current state, just like defining a groove.
        Here we use a magic number which can't be created with
        a defgroove ('cause it's an integer). Save, read, restore.
    """

    MMA.grooves.stackGroove.push()
    parseFile(fn)
    MMA.grooves.stackGroove.pop()


#######################################
# Misc

def rndseed(ln):
    """ Reseed the random number generator. """

    if not ln:
        random.seed()   # just resets, not predicable.

    elif len(ln) > 1:
        error("RNDSEED: requires 0 or 1 arguments")
    else:
        random.seed(stoi(ln[0]))  # predicable results.


def lnPrint(ln):
    """ Print stuff in a "print" command. """

    print(" ".join(ln))


def printActive(ln):
    """ Print a list of the active tracks. """

    print("Active tracks, groove: %s %s" % (MMA.grooves.currentGroove, ' '.join(ln)))
    print("%15s  %2s   %s" % ("Track", "Ch", "Events"))
    for a in sorted(gbl.tnames.keys()):
        f = gbl.tnames[a]
        if f.sequence:
            if f.channel > 0:
                ch = f.channel
                ecount = 0
                for ev in gbl.mtrks[ch].miditrk:
                    ecount +=  len(gbl.mtrks[ch].miditrk[ev])
            else:
                ch = '-'
                ecount = ''
            print("%15s  %2s   %s" % (a, ch, ecount))
    print("\n")


###########################################################
###########################################################
## Track specific commands


#######################################
# Pattern/Groove

    
def trackDefPattern(name, ln):
    """ Define a pattern for a track.

    Use the type-name for all defines.... check the track
    names and if it has a '-' in it, we use only the
    part BEFORE the '-'. So DRUM-Snare becomes DRUM.
    """

    ln = ln[:]

    name = name.split('-')[0]

    trackAlloc(name, 1)

    if ln:
        pattern = ln.pop(0).upper()
    else:
        error("Define is expecting a pattern name")

    if pattern in ('z', 'Z', '-'):
        error("Pattern name '%s' is reserved" % pattern)

    if pattern.startswith('_'):
        error("Names with a leading underscore are reserved")

    if not ln:
        error("No pattern list given for '%s %s'" % (name, pattern))

    ln = ' '.join(ln)
    gbl.tnames[name].definePattern(pattern, ln)


def trackRiff(name, ln):
    """ Set a riff for a track. """

    gbl.tnames[name].setRiff(' '.join(ln))


def trackDupRiff(name, ln):
    """ Set a riff for a track. """

    if not ln:
        error("%s DupRiff: need at least one track to copy to.")

    gbl.tnames[name].dupRiff(ln)


def deleteTrks(ln):
    """ Delete a track and free the MIDI track. """

    if not len(ln):
        error("Use Delete Track [...]")

    for name in ln:
        name = name.upper()
        if name in gbl.tnames:
            tr = gbl.tnames[name]
        else:
            error("Track '%s' does not exist" % name)

        if tr.channel:
            tr.doMidiClear()
            tr.clearPending()

            if tr.riff:
                warning("%s has pending RIFF(s)" % name)
            gbl.midiAvail[tr.channel] -= 1

            # NOTE: Don't try deleting 'tr' since it's just a copy!!

            del gbl.tnames[name]

        if not name in gbl.deletedTracks:
            gbl.deletedTracks.append(name)

        if MMA.debug.debug:
            dPrint("Track '%s' deleted" % name)

#######################################
# Volume


def trackRvolume(name, ln):
    """ Set random volume for specific track. """

    if not ln:
        error("Use: %s RVolume N [...]" % name)
    gbl.tnames[name].setRVolume(ln)


def trackSwell(name, ln):
    gbl.tnames[name].setSwell(ln)


def trackCresc(name, ln):
    gbl.tnames[name].setCresc(1, ln)


def trackDeCresc(name, ln):
    gbl.tnames[name].setCresc(-1, ln)


def trackVolume(name, ln):
    """ Set volume for specific track. """

    if not ln:
        error("Use: %s Volume DYN [...]" % name)

    gbl.tnames[name].setVolume(ln)


def trackChords(name, ln):
    """ Set a chord line for a specific track. """

    gbl.tnames[name].setChords(ln)


def trackAccent(name, ln):
    """ Set emphasis beats for track."""

    gbl.tnames[name].setAccent(ln)


#######################################
# Timing

def trackMallet(name, ln):
    """ Set repeating-mallet options for solo/melody track. """

    if not ln:
        error("Use: %s Mallet <Option=Value> [...]" % name)

    gbl.tnames[name].setMallet(ln)


def trackRduration(name, ln):
    """ Set random duration effect for specific track."""

    if not ln:
        error("Use: %s Rduration N [...]" % name)

    gbl.tnames[name].setRDuration(ln)


def trackRtime(name, ln):
    """ Set random timing for specific track. """

    if not ln:
        error("Use: %s RTime N [...]" % name)

    gbl.tnames[name].setRTime(ln)


def trackRskip(name, ln):
    """ Set random skip for specific track. """

    gbl.tnames[name].setRSkip(ln)


def trackArtic(name, ln):
    """ Set articulation. """

    if not ln:
        error("Use: %s Articulation N [...]" % name)

    gbl.tnames[name].setArtic(ln)


#######################################
# Chord stuff


def trackCompress(name, ln):
    """ Set (unset) compress for track. """

    if not ln:
        error("Use: %s Compress <value[s]>" % name)

    gbl.tnames[name].setCompress(ln)


def trackVoicing(name, ln):
    """ Set Voicing options. Only valid for chord tracks at this time."""

    if not ln:
        error("Use: %s Voicing <MODE=VALUE> [...]" % name)

    gbl.tnames[name].setVoicing(ln)


def trackDupRoot(name, ln):
    """ Set (unset) the root note duplication. Only applies to chord tracks. """

    if not ln:
        error("Use: %s DupRoot <value> ..." % name)

    gbl.tnames[name].setDupRoot(ln)


def trackChordLimit(name, ln):
    """ Set (unset) ChordLimit for track. """

    gbl.tnames[name].setChordLimit(ln)


def trackRange(name, ln):
    """ Set (unset) Range for track. Only effects arp and scale. """

    if not ln:
        error("Use: %s Range <value> ... " % name)

    gbl.tnames[name].setRange(ln)


def trackInvert(name, ln):
    """ Set invert for track."""

    if not ln:
        error("Use: %s Invert N [...]" % name)

    gbl.tnames[name].setInvert(ln)


def trackSpan(name, ln):
    """ Set midi note span for track. """

    if len(ln) != 2:
        error("Use: %s Start End" % name)

    start = stoi(ln[0], "Expecting integer for SPAN 1st arg")
    if start < 0 or start > 127:
        error("Start arg for Span must be 0..127, not %s" % start)

    end = stoi(ln[1], "Expecting integer for SPAN 2nd arg")
    if end < 0 or end > 127:
        error("End arg for Span must be 0..127, not %s" % end)

    if end <= start:
        error("End arg for Span must be greater than start")

    if end - start < 11:
        error("Span range must be at least 12")

    gbl.tnames[name].setSpan(start, end)


def trackOctave(name, ln):
    """ Set octave for specific track. """

    if not ln:
        error("Use: %s Octave N [...], (n=0..10)" % name)

    gbl.tnames[name].setOctave(ln)


def trackMOctave(name, ln):
    """ Set midi-based octave for specific track. """

    if not ln:
        error("Use: %s MOctave N [...], (n=01..9)" % name)

    gbl.tnames[name].setMOctave(ln)


def trackRpitch(name, ln):
    """ Set random pitch adjustment for specific track. """

    if not ln:
        error("Use: %s RPitch N [...]" % name)
    gbl.tnames[name].setRPitch(ln)

def trackStrum(name, ln):
    """ Set all specified track strum. """

    if not ln:
        error("Use: %s Strum N [...]" % name)

    gbl.tnames[name].setStrum(ln)

def trackStrumAdd(name, ln):
    """ Set all specified track strumAdd. """

    if not ln:
        error("Use: %s StrumAdd N [...]" % name)

    gbl.tnames[name].setStrumAdd(ln)

def trackSticky(name, ln):
    """ Sets a track as sticky. Ignored by groove commands. """

    if not ln:
        error("Use: %s Sticky On/Off" % name)

    gbl.tnames[name].setSticky(ln)

def trackHarmony(name, ln):
    """ Set harmony value. """

    if not ln:
        error("Use: %s Harmony N [...]" % name)

    MMA.harmony.setHarmony(gbl.tnames[name], ln)
#    gbl.tnames[name].setHarmony(ln)


def trackHarmonyOnly(name, ln):
    """ Set harmony only for track. """

    if not ln:
        error("Use: %s HarmonyOnly N [...]" % name)

    MMA.harmony.setHarmonyOnly(gbl.tnames[name], ln)
#      gbl.tnames[name].setHarmonyOnly(ln)


def trackHarmonyVolume(name, ln):
    """ Set harmony volume for track."""

    if not ln:
        error("Use: %s HarmonyVolume N [...]" % name)

    MMA.harmony.setHarmonyVolume(gbl.tnames[name], ln)
#      gbl.tnames[name].setHarmonyVolume(ln)


#######################################
# Plectrum only stuff

def trackPlectrumTuning(name, ln):
    """ Define the number of strings and tuning for
        for an instrument that can be played with a plectrum.
    """

    if not ln:
        error("Use: %s Tuning string1 string2 string3 [stringN ...]" % name)

    g = gbl.tnames[name]

    try:
        g.setPlectrumTuning(ln)
    except AttributeError:
        warning("TUNING: not permitted in %s tracks. Arg '%s' ignored." %
                (g.vtype, ' '.join(ln)))


def trackPlectrumCapo(name, ln):
    """ Define the position of the capo
        (unlike a real guitar negative numbers are allowed)
        for an instrument that can be played with a plectrum.
    """

    if not ln or len(ln) != 1:
        error("Use: %s Capo N" % name)

    g = gbl.tnames[name]
    try:
        g.setPlectrumCapo(ln[0])
    except AttributeError:
        warning("CAPO: not permitted in %s tracks. Arg '%s' ignored." %
                (g.vtype, ' '.join(ln)))


def trackPlectrumFretNoise(name, ln):
    """ Define fret noise options.
    """

    g = gbl.tnames[name]

    try:
        g.setPlectrumFretNoise(ln)
    except AttributeError:
        warning("FRETNOISE: not permitted in %s tracks. Arg '%s' ignored." %
                (g.vtype, ' '.join(ln)))

def trackPlectrumShape(name, ln):
    """ Define chord shape for stringed instrument. """

    g = gbl.tnames[name]
    
    try:
        g.setPlectrumShape(ln)
    except AttributeError:
        warning("SHAPE: not permitted in %s tracks. Arg '%s' ignored." %
                (g.vtype, ' '.join(ln)))


#######################################
# MIDI setting


def trackChannel(name, ln):
    """ Set the midi channel for a track."""

    if not ln:
        error("Use: %s Channel" % name)

    gbl.tnames[name].setChannel(ln[0])


def trackChShare(name, ln):
    """ Set MIDI channel sharing."""

    if len(ln) != 1:
        error("Use: %s ChShare TrackName" % name)

    gbl.tnames[name].setChShare(ln[0])


def trackVoice(name, ln):
    """ Set voice for specific track. """

    if not ln:
        error("Use: %s Voice NN [...]" % name)

    gbl.tnames[name].setVoice(ln)


def trackOff(name, ln):
    """ Turn a track off """

    if ln:
        error("Use: %s OFF with no paramater" % name)

    gbl.tnames[name].setOff()


def trackOn(name, ln):
    """ Turn a track on """

    if ln:
        error("Use: %s ON with no paramater" % name)

    gbl.tnames[name].setOn()


def trackOrnament(name, ln):
    """ Set the ornamentation. Currently only for SCALE. """

    MMA.ornament.setOrnament(gbl.tnames[name], ln)


def trackTone(name, ln):
    """ Set the tone (note). Only valid in drum tracks."""

    gbl.tnames[name].setTone(ln)


def trackForceOut(name, ln):
    """ Force output of voice settings. """

    if len(ln):
        error("Use %s ForceOut (no options)" % name)

    gbl.tnames[name].setForceOut()


#######################################
# Misc

def trackArpeggiate(name, ln):
    """ Set up the solo/melody arpeggiator. """

    if not ln:
        error("Use: %s Arpeggiate N" % name)

    g = gbl.tnames[name]
    try:
        g.setArp(ln)
    except AttributeError:
        warning("Arpeggiate: not permitted in %s tracks. Arg '%s' ignored." %
                (g.vtype, ' '.join(ln)))


def trackStretch(name, ln):
    """ Set the stretch value for solo/melody. """

    if not ln:
        error("Use: %s Stretch N" % name)

    g = gbl.tnames[name]
    try:
        g.setStretch(ln)
    except AttributeError:
        warning("Stretch: not permitted in %s tracks. Arg '%s' ignored." %
                (g.vtype, ' '.join(ln)))


def trackDelay(name, ln):
    """ Set up the solo/melody delay (echo). """

    if not ln:
        error("Use: %s Delay N" % name)

    gbl.tnames[name].setDelay(ln)


def trackDrumType(name, ln):
    """ Set a melody or solo track to be a drum solo track."""

    tr = gbl.tnames[name]
    if tr.vtype not in ('SOLO', 'MELODY'):
        error("Only Solo and Melody tracks can be to DrumType, not '%s'" % name)
    if ln:
        error("No parmeters permitted for DrumType command")

    tr.setDrumType()


def trackDirection(name, ln):
    """ Set scale/arp direction. """

    if not ln:
        error("Use: %s Direction OPT" % name)

    gbl.tnames[name].setDirection(ln)


def trackScaletype(name, ln):
    """ Set the scale type. """

    if not ln:
        error("Use: %s ScaleType OPT" % name)

    gbl.tnames[name].setScaletype(ln)


def trackUnify(name, ln):
    """ Set UNIFY for track."""

    if not len(ln):
        error("Use %s UNIFY 1 [...]" % name)

    gbl.tnames[name].setUnify(ln)


""" =================================================================

    Command jump tables. These need to be at the end of this module
    to avoid undefined name errors. The tables are only used in
    the parse() function.

    The first table is for the simple commands ... those which DO NOT
    have a leading trackname. The second table is for commands which
    require a leading track name.

    The alphabetic order is NOT needed, just convenient.

"""

simpleFuncs = {'ADJUSTVOLUME': MMA.volume.adjvolume,
               'AFTER': MMA.after.create,
               'ALLGROOVES': MMA.grooves.allgrooves,
               'ALLTRACKS': allTracks,
               'AUTHOR': MMA.docs.docAuthor,
               'AUTOSOLOTRACKS': MMA.patSolo.setAutoSolo,
               'BEATADJUST': MMA.tempo.beatAdjust,
               'CALL': MMA.func.callFunction,
               'CHANNELPREF': MMA.midifuncs.setChPref,
               'CHORDADJUST': MMA.chords.chordAdjust,
               'CMDLINE': MMA.options.cmdLine,
               'COMMENT': comment,
               'CRESC': MMA.volume.setCresc,
               'CUT': MMA.tempo.cut,
               'DEBUG': MMA.debug.setDebug,
               'DEC': macros.vardec,
               'DECRESC': MMA.volume.setDecresc,
               'DEFALIAS': MMA.grooves.grooveAlias,
               'DEFCHORD': MMA.chords.defChord,
               'DEFCALL': MMA.func.defCall,
               'DEFGROOVE': MMA.grooves.grooveDefine,
               'DELETE': deleteTrks,
               'DOC': MMA.docs.docNote,
               'DOCVAR': MMA.docs.docVars,
               'DRUMVOLTR': MMA.translate.drumVolTable.set,
               'ELSE': ifelse,
               'ENDIF': ifend,
               'ENDMSET': endmset,
               'ENDREPEAT': repeatend,
               'EOF': eof,
               'ERROR': forceError,
               'FERMATA': MMA.tempo.fermata,
               'GOTO': goto,
               'GROOVE': MMA.grooves.groove,
               'GROOVECLEAR': MMA.grooves.grooveClear,
               'IF': macros.varIF,
               'IFEND': ifend,
               'INC': macros.varinc,
               'INCLUDE': include,
               'KEYSIG': keySig.create,
               'LABEL': comment,
               'LYRIC': MMA.lyric.lyric.option,
               'MIDIDEF': MMA.mdefine.mdefine,
               'MIDI': MMA.midifuncs.rawMidi,
               'MIDICOPYRIGHT': MMA.midifuncs.setMidiCopyright,
               'MIDICUE': MMA.midifuncs.setMidiCue,
               'MIDIFILE': MMA.midifuncs.setMidiFileType,
               'MIDIINC': MMA.midiIn.midiinc,
               'MIDIVOLUME': MMA.midifuncs.setMidiVolume,
               'MIDICRESC': MMA.midifuncs.setMidiCresc,
               'MIDIDECRESC': MMA.midifuncs.setMidiDecresc,
               'CHANNELINIT': MMA.midifuncs.setChannelInit,
               'MIDIMARK': MMA.midifuncs.midiMarker,
               'MIDISPLIT': MMA.midi.setSplitChannels,
               'MIDITEXT': MMA.midifuncs.setMidiText,
               'MIDITNAME': MMA.midifuncs.setMidiName,
               'MMAEND': MMA.paths.mmaend,
               'MMASTART': MMA.paths.mmastart,
               'MSET': macros.msetvar,
               'MSETEND': endmset,
               'NEWSET': macros.newsetvar,
               'PATCH': MMA.patch.patch,
               'PLUGIN': MMA.regplug.plugin,
               'PRINT': lnPrint,
               'PRINTACTIVE': printActive,
               'PRINTCHORD': MMA.chords.printChord,
               'REPEAT': repeat,
               'REPEATEND': repeatend,
               'REPEATENDING': repeatending,
               'RESTART': MMA.sequence.restart,
               'RNDSEED': rndseed,
               'RNDSET': macros.rndvar,
               'SEQ': MMA.sequence.seq,
               'SEQCLEAR': MMA.sequence.seqClear,
               'SEQRND': MMA.seqrnd.setSeqRnd,
               'SEQRNDWEIGHT': MMA.seqrnd.setSeqRndWeight,
               'SEQSIZE': MMA.sequence.seqsize,
               'SET': macros.setvar,
               'SETINCPATH': MMA.paths.setIncPath,
               'SETLIBPATH': MMA.paths.setLibPath,
               'SETMIDIPLAYER': MMA.player.setMidiPlayer,
               'SETOUTPATH': MMA.paths.setOutPath,
               'SETPLUGPATH': MMA.paths.setPlugPath,
               'SETSYNCTONE': MMA.sync.setSyncTone,
               'SHOWVARS': macros.showvars,
               'STACKVALUE': macros.stackValue,
               'SWELL': MMA.volume.setSwell,
               'SWINGMODE': MMA.swing.swingMode,
               'SYNCHRONIZE': MMA.sync.synchronize,
               'TEMPO': MMA.tempo.tempo,
               'TIME': MMA.tempo.setTime,
               'TIMESIG': timeSig.setSig,
               'TONETR': MMA.translate.dtable.set,
               'TRUNCATE': MMA.truncate.setTruncate,
               'TWEAKS': MMA.tweaks.setTweak,
               'UNSET': macros.unsetvar,
               'USE': usefile,
               'VARCLEAR': macros.clear,
               'VEXPAND': macros.vexpand,
               'VOICEVOLTR': MMA.translate.voiceVolTable.set,
               'VOICETR': MMA.translate.vtable.create,
               'VOLUME': MMA.volume.setVolume,
               'TRANSPOSE': MMA.keysig.transpose}

trackFuncs = {
    'ACCENT': trackAccent,
    'ARPEGGIATE': trackArpeggiate,
    'ARTICULATE': trackArtic,
    'CHANNEL': trackChannel,
    'CHORDS': trackChords,
    'DUPRIFF': trackDupRiff,
    'MIDIVOLUME': MMA.midifuncs.trackMidiVolume,
    'MIDICRESC': MMA.midifuncs.trackMidiCresc,
    'MIDIDECRESC': MMA.midifuncs.trackMidiDecresc,
    'CHSHARE': trackChShare,
    'COMPRESS': trackCompress,
    'COPY': MMA.grooves.trackCopy,
    'CRESC': trackCresc,
    'CUT': MMA.tempo.trackCut,
    'DECRESC': trackDeCresc,
    'DELAY': trackDelay,
    'DIRECTION': trackDirection,
    'DRUMTYPE': trackDrumType,
    'DUPROOT': trackDupRoot,
    'FORCEOUT': trackForceOut,
    'FRETNOISE': trackPlectrumFretNoise,
    'GROOVE': MMA.grooves.trackGroove,
    'HARMONY': trackHarmony,
    'HARMONYONLY': trackHarmonyOnly,
    'HARMONYVOLUME': trackHarmonyVolume,
    'INVERT': trackInvert,
    'LIMIT': trackChordLimit,
    'MALLET': trackMallet,
    'MIDICLEAR': MMA.midifuncs.trackMidiClear,
    'MIDICUE': MMA.midifuncs.trackMidiCue,
    'MIDIDEF': MMA.mdefine.trackMdefine,
    'MIDIGLIS': MMA.midifuncs.trackGlis,
    'MIDIPAN': MMA.midifuncs.trackPan,
    'MIDISEQ': MMA.midifuncs.trackMidiSeq,
    'MIDITEXT': MMA.midifuncs.trackMidiText,
    'MIDITNAME': MMA.midifuncs.trackMidiName,
    'MIDIVOICE': MMA.midifuncs.trackMidiVoice,
    'MIDIWHEEL': MMA.midifuncs.trackWheel,
    'MOCTAVE': trackMOctave,
    'OCTAVE': trackOctave,
    'OFF': trackOff,
    'ON': trackOn,
    "ORNAMENT": trackOrnament,
    'TUNING': trackPlectrumTuning,
    'CAPO': trackPlectrumCapo,
    'SHAPE': trackPlectrumShape,
    'RANGE': trackRange,
    'RDURATION': trackRduration,
    'RESTART': MMA.sequence.trackRestart,
    'RIFF': trackRiff,
    'RSKIP': trackRskip,
    'RTIME': trackRtime,
    'RVOLUME': trackRvolume,
    'RPITCH':  MMA.rpitch.setRPitch,
    'SCALETYPE': trackScaletype,
    'SEQCLEAR': MMA.sequence.trackSeqClear,
    'SEQRND': MMA.sequence.trackSeqRnd,
    'SEQUENCE': MMA.sequence.trackSequence,
    'SEQRNDWEIGHT': MMA.sequence.trackSeqRndWeight,
    'STRETCH': trackStretch,
    'STICKY': trackSticky,
    'SWELL': trackSwell,
    'TRIGGER': MMA.trigger.setTrigger,
    'MIDINOTE': MMA.midinote.parse,
    'NOTESPAN': trackSpan,
    'STRUM': trackStrum,
    'STRUMADD': trackStrumAdd,
    'TONE': trackTone,
    'UNIFY': trackUnify,
    'VOICE': trackVoice,
    'VOICING': trackVoicing,
    'VOLUME': trackVolume,
    'DEFINE': trackDefPattern}

dataFuncs = {}

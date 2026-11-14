# midiIn.py

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
import MMA.file
import MMA.debug
from   MMA.common import *

from   MMA.alloc import trackAlloc
from   MMA.readmidi import MidiData

from   MMA.midiM import packBytes

### FIXME ... some truly ugly code follows!!!

######################################################
## Main function, called from parser.

def midiinc(ln):
    """ Include a MIDI file into MMA generated files. """

    filename = ''
    doLyric = False
    doText = False
    channels = []
    transpose = None
    stripSilence = -1   # Important! Don't use True or 1 since positive # are option
    report = False
    istart = 0          # istart/end are in ticks
    iend = 0xffffff     # but are set in options in Beats
    insertOffset = 0          # where in the current stream to insert (like BeatAdjust)
    verbose = False
    octAdjust = 0
    velAdjust = 100
    ignorePC = True   # ignore imported PC commands before insert point
    stretch = None

    notopt, ln = opt2pair(ln)

    if notopt:
        error("MidiInc: Expecting cmd=opt pairs, not '%s'." % ' '.join(notopt))

    for cmd, opt in ln:
        cmd = cmd.upper()

        if cmd == 'FILE':
            filename = MMA.file.fixfname(opt)

        elif cmd == 'VOLUME':
            velAdjust = stoi(opt)

        elif cmd == 'OCTAVE':
            octAdjust = stoi(opt)
            if octAdjust < -4 or octAdjust > 4:
                error("MidiInc: 'Octave' adjustment must be -4 to 4, not %s" % opt)
            octAdjust *= 12

        elif cmd == 'TRANSPOSE':
            transpose = stoi(opt)
            if transpose < -24 or transpose > 24:
                error("MidiInc: 'Transpose' must be -24 to 24, not %s" % opt)

        elif cmd == 'START':
            istart = stotick(opt, 'B', "MidiInc Start: '%s' is not recognized." % opt)
            if istart < 0:
                error("MidiInc: 'Start' must be > 0.")

        elif cmd == 'END':
            iend = stotick(opt, 'B', "MidiInc End: '%s' is not recognized." % opt)
            if iend < 0:
                error("MidiInc: 'End' must be > 0.")

        elif cmd == 'OFFSET':
            insertOffset = stotick(opt, 'B', "MidiInc Offset: '%s' is not recognized." % opt)
            if gbl.tickOffset + insertOffset < 0:
                error("MidiInc: 'Offset' cannot point before start.")
                
        elif cmd == 'TEXT':
            doText = getTF(opt, "MidiInc 'Text'")

        elif cmd == 'LYRIC':
            doLyric = getTF(opt, "MidiInc 'Lyric'")

        elif cmd == "REPORT":
            report = getTF(opt, "MidiInc 'Report'")

        elif cmd == "VERBOSE":
            verbose = getTF(opt, "MidiInc 'Verbose'")

        elif cmd == "STRIPSILENCE":
            opt = opt.upper()
            if opt in ("OFF", 'FALSE', '0'):
                stripSilence = False
            elif opt in ("TRUE", "ON"):  # this is the default
                stripSilence = -1  # Don't use TRUE, positive values are important
            else:
                stripSilence = stoi(opt, "MIdiInc StripSilence= expecting "
                                    "'value', 'On' or 'Off', not %s" % opt)


        elif cmd == "IGNOREPC":
            ignorePC = getTF(opt, "MidiInc 'IgnorePC'")

        elif cmd == "STRETCH":
            v = stof(opt)
            if v < 1 or v > 500:
                error("MidiInc: 'Stretch' range of 1 to 500, not %s." % opt)
            stretch = v/100.

        # If none of the above matched a CMD we assume that it is
        # a trackname. Keep this as the last test!

        else:
            trackAlloc(cmd, 0)
            if not cmd in gbl.tnames:
                error("MidiInc: %s is not a valid MMA track" % cmd)

            opt = opt.split(',')
            riffmode = 0
            printriff = 0
            ch = None
            for o in opt:
                o = o.upper()
                if o == 'RIFF':
                    riffmode = 1
                elif o == 'SEQUENCE':
                    riffmode = 2
                elif o == 'PRINT':
                    printriff = 1
                    if not riffmode:
                        riffmode = 1
                else:
                    if ch is not None:
                        error("MidiInc: Only one channel assignment per track.")
                    ch = stoi(o)

            if ch < 1 or ch > 16:
                error("MidiInc: MIDI channel for import must be 1..16, not %s" % ch)

            channels.append((cmd, ch-1, riffmode, printriff))

    # If transpose was NOT set, use the global transpose value
    # Note special riff value as well. Need to double adjust since
    # the riff import will do its own adjustment.
    # this needs to be done BEFORE reading the midi file

    if transpose is None:
        transpose = gbl.transpose
        riffTranspose = -gbl.transpose
    else:
        riffTranspose = 0
    octAdjust += transpose    # this takes care of octave and transpose

    
    mf = MidiData()
    mf.octaveAdjust = octAdjust
    mf.velocityAdjust = velAdjust
    mf.ignorePC = ignorePC

    try:
        mf.readFile(filename)
    except RuntimeError as e:
        error("MidiInc: %s" % e)

    if mf.beatDivision != gbl.BperQ:
        warning("MIDI file '%s' tick/beat of %s differs from MMA's "
                "%s. Will try to compensate" % 
                (filename, mf.beatDivision, gbl.BperQ))
        mf.adjustBeats( gbl.BperQ / float(mf.beatDivision))

    if report or verbose:  # try to be helpful
        print("MIDI File %s successfully read." % filename)
        print("Total Text events: %s" % len(mf.textEvents))
        print("Total Lyric events: %s" % len(mf.lyricEvents))
        print('\n')

        for ch in sorted(mf.events.keys()):
            if not mf.events[ch]:
                continue

            if verbose and not report:   # in verbose mode only list info for tracks we're using
                doit = 0
                for z in channels:
                    if z[1] == ch:
                        doit = 1
                        break
                
                if not doit:
                    continue

            fnote = fevent = 0xffffff
            ncount = 0
            for ev in mf.events[ch]:
                delta = ev[0]
                if delta < fevent:
                    fevent = delta
                if ev[1] >> 4 == 0x9:
                    if delta < fnote:
                        fnote = delta
                    if ev[3]:
                        ncount += 1
            msg = ["Channel %2s: First event %-8s" % (ch+1, fevent)]
            if ncount:
                msg.append("First Note %-8s Total Notes %-4s" % (fnote, ncount))
            print(' '.join(msg))

        if report:
            print("\nNo data generated!")
            sys.exit(0)
        
    if not channels:
        if doLyric or doText:
            warning("MidiInc: no import channels specified, "
                    "only text or lyrics imported")
        else:
            error("MidiInc: A channel to import and a destination "
                  "track must be specified")

    if (istart >= iend) or (istart < 0) or (iend < 0):
        error("MidiInc: Range invalid, start=%s, end=%s" % (istart, iend))

    if MMA.debug.debug:
        dPrint("MidiInc: File=%s, Volume=%s, Octave=%s, Transpose=%s, Lyric=%s, " 
            "Text=%s, Range=%sT..%sT StripSilence=%sT Offset=%sT Verbose=%s" 
            % (filename, velAdjust, octAdjust, transpose, doLyric, doText,
               istart, iend, stripSilence, insertOffset, verbose))
        msg = []
        for t, ch, riffmode, riffprint in channels:
            o = ''
            if riffmode == 1:
                o = ',riff'
            elif riffmode == 2:
                o = ',sequence'
            elif printriff:
                o += ',print'
            msg.append("MidiInc: Channel %s-->%s%s" % (ch+1, t, o))
        dPrint(' '.join(msg))

    if stretch:
        if verbose:
            print("Applying stretch to all events. Deltas will be multiplied by %s" % stretch)

        for tr in mf.events:
            for e in mf.events[tr]:
                e[0] = int(e[0] * stretch)   # e[0] is the offset

        for e in mf.textEvents:
            e[0] = int(e[0] * stretch)

        for e in mf.lyricEvents:
            e[0] = int(e[0] * stretch)

    # Midi file parsed, add selected events to mma data

    if stripSilence == False:
        if verbose:
            print("Firstnote offset was %s. Being reset to start of file by StripSilence=Off." 
                % mf.firstNote)
        mf.firstNote = 0

    if verbose:
        print("First note offset: %s" % mf.firstNote)

    if doText:
        inst = 0
        disc = 0
        if verbose:
            print("Scanning %s textevents." % len(mf.textEvents))
        for tm, tx in mf.textEvents:
            delta = tm-mf.firstNote
            if delta >= istart and delta <= iend:
                gbl.mtrks[0].addText(gbl.tickOffset + insertOffset + delta, tx)
                inst += 1
            else:
                disc += 1

        if MMA.debug.debug:
            dPrint("MidiInc text events: %s inserted, %s out of range." % (inst, disc))

    if doLyric:
        inst = 0
        disc = 0
        if verbose:
            print("Scanning %s LyricEvents." % len(mf.lyricEvents))
        for tm, tx in mf.lyricEvents:
            delta = tm-mf.firstNote
            if delta >= istart and delta <= iend:
                gbl.mtrks[0].addLyric(gbl.tickOffset + insertOffset + delta, tx)
                inst += 1
            else:
                disc += 1
        if MMA.debug.debug:
            dPrint("MidiInc lyric events: %s inserted, %s out of range." % (inst, disc))

    for n, c, riffmode, printriff in channels:
        if not len(mf.events[c]):
            warning("No data to assign from imported channel %s to track %s" % (c+1, n))

    inst = 0
    disc = 0

    for tr, ch, riffmode, printriff in channels:
        onNotes = []
        if gbl.tnames[tr].disable:   # skip if disabled track

            if verbose:
                print("Skipping import of channel %s since track %s is disabled." 
                    % (ch, tr))
            continue

        t = gbl.tnames[tr]
        if not t.channel:
            t.setChannel()

        if riffmode:
            riff = []
            if t.vtype not in ('MELODY', 'SOLO'):
                error("MidiInc: Riff only works on Melody/Solo tracks, not '%s'." % t.name)

        t.clearPending()
        if t.voice[0] != t.ssvoice:
            gbl.mtrks[t.channel].addProgChange(gbl.tickOffset + insertOffset,
                                               t.voice[0], t.ssvoice)

        channel = t.channel
        track = gbl.mtrks[channel]

        if verbose or 1:
            print("Parsing imported file. Channel=%s Track=%s MIDI Channel=%s" 
                  % (ch, tr, channel))
            if len(mf.events[ch]):
                print(" Total events: %s; Event range: %sT %sT; Start/End Range: %sT %sT" 
                      % (len(mf.events[ch]), mf.events[ch][0][0], 
                        mf.events[ch][-1][0], istart, iend))
            else:
                print("No events in Channel %s" % ch)

        
        # If we're processing midi voice changes (ignorePC=False) and there
        # are events BEFORE the first note, we need to insert
        # them before the notes. We put them all at the start offset.
        if ignorePC==False:
            for ev in mf.events[ch]:
                if ev[0] > mf.firstNote:
                    break
                if ev[1] >> 4 == 0xc:
                    track.addToTrack(gbl.tickOffset + insertOffset,
                                     packBytes(ev[1] | channel-1, *ev[2:]))
                    inst += 1
                    disc -= 1

        for ev in mf.events[ch]:
            delta = ev[0]-mf.firstNote
            
            if delta >= istart and delta <= iend:
                if riffmode:
                    offset = delta-istart
                    x = ev[1] >> 4
                    if x != 0x09 and x != 0x08:  # skip non note events
                        continue
                    pitch = ev[2]
                    velocity = ev[3]
                    if x == 0x8:
                        velocity = 0
                    riff.append([offset, pitch, velocity])

                else:
                    offset = gbl.tickOffset + insertOffset + (delta-istart)
                    # add note on/off, key pressure, etc.
                    track.addToTrack(offset, packBytes(ev[1] | channel-1, *ev[2:]))

                    # Track on/off events to avoid stuck midi notes.
                    x = ev[1] >> 4
                    if x == 0x09 and ev[3] and ev[2] not in onNotes:
                        onNotes.append(ev[2])  # append this pitch to onNotes
                    if (x == 0x09 and not ev[3] or x == 0x08) and (ev[2] in onNotes):
                        onNotes.remove(ev[2])  # remove this as being ON
                        
                inst += 1
            else:
                disc += 1

        if onNotes:
            for x in onNotes:
                track.addToTrack(offset, packBytes(0x90 | channel-1, [x,0]))
            warning("MidiINC: Stuck MIDI note(s) '%s' turned off in %s." % 
                    (', '.join([str(x) for x in onNotes]), tr))

        if riffmode:
            evlist = createRiff(riff, tr, riffTranspose)

            if riffmode == 2:
                txt = []
            for a in sorted(evlist):
                if printriff and riffmode == 1:
                    print("%s Riff %s" % (tr, evlist[a]))
                elif riffmode == 2:   # sequence mode, create sequence line and push into input
                    txt.append("{%s}" % evlist[a])
                else:   # riffmode==1, printriff=0 - just add to the riff stack
                    gbl.tnames[tr].setRiff(evlist[a])

            if riffmode == 2 and txt:
                if printriff:
                    print("%s Sequence %s" % (tr, ' '.join(txt)))
                else:
                    MMA.sequence.trackSequence(tr, txt)

    if MMA.debug.debug:
            dPrint("MidiInc events: %s inserted, %s out of range." % (inst, disc))


def createRiff(riff, tname, riffTranspose):

    # convert list of ON values to durations. We need to
    # look at each event and, if an on-event, search forward
    # for an off. Subtract 2 times and save in new list.

    if gbl.tnames[tname].riff:
        error("MidiInc: Data already pending for %s." % tname)

    missed = 0
    events = []
    riff.sort()
    for i in range(len(riff)):
        duration = None
        offset, pitch, velocity = riff[i]
        if velocity:
            for t in range(i, len(riff)):
                off1, pitch1, vel1 = riff[t]
                if not vel1 and pitch1 == pitch:
                    duration = off1 - offset
                    break
            if duration:
                if riffTranspose:
                    pitch += riffTranspose
                    while pitch > 127:
                        pitch -= 12
                    while pitch < 0:
                        pitch += 12
                events.append([offset, duration, pitch, velocity])

            else:
                missed += 1

    if missed:
        warning("MidiInc Riff: conversion missed %s notes in track %s" % (missed, tname))

    # We have a list of events: [offset, duration, pitch, velocity]...
    # create yet another list with the events put into bars. Easier
    # this time to use a dict

    tickBar = gbl.barLen
    bars = {}
    for offset, duration, pitch, velocity in events:
        b = (offset // tickBar)
        if not b in bars:
            bars[b] = ''
        if int(offset % tickBar) + duration > gbl.barLen:
            eol = "~;"
        else:
            eol = ";"
        bars[b] += "<Offset=%s> %st %s/%s %s" % \
            (int(offset % tickBar), duration, pitch, velocity, eol)

    # Ensure that all bars in the riff pushback data have something.
    # Otherwise the MIDI gets out of sync with the chords. This happens
    # when there are rest bars in the imported data. We just step though
    # and create mma rest bars for the missing ones.

    if not len(bars):
        bars = {0: "4r;"}
    for b in range(0, sorted(bars.keys())[-1], 1):
        if not b in bars:
            bars[b] = "4r;"

        while bars[b].count('~') > 1:
            bars[b] = bars[b].replace('~', '', 1)

    return bars

# parseCL.py

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


This module parses a chordline and sets the timing offsets for 
each "tab". 

"""

from . import gbl
from MMA.common import *

import MMA.truncate

# This table is passed to the track classes. It has
# an instance for each chord in the current bar.

class CTable:
    name = None        # Chord name (used by plectrum track)
    chord = None       # A pointer to the chordNotes structures
    lastchord = None   # chord from previous ctable. Used by trigger()
    chStart = None     # where in the bar the chord starts (in ticks, 0..)
    chEnd = None       # where it ends (in ticks)
    chordZ = None      # set if chord is tacet
    arpeggioZ = None   # set if arpeggio is tacet
    walkZ = None       # set if walking bass is tacet
    drumZ = None       # set if drums are tacet
    bassZ = None       # set if bass is tacet
    scaleZ = None      # set if scale track is tacet
    ariaZ = None       # set if aria track is tacet
    plectrumZ = None   # set if plectrum is tacet

lastChord = None   # tracks last chord for "/ /" data lines.

chordTabs = []  # initialized by MMA.main call to setTime()

# these are the track names for muting
muteTrackNames = 'CBAWDSRP'
muteTrackNamesNoDrum = muteTrackNames.replace('D', '')

def setChordTabs(l):
    """ Set the tab positions for chord parsing.

        This table is set up on each TIME change. Need to
        do it even if the TIME is NOT changed since the table
        positions might. Cheap to do, so not worth worrying.
    """

    global chordTabs

    chordTabs = tuple(( int((x-1) * gbl.BperQ) for x in l ))

def parseChordLine(l):
    """ Parse a line of chord symbols and determine start/end points. """

    global lastChord

    ctable = []               # an entry for each chord in the bar
    quarter = gbl.BperQ       # ticks in a quarter note (== 1 beat)
    if MMA.truncate.length:
        endTime = MMA.truncate.length
    else:
        endTime = (quarter * gbl.QperBar)  # number of ticks in bar

    p = 0                    # our beat counter --- points to tab 0, 1, etc in chordTabs

    for ll in l:
        if '@' in ll:  # we have something like "Cm@3.2"
            ch, beat = ll.split('@', 1)
            beat = stof(beat, "Expecting a value after the @ in '%s'" % ll)
            
            if beat < 1:
                error("Beat after @ must be 1 or greater, not '%s'." % beat)
            if beat >= gbl.QperBar + 1:
                error("Beat after @ must be less than %s, not '%s'." % (gbl.QperBar + 1, beat))

            # tick offset for this chord
            beat = int((beat - 1) * quarter)
            
            # need to set p to next spot in chordTabs[].
            for p, i in enumerate(chordTabs):
                if i > beat:
                    break
        else:
            ch = ll
            if p > len(chordTabs)-1:
                error("Too many chords specified in line. Max is %s. "
                      "For more chords use @ notation or change TIME TABS."
                      % (len(chordTabs)))
            beat = chordTabs[p]

            p += 1  # for next beat

        if ch in '-/':      # handle continuation chords
            if not ctable:
                if lastChord:
                    ch = lastChord
                else:
                    error("No previous chord for '/' or '-' at line start")
            else:  # '/' other than at start just increment the beat counter
                continue

        if ctable:
            if ctable[-1].name == ch:  # skip duplicate chords
                continue

            if ctable[-1].chStart >= beat:
                error("Chord positions out of order")

        else:    # first entry
            if beat != 0:
                error("The first chord must be at beat 1, not %s." % ((beat / quarter) + 1))

        ctab = CTable()
        ctab.name = ch
        ctab.chStart = beat
        if ctable:
            ctab.lastchord = ctable[-1].name
        else:
            ctab.lastchord = lastChord

        # If the chord we just extracted has a 'z' in it then we do the
        # following ugly stuff to figure out which tracks to mute. 'ch'
        # will be a chord name or 'z' when this is done.


        if 'z' in ch:
            if ch.count('z')>1:
                error("Only one 'z' is permitted in the mute shortcut. '%s' is "
                      "illegal." % ch)

            if lastChord and 'z' in lastChord:  # strip off z stuff from prior chord
                lastChord = lastChord.split('z')[0]
                
            c, r = ch.split('z', 1)  # get chord and track list

            if not c:   # no chord specified
                c = 'z'        # dummy chord name to keep chordnotes() happy

                if r == '!':    # 'z!' is fine, mute all
                    r = muteTrackNames
                elif not r:     # 'z' is fine, mute all tracks except Drum
                    r = muteTrackNamesNoDrum
                    
                else:
                    if lastChord:
                        c = lastChord
                        if 'z' in c:
                            c = c.split('z')[0]  # we only want the chord
                    else:
                        error("Unable to find a chord for '%s'. Try specifing the "
                              "chord name." % ch)
                        if not c:
                            error("To use this shortcut to mute individual tracks "
                                  "the chord must be included. "
                                  "Use CHORDz[%s] not '%s'" % (ch, muteTrackNames))


            else:    # illegal CHORD + 'z' or 'z!'
                if r == '!':
                    error("'%s' is illegal. 'z!' mutes all tracks "
                          "so you can't include the chord." % ch)
                elif not r:
                    error("'%s' is illegal. This notation is a shortcut,  You must specify tracks "
                          "if you use a chord." % ch)

            ch = c   # this will be 'z' or the chord part

            # A throwaway '-', indicating "these are the tracks to mute" is
            # permitted for compatibility with the '+' option. If found, we just
            # remove it.

            if '-' in r:
                if r.count('-') > 1 or r.count('+') or r[0] != '-':
                    error("Track mute: Use of a '-' must be at start of line and "
                          "cannot be used with '+' option.")
                r=r[1:]
            
            # If the mute list is started with + we mute the tracks
            # which are not in the supplied list.
            if '+' in r:
                if r.count('+') > 1 or r[0] != '+':
                    error("Track mute: Only 1 + permitted. Must be first character.")
                for a in r[1:]:
                    if a not in muteTrackNames:
                        error("Track mute: track name '%s' not in permitted list '%s'."
                              % (a, muteTrackNames))
                r = r[1:]
                if 'C' not in r:
                    ctab.chordZ = 1
                if 'B' not in r:
                    ctab.bassZ = 1
                if 'A' not in r:
                    ctab.arpeggioZ = 1
                if 'W' not in r:
                    ctab.walkZ = 1
                if 'D' not in r:
                    ctab.drumZ = 1
                if 'S' not in r:
                    ctab.scaleZ = 1
                if 'R' not in r:
                    ctab.ariaZ = 1
                if 'P' not in r:
                    ctab.plectrumZ = 1

            else: # mute only tracks in list ('-' or no option, default)
                for v in r:
                    if v == 'C':
                        ctab.chordZ = 1
                    elif v == 'B':
                        ctab.bassZ = 1
                    elif v == 'A':
                        ctab.arpeggioZ = 1
                    elif v == 'W':
                        ctab.walkZ = 1
                    elif v == 'D':
                        ctab.drumZ = 1
                    elif v == 'S':
                        ctab.scaleZ = 1
                    elif v == 'R':
                        ctab.ariaZ = 1
                    elif v == 'P':
                        ctab.plectrumZ = 1
                    else:
                        error("Track mute: track name '%s' not in permitted list '%s'."
                              % (v, muteTrackNames))

        ctab.chord = MMA.chords.ChordNotes(ch)  # Derive chord notes (or mute)
        ctable.append(ctab)

    # Finished each chord in data line, test
    # to see that all chords are in range.
    if ctable[-1].chStart >= endTime:
        error("Maximum offset for chord '%s' must be less than %s, not '%s'." %
              (ctable[-1].name, endTime / quarter + 1, ctable[-1].chStart / quarter + 1))

    # Fix up some pointers.

    for i, v in enumerate(ctable[:-1]):  # set end range for each chord
        ctable[i].chEnd = ctable[i + 1].chStart

    ctable[-1].chEnd = endTime      # set end of range for last chord
    lastChord = ctable[-1].name     # remember chord at end of this bar for next
    
    return ctable


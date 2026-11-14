# swing.py

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
from MMA.common import *
import MMA.debug
from MMA.notelen import noteLenTable

mode = 0      # defaults to 0, set to 1 for swing mode
skew = None   # this is just for $_SwingMode macro
accent1 = 1      # velocity % adjustments for 1st/2nd notes of swing pattern
accent2 = 1
delay1 = 0      # value, in ticks, for additional delay
delay2 = 0
noteValue = 8    # this can be 8 or 16 for 8th swing or 16th swing

# These 2 funcs are called by the groove save/restore funcs. They
# are used just to make the groove code a bit more readable.


def gsettings():
    return (mode, skew, accent1, accent2, delay1, delay2, noteLenTable['81'], noteLenTable['82'], noteValue)


def grestore(s):
    global mode, skew, accent1, accent2, delay1, delay2, noteValue

    mode, skew, accent1, accent2, delay1, delay2, \
        noteLenTable['81'], noteLenTable['82'], noteValue = s


def swingMode(ln):
    """ Enable/Disable Swing timing mode. """

    global skew, mode, accent1, accent2, delay1, delay2, noteValue

    emsg = "Use: SwingMode [ ON | 1, OFF | 0, SKEW=nn | Accent=nn,nn | Delay=nn,nn | Notes=8|16 ]."

    if not ln:
        error(emsg)

    ln, opts = opt2pair(ln, toupper=True)

    for v in ln:
        if v in ("ON", "1"):
            mode = 1
            continue

        elif v in ("OFF", "0"):
            mode = 0
            continue

        else:
            error(emsg)

    for v, o in opts:
        if v == 'SKEW':
            skew = o
            a = int(stoi(o) * gbl.BperQ / 100)
            noteLenTable['81'] = a
            noteLenTable['82'] = gbl.BperQ - a

        elif v == 'ACCENT':
            if o.count(',') != 1:
                error("Swingmode: ACCENT expecting comma separated values, not '%s'." % o)
            a1, a2 = o.split(',')
            a1 = stoi(a1)
            a2 = stoi(a2)
            if a1 < 1 or a1 > 200 or a2 < 1 or a2 > 200:
                error("Swingmode: Both ACCENT values must be 1..200, not %s,%s."
                      % (a1, a2))

            accent1 = a1 / 100.
            accent2 = a2 / 100.

        elif v == 'DELAY':
            if o.count(',') != 1:
                error("Swingmode: DELAY expecting comma separated values, not '%s'." % o)
            a1, a2 = o.split(',')
            a1 = stoi(a1)
            a2 = stoi(a2)
            if a1 < -20 or a1 > 20 or a2 < -20 or a2 > 20:
                error("Swingmode: Both DELAY values must be -20..20, not %s,%s."
                      % (a1, a2))

            delay1 = a1
            delay2 = a2

        elif v == 'NOTES':
            o = stoi(o)

            if o not in (8, 16):
                error("Swingmode: NOTES expecting 8 or 16, not '%s'." % o)

            noteValue = o

        else:
            error(emsg)

    if MMA.debug.debug:
        dPrint("SwingMode: Status=%s; Accent=%s,%s; Delay=%s,%s; Skew Note lengths: " 
            "%s and %s ticks. Notes=%s" % 
            (mode, int(accent1 * 100), int(accent2 * 100), delay1, delay2,
             noteLenTable['81'], noteLenTable['82'], noteValue))


def settings():
    """ Return string of current settings. For macros. """

    if mode:
        a = "On"
    else:
        a = "Off"

    return "%s Accent=%s,%s Delay=%s,%s Skew=%s Notes=%s" % \
        (a, int(accent1 * 100), int(accent2 * 100), delay1, delay2, skew, noteValue)


def getBeats():
    """ Calc on and off beats for swing. This will work if "notevalue" is
        set to 8 or 16.
    """

    len8 = noteLenTable['8']
    len81 = noteLenTable['81']
    len82 = noteLenTable['82']

    rng = int(gbl.QperBar)
    cnt = gbl.BperQ

    if noteValue == 16:
        len8 /= 2
        len81 /= 2
        len82 /= 2
        rng *= 2
        cnt /= 2

    onBeats = [x * cnt for x in range(rng)]
    offBeats = [(x * cnt + len8) for x in range(rng)]

    return (len8, len81, len82, onBeats, offBeats)


def pattern(plist, vtype):
    """ Do swing adjustments for pattern defs. """

    len8, len81, len82, onBeats, offBeats = getBeats()

    for p in plist:
        if p.duration == len8 or (vtype == "DRUM" and p.duration == 1):
            if p.offset in onBeats:
                if p.duration == len8:
                    p.duration = len81
                    adj = accent1
                    if isinstance(p.vol, list):
                        p.vol = [x * adj for x in p.vol]
                    else:
                        p.vol *= adj
                    p.offset += delay1

            elif p.offset in offBeats:
                if p.duration == len8:
                    p.duration = len82
                    adj = accent2
                    if isinstance(p.vol, list):
                        p.vol = [x * adj for x in p.vol]
                    else:
                        p.vol *= adj
                i = offBeats.index(p.offset)
                p.offset = onBeats[i] + len81 + delay2

    return plist


def swingSolo(notes):
    """ Adjust an entire bar of solo note chords for swingmode.

        Check each chord in the array of chords for a bar for
        successive 8ths on & off the beat. If found, the first is
        converted to 'long' 8th, the 2nd to a 'short'
        and the offset for the 2nd is adjusted to comp. for the 'long'.

        If there is a spurious offset between an on/off beat that pair
        will NOT be adjusted. Not sure if that is right or not?

        Only called from getLine(), this is a separate function for sanity.
    """

    len8, len81, len82, onBeats, offBeats = getBeats()

    nl = sorted(notes)   # list of offsets

    for i in range(len(nl) - 1):

        # Check for successive note event offsets on 8th note positions

        if nl[i] in onBeats and nl[i + 1] == nl[i] + len8:
            beat0 = nl[i]
            beat1 = nl[i + 1]

            # check that all notes are 8ths by comparing a set of all
            # the durations in both offsets with set([len8])

            if set([nev.duration for nev in notes[beat0] + notes[beat1]]) == set([len8]):

                # lengthen notes on-the-beat

                for nev in notes[beat0]:
                    nev.duration = len81
                    nev.velocity *= accent1
                    nev.defvelocity *= accent1

                # if we have a delay for the first note we push
                # the whole array by the correct value.

                if delay1:
                    notes[beat0 + delay1] = notes[beat0]
                    del notes[beat0]

                # shorten notes off-the-beat

                for nev in notes[beat1]:
                    nev.duration = len82
                    nev.velocity *= accent2
                    nev.defvelocity *= accent2

                # move notes off-the-beat to the proper offset.
                src = beat1
                dest = beat0 + len81 + delay2
                if src != dest:
                    notes[dest] = notes[src]
                    del notes[src]

    return notes


# This forces our skew value default and in the process
# it sets the durations for the 81/82 notes

swingMode(['Skew=66'])

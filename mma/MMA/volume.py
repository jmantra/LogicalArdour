

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

from MMA.common import *
import MMA.debug
import re

""" Volumes are specified in musical terms, but converted to
    midi velocities. This table has a list of percentage changes
    to apply to the current volume. Used in both track and global
    situations. Note that the volume for 'ffff' is 200%--this will
    most likely generate velocities outside the midi range of 0..127.
    But that's fine since mma will adjust volumes into the valid
    range. Using very high percentages will ensure that 'ffff' notes
    are (most likely) sounded with a maximum velocity.
"""

vols = {'OFF': 0.00, 'PPPP': 0.05, 'PPP': 0.10,
        'PP': 0.25, 'P': 0.40, 'MP': 0.70,
        'M': 1.00, 'MF': 1.10, 'F': 1.30,
        'FF': 1.60, 'FFF': 1.80, 'FFFF': 2.00}

volume = vols['M']        # default global volume
nextVolume = None         # main parser sets this to the next volume
                          # when future volumes are stacked. It's used
                          # by the volume adjust to smooth out (de)crescendos.
lastVolume = volume
futureVol = []
vTRatio = .6
vMRatio = 1 - vTRatio


def adjvolume(ln):
    """ Adjust the ratio used in the volume table and track/global ratio. """

    global vols, vTRatio, vMRatio

    if not ln:
        error("Use: AdjustVolume DYN=RATIO [..]")

    notopt, ln = opt2pair(ln, toupper=True)

    if notopt:
        error("ADJUSTVOLUME: Expecting DYNAMIC=RATIO pairs")

    for v, r in ln:
        if v == 'RATIO':
            r = stof(r)

            if r < 0 or r > 100:
                error("ADJUSTVOLUME RATIO: value must be 0 to 100")

            vTRatio = r / 100
            vMRatio = 1 - vTRatio

        elif v in vols:
            vols[v] = calcVolume(r, vols[v])

        else:
            error("ADJUSTVOLUME DYNAMIC: '%s' for AdjustVolume is unknown" % v)

    if MMA.debug.debug:
        dPrint("Volume Ratio: %s%% Track / %s%% Master" % (vTRatio * 100, vMRatio * 100))
        dPrint("Volume table: %s" % 
              ' '.join([ "%s=%s" % (a, int(vols[a] * 100)) for a in sorted(vols)]))


calcVolumeRePat = re.compile(
    # This is a regular expression to parse the input for the calcVolume
    # function. The details are embedded in the comments below.
    # Thanks to Johan Vromans!

    # Note, there are 2 parts to this. It's either numeric
    # or mnemonic. We use a | to join the 2 halves.
    # opt. +/- (assigned to 'pre'), numeric value ('val'), and optional % to 'post'
    # Note the '$' terminator which forces NUMERIC[%] to be end.
    r'(?P<pre>[-+])?(?P<val>[\d.]+)(?P<post>%)?$'
    + '|' +
    # mnemonic is assigned to 'mn'.
    r'(?P<mn>[OFPM]+)$',re.IGNORECASE )

def calcVolume(new, old):
    """ Calculate a new volume "new" possibly adjusting from "old". """

    m = calcVolumeRePat.match(new)
    if m is None:
        error("Unknown volume '%s'" % new)

    # Do we have a mnemonic?

    mn = m.group('mn')
    if mn:
        mn = mn.upper()
        if not mn in vols:
            error("Unknown volume mnemonic '%s'" % mn)
        return vols[mn]

    # So it must be a value.
    val  = m.group('val')
    pre  = m.group('pre')
    post = m.group('post')

    if pre and not post:
        warning("Please use '%s%s%%' if you want to %screase the volume"
                % (pre, val, "in" if pre == '+' else "de"))

    v = stof(val, "Volume expecting value, not '%s'" % val) / 100.

    if pre == '+':
        v = old * ( 1 + v )
    elif pre == '-':
        v = old * ( 1 - v )
    elif post == '%':
        v = old * ( v )

    return v

def setVolume(ln):
    """ Set master volume. """

    global volume, lastVolume, futureVol

    if len(ln) != 1:
        error("Use: Volume DYNAMIC")

    volume = calcVolume(ln[0], volume)

    futureVol = []
    if MMA.debug.debug:
        dPrint("Volume: %s%%" % (100 * volume))


# The next 3 are called from the parser.

def setCresc(ln):
    """ Master Crescendo. """

    setCrescendo(1, ln)


def setDecresc(ln):
    """ Master Decrescendo (Diminuendo). """
    setCrescendo(-1, ln)


def setSwell(ln):
    """ Set a swell (cresc<>decresc). """

    global futureVol, volume, lastVolume

    lastVolume = volume

    if len(ln) == 3:            # 3 args, 1st is intial setting
        setVolume([ln[0]])
        ln = ln[1:]

    if len(ln) != 2:
        error("Swell expecting 2 or 3 args.")

    count = stoi(ln[1])
    if count < 2:
        error("Swell bar count must be 2 or greater.")

    if count % 2:
        c = (count + 1) // 2
        offset = 1
    else:
        c = count // 2
        offset = 0

    c = str(c)

    futureVol = fvolume(0, volume, [ln[0], c])
    futureVol.extend(fvolume(0, futureVol[-1],
                             [str(int(volume * 100)), c])[offset:])

    if MMA.debug.debug:
        dPrint("Set Swell to: %s" % ' '.join([str(int(a * 100)) for a in futureVol]))


def setCrescendo(dir, ln):
    """ Combined (de)cresc() """

    global futureVol, volume, lastVolume

    lastVolume = volume

    if len(ln) not in (2, 3):
        error("Usage: (De)Cresc [start-Dynamic] final-Dynamic bar-count")

    if len(ln) == 3:
        setVolume([ln[0]])
        ln = ln[1:]

    futureVol = fvolume(dir, volume, ln)

    if MMA.debug.debug:
        dPrint("Set (De)Cresc to: %s" % ' '.join([str(int(a * 100)) for a in futureVol]))

# Used by both the 2 funcs above and from TRACK.setCresc()


def fvolume(dir, startvol, ln):
    """ Create a list of future vols. Called by (De)Cresc. """

    # Get destination volume

    destvol = calcVolume(ln[0], startvol)

    bcount = stoi(ln[1], "Type error in bar count for (De)Cresc, '%s'" % ln[1])

    if bcount <= 0:
        error("Bar count for (De)Cresc must be postive")

    # Test to see if (de)cresc is contrary to current settings.
    # Using 'dir' of 0 will bypass this (used by SWELL).

    if dir > 0 and destvol < startvol:
        warning("Cresc volume less than current setting")

    elif dir < 0 and destvol > startvol:
        warning("Decresc volume greater than current setting")

    elif destvol == startvol:
        warning("(De)Cresc volume equal to current setting")

    if bcount > 1:
        bcount -= 1
    step = (destvol - startvol) / bcount
    volList = [startvol]

    for a in range(bcount - 1):
        startvol += step
        volList.append(startvol)

    volList.append(destvol)

    return volList


def calcMidiVolume14(s):
    """ Convert a mnemonic volume to value for MIDI channel.
        This function uses a 14 bit (0..0x3fff). See below for
        the 7 bit version.
    """

    s = s.upper()
    if s in vols:
        v = int(0x1fff * vols[s])
        if v < 0:
            v = 0
        if v > 0x3fff:
            v = 0x3fff

    else:
        v = stoi(s, "Expecting integer arg or volume mnemonic, not %s" % s)

    return v


def calcMidiVolume(s):
    """ Convert a mnemonic volume to value for MIDI channel. """

    s = s.upper()
    if s in vols:
        v = int(80 * vols[s])
        if v < 0:
            v = 0
        if v > 127:
            v = 127

    else:
        v = stoi(s, "Expecting integer arg or volume mnemonic, not %s" % s)

    return v

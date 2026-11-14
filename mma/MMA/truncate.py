# truncate.py

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


This code just sets up truncate. The heavy lifting is done in pat.py/bar()
where the sequence for each track is re-created with adjusted offsets.
In parse.py/parse() we adjust the song pointer for the current seq size.

"""

from MMA.common import *
import MMA.debug

length = None
count = None
side = None


def setTruncate(ln):
    """ Set the truncate variable for the next bar. """

    global length, count, side

    if length:
        warning("Truncate: option set with value pending, previous setting discarded.")

    side = 0    # assume 'right' or start of bar
    count = 1    # assume 1 bar only

    ln, opts = opt2pair(ln)   # separate out the option strings

    # Grab the truncate length first, need this to figure the
    # value for the side option, later.

    if len(ln) != 1:
        error("Truncate: Beats must be set. Syntax is <beats> [option=value]")

    beats = stof(ln[0], "Truncate: Bar length must be value.")

    if beats <= 0 or beats >= gbl.QperBar:
        error("Truncate: Range must be >0 and <=%s, not '%s'." % (gbl.QperBar, beats))

    length = int(beats * gbl.BperQ)

    # now parse options

    for cmd, opt in opts:
        cmd = cmd.upper()

        if cmd == 'COUNT':
            b = stoi(opt, "Truncate: Bar COUNT must be integer.")
            if b < 1:
                error("Truncate: Bar COUNT must be 1 or greater.")
            count = b

        elif cmd == "SIDE":
            opt = opt.upper()
            max = gbl.barLen

            if opt == "LEFT":   # side to use, default==left
                side = 0

            elif opt == "RIGHT":  # use the right side of pattern
                side = max - length

            else:
                opt = stof(opt, "Truncate: Expecting value, not '%s'." % opt)
                side = int((opt - 1) * gbl.BperQ)
                if side >= gbl.barLen:
                    error("Truncate: Side value of '%g' too large." % opt)

        else:
            error("Truncate: '%s' is an unknown option." % cmd)

    if MMA.debug.debug:
        dPrint("Truncate: Next %s bar(s) are %g beats, "
              "using pattern from beats %g to %g."
            % (count, beats, float(side) / gbl.BperQ, (float(side) + length) / gbl.BperQ))


def countDown():
    """ Decrement the bar count. Called from parse.  """

    global length, count, side

    count -= 1
    if count <= 0:
        count = None
        length = None
        side = None

# timesig.py

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

Timesig manager. All timesig stuff is here, except for the Mtrk.setTimeSig
class function. For a function which has no effect, it appears to be
a lot of code. But some sequencers and notation programs absolutely require
proper time sigs for correct operation. So, here you go.
"""

from . import gbl
import MMA.midi
from   MMA.common import *

class TimeSig:
    """ Track and set the current time signature.

        Timesigs are completely optional and are inserted into
        the MIDI file by addTimeSig(). MMA routines ignore timesig
        settings.

        NOTE: The actual func to place a timesig meta into the midi 
              stream is not here. It's part of the Mtrk() class.
    """

    def __init__(self):
        """ Initialze to null value, user will never set to this."""

        self.lastsig = (None, None)


    def create(self, nn, dd):
        """ Set timesig. If no change from last value, ignore. """

        if self.lastsig == (nn, dd):
            return

        cc = 48  # apparently clocks per beat, don't understand so just use default
        bb = 8   # number of 32nd notes in quarter. Is it ever not 8?
        gbl.mtrks[0].addTimeSig(gbl.tickOffset, nn, dd, cc, bb)
        self.lastsig = (nn, dd)


    def setSig(self, ln):
        """ Set the midi time signature from parser. """

        if len(ln) == 1:
            a = ln[0].upper()
            if a == 'COMMON':
                ln = ('4', '4')
            elif a == 'CUT':
                ln = ('2', '2')
            elif '/' in ln[0]:
                ln = ln[0].split('/',1)

        if len(ln) != 2:
            error("TimeSig: Usage (numerator denominator) or ('cut' or 'common')")

        nn = stoi(ln[0])

        if nn < 1 or nn > 126:
            error("Timesig: Numerator must be 1..126")

        try:
            dd = {'1':0, '2':1, '4':2, '8':3, '16':4, '32':5, '64':6, '128':7 }[ln[1]]
        except:
            error("Timesig: Denominator must be 1, 2, 4, 8, 16, 32, 64 or 128ot '%s'." % ln[1])

        self.create(nn, dd)


    def get(self):
        """ Return existing timesig in MIDI format. """

        return self.lastsig


    def getAscii(self):
        """ Return existing timesig in readable format. """
        
        if not self.lastsig[0]:
            return "Not Set"
        n, d = self.lastsig
        return "%s/%s" % (n, ['1', '2', '4', '8',  '16', '32', '64'][d] )


timeSig = TimeSig()  # singleton 



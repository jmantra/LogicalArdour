# sync.py

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

Functions/variables for the sync stuff.
  Sync START puts a midi on/off event at the start of every track,
  END pads all tracks out to the same length. This is a "be kind"
  process for certain synths and notation converters.
"""

from MMA.common import *
import MMA.debug

synctick    =  0      # flag, set if we want a tick on all tracks at offset 0
endsync     =  0      # flag, set if we want a eof sync

syncTone = [80, 90]  # tone/velocity for -0 option. Changable from setSyncTone

def synchronize(ln):
    """ Set synchronization in the MIDI. This is called by the SYNCRONIZE option
        and the command line -0 and -1 options.
    """

    global synctick, endsync
    
    if not ln:
        error("SYNCHRONIZE: requires args END and/or START.")

    for a in ln:
        if a.upper() == 'END':
            endsync = 1
        elif a.upper() == 'START':
            synctick = 1
        else:
            error("SYNCHRONIZE: expecting END or START")
    

def setSyncTone(ln):
    """ Parser routine, sets tone/velocity for the -0 sync tone. """

    global syncTone
    
    notopts, ln = opt2pair(ln)

    if notopts or not ln:
        error("SetSyncTone: Expecting option pairs: Tone=xx Velocity=xx Volume=xx.")

    for cmd, opt in ln:
        cmd = cmd.upper()

        if cmd == "TONE":
            t = stoi(opt)
            if t < 0 or t > 127:
                error("SetSyncTone: Tone must be 0..127, not %s." % t)
            syncTone[0] = t

        elif cmd in ("VELOCITY", "VOLUME"):
            t = stoi(opt)
            if t < 1 or t > 127:
                error("SetSyncTone: Velocity must be 1..127, not %s." % t)
            syncTone[1] = t

        else:
            error("SetSyncTone: Expecting options: Tone, Velocity, Volume. Not %s"
                  % cmd)

    if MMA.debug.debug:
        dPrint("SetSyncTone: Tone=%s, Velocity=%s" % tuple(syncTone))

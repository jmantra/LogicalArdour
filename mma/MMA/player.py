# player.py

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

import time
import subprocess
import re

from MMA.common import *
from . import gbl
import MMA.file
import MMA.debug

# Initialize the default midi player.
if gbl.platform == 'Windows':
    midiPlayer = ['']   # must be a list!
elif gbl.platform == 'Darwin':
    midiPlayer = ['open']   # must be a list!
else:
    midiPlayer = ["aplaymidi"] # Must be a list!

# We run in background in windows, foreground in linux
if gbl.platform == 'Windows':
    inBackGround = 1  # by default we run in foreground
else:
    inBackGround = 0

waitTime = 5  # default time to wait after forking in background


def setMidiPlayer(ln):
    """ Set the MIDI file player (used with -P and -V). """

    global midiPlayer, waitTime, inBackGround

    if not ln:
        ln = ['']

    n = []
    for l in ln:   # parse out optional args
        if '=' in l and l[0].isalpha():
            a, b = l.upper().split('=', 1)
            if a == 'DELAY':
                b = stof(b, "SetMidiPlayer: Delay must be value, not '%s'." % b)
                waitTime = b

            elif a == "BACKGROUND":
                if b in ('1', 'YES'):
                    inBackGround = 1
                elif b in ('0', 'NO'):
                    inBackGround = 0
                else:
                    error("SetMidiPlayer: Background must be 'yes'"
                          "or 'no', not '%s'." % b)

            else:
                error("SetMidiPlayer: unknown option '%s'." % a)

        else:
            n.append(MMA.file.fixfname(l))

    if not n:
        n = ['']
    midiPlayer = n

    if MMA.debug.debug:
        dPrint("MidiPlayer set to '%s' Background=%s Delay=%s." %
            (' '.join(midiPlayer), inBackGround, waitTime))


def playMidi(file):
    """ Play a midi file. """

    pl = midiPlayer[0]
    opts = midiPlayer[1:]

    if not pl and gbl.platform != "Windows":
        error("No MIDI file player defined, temp files will be deleted.")

    if not pl:
        m = "default windows MIDI player"
    else:
        m = pl
    print("Playing MIDI '%s' with %s." % (file, m))

    if gbl.platform == "Windows":
        sh = True
    else:
        sh = False

    cmd = [pl]
    if opts:
        cmd.extend(opts)
    cmd.append(file)

    t = time.time()

    # fork our player.
    try:
        pid = subprocess.Popen(cmd, shell=sh)
    except OSError as e:
        dPrint(e)
        msg = "MidiPlayer fork error."
        if re.search("[\'\"]", ''.join(cmd)):
            msg += " Using quotes in the MidiPlayer name/opts might be your problem."
        error(msg)

    if inBackGround:    # if the background option set, do a sleep
        print("Play in progress ... file will be deleted.")
        time.sleep(waitTime)

    else:   # foreground player ... wait for process to finish
        pid.wait()
        print("Play complete (%.2f min), MIDI file has been deleted." 
            % ((time.time() - t) / 60))

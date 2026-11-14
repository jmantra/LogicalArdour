
# alloc.py

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

import MMA.patChord
import MMA.patWalk
import MMA.patBass
import MMA.patPlectrum
import MMA.patDrum
import MMA.patScale
import MMA.patArpeggio
import MMA.patSolo
import MMA.patAria
import MMA.grooves
import MMA.debug

from . import gbl
from MMA.common import *

trkClasses = {
    'BASS'     : MMA.patBass.Bass,
    'CHORD'    : MMA.patChord.Chord,
    'ARPEGGIO' : MMA.patArpeggio.Arpeggio,
    'SCALE'    : MMA.patScale.Scale,
    'DRUM'     : MMA.patDrum.Drum,
    'WALK'     : MMA.patWalk.Walk,
    'MELODY'   : MMA.patSolo.Melody,
    'SOLO'     : MMA.patSolo.Solo,
    'ARIA'     : MMA.patAria.Aria,
    'PLECTRUM' : MMA.patPlectrum.Plectrum

}


def trackAlloc(name, err):
    """ Check existence of track and create if possible.

        If 'err' is set, the function will 'error out' if
        it's not possible to create the track. Otherwise,
        it is content to return without creation taking place.
    """

    # If the track already exists, just return

    if name in gbl.tnames:
        return

    # Get the trackname. Can be just a type, or type-name.

    if '-' in name:
        base, ext = name.split('-', 1)
    else:
        ext = None
        base = name

    """ See if there is a track class 'base'. If there is, then
        'f' points to the initialization function for the class.
        If not, we either error (err==1) or return (err==0).
    """

    try:
        f = trkClasses[base]
    except KeyError:
        if err:
            error("There is no track class '%s' for trackname '%s'" % (base, name))
        else:
            return

    # Now attempt to allocate the track

    gbl.tnames[name] = newtk = f(name)

    # Update current grooves to reflect new track.

    for slot in MMA.grooves.glist.keys():
        newtk.saveGroove(slot)

    if MMA.debug.debug:
        dPrint("Creating new track %s" % name)

    return

# tweaks.py

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

This module has support for some simple default tweaks.

"""

from MMA.common import *
import MMA.midiC

import copy

def setTweak(ln):
    """ Option tweaks. """

    import MMA.pat   # here to avoid a circular dep problem
    from MMA.miditables import drumKits
   

    notopt, ln = opt2pair(ln)

    if notopt:
        error("Tweaks: expecting cmd=opt pairs, not '%s'." % ' '.join(notopt))

    for cmd, opt in ln:
        cmd = cmd.upper()

        if cmd in ('DEFAULTDRUM', 'DEFAULTTONE'):
            MMA.pat.defaultDrum = MMA.midiC.decodeVoice(opt)

        elif cmd == 'DEFAULTVOICE':
            MMA.pat.defaultVoice = MMA.midiC.decodeVoice(opt)

        elif cmd == 'DRUMKIT':
            opt = opt.upper()
            if opt.endswith('KIT'):  # optional, end kit name with 'KIT'
                opt = opt[:-3]
            if opt in drumKits:
                opt = drumKits[opt]
            else:
                opt = stoi(opt)
                if opt<0 or opt>127:
                    error("Tweaks DrumKit: value must be 0..127 not '%s'." % opt)
                    
            MMA.pat.defaultDrum = opt
            
        elif cmd == 'DIM':
            from MMA.chordtable import chordlist

            if opt == '3':
                # this is so we can change the desc. (no non-standard)
                chordlist['dim'] = (chordlist['dim3'][0], chordlist['dim3'][1], "Diminished triad")
            elif opt == '7':
                chordlist['dim'] = copy.deepcopy(chordlist['dim7'])
            else:
                error("Tweaks: DIM requires '3' or '7' arg, not '%s'." % opt)

        elif cmd == 'PLECTRUMRESET':
            import MMA.patPlectrum
            MMA.patPlectrum.plectrumReset = getTF(opt, "Tweaks PlectrumReset")
            
        else:
            error("Tweaks: '%s' unknown command." % cmd)

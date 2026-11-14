# translate.py

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


This module handles voice name translations.

"""

import MMA.midiC

from . import gbl
from MMA.common import *
import MMA.debug

""" Translation table for VOICE. This is ONLY used when a voice is set
    from the VOICE command. If a translation exists the translation is
    substituted.
"""


class Vtable:

    def __init__(self):
        self.table = {}

    def retlist(self):

        l = []
        for n in sorted(self.table.keys()):
            l.append("%s=%s" % (n.title(), self.table[n]))

        return ' '.join(l)

    def create(self, ln):
        """ Set a name/alias for voice translation, called from parser. """

        if not ln:
            self.table = {}
            if MMA.debug.debug:
                dPrint("Voice Translation table reset.")
            return

        ln, opts = opt2pair(ln, toupper=True)

        if ln:
            error("VOICETR: Each translation pair must be in the format Alias=Voice.")

        for v, a in opts:
            self.table[v] = a

        if MMA.debug.debug:
            dPrint("Voice Translations: %s" % ' '.join(["%s=%s" % (v, a) for v, a in opts]))

    def get(self, name):
        """ Return a translation or original. """

        name = name.upper()
        try:
            return self.table[name]
        except KeyError:
            return name

vtable = Vtable()            # Create single class instance.


""" This is just like the Vtable, but it is used for DRUM TONES. We use
    this translation when a TONE is set for a drum in setTone() and when a
    tone is selected in a Solo/Melody DRUM track.
"""


class Dtable:

    def __init__(self):
        self.table = {}

    def retlist(self):

        l = []
        for n in sorted(self.table.keys()):
            l.append("%s=%s" % (MMA.midiC.valueToDrum(n),
                                MMA.midiC.valueToDrum(self.table[n])))

        return ' '.join(l)

    def set(self, ln):
        """ Set a name/alias for drum tone translation, called from parser. """

        if not ln:
            self.table = {}
            if MMA.debug.debug:
                dPrint("DrumTone Translation table reset.")

            return

        ln, opts = opt2pair(ln, toupper=True)

        if ln:
            error("TONETR: Each translation pair must be in the format Tone=NewTone.")

        for v, a in opts:
            v1 = MMA.midiC.drumToValue(v)
            if v1 < 0:
                error("TONETR: Tone '%s' not defined." % v)

            a1 = MMA.midiC.drumToValue(a)
            if a1 < 0:
                error("TONETR: Tone '%s' not defined." % a)

            self.table[v1] = a1

        if MMA.debug.debug:
            dPrint("TONETR Translations: %s" % 
                  ' '.join(["%s(%s)=%s" % (v, MMA.midiC.drumToValue(v), 
                                           MMA.midiC.drumToValue(a)) for v, a in opts]))


    def get(self, name):
        """ Return a translation or original. Note that this also does
            validation of 'name'. It is called from patDrum and patSolo.
        """

        v = MMA.midiC.drumToValue(name)

        if v < 0:
            if MMA.midiC.instToValue(name) >= 0 and name[0].isalpha():
                emsg = "(Note: %s is a valid TONE name.)" % name
            else:
                emsg = ''
            error("Drum Tone '%s' not defined. %s" % (name, emsg))

        try:
            return self.table[v]
        except KeyError:
            return v


dtable = Dtable()

""" Volume adjustment. Again, similar to voice/tone translations,
    but this is for the volume. The table creates a percentage adjustment
    for tones/voices specified. When a TRACK VOLUME is set in
    MMApat.setVolume() the routine checks here for an adjustment.
"""


class VoiceVolTable:

    def __init__(self):
        self.table = {}

    def retlist(self):
        l = []
        for n in sorted(self.table.keys()):
            l.append("%s=%s" % (MMA.midiC.valueToInst(n), self.table[n]))

        return ' '.join(l)

    def set(self, ln):
        """ Set a name/alias for voice volume adjustment, called from parser. """

        if not ln:
            self.table = {}
            if MMA.debug.debug:
                dPrint("Voice Volume Adjustment table reset.")

            return

        ln, opts = opt2pair(ln)

        if ln:
            error("VOICEVOLTR: Expecting VOICE=VOLUME pairs.")

        for v, a in opts:
            val = MMA.midiC.instToValue(v)

            if val < 0:
                error("VOICEVOLTR: unknown voice '%s'." % v)

            a = stoi(a)
            if a < 1 or a > 200:
                error("VOICEVOLTR: adjustments must be in range 1 to 200, not '%s'." % a)

            self.table[val] = a / 100.

        if MMA.debug.debug:
            dPrint("VOICEVOLTR: %s" % ' '.join(["%s=%s" % (v.upper(), a) for v, a in opts]))

    def get(self, v, vol):
        """ Return an adjusted value or original. """

        try:
            return vol * self.table[v]
        except:
            return vol

voiceVolTable = VoiceVolTable()


class DrumVolTable:

    def __init__(self):
        self.table = {}

    def retlist(self):

        l = []
        for n in sorted(self.table.keys()):
            l.append("%s=%s" % (MMA.midiC.valueToDrum(n), self.table[n]))

        return ' '.join(l)

    def set(self, ln):
        """ Set a name/alias for drumtone volume adjustment, called from parser. """

        if not ln:
            self.table = {}
            if MMA.debug.debug:
                dPrint("DRUMVOLTR: Adjustment table reset.")

            return

        ln, opt = opt2pair(ln, toupper=True)

        if ln:
            error("DRUMVOLTR: Each option must be in the format TONE=AJUSTMENT.")

        for v, a in opt:
            val = MMA.midiC.drumToValue(v)

            if val < 0:
                error("DRUMVOLTR: Unknown tone '%s'." % v)

            a = stoi(a)
            if a < 1 or a > 200:
                error("DRUMVOLTR: adjustments must be in range 1 to 200, not '%s'." % a)

            self.table[val] = a / 100.

        if MMA.debug.debug:
            dPrint("DRUMVOLTR: %s" %
                  ' '.join(["%s=%s" % (MMA.midiC.valueToDrum(val), a) for v, a in opt]))


    def get(self, v, vol):
        """ Return an adjusted value or original. """

        try:
            return vol * self.table[v]

        except:         # not the best, but any errors just return the orignal volume.
            return vol

drumVolTable = DrumVolTable()

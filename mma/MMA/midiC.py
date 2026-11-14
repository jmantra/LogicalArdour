# midiC.py

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

This module contains interface for MIDI constants and conversion routines.
"""

from MMA.common import *
from MMA.miditables import *
import MMA.translate


def decodeVoice(n):
    """ Convert a single voice item. Used by setVoice() and tweaks. """

    n = MMA.translate.vtable.get(n)
    voc = instToValue(n)

    if voc < 0 and n[0].isalpha():
        t = drumToValue(n)
        if not t < 0 and n[0].isalpha():
            emsg = "(Note: %s is a valid DRUM tone.)" % n
        else:
            emsg = ''
        error("Voice '%s' is not defined. %s" % (n, emsg))
        
    if voc < 0:  # not a valid name, assume vv.msb(ctrl0).lsb(ctrl32) value
        nn = n.split('.')
        if len(nn) > 3 or len(nn) < 1:
            error("Expecting a voice value Prog.MSB.LSB, not '%s'" % n)
        voc = 0
        if len(nn) > 2:
            i = stoi(nn[2])
            if i < 0 or i > 127:
                error("LSB must be 0..127, not '%s'" % i)
            voc = i << 16

        if len(nn) > 1:
            i = stoi(nn[1])
            if i < 0 or i > 127:
                error("MSB must be 0..127, not '%s'" % i)
            voc += i << 8

        i = stoi(nn[0])
        if i < 0 or i > 127:
            error("Program must be 0..127, not '%s'" % i)
        voc += i

    return voc


def voice2tup(x):
    """ Convert integer into 3 byte tuple: Voice, LSB, MSB. """

    if x == -1:
        return (-1, -1, -1) # TSO added to ensure bank 0/0 is setup first time
    
    if x > 0xffff:
        msb = x >> 16
        x &= 0xffff
    else:
        msb = 0

    if x > 0xff:
        lsb = x >> 8
        x &= 0xff
    else:
        lsb = 0

    return (x, lsb, msb)


def extVocStr(v):

    v = "%s.%s.%s" % voice2tup(v)
    if v[-2:] == '.0':
        v = v[:-2]
    if v[-2:] == '.0':
        v = v[:-2]
    return v

###############################


def drumToValue(name):
    """ Get the value of the drum tone (-1==error).
        Note that this is quite different from instToValue() ... in that
        case the caller does a bunch of validation stuff for controllers, etc.
    """

    try:  # assuming that 'name' is an integer
        i = int(name, 0)
        if i >= 0 and i <= 127:
            return int(name)
        else:
            return -1
    except:
        try:
            return drumInx[name.upper()]
        except KeyError:
            return -1


def valueToDrum(val):
    """ Get the name of the drum tone.  """

    try:
        return drumNames[val]
    except KeyError:
        return str(val)


def instToValue(name):
    """ Get the value of the instrument name (-1==error). """

    try:
        return voiceInx[name.upper()]
    except KeyError:
        return -1


def valueToInst(val):
    """ Get the name of the inst. (or 'ERR'). """

    try:
        return voiceNames[val]
    except KeyError:
        try:
            int(val)
        except:
            return "ERROR"
        return extVocStr(val)


def ctrlToValue(name):
    """ Get the value of the controler name (-1==error). """

    try:
        return ctrlInx[name.upper()]
    except KeyError:
        return -1


def valueToCtrl(val):
    """ Get the name of the controller (or 'ERR'). """

    try:
        return ctrlNames[val]
    except KeyError:
        return "ERROR"

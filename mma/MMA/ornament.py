
# ornament.py

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

All ornamentation functions.

"""

from MMA.common import *
from . import gbl
import MMA.notelen
import random
import MMA.debug

def default():
    return {'type': None, 'chromatic': False, 'duration': .2, 'pad': (.1, .1),
            'place': 'ABOVE', 'volume': .75, 'beats': (), 'bars': (), 'rskip': 0,
            'rvolume': (0,0), 'count': 5, 'offset': 0}


def getOrnOpts(self):
    """ Return the ornament settings. Used by debug and macro code. """

    o = self.ornaments

    if o['bars']:
        bars = ','.join([str(i + 1) for i in o['bars']])
    else:
        bars = 'ALL'
    if o['beats']:
        beats = ','.join([str(1 + (i / float(gbl.BperQ))) for i in o['beats']])
    else:
        beats = 'ALL'

    return "Type=%s Chromatic=%s Duration=%s Count=%s Pad=%s,%s Offset=%s Volume=%s " \
      "RVolume=%s,%s Place=%s Beats=%s Rskip=%s Bars=%s" % \
      (str(o['type']).upper(),
       ('OFF', 'ON')[o['chromatic']],
       o['duration'] * 100,
       o['count'],
       o['pad'][0] * 100, o['pad'][1] * 100,
       o['offset'],
       o['volume'] * 100,
       o['rvolume'][0] * 100, o['rvolume'][1] * 100,
       o['place'],
       beats,
       o['rskip'] * 100,
       bars)


def setOrnament(self, ln):
    """ Add an ornamentation option. """

    o = self.ornaments = default()
    notopt, optpair = opt2pair(ln)

    if self.vtype not in ("CHORD", "BASS", "WALK", "ARPEGGIO", "SCALE"):
        error("Ornament is not valid in %s tracks." % self.vtype)

    if (notopt and len(notopt) == 1 and notopt[0].upper() in ('NONE', 'OFF')) \
            or (not notopt and not optpair):
        o['type'] = None
        if MMA.debug.debug:
            dPrint("%s Ornament: Off" % self.name)
        return

    if notopt or not optpair:
        error("%s Ornament: expecting cmd=opt pairs,"
              "not '%s'." % (self.name, ' '.join(notopt)))

    for cmd, opt in optpair:
        cmd = cmd.upper()
        opt = opt.upper()
        
        if cmd == 'TYPE':
            if opt in ('MORDENT', 'TRILL', 'TURN', 'GRACE',
                       '3AFTER', 'FALL', 'GLISS', 'GLISSAFTER' ):
                o['type'] = opt
            else:
                error("%s Ornament Type: '%s' is an unknown type." % (self.name, opt))

        elif cmd == 'COUNT':
            o['count'] = stoi(opt)
            if o['count'] <= 0:
                error("%s Ornament Count: value must be positive integer, not '%s'." % 
                      (self.name, opt))

        elif cmd == 'CHROMATIC':
            o['chromatic'] = getTF(opt, "%s Ornament Chromatic" % (self.name))

        elif cmd == 'DURATION':
            v = stof(opt)
            if v < 0 or v > 100:
                error("%s Ornament Duration: values must be greater "
                      "than 0 and less that 100, not '%s'." % (self.name, v))
            o['duration'] = v / 100

        elif cmd == 'PAD':
            o['pad'] = []
            for v in opt.split(',', 1):
                v = stof(v)
                if v < -100 or v > 100:
                    error("%s Ornament Pad: values must be -100...100, not '%s'." % (self.name, v))
                o['pad'].append(v / 100)
            if len(o['pad']) == 1:
                o['pad'] += o['pad']
            
        elif cmd == 'PLACE':
            if opt not in ('ABOVE', 'BELOW', 'RANDOM'):
                error("%s Ornament Place: must be ABOVE, BELOW or RANDOM, not '%s'." %
                      (self.name, opt))
            o['place'] = opt

        elif cmd == 'VOLUME':
            t = stof(opt)
            if t > 0 and t <= 1000:
                o['volume'] = t / 100
            else:
                error("%s Ornament Volume: must be greater "
                      "than 0 and less that 1000, not '%s'." % (self.name, opt))

        elif cmd == 'BEATS':  
            o['beats'] = []
            if opt != 'ALL':
                for t in opt.split(','):
                    z = self.name  # this is for error msg in setBarOffset()
                    self.name = "%s Ornament beats" % z
                    o['beats'].append(self.setBarOffset(t))
                    self.name = z

        elif cmd == 'RSKIP':
            v = stof(opt)
            if v < 0 or v > 100:
                error("%s Ornament Rskip: must be 0 .. 100, not '%s'." % (self.name, v))
            o['rskip'] = v / 100

        elif cmd == 'RVOLUME':
            n1, n2 = MMA.pat.getRndPair(opt, '%s Ornament' % self.name, -100, 100)
            o['rvolume'] = (n1 / 100., n2 / 100.)
            
        elif cmd == 'BARS':
            o['bars'] = []
            if opt != 'ALL':
                for t in opt.split(','):
                    v = stoi(t)
                    if v < 1 or v > gbl.seqSize:
                        warning("%s Ornament Bars: setting of %s may be "
                                "ignored since SeqSize is %s." %
                                (self.name, v, gbl.seqSize))
                    o['bars'].append(v - 1)

        elif cmd == 'OFFSET':
            v = stof(opt)
            if v < -gbl.BperQ or v > gbl.BperQ:
                error("%s Ornament Offset: must be %s .. %s, "
                      "not '%s' (note: value is MIDI ticks)." %
                      (self.name, -gbl.BperQ, gbl.BperQ, v))
            o['offset'] = v

        else:
            error("%s Ornament: '%s' is an unknown option." % (self.name, cmd))

    if MMA.debug.debug:
        dPrint("%s Ornament: %s" % (self.name, getOrnOpts(self)))


def getNote(o, orig, scale, off):
    """ Calc a new note (the ornament) from the original. """

    if o['place'] == 'BELOW':
        off *= -1

    elif o['place'] == 'RANDOM':
        off = random.choice((1, -1))

    # Chromatic is easy.
    if o['chromatic']:
        return orig + off

    inoct = orig   # a copy of the original note adjusted to be in a 0..12
    oadjust = 0    # range. this lets us find it in the scale list.

    # Adjust 'inoct' to be in the scale list. The original note could
    # be '44' which is not in any scale list. So we need to adjust it
    # down by '12's until it's in range. Keep track of the number of times
    # we do this by also ajdusting 'oadjust' by the opposite value.
    while inoct > scale[-1]:
        oadjust += 12
        inoct -= 12
    while inoct < scale[0]:
        oadjust -= 12
        inoct += 12

    if inoct in scale:
        i = scale.index(inoct)    # this is the position of the note in the scale

        z = nn = i + off          # new note is just offset + old

        # adjust new into scale list
        while nn >= len(scale):
            oadjust += 12
            nn -= len(scale)
        while nn < 0:
            oadjust -= 12
            nn += len(scale)
        nn = scale[nn] + oadjust   # new note, plus octave

    else:
        # opps, not in scale, do chromatic adjustment
        # One place this can happen is with bass patterns using #/b options
        nn = orig + off

    return nn

def getOvolume(o, nvol):
    """ Calculate the note volume. This applies the ornament VOLUME and RVOLUME. """

    vol = int(nvol * o['volume'])
    r1 = int(vol * o['rvolume'][0])
    r2 = int(vol * o['rvolume'][1])
    if r1 or r2:
        if r2 < r1:
            r2, r1 = r1, r2
        vol += random.randrange(r1, r2)
    return vol

def getNOdur(o, noteDur, ornamentDur):
    """ Return an actual duration for the note and ornament. """

    return int(noteDur + (noteDur * o['pad'][0])), \
        int(ornamentDur + (ornamentDur * o['pad'][1]))


def doOrnament(self, nlist, scale, p):
    """ We pass the class structure and the [note duration] to ornament.
        Returns offset of the main note (for chords/harmony to sound right).
    """

    o = self.ornaments
    ornament = o['type']
    orn_duration = o['duration']
    orn_beats = o['beats']
    orn_rskip = o['rskip']
    orn_bars = o['bars']
    orn_offset = o['offset']
    orn_count = o['count']  # only effects gliss

    note, nvol = nlist[0]   # unpack the first note/duration passed.

    # if there is a beat list and the current note is not in the list
    # or if not the right seq bar, we send that note out without ornamentation.

    # skip over bars, beats and random
    if (orn_beats and p.offset not in orn_beats) \
            or (orn_bars and gbl.seqCount not in orn_bars) \
            or (orn_rskip and random.random() < orn_rskip):
        self.sendChord([[note, nvol]], p.duration, p.offset)
        retoffset = p.offset

    # start of the different option code.

    elif ornament == 'GRACE':  # short note before main
        gnote = getNote(o, note, scale, 1)
        odur = int(p.duration * orn_duration)
        ndur = p.duration - odur
        noteDur, ornamentDur = getNOdur(o, ndur, odur)
        ovol = getOvolume(o, nvol)
        self.sendChord([[gnote, ovol]], ornamentDur, p.offset + orn_offset)
        self.sendChord([[note, nvol]], noteDur, p.offset + odur)
        retoffset = p.offset + odur

    elif ornament == 'FALL':  # short note after main (reverse grace)
        gnote = getNote(o, note, scale, 1)
        odur = int(p.duration * orn_duration)
        ndur = p.duration - odur
        ovol =  getOvolume(o, nvol)
        noteDur, ornamentDur = getNOdur(o, ndur, odur)

        self.sendChord([[note, nvol]], ornamentDur, p.offset)
        self.sendChord([[gnote, ovol]], noteDur, p.offset + ndur + orn_offset)
        retoffset = p.offset

    elif ornament == 'TRILL':
        tnote = getNote(o, note, scale, 1)
        odur = int(p.duration * orn_duration)
        noteDur, _ = getNOdur(o, odur, odur)
        offset = p.offset
        count = range(int((p.duration / odur) / 2))  # number of pairs
        if not count:   # ensure at least 1 pair
            count = [1]
        for t in count:
            self.sendChord([[note, getOvolume(o, nvol)]], noteDur, offset)
            self.sendChord([[tnote, getOvolume(o, nvol)]], noteDur, offset + odur + orn_offset)
            offset += (odur + odur)
        retoffset = p.offset

    elif ornament == 'MORDENT':  # note, above, note
        onote = getNote(o, note, scale, 1)
        odur = int((p.duration * orn_duration) / 2)
        ndur = p.duration - odur - odur
        noteDur, ornamentDur = getNOdur(o, ndur, odur)

        self.sendChord([[note, getOvolume(o, nvol)]], ornamentDur, p.offset + orn_offset)
        self.sendChord([[onote, getOvolume(o, nvol)]], ornamentDur, p.offset + odur + orn_offset)
        self.sendChord([[note, nvol]], noteDur, p.offset + odur + odur)
        retoffset = p.offset + odur + odur

    elif ornament == 'TURN':  # above, note, below, note
        note1 = getNote(o, note, scale, 1)
        note2 = getNote(o, note, scale, -1)
        odur = int((p.duration * orn_duration) / 3)
        ndur = p.duration - (odur * 3)
        noteDur, ornamentDur = getNOdur(o, ndur, odur)
        self.sendChord([[note1, getOvolume(o, nvol)]],
                       ornamentDur, p.offset + orn_offset)
        self.sendChord([[note, getOvolume(o, nvol)]],
                       ornamentDur, p.offset + odur + orn_offset)
        self.sendChord([[note2, getOvolume(o, nvol)]],
                       ornamentDur, p.offset + (odur * 2) + orn_offset)
        self.sendChord([[note, nvol]], noteDur, p.offset + (odur * 3))
        retoffset = p.offset + (odur * 3)

    elif ornament == '3AFTER':     # note, 2above, 1above, 2above
        note1 = getNote(o, note, scale, 1)
        note2 = getNote(o, note, scale, 2)

        odur = int((p.duration * orn_duration) / 3)
        ndur = p.duration - (odur * 3)
        noteDur, ornamentDur = getNOdur(o, ndur, odur)

        self.sendChord([[note, nvol]], noteDur, p.offset)
        self.sendChord([(note2, getOvolume(o, nvol))],
                       ornamentDur, p.offset + ndur + orn_offset)
        self.sendChord([(note1, getOvolume(o, nvol))],
                       ornamentDur, p.offset + ndur + odur + orn_offset)
        self.sendChord([(note2, getOvolume(o, nvol))],
                       ornamentDur, p.offset + ndur + odur + odur + orn_offset)
        retoffset = p.offset 

    elif ornament == 'GLISS' or ornament == 'GLISSAFTER':  #  notes before or after
        
        # Make sure that each note in the gliss sounds for at least a tick.
        # Otherwise, it's really a bit of a waste. We need this since we don't
        # range test the count (except to make sure it's a positive integer).

        if  orn_duration * p.duration <  orn_count:
            orn_count = int(orn_duration * p.duration)

        # Create a list of gliss notes
        nlist = []
        for n in range(1, orn_count + 1):
            nn = getNote(o, note, scale, n)
            nlist.insert(0, nn)

        odur = int((p.duration * orn_duration) / orn_count)
        ndur = p.duration - (odur * orn_count)
        noteDur, ornamentDur = getNOdur(o, ndur, odur)
   
        y = p.offset

        if ornament == 'GLISSAFTER':
            self.sendChord([[note, nvol]], noteDur, y)
            retoffset = y
            y += ndur

        for n in nlist:
            self.sendChord([[n, getOvolume(o, nvol)]], ornamentDur, y )
            y += odur
        
        if ornament == 'GLISS':
            self.sendChord([[note, nvol]], noteDur, y)
            retoffset = y

    # when done we return the offset of the main note. This is only
    # used by CHORD so that the other notes in the chord line up.
    # Without this return the other notes in the chord cover up
    # the ornament.
    return retoffset

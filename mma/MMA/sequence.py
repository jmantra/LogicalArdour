# sequence.py

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

from . import gbl
from MMA.common import *
import MMA.debug
from MMA.notelen import noteLenTable

from MMA.alloc import trackAlloc
from MMA.macro import macros
from MMA.pat import pats

import MMA.seqrnd

def trackSequence(name, ln):
    """ Define a sequence for a track.

    The format for a sequence:
    TrackName Seq1 [Seq2 ... ]

    Note, that SeqX can be a predefined seq or { seqdef }
    The {} is dynamically interpreted into a def.
    """

    if not ln:
        error("Use: %s Sequence NAME [...]" % name)

    ln = ' '.join(ln)
    self = gbl.tnames[name]  # this is the pattern class

    if self.vtype == "SOLO":
            warning("Sequences for SOLO tracks are not saved in Grooves.")

    # Before we do extraction of {} stuff make sure we have matching {}s.
    # Count the number of { and } and if they don't match read more lines and
    # append. If we get to the EOF then we're screwed and we error out. Only trick
    # is to make sure we do macro expansion! This code lets one have long
    # sequence lines without bothering with '\' continuations.

    oLine = gbl.lineno   # in case we error out, report start line
    while ln.count('{') != ln.count('}'):
        l = gbl.inpath.read()
        if l is None:   # reached eof, error
            gbl.lineno = oLine
            error("%s Sequence {}s do not match" % name)

        l = ' '.join(macros.expand(l))

        if l[-1] != '}' and l[-1] != ';':
            error("%s: Expecting multiple sequence lines to end in ';'" % name)

        ln += ' ' + l

    # Extract out any {} definitions and assign them to new
    # define variables (__1, __99, etc) and melt them
    # back into the string. The variable 'ids' is reset
    # for every sequence defined. This is fine since tracks don't
    # share sequence data and if we redefine a specific track we
    # don't care about the old setting.

    ids = 1
        
    while 1:
        sp = ln.find("{")

        if sp < 0:
            break

        ln, s = pextract(ln, "{", "}", onlyone=True)
        if not s:
            error("Did not find matching '}' for '{'")

        pn = "_%s" % ids
        ids += 1

        trk = name.split('-')[0]
        trackAlloc(trk, 1)

        # We need to mung the plectrum classes. Problem is that we define all
        # patterns in the base class (plectrum-banjo is created in PLECTRUM)
        # which is fine, but the def depends on the number of strings in the
        # instrument (set by the tuning option). So, we save the tuning for
        # the base class, copy the real tuning, and restore it.
        #
        # NOTE: at this point the base and current tracks have been initialized.

        if trk == 'PLECTRUM' and name != trk:
            z = gbl.tnames[trk]._tuning[:]
            gbl.tnames[trk]._tuning = gbl.tnames[name]._tuning
        else:
            z = None

        gbl.tnames[trk].definePattern(pn, s[0])  # 'trk' is a base class!
        if z:
            gbl.tnames[trk]._tuning = z

        ln = ln[:sp] + ' ' + pn + ' ' + ln[sp:]


    ln = ln.split()

    # We now have a sequence we can save for the track. All the {} defs have
    # been converted to special defines (_1, _2, etc.).
    #
    # First we expand ln to the proper length. lnExpand() also
    # duplicates '/' to the previous pattern.
    #
    # Then we step though ln:
    #  - convert 'z', 'Z' and '-' to empty patterns.
    #  - duplicate the existing pattern for '*'
    #  - copy the defined pattern for everything else.
    #    There's a bit of Python reference trickery here.
    #    Eg, if we have the line:
    #       Bass Sequence B1 B2
    #    the sequence is set with pointers to the existing
    #    patterns defined for B1 and B2. Now, if we later change
    #    the definitions for B1 or B2, the stored pointer DOESN'T
    #    change. So, changing pattern definitions has NO EFFECT.

    ln = lnExpand(ln, '%s Sequence' % self.name)
    tmp = [None] * len(ln)

    for i, n in enumerate(ln):
        n = n.upper()

        if n in ('Z', '-'):
            tmp[i] = None

        elif n == '*':
            tmp[i] = self.sequence[i]

        else:
            p = (self.vtype, n)
            if not p in pats:
                error("Track %s does not have pattern '%s'" % p)
            tmp[i] = pats[p]

    self.sequence = seqBump(tmp)

    if MMA.debug.seqshow:
        msg = ["%s sequence set:" % self.name]
        for a in ln:
            if a in "Zz-":
                msg.append("-")
            else:
                msg.append(a)
        dPrint(' '.join(msg))


def seqsize(ln):
    """ Set the length of sequences. """

    if len(ln) != 1:
        error("Usage 'SeqSize N'")

    n = stoi(ln[0], "Argument for SeqSize must be integer")

    if n < 1:
        error("SeqSize: sequence size must be 1 or greater, not '%s'." % n)

    # Setting the sequence size always resets the seq point

    gbl.seqCount = 0

    # Now set the sequence size for each track. The class call
    # will expand/contract existing patterns to match the new
    # size.

    if n != gbl.seqSize:
        gbl.seqSize = n
        for a in gbl.tnames.values():
            a.setSeqSize()

        MMA.seqrnd.seqRndWeight = seqBump(MMA.seqrnd.seqRndWeight)

    if MMA.debug.debug:
        dPrint("Set SeqSize to %s" % n)


def seq(ln):
    """ Set the sequence point. """

    if len(ln) == 0:
        s = 0
    elif len(ln) == 1:
        s = stoi(ln[0], "Expecting integer value after SEQ")
    else:
        error("Use: SEQ or SEQ NN to reset seq point")

    if s > gbl.seqSize:
        error("Sequence size is '%d', you can't set to '%d'" %
              (gbl.seqSize, s))

    if s == 0:
        s = 1

    if s < 0:
        error("Seq parm must be greater than 0, not %s", s)

    gbl.seqCount = s - 1

    if MMA.seqrnd.seqRnd[0] == 1:
        warning("SeqRnd has been disabled by a Seq command")
        MMA.seqrnd.seqRnd = [0]


def seqClear(ln):
    """ Clear all sequences (except SOLO/ARIA and STICKY tracks). """

    if ln:
        error("Use: 'SeqClear' with no args")

    for n in gbl.tnames.values():
        if n.vtype in ('SOLO', 'ARIA') or n.sticky:
            continue
        n.clearSequence()

    MMA.volume.futureVol = []

    MMA.seqrnd.setSeqRndWeight(['1'])


def restart(ln):
    """ Restart all tracks to almost-default conditions. """

    if ln:
        error("Use: 'Restart' with no args")

    for n in gbl.tnames.values():
        n.restart()

#####################################################
## Misc track sequence commands. Called from parser.

def trackSeqClear(name, ln):
    """ Clear sequence for specified tracks.

    Note: "Drum SeqClear" clears all Drum tracks,
          "Drum-3 SeqClear" clears track Drum-3.
    """

    if ln:
        error("No args permitted. Use %s SEQCLEAR" % name)

    for n in gbl.tnames:
        if n.find(name) == 0:
            if MMA.debug.debug:
                dPrint("SeqClear: Track %s cleared." % n)
            gbl.tnames[n].clearSequence()


def trackSeqRnd(name, ln):
    """ Set random order for specified track. """

    if len(ln) != 1:
        error("Use: %s SeqRnd [On, Off]" % name)

    self = gbl.tnames[name]
    arg = ln[0].upper()

    self.seqRnd = getTF(arg, "%s SeqRnd" % (name))

    if MMA.debug.debug:
        if self.seqRnd:
            a = "On"
        else:
            a = "Off"
        dPrint("%s SeqRnd: %s" % (self.name, a))


def trackSeqRndWeight(name, ln):
    """ Set rnd weight for track. """
 
    tr = gbl.tnames[name]
    tr.seqRndWeight = MMA.seqrnd.getweights(ln, "%s SeqRndWeight" % name)
 

def trackRestart(name, ln):
    """ Restart track to almost-default condidions. """

    if ln:
        error("Use: '%s Resart' with no args", name)

    gbl.tnames[name].restart()


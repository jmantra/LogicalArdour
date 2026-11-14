
# docs.py

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
import json
import os
import time

import MMA.midiC
import MMA.grooves

from . import gbl
from   MMA.common import *


def docDrumNames(order):
    """ Print LaTex table of drum names. """

    notenames = ['E\\flat', 'E', 'F', 'G\\flat', 'G', 'A\\flat',
                 'A', 'B\\flat', 'B', 'C', 'D\\flat', 'D'] * 5

    n = zip(MMA.midiC.drumNames, range(27, len(MMA.midiC.drumNames)+27), notenames)

    if order == "a":
        for a, v, m in sorted(n):
            print("\\insline{%s} {%s$^{%s}$}" % (a, v, m))

    else:
        for a, v, m in n:
            print("\\insline{%s} {%s$^{%s}$}" % (v, a, m))


def docCtrlNames(order):
    """ Print LaTex table of MIDI controller names. """

    n = zip(MMA.midiC.ctrlNames, range(len(MMA.midiC.ctrlNames)))

    if order == "a":
        for a, v in sorted(n):
            print("\\insline{%s} {%02x}" % (a, v))

    else:
        for a, v in n:
            print("\\insline{%02x} {%s}" % (v, a))


def docInstNames(order):
    """ Print LaTex table of instrument names. """

    n = zip(MMA.midiC.voiceNames, range(len(MMA.midiC.voiceNames)))
    if order == "a":
        for a, v in sorted(n):
            a = a.replace('&', '\&')
            print("\\insline{%s} {%s}" % (a, v))

    else:
        for a, v in n:
            a = a.replace('&', '\&')
            print("\\insline{%s} {%s}" % (v, a))


""" Whenever MMA encounters a DOC command, or if it defines
    a groove with DEFGROOVE it calls the docAdd() function.

    The saved docs are printed to stdout with the docDump() command.
    This is called whenever parse() encounters an EOF.

    Both routines are ignored if the -Dx command line option has
    not been set.

    Storage is done is in the following arrays.
"""

fname     = ''
author    = ""
notes     = ""
defs      = []
variables = []


def docAuthor(ln):
    global author

    author = ' '.join(ln)


def docNote(ln):
    """ Add a doc line. """

    global fname, notes

    if not gbl.createDocs or not ln:
        return

    # Grab the arg and data, save it

    fname = os.path.basename(gbl.inpath.fname)
    if notes:
        notes += ' '
    notes += ' '.join(ln)


def docVars(ln):
    """ Add a VARIABLE line (docs vars used in lib file)."""

    global fname, variables

    if not gbl.createDocs or not ln:
        return

    fname = os.path.basename(gbl.inpath.fname)
    variables.append([ln[0], ' '.join(ln[1:])])


def docDefine(ln):
    """ Save a DEFGROOVE comment string.

        Entries are stored as a list. Each item in the list is
        complete groove def looking like:
        defs[ [ Name, Seqsize, Description, [ [TRACK,INST, [Sequences...] ]...]] ...]

    """

    global defs

    # Skip if not creating docs
    if not gbl.createDocs:
        return

    des = ' '.join(ln[1:])  
    if not des[-1] in ".!?": # Add a '.' to the end of all descriptions
        des += '.'
    l = [ln[0], gbl.seqSize, des]
    for a in sorted(gbl.tnames.keys()):
        c = gbl.tnames[a]
        if c.sequence and len(c.sequence) != c.sequence.count(None):
            if c.vtype == 'DRUM':
                v = [MMA.midiC.valueToDrum(x) for x in c.toneList]
            else:
                v = [MMA.midiC.valueToInst(x) for x in c.voice]
            seq = [c.formatPattern(c.sequence[x]) for x in range(gbl.seqSize)]
            l.append([c.name, v, seq])

    defs.append(l)


def docDump():
    """ Print the LaTex docs. """

    global fname, author, notes, defs, variables

    if gbl.createDocs == 1:    # latex docs
        if notes:
            notes = notes.replace("<P>", "\\\\[.5ex]")
            notes = notes.replace("<p>", "\\\\[.5ex]")
            if fname.endswith(gbl.EXT):
                fname = '.'.join(fname.split('.')[:-1])
            print("\\filehead{%s}{%s}\n" % (totex(fname), totex(notes)))

        if variables:
            print("  \\variables{")
            for l in variables:
                print("     \\insvar{%s}{%s}" % (totex(l[0]), totex(l[1])))
            print("  }\n")

        if defs:
            for l in defs:
                alias = MMA.grooves.getAlias(l[0])
                if alias:
                    if len(alias) > 1:
                        alias = "Aliases: %s" % alias
                    else:
                        alias = "Alias: %s" % alias
                else:
                    alias = ''
                print("     \\instable{%s}{%s}{%s}{%s}{" % 
                    (totex(l[0]), totex(l[2]), l[1], alias))
                for c, v, s in l[3:]:  # we ignore the seqence data here
                    print("       \\insline{%s}{%s}" % (c.title(), totex(v[0])))
                print("     }")

    elif gbl.createDocs == 2:    # html docs
        if notes:
            print('<!-- Auto-Generated by MMA on: %s -->' % time.ctime())
            print('<HTML>')
            print('<BODY  BGCOLOR="#B7DFFF" Text=Black>')
            if fname.endswith(gbl.EXT):
                fname = '.'.join(fname.split('.')[:-1])
            print("<H1>%s</H1>" % fname.title())
            print("<P>%s" % notes)

        if variables:
            print("<P>")
            print('<Table Border=3 CELLSPACING=0 CELLPADDING=5 BGColor="#eeeeee" Width="60%">')
            print('  <TR><TD>')
            print('    <H2> Variables </H2> ')
            print('  </TD></TR>')
            print('  <TR><TD>')
            print('    <Table CELLSPACING=0 CELLPADDING=5 BGColor="#eeeeee" Width="100%">')
            for l in variables:
                print("       <TR>")
                print("          <TD Valign=Top> <B> %s </B> </TD> " % l[0])
                print("          <TD Valign=Top> %s </TD>" % l[1])
                print("       </TR>")
            print('    </Table>')
            print('  </TD></TR>')
            print('</Table>')

        if defs:
            print("<ul>")
            for l in defs:
                print("<LI><A Href=#%s>%s</a>" % (l[0], l[0]))
            print("</ul>")
            for l in defs:
                gg = l[0]
                iname = os.path.basename(gbl.infile)
                iname, ext = os.path.splitext(iname)
                gfile = "%s_%s.html" % (iname, gg.lower())
                print('<!-- GROOVE=%s FILE=%s SRC=%s -->' % (gg.lower(), gfile, gbl.infile))
                print('<A Name=%s></a>' % gg)
                print('<Table Border=3 CELLSPACING=0 CELLPADDING=5 BGColor="#eeeeee" Width="60%">')
                print('  <TR><TD>')
                print('    <H2> <A Href=%s> %s </a> </H2> ' % (gfile, l[0]))
                alias = MMA.grooves.getAlias(l[0])
                if alias:
                    if len(alias) > 1:
                        ll = "Aliases"
                    else:
                        ll = "Alias"
                    print(' <H4> %s: %s </H4>' % (ll, alias))

                print('    %s <B>(%s)</B> ' % (l[2], l[1]))
                print('  </TD></TR>')
                print('  <TR><TD>')
                print('    <Table CELLSPACING=0 CELLPADDING=5 BGColor="#eeeeee" Width="10%">')
                for c,v,s in l[3:]:
                    print("       <TR><TD> %s </TD> <TD> %s </TD></TR>" % (c.title(), v[0]))
                print('    </Table>')
                print('  </TD></TR>')
                print('</Table>')
            print('\n</Body></HTML>')

    elif gbl.createDocs == 3:    # sequence table
        for l in defs:
            print("GROOVE %s" % l[0])
            print("DESCRIPTION %s" % l[2])
            print("SIZE %s" % l[1])
            for c, v, s in l[3:]:
                print("TRACK %s" % c)
                print("VOICE %s" % v)
                print("SEQ %s" % s)

    elif gbl.createDocs == 5:    # JSON
        doc = []
        print("JSON")
        for l in defs:
            groove = {
                 "groove": l[0],
                 "description": l[2],
                 "size": l[1],
            }
            groove['tracks'] = [];
            for c,v,s in l[3:]:
                groove['tracks'].append({ "track": c, "voice": v, "sequence": s });
            doc.append(groove)
        print(json.dumps(doc, indent=1))

    elif gbl.createDocs == 99:  # creating entry for groove browser
        for a, b in (("``", '"'), ("''", '"'), ('  ', ' ')):
            notes = notes.replace(a, b)
        if not notes:
            notes = "No header available ... please add DOC to file"
        print(notes)

        for l in defs:
            print("%s\n %s" % (l[0], l[2]))

    else:
        return

    defs = []
    variables = []
    notes = ""
    author = ""


def totex(s):
    """ Parse a string and quote tex stuff.

        Also handles proper quotation style.
    """

    s = s.replace("$", "\$")
    s = s.replace("*", "$*$")
    s = s.replace("_", "\\_")
    #s = s.replace("\\", "\\\\")
    s = s.replace("#", "\\#")
    s = s.replace("&", "\\&")
    q = "``"
    while s.count('"'):
        s = s.replace('"', q, 1)
        if q == "``":
            q = "''"
        else:
            q = "``"

    return s


def htmlGraph(f):
    """ Print (stdout) an html file representing a graph and details of the current groove."""

    global fname, author, notes, variables, defs

    def getAbsPair(x1, x2):
        if abs(x1) == abs(x2):
            return "%s" % abs(x1)
        else:
            return "%s,%s" % (x1, x2)

    def docol(lab, data):
        if lab == '':
            return
        
        if not isinstance(data, list):
            data = [data]
        print("  <td width=50%> ")
        print("%s: " % lab)
        if len(set(data)) == 1:
            print(str(data[0]))
        else:
            print('&nbsp;&nbsp; '.join([str(x) for x in data]))
        print("  </td>")

    def dorow(a, a1, b, b1):
        print("<tr>")
        docol(a, a1)
        docol(b, b1)
        print("</tr>")

    defs = []
    variables = []
    notes = ""
    author = ""
    desc = ""

    if '/' in f:
        u, f = f.rsplit('/', 1)
        MMA.parse.usefile([u])
    MMA.grooves.groove([f])

    groove = MMA.grooves.currentGroove.title()

    for a in defs:
        if a[0].upper() == groove.upper():
            desc = a[2]

    print('<!-- Auto-Generated by MMA on: %s -->' % time.ctime())
    print('<HTML>')
    print('<BODY  BGCOLOR="#B7DFFF" Text=Black>')

    #if fname.endswith(gbl.EXT):
    #    fname='.'.join(fname.split('.')[:-1])

    print("<h2>File: %s</h2>" % fname)
    print("<h2>Groove: %s</h2>" % groove)
    print("<p><b>Notes:</b> %s" % notes)
    print("<p><b>Author:</b> %s" % author)
    print("<p><b>Description:</b> %s" % desc)

    print("<p><Table Border=0 Width=75%>")
    dorow("SeqSize", gbl.seqSize, "Time (beats per bar)", gbl.QperBar)
    print("</Table>")

    if variables:
        print("<p> <b>Variables</b>")
        print('<Table Border=.2em Cellspacing=5 Cellpadding=5  Width="90%">')
        for l in variables:
            print("          <TD Valign=Top> <B> %s </B> </TD> " % l[0])
            print("          <TD Valign=Top> %s </TD>" % l[1])
            print("       </TR>")
        print('</Table>')

    for t in sorted(gbl.tnames.keys()):
        trk = gbl.tnames[t]
        if not trk.sequence or len(trk.sequence) == trk.sequence.count(None):
            continue

        print("<p> <b>Track Name: %s</b>" % t.title())
        print("<p><Table Border=0 Width=75%>")
        if trk.vtype == "DRUM":
            v = [MMA.midiC.valueToDrum(x) for x in trk.toneList]
        else:
            v = [MMA.midiC.valueToInst(x) for x in trk.voice]
        dorow("Voice/Tones", v, "Articulate", trk.artic)
        v = [str(int(x * 100)) for x in trk.volume]
        if trk.vtype != "DRUM":
            oct = [x // 12 for x in trk.octave]
            dorow('Unify', trk.unify, "Octave", oct)
        dorow("Volume", v, "Harmony", trk.harmony)
        v1 = [str(int(x * 100)) for x in trk.rSkip]
        v2 = [getAbsPair(int(x1 * 100), int(x2 * 100)) for x1, x2 in trk.rVolume]
        dorow("Rskip", v1, "Rvolume", v2)
        v1 = [getAbsPair(x1, x2) for x1, x2 in trk.rTime]
        if trk.seqRnd:
            v2 = "On"
        else:
            v2 = "Off"
        dorow("Rtime", v1, "SeqRND", v2)
        if trk.vtype == 'CHORD':
            vv = trk.voicing.mode
            v = 'Voicing'
        else:
            vv = v = ''
        strm = []
        for z in trk.strum:
            if z is None:
                strm.append( "None")
            else:
                strm.append( getAbsPair(z[0], z[1]))
        dorow("Strum", strm, v, vv)
        print("</Table>")
 
        pointx = 2.5
        pointPerS = pointx * gbl.QperBar
        pointy = 5
        boxx = gbl.seqSize * pointPerS
        boxy = pointy

        print(r'<div style="position:relative;background-color:#99bdf4;')
        print(r'padding:0; border:.1em solid black; left:5em;')
        print(r'height:%sem; width:%sem">' % (boxy, boxx))

        if gbl.seqSize > 1:
            for a in range(1, gbl.seqSize):
                print(r'<img style="position:absolute; bottom:0; left:%sem;' % (a * pointPerS))
                print(r'width:.05em; height:%sem; border:.05em solid white"' % pointy)
                print(r'src="../black.gif">')

        for a in range(gbl.seqSize):
            s = trk.sequence[a]
            if not s:
                continue
            for p in s:
                bwidth = p.duration * pointx * (trk.artic[a] / 100.) / gbl.BperQ 
                if bwidth < .1:
                    bwidth = .1
                offset = (p.offset * pointx) // gbl.BperQ + (a * pointPerS)
                if trk.vtype == 'CHORD' or trk.vtype == 'PLECTRUM':
                    # A plectrum track with all 0 volumes is a mute, so ignore.
                    if trk.vtype == 'PLECTRUM' and sum(p.vol) == 0:
                        continue
                    ll = len(p.vol) - p.vol.count(0)
                    vol = sum(p.vol) // ll
                else:
                    vol = p.vol
                height = (vol * pointy) // 127

                print(r'<img style="position:absolute; border:.02em solid red;bottom:0; ')
                print(r'left:%sem; width:%sem; height:%sem"'  % ( offset, bwidth, height))
                print(r' src="../blue.gif">')

        print(r'</div>')

    print('</Body></HTML>')

    sys.exit(0)

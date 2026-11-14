
# chords.py

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

from MMA.common import *
from MMA.chordtable import chordlist
import MMA.roman
from MMA.keysig import keySig  # needed for voicing mode keycenter()
import MMA.debug

import copy

slashPrinted = []  # for slash chord error message

####################################################
# Convert a roman numeral chord to standard notation


def defChord(ln):
    """ Add a new chord type to the chords{} dict. """

    emsg = "DefChord needs NAME (NOTES) (SCALE)"

    # At this point ln is a list. The first item should be
    # the new chord type name.

    if not len(ln):
        error(emsg)
    name = ln.pop(0)
    if name in chordlist.keys():
        warning("Redefining chordtype '%s'" % name)

    if '/' in name:
        error("A slash in not permitted in chord type name")

    if '>' in name:
        error("A '>' in not permitted in chord type name")

    ln = pextract(''.join(ln), '(', ')')

    if ln[0] or len(ln[1]) != 2:
        error(emsg)

    notes = ln[1][0].split(',')
    if len(notes) < 2 or len(notes) > 8:
        error("There must be 2..8 notes in a chord, not '%s'" % len(notes))

    for i, v in enumerate(notes):
        v = stoi(v, "Note offsets in chord must be integers, not '%s'" % v)
        if v < 0 or v > 24:
            error("Note offsets in chord must be 0..24, not '%s'" % v)
        notes[i] = v

    scale = ln[1][1].split(',')
    if len(scale) != 7:
        error("There must be 7 offsets in chord scale, not '%s'" % len(scale))

    for i, v in enumerate(scale):
        v = stoi(v, "Scale offsets in chord must be integers, not '%s'" % v)
        if v < 0 or v > 24:
            error("Scale offsets in chord must be 0..24, not '%s'" % v)
        scale[i] = v

    chordlist[name] = (notes, scale, "User Defined")

    if MMA.debug.debug:
        dPrint("ChordType '%s', %s" % (name, chordlist[name]))


def printChord(ln):
    """ Display the note/scale/def for chord(s). """

    for c in ln:
        try:
            print("%s: %s %s  %s" % 
                  (c, tuple(chordlist[c][0]),
                   tuple(chordlist[c][1]), chordlist[c][2]))
        except KeyError:
            error("Chord '%s' is unknown. Use only the chord type (m, M, M7, ...)." % c)


""" Table of chord adjustment factors. Since the initial chord is based
    on a C scale, we need to shift the chord for different degrees. Note,
    that with C as a midpoint we shift left for G/A/B and right for D/E/F.

    Should the shifts take in account the current key signature?
         (probably not, use chordAdjust option if a problem).
"""

cdAdjust = {
    'Gb': -6,
    'G' : -5,
    'G#': -4, 'Ab':-4,
    'A' : -3,
    'A#': -2, 'Bb':-2,
    'B' : -1, 'Cb':-1,
    'B#':  0, 'C' : 0,
    'C#': 1, 'Db': 1,
    'D' : 2,
    'D#': 3, 'Eb': 3,
    'E' : 4, 'Fb': 4,
    'E#': 5, 'F' : 5,
    'F#': 6 }

### DON'T WRITE TO THIS. IT'S USED TO RESTORE ORIGINAL!
cdAdjustOrig = copy.copy(cdAdjust)

def chordAdjust(ln):
    """ Adjust the selected chord point(s) up/down one octave. """

    global cdAdjust

    args, ln = opt2pair(ln)

    if not ln and not args:
        error("ChordAdjust: Needs at least one argument.")

    for a in args:
        if a.upper() == 'RESET':
            cdAdjust = copy.copy(cdAdjustOrig)

        else:
            error("ChordAdjust: %s is not a valid argument." % a)


    for p, octave in ln:
        octave = stoi(octave, "ChordAdjust: expecting integer (-1, 0 or 1), not '%s'" % octave)
        if octave not in (-1, 0, 1):
            error("ChordAdjust: '%s' is not a valid octave. Use 1, 0 or -1" % octave)

        for pitch in p.upper().split(','):
            if pitch not in cdAdjust:
                error("ChordAdjust: '%s' is not a valid pitch. Chord names must be"
                      " A..G and can be grouped in a list with ','s." % pitch)

            cdAdjust[pitch] = cdAdjustOrig[pitch] + (octave * 12)

###############################
# Chord creation/manipulation #
###############################


class ChordNotes:
    """ The Chord class creates and manipulates chords for MMA. The
    class is initialized with a call with the chord name. Eg:

    ch = ChordNotes("Am")

    The following methods and variables are defined:

    name - original chord name without leading +/- and trail > etc.

    noteList  - the notes in the chord as a list. The "Am"
        would be [9, 12, 16].

    noteListLen     - length of noteList.

    tonic       - the tonic of the chord ("Am" would be "A").

    chordType  - the type of chord ("Am" would be "m").

    rootNote   - the root note of the chord ("Am" would be a 9).

    bnoteList  - the original chord notes, bypassing any
                     invert(), etc. mangling.

    scaleList  - a 7 note list representing a scale similar to
                     the chord.

    reset() - resets noteList to the original chord notes.
              This is useful to restore the original after
              chord note mangling by invert(), etc. without having to
              create a new chord object.


    invert(n) - Inverts a chord by 'n'. This is done inplace and
                returns None. 'n' can have any integer value, but -1 and 1
                are most common. The order of the notes is not changed. Eg:

                ch=Chord('Am')
                ch.noteList == [9, 12, 16]
                ch.invert(1)
                ch.noteList     = [21, 12, 16]

    compress() - Compresses the range of a chord to a single octave. This is
                 done inplace and returns None. Eg:

                 ch=Chord("A13")
                 ch.noteList == [1, 5, 8, 11, 21]
                 ch.compress()
                 ch.noteList == [1, 5, 8, 11, 10 ]


    limit(n) -    Limits the range of the chord 'n' notes. Done inplace
                  and returns None. Eg:

                  ch=Chord("CM711")
                  ch.noteList == [0, 4, 7, 11, 15, 18]
                  ch.limit(4)
                  ch.noteList ==    [0, 4, 7, 11]
                  
                  DROP option deletes specific itervals first:
                      chord  [0, 4, 7, 11, 15, 18]
                      limit(5, Drop=1) - [4, 7, 11, 15, 18]
                      limit(3, Drop=5) - [0, 4, 11]

    """

    #################
    ### Functions ###
    #################

    def __init__(self, name):
        """ Create a chord object. Pass the chord name as the only arg.

        NOTE: Chord names ARE case-sensitive!

            The chord NAME at this point is something like 'Cm' or 'A#7'.
            Split off the tonic and the type.
            If the 2nd char is '#' or 'b' we have a 2 char tonic,
            otherwise, it's the first char only.

            A chord can start with a single '+' or '-'. This moves
            the entire chord and scale up/down an octave.

            Note pythonic trick: By using ranges like [1:2] we
            avoid runtime errors on too-short strings. If a 1 char
            string, name[1] is an error; name[1:2] just returns None.

            Further note: I have tried to enable caching of the generated
            chords, but found no speed difference. So, to make life simpler
            I've decided to generate a new object each time.

        """

        slash = None
        wmessage = ''   # slash warning msg, builder needed for debug.rmShow
        octave = 0
        inversion = 0
        polychord = None
        startingName = name

        if name == 'z':
            self.tonic = self.chordType = None
            self.noteListLen = 0
            self.notesList = self.bnoteList = []
            return

        if '|' in name:
            if name.count('|') > 1:
                error("Polychord marker '|' can only be used once.")

            name, polychord = name.split('|')

        if '/' in name and '>' in name:
            error("You cannot use both an inversion and a slash in the same chord")

        if ':' in name:
            name, barre = name.split(':', 1)
            barre = stoi(barre, "Expecting integer after ':'")
            if barre < -127 or barre > 127:
                error("Chord barres limited to -127 to 127 (more than about +/-20 is silly)")
        else:
            barre = 0

        if '>' in name:
            name, inversion = name.split('>', 1)
            inversion = stoi(inversion, "Expecting integer after '>'")
            if inversion < -5 or inversion > 5:
                error("Chord inversions limited to -5 to 5 (more seems silly)")

        while name[0:1] in ['-', '+']:
            if name[0] == '-':
                octave -= 12
            else:
                octave += 12
            if abs(octave) > 96:
                error("Too many octave adjustments in '%s'." % startingName)
            name = name[1:]

        # we have just the name part. Save 'origname' for debug print

        self.name = name = name.replace('&', 'b')

        if not name:
            error("Empty chord name generated from '%s'." % startingName)

        # Strip off the slash part of the chord. Use later
        # to do proper inversion.

        if name.find('/') > 0:
            name, slash = name.split('/')

        # Name stars with roman (I, V, i, v) then assume
        # rest of name is valid roman. Convert to "standard"
        if name[0] in ("I", "V", "i", "v"):
            n = name
            name = MMA.roman.convert(name)

        # Split chord name (A,B..) and type (minor, dim)
        if name[1:2] in ('#b'):
            tonic = name[0:2]
            ctype = name[2:]
        else:
            tonic = name[0:1]
            ctype = name[1:]

        if not ctype:        # If no type, make it a Major
            ctype = 'M'

        # Now we get the notes for this chord. Just based on the type.
        # Adjust it up/down for the tonic (c,d...)
        try:
            notes = chordlist[ctype][0]
            adj = cdAdjust[tonic] + octave
        except KeyError:
            error("Illegal/Unknown chord name: '%s'" % name)

        self.noteList = [x + adj for x in notes]
        self.bnoteList = tuple(self.noteList)
        self.scaleList = tuple([x + adj for x in chordlist[ctype][1]])
        self.chordType = ctype
        self.tonic = tonic
        self.rootNote = self.noteList[0]
        self.barre = barre

        self.noteListLen = len(self.noteList)

        # Inversion

        if inversion:
            self.invert(inversion)
            self.bnoteList = tuple(self.noteList)

        # Do inversions if there is a valid slash notation.

        if slash:   # convert Roman or Arabic to name of note from chord scale
            if slash[0] in ('I', 'i', 'V', 'v') or slash[0].isdigit():
                n = MMA.roman.rvalue(slash)
                n = self.scaleList[n] % 12   # midi value 

                slash = ('C', 'C#', 'D', 'D#', 'E', 'F',
                         'F#', 'G', 'G#', 'A', 'A#', 'B')[n]
            try:
                r = cdAdjust[slash]    # r = -6 to 6
            except KeyError:
                error("The note '%s' in the slash chord is unknown" % slash)

            # If the slash note is in the chord we invert
            # the chord so the slash note is in root position.
            # NOTE: 'r' is the value of the slash note. NOTE:
            # this is a true rotate, the self.invert() routine
            # fakes it by changing note octaves.

            # Check the slash note against the chord notes
            c_roted = 0
            s = self.noteList
            for octave in [0, 12, 24]:
                if r+octave in s:
                    rot = s.index(r+octave)
                    for i in range(rot):
                        s.append(s.pop(0)+12)
                    if s[0] >= 12:
                        s = [v-12 for v in s]
                    self.noteList = s
                    self.bnoteList = tuple(s)
                    self.rootNote = self.noteList[0]
                    c_roted = 1
                    break

            # Check against the scale notes. If the note is in
            # the scale we rotate the scale to force the slash note
            # to the root position. 
            s_roted = 0
            s = list(self.scaleList)
            for octave in [0, 12, 24]:
                if r+octave in s:
                    rot = s.index(r+octave)
                    for i in range(rot):
                        s.append(s.pop(0)+12)
                    if s[0] >= 12:
                        s = [ v-12 for v in s ]
                    self.scaleList = tuple(s)
                    s_roted = 1
                    break

            # Slash note is not in the chord or scale. This is
            # not an error ... but the note is ignored. So, print
            # a message and list out alternate chords to use.
            if not c_roted and not s_roted:
                wmessage = "The slash chord note '%s' not in chord or scale '%s'" % \
                         (slash, name)

                t = "%s/%s" % (name, slash )
                if t not in slashPrinted:
                    note = r % 12
                    ll = []
                    for c in chordlist:
                        if ord(c[0]) > 128:  # skip dim. symbol
                            continue
                        # We need 'adj' to convert the chords from "C" to the current tonic.
                        adj = cdAdjust[self.tonic]
                        if note in  [(x % 12) + adj for x in chordlist[c][0]]:
                            ll.append("%s%s" % (self.tonic, c))
                    if ll:
                        wmessage += "\nChords with '%s': %s" % (slash, ' '.join(sorted(ll)))

                    slashPrinted.append(t)  # only print this chord/slash once
                if not MMA.debug.rmShow:
                    warning(wmessage)
            

        if polychord:
            ctable = ChordNotes(polychord)
            self.noteList.extend(ctable.noteList)
            self.noteList = list(set(self.noteList))
            self.noteList.sort()
            if len(self.noteList) > 8:
                i = len(self.noteList)
                self.noteList = self.noteList[:8]
                warning("Polychord %s|%s has been truncated from %d to 8 notes." % \
                        (name, polychord, i))
            self.noteListLen = len(self.noteList)
            self.bnoteList = tuple(self.noteList)

        if MMA.debug.rmShow:  # Display roman debug (Debug=Roman)
            if slash:
                a = '/' + slash
            else:
                a = ''
            if wmessage:
                a += '   ' + wmessage
            dPrint(" %03s] %-09s -> %s%s" % (gbl.lineno, startingName, name, a))

    def reset(self):
        """ Restores notes array to original, undoes mangling. """

        self.noteList = list(self.bnoteList[:])
        self.noteListLen = len(self.noteList)


    def invert(self, n):
        """ Apply an inversion to a chord.

        This does not reorder any notes, which means that the root note of
        the chord reminds in position 0. We just find that highest/lowest
        notes in the chord and adjust their octave.

        NOTE: Done on the existing list of notes. Returns None.
        """

        if n:
            c = self.noteList[:]
            while n > 0:        # Rotate up by adding 12 to lowest note
                n -= 1
                c[c.index(min(c))] += 12

            while n < 0:        # Rotate down, subtract 12 from highest note
                n += 1
                c[c.index(max(c))] -= 12

            self.noteList = c

        return None



    def compress(self):
        """ Compress a chord to one ocatve. """

        # Get the max value in the chord list. This is the
        # lowest note in the chord + 12. Note: use the unmodifed value bnoteList!
        mx = min(self.bnoteList) + 12
        c=[]
        for n in self.noteList:
            if n > mx:
                n -= 12
            c.append(n)

        self.noteList = c
        return None



    def limit(self, v, mode, force):
        """ Limit the number of notes in a chord. """

        #z = self.noteList[:] # orig notes
        
        # Look for a matching note from the scale in the chord
        # By using remove() we only remove the 1st instance (a good thing)
        # Note: on a 3 note chord this could make it into 2 note chord.
        # Note: If we are forcing a drop of the root on chords like '11' which
        #       we (wrongly?) include 2 copies of root (actually we change the 3rd
        #       to a root) to prevent the 3rd being voiced we end up with a bit of
        #       a problem since we only remove the 1st match. Uuuggghhh!
        if mode and (v < self.noteListLen or force):
            try:
                self.noteList.remove(self.scaleList[mode-1])
                self.noteListLen = len(self.noteList)
            except ValueError:
                pass

        # Cut of right side to correct length
        if v < self.noteListLen:
            self.noteList = self.noteList[:v]
            self.noteListLen = len(self.noteList)

        #print (f"Dropmode={mode} Force={force} Transform{z}->{self.noteList}")
        
        return None

    def keycenter(self):
        """ Rotate the chord notes until the tonic is close to
            the keysig value. Note that keysig is set C=0, D=2, etc
            which matches the note values in the noteList.
        """

        key = keySig.keyNoteValue
        notes = self.noteList  # just a shorter variable name

        nbelow=0
        nabove=0

        for n in notes:
            if n<key: nbelow+=1
            elif n>key: nabove+=1

        if nbelow>nabove:
            for a in range(nbelow-nabove-1): # this is 0,1 ... start of list
                notes[a] += 12

        elif nbelow<nabove:
            for a in range(1,nabove-nbelow):   # this should give 1,2 
                notes[-a] -= 12                # and the - means end of list

        return None

    def key2center(self):
        """ This is the same as 'key', but the 9th, 11th, etc. are not modified.
            We do this by changing the note list so that 9th, etc. are deleted,
            the 'key' function is called and the deleted notes are restored.
        """
        
        orig = self.noteList[:]

        saved=[]
        self.noteList = []
        root = orig[0]
        for n in orig: 
            if n >= root+12:
                saved.append(n)
            else:
                self.noteList.append(n)
        self.keycenter()
        self.noteList.extend(saved)

        return None

    def rootkey(self):
        """ Modify the chord so that the notes are all close to, but above, the 
            root note (from the key sig).
        """
        
        key = keySig.keyNoteValue
        new = []

        for n in self.noteList: 
            while n<0:
                n+=12
            while n>12:
                n-=12

            if n-12 >= key:
                new.append(n-12)
            else:
                new.append(n)

        self.noteList = new

    def center1(self, lastChord):
        """ Descriptive comment needed here!!!! """

        def minDistToLast(x, lastChord):
            dist=99
            for j in range(len(lastChord)):
                if abs(x-lastChord[j]) < abs(dist):
                    dist = x-lastChord[j]
            return dist

        def sign(x):
            if (x>0):
                return 1
            elif (x<0):
                return -1
            else:
                return 0

        # Only change what needs to be changed compared to the last chord
        # (leave notes where they are if they are in the new chord as well).

        if lastChord:
            ch=self.noteList

            for i in range(len(ch)):

                # minimize distance to last chord

                oldDist = minDistToLast(ch[i], lastChord)
                while abs(minDistToLast(ch[i] - sign(oldDist)*12,
                                lastChord)) < abs(oldDist):
                    ch[i] -= 12* sign(oldDist)
                    oldDist = minDistToLast(ch[i], lastChord)

        return None

    def center2(self, centerNote, noteRange):
        """ Need COMMENT """

        ch=self.noteList
        for i,v in enumerate(ch):

            dist = v - centerNote
            if dist < -noteRange:
                ch[i] = v + 12 * ( abs(dist) // 12+1 )
            if dist > noteRange:
                ch[i] = v - 12 * ( abs(dist) // 12+1 )


        return None


    def drop2(self):
        """ Take the 2nd note of the chord from the top and
            lower it by one octave.
        """

        try:    # just in case some future chords are not long enuf (assume 2+)
            self.noteList[-2] -= 12
        except:
            pass
        return None

    def drop2key(self):
        """ Drop2 plus key rotate. """
        
        self.drop2()
        self.keycenter()
        return None
        
    def drop3(self):
        """ Take the 3rd note of the chord from the top
            and lower it by one octave.
        """

        try: # just in case some future chords are not long enuf (assume 3+)
            self.noteList[-3] -= 12
        except:
            pass
        return None

    def drop3key(self):
        """ Drop3 and key rotate. """

        self.drop3()
        self.keycenter()
        return None
    
    def drop23(self):
        """ Combined Drop2 and Drop3. """
        
        self.drop2()
        self.drop3()
        return None

    def drop23key(self):
        """ Drop2/3 and key rotate. """

        self.drop23()
        self.keycenter()
        return None



######## End of Chord class #####





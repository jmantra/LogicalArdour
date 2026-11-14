
# macros.py

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

The macros are stored, set and parsed in this single-instance
class. At the top of MMAparse an instance in created with
something like:     macros=MMMmacros.Macros().
"""

import random
import datetime
import re
import types
import os
from os import environ
from os import path

import MMA.midiC
import MMA.translate
import MMA.volume
import MMA.grooves
import MMA.parse
import MMA.parseCL
import MMA.player
import MMA.seqrnd
import MMA.midinote
import MMA.swing
import MMA.ornament
import MMA.rpitch
import MMA.chords
import MMA.debug
import MMA.lyric

from MMA.safe_eval import safeEnv, safeEval
from . import gbl

from   MMA.notelen import getNoteLen
from   MMA.keysig import keySig
from   MMA.timesig import timeSig
from   MMA.common import *


def sliceVariable(p, sl):
    """ Slice a variable. Used by macro expand. """

    # If slice is empty, return length.
    if sl == '':
        return [ str(len(p)) ]

    try:
        # Important: We are using the non-safe version of eval()
        #            changing to safe_eval() will stop slice
        #            args from working!!! So, don't change it.
        new = eval('p' + "[" + sl + "]")
    except IndexError:
        error("Index '%s' out of range." % sl)
    except:
        error("Index error '%s' in '%s' Check the array being sliced." % (sl,p) )

    if ":" not in sl:
        new = [new]

    return new


class Macros:
    vars = {}            # storage
    expandMode = 1        # flag for variable expansion
    pushstack = []

    def __init__(self):

        self.vars = {}

    def clear(self, ln):
        if ln:
            error("VarClear does not take an argument.")
        self.vars = {}
        if MMA.debug.debug:
            dPrint("All variable definitions cleared.")

    def stackValue(self, s):
        self.pushstack.append(' '.join(s))

    def sysvar(self, s):
        """ Create an internal macro. """

        # Check for system functions.

        m = re.match( r'([^\(]+)\((.*)\)$', s )
        if m:
            return self.sysfun( m.group(1), m.group(2) )
            
        # Simple/global     system values

        if s == 'CHORDADJUST':
            return ' '.join([ "%s=%s" % (a, MMA.chords.cdAdjust[a]) 
                              for a in sorted(MMA.chords.cdAdjust)])

        elif s == 'FILENAME':
            a = gbl.inpath.fname
            if isinstance(a, int):
                return ''
            else:
                return str(gbl.inpath.fname)

        elif s == 'FILEPATH':
            a = gbl.inpath.fname
            if isinstance(a, int):
                return ''
            else:
                return path.abspath(gbl.inpath.fname)

        elif s == 'SONGPATH':
            a = gbl.infile
            if isinstance(a, int):
                return ''
            else:
                return path.abspath(gbl.infile)
        
        elif s == 'KEYSIG':
            return keySig.getKeysig()

        elif s == 'TIME':
            return str(gbl.QperBar)

        elif s == 'CTABS':
            return ','.join([ str((float(x) / gbl.BperQ) + 1) for x in MMA.parseCL.chordTabs])

        elif s == 'TIMESIG':
            return timeSig.getAscii()

        elif s == 'TEMPO':  # get the current tempo via the record in midi.py
            tmp = gbl.tempo
            for o,t in MMA.midi.tempoChanges:
                if o > gbl.tickOffset:
                    break
                tmp = t
            return str(tmp)

        elif s == 'OFFSET':
            return str(gbl.tickOffset)
        
        elif s == 'SONGFILENAME':
            return str(gbl.infile)

        elif s == 'VOLUME':
            return str(int(MMA.volume.volume * 100))  # INT() is important

        elif s == 'VOLUMERATIO':
            return str((MMA.volume.vTRatio * 100))

        elif s == 'LASTVOLUME':
            return str(int(MMA.volume.lastVolume * 100))

        elif s == 'GROOVE':
            return MMA.grooves.currentGroove

        elif s == 'GROOVELIST':
            return ' '.join(sorted([x for x in MMA.grooves.glist.keys() if isinstance(x, str)]))

        elif s == 'TRACKLIST':
            return ' '.join(sorted(gbl.tnames.keys()))

        elif s == 'LASTGROOVE':
            return MMA.grooves.lastGroove

        elif s == 'PLUGINS':
            from MMA.regplug import simplePlugs  # to avoid circular import error
            return ' '.join(simplePlugs)

        elif s == 'TRACKPLUGINS':
            from MMA.regplug import trackPlugs  # to avoid circular import error
            return ' '.join(trackPlugs)
         
        elif s == 'DATAPLUGINS':
            from MMA.regplug import dataPlugs  # to avoid circular import error
            return ' '.join(dataPlugs)
        
        elif s == 'SEQ':
            return str(gbl.seqCount)

        elif s == 'SEQRND':
            if MMA.seqrnd.seqRnd[0] == 0:
                return "Off"
            if MMA.seqrnd.seqRnd[0] == 1:
                return "On"
            return ' '.join(MMA.seqrnd.seqRnd[1:])

        elif s == 'SEQSIZE':
            return str(gbl.seqSize)

        elif s == 'SWINGMODE':
            return MMA.swing.settings()

        elif s == 'TICKPOS':
            return str(gbl.tickOffset)
        
        elif s == 'TRANSPOSE':
            return str(gbl.transpose)

        elif s == 'STACKVALUE':
            if not self.pushstack:
                error("Empty push/pull variable stack")
            return self.pushstack.pop()

        elif s == 'DEBUG':
            return MMA.debug.getFlags()
        
        elif s == 'LASTDEBUG':
            return MMA.debug.getLFlags()
            
        elif s == 'VEXPAND':
            if self.expandMode:
                return "On"
            else:
                return "Off"

        elif s == "MIDIPLAYER":
            return "%s Background=%s Delay=%s." % \
                (' '.join(MMA.player.midiPlayer), MMA.player.inBackGround,
                 MMA.player.waitTime)

        elif s == "MIDISPLIT":
            return ' '.join([str(x) for x in MMA.midi.splitChannels])

        elif s == "MIDIASSIGNS":
            x = []
            for c, n in sorted(gbl.midiAssigns.items()):
                if n:
                    x.append("%s=%s" % (c, ','.join(n)))
            return ' '.join(x)

        elif s == 'SEQRNDWEIGHT':
            return ' '.join([str(x) for x in MMA.seqrnd.seqRndWeight])

        elif s == 'AUTOLIBPATH':
            return ' '.join(MMA.paths.libDirs)

        elif s == 'LIBPATH':
            return ' '.join(MMA.paths.libPath)

        elif s == 'MMAPATH':
            return gbl.MMAdir

        elif s == 'INCPATH':
            return ' '.join(MMA.paths.incPath)

        elif s == 'PLUGPATH':
            return ' '.join(MMA.paths.plugPaths)
    
        elif s == 'VOICETR':
            return MMA.translate.vtable.retlist()

        elif s == 'TONETR':
            return MMA.translate.dtable.retlist()

        elif s == 'OUTPATH':
            return gbl.outPath

        elif s == 'BARNUM':
            return str(gbl.barNum + 1)

        elif s == 'LINENUM':
            return str(gbl.lineno)

        elif s == 'LYRIC':
            return MMA.lyric.lyric.setting()

        # Some time/date macros. Useful for generating copyright strings

        elif s == 'DATEYEAR':
            return str(datetime.datetime.now().year)

        elif s == 'DATEDATE':
            return datetime.datetime.now().strftime("%Y-%m-%d")

        elif s == 'DATETIME':
            return datetime.datetime.now().strftime("%H:%M:%S")

        
        # Some system info. Could be useful in generating path names?

        elif s == 'PWD':
            return os.getcwd()
        
        # Track vars ... these are in format TRACKNAME_VAR

        a = s.rfind('_')
        if a == -1:
            error("Unknown system variable $_%s" % s)

        tname = s[:a]
        func = s[a+1:]

        try:
            t = gbl.tnames[tname]
        except KeyError:
            error("System variable $_%s refers to nonexistent track." % s)

        if func == 'ACCENT':
            r = []
            for s in t.accent:
                r.append("{")
                for b, v in s:
                    r.append('%g' % (b/float(gbl.BperQ)+1))
                    r.append(str(int(v * 100)))
                r.append("}")
            return ' '.join(r)

        elif func == 'ARTICULATE':
            return ' '.join([str(x) for x in t.artic])

        elif func == 'CHORDS':
            r = []
            for l in t.chord:
                r.append('{' + ' '.join(l) + '}')
            return ' '.join(r)

        elif func == 'CHANNEL':
            return str(t.channel)

        elif func == 'COMPRESS':
            return ' '.join([str(x) for x in t.compress])

        elif func == 'DELAY':
            return ' '.join([str(x) for x in t.delay])

        elif func == 'DIRECTION':
            if t.vtype == 'ARIA':
                return ' '.join([str(x) for x in t.selectDir])
            else:
                return ' '.join([str(x) for x in t.direction])

        elif func == 'DUPROOT':
            if t.vtype != "CHORD":
                error("Only CHORD tracks have DUPROOT")
            return t.getDupRootSetting()

        elif func == 'FRETNOISE':
            return t.getFretNoiseOptions()

        elif func == 'HARMONY':
            return ' '.join([str(x) for x in t.harmony])

        elif func == 'HARMONYONLY':
            return ' '.join([str(x) for x in t.harmonyOnly])

        elif func == 'HARMONYVOLUME':
            return ' '.join([str(int(i * 100)) for i in t.harmonyVolume])

        elif func == 'INVERT':
            return ' '.join([str(x) for x in t.invert])

        elif func == 'LIMIT':
            return "%s mode=%s" % (t.chordLimit[0], t.chordLimit[1])

        elif func == 'MALLET':
            if t.vtype not in ("SOLO", "MELODY"):
                error("Mallet only valid in SOLO and MELODY tracks")
            return "Mallet Rate=%i Decay=%i" % (t.mallet, t.malletDecay*100)

        elif func == 'MIDINOTE':
            return MMA.midinote.mopts(t)

        elif func == 'MIDIVOLUME':
            return "%s" % t.cVolume

        elif func == 'OCTAVE':
            return ' '.join([str(i//12) for i in t.octave])

        elif func == 'MOCTAVE':
            return ' '.join([str((i//12)-1) for i in t.octave])

        elif func == 'ORNAMENT':
            return MMA.ornament.getOrnOpts(t)
        
        elif func == 'PLUGINS':
            from MMA.regplug import trackPlugs  # avoids circular import
            return ' '.join(trackPlugs)
        
        elif func == 'RANGE':
            return ' '.join([str(x) for x in t.chordRange])

        elif func == 'RSKIP':
            m = ''
            if t.rSkipBeats:
                m = "Beats=%s " % ','.join(['%g' % (x/float(gbl.BperQ)+1) for x in t.rSkipBeats])
            m += ' '.join([str(int(i * 100)) for i in t.rSkip])
            return m

        elif func == 'RDURATION':
            tmp = []
            for a1, a2 in t.rDuration:
                a1 = int(a1 * 100)
                a2 = int(a2 * 100)
                if a1 == a2:
                    tmp.append('%s' % abs(a1))
                else:
                    tmp.append('%s,%s' % (a1, a2))

            return ' '. join(tmp)

        elif func == 'RTIME':
            tmp = []
            for a1, a2 in t.rTime:
                if a1 == a2:
                    tmp.append('%s' % abs(a1))
                else:
                    tmp.append('%s,%s' % (a1, a2))
            return ' '.join(tmp)

        elif func == 'RVOLUME':
            tmp = []
            for a1, a2 in t.rVolume:
                a1 = int(a1 * 100)
                a2 = int(a2 * 100)
                if a1 == a2:
                    tmp.append('%s' % abs(a1))
                else:
                    tmp.append('%s,%s' % (a1, a2))
            return ' '.join(tmp)

        elif func == 'RPITCH':
            return MMA.rpitch.getOpts(t)
            
                    
        elif func == 'SEQUENCE':
            tmp = []
            for a in range(gbl.seqSize):
                tmp.append('{' + t.formatPattern(t.sequence[a]) + '}')
            return ' '.join(tmp)

        elif func == 'SEQRND':
            if t.seqRnd:
                return 'On'
            else:
                return 'Off'

        elif func == 'SEQRNDWEIGHT':
            return ' '.join([str(x) for x in t.seqRndWeight])

        elif func == 'SPAN':
            return "%s %s" % (t.spanStart, t.spanEnd)

        elif func == 'STICKY':
            if t.sticky:
                return "True"
            else:
                return "False"
            

        elif func == 'STRUM':
            r = []
            for v in t.strum:
                if v is None:
                    r.append("0")
                else:
                    a, b = v
                    if a == b:
                        r.append("%s" % a)
                    else:
                        r.append("%s,%s" % (a, b))

            return ' '.join(r)

        elif func == 'STRUMADD':
            return ' '.join([str(x) for x in t.strumAdd])

        elif func == 'TRIGGER':
            return MMA.trigger.getTriggerOptions(t)

        elif func == 'TONE':
            if t.vtype in ('MELODY', 'SOLO'):
                if not t.drumType:
                    error("Melody/Solo tracks must be DRUMTYPE for tone.")
                return str(MMA.midiC.valueToDrum(t.drumTone))

            elif t.vtype != 'DRUM':
                error("Tracktype %s doesn't have TONE" % t.vtype)

            return ' '.join([MMA.midiC.valueToDrum(a) for a in t.toneList])

        elif func == 'UNIFY':
            return ' '.join([str(x) for x in t.unify])

        elif func == 'VOICE':
            return ' '.join([MMA.midiC.valueToInst(a) for a in t.voice])

        elif func == 'VOICING':
            if t.vtype != 'CHORD':
                error("Only CHORD tracks have VOICING")
            t = t.voicing
            return "Mode=%s Range=%s Center=%s RMove=%s Move=%s Dir=%s" % \
                (t.mode, t.range, t.center, t.random, t.bcount, t.dir)

        elif func == 'VOLUME':
            return ' '.join([str(int(a * 100)) for a in t.volume])

        else:
            error("Unknown system track variable %s" % s)

    def sysfun(self, func, arg):
        print("In sysfun", func, arg)
        if func == 'NOTELEN':
            return "%sT" % getNoteLen(arg)
        
        elif func == 'ENV':
            return safeEnv(arg)

        else:
            error("Unknown system function %s" % func)

    def expand(self, l):
        """ Loop though input line and make variable subsitutions.
            MMA variables are pretty simple ... any word starting
            with a "$xxx" is a variable.

            l - list

            RETURNS: new list with all subs done.
        """

        if not self.expandMode:
            return l

        gotmath = 0
        sliceVar = None

        while 1:          # Loop until no more subsitutions have been done
            sub = 0

            for i, s in enumerate(l):
                  if len(s) > 0 and s[0] == '$':
                    
                    s = s[1:].upper()
                    if not s:
                        error("Illegal macro name '%s'." % l[i])

                    frst = s[0]  # first char after the leading '$'

                    if frst == '$':  # $$ - don't expand (done in IF clause)
                        continue

                    if frst == '(':   # flag math macro
                        gotmath = 1
                        continue

                    # pull slice notation off the end of the name

                    if s.endswith(']'):
                        x = s.rfind('[')
                        if not x:
                            error("No matching for '[' for trailing ']' in variable '%s'." % s)
                        sliceVar = s[x+1:-1]
                        s = s[:x]

                        # If the slice is empty sliceVar will return the length
                        # of the list, i.e. the number of words.
                        
                        """ Since we be using an 'eval' to do the actual slicing,
                            we check the slice string to make sure it's looking
                            valid. The easy way out makes as much sense as anything
                            else ... just step through the slice string and make
                            sure we ONLY have integers or empty slots.
                        """

                        for test in sliceVar.split(":"):
                            try:
                                test == '' or int(test)
                            except:
                                error("Invalid index in slice notation '%s'." % sliceVar)

                    else:
                        sliceVar = None

                    # we have a var, see if system or user. Set 'ex'

                    if frst == '_':   # system var
                        ex = self.sysvar(s[1:])

                    elif s in self.vars:  # user var?
                        ex = self.vars[s]

                    elif sliceVar == "":
                        l = l[:i] + ["-1"] + l[i+1:]
                        sub = 1
                        sliceVar = None
                        break
                    
                    else:                 # unknown var...error
                        error("User variable '%s'  has not been defined" % s)

                    if isinstance(ex, list):  # MSET variable
                        if sliceVar is not None:
                            ex = sliceVariable(ex, sliceVar)
                            sliceVar = None

                        if len(ex):
                            gbl.inpath.push(ex[1:], [gbl.lineno] * len(ex[1:]))
                            if len(ex):
                                ex = ex[0]
                            else:
                                ex = []

                    else:                       # regular SET variable
                        ex = ex.split()
                        if sliceVar is not None:
                            ex = sliceVariable(ex, sliceVar)
                            sliceVar = None

                    """ we have a simple variable (ie $_TEMPO) converted to a list,
                        or a list-like var (ie $_Bass_Volume) converted to a list,
                        or the 1st element of a multi-line variable
                        We concat this into the existing line, process some more
                    """

                    l = l[:i] + ex + l[i+1:]

                    sub = 1
                    break

            if not sub:
                break

        
        # all the mma internal and system macros are expanded. Now check for math.

        if gotmath:
            l = ' '.join(l)   # join back into one line

            while 1:
                try:
                    s1 = l.index('$(')  # any '$(' left?
                except:
                    break               # nope, done
                # find trailing )
                nest = 0
                s2 = s1+2
                max = len(l)
                while 1:
                    if l[s2] == '(':
                        nest += 1
                    if l[s2] == ')':
                        if not nest:
                            break
                        else:
                            nest -= 1
                    s2 += 1
                    if s2 >= max:
                        error("Unmatched delimiter in '%s'." % l)

                l = l[:s1] + str( safeEval(l[s1+2:s2].strip())) + l[s2+1:]

            l = l.split()

        return l

    def showvars(self, ln):
        """ Display all currently defined user variables. """

        if len(ln):
            for a in ln:
                a = a.upper()
                if a in self.vars:
                    print("$%s: %s" % (a, self.vars[a]))
                else:
                    print("$%s - not defined" % a)

        else:

            print("User variables defined:")
            kys = self.vars.keys()
            kys.sort()

            mx = 0

            for a in kys:                    # get longest name
                if len(a) > mx:
                    mx = len(a)

            mx = mx + 2

            for a in kys:
                print("     %-*s  %s" % (mx, '$'+a, self.vars[a]))

    def getvname(self, v):
        """ Helper routine to validate variable name. """

        if v[0] in ('$', '_'):
            error("Variable names cannot start with a '$' or '_'")
        if '[' in v or ']' in v:
            error("Variable names cannot contain [ or ] characters.")

        return v.upper()

    def rndvar(self, ln):
        """ Set a variable randomly from a list. """

        if len(ln) < 2:
            error("Use: RndSet Variable_Name <list of possible values>")

        v = self.getvname(ln[0])

        self.vars[v] = random.choice(ln[1:])

        if MMA.debug.debug:
            dPrint("Variable $%s randomly set to '%s'" % (v, self.vars[v]))

    def newsetvar(self, ln):
        """ Set a new variable. Ignore if already set. """

        if not len(ln):
            error("Use: NSET VARIABLE_NAME [Value] [[+] [Value]]")

        if self.getvname(ln[0]) in self.vars:
            return

        self.setvar(ln)

    def setvar(self, ln):
        """ Set a variable. Note the difference between the next 2 lines:
                Set Bar BAR
                Set Foo AAA BBB $bar
                   $Foo == "AAA BBB BAR"
                Set Foo AAA + BBB + $bar
                   $Foo == "AAABBBBAR"

            The "+"s just strip out intervening spaces.
        """

        if len(ln) < 1:
            error("Use: SET VARIABLE_NAME [Value] [[+] [Value]]")

        v = self.getvname(ln.pop(0))

        t = ''
        addSpace = 0
        for i, a in enumerate(ln):
            if a == '+':
                addSpace = 0
                continue
            else:
                if addSpace:
                    t += ' '
                t += a
                addSpace = 1

        self.vars[v] = t

        if MMA.debug.debug:
            dPrint("Variable $%s == '%s'" % (v, self.vars[v]))

    def msetvar(self, ln):
        """ Set a variable to a number of lines. """

        if len(ln) != 1:
            error("Use: MSET VARIABLE_NAME <lines> MsetEnd")

        v = self.getvname(ln[0])

        lm = []

        while 1:
            l = gbl.inpath.read()
            if not l:
                error("Reached EOF while looking for MSetEnd")
            cmd = l[0].upper()
            if cmd in ("MSETEND", 'ENDMSET'):
                if len(l) > 1:
                    error("No arguments permitted for MSetEnd/EndMSet")
                else:
                    break
            lm.append(l)

        self.vars[v] = lm
        
    def unsetvar(self, ln):
        """ Delete a variable reference. """

        if len(ln) != 1:
            error("Use: UNSET Variable")
        v = ln[0].upper()
        if v[0] == '_':
            error("Internal variables cannot be deleted or modified")

        if v in self.vars:
            del(macros.vars[v])

            if MMA.debug.debug:
                dPrint("Variable '%s' UNSET" % v)
        else:
            warning("Attempt to UNSET nonexistent variable '%s'" % v)

    def vexpand(self, ln):

        if len(ln) == 1:
            cmd = ln[0].upper()
        else:
            cmd = ''

        if cmd == 'ON':
            self.expandMode = 1
            if MMA.debug.debug:
                dPrint("Variable expansion ON")

        elif cmd == 'OFF':
            self.expandMode = 0
            if MMA.debug.debug:
                dPrint("Variable expansion OFF")

        else:
            error("Use: Vexpand ON/Off")

    def varinc(self, ln):
        """ Increment  a variable. """

        if len(ln) == 1:
            inc = 1

        elif len(ln) == 2:
            inc = stof(ln[1], "Expecting a value (not %s) for Inc" % ln[1])

        else:
            error("Usage: INC Variable [value]")

        v = ln[0].upper()

        if v[0] == '_':
            error("Internal variables cannot be modified")

        if not v in self.vars:
            error("Variable '%s' not defined" % v)

        vl = stof(self.vars[v], "Variable must be a value to increment") + inc

        # lot of mma commands expect ints, so convert floats like 123.0 to 123

        if vl == int(vl):
            vl = int(vl)

        self.vars[v] = str(vl)

        if MMA.debug.debug:
            dPrint("Variable '%s' INC to %s" % (v, self.vars[v]))

    def vardec(self, ln):
        """ Decrement a varaiable. """

        if len(ln) == 1:
            dec = 1

        elif len(ln) == 2:
            dec = stof(ln[1], "Expecting a value (not %s) for Inc" % ln[1])

        else:
            error("Usage: DEC Variable [value]")

        v = ln[0].upper()
        if v[0] == '_':
            error("Internal variables cannot be modified")

        if not v in self.vars:
            error("Variable '%s' not defined" % v)

        vl = stof(self.vars[v], "Variable must be a value to decrement") - dec

        # lot of mma commands expect ints, so convert floats like 123.0 to 123

        if vl == int(vl):
            vl = int(vl)

        self.vars[v] = str(vl)

        if MMA.debug.debug:
            dPrint("Variable '%s' DEC to %s" % (v, self.vars[v]))

    def varIF(self, ln):
        """ Conditional variable if/then. """

        def expandV(l):
            """ Private func. """

            l = l.upper()

            if l[:2] == '$$':
                l = l.upper()
                l = l[2:]
                if not l in self.vars:
                    error("String Variable '%s' does not exist" % l)
                l = self.vars[l]

            try:
                v = float(l)
            except:
                try:
                    v = int(l, 0)  # this lets us convert HEX/OCTAL
                except:
                    v = None

            return(l.upper(), v)

        def readblk():
            """ Private, reads a block until ENDIF, IFEND or ELSE.
                Return (Terminator, lines[], linenumbers[] )
            """

            q = []
            qnum = []
            nesting = 0

            while 1:
                l = gbl.inpath.read()
                if not l:
                    error("EOF reached while looking for EndIf")

                cmd = l[0].upper()
                if cmd == 'IF':
                    nesting += 1
                if cmd in ("IFEND", 'ENDIF', 'ELSE'):
                    if len(l) > 1:
                        error("No arguments permitted for IfEnd/EndIf/Else")
                    if not nesting:
                        break
                    if cmd != 'ELSE':
                        nesting -= 1

                q.append(l)
                qnum.append(gbl.lineno)

            return (cmd, q, qnum)

        if len(ln) < 2:
            error("Usage: IF <Operator> ")

        action = ln[0].upper()

        # 1. do the unary options: DEF, NDEF

        if action in ('DEF', 'NDEF', 'ISEMPTY', 'ISNOTEMPTY'):
            if len(ln) != 2:
                error("Usage: IF %s VariableName" % action)

            v = ln[1].upper()  # everyone expects upper() except for EXISTS

            if action == 'DEF':
                compare = v in self.vars
                
            elif action == 'NDEF':
                compare = (v not in self.vars)

            elif action in ('ISEMPTY', 'ISNOTEMPTY'):
                if v.startswith('_'):
                    v = self.sysvar(v[1:])
                elif v not in self.vars:
                    error("Variable '%s' has not been created" % v)
                else:
                    v = self.vars[v]  # contents of user var
                if action == 'ISEMPTY':
                    compare = (v == '')
                else:
                    compare = (v != '')
             
        # 2. FIle operations

        elif action in ('EXISTS', 'ISDIR', 'ISFILE'):
            if action == 'EXISTS':   # does file exist?
                compare = path.exists(path.expanduser(ln[1]))
                
            if action == 'ISDIR':   # does file exist and is it a directory
                compare = path.isdir(path.expanduser(ln[1]))
                
            if action == 'ISFILE':   # does file exist and is it a file
                compare = path.isfile(path.expanduser(ln[1]))
 
        # 2. Binary ops: EQ, NE, etc.

        elif action in ('LT', '<', 'LE', '<=', 'EQ', '==', 'GE', '>=', 'GT', '>', 'NE', '!='):
            if len(ln) != 3:
                error("Usage: VARS %s Value1 Value2" % action)

            s1, v1 = expandV(ln[1])
            s2, v2 = expandV(ln[2])

            # Make the comparison to strings or values. If either arg
            # is NOT a value, use string values for both.
            if None in (v1, v2):
                v1, v2 = s1, s2

            if action == 'LT' or action == '<':
                compare = (v1 < v2)
            elif action == 'LE' or action == '<=':
                compare = (v1 <= v2)
            elif action == 'EQ' or action == '==':
                compare = (v1 == v2)
            elif action == 'GE' or action == '>=':
                compare = (v1 >= v2)
            elif action == 'GT' or action == '>':
                compare = (v1 > v2)
            elif action == 'NE' or action == '!=':
                compare = (v1 != v2)
            else:
                error("Unreachable binary conditional")  # can't get here

        else:
            error("Usage: IF <CONDITON> ...")

        """ Go read until end of IF block.
            We shove the block back if the compare was true.
            Unless, the block is terminated by an ELSE ... then we need
            to read another block and push back one of the two.
        """

        cmd, q, qnum = readblk()

        if cmd == 'ELSE':
            cmd, q1, qnum1 = readblk()

            if cmd == 'ELSE':
                error("Only one ELSE is permitted in IF construct")

            if not compare:
                compare = 1
                q = q1
                qnum = qnum1

        if compare:
            gbl.inpath.push(q, qnum)


macros = Macros()

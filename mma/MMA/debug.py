# debug.py

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

Some silly functions used by the debug code.


"""

# the Lxxx values are the previous settings, used for LASTDEBUG macro

debug          =     Ldebug         = 0
pshow          =     Lpshow         = 0
seqshow        =     Lseqshow       = 0
showrun        =     Lshowrun       = 0
noWarn         =     LnoWarn        = 0
noOutput       =     LnoOutput      = 0
showExpand     =     LshowExpand    = 0
showFilenames  =     LshowFilenames = 0
chshow         =     Lchshow        = 0

plecShow       =     LplecShow  = 0  # not a command line setting
rmShow         =     LrmShow    = 0  # not command
gvShow         =     LgvShow    = 0

def cmdLineDebug(o):
    """ Set a command line debug option. Called from options.py """

    global debug, Ldebug, showFilenames, LshowFilenames, \
        pshow, Lpshow, seqshow, Lseqshow, showrun, Lshowrun, \
        noWarn, LnoWarn, noOutput, LnoOutput, showExpand, \
        LshowExpand, chshow, Lchshow 
    
    if o == 'd':
        debug = Ldebug = 1

    elif o == 'o':
        showFilenames = LshowFilenames = 1

    elif o == 'p':
        pshow = Lpshow = 1

    elif o == 's':
        seqshow = Lseqshow = 1

    elif o == 'r':
        showrun = Lshowrun = 1

    elif o == 'w':
        noWarn = LnoWarn = 1

    elif o == 'n':
        noOutput = LnoOutput = 1

    elif o == 'e':
        showExpand = LshowExpand = 1

    elif o == 'c':
        chshow = Lchshow = 1
    
def setDebug(ln):
    """ Set debugging options dynamically. """

    # This needs to be here to avoid circular import problem
    from MMA.common import opt2pair
    from MMA.common import dPrint
    
    global Ldebug, debug, LshowFilenames, showFilenames, \
        Lpshow, pshow, Lseqshow, seqshow, Lshowrun, showrun, \
        LnoWarn, noWarn, LnoOutput, noOutput, LshowExpand, showExpand, \
        Lchshow, chshow, LplecShow, plecShow, LrmShow, rmShow, \
        LgvShow, gvShow
    
    msg = ("Debug: Use MODE=On/Off where MODE is one or more of "
           "DEBUG, FILENAMES, PATTERNS, SEQUENCE, GROOVE, "
           "RUNTIME, WARNINGS, EXPAND, ROMAN or PLECTRUM.")

    if not len(ln):
        from MMA.common import error
        error(msg)

    # save current flags

    Ldebug = debug
    LshowFilenames = showFilenames
    Lpshow = pshow
    Lseqshow = seqshow
    Lshowrun = showrun
    LnoWarn = noWarn
    LnoOutput = noOutput
    LshowExpand = showExpand
    Lchshow = chshow
    LplecShow = plecShow
    LrmShow = rmShow
    LgvShow = gvShow

    ln, opts = opt2pair(ln, 1)
    if ln:
        error("Each debug option must be a opt=value pair.")

    for cmd, val in opts:
        if val == 'ON' or val == '1':
            val = 1
        elif val == 'OFF' or val == '0':
            val = 0
        else:
            error("Debug: %s needs ON, 1, OFF, or 0 arg." % cmd)

        if cmd == 'DEBUG':
            debug = val
            if debug:
                dPrint("Debug=%s." % val)

        elif cmd == 'FILENAMES':
            showFilenames = val
            if debug:
                dPrint("ShowFilenames=%s." % val)

        elif cmd == 'PATTERNS':
            pshow = val
            if debug:
                dPrint("Pattern display=%s." % val)

        elif cmd == 'SEQUENCE':
            seqshow = val
            if debug:
                dPrint("Sequence display=%s." % val)

        elif cmd == 'RUNTIME':
            showrun = val
            if debug:
                dPrint("Runtime display=%s." % val)

        elif cmd == 'WARNINGS':
            noWarn = not(val)
            if debug:
                dPrint("Warning display=%s" % val)

        elif cmd == 'EXPAND':
            showExpand = val
            if debug:
                dPrint("Expand display=%s." % val)

        elif cmd == 'ROMAN':
            rmShow = val
            if debug:
                dPrint("Roman numeral chords/slash display=%s" % val)

        elif cmd == 'GROOVE':
            gvShow = val
            if debug:
                dPrint("Groove re-define display=%s" % val)

        elif cmd == 'PLECTRUM':
            plecShow = val
            if debug:
                dPrint("Plectrum display=%s" % val)

        else:
            from MMA.common import error
            error(msg)

            
def getFlags():
    """ Returns current values of debug flags in a string.
        Used by macro.py to expand $_Debug. 
    """    
    
    return "Debug=%s  Filenames=%s Patterns=%s " \
        "Sequence=%s Runtime=%s Warnings=%s Expand=%s " \
        "Roman=%s Plectrum=%s Groove=%s" % \
           (debug, showFilenames, pshow, seqshow, showrun,
            int(not noWarn), showExpand, rmShow, plecShow, gvShow)

def getLFlags():
    """ Returns last set values of debug flags in a string.
        Used by macro.py to expand %_LastDebug. 
    """
    
    return "Debug=%s  Filenames=%s Patterns=%s " \
                "Sequence=%s Runtime=%s Warnings=%s Expand=%s " \
                "Roman=%s Plectrum=%s Groove=%s" % \
                (Ldebug, LshowFilenames, Lpshow, Lseqshow, Lshowrun,
                 int(not LnoWarn), LshowExpand, LrmShow, LplecShow, LgvShow)

def trackSet(track, func):
    """ Print a debug message for functions which set a track setting. 

        track - name of the track (Chord-Sus ... )
        name - the name of the function (Strum, Compress ...)

        By using the macro formatting functions we get consistent output 
         between debug and macro expansion.
    """

    # Need to do this way to avoid circular import problem
    from MMA.macro import macros
    from MMA.common import dPrint
    
    dPrint("Set %s %s: %s" % (track, func,
            macros.sysvar("%s_%s" % (track, func.upper()))))




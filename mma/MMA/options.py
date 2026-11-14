# options.py

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

import getopt
import sys
import os
import tempfile

import MMA.docs
import MMA.parse
import MMA.chords
import MMA.volume
import MMA.exits

from . import gbl
from MMA.common import *
from MMA.macro import macros

cmdSMF = None

def cmdLine(l):
    """ Try to take a mma input line and parse it like a command line. 
        An empty CmdLine is just ignored. """
    
    if l:
        opts(l)

def cmdError(e):
    """ Illegal internal command line options."""

    error("CmdLine: the command line option '%s' is not permitted in a MMA script." % e)

def opts(l=None):
    """ Option parser. 
         FIXME: this code segment is much too long!
    """

    if not l:
        l = sys.argv[1:]
        internal = False
    else:
        internal = True

    try:
        opts, args = getopt.gnu_getopt(
                         l, "b:B:dpsS:ri:wneom:f:M:cLgGvVD:01PT:I:x:", [])
    except getopt.GetoptError:
        usage()

    for o, a in opts:
        if o == '-b':
            setBarRange(a)

        elif o == '-B':
            setBarRange(a)
            gbl.barRange.append("ABS")

        elif o in ('-d', '-o', '-p', '-s', '-r', '-w', '-n', '-e', '-c'):
            import MMA.debug   # circular dep. problem
            MMA.debug.cmdLineDebug(o[-1])
        
        elif o == '-S':
            ln = a.split('=', 1)
            macros.setvar(ln)

        elif o == '-L':
            gbl.printProcessed = True

        elif o == '-f':
            import MMA.paths
            gbl.outfile = a
            if internal:
                warning("Output filename overwritten by -f CmdLine option.")
                MMA.paths.createOutfileName(".mid")

        elif o == '-i':
            import MMA.paths
            if internal:
                cmdError("-i")
            MMA.paths.setRC(a)

        elif o == '-g':
            if internal:
                cmdError("-g")
            gbl.makeGrvDefs = 1

        elif o == '-G':
            if internal:
                cmdError("-G")
            gbl.makeGrvDefs = 2

        elif o == '-m':
            try:
                a = int(a)
            except:
                error("Expecting -m arg to be a integer")
            gbl.maxBars = a

        elif o == '-v':
            print("%s" % gbl.version)
            if not internal:
                sys.exit(0)

        elif o == '-M':
            global cmdSMF
            if a in ['0', '1']:
                cmdSMF = a
            else:
                error("Only a '0' or '1' is permitted for the -M arg")

        elif o == '-T':   # set tracks to generate, mute all others
            gbl.muteTracks = a.upper().split(',')

        elif o == '-D':
            if internal:
                cmdError("-D..")
            if a == 'xl':
                gbl.createDocs = 1

            elif a == 'xh':
                gbl.createDocs = 2

            elif a == 's':
                gbl.createDocs = 3

            elif a == 'gh':
                gbl.createDocs = 4

            elif a == 'js':
                gbl.createDocs = 5

            elif a == 'bo':
                gbl.createDocs = 99

            elif a == 'k':
                import MMA.alloc
                # important! Needs a space before the trailing LF for mma.el
                print("Base track names: %s \n" % 
                      ' '.join([a for a in sorted(MMA.alloc.trkClasses)]))
                print("Commands: %s BEGIN END DEFAULT\n" % 
                      ' '.join([a for a in sorted(MMA.parse.simpleFuncs)]))
                print("TrackCommands: %s \n" %
                      ' '.join([a for a in sorted(MMA.parse.trackFuncs)]))
                print("Not complete ... subcommands, comments, chords...")
                sys.exit(0)

            else:
                print("Unknown option: '-D%s'." % a)
                usage()

        elif o == '-0':
            import MMA.sync
            MMA.sync.synchronize(['START'])

        elif o == '-1':
            import MMA.sync
            MMA.sync.synchronize(['END'])

        elif o == '-P':
            gbl.playFile = 1

        elif o == '-I':
            # We use -I for plugin help and overload it to discard 
            # the plugin security. Use -II for security override.
            # It does mean you can't have plugin called "I", but
            # you could use "i" and it'll work.
            import MMA.regplug
            if a == 'I':
                MMA.regplug.secOverRide = True

            # Plugin help. Note we have not loaded any plugins at this
            # point. pluginHelp() will find the plugin, register it and
            # call its help function.
            else: 
                MMA.regplug.pluginHelp(a)
                sys.exit(0)
                

        elif o == '-V':
            import MMA.file
            
            if internal:   # can't have a -V in a -V :)
                cmdError("-V")
                
            gbl.playFile = 2  # signal create and play groove
            if not args:
                error("-V: option requires Groove Name.")

            _, tfile = tempfile.mkstemp(prefix="MMA_", suffix=".mma")
            op = open(tfile, "w")
            groove = ''
            cmds = []
            chords = "I, vi, ii, V7"
            count = 4
            for g in args:
                if '=' in g:
                    c = g.split('=')
                    if c[0].upper() == 'CHORDS':
                        chords = c[1]
                    elif c[0].upper() == "COUNT":
                        count = c[1]
                        try:
                            count = int(count)
                        except:
                            error("-V: expecting integer for Count.")
                    else:
                        cmds.append(c)
                elif groove:
                    error("-V: Only one groove name permitted.")
                else:
                    groove = g
            if not groove:
                error("-V: no groove name specified.")

            op.write("Groove %s\n" % groove)
            for g in cmds:
                op.write("%s %s \n" % (g[0], g[1]))
            chords = chords.split(',')
            while len(chords) < count:
                chords += chords
            chords = chords[:count]
            for c in chords:
                op.write("%s\n" % c)

            op.close()

            # we can only have one scratch file, so no fear of overload.
            # otherwise we might need to explicity delete file here.
            MMA.exits.files.append(tfile)

            args = [tfile]  # fake the CLI so mma thinks the created file is yours
            
        elif o=='-x':  # any one of some xtra, seldom used, options
            import MMA.xtra
            MMA.xtra.xoption(a, args)
            
        else:
            usage()      # unreachable??

    if internal:
        return

    # a few sanity checks

    #if  MMA.writeMid.splitOutput:
    #    if gbl.playFile:
    #        error("The -P (play) option is not compatible with channel/track splitting.")
    #    if gbl.infile == 1:
    #        error("The '-' (read from stdin) is not compatible with channel/track splitting.")
            
    # we have processed all the args. Should just have a filename left

    if len(args) > 1:
        usage("Only one input filename is permitted, %s given on command line." % len(args))

    if gbl.infile:
        usage("Input filename already assigned ... should not happen.")

    if args:
        gbl.infile = args[0]

    # if a single '-' is left on the cmd line user want stdin. We set the
    # the input filename to numeric 1 which can't be entered.

    if gbl.infile == '-':
        gbl.infile = 1
        
        if not gbl.outfile:
            import MMA.debug   # circular dep. problem
            if not(MMA.debug.noOutput):
                error("Input from STDIN specified. Use -f to set an output filename.")

    
def usage(msg=''):
    """ Usage message. """

    txt = [
        "MMA - Musical Midi Accompaniment",
        "  Copyright 2003-22, Bob van der Poel. Version %s" % gbl.version,
        "  Distributed under the terms of the GNU Public License.",
        "  Usage: mma [opts ...] INFILE [opts ...]",
        "",
        "Options:",
        " -b <n> Limit compilation to n1-n2 bars (comment numbers)",
        " -B <n> Like -b but for absolute bar numbers",
        " -c    display default Channel assignments",
        " -d    enable lots of Debugging messages",
        " -Dk   print list of MMA keywords",
        " -Dxl  eXtract Latex doc blocks from file",
        " -Dxh  eXtract HTML doc blocks from file",
        " -Dgh  extract HTML Groove doc",
        " -Djs  extract JSON Groove information from file",
        " -Dbo  extract text for browser app",
        " -Ds   extract sequence lists from file",
        " -e    show parsed/Expanded lines",
        " -f <file>  set output Filename",
        " -g    update Groove dependency database",
        " -G    create Groove dependency database",
        " -i <file> specify init (mmarc) file",
        " -I <plugin> print docs for plugin if available",
        " -II   skip permissions test for plugins (Dangerous!)",
        " -L    show order of bars processed",
        " -m <x> set Maxbars (default == 500)",
        " -M <x> set SMF to 0 or 1",
        " -n    No generation of midi output",
        " -o    show complete filenames when Opened",
        " -p    display Patterns as they are defined",
        " -P    play song (don't save) with player",
        " -r    display Running progress",
        " -s    display Sequence info during run",
        " -S <var[=data]>  Set macro 'var' to 'data'",
        " -T <tracks> Limit generation to specified tracks",
        " -v    display Version number",
        " -V <groove [options]> preview play groove",
        " -w    disable Warning messages",
        " -xCHORDS=<chord list> test listed chords for validity",
        " -xNOCREDIT disable MMA credits in Midi Meta track",
        " -xCHECKFILE=<filename> check chords in file",
        " -xTSplit  create midi for each track",
        " -xCSplit  create MIDI for each channel",
        " -0    create sync at start of all channel tracks",
        " -1    create sync at end of all channel tracks",
        " -     a single hyphen signals to use STDIN instead of a file"]

    for a in txt:
        print(a)

    if msg:
        print("\n%s" % msg)
    
    sys.exit(1)


def setBarRange(v):
    """ Set a range of bars to compile. This is the -B/b option."""
    
    if gbl.barRange:
        error("Only one -b or -B permitted.")

    for ll in v.split(','):

        l = ll.split("-")

        if len(l) == 2:
            s, e = l
            try:
                s = int(s)
                e = int(e)
            except:
                usage("-B/b ranges must be integers, not '%s'." % l)

            for a in range(s, e + 1):
                gbl.barRange.append(str(a))

        elif len(l) == 1:
            try:
                s = int(l[0])
            except:
                usage("-B/b range must be an integer, not '%s'." % l[0])
            gbl.barRange.append(str(s))

        else:
            usage("-B/b option expecting N1-N2,N3... not '%s'." % v)

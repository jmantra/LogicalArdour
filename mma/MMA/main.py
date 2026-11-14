# main.py

"""
The program "MMA - Musical Midi Accompaniment" and the associated
modules distributed with it are protected by copyright.

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

import os

import MMA.midi
import MMA.midifuncs
import MMA.parse
import MMA.file
import MMA.options
import MMA.auto
import MMA.docs
import MMA.tempo
import MMA.debug
import MMA.paths
import MMA.writeMid

from  MMA.safe_eval import safeEnv

from . import gbl
from   MMA.common import *


cmdSMF = None

########################################
########################################

# This is the program mainline. It is called/executed
# exactly once from a call in the stub program mma.py.

# for some reason, someone might want a different encoding
# real easy to set it from env at startup
m = safeEnv( 'MMA_ENCODING' )
if m:    # don't set to empty ... will crash
    gbl.encoding = m

# MMA prints errors/warning/debug to stdout
# this will redirect to a file
gbl.logFile = safeEnv('MMA_LOGFILE')

MMA.paths.init()   # initialize the lib/include paths

# Get our command line stuff

MMA.options.opts()


#  LibPath and IncPath are set before option parsing, but
#  debug setting wasn't. So we need to do the debug for this now
if MMA.debug.debug:
    dPrint("Initialization has set LibPath set to %s" % MMA.paths.libPath)
    dPrint("Initialization has set IncPath set to %s" % MMA.paths.incPath)

#######################################
# Set up initial meta track stuff. Track 0 == meta

m = gbl.mtrks[0] = MMA.midi.Mtrk(0)

if gbl.infile:
    if gbl.infile != 1:
        fileName = MMA.file.locFile(gbl.infile, None)
        if fileName and not gbl.noCredit:
            m.addTrkName(0, "%s" % fileName.rstrip(".mma"))
            m.addText(0, "Created by MMA. Input filename: %s" % fileName)


m.addTempo(0, gbl.tempo)      # most user files will override this
MMA.tempo.setTime(['4/4'])    # and this. IMPORTANT! Sets default chordTabs[]
   
# Read RC files
MMA.paths.readRC()


################################################
# Update the library database file(s) (-g option)
# Note: This needs to be here, after reading of RC files

if gbl.makeGrvDefs:
    if gbl.infile:
        error("No filename is permitted with the -g option")
    MMA.auto.libUpdate()                # update and EXIT


################################
# We need an input file for anything after this point.

if not gbl.infile:
    if gbl.createDocs:
        gbl.lineno = -1
        error("-D options require a filename.")
    MMA.options.usage("No input filename specified.")

################################
# Just extract docs (-Dxh, etc) to stdout.

if gbl.createDocs:
    if gbl.createDocs == 4:
        MMA.docs.htmlGraph(gbl.infile)
    else:
        f = MMA.file.locFile(gbl.infile, None)
        if not f:
            error("File '%s' not found" % gbl.infile)
        MMA.parse.parseFile(f)
        MMA.docs.docDump()
    sys.exit(0)


#########################################################
# This cmdline option overrides the setting in RC files

if MMA.options.cmdSMF is not None:
    gbl.lineno = -1
    MMA.midifuncs.setMidiFileType(['SMF=%s' % MMA.options.cmdSMF])

######################################
# Create the output filename

if not MMA.debug.noOutput:
    MMA.paths.createOutfileName(".mid")


################################################
# Read/process files....

# First the mmastart files
MMA.paths.dommaStart()

# The song file specified on the command line

if gbl.infile == 1:  # use stdin, set filename to 1
    f = 1
else:
    f = MMA.file.locFile(gbl.infile, None)

    if not f:
        gbl.lineno = -1
        error("Input file '%s' not found" % gbl.infile)

MMA.parse.parseFile(f)

# Finally, the mmaend files
MMA.paths.dommaEnd() 

#################################################
# Just display the channel assignments (-c) and exit...

if MMA.debug.chshow:
    msg = ["\nFile '%s' parsed, but no MIDI file produced!" % gbl.infile]
    msg.append("\nTracks allocated:\n")
    k = list(gbl.tnames.keys())
    k.sort()
    max = 0
    for a in k + gbl.deletedTracks:
        if len(a) > max:
            max = len(a)
    max += 1
    wrap = 0
    for a in k:
        wrap += max
        if wrap > 60:
            wrap = max
            msg.append('\n')
        msg.append(" %-*s" % (max, a))
    msg.append('\n')
    print(' '.join(msg))
    
    if gbl.deletedTracks:
        msg = ["Deleted Tracks:\n"]
        wrap = 0
        for a in gbl.deletedTracks:
            wrap += max
            if wrap > 60:
                wrap = max
                msg.append('\n')
            msg.append(" %-*s" % (max, a),)
        msg.append('\n')
        print(' '.join(msg))
        
    msg=["Channel assignments:\n"]
    for c, n in sorted(gbl.midiAssigns.items()):
        if n:
            wrap = 3
            msg.append(" %2s" % c)
            for nn in n:
                wrap += max
                if wrap > 63:
                    msg.append('\n    ')
                    wrap = max+3
                msg.append(" %-*s" % (max, nn))
            msg.append('\n')
    print(' '.join(msg))

    sys.exit(0)

MMA.writeMid.maker()

if MMA.debug.debug:
    dPrint("Completed processing '%s' to '%s'." %
           (gbl.infile, MMA.paths.outfile))
    

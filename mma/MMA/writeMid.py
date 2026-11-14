# writeMid.py

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

This module is responsible for actually writing the MIDI tracks to a file.

"""

import os
import sys
import copy
import subprocess

import MMA.midi
import MMA.lyric
from . import gbl
from   MMA.common import *

splitOutput = None

def createMIDI(outfile):
    
    fileExist = os.path.exists(outfile)

    if fileExist:
        msg = "Overwriting existing"
    else:
        msg = "Creating new"

    print("%s midi file (%s bars, %.2f min / %d:%02d m:s): '%s'" %
        (msg, gbl.barNum, gbl.totTime, gbl.totTime, (gbl.totTime%1)*60, outfile))

    # Insert the estimated play time in seconds into a comment line.
    # A player program can search for this and display it. The value
    # will be terminated by a null which should be easy enuf to search for.

    gbl.mtrks[0].addText(0, "DURATION: %d" % (gbl.totTime*60) )
    
    try:
        out = open(outfile, 'wb')
    except IOError:
        error("Can't open file '%s' for writing" % outfile)

    MMA.midi.writeTracks(out)
    out.close()

def createOutName(name, subname):
    if name.endswith(".mid"):
        name = name.replace(".mid", "-%s.mid" % subname)
    else:
        name = "%s-%s" % (name, subname)
    return name

   
def channelSplit(outfile):
    """ Write midi files split by channel number. """

    if len(sys.argv) > 3:
        error("Command line arguments are not permitted using '-xTsplit'.")
        
    tempMtrk = copy.copy(gbl.mtrks)  # keep this copy pristine 
    # zap all tracks out
    for c in sorted(list(tempMtrk))[1:]:
        del gbl.mtrks[c]
    # we now have an empty mtrk, except for 0 which is for meta data
    # now process each separately
    for c in sorted(list(tempMtrk))[1:]:   
        gbl.mtrks[c] = copy.copy(tempMtrk[c])  # restore only 1 track
        createMIDI( createOutName(outfile, "%02d" % c) )
        del gbl.mtrks[c]
    gbl.mtrks = copy.copy(tempMtrk)
    
def trackSplit(outfile):
    """ Write midi files split by trackname. Recursively calls MMA. """
    
    if len(sys.argv) > 3:
        error("Command line arguments are not permitted using '-xTsplit'.")

    mma = sys.argv[0]
    print("Splitting by tracks:")
    for ff in sorted(gbl.tnames.keys()):
        oname = "-f%s" % createOutName(outfile, ff)
        z=subprocess.run([ mma, gbl.infile, oname, "-T%s" % ff])

#########################3

def maker():
    """ Called from the main loop to create the midi, etc.
        returns: Name of output file
    """
    import MMA.debug   # here! avoid circular import

    ####################################
    # Dry run, no output

    if MMA.debug.noOutput:
        gbl.lineno = -1
        warning("Input file parsed successfully. No midi file generated")
        sys.exit(0)
        
    ##############################
    # Create the output (MIDI) file

    gbl.lineno = -1    # disable line nums for error/warning

    # We fix the outPath now. This lets you set outpath in the song file.
    #
    #  The filename "outfile" was created in paths, get a copy.
    #     It is either the input filename with '.mma' changed to '.mid' (or kar)
    #     OR if -f<FILE> was used then it's just <FILE>.
    #
    #  If any of the following is true we skip inserting the outputpath into the
    #     filename:
    #       - if outfile starts with a '/'
    #       - if outPath was not set
    #       - if -f was used
    #
    #   outPath is inserted into the filename. If outPath starts with
    #   a ".", "/" or "\ " then it is inserted at the start of the path;
    #   otherwise it is inserted before the filename portion.

    outfile = MMA.paths.outfile

    if (not outfile.startswith('/')) and gbl.outPath \
            and not gbl.outfile and not gbl.playFile:
        if gbl.outPath[0] in '.\\/':
            outfile = "%s/%s" % (gbl.outPath, outfile)
        else:
            head, tail = os.path.split(outfile)
            outfile = "%s/%s/%s" % (head, gbl.outPath, tail)

    fileExist = os.path.exists(outfile)

    # Check if any pending midi events are still around. Mostly
    #   this will be a DRUM event which was assigned to the 'DRUM'
    #   track, but no DRUM track was used, just DRUM-xx tracks used.

    for n in gbl.tnames.values():
        if n.channel:
            n.clearPending()
            n.doMidiClear()
            n.doChannelReset()
            if n.riff:
                warning("%s has pending Riff(s)" % n.name)

    # Check all the tracks and find total number used. When
    #   initializing each track (class) we made an initial entry
    #   in the track at offset 0 for the track name, etc. So, if the
    #   track only has one entry we can safely skip the entire track.

    trackCount = 1    # account for meta track

    for n in sorted(gbl.mtrks.keys())[1:]:     # check all but 0 (meta)
        if len(gbl.mtrks[n].miditrk) > 1:
            trackCount += 1
    
    if gbl.printProcessed:
        import MMA.rangeify
        print ("Bars processed: %s" % MMA.rangeify.rangeify(gbl.barLabels))

    if trackCount == 1:  # only meta track
        if fileExist:
            print("\n")
        print("No data created. Did you remember to set a groove/sequence?")
        if fileExist:
            print("Existing file '%s' has not been modified." % outfile)
        sys.exit(1)

    MMA.lyric.lyric.leftovers()

    # go and write file (or files if splitting)

    if splitOutput == 'CHANNELS':
        channelSplit(outfile)
    elif splitOutput == 'TRACKS':
        trackSplit(outfile)
    else:
        createMIDI(outfile)
    
    if gbl.playFile:
        import MMA.player
        MMA.player.playMidi(outfile)

    return(outfile)

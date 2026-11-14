# extend plugin

# This plugin is a sortof reverse truncate. It parses its arguments
# and splits the data out into 2 lines: an original line short enough for the
# current time, a truncate line and shortened line.
# The goal is to take:
#   Time 3
#   @extend side=right len=4 22 Am Bm C7 E9
#   ... into ...
#   22 Am Bm C7
#   Truncate side=right 1
#   22 E9
#   

import MMA.gbl as gbl
import MMA.timesig
from MMA.common import *

def run(ln):
    barLen = None     # We do need to fill this value
    side = 1          # default to left (1)
    timesig = None    # optional. Helpful if importing results into score prog.
    
    ln, opts = opt2pair(ln)  # Use MMA to gather options
    for cmd, o in opts:
        if cmd.upper()=='SIDE':
            side = o
        elif cmd.upper() == 'LEN':
            barLen = stoi(o, "@Extend LEN option expecting integer")
            if barLen == gbl.QperBar:
                error("@Extend: Expected the Len= to be different from the current TIME value.")
        elif cmd.upper() == "TIMESIG":
            timesig = o

    # Do some sanity/validity tests
    
    if '*' in ln:
        error("@Extend: does not support the '*' multiplier in data lines.")

    for a in ln:
        if '{' in a:
            error("@Extend: Does not support embedded solo/melody. Use Riff instead.")

        if '@' in a:
            error("@Extend: the '@' notation in chord data lines is not supported. " \
                      "You probably don't need to use it since it makes very little " \
                      "difference to the final sound. But, you can always create 2 chord " \
                      "lines and a Truncate by hand.")
            
    if barLen == None:
        error("@Extend: requires a LEN=x option. x is the new length of bar")

    if barLen > gbl.QperBar * 2:
        error("@Extend: doesn't support lines longer than 2x the current TIME setting.")

    # Create new lines for MMA to consider
    
    line1 = []
    line2 = []

    # we're shortening the line (just a normal Truncate) so
    # we don't need the split data. Just end up with
    #   Truncate ...
    #   Data
    if barLen <= gbl.QperBar:
        line2 = ln[:]

    # lengthen. End with:
    #   Data for full bar
    #   Truncate ..
    #   Data for partial bar
    else:
        if ln[0].isdigit():
            line1.append(ln[0])
            line2.append(ln[0])
            ln=ln[1:]
        for c,b in enumerate(ln):
            if c < gbl.QperBar:
                line1.append(b)
            else:
                line2.append(b)
        if len(line2)==0 or len(line2) == 1 and line2[0].isdigit:
            line2.append('/')

    len2 = int(barLen-gbl.QperBar)
    if len2<1:
        len2=barLen

    # Generate input for MMA. 
    ret = []
    
    if timesig:
        oldtime=MMA.timesig.timeSig.getAscii()
        ret.append(["Timesig", timesig])

    if len2 <= gbl.QperBar:
        ret.append(line1)

    ret.append( ["Truncate", 'side=%s' % side, '%s' % len2 ] )

    ret.append(line2)

    if timesig:
        ret.append(["Timesig",  oldtime])

    # And now MMA will happily do it all.
    gbl.inpath.push(ret, [gbl.lineno] * len(ret))

# Entry for usage (mma -Iextend)

def printUsage():
    print("""
@Extend len=dd [other options] Chord Data

Convert a data line into parts so that it can be longer (in beats)
than what the current Time supports. For example, you might have a
song in 3/4 which switches to 4/4 for a few bars. This function
will split the data lines into parts with interleaving TRUNCATE
lines. You can use a short length and it will work as a normal 
Truncate function.

A few differences between this plugin and the native Truncate:
  The is no Count option
  The length is specified with Len=dd
  The new bar length must be an integer value

Supported options are:
  Side=right,left,beat  -- defaults to left
  Len=count             -- new bar length REQUIRED
  TimeSig=N/D           -- inserts a timesig event in the midi file

Caution: Do not attempt to use this in Begin/End block. The line will
         recurse and you will end up in an infinite loop.

Following the options is a MMA data line with optional line number and chords.

  Author: bvdp, 2018/12/25. """)
    



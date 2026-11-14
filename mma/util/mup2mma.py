#!/usr/bin/env python 

""" mup2mma extracts chords from a MUP music notation file and
    creates a MMA file. For this to work the MUP file must use
    the macro "C" for chord. In my MUP files I have the following:
    
        define C bold (11) chord above all: @
        
    This script just checks all input lines and assumes that anything
    starting with "C" is a chord line.

    Additional "features":
    
        Lines in the form "// TEMPO: xx" generate a Tempo entry
        "time =" lines are parsed for common time signatures
        repeats are inserted as comment lines

    0.3 - added options:
                 -m   add melody lines
                 -l     add lyrics
                 -o    overwrite

    0.4 - reformatted output
    
    0.5 - corrected melody/lyric notation.

    1.0 - converted to python 2 or 3 (March/2014)

    bvdp, Dec/2004
    
"""

import os
import sys
import getopt

# Useful functions

def error(m=''):
    print("Error: %s" % m)
    sys.exit(1)
    
def usage():
    print("""mup2mma - (c) Bob van der Poel
Extract MMA data from MUP file.
Options:
 -o   overwrite existing MMA file
 -m   extract melody data
 -l   extract lyric data
 -v   print version
""")
    sys.exit(0)

# Global variables

Version = '1.0'

overwrite = 0         # set if overwrite of old mma file okay
doLyric = 0           # set if we want lyrics output
doMelody = 0          #  set if we want melody output


# Parse command line, open files 
 
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],  "omlv")
except getopt.GetoptError:
    usage()

for o, a in opts:
    if o == '-o':
        overwrite = 1
    elif o == '-l':
        doLyric = 1
    elif o == '-m':
        doMelody = 1
    elif o == '-v':
        print(Version)
        sys.exit(0)
    else:
        usage()

if len(args) != 1:
    error("Exactly 1 filename is required.")

infile = args[0]

outfile = os.path.basename(infile)
if outfile.endswith('.mup'):
    outfile = outfile[:-4]
title = outfile.replace("-", ' ').title()
outfile += ".mma"

try:
    bars = open(infile)
except:
    error("Can't open input file '%s'." % infile)

if os.path.exists(outfile) and not overwrite:
    error("File '%s' already exists." % outfile)

try:
    out = open(outfile, "w")
except:
    error("Can't open output file '%s'." % outfile)

# Input and output files open, start processing

out.write( "// %s\n\n" % title)

bnum = 1

donebar = 0
melody = ''
lyric = ''
chordList = []

for b in bars:
    b = b.strip()
    if b == '':               # skip empty lines
         continue

    if b.startswith("// TEMPO:"):
        out.write("Tempo %s\n\n" % b.split()[2])
        continue

     # Parse line number from MUP
    
    if b.startswith('// #') or b.startswith('//# '):
        bnum = b[4:]
        continue

    # strip out mid-line comments and
    # just keep stuff to the left of //
    if '//' in b:
        b = b.split('//', 1)[0].strip()
        if not b:
            continue
        
    # Parse out time sig from MUP
    
    ck = b.split("=")
    
    if len(ck) and ck[0].strip() == 'time':
        ts=ck[1].strip()
        if ts in ('common', '4/4'):
            beats = 4
            posStep = 1
            
        elif ts in ('cut', '2/4', '2/2'):
            beats = 2
            posStep = .5
            
        elif ts=='3/4':
            beats = 3
            posStep = 1
            
        elif ts=='6/8':
            beats = 6
            posStep = 1
        
        elif ts=='12/8':
            beats = 12
            posStep = 4
        elif ts=='5/4':
            beats = 5
            posStep = 1
        else:
            error("Unknown time sig, %s" % b)
    
    
        
    # mup accepts "(dblbar)repeatstart" (no space)
    # but we don't like it!
    b=b.replace("dblbar)r", "dblbar) r")
    
    # Parse out melody, lyric and chords.
    #    Melody must be a line starting with "M:"
    #    Lyric must be a line starting with "L:"
    #    Chord must be a line starting with "C "

    key = b.split()[0]
            
    if key == 'M:' and doMelody:         
        melody = b.split(' ', 1)[1]
        
    elif key == 'L:' and doLyric:
        lyric = b.split(' ', 1)[1]

    elif key == 'C':
        ch = b[2:]
        ch=ch.replace ('"', ' ')
        ch=ch.replace('&', 'b')
        ch = ch[:-1]
        ch=ch.split(';')
        
        chordList = []
        pos = 1.0
        
        for c in ch:
            c = c.split()
            off = c[0]
            
            # Strip out printing offset from chord. Since the position
            # has been split off, we just strip out everything after the
            # inital '['. If this doesn't work, then the MUP is wrong as well
            #    eg:  1.5[-5]  becomes 1.5 
            
            if off.count('['):
                off=off[:off.index('[')]
            
            count = float(off)
            
            while pos < count:
                chordList.append('/')
                pos += posStep            
                
            chord=c[1]
            if chord.upper()=="TACET" or chord.upper()=='N.C':
                chord = 'z'
            
            chord = chord.replace('^', 'M')
            chord = chord.replace('o', 'dim')
            chord = chord.replace('\\(dim)', 'dim')
            chord = chord.replace('6/9', '6(add9)')

            chordList.append(chord )
            pos += posStep
        
    
    elif key in ('bar', 'repeatend', 'endbar', 'dblbar', '(dblbar)',
            'repeatstart', 'repeatboth' ):

        out.write('%-4s' % bnum) # no CR, chord will append to line number
        
        if not chordList:
            chordList = ['/'] 
        for a in chordList:
            out.write((' %6s' % a).rstrip())
            chordList = []
            
        if doMelody and melody:
            out.write(('  { %s }' % melody).rstrip())
            melody = ''
            
        if doLyric and lyric:
            out.write(('  [ %s ]' % lyric).rstrip())
            lyric = ''
        
        out.write('\n')

        try:
            if int(bnum) % 4 == 0:   # put in blank line every 4 bars
                out.write('\n')
        except:
            pass

        if key == 'repeatend':
            out.write( "\n// RepeatEnd\n\n")
        if key == 'repeatboth':
            out.write( "\n// RepeatEnd\n\n")
            out.write( "// Repeat\n\n")
        if key == "repeatstart" or key=='(dblbar)':
            out.write( "\n// Repeat\n\n")
            
        rpt = b.split()[1:]
        
        if len(rpt) and rpt[0] == "ending":
            out.write( '\n// RepeatEnding\n\n')

    else:
        pass     # Just ignore other MUP stuff
    
out.write('\n')
out.close()

        



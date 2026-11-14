#!/usr/bin/env python

# Convert mma file with roman numeral chords to std.

import sys, os, platform

# setup for the MMA modules.

platform = platform.system()

if platform == 'Windows':
    dirlist = ( sys.path[0], "c:/mma", "c:/program files/mma", ".")
else:
    dirlist = ( sys.path[0], "/usr/local/share/mma", "/usr/share/mma", '.' )

for d in dirlist:
    moddir = os.path.join(d, 'MMA')
    if os.path.isdir(moddir):
        if not d in sys.path:
            sys.path.insert(0, d)
        MMAdir = d
        break

import MMA.roman
import MMA.keysig
import MMA.gbl as gbl
import MMA.midi

def error(m):
    """ Abort on error with message. """
    print m
    sys.exit(1)

def usage():
    """ Print usage message and exit. """

    print "Mma-rm2std, (c) Bob van der Poel"
    print "Convert a mma file using roman chords to std."
    print
    sys.exit(1)



##########################

if len(sys.argv[1:]) != 1:
    print "mma-rm2std: requires 1 filename argument."
    usage()
    
filename = sys.argv[1]

if filename[0] == '-':
    usage()

try:
    inpath = open(filename, 'r')
except:
    error("Can't access the file '%s'" % filename)


linenum = 1
m = gbl.mtrks[0] = MMA.midi.Mtrk(0)

for l in inpath:
    l=l.rstrip()

    if l.strip().upper().startswith("KEYSIG"):
        t = l
        if '//' in t:
            t = t[ :t.find('//')]
        t=t.split()
        MMA.keysig.keySig.set(t[1:])
        
    if l and l[0].isdigit():
        
        # strip off trailing lyric, notes, repeat or comment
        eolstuff = ''
        s=[]
        for d in ("*", "{", "[", '//'):
            if l.count(d):
                s.append(l.find(d))
        if s:
            s.sort()
            eolstuff = l[s[0]:]
            l = l[:s[0]]

        l = l.split()

        for i in range(1,len(l)):
            c=l[i]
            if c[0] == '/':
                l[i] = " %6s" % c
                continue

            lead = end = ''

            while c[0] in ('+', '-'):
                lead += c[0]
                c=c[1:]

            # strip from right side of chord barre, invert, etc.

            s = []
            for d in (":", ">", "/", 'z'):
                if c.count(d):
                    s.append(c.find(d))
            if s:
                s.sort()
                end = c[s[0]:]
                c = c[:s[0]]

            # all we have now is a chord name

            if c and c[0] in ("I", "V", "i", "v"):
                c=MMA.roman.convert(c)

            # reassemble name

            c = lead + c + end
            l[i] = " %6s" % c

        # reassemble line

        l.append(eolstuff)   # put back comment, lyric, etc.
        l = ' '.join(l)

    print l

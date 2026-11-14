#!/usr/bin/python

#  Works with python 2 and 3

# Renumber a mma song file. Just take any lines
# which start with a number and do those sequentially.

import sys, os


def error(m):
    """ Abort on error with message. """
    print(m)
    sys.exit(1)

def usage():
    """ Print usage message and exit. """

    print("""
Mma-renum, (c) Bob van der Poel
Re-numbers a mma song file and
cleans up chord tabbing.
Overwrites existing file!
""")
    sys.exit(1)



##########################

if len(sys.argv[1:]) != 1:
    print("mma-renum: requires 1 filename argument.")
    usage()

filename = sys.argv[1]

if filename[0] == '-':
    usage()

try:
    inpath = open(filename, 'r')
except:
    error("Can't access the file '%s'" % filename)

tempfile = "%s.%s.tmp" % (filename, os.getpid())
try:
    outpath = open( tempfile, 'w')
except:
    error("Can't open scratchfile '%s', error '%s'" % (tempfile, sys.exc_info()[0]) )

linenum = 1

for l in inpath:
    l=l.rstrip()

    if l and l[0].isdigit():
        try:
            currentLnum = int(l.split()[0])
        except:
            currentLnum = None
    else:
        currentLnum = None

    if currentLnum != None:
        otherstuff = ''           # break off non-chord items
        cmt = ''
        if l.count('//'):
            l, cmt=l.split('//', 1)

        for i,a in enumerate(l):
            if a in('{[*'):
                otherstuff=l[i:]
                l=l[:i]
                l=l.strip()
                break

        # if current line is 0 or less leave it alone
        # Should we test on neg values since MMA will not accept them??
        if currentLnum <= 0:
            newl = ['%-5s' % currentLnum]
        else:
            newl=['%-5s' % linenum]
            linenum += 1              # the global line number

        for a in l.split()[1:]:   # do each chord item
            newl.append(" %6s" % a)

        if otherstuff:            # join on non-chord stuff
            newl.append("    ")
            newl.append(otherstuff)

        if cmt:
            newl.append("   //")
            newl.append(cmt)

        newl=''.join(newl)

    else:
        newl = l

    outpath.write(newl + "\n")

inpath.close()
outpath.close()

try:
    os.remove(filename)
except:
    error("Cannot delete '%s', new file '%s' remains" % (filename, tempfile) )

try:
    os.rename(tempfile, filename)
except:
    error("Cannot rename '%s' to '%s'." % (tempfile, filename) )

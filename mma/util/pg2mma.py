#!/usr/bin/env python

""" Simple program to convert a PG music PAT file to MMA. """

import os, sys, time


def usage():
    print "pg2mma, (c) Bob van der Poel"
    print "Converts a PG-music PAT file to MMA."
    print "  usage: pg2mma <infile> <outfile>"
    print
    sys.exit(1)

def error(m):
    print m
    sys.exit(1)
        
if len(sys.argv[1:]) != 2:
    print "pg2mma: requires 2 filename arguments."
    usage()
    
ifile = sys.argv[1]
ofile = sys.argv[2]

if ifile[0] == '-' or ofile[0] == '-':
    usage()
    
try:
    infile = open(ifile, 'r')
except:
    error( "Cannot open input file %s." % ifile)
    

if os.path.exists(ofile):
    error("Outfile file %s already exists." % ofile)

try:
    outfile = open(ofile, 'w')
except:
    error( "Cannot open output file %s." % ofile )
    

outfile.write("// Converted by pg2mma from %s, %s.\n\n" % (ifile, time.asctime() ))
outfile.write("Begin Patch Set\n\n")

## Read and convert. 

lnum = 0
offadj = 0

while 1:
    l=infile.readline()

    lnum += 1

    if l == '':
        outfile.write("\nEnd    // end of Patch Set\n")
        infile.close()
        outfile.close()
        sys.exit(0)

    l=l.strip()

    if l=='':
        continue

    if l == "ONEBASED":
        offadj = 1
        continue

    if l[0] == ';':
        outfile.write("    // %s\n" % l[1:])
        continue

    if l[0] == '[':
        l = l[1:].strip()
        l = l.rstrip(']')
        if l:
            outfile.write("\n    // %s\n\n" % l)
        continue

    if not l or not l[0].isdigit():
        continue
                
    try:
        v,n = l.split('=',1)
    except:
        error( "Expecting '=' in pat line, line %s" % lnum)


    # Convert the patch name to non-space, CamelCase, no '.'s

    n = n.title()
    n = n.replace('.', '')
    n = n.replace(' ', '')
        
    # verify the voice value
    # apply offset adjustment

    v=v.rstrip('.')  # some files have extra dots!!

    t = v.split('.')

    if len(t) > 3:
        t=t[:3]

    if offadj:
        try:
            a = int(t[0])
        except:
            error( "Expecting integer value, '%s' line %s." % (v, lnum))
        t[0] = str( a - 1 )

    for a in t:
        try:
            a = int(a)
        except:
            error( "Expecting integer value in value set, '%s' line %s." % (v, lnum))
        
        if a<0 or a>127:
            error( "Each part of the value set must be 0..127, '%s' line %s." % (v,lnum))
    
    if len(t)==3 and t[2]=='0':
        t=t[:2]

    if len(t)==2 and t[1]=='0':
        t=t[0]

    outfile.write("    %s=%s\n" % ('.'.join(t) , n))

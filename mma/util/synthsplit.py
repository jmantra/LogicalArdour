#!/usr/bin/env python


# A hack of timsplit.py ... this plays each track out to a synth
# with aplaymidi. The idea is to record the works, split into tracks.


import sys, os, commands, time

bgtrack = "bg.wav"

def usage():
    print "synthsplit, (c) Bob van der Poel"
    print "Create multi-track wav file using"
    print "  MMA files and external synth."
    print
    sys.exit(0)
    
if len(sys.argv[1:]) != 1:
    print "synthsplit: requires 1 filename argument."
    usage()

mmafile = sys.argv[1]

if mmafile.endswith(".mma"):
    basename = mmafile[:-4]
else:
    basename = mmafile


# Create the background midi and wav. FIXME: have a command line option to skip

status, txt = commands.getstatusoutput("mma -0 %s -f %s.mid" % (mmafile, basename))
if status:
    print "synthplit error", status
    print txt
    sys.exit(1)

# create a wav of the base file. This should get copied to your mixer

#print "Creating background track:", basemid
#status, txt = commands.getstatusoutput("aplaymidi %s" % basemid )
#if status:
#    print "synthsplit error", status
#    print txt
#    sys.exit(1)

# Get the tracks generated in the file

status, txt = commands.getstatusoutput("mma -c %s" % mmafile)
txt = txt.split()
txt=txt[txt.index('assignments:')+1:]
tracklist=[]
for a in sorted(txt):
    try:
        int(a)
    except:
        tracklist.append(a)

print "MMA file '%s' being split to: " % mmafile,
for a in tracklist:
    print a,
print


# Do the magic. For each track call mma & create midi

for trackname in tracklist:
    cmd = "mma -0 %s -T %s -f %s-%s.mid" % (mmafile, trackname, basename, trackname) 
    print cmd
    status, txt = commands.getstatusoutput(cmd)
    if status:
        if txt.startswith("No data created"):
            print "NO DATA for '%s', skipping" % trackname
            continue
        print "synthsplit error", status
        print txt
        sys.exit(1)







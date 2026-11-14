#!/usr/bin/env python

# This program will take a mma file, split into separate tracks
# play them on a default external device and record as wav
# Will also work using timidity to create the wav files.

# bvdp  Jan/2011

# Sept/2015 - patched by Anthony Fok <foka@debian.org> for Python3.

from __future__ import print_function
import sys
import os
import subprocess
import getopt

# These can be reset from command line options

midiopts   = "-p 20"                #  -p
recordopts = "-D hw:2,0 -f cd"      #  -r
timopts    = "-OwM"                 #  -o
createbg = True                     #  -b
usetimidity = False                 #  -i

# Create option list. This copies defaults from above
# and freezes them into the message.

optmsg= ["  -m  set midi opts      (default = %s)" % midiopts,
         "  -r  recorder opts      (default = %s)" % recordopts,
         "  -o  timidity opts      (default = %s)" % timopts,
         "  -i  use TiMidity++     (default = %s)" % ("No", "Yes")[usetimidity],
         "  -b  create full track  (default = %s)" % ("No", "Yes")[createbg],
         "  -t  do only track X",
         "  -x  eXclude track X" ]

# screwing with these is optional

midiplayer = "/usr/bin/aplaymidi"    # path to player
recorder   = "/usr/bin/arecord"      # path to record program
timidity   = "/usr/bin/timidity"     # path to timidity
MMA = "mma"
tmpname = "tmp-%s" % os.getpid()
tmpmid  = "%s.mid" % tmpname 
bgtrack = "bg"

# Don't touch.

excludelist = []  # tracks to skip
onlylist    = []  # only do these tracks

def opts():
    """ Option parser. """

    global midiopts, recordopts
    global usetimidity, timopts
    global createbg, excludelist, onlylist

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:],
            "m:r:o:bix:t:", [] )
    except getopt.GetoptError:
        usage()

    for o,a in opts:
        if o == '-m':
            midiopts = a

        elif o == '-r':
            recordopts = a

        elif o == '-i':
            usetimidity = True

        elif o == '-o':
            timopts = a

        elif o == '-b':
            createbg = False

        elif o == '-t':
            onlylist.append(a.upper())

        elif o == '-x':
            excludelist.append(a.upper())

        else:
            print("Unknown option: %s %s" % (o, a))
            usage()

    if excludelist and onlylist:
        error("You can't set both exclude and do-only tracks.")

    if len(args) > 1:
        error("Too many filenames on command line.")
    elif not args:
        error("One filename required.")
    
    return args[0]


def usage():
    print("mma-splitrec, (c) Bob van der Poel")
    print("Create multi-track wav files from MMA.")
    print("Usage: mma-splitrec [opts] mmafile [opts]")
    print("Options:")
    for a in optmsg:
        print(a)
    print()
    sys.exit(1)


def isint(i):
    """ See if passed STRING is an integer. """

    try:
        int(i)
        return True
    except:
        return False


def error(m, e=None):
    print("Error - mma-splitrec: %s" % m)
    if e:
        print("       ", e)
    sys.exit(1)


def mid2wav(trackname, midifile):
    """ Play the midi file and record to wav. 

        This uses arecord as a background process to record
        and aplaymidi in the foreground to play the midi file.
    """

    print("Creating: %s.wav" % trackname)

    # start recording

    cmd = [recorder ] + recordopts.split() + ["%s.wav" % trackname]
    print(cmd)
    try:
        recpid = subprocess.Popen(cmd, shell=False)
    except OSError as e:
        error("Can't fork recorder.", e)

    # start playing midi

    cmd = [midiplayer] + midiopts.split() + [ midifile ]

    try:
        midpid = subprocess.Popen(cmd, shell=False)
    except OSError as e:
        recpid.kill()  # stop recorder
        error("Can't fork midi player.", e)

    midpid.wait()       # wait for midi play to stop

    try:
        recpid.terminate()       # stop recorder
    except OSError as e:
        error("Can't stop recorder.", e)


def tim2wav(trackname, midifile):
    """ Use timidity to create wav file.  """

    print("Creating: %s.wav with timidity" % trackname)

    cmd = [timidity] + timopts.split() + [ "-o%s.wav" % trackname,  midifile ]
    
    try:
        midpid = subprocess.Popen(cmd, shell=False)
    except OSError as e:
        recpid.kill()  # stop recorder
        error("Can't fork midi player.", e)

    midpid.wait()       # wait for midi play to stop


def makemidi(infile, outfile, opts):
    """ Create a midifile using mma. """

    cmd = [ MMA, '-0', infile]
    if outfile:
        cmd.extend(['-f', outfile])
    cmd.extend(opts)

    try:
        pid = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)
    except OSError as e:
        error("Can't fork mma.", e)

    data, err = pid.communicate()
    retcode = pid.returncode

    return (data, err, retcode)


#############################
#### Main line program  #####

mmafile = opts()

if mmafile.endswith(".mma"):
    basemid = mmafile[:-4]
else:
    basemid = mmafile

basemid += ".mid"


# Create the background midi and wav. 

if createbg:
    data, err, retcode = makemidi(mmafile, basemid, ["-0"])
    if usetimidity:
        tim2wav(bgtrack, basemid)
    else:
        mid2wav(bgtrack, basemid)


# Before we can split out the tracks we need to know the names
# of the tracks in the file. Using the -c option in mma will
# give us a list of allocated tracks and channel assignments.
# We grab the names after the "Channel assignments:" and parse 
# out the track names.

txt, err, retcode = makemidi(mmafile, '', ['-c'])
if err or retcode:
    error("MMA error.", err)

txt = txt.split()
txt=txt[txt.index('assignments:')+1:]
tracklist=[]
for a in sorted(txt):
    if isint(a): continue
    if a in excludelist: continue
    if onlylist and a not in onlylist: continue
    tracklist.append(a)

print("MMA file '%s' being split to: " % mmafile, end=' ')
for a in tracklist:
    print(a, end=' ')
print()


# Now we have a list of tracks ... do the magic.
# For each track call mma to generate midi, check if
# data was created (some tracks will be empty) and play/rec.

for trackname in tracklist:
  
    trackname = trackname.title()
    txt, err, retcode = makemidi(mmafile, tmpmid, ['-T', trackname])
    
    if err or retcode:
        if txt.find("No data created") >= 0:
            print("NO DATA for '%s', skipping" % trackname)
            continue
        else:
            error("MMA parsing error.", e)

    if usetimidity:
        tim2wav(trackname, tmpmid)
    else:
        mid2wav(trackname, tmpmid)
    os.remove(tmpmid)   # delete midifile








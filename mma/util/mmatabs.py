#!/usr/bin/env python

# create tex files of the mma midi constants
# works with python 2 and 3

import sys, os

# quick and dirty ... just insert possible mma locations into
# sys.path. We're just interested in loading miditables.py and
# chordtable.py so we can get the constant data we need.

sys.path = ["/usr/local/share/mma/MMA", "/usr/share/mma/MMA", 
      "/home/bob/src/bv/mma/MMA/"] + sys.path

from miditables import *
from chordtable import chordlist

#########################
# Functions

def dodrums(order):
    """ Print LaTex table of drum names. """

    notenames = ['E\\flat', 'E', 'F', 'G\\flat', 'G', 'A\\flat',
                 'A', 'B\\flat', 'B', 'C', 'D\\flat', 'D'] * 5


    if order == "m":
        for a in sorted(drumNames.keys()):
            n = drumNames[a].replace('&', '\&')
            outfile.write("\\insline{%s} {%s$^{%s}$}\n" % (a, n,notenames[a-27]))

    else:
        for a in sorted(drumInx.keys()):
            v=drumInx[a]
            n=drumNames[v].replace('&', '\&')
            outfile.write( "\\insline{%s} {%s$^{%s}$}\n" % (n, v, notenames[v-27]))


def docrtls(order):
    """ Print LaTex table of MIDI controller names. """
   
    if order == "m":
        for a in sorted(ctrlNames.keys()):
            n = ctrlNames[a].replace('&', '\&')
            outfile.write("\\insline{%s} {%s}\n" % (a, n))

    else:
        for a in sorted(ctrlInx.keys()):
            v=ctrlInx[a]
            n=ctrlNames[v].replace('&', '\&')
            outfile.write( "\\insline{%s} {%s}\n" % (n, v))


def doinsts(order):
    """ Print LaTex table of instrument names. """

    if order == "m":
        for a in sorted(voiceNames.keys()):
            if a>127: continue  # we don't want "none" to appear
            n = voiceNames[a].replace('&', '\&')
            outfile.write("\\insline{%s} {%s}\n" % (a, n))

    else:
        #for a in sorted(voiceInx.keys()):
        #    print a, voiceInx[a]
            
        for a in sorted(voiceInx.keys()):
            if a == 'DISTORTONGUITAR': continue  # skip old sp. mistake
            v=voiceInx[a]
            if v>127: continue  # we don't want "none" to appear
            n=voiceNames[v].replace('&', '\&')
            a=a.replace('&', '\&')
            outfile.write( "\\insline{%s} {%s}\n" % (n, v))
            
def dochords():
    """ Print out a list of chord names and docs in LaTex. """

    for n in sorted(chordlist.keys()):
        nm=n.replace("#", '$\\sharp$')
        nm=nm.replace('b', '$\\flat$')
        nm=nm.replace(chr(176), '\\diminished')
        nm=nm.replace(chr(248), '\\halfdim')

        outfile.write( "\\insline{%s}{%s}\n" % (nm, chordlist[n][2]) )

def dodrumkits(order):
    """ Print a list of the known drumkits and values in LaTex. """
    
    for a in sorted(drumKits.keys()):
        v = drumKits[a]
        outfile.write( "\\insline{%s}{%s}\n" % (a, v))
        
###############################
# Main program

for a, f, o in ( ('m', docrtls, 'ctrlmidi.AUTO'),
                 ('a', docrtls, 'ctrlalpha.AUTO'),
                 ('m', dodrums, 'drumsmidi.AUTO'),
                 ('a', dodrums, 'drumsalpha.AUTO'),
                 ('m', doinsts, 'instmidi.AUTO'),
                 ('a', doinsts, 'instalpha.AUTO'),
                 ('a', dodrumkits, 'drumkits.AUTO')
                ):
                 
        outfile = open(o, 'w')
        f(a)
        outfile.close()

outfile = open("chordnames.AUTO", 'w')
dochords()
outfile.close()


# qtone.
# parse a solo note string and break it into 3 lines:
#   line 1 - western notes
#   line 2 - quarter tone flats
#   line 3 - quarter tone sharps

# We import the plugin utilities

from MMA import pluginUtils as pu

# and some other things we'll need

import MMA.alloc
import MMA.gbl
import re

# ###################################
# # Documentation and arguments     #
# ###################################

# Minimum MMA required version.
pu.setMinMMAVersion(15, 12)

# A short plugin description.
pu.setDescription("Separate quarter tone solo riff lines into 3 parts.")

# A short author line.
pu.setAuthor("Written by bvdp.")
pu.setTrackType("Solo")
pu.addArgument("valid riff data",     None,  "")
# helpful notes
pu.setPluginDoc("""QRiff ... convert a solo line into quarter tones.

This plugin will convert a solo riff line into 3 separate solo lines:
   Solo - the original track. It can be custom name like "Solo-Foo".
          Any quarter tone notes are replaced by rests.
   Solo-qFlat - the quarter tone flat notes.
   Solo-qSharp - the quarter tone sharp notes.

NOTE: Don't try to have chords in your riff line. It doesn't work!
      Use only single notes!!!!

To specify quarter tone flats and sharps use a single '%' or '*'.
""")


# ###################################
# # Entry points                    #
# ###################################

def printUsage():
    pu.printUsage()


# Convert a line like:
#  qtone            4c+;c+**;8b;a%;b;c+;
# into
#  solo Riff        4c+;4r;8b;r;b;c+;
#  solo-qflat riff  4r;r;8r;a;r;;
#  solo-qsharp riff 4r;c+;8r;;;;


tuningSet = False

def setTuning(trk):
    global tuningSet, sTrack, fTrack

    fTrack = '%s-qFlat' % trk
    sTrack = '%s-qSharp' % trk

    if not tuningSet:
        
        if not fTrack.upper() in MMA.gbl.tnames:
            MMA.alloc.trackAlloc('%s' % fTrack, 0)
            pu.addCommand("%s Copy %s" % (fTrack, trk))

        if not sTrack.upper() in MMA.gbl.tnames:
            MMA.alloc.trackAlloc('%s' % sTrack, 0)
            pu.addCommand("%s Copy %s" % (sTrack, trk))

        pu.addCommand( '%s MidiNote PB 0 -2048' % fTrack)
        pu.addCommand( '%s MidiNote PB 0 2048' %  sTrack)
        pu.addCommand( 'After Bar=EOF %s MidiNote PB 0 0' % fTrack)
        pu.addCommand( 'After Bar=EOF %s MidiNote PB 0 0' % sTrack)
        pu.sendCommands()

        tuningSet = True

def note2rest(n):
    """ String out note information and replace with a single 'r' (rest) """
    return re.sub('[abcdefg\+\#\&-]+', 'r', n).replace('%', '').replace('*', '')


def trackRun(tr, line):
    """ Entry point for track command. """

    # We check if track type is correct.
    pu.checkTrackType(tr)
    
    # initalize tracks 2 and 3
    setTuning(tr)

    out1 = ["%s Riff  " % tr]
    out2 = ["%s Riff  " % fTrack]
    out3 = ["%s Riff  " % sTrack]

    line = ''.join(line)[:-1]

    for a in line.split(';'):
        if not ']' in a:
            attr, note = ('', a)
        else:
            attr, note = a.split(']', 1)

        # we now have just the note info to worry about. The stuff in []
        # is tucked away in 'attr'.

        if '%' in note:
            flatNote = attr + note.replace('%', '')
            normNote = attr + note2rest(note)
            sharpNote = attr + note2rest(note)

        elif '*' in note:
            sharpNote = attr + note.replace('*', '')
            normNote = attr + note2rest(note)
            flatNote = attr + note2rest(note)

        else:
            sharpNote = attr + note2rest(note)
            flatNote = attr + note2rest(note)
            normNote = attr + note


        out1.extend([normNote,  ';' ])
        out2.extend([flatNote,  ';' ])
        out3.extend([sharpNote, ';' ])


    pu.addCommand( ''.join(out1) )
    pu.addCommand( ''.join(out2) )
    pu.addCommand( ''.join(out3) )


    if MMA.debug.debug:
        print(''.join(out1));
        print(''.join(out2));
        print(''.join(out3));



    pu.sendCommands()

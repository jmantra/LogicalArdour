#!/usr/bin/env python

# Extract midi solos for including into mma scripts using MIDINote.
# Bob van der Poel, Jan/09

# You need to run this with python2. Probably will not get converted since
# the usage of this program is mostly replaced my the midiInc command in MMA.
# bvdp, Feb/2014.

import os, sys, math, time, getopt

# Some constants/globals

voiceNames=[
    'Piano1', 'Piano2','Piano3',
    'Honky-TonkPiano', 'RhodesPiano', 'EPiano',
    'HarpsiChord', 'Clavinet', 'Celesta',
    'Glockenspiel', 'MusicBox', 'Vibraphone',
    'Marimba', 'Xylophone', 'TubularBells', 'Santur',
    'Organ1', 'Organ2', 'Organ3', 'ChurchOrgan',
    'ReedOrgan', 'Accordion', 'Harmonica',
    'Bandoneon', 'NylonGuitar', 'SteelGuitar',
    'JazzGuitar', 'CleanGuitar', 'MutedGuitar',
    'OverDriveGuitar', 'DistortonGuitar',
    'GuitarHarmonics', 'AcousticBass',
    'FingeredBass', 'PickedBass', 'FretlessBass',
    'SlapBass1', 'SlapBass2', 'SynthBass1',
    'SynthBass2', 'Violin', 'Viola', 'Cello',
    'ContraBass', 'TremoloStrings',
    'PizzicatoString', 'OrchestralHarp', 'Timpani',
    'Strings', 'SlowStrings', 'SynthStrings1',
    'SynthStrings2', 'ChoirAahs', 'VoiceOohs',
    'SynthVox', 'OrchestraHit', 'Trumpet',
    'Trombone', 'Tuba', 'MutedTrumpet', 'FrenchHorn',
    'BrassSection', 'SynthBrass1', 'SynthBrass2',
    'SopranoSax', 'AltoSax', 'TenorSax',
    'BaritoneSax', 'Oboe', 'EnglishHorn', 'Bassoon',
    'Clarinet', 'Piccolo', 'Flute', 'Recorder',
    'PanFlute', 'BottleBlow', 'Shakuhachi',
    'Whistle', 'Ocarina', 'SquareWave', 'SawWave',
    'SynCalliope', 'ChifferLead', 'Charang',
    'SoloVoice', '5thSawWave', 'Bass&Lead',
    'Fantasia', 'WarmPad', 'PolySynth', 'SpaceVoice',
    'BowedGlass', 'MetalPad', 'HaloPad', 'SweepPad',
    'IceRain', 'SoundTrack', 'Crystal', 'Atmosphere',
    'Brightness', 'Goblins', 'EchoDrops',
    'StarTheme', 'Sitar', 'Banjo', 'Shamisen',
    'Koto', 'Kalimba', 'BagPipe', 'Fiddle', 'Shanai',
    'TinkleBell', 'AgogoBells', 'SteelDrums',
    'WoodBlock', 'TaikoDrum', 'MelodicTom1',
    'SynthDrum', 'ReverseCymbal', 'GuitarFretNoise',
    'BreathNoise', 'SeaShore', 'BirdTweet',
    'TelephoneRing', 'HelicopterBlade',
    'Applause/Noise', 'GunShot' ]

# Controller names. Tables are borrowed from:
#     http://www.midi.org/about-midi/table3.shtml

ctrlNames = {
    0:'Bank', 1:'Modulation', 2:'Breath',
    3:'Ctrl3', 4:'Foot', 5:'Portamento',
    6:'Data', 7:'Volume', 8:'Balance',
    9:'Ctrl9', 10:'Pan', 11:'Expression',
    12:'Effect1', 13:'Effect2', 14:'Ctrl14',
    15:'Ctrl15', 16:'General1', 17:'General2',
    18:'General3', 19:'General4', 20:'Ctrl20',
    21:'Ctrl21', 22:'Ctrl22', 23:'Ctrl23',
    24:'Ctrl24', 25:'Ctrl25', 26:'Ctrl26',
    27:'Ctrl27', 28:'Ctrl28', 29:'Ctrl29',
    30:'Ctrl30', 31:'Ctrl31', 32:'BankLSB',
    33:'ModulationLSB', 34:'BreathLSB', 35:'Ctrl35',
    36:'FootLSB', 37:'PortamentoLSB', 38:'DataLSB',
    39:'VolumeLSB', 40:'BalanceLSB', 41:'Ctrl41',
    42:'PanLSB', 43:'ExpressionLSB', 44:'Effect1LSB',
    45:'Effect2LSB', 46:'Ctrl46', 47:'Ctrl47',
    48:'General1LSB', 49:'General2LSB', 50:'General3LSB',
    51:'General4LSB', 52:'Ctrl52', 53:'Ctrl53',
    54:'Ctrl54', 55:'Ctrl55', 56:'Ctrl56',
    57:'Ctrl57', 58:'Ctrl58', 59:'Ctrl59',
    60:'Ctrl60', 61:'Ctrl61', 62:'Ctrl62',
    63:'Ctrl63', 64:'Sustain', 65:'Portamento',
    66:'Sostenuto', 67:'SoftPedal', 68:'Legato',
    69:'Hold2', 70:'Variation', 71:'Resonance',
    72:'ReleaseTime', 73:'AttackTime', 74:'Brightness',
    75:'DecayTime', 76:'VibratoRate', 77:'VibratoDepth',
    78:'VibratoDelay', 79:'Ctrl79', 80:'General5',
    81:'General6', 82:'General7', 83:'General8',
    84:'PortamentoCtrl', 85:'Ctrl85', 86:'Ctrl86',
    87:'Ctrl87', 88:'Ctrl88', 89:'Ctrl89',
    90:'Ctrl90', 91:'Reverb', 92:'Tremolo',
    93:'Chorus', 94:'Detune', 95:'Phaser',
    96:'DataInc', 97:'DataDec', 98:'NonRegLSB',
    99:'NonRegMSB', 100:'RegParLSB', 101:'RegParMSB',
    102:'Ctrl102', 103:'Ctrl103', 104:'Ctrl104',
    105:'Ctrl105', 106:'Ctrl106', 107:'Ctrl107',
    108:'Ctrl108', 109:'Ctrl109', 110:'Ctrl110',
    111:'Ctrl111', 112:'Ctrl112', 113:'Ctrl113',
    114:'Ctrl114', 115:'Ctrl115', 116:'Ctrl116',
    117:'Ctrl117', 118:'Ctrl118', 119:'Ctrl119',
    # pseudo controllers, also called channel mode messages
    120:'AllSoundsOff', 121:'ResetAll', 122:'LocalCtrl',
    123:'AllNotesOff', 124:'OmniOff', 125:'OmniOn',
    126:'PolyOff', 127:'PolyOn' }

# This is our midi file reader. Sucked out of ys2mma

class MF:

    def __init__(self, filename):

        """ The filename is assumed to be a valid midi file and is read and
            parsed. The events found are separated into channels and inserted
            into events{}. The stucture of events() is:
                 events[ch]     - a entry for each channel
                 events[ch][ev] - entry for each offset 

            we also create a few helpful variables:
                 voices[] - the last voice found for each channel, defaults to 0
                 metanames[] - set for ??/
                 tempo       - pulled out of header info

            NOTE: All events are read/parsed but only the limited set
                  needed are saved ... meta events, etc. are just dumped.
        """

        self.events        = {}
        self.voices        = [ 0 ] * 16   # last voice found for each track
        self.metanames     = []
        self.tempo         = 120          # default tempo if none found in file
 
        for c in range(0,16):   # create an empty entry for each possible channel
            self.events[c]=[]

        # read in file

        try:
            inpath = file(filename, "rb")
        except:
            error("Unable to open MIDI file %s for reading" % filename)

        self.midifile=inpath.read()
        inpath.close()
        self.offset = 0

        hd = self.chars(4) # Ensure this is valid header
        if hd != 'MThd':
            error("Expecting 'HThd', %s not a standard midi file." % filename)

        # the next chunk is a 32bit length (always 6), format (0 or 1),
        # number of tracks, beat division

        a = self.m32i() 
        if a != 6:
            error("Expecting a 32 bit value of 6 in header")

        format=self.m16i()
        if format not in (0,1):
            error("MIDI file format %s not recognized" % format)

        ntracks=self.m16i()
        self.beatDivision=self.m16i()

        # Finished the header, now we do each track

        for tr in range(ntracks):
            tm=0    # this is the offset pointer, incremented as we parse event times
            hdr = self.chars(4)
            if hdr != 'MTrk':
                error("Malformed MIDI file in track header")
            trlen = self.m32i()     # track length (we don't use it)

            lastevent = None

            """ Parse the midi file. We have to parse off each event, even
                though many will just be thrown away. You can't just skip around
                in a midi file :)
            """

            while 1:
                tm += self.mvarlen()        # adjust total offset by delta

                ev=self.m8b()               # command byte

                # if the command byte is < 0x80 then we are doing running status
                if ev < 0x80:
                    if not lastevent:
                        error("Illegal running status in %s at $%06x"  % (filename, self.offset))
                    self.offset -= 1
                    ev=lastevent

                sValue = ev>>4         # Shift MSBs to get a 4 bit value for the command
                channel = ev & 0x0f    # and the channel number (0..15)
                evptr = self.events[channel]

                if sValue == 0x8:           # note off event
                    evptr.append([tm, 'NoteOff', self.m8b(), self.m8b() ])

                elif sValue == 0x9:         # note on event
                    note=self.m8b()
                    vel=self.m8b()
                    # this needs to be conditional FIXME!
                    if vel == 0:
                        evptr.append([tm, 'NoteOff', note, vel])
                    else:
                        evptr.append([tm, 'NoteOn', note, vel])

                elif sValue == 0xa:         # key pressure
                    self.m8b()  # grab and ignore key pressure
                    self.m8b()

                elif sValue == 0xb:         # control change
                    evptr.append([tm, 'Controller', self.m8b(), self.m8b() ])
                    
                elif sValue == 0xc:         # program change
                    v = self.m8b()
                    evptr.append( [tm, 'ProgChange', v])
                    self.voices[channel] = v

                elif sValue == 0xd:         # channel pressure
                    evptr.append( [tm, 'ChannelPressure', self.m8b() ])

                elif sValue == 0xe:         # pitch blend
                    evptr.append([tm, 'PitchBend',  self.m8b()+(self.m8b()*128) ])

                elif sValue == 0xf:      # system events
                    if ev == 0xff:       # meta events
                        a=self.m8b()
                        stuff=self.chars(self.mvarlen())
 
                        if a == 0x2f: # end of track
                            evptr.append([tm, "EOT", stuff])
                            break
  
                        elif a == 0x58: # time sig
                            self.BperB = ord(stuff[0])
                            self.timedenom = 2 ** ord(stuff[1])

                        else:       # ignore anything else
                            pass

                    elif ev == 0xf0:    # system exclusive
                        self.offset += self.mvarlen()
 
                    elif ev == 0xf2:    # song position pointer, 2 bytes
                        self.offset += 2

                    elif ev == 0xf3:    # song select, 1 byte
                        self.offset += 1

                    else:       # all others are single byte commands
                        pass

                if ev >= 0x80 and ev <= 0xef:
                    lastevent = ev

        self.metanames.append( [tm, "EOF"])


    def mvarlen(self):
        """ Convert variable length midi value to int. """

        x=0L
        for i in range(4):

            try:
                byte=ord(self.midifile[self.offset])
                self.offset += 1
            except:
                error("Invalid MIDI file include (varlen->int).")

            if byte < 0x80:
                x = ( x << 7 ) + byte
                break
            else:
                x = ( x << 7 ) + ( byte & 0x7f )

        return int(x)

    # Class routines to grab bits of the midi

    def chars(self, count):
        """ Return 'count' chars from file (updates global pointer). """

        bytes=self.midifile[self.offset:self.offset+count]
        self.offset+=count
        return bytes


    def m8b(self):
        """ Get 1 byte/8 bit value (updates global pointer). """

        try:
            byte = self.midifile[self.offset]
            self.offset += 1
        except:
            error("Invalid MIDI file include (byte, offset=%s)." % self.offset)

        return ord(byte)


    def m32i(self):
        """ Get 4 byte/32 bit integer. """

        x = 0L
        for i in range(4):
            try:
                byte = self.midifile[self.offset]
                self.offset += 1
            except:
                error("Invalid MIDI file include (i32->int, offset=%s)." % self.offset)
            x = (x << 8) + ord(byte)

        return int(x)


    def m16i(self):
        """ Get 2 byte/16 bit integer. """

        x = 0L
        for i in range(2):
            try:
                byte = self.midifile[self.offset]
                self.offset += 1
            except:
                error("Invalid MIDI file include (i16->int, offset=%s)." % self.offset)
            x = (x << 8) + ord(byte)

        return int(x)


#####################################################
# Routines for errors, usage, etc.

def error(msg):
    print "ERROR: %s" % msg
    sys.exit(1)

def usage():
    print "mma-mnx.py - Extracts note events from MIDI files"
    print "             for future inclusion into MMA files"
    print "             using MidiNote (mnx==MidiNote eXtract)."
    print "usage: mma-mnx.py INFILE [options]"
    print "Options:"
    print "   -h this screen"
    print "   -v display version"
    print "   -c CHANNEL channel to extract data"

    sys.exit(1)

def showversion():
    print "0.1"
    sys.exit(0)

def doOpts():
    """ Parse off the command line options. """

    global channel, infile

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hvc:", [])
    except getopt.GetoptError:
        usage()
    for o, a in opts:

        if o == "-v":
            showversion()

        elif o == "-h":
            usage()

        elif o == "-c":
            channel = int(a)

        else:
            usage()

    if len(args) != 1:
        usage()

    infile = args[0]  


def chReport(mf):
    """ Report number of channels, events. """

    for a in range(0,16):
        if len(mf.events[a]):
            print "  Channel %02s  Total Events: %04s  Voice: %s" % \
                (a+1, len(mf.events[a]), voiceNames[mf.voices[a]])
    sys.exit(0)

def chDump(mf):
    """ Make up a list of recognized events for MMA midinote. """

    events = mf.events[channel-1]
    ons=[]
    quarters=mf.beatDivision  # beats per quarter note

    print "// Note data for %s. Offsets=Ticks  Duration=Ticks" % (infile)

    # Go though track and change all offsets to MMA's 192 BperQ

    if quarters != 192:
        print "// MIDI file tick/beat of %s differs from MMA's 192." \
           " Will try to compensate" % quarters

        adjust = 192. / quarters
        for i in xrange(len(events)):
            events[i][0] = int(events[i][0] * adjust)
        quarters = 192

    beatBar = mf.BperB * quarters   # beats per bar
    bprint=-1     # last bar number printed

    for i,a in enumerate(events):
        thisbar = int(a[0]/beatBar)

        # Determine current bar number

        if thisbar > bprint:
            print "// %s" % thisbar
            bprint=thisbar

        if a[1] == 'NoteOn':
            start=a[0]
            end=-1
            note=a[2]
            for aa in events[i:]:
                if aa[1]=='NoteOff' and aa[2]==note:
                    end=aa[0]
                    break
            if end == -1:
                end = start+1
            dur = end-start

            print "Note %d %d %d %d" % (a[0], note, a[3], dur )

        elif a[1] == 'PitchBend':   # pitch bend
            # NOTE, we subtract 8191 from the real value to keep
            # our values -8191 to +8192.
            print "PB %s %d " % (a[0], a[2]-8191)

        elif a[1] == 'ChannelPressure':   # channel aftertouch
            print "CHaT %s %s" % (a[0], a[2])

        elif a[1] == 'Controller':   # controller
            print "Ctrl %s %s %s" % (a[0], ctrlNames[a[2]], a[3])



########################################################
######  Start of mainline code.


channel = 0     # midi channel to extract 1..16
infile = ''     # name of the midi file

doOpts()        # get command line options/filename

mididata=MF(infile)

if not mididata.BperB:
    error("Expecting file to have valid time signature.")

if channel == 0:
    chReport(mididata)
else:
    chDump(mididata)

# eof

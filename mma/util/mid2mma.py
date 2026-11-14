#!/usr/bin/env python

# Read a SMF and convert it into mma patterns
# Bob van der Poel, July/09

# much of this is converted from ys2mma

# CAUTION: Ugly code ahead ... but it seems to work :)

import os, sys, math, time, getopt

# Ugly globals ...

outfile = None
quantz = 0

class struct:
    pass

# Conversions ...

drumNames=[
    'HighQ', 'Slap', 'ScratchPush', 'ScratchPull',
    'Sticks', 'SquareClick', 'MetronomeClick',
    'MetronomeBell', 'KickDrum2', 'KickDrum1',
    'SideKick', 'SnareDrum1', 'HandClap',
    'SnareDrum2', 'LowTom2', 'ClosedHiHat',
    'LowTom1', 'PedalHiHat', 'MidTom2', 'OpenHiHat',
    'MidTom1', 'HighTom2', 'CrashCymbal1',
    'HighTom1', 'RideCymbal1', 'ChineseCymbal',
    'RideBell', 'Tambourine', 'SplashCymbal',
    'CowBell', 'CrashCymbal2', 'VibraSlap',
    'RideCymbal2', 'HighBongo', 'LowBongo',
    'MuteHighConga', 'OpenHighConga', 'LowConga',
    'HighTimbale', 'LowTimbale', 'HighAgogo',
    'LowAgogo', 'Cabasa', 'Maracas',
    'ShortHiWhistle', 'LongLowWhistle', 'ShortGuiro',
    'LongGuiro', 'Claves', 'HighWoodBlock',
    'LowWoodBlock', 'MuteCuica', 'OpenCuica',
    'MuteTriangle', 'OpenTriangle', 'Shaker',
    'JingleBell', 'Castanets', 'MuteSudro',
    'OpenSudro' ]


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

# Table of bass conversions. These map a MIDI 'C' (value==0) to
# a MMA bass offset.

bassconvt = { 0:'1',    1:'1#',    2:'2',    3:'2#',   4:'3',
              5:'4',    6:'4#',    7:'5',    8:'5#',   9:'6',
             10:'6#',  11:'7',    -1:'7-',  -2:'6#-', -3:'6-',
             -4:'5#-', -5:'5',    -6:'4#-', -7:'4-',  -8:'3-',
             -9:'2#-',-10:'2-',  -11:'1#-' }

# Table of note length conversions. This is a list of tuples.
# Each tuple has: Note Length (string)
#         Min duration in ticks
#         Max duration in ticks
# Note that the tick length is for MMA standard 192 ticks/quarter
# user will need to modify HIS ticks to this.
# Order is shortest ot longest. It may be appropriate to insert move values?

notelens = [ ( '0'   ,  1      ),
             ( '32'  ,  192 * .125 ),
             ( '16'  ,  192 * .25  ),
             ( '8'   ,  192 * .5   ),
             ( '8.'  ,  192 * .75  ),
             ( '4'   ,  192    ),
             ( '4.'  ,  192 * 1.5  ),
             ( '2.'  ,  192 * 3    ),
             ( '1'   ,  192 * 4    ),
             ( 'LONG',  99999      ) ]


def vol2vol(vol):
    """ Convert a velocity to a MMA volume (average)."""

    vol = vol/127.0

    for a, b in (('FFFF', 2.00 ), ('FFF', 1.80), ('FF', 1.60),
                 ('F', 1.30), ('MF', 1.10), ('M', 1.00),
                 ('MP', 0.70), ('P', 0.40), ('PP', 0.25),
                 ('PPP', 0.10), ('PPPP', 0.05) ):

        if vol >= b :
            return a


def dur2len(duration):
    """ Convert midi tick value to MMA not length. """

    bot=0
    for i in range(len(notelens)-1):
        a=notelens[i][1]
        b=notelens[i+1][1]
        max = a+((b-a)/2)   # determine 1/2 point between values
        if duration < max:
            return notelens[i][0]

    return "XXX"


def fixname(n):
    """ Convert a yamaha style name like "Fill In A" to a MMA form."""

    n=n.replace(" In", "")
    n=n.replace(" ", "-")

    return n

###################################

def ofile(msg):
    if not outfile:
        print msg
    else:
        outfile.write(msg + "\n")

#####################################

def svalue(a):
    """ Return a value as a string with trailing 0's deleted.

        Don't use "%f conversions since
        this will convert values like 4.999 to 5.00!
    """

    a=str(a)
    try:
        a,b = a.split('.')
    except:
        b='0'
    b=b[:2]
    b=b.rstrip('0')
    if b:
        a = a+ '.' + b

    return a


########################################

# This is our midi file reader. Implemented as a class (at least we do some things right)

class MF:

    def __init__(self, filename):

        self.events = {}
        self.voices = [ 0 ] * 16   # last voice found for each track
        self.metanames = []
        self.volumeAdjusts = [127] * 16
        self.tempo = 120           # default tempo if none found in file
        self.midifile = ''         # The imported MIDI file (data) as a long string

        for c in range(0,16):
            self.events[c]=[]

        # read in file

        try:
            inpath = file(filename, "rb")
        except:
            error("Unable to open MIDI file %s for reading" % filename)

        self.midifile=inpath.read()
        inpath.close()

        # Ensure this is valid header

        hd = self.midifile[0:4]
        if hd != 'MThd':
            error("Expecting 'HThd', %s not a standard midi file." % filename)

        self.offset = 4
        a = self.m32i()

        if a != 6:
            error("Expecting a 32 bit value of 6 in header")

        format=self.m16i()

        if format not in (0,1):
            error("MIDI file format %s not recognized" % format)

        ntracks=self.m16i()
        self.beatDivision=self.m16i()

        for tr in range(ntracks):
            tm=0

            hdr = self.midifile[self.offset:self.offset+4]
            self.offset+=4

            if hdr != 'MTrk':
                error("Malformed MIDI file in track header")
            trlen = self.m32i()     # track length, not used?

            lastevent = None

            """ Parse the midi file. We have to parse off each event, even
                though many will just be thrown away. You can't just skip around
                in a midi file :)
            """

            while 1:

                tm += self.mvarlen()        # adjust total offset by delta

                ev=self.m1i()

                if ev < 0x80:
                    if not lastevent:
                        error("Illegal running status in %s at $%06x" \
                            % (filename, self.offset))
                    self.offset -= 1
                    ev=lastevent


                sValue = ev>>4      # Shift MSBs to get a 4 bit value
                channel = ev & 0x0f

                if sValue == 0x8:           # note off event
                    note=self.m1i()
                    vel=self.m1i()
                    self.events[ev & 0xf].append([tm, ev & 0xf0, chr(note)+chr(vel)])

                elif sValue == 0x9:         # note on event
                    note=self.m1i()
                    vel=self.m1i()
                    self.events[ev & 0xf].append([tm, ev & 0xf0, chr(note)+chr(vel)])

                elif sValue == 0xa:         # key pressure
                    chars(2)
                    #events[ev & 0xf].append([tm, ev & 0xf0, self.chars(2)])

                elif sValue == 0xb:         # control change
                    ctrl=ord(self.chars(1))
                    parm=ord(self.chars(1))
                    if ctrl==0x07:
                        self.volumeAdjusts[channel]=parm

                elif sValue == 0xc:         # program change
                    v = self.chars(1)
                    self.events[ev & 0xf].append([tm, ev & 0xf0, v])
                    self.voices[ev & 0xf] = ord(v)

                elif sValue == 0xd:         # channel pressure
                    self.chars(1)
                    #events[ev & 0xf].append([tm, ev & 0xf0, chars(1)])

                elif sValue == 0xe:         # pitch blend
                    self.chars(2)
                    #events[ev & 0xf].append([tm, ev & 0xf0, chars(2)])

                elif sValue == 0xf:         # system, mostly ignored
                    if ev == 0xff:      # meta events
                        a=self.m1i()
                        if a == 0x00:   # sequence number
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x01: # text (could be lyrics)
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x02: # copyright
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x03: # seq/track name
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x04: # instrument name
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x05: # lyric
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x06: # marker
                            self.metanames.append([tm, self.chars(self.mvarlen())])

                        elif a == 0x07: # cue point
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x21: # midi port
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x2f: # end of track
                            l=self.mvarlen()
                            self.offset += l
                            break

                        elif a == 0x51:     #tempo
                            x=0l
                            for b in self.chars(self.mvarlen()):
                                x = (x << 8) + ord(b)
                            self.tempo = 60000000/x

                        elif a == 0x54: # SMPTE offset
                            l=self.mvarlen()
                            self.offset += l

                        elif a == 0x58: # time sig
                            l=self.mvarlen()
                            self.BperB = ord(self.midifile[self.offset])
                            self.timedenom = 2 ** ord(self.midifile[self.offset+1])
                            self.offset += l

                        elif a == 0x59: # key sig
                            l=self.mvarlen()
                            self.offset += l

                        else:       # probably 0x7f, proprietary event
                            l=self.mvarlen()
                            self.offset += l


                    elif ev == 0xf0:    # system exclusive
                        l=self.mvarlen()
                        self.offset += l

                    elif ev == 0xf2:    # song position pointer, 2 bytes
                        self.offset += 2

                    elif ev == 0xf3:    # song select, 1 byte
                        self.offset += 1

                    else:       # all others are single byte commands
                        pass

                if ev >= 0x80 and ev <= 0xef:
                    lastevent = ev

        self.metanames.append( [tm, "EOF"])
        self.lastTime = tm

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


    def chars(self, count):
        """ Return 'count' chars from file (updates global pointer). """

        bytes=self.midifile[self.offset:self.offset+count]
        self.offset+=count
        return bytes


    def m1i(self):
        """ Get 1 byte (updates global pointer). """

        try:
            byte = self.midifile[self.offset]
            self.offset += 1
        except:
            error("Invalid MIDI file include (byte, offset=%s)." % self.offset)

        return ord(byte)


    def m32i(self):
        """ Convert 4 bytes to integer. """

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
        """ Convert 2 bytes to integer. """

        x = 0L
        for i in range(2):
            try:
                byte = self.midifile[self.offset]
                self.offset += 1
            except:
                error("Invalid MIDI file include (i16->int, offset=%s)." % self.offset)
            x = (x << 8) + ord(byte)

        return int(x)


############################################

def error(msg):
    print "ERROR: %s" % msg
    sys.exit(1)

################################################

def countevents(events, start, end):
    """ Count the number of note on events in track. """

    el={}

    for ev in events:
        delta=ev[0]

        if delta < start or delta > end:
            continue

        if ev[1] == 0x90 and ord(ev[2][1]):    # only track note-on events
            if el.has_key(delta):
                el[delta] += 1
            else:
                el[delta] = 0

    ecount = len(el)

    mcount = 0
    for e in el:
        if el[e]:
            mcount +=1

    """ The return values are:
          ecount - the number of event TIMEs with note-on events
          mcount - the number of of ecount events with multiple on-events (chords?)
    """

    return (ecount, mcount)

####################################################
########  Process/create the different tracks ######

def printseq(l):
    """ Convert list of defs and print. """

    s = " Sequence  "
    for t in l:
        if t == '':
            t = ' z '
        else:
            t=t.strip()
            t=t.strip(';')
            t = "{" + t + " }"
        s += t

    s=s.replace("}{", "} \\\n       {")
    #s=s.replace("z",  " z \\\n        ")
    ofile(s)


def parse_evs(events, sec, channel):

    voice = None
    nl=[]  # list of notes: [note pitch, velocity, on time, duration]

    for ev in events:
        delta = ev[0]

        if delta >= sec.start and delta <= sec.end:
            if ev[1] == 0xc0:
                voice = ord(ev[2])

            if ev[1] == 0x90 or ev[1]== 0x80:
                pitch    = ord(ev[2][0])
                velocity = ord(ev[2][1])

                if ev[1] == 0x80:  # convert NoteOff to NoteOn, Vel=0
                    velocity = 0

                if velocity and delta < sec.end:   # must be IN section
                    c=struct()
                    c.pitch=pitch
                    c.velocity=velocity
                    c.start=delta
                    c.dur=None
                    nl.append(c)

                """ Turn off a note. Step though the list and turn off
                    any pitches found. NOTE: You can have a note set on
                    multiple times and have only 1 off event .. so do everything!
                """

                if not velocity:
                    for n in nl:
                        if n.pitch == pitch and n.dur == None:
                            n.dur = delta - n.start

    # delete any entries without OFF time  ????

    for n in range(len(nl)-1, -1, -1):
        if nl[n].dur == None:
            print "Warning: Fixing event without OFF Ch=%s, pitch=%s offset=%s" %  \
                (channel+1, nl[n].pitch,nl[n].start)
            nl[n].dur = sec.end

    # Determine the average velocity for this segment.

    a=0
    c=0
    for n in nl:
        a+=n.velocity
        c+=1


    return (nl, voice)


def dodrums(name, sec, events, channel, defvoice, voladj):
    """ Create a drum entry. """

    notes={}
    for a in range(0,128):
        notes[a]=[]

    totalvol = 0
    totalnotes = 0
    for ev in sorted(events):       # just grab note-ON events

        delta = ev[0]
        if delta >= sec.start and delta < sec.end and ev[1] == 0x90:
            pitch = ord(ev[2][0])
            vel = ord(ev[2][1])

            if pitch:
                if quantz:
                    delta = int(delta/quantz)*quantz
                notes[pitch].append( [delta-sec.start, vel])
                totalvol += vel
                totalnotes += 1


    for a in sorted(notes):
        if notes[a]:
            if  a<27 or a>86:
                k=str(a)
            else:
                k=drumNames[a-27]

            ofile( "Begin Drum-%s" % k)
            ofile( " Tone %s" % k )    # might to a table lookup here for english name
            ofile( " Rvolume 0")
            ofile( " Rtime 0")
            ofile( " Articulate 100")
            ofile( " Volume %s" % vol2vol(voladj) )

            l = [ ]

            for i in range(sec.bars):
                l.append("")

            for t,v in notes[a]:
                off = t/sec.TperB
                if off<0:
                    off=0
                i = 0
                while off >= sec.BperB:
                    off -= sec.BperB
                    i += 1
                if i >=len(l):
                    ofile( "/// LOST EVENT offset=%s " % (sec.start+t))
                else:
                    l[i]+= "%s 0 %s; " % (svalue(off+1), v)

            printseq(l)
            ofile( "End\n")


def dochord(name, sec, events, channel, defvoice, voladj):
    """ Create a chord entry. """

    nl, voice = parse_evs(events, sec, channel)

    if voice == None:
        voice = defvoice

    pa = 0
    pac = 0
    for n in nl:
        pa += n.pitch
        pac += 1
    octave = pa/pac/12


    ofile( "Begin Chord-%s" % name )
    ofile( " Voice %s" % voiceNames[voice] )
    ofile( " Rvolume 0")
    ofile( " Rtime 0")
    ofile( " Volume %s" % vol2vol(voladj) )
    ofile( " Voicing Mode=Optimal")
    ofile( " Articulate 100")
    ofile( " Octave %s" % octave )

    if quantz:
        for n in nl:
            n.start = int(n.start/quantz)*quantz

    # Delete duplicate starts

    newnl = []

    for n in nl:
        delta = n.start
        ex = 0
        for i in newnl:
            if i.start == delta:
                ex = 1
                i.velocity += n.velocity
                i.count += 1
        if not ex:
            n.count = 1
            newnl.append(n)
    nl = newnl

    # split the list into bars

    l = [ ]
    for i in range(sec.bars):
        l.append("")

    for n in  nl:
        off = (n.start-sec.start)/sec.TperB
        if off<0:
            off = 0
        i = 0
        while off >= sec.BperB:
            off -= sec.BperB
            i += 1
        if i >=len(l):
            ofile( "/// LOST EVENT offset=%s " % n.start )
        else:
            l[i]+= "%s %s %s; " % (svalue(off+1),  dur2len((192 * n.dur)/sec.TperB),
              n.velocity/n.count)

    printseq(l)

    ofile( "End\n")


def dobass(name, sec, events, channel, defvoice, voladj):
    """ Create a bass entry. """

    nl, voice = parse_evs(events, sec, channel)

    if voice == None:
        voice = defvoice

    pa = 0
    pac = 0
    for n in nl:
        pa += n.pitch
        pac += 1
    octave = pa/pac/12


    # convert pitches to constants offset from 'C'
    # and durations to note-lens

    for n in nl:
        note=n.pitch
        while note >= 11:
            note -= 12
        n.pitch = bassconvt[note]
        if quantz:
            n.start = int(n.start/quantz)*quantz
        n.dur = dur2len( (192 * n.dur) / sec.TperB)

    # Print mma header for this section

    ofile( "Begin Bass-%s" % name )
    ofile( " Voice %s" % voiceNames[voice] )
    ofile( " Rvolume 0")
    ofile( " Rtime 0")
    ofile( " Volume %s" % vol2vol(voladj) )
    ofile( " Octave %s" % octave)

    # split the list into bars

    l = [ ]
    for i in range(sec.bars):
        l.append("")

    for n in nl:
        off = (n.start-sec.start)/sec.TperB
        if off<0:
            off=0
        i = 0
        while off >= sec.BperB:
            off -= sec.BperB
            i += 1
        if i >=len(l):
            ofile( "/// LOST EVENT offset=%s " % n.start )
        else:
            l[i]+= "%s %s %s %s; " % (svalue(off+1), n.dur, n.pitch, n.velocity)

    printseq(l)
    ofile( "End\n")

def usage():
    print "mid2mma.py - converts track(s) from SMF to MMA"
    print "usage: mid2mma.py INFILE [OUTFILE] [options]"
    print "Options:"
    print "   -h this screen"
    print "   -q N set quantization to N (default == 0)"
    print "      use note subscript (8==1/8s, 4=1/4, etc)"
    print "   -t don't generate test code (default=on)"
    print "   -a N use auto track select, N == ratio"
    print "   -v display version"

    sys.exit(1)

def showversion():
    print "0.0"
    sys.exit(0)

########################################################
######  Start of mainline code.

""" Parse off command line options:
        -h or -? - show usage screen
        -v       - display version
        -a       - enable auto chord/bass select
        -q       - set quantization
        -t       - no test code
"""

autoratio = None
dotest = 1

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hq:a:vt", [])
except getopt.GetoptError:
    usage()
for o, a in opts:

    if o == "-v":
        showversion()

    elif o == "-q":
        try:
            quantz = int(a)
        except:
            error("Expecting integer for -q argument")

    elif o == '-a':

        try:
            autoratio = int(a)
        except:
            error("Expecting integer for -a argument")

    elif o == '-t':
        dotest = None

    else:
        usage()

if len(args) not in (1,2):
    usage()

infile = args[0]

if len(args) == 2:
    outname = args[1]
else:
    outname = infile
    if outname.split('.')[-1].lower() in ("mid", "sty"):
        outname = outname[:-4]
    outname += '.mma'
    outname = outname.replace(" ", "")
    outname = outname.lower()

mididata=MF(infile)

if not mididata.BperB:
    error("Expecting file to have valid time signature.")

### Do a summary of what we know 

print "Summary for '%s' (Channels are labeled 1..x)" % infile
print "Tempo:", mididata.tempo
print "TimeSig: %s/%s" % (mididata.BperB, mididata.timedenom)
totalBeats = mididata.lastTime/mididata.beatDivision
totalBars = totalBeats/mididata.BperB
print "Number of Beats=%s, Bars=%s." % (totalBeats, totalBars)

for a in mididata.metanames:
    if a[1] == "EOF":
        continue
    print fixname(a[1]),
print
validTracks = []
for a in range(0,16):
    if len(mididata.events[a]):
        print "  Channel %02s  Total Events: %04s  Voice: %s" % \
            (a+1, len(mididata.events[a]), voiceNames[mididata.voices[a]])
    validTracks.append(a)

while(1):
    print "Enter bar range for extraction: ",
    barRange = sys.stdin.readline()
    barRange=barRange.replace(',', ' ')
    barRange=barRange.split()
    if len(barRange) != 2:
        print "Enter range as 'Start [,] End'. You must use 2 values."
    elif barRange[0] >= barRange[1]:
        print "Range 1 must be less than range 2."
    else:
        break

while(1):
    print "Enter value of MIDI track to extract: ",
    suckTrack = sys.stdin.readline()
    try:
        suckTrack = int(suckTrack)
    except:
        print "Please enter an integer value.";
        continue

    suckTrack -= 1
    if suckTrack not in validTracks:
        print "Track '%s' not in this song." % suckTrack
    else:
        break

print suckTrack

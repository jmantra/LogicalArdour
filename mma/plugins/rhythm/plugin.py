# We import the plugin utilities
from MMA import pluginUtils as pu
from MMA import parse
from MMA import macro
import re

# A short plugin description.
pu.setDescription("Define percussion grooves.")

author = "Johan Vromans"
# A short author line.
pu.setAuthor("Written by {}".format(author))

pu.setTrackType('DRUM')

pu.setSynopsis("""
    @rhythm Groove, Seq, Bpm, Level, RTime, RVolume, Clear, SeqSize, Debug
  or
    Track @rhythm Seq, Bpm, Level, Debug
  or
    Track @rhythm Define=Pat, Seq, Bpm, Level, Debug

""")

# These are the arguments for the full (non-track) call.
# Track usage is a subset.
# Note that pu.printUsage requires the default values to be strings. 
pu.addArgument( "Groove", None,   "Groove to define." )
pu.addArgument( "Seq",    None,   "Sequence tab."     )
pu.addArgument( "Bpm",    '4',    "Beats per bar."    )
pu.addArgument( "Level",  '9',    "Max volume value." )
pu.addArgument( "RTime",  '0',    "Time randomizer."  )
pu.addArgument( "RVolume",'0',    "Volume randomizer.")
pu.addArgument( "Clear",  '0',    "Issue SeqClear."   )
pu.addArgument( "SeqSize",'0',    "Issue SeqSize."    )
pu.addArgument( "Debug",  '0',    "For debugging."    )

# We add a small doc. %NAME% is replaced by plugin name.
pu.setPluginDoc("""
This plugin creates percussion patterns using ASCII tabs.

See https://github.com/sciurius/mma-plugins/blob/master/rhythm/README.md for extensive documentation.

This plugin has been written by Johan Vromans <jvromans@squirrel.nl>
Version 1.03.
""")

# ###################################
# # Entry points                    #
# ###################################

# This prints help when MMA is called with -I switch.
def printUsage():
    pu.printUsage()

# Entry point for groove defining.
def run(line):

    args = pu.parseCommandLine(line)

    # Mandatory.
    groove = args["Groove"]
    seq    = args["Seq"]

    # Optional.
    bpm    = int(args["Bpm"])
    level  = int(args["Level"])
    rvol   = int(args["RVolume"])
    rtime  = int(args["RTime"])
    seqsz  = int(args["SeqSize"])
    clear  = int(args["Clear"])
    debug  = int(args["Debug"])

    # Some checks.
    if level < 1 or level > 9:
        raise Exception( "Rhtythm: Level must be 1 .. 9, not {}".format(level))

    if clear: pu.addCommand("SeqClear")
    if seqsz: pu.addCommand("SeqSize {}".format(seqsz))

    # The sequence data is a series of Instrument Pattern pairs.
    # It may be passed in a macro name.
    line = seq.split()
    if len(line) == 1:
        # Macro name.
        line = pu.getVar(seq.upper())
        # MSet macro return list of list. Flatten.
        if len(line) > 0 and isinstance(line[0], list):
            line = [item for sublist in line for item in sublist]
        else:
            # Single value macro. Split.
            line = line.split()

    if len(line) % 2:
        raise Exception("Rhythm: Seq must have an even number of whitespace separated items")

    # Process two at a time.
    while len(line) > 1:

        # Pop off instrument name.
        instr = line.pop(0)
        if re.match( r'^[0-9]+$', instr ):
            # If it is a number, use the Zoom predefined names.
            tone = zoomTones[int(instr)-1]
            instr = zoomNames[int(instr)-1]
        elif instr in zoomNames:
            i = zoomNames.index(instr)
            tone = zoomTones[i]
        else:
            tone = instr

        # Pop off the sequence data.
        seq   = line.pop(0)

        pu.addCommand("Begin Drum-" + instr)
        pu.addCommand("  Tone     " + tone)
        if rtime: pu.addCommand("  RTime    {:d}".format(rtime))
        if rvol:  pu.addCommand("  RVolume  {:d}".format(rvol))
        pu.addCommand("  Sequence " + process_sequence( seq, bpm, level ))
        pu.addCommand("End")

    pu.addCommand("DefGroove " + groove)
    # if debug: print(pu._P().COMMANDS)
    pu.sendCommands()

# Entry point for track plugin.
# The track plugin takes a subset of arguments.
def trackRun( track, line ):
    pu._P().ARGUMENTS = [];
    pu.addArgument( "Seq",   None, "Sequence tab."     )
    pu.addArgument( "Define", "",    "For defining."    )
    pu.addArgument( "Bpm",   "4",    "Beats per bar."    )
    pu.addArgument( "Level", "9",    "Max volume value." )
    pu.addArgument( "Debug", "0",    "For debugging."    )
    args = pu.parseCommandLine(line)

    seq = args["Seq"]
    bpm = int(args["Bpm"])
    vol = int(args["Level"])
    debug = int(args["Debug"])
    define = args["Define"]
    
    if define == "":
        cmd = "Sequence " + process_sequence( seq, bpm, vol )
    else:
        cmd = process_sequence( seq, bpm, vol )
        cmd = "Define " + define + " " + cmd[2:-2]

    # Hackattack...
    # If we're called from a Begin Drum-Foo then we should not include
    # the track in the resultant command.
    beginData = parse.beginData
    if beginData and beginData[0].upper() == track:
        1
    else:
        cmd = track + " " + cmd

    if debug: print("Rhythm: " + cmd)
    pu.addCommand(cmd)
    # if debug: print(pu._P().COMMANDS)
    pu.sendCommands()

# Produces an MMA sequence string from an ASCII tab.
def process_sequence( tab, bpm=4, vol=9  ):

    # Volume scale. Scale 1..9 -> 10..90
    vscale = 90/vol;

    # Just in case we're quoted.
    if tab[ 0] in "\"'": tab = tab[1:]
    if tab[-1] in "\"'": tab = tab[:-1]

    # Check validity.
    if len(tab) < 3 or tab[0] != '|' or tab[-1] != '|':
        raise Exception( "Invalid tab: {}".format(tab) )

    prev = ""
    res = ""

    m = re.finditer( r'([-0-9*]*)\|', tab[1:] )
    if m == None:
        raise Exception( "Not well-formed tab: {}".format(tab) )

    # Process the bars
    for x in m:
        bar = x.group(1)
        step = len(bar)
        if step == 0:
            # Empty bar: repeat previous.
            # If first: silent bar.
            if res != "":
                res = res + '/ '
            else:
                res = 'Z'
            continue

        # Single arsterisk copies existing sequence.
        if step == 1 and bar == '*':
            res = res + '* '
            continue

        seqs = []
        for index, char in enumerate(bar):
            if char == '-':
                continue
            t = "{:f}".format( 1 + index * bpm / step)
            # Strip unneeded trailing zeroes and decimal point.
            t = re.sub(r'\.?0+$', '', t)
            # Append.
            seqs.append( "{} 0 {:d}".format( t,
                                             round(int(char)*vscale)))

        if len(seqs) == 0:
            # Silent sequence.
            seq = "Z "
        else:
            # Combine.
            seq = "{ " + "; ".join(seqs) + " } "

        # Check for copies.
        if prev == seq:
            res = res + "/ "
        else:
            res = res + seq
            prev = seq

    return res

# Instrument names as used by Zoom percussion devices.
zoomNames = [
    "Kick",       "Snare",    "ClosedHat",  "OpenHat",
    "Crash",      "Ride",     "Tom1",       "Tom2",
    "Tom3",       "Stick",    "Bell",       "Maracas",
    "Tambourine", "LowConga", "MutHiConga", "OpenHiConga" ]

# Corresponding MMA percussion tones.
zoomTones = [
    "KickDrum1",    "SnareDrum1",  "ClosedHiHat",   "OpenHiHat",
    "CrashCymbal1", "RideCymbal1", "MidTom1",       "LowTom1",
    "HighTom1",     "SideKick",    "RideBell",      "Maracas",
    "Tambourine",   "LowConga",    "MuteHighConga", "OpenHighConga" ]

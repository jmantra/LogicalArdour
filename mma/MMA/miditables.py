
# miditables.py

"""
This module is an integeral part of the program
MMA - Musical Midi Accompaniment.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

Bob van der Poel <bob@mellowood.ca>

This module contains the constant names for the various
MIDI controllers.

Having only the constants in this separate file permits to
call this from other programs, mainly the mma doc creators.

"""

# Create a NONE value for "do nothing" midi voicing. This is 127.127.127
NONETONE = (127 << 16) + (127 < 8) + 127

#  Standard GM drum tone  names.

drumNames = {
    27: 'HighQ', 28: 'Slap', 29: 'ScratchPush',
    30: 'ScratchPull', 31: 'Sticks', 32: 'SquareClick',
    33: 'MetronomeClick', 34: 'MetronomeBell', 35: 'KickDrum2',
    36: 'KickDrum1', 37: 'SideKick', 38: 'SnareDrum1',
    39: 'HandClap', 40: 'SnareDrum2', 41: 'LowTom2',
    42: 'ClosedHiHat', 43: 'LowTom1', 44: 'PedalHiHat',
    45: 'MidTom2', 46: 'OpenHiHat', 47: 'MidTom1',
    48: 'HighTom2', 49: 'CrashCymbal1', 50: 'HighTom1',
    51: 'RideCymbal1', 52: 'ChineseCymbal', 53: 'RideBell',
    54: 'Tambourine', 55: 'SplashCymbal', 56: 'CowBell',
    57: 'CrashCymbal2', 58: 'VibraSlap', 59: 'RideCymbal2',
    60: 'HighBongo', 61: 'LowBongo', 62: 'MuteHighConga',
    63: 'OpenHighConga', 64: 'LowConga', 65: 'HighTimbale',
    66: 'LowTimbale', 67: 'HighAgogo', 68: 'LowAgogo',
    69: 'Cabasa', 70: 'Maracas', 71: 'ShortHiWhistle',
    72: 'LongLowWhistle', 73: 'ShortGuiro', 74: 'LongGuiro',
    75: 'Claves', 76: 'HighWoodBlock', 77: 'LowWoodBlock',
    78: 'MuteCuica', 79: 'OpenCuica', 80: 'MuteTriangle',
    81: 'OpenTriangle', 82: 'Shaker', 83: 'JingleBell',
    84: 'Castanets', 85: 'MuteSurdo', 86: 'OpenSurdo'}

drumInx = dict((v.upper(), k) for (k, v) in drumNames.items())

# Standard GM voice names.

voiceNames = {
    0: 'Piano1', 1: 'Piano2', 2: 'Piano3',
    3: 'Honky-TonkPiano', 4: 'RhodesPiano', 5: 'EPiano',
    6: 'HarpsiChord', 7: 'Clavinet', 8: 'Celesta',
    9: 'Glockenspiel', 10: 'MusicBox', 11: 'Vibraphone',
    12: 'Marimba', 13: 'Xylophone', 14: 'TubularBells',
    15: 'Santur', 16: 'Organ1', 17: 'Organ2',
    18: 'Organ3', 19: 'ChurchOrgan', 20: 'ReedOrgan',
    21: 'Accordion', 22: 'Harmonica', 23: 'Bandoneon',
    24: 'NylonGuitar', 25: 'SteelGuitar', 26: 'JazzGuitar',
    27: 'CleanGuitar', 28: 'MutedGuitar', 29: 'OverDriveGuitar',
    30: 'DistortionGuitar', 31: 'GuitarHarmonics', 32: 'AcousticBass',
    33: 'FingeredBass', 34: 'PickedBass', 35: 'FretlessBass',
    36: 'SlapBass1', 37: 'SlapBass2', 38: 'SynthBass1',
    39: 'SynthBass2', 40: 'Violin', 41: 'Viola',
    42: 'Cello', 43: 'ContraBass', 44: 'TremoloStrings',
    45: 'PizzicatoString', 46: 'OrchestralHarp', 47: 'Timpani',
    48: 'Strings', 49: 'SlowStrings', 50: 'SynthStrings1',
    51: 'SynthStrings2', 52: 'ChoirAahs', 53: 'VoiceOohs',
    54: 'SynthVox', 55: 'OrchestraHit', 56: 'Trumpet',
    57: 'Trombone', 58: 'Tuba', 59: 'MutedTrumpet',
    60: 'FrenchHorn', 61: 'BrassSection', 62: 'SynthBrass1',
    63: 'SynthBrass2', 64: 'SopranoSax', 65: 'AltoSax',
    66: 'TenorSax', 67: 'BaritoneSax', 68: 'Oboe',
    69: 'EnglishHorn', 70: 'Bassoon', 71: 'Clarinet',
    72: 'Piccolo', 73: 'Flute', 74: 'Recorder',
    75: 'PanFlute', 76: 'BottleBlow', 77: 'Shakuhachi',
    78: 'Whistle', 79: 'Ocarina', 80: 'SquareWave',
    81: 'SawWave', 82: 'SynCalliope', 83: 'ChifferLead',
    84: 'Charang', 85: 'SoloVoice', 86: '5thSawWave',
    87: 'Bass&Lead', 88: 'Fantasia', 89: 'WarmPad',
    90: 'PolySynth', 91: 'SpaceVoice', 92: 'BowedGlass',
    93: 'MetalPad', 94: 'HaloPad', 95: 'SweepPad',
    96: 'IceRain', 97: 'SoundTrack', 98: 'Crystal',
    99: 'Atmosphere', 100: 'Brightness', 101: 'Goblins',
    102: 'EchoDrops', 103: 'StarTheme', 104: 'Sitar',
    105: 'Banjo', 106: 'Shamisen', 107: 'Koto',
    108: 'Kalimba', 109: 'BagPipe', 110: 'Fiddle',
    111: 'Shanai', 112: 'TinkleBell', 113: 'AgogoBells',
    114: 'SteelDrums', 115: 'WoodBlock', 116: 'TaikoDrum',
    117: 'MelodicTom1', 118: 'SynthDrum', 119: 'ReverseCymbal',
    120: 'GuitarFretNoise', 121: 'BreathNoise', 122: 'SeaShore',
    123: 'BirdTweet', 124: 'TelephoneRing', 125: 'HelicopterBlade',
    126: 'Applause/Noise', 127: 'GunShot',
    NONETONE: 'None'}

voiceInx = dict((v.upper(), k) for (k, v) in voiceNames.items())
# fix an unfortunate spelling error.
voiceInx['DISTORTONGUITAR']=voiceInx['DISTORTIONGUITAR']

# Controller names. Tables are borrowed from:
#     http: //www.midi.org/about-midi/table3.shtml

#      0-31 Double Precise Controllers    MSB (14-bits, 16,384 values)
#      32-63  Double Precise Controllers  LSB (14-bits, 16,384 values)
#      64-119 Single Precise Controllers  (7-bits, 128 values)
#      120-127 Channel Mode Messages

ctrlNames = {
    0: 'Bank', 1: 'Modulation', 2: 'Breath',
    3: 'Ctrl3', 4: 'Foot', 5: 'Portamento',
    6: 'Data', 7: 'Volume', 8: 'Balance',
    9: 'Ctrl9', 10: 'Pan', 11: 'Expression',
    12: 'Effect1', 13: 'Effect2', 14: 'Ctrl14',
    15: 'Ctrl15', 16: 'General1', 17: 'General2',
    18: 'General3', 19: 'General4', 20: 'Ctrl20',
    21: 'Ctrl21', 22: 'Ctrl22', 23: 'Ctrl23',
    24: 'Ctrl24', 25: 'Ctrl25', 26: 'Ctrl26',
    27: 'Ctrl27', 28: 'Ctrl28', 29: 'Ctrl29',
    30: 'Ctrl30', 31: 'Ctrl31', 32: 'BankLSB',
    33: 'ModulationLSB', 34: 'BreathLSB', 35: 'Ctrl35',
    36: 'FootLSB', 37: 'PortamentoLSB', 38: 'DataLSB',
    39: 'VolumeLSB', 40: 'BalanceLSB', 41: 'Ctrl41',
    42: 'PanLSB', 43: 'ExpressionLSB', 44: 'Effect1LSB',
    45: 'Effect2LSB', 46: 'Ctrl46', 47: 'Ctrl47',
    48: 'General1LSB', 49: 'General2LSB', 50: 'General3LSB',
    51: 'General4LSB', 52: 'Ctrl52', 53: 'Ctrl53',
    54: 'Ctrl54', 55: 'Ctrl55', 56: 'Ctrl56',
    57: 'Ctrl57', 58: 'Ctrl58', 59: 'Ctrl59',
    60: 'Ctrl60', 61: 'Ctrl61', 62: 'Ctrl62',
    63: 'Ctrl63', 64: 'Sustain', 65: 'Portamento',
    66: 'Sostenuto', 67: 'SoftPedal', 68: 'Legato',
    69: 'Hold2', 70: 'Variation', 71: 'Resonance',
    72: 'ReleaseTime', 73: 'AttackTime', 74: 'Brightness',
    75: 'DecayTime', 76: 'VibratoRate', 77: 'VibratoDepth',
    78: 'VibratoDelay', 79: 'Ctrl79', 80: 'General5',
    81: 'General6', 82: 'General7', 83: 'General8',
    84: 'PortamentoCtrl', 85: 'Ctrl85', 86: 'Ctrl86',
    87: 'Ctrl87', 88: 'Ctrl88', 89: 'Ctrl89',
    90: 'Ctrl90', 91: 'Reverb', 92: 'Tremolo',
    93: 'Chorus', 94: 'Detune', 95: 'Phaser',
    96: 'DataInc', 97: 'DataDec', 98: 'NonRegLSB',
    99: 'NonRegMSB', 100: 'RegParLSB', 101: 'RegParMSB',
    102: 'Ctrl102', 103: 'Ctrl103', 104: 'Ctrl104',
    105: 'Ctrl105', 106: 'Ctrl106', 107: 'Ctrl107',
    108: 'Ctrl108', 109: 'Ctrl109', 110: 'Ctrl110',
    111: 'Ctrl111', 112: 'Ctrl112', 113: 'Ctrl113',
    114: 'Ctrl114', 115: 'Ctrl115', 116: 'Ctrl116',
    117: 'Ctrl117', 118: 'Ctrl118', 119: 'Ctrl119',
    120: 'AllSoundsOff', 121: 'ResetAll', 122: 'LocalCtrl',
    123: 'AllNotesOff', 124: 'OmniOff', 125: 'OmniOn',
    126: 'PolyOff', 127: 'PolyOn'}

ctrlInx = dict((v.upper(), k) for (k, v) in ctrlNames.items())

# These are the names of the drumkits. Those marked
# with 'RS' are Roland standard, others are known to
# Yamaha and Casio. Duplicate names are okay.
drumKits = {
    'STANDARD'   :  0,   # RS
    'STANDARD2'  :  1,
    'ROOM'       :  8,   # RS
    'POWER'      : 16,   # RS
    'ROCK'       : 16,
    'ELECTRONIC' : 24,   # RS
    'TR808'      : 25,   # RS
    'SYNTH1'     : 25,
    'SYNTH2'     : 30,
    'JAZZ'       : 32,   # RS
    'BRUSH'      : 40,   # RS
    'ORCHESTRA'  : 48,   # RS
    'CLASSIC'    : 48,
    'SFX'        : 56,   # RS
    'HIPHOP1'    : 64,
    'HIPHOP2'    : 65,
    'TECHNO1'    : 66,
    'TECHNO2'    : 67,
    'DANCE1'     : 68,
    'DANCE2'     : 69
}

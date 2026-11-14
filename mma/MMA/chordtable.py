
# chordtable.py

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



Table of chords. All are based on a C scale.
Generating chords is easy in MIDI since we just need to
add/subtract constants, based on yet another table.

CAUTION, if you add to this table make sure there are at least
3 notes in each chord! 

There is a corresponding scale set for each chord. These are
used by bass and scale patterns. All scales MUST be 7 notes long ...
duplicate notes if needed to make the scale exactly 7 notes.

Each chord needs an English doc string. This is extracted by the
-Dn option to print a table of chordnames for inclusion in the
reference manual.

"""

C  = 0
Cs = Db = 1
D       = 2
Ds = Eb = 3
E  = Fb = 4
Es = F  = 5
Fs = Gb = 6
G       = 7
Gs = Ab = 8
A  = Bbb= 9
As = Bb = 10
B  = Cb = 11

chordlist = {
    'M':    ((C,    E,      G ),
             (C, D, E, F, G, A, B),
             "Major triad. This is the default and is used in  "
             "the absence of any other chord type specification."),

    '(b5)':  ((C,    E,      Gb ),
             (C, D, E, F, Gb, A, B),
             "Major triad with flat 5th. MMA notatation requires the () around the name."),

    'add9': ((C,    E,    G,    D+12),
             (C, D, E, F, G, A, D+12),
             "Major chord plus 9th (no 7th.)"),

    'addb9': ((C,    E,    G,    Db+12),
             (C, D, E, F, G, A, Db+12),
             "Major chord plus flat 9th (no 7th.)"),

    'add#9': ((C,    E,    G,    Ds+12),
             (C, D, E, F, G, A, Ds+12),
             "Major chord plus sharp 9th (no 7th.)"),

    'm':    ((C,    Eb,    G ),
             (C, D, Eb, F, G, Ab, Bb),
             "Minor triad."),

    'mb5':    ((C,    Eb,       Gb ),
             (C, D, Eb, F, Gb, Ab, Bb),
             "Minor triad with flat 5th (aka dim)."),

    'm#5':    ((C,    Eb,       Gs ),
             (C, D, Eb, F, Gs, Ab, Bb),
             "Minor triad with augmented 5th."),

    'm6':    ((C,    Eb,       G, A ),
             (C, D, Eb, F, G, A, Bb),
             "Minor 6th (flat 3rd plus a 6th)."),

    'm6(add9)':    ((C, Eb, G, D+12, A+12),
             (C, D, Eb, F, G, A, Bb),
             "Minor 6th with added 9th. This is sometimes notated as a slash chord "
             "in the form ``m6/9''." ),

    'm7':    ((C,    Eb,       G,      Bb ),
             (C, D, Eb, F, G, Ab, Bb),
             "Minor 7th (flat 3rd plus dominant 7th)."),

    'm7#5':    ((C,    E,    Gs,    Bb),
             (C, D, E, F, Gs, A, Bb),
             "Minor 7th with sharp 5th."),

    'mM7':    ((C,    Eb,      G,      B ),
             (C, D, Eb, F, G, Ab, B),
             "Minor Triad plus Major 7th. You will also see this printed "
             "as ``m(maj7)'', ``m+7'', ``min(maj7)'' and ``min$\sharp$7'' "
             "(which \mma\ accepts); as well as the \mma\ \emph{invalid} "
             "forms: ``-($\Delta$7)'', and ``min$\\natural$7''."),

    'm+7b9':  ((C, Eb, Gs, Bb, Db+12),
               (C, Db, Eb, F, Gs, Ab, Bb),
               "Augmented minor 7 plus flat 9th."),

    'm+7#9':  ((C, Eb, Gs, Bb, Ds+12),
               (C, Ds, Eb, F, Gs, Ab, Bb),
               "Augmented minor 7 plus sharp 9th."),
    
    'mM7(add9)': ((C, Eb, G, B, D+12),
                 (C, D, Eb, F, G, Ab, B),
                 "Minor Triad plus Major 7th and 9th."),

    'm7b5': ((C,    Eb,       Gb,       Bb ),
             (C, D, Eb, F, Gb, Ab, Bb),
             "Minor 7th, flat 5 (aka 1/2 diminished). "),

    'm7b9': ((C,     Eb,    G,     Bb, Db+12 ),
             (C, Db, Eb, F, G, Ab, Bb),
             "Minor 7th with added flat 9th."),

    'm7#9': ((C,     Eb,    G,     Bb, Ds+12 ),  # Eb == D# 
             (C, Ds, Eb, F, G, Ab, Bb),
             "Minor 7th with added sharp 9th."),

    'mb9': ((C,    Eb,    G,    Db+12),
             (C, D, Eb, F, G, A, Db+12),
             "Minor chord plus flat 9th (no 7th.)"),

    '7':    ((C,    E,      G,    Bb ),
             (C, D, E, F, G, A, Bb),
             "7th."),

    '7(6)':    ((C,    E,      G, A,   Bb ),
             (C, D, E, F, G, A, Bb),
             "7th with added 6th."),

    '7b5':    ((C,    E,      Gb,    Bb ),
             (C, D, E, F, Gb, A, Bb),
             "7th, flat 5."),

    'dim7': ((C,    Eb,       Gb,       Bbb ),
             (C, D, Eb, F, Gb, Ab, Bbb ),    # missing 8th note
             "Diminished seventh."),
    
    'dim7(addM7)': ((C, Eb, Gb, A, B),
             (C, D, Eb, F, Gb, A, B),
             "Diminished triad with added Major 7th."),

    'dim(b13)':  ((C, Eb, Gb, Bbb, Ab),
                 (C, D, Eb, F, Gb, Ab, Bbb),
                 "Diminished seventh, added flat 13th."),

    'aug':    ((C,    E,      Gs ),
             (C, D, E, F, Gs, A, B ),
             "Augmented triad."),

    '6':    ((C,    E,      G, A ),
             (C, D, E, F, G, A, B),
             "Major triad with added 6th."),

    '6(add9)':    ((C,   E, G, D+12, A+12),
             (C, D, E, F, G, A, B),
             "6th with added 9th. This is sometimes notated as a slash chord "
             "in the form ``6/9''. MMA voices the 6th an octave higher."),

    'M7':    ((C,    E,    G,    B),
             (C, D, E, F, G, A, B),
             "Major 7th."),



    'M7#5':    ((C,    E,    Gs,    B),
             (C, D, E, F, Gs, A, B),
             "Major 7th with sharp 5th."),

    'M7b5': ((C,    E,      Gb,    B ),
             (C, D, E, F, Gb, A, B ),
             "Major 7th with a flat 5th."),

    'M7(add6)': ((C, E, G, A, B),
               (C, D, E, F, Gb, A, B),
               "Major 7th with a 6th."),

    '9':    ((C,    E,    G,    Bb, D+12 ),
             (C, D, E, F, G, A, Bb),
             "7th plus 9th."),

 

    '9b5':    ((C,    E,    Gb,    Bb, D+12 ),
             (C, D, E, F, Gb, A, Bb),
             "7th plus 9th with flat 5th."),

    'm9':    ((C,    Eb,       G,      Bb, D+12 ),
             (C, D, Eb, F, G, Ab, Bb),
             "Minor triad plus 7th and 9th."),

    'm7b5b9': ((C, Eb, Gb, Bb, Db+12),
               (C, Db, Eb, F, Gb, Ab, Bb),
               "Minor 7th with flat 5th and flat 9th."),

    'm9b5': ((C,    Eb,    Gb, Bb, D+12 ),
             (C, D, Eb, F, Gb, Ab, Bb),
             "Minor triad, flat 5, plus 7th and 9th."),

    'm(sus9)':((C,      Eb,    G,     D+12 ),
               (C, D, Eb, F, G, Ab, D+12),
               "Minor triad plus 9th (no 7th)."),

    'M9':    ((C,    E,    G,    B, D+12 ),
             (C, D, E, F, G, A, B),
             "Major 7th plus 9th."),

    'M9#11': ((C, E, G, B, D+12, Fs+12),
              (C, D, E, Fs, G, A, B),
              "Major 9th plus sharp 11th."),

    '7b9':    ((C,     E,    G,    Bb, Db+12 ),
             (C, Db, E, F, G, A, Bb),
             "7th with flat 9th."),
    
    '7b9b13':    ((C,     E,    G,    Bb, Db+12, Ab+12 ),
             (C, Db, E, F, G, A, Bb),
             "7th with flat 9th and flat 13th."),
    
    '7#9':    ((C,     E,    G,    Bb, Ds+12 ),
             (C, Ds, E, F, G, A, Bb),
             "7th with sharp 9th."),

    '7#9b13':    ((C,     E,    G,    Bb, Ds+12, Ab+12 ),
             (C, Ds, E, F, G, Ab, Bb),
             "7th with sharp 9th and flat 13th."),

    '7b5(add13)':    ((C,     E,    Gb,    Bb, A+12 ),
             (C, D, E, F, Gb, A, Bb),
             "7th with flat 5 and 13th."),

    '7(add13)':    ((C,     E,    G,    Bb, A+12 ),
             (C, D, E, F, G, A, Bb),
             "7th with added 13th."),

    '7b5b9':((C,     E,    Gb,    Bb, Db+12 ),
             (C, Db, E, F, Gb, A, Bb),
             "7th with flat 5th and flat 9th."),

    '7b5#9':((C,     E,    Gb,    Bb, Ds+12 ),
             (C, Ds, E, F, Gb, A, Bb),
             "7th with flat 5th and sharp 9th."),

    '7#5#9':((C,     E,    Gs,    Bb, Ds+12 ),
             (C, Ds, E, F, Gs, A, Bb),
             "7th with sharp 5th and sharp 9th."),

 
    'aug7': ((C,    E,    Gs,    Bb ),
             (C, D, E, F, Gs, A, Bb),
             "An augmented chord (raised 5th) with a dominant 7th."),

    'aug7b9':((C,     E,    Gs,    Bb, Db+12 ),
              (C, Db, E, F, Gs, A, Bb),
              "An augmented chord (raised 5th) with a dominant 7th and flat 9th."),

    'aug7#9':((C,     E,    Gs,    Bb, Ds+12 ),
              (C, Ds, E, F, Gs, A, Bb),
              "An augmented chord (raised 5th) with a dominant 7th and sharp 9th."),

    'aug9M7':((C,     E,    Gs,    B, D+12 ),
              (C, D, E, F, Gs, A, B),
              "An augmented chord (raised 5th) with a major 7th and 9th."),

    '+7b9#11': ((C, E, Gs, Bb, Db+12, Fs+12),
                (C, Db, E, Fs, G, A, Bb),
                "Augmented 7th with flat 9th and sharp 11th."),

    'm+7b9#11':  ((C, Eb, Gs, Bb, Db+12, Fs+12),
                (C, Db, Eb, Fs, Gs, A, Bb),
                "Augmented minor 7th with flat 9th and sharp 11th."),

    '11':    ((C,   C,    G,    Bb, D+12, F+12 ),
             (C, D, E, F, G, A, Bb),
             "9th chord plus 11th (3rd not voiced)."),

    '11+':    ((C,   C,    Gs,    Bb, D+12, F+12 ),
             (C, D, E, F, Gs, A, Bb),
             "Augmented 11th (sharp 5)."),
    
    'm11':    ((C,    Eb,    G,     Bb, D+12, F+12 ),
             (C, D, Eb, F, G, Ab, Bb),
             "9th with minor 3rd,  plus 11th."),

    'M11':    ((C,    E,    G,   B, D+12, F+12 ),
             (C, D, E, F, G, Ab, B),
             "Major 9th plus 11th."),

    'm7(add11)':    ((C,    Eb,    G,    Bb, F+12 ),
             (C, D, Eb, F, G, Ab, Bb),
             "Minor 7th  plus 11th."),

    'm9#11':   ((C, Eb, G, Bb, D+12, Fs+12),
                (C, D, Eb, Fs, G, A, Bb),
                "Minor 7th plus 9th and sharp 11th."),

    'm7b9#11':  ((C, Eb, G, Bb, Db+12, Fs+12),
                (C, Db, Eb, Fs, G, A, Bb),
                "Minor 7th plus flat 9th and sharp 11th."),

    'm7(add13)':    ((C,    Eb,    G,    Bb, A+12 ),
             (C, D, Eb, F, G, A, Bb),
             "Minor 7th  plus 13th."),

    '11b9': ((C,     E,    G,    Bb, Db+12, F+12 ),
             (C, Db, E, F, G, A, Bb),
             "7th chord plus flat 9th and 11th."),

    '9#5':    ((C,    E,    Gs,    Bb, D+12 ),
             (C, D, E, F, Gs, A, Bb),
             "7th plus 9th with sharp 5th (same as aug9)."),

    '9b6':   ((C,   E,  Ab, D+12 ),
              (C, D, E, F, Ab, B, D+12),
              "9th with flat 6 (no 5th or 7th)."),
    
    '9#11': ((C,    E,     G,    Bb, D+12, Fs+12 ),
             (C, D, E, Fs, G, A, Bb),
             "7th plus 9th and sharp 11th."),

    '7#9#11':((C,     E,     G,    Bb, Ds+12, Fs+12 ),
              (C, Ds, E, Fs, G, A, Bb),
              "7th plus sharp 9th and sharp 11th."),

    '7b9#11': ((C,     E,     G,    Bb, Db+12, Fs+12 ),
              (C, Db, E, Fs, G, A, Bb),
              "7th plus flat 9th and sharp 11th."),

    '7#11':((C,    E,     G,    Bb,  Fs+12 ),
             (C, D, E, Fs, G, A, Bb),
             "7th plus sharp 11th (9th omitted)."),

    'M7#11':((C,    E,     G,    B,  Fs+12 ),
             (C, D, E, Fs, G, A, B),
             "Major 7th plus sharp 11th (9th omitted)."),

    'm11b5': ((C, Eb, Gb, Bb, D+12, F+12),
              (C, D, Eb, F, Gb, A, Bb),
              "Minor 7th with flat 5th plus 11th."),

    # Sus chords. Not sure what to do with the associated scales. For
    # now just duplicating the 2nd or 3rd in the scale seems to make sense.

    'sus4': ((C,    F,    G ),
             (C, D, F, F, G, A, B),
             "Suspended 4th, major triad with the 3rd raised half tone."),

    'msus4':   ((C,    Eb,  F,  G ),
             (C, D, Eb, F, G, Ab, Bb),
             "Minor suspended 4th, minor triad plus 4th."),

    'm7sus4':  ((C,    Eb,  F,  G, Bb ),
             (C, D, Eb, F, G, Ab, Bb),
             "Minor suspended 4th, minor triad plus 4th and dominant 7th."),

    'sus(addb9)': ((C,    F,    G, Db+12 ),
             (C, D, F, F, G, A, B),
             "Suspended 4th, major triad with the 3rd raised half tone plus flat 9th."),

    'sus(add9)': ((C,    F,    G,  D+12 ),
             (C, D, F, F, G, A, B),
             "Suspended 4th, major triad with the 3rd raised half tone plus 9th."),

    'sus(add#9)': ((C,    F,    G, Ds+12 ),
             (C, D, F, F, G, A, B),
             "Suspended 4th, major triad with the 3rd raised half tone plus sharp 9th."),

    '7sus': ((C,    F,    G,    Bb ),
             (C, D, F, F, G, A, Bb),
             "7th with suspended 4th, dominant 7th with 3rd "
             "raised half tone."),

    '7susb9': ((C, F, G, Bb, Db+12),
               (C, Db, F, F, G, A, Bb),
               "7th with suspended 4th and flat 9th."),

    'sus2': ((C,    D,    G ),
             (C, D, D, F, G, A, B),
             "Suspended 2nd, major triad with the major 2nd above the "
             "root substituted for 3rd."),

    '7sus2':((C,    D,    G,    Bb ),
             (C, D, D, F, G, A, Bb),
             "A sus2 with dominant 7th added."),

    'sus9': ((C,    F,    G,    Bb, D+12),
             (C, D, F, F, G, A, Bb),
             "7sus plus 9th."),

    '13sus': ((C, F, G, Bb, D+12, A+12),
               (C, D, F, F, G, A, Bb),
               "7sus, plus 9th and 13th"),

    '13susb9': ((C, F, G, Bb, Db+12, A+12),
               (C, Db, F, F, G, A, Bb),
               "7sus, plus flat 9th and 13th"),

    # these chords should probably NOT have the 5th included,
    # but since a number of voicings depend on the 5th being
    # the third note of the chord, they're here.

    '13':    ((C,    E,    G,    Bb, A+12),
             (C, D, E, F, G, A, Bb),
             "7th (including 5th) plus 13th (the 9th and 11th are not voiced)."),

    '7b13':  ((C,    E,    G,    Bb, Ab+12),
             (C, D, E, F, G, A, Bb),
             "7th (including 5th) plus flat 13th (the 9th and 11th are not voiced)."),

    '13b5':  ((C,    E,    Gb,    Bb, Ab+12),
             (C, D, E, F, Gb, A, Bb),
             "7th with flat 5th,  plus 13th (the 9th and 11th are not voiced)."),

    '13#9':    ((C,    E,    G,    Bb, Ds+12,  A+12),
             (C, Ds, E, F, G, A, Bb),
             "7th (including 5th) plus 13th and sharp 9th (11th not voiced)."),
 
    '13b9':  ((C,    E,    G,    Bb, Db+12,  A+12),
             (C, Db, E, F, G, A, Bb),
             "7th (including 5th) plus 13th and flat 9th (11th not voiced)."),
    
    'M#11':   ((C,    E,    G,    B, Fs+12),
             (C, D, E, Fs, G, A, B),
             "Major triad plus sharp 11th."),
    
    'M13':   ((C,    E,    G,    B, A+12),
             (C, D, E, F, G, A, B),
             "Major 7th (including 5th) plus 13th (9th and  11th not voiced)."),

    'm13':   ((C, Eb, G, Bb, A+12),
              (C, D, Eb, F, G, A, Bb),
              "Minor 7th (including 5th) plus 13th (9th and 11th not voiced)."),

    '13#11': ((C,    E,    G,    Bb, Fs+12, A+12),
             (C, D, E, Fs, G, A, Bb),
             "7th plus sharp 11th and 13th (9th not voiced)."),

    'M13#11': ((C,    E,    G,    B, Fs+12, A+12),
             (C, D, E, Fs, G, A, B),
             "Major 7th plus sharp 11th and 13th (9th not voiced)."),

    # Because some patterns assume that the 3rd note in a chord is a 5th,
    # or a varient, we duplicate the root into the position of the 3rd ... and
    # to make the sound even we duplicate the 5th into the 4th position as well.

    '5':    ((C, C,    G, G ),
             (C, D, E, F, G, A, B),
             "Altered Fifth or Power Chord; root and 5th only."),

    'omit3add9': ((C, C, G, D+12),
               (C, D, E, F, G, A, Bb),
               "Triad: root, 5th and 9th."),

    '7omit3': ((C, C, G, Bb),
                (C, D, E, F, G, A, Bb),
                "7th with unvoiced 3rd."),

    'm7omit5': ((C, Eb, Bb),
                 (C, D, Eb, F, G, A, Bb),
                 "Minor 7th with unvoiced 5th."),
}


# Extend our table with common synomyns. These are real copies,
#   not pointers. This is done so that a user redefine only affects
#   the original. There is no way to tell if a chordlist[] entry is
#   from above or if it's an added alias or defChord.

aliases = (
    ('11#5',     '11+',      ''),
    ('aug9',     '9#5',      ''),
    ('9+',       '9#5',      'Recommended notation is "+9" or "9\#5"'),
    ('+9',       '9#5',      ''),
    ('+9M7',     'aug9M7',   ''),
    ('+M7',      'M7#5',     ''),
    ('m(add9)',  'm(sus9)',  ''),
    ('(add9)',   'add9',     ''),
    ('(addb9)',  'addb9',    ''),
    ('(add#9)',  'add#9',    ''),
    ('69',       '6(add9)',  ''),
    ('m69',      'm6(add9)', ''),
    ('m(b5)',    'mb5',      ''),
    ('m7(b9)',   'm7b9',     ''),
    ('m7(#9)',   'm7#9',     ''),
    ('9+5',      '9#5',      ''),
    ('m+5',      'm#5',      ''),
    ('m+',       'm#5',      ''),
    ('M6',       '6',        ''),
    ('m7-5',     'm7b5',     ''),
    ('m7(omit5)','m7omit5',  ''),
    ('+',        'aug',      ''),
    ('+7',       'aug7',     ''),
    ('+7#9',     'aug7#9',   ''),
    ('+7b9',     'aug7b9',   ''),
    ('7(omit3)', '7omit3',   ''),
    ('(#5)',     'aug',      ''),
    ('7#5b9',    'aug7b9',   ''),
    ('7b9#5',    'aug7b9',   ''),
    ('7-9',      '7b9',      ''),
    ('7+9',      '7#9',      'Confusing, not recommended.'),
    ('maj7',     'M7',       ''),
    ('M7-5',     'M7b5',     ''),
    ('M7+5',     'M7#5',     'Recommended notation is +M7.'),
    ('M7(add13)','13b9',     ''),
    ('7alt',     '7b5b9',    'Uses a 7th flat 5, flat 9. Probably not correct, but works (mostly).'),
    ('7sus4',    '7sus',     ''),
    ('13sus4',   '13sus',    ''),
    ('7+',       'aug7',     'An augmented (sharp 5) 7th. Recommended notation is "+7"'),
    ('7#5',      'aug7',     'Recommended notation is "+7"'),
    ('7+5',      'aug7',     'Recommented notation is "+7"'),
    ('7-5',      '7b5',      ''),
    ('sus',      'sus4',     ''),
    ('maj9',     'M9',       ''),
    ('maj13',    'M13',      ''),
    ('m(maj7)',  'mM7',      ''),
    ('m+7',      'mM7',      ''),
    ('min(maj7)','mM7',      ''),
    ('min#7',    'mM7',      ''),
    ('m#7',      'mM7',      ''),
    ('msus',     'msus4',    ''),
    ('m7sus',    'm7sus4',   ''),
    ('dim',      'dim7',     'A dim7, not a triad!'),
    (chr(176),   'dim7',     'A dim7 using a degree symbol'),
    (chr(176)+'3', 'mb5',   'A dim3 (triad) using a degree symbol'),
    (chr(176)+'(addM7)', 'dim7(addM7)', 'dim7(addM7) using degree symbol'),
    (chr(248),   'm7b5',     'Half-diminished using slashed degree symbol'),
    ('9sus',     'sus9',     ''),
    ('9-5',      '9b5',      ''),
    ('dim3',     'mb5',      'Diminished triad (non-standard notation).'),
    ('omit3(add9)','omit3add9', ''),
    ('9sus4',    'sus9',     ''),
    ('7b9sus',   '7susb9',   '')
    )

for a, b, d in aliases:
    n = chordlist[b][0]
    s = chordlist[b][1]
    if not d:
        d = chordlist[b][2]

    chordlist[a] = (n, s, d)

### little snippet to print chord info for my accordion chord program.
##print "chords = {"
##for a in chordlist:
##    print "   '%s': ( %s,  \"%s\")," % (a, chordlist[a][0], chordlist[a][2])
##print "}"

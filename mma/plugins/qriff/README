
This is a plugin to handle quarter tone notes in MMA solo/melody sections.

To use, just use a "%" or "*" to indicate that a note should be 1/4 flat or sharp.

Example:  Solo Qriff  4a;b*;c#*;b&%;


What happens:
-------------

1. The Qriff plugin creates (if necessary) 2 new tracks. Each has "-qSharp" and
 "-qFlat" appended to the original track name. Existing settings are copied to
 the new tracks. Yes, this does use up 2 additional MIDI tracks. And, yes, there
 are reasons (see below).

2. MIDI commands to "tune" the 1/4 tone tracks. 

3. An After command is generated to "retune" the 1/4 tone tracks.

4. Quarter tone notes are extracted from the original line and added to the 1/4
 flat/sharp flats. The original track's 1/4 tone notes are replaced with rests.

5. The magic is achieved by pushing the text for the 3 strings back into the
 input stream when they can be re-evaluated.

6. If you want to see what's happening, use a -d on the command line. Or, 
 even better, -e.


Problems:
---------

1. The parsing is pretty primitive. 

2. A single "*" or "@" is applied to all the notes in a chord. So, you
 cannot have a chord with, for example, a "g natural" and a "b *". Both
 notes will be copied to the "*" track. You could work around this with a 4th track :)

3. The same de-tuning is applied to * and %. I have no idea if this is correct
 for this kind of music, or if the intervals should be modified.

4. Plugins don't work with the {} solo note notation.

5. This doesn't work with chord and other tracks. Just Solo/Melody.


Rationale:
----------

When I started to write the plugin I picked the "use additional tracks" approach
 simply because it was easy. But, looking with hindsight it really is the only
 logical way to do this. Once might think that surrounding each note with tuning
 code would be a way to avoid some problems, but it just creates more. The MIDI
 pitch bend directive applies to a track and if there were overlapping tones it
 would create something not wanted. There are micro-tuning enhancements to the
 MIDI spec, but few synths support it.


And:
----

Here you go. It's not supported and really could use some love and attention! Let me know.


June 2016, bvdp   





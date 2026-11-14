
This directory contains examples of how you can include
recorded MIDI tracks into a MMA song. This is very quick,
dirty and not-all-that-great-sounding, but it serves as a
demo.

First off, I recorded two takes of the solo line for
Frankie and Johnny. I did this by recording me playing
my synth via the the Linux program arecordmidi, but
just about any MIDI recording should work. 

For the first track recording I used the command line:

	arecordmidi -p64 -b120 -m64 -t192 -s rec1.mid
	
The command line switches:

	-p64  ALSA midi input port 0:64
	-m64  Play a metronome on ALSA port 0:64
	-s    Split recorded tracks
	-t192 Set beat division to 192 (the same as what MMA uses)
	-b120 Tempo of 120 bpm
	
If you play this back you'll hear a piano playing the melody
at 120 bpm. 

The second track recording also has a piano voice on playback, but
used a different set of switches:

	arecordmidi -p64 -b100 -m64 -t192 -s rec2.mid
	
The important one here is the tempo which is 100. If you play this
file back you'll get some quite awful sounding piano with vibrato
and wheel effects. Really, the only reason I recorded this is to
see what happens with the wheel and vibrato button. BTW, I have
not done this kind of playing in the past and it is hard to get
good sounding wheel/vibrato effect :)

A third track recorded is a one bar drum solo. Hey, it's not a wonderful
drum solo, but I'm not a drummer ... and this is just a demo :)
The drum was recorded just like the other examples above, but this time
we set our keyboard up with drum tones so we could hear it properly. Note
that when we include the file we transfer the recorded channel 1 to the drum
track (and if you just play it, it'll sound like a badly played piano
instead of badly played drums). Also note that we do a transpose=0;
this ensures that no notes are moved, even if there is a global transpose.
Including drum solos were a major reason to write this code in the first
place, so please make use of the feature ... and do share some good solos
with the rest of us!

Now, we have some tracks. It is so easy to combine these with a
MMA song! Just look at the file frankie.mma which is quite fully
commented. Note the tricks, they're used for a reason :)

For complete listing of the various options available in
a MIDIinc line, please Read The Fine Manual.



Short usage file for mma-splitrec.py.

NOTE: this program replaces the earlier program timsplit.

This program is used to create a set of wav tracks from a MMA
input file. You need MMA, the input file, a midiplayer, audio
recorder and an external synth or timidity.

The command:

	  mma-splitrec.py somefile.mma

will determine the tracks in the MMA file, create temporary MIDIs
for each track, play each file though an external synth and record
the results into a series of wav files.

Also created is a mix file with all the tracks. This is called "bg.wav".

When using an external synth the conversion takes a long time ...
about the number of tracks times the duration of the song. Be patient.

I you have timidity installed you can let it create the wav files. It works
pretty well, depending on your installed soundfonts.

Using timidity i've had good success with the following:

  1. use timsplit with a decent soundfont to create tracks,
  2. use timidity to create a mix track of the mma file,
  3. copy the mix to my Zoom H4 recorder into a project file,
  4. play/create lots of sax tracks while listening to the mix (4 track mode on the H4),
  5. copy the sax tracks the split tracks from (1) into audacity,
  6. edit the tracks,
  7. publish the song and become rich and famous!


Command summary:

mma-splitrec takes a number of command line options:

 -m  Set the midi file player (aplaymidi) options. This is usually
     the port. You should quote the arg:  -m "-p 20"

 -r  Recorder options (arecord). You can change the number of channels,
     quality, port, etc. Again, quote the arg: -r "-D hw:0,0 -c2"

 -o  Timidity options. Quote args: -o "-Ow"

See the manual pages for aplaymidi, arecord and timidiy for option details.

 -i  By default an external synth is assumed. Use this option to force use
     of timidity.

 -b  By default the track "bg.wav" is created with all tracks playing. This
     option will skip creating that track.

 -t  Create only track XX. The track name is passed to mma and its -T option.
     To create a set of tracks you need multiple -t settings: -t Solo -t Chord-piano
     The track names are NOT case sensitive.

 -x  Exclude tracks. Again, a separate -x is required for each track to skip.


More questions are answered by reading the source :)

bvdp, January/2011


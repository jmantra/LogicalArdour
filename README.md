# LogicalArdour
This is a project currently in development to give Ardour functionality similiar to GarageBand/Logic Pro out of the box using Ardour's Lua scripting interface as well as some Python, Bash scripting and FOSS plugins.

# Talk/Demo
Here is my Ohio LinuxFest talk on this project: "Why Ardour is the GarageBand of Linux: Elevating Ardour with Lua scripting": https://www.youtube.com/live/JOPmdu7Wrh4?si=pqtiZVCIf2Y8QHny&t=7369

# Goals
* Guided menu system for creating different track types as well as changing Instruments/Plugins and presets.
* Have lots of MIDI/Audio loops available at your disposal(Ardour has these by default out of the box.
* Instruments: Have access to a full library of Instruments and instrument sounds out of the box and be easily able to switch
* between the different instruments.
* Drums: Have a wide variety of drum sets available and the ability to easily switch between them. Have drum loops
 automatically “follow” any audio loops.
* Guitar: have a ton of presets for guitar/bass sounds available out of the box, be easily able to switch between guitar sounds and
 be able to customize your sound.
* Vocals: Be able to easily switch between different vocal presets.
* Autotune: Easy to setup autotune that can “follow” the key of your project.(Sound like T-pain)
* Be able to transpose audio by key and scale. (I.E. change the pitch of an audio loop for C Major to F Major)
* Be able to time stretch an audio loop to a fixed BPM (Beats Per Minute or Tempo).
* Be able to view and edit MIDI regions as musical scores (sheet music)
* Other functionality not found in GB.
* Have all instruments, plugins, loops, dependencies and defaults installed out of the box by an install shell script.
* Have an easy to use sampler
* Have a help section built into the menu system that takes you to Youtube help videos for the project as well as written documentation and other resources for music production. 

# Additional Functionality
Below are a list of additional functionality that has been implemented in this project that GarageBand does not currently have
* Session Player: This is similiar to the Session Player found in Logic Pro 11 where you have arpeggiated intruments( that randomly go up and down octaves) following a chord progression. It works similiar to the drummer where instruments can "follow" an audio loop. Can also use the audio to MIDI lua script that comes with Ardour to "follow" the audio loop as well.
* Random Chord Genrator
* Random Bassline Generator
* Voice to MIDI using moified version of Ardour's audio to MIDI lua script.
* Drum sequencing: While GarageBand for iOS does have a drum sequencer, GarageBand for Mac does not.
* Unlimited tracks and customizability: Unlike GarageBand, Ardour is a full DAW.

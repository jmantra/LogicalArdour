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

"""

# ###################################
# # StrumPattern 1.0 MMA plugin     #
# #                                 #
# # written by Ignazio Di Napoli    #
# # <neclepsio@gmail.com>           #
# ###################################

# We import the plugin utilities
from MMA import pluginUtils as pu


# ###################################
# # Documentation and arguments     #
# ###################################

# We add plugin parameters and documentation here.
# The documentation will be printed either calling printUsage() or
# executing "python mma.py -I pluginname". 
# I suggest to see the output for this plugin to understand how code
# of this section will be formatted when printed.

# Minimum MMA required version.
pu.setMinMMAVersion(15, 12)

# A short plugin description.
pu.setDescription("Sets a strum pattern for Plectrum tracks.")

# A short author line.
pu.setAuthor("Written by Ignazio Di Napoli <neclepsio@gmail.com>.")

# Since this is a track plugin, we set the track types for which it can
# be used. You can specify more than one. To allow for all track types,
# call setTrackType with no arguments.
# For non-tracks plugin, don't call setTrackType at all.
# Whether the plugin is track or non-track is decided by the entry point,
# but help will use this information.
pu.setTrackType("Plectrum")

# We add the arguments for the command, each with name, default value and a
# small description. A default value of None requires specifying the argument.
pu.addArgument("Pattern",     None,  "see after")
pu.addArgument("Strum",       "5",   "strum value to use in sequence (see Plectrum docs)")
pu.addArgument("Volume",      "80",  "volume for strums, can be specified for each string (see Plectrum docs)")
pu.addArgument("VolumeMuted", "60",  "volume for mute, can be specified for each string (see Plectrum docs)")
pu.addArgument("VolumeEmph",  "100", "volume for emphatized strums, can be specified for each string (see Plectrum docs)")
pu.addArgument("VolumePick",  "90",  "volume for single string pick")

# We add a small doc. %NAME% is replaced by plugin name.
pu.setPluginDoc("""
The pattern is specified as a string of dot-separed values, that are equally spaced into the bar.
Values can be:
    d   downward strum
    u   upward strum
    de  downward strum with emphasis
    ue  upward strum with emphasis
    dm  downward strum with muted strings
    um  upward strum with muted strings
    x   chunk
    -   do nothing (used to skip to next time division)
If only one-character codes are used, you can avoid dots.
You can specify more bars separed by semicolons (;).
    
Examples:
    Plectrum %NAME% dudududu
    Plectrum %NAME% dm.um.dm.um.dm.um.dm.um
    Plectrum %NAME% dudududu;12345654
    Plectrum %NAME% dudududu, Strum=10
    Plectrum %NAME% dudududu, 5, 70, 60, 90, 80
    Plectrum %NAME% dudududu, 7, VolumeEmph=90
    
Each time it's used, %NAME% creates a clone track of the provided one using the voice MutedGuitar for chucks and muted strums.
Its name is the name of the main track with an appended "-Muted", if you need to change it you must do so every time after using %NAME%.

This plugin has been written by Ignazio Di Napoli <neclepsio@gmail.com>. 
Version 1.0.
""")
  
    

# ###################################
# # Entry points                    #
# ###################################

# This prints help when MMA is called with -I switch.
# Cannot import plugin_utils directly because it wouldn't recognize which
# plugin is executing it.
def printUsage():
    pu.printUsage()

# This is a track plugin, so we define trackrun(trackname, line).
# For non-track plugins we use run(line).
# When using this library, only one of the two can be used.
def trackRun(trackname, line):
    # We check if track type is correct.
    pu.checkTrackType(trackname)
    # We parse the arguments. Errors are thrown if something is wrong,
    # printing the correct usage on screen. Default are used if needed.
    # parseCommandLine also takes an optional boolean argument to allow
    # using of arguments not declared with pu.addArgument, default is False.
    args = pu.parseCommandLine(line)
    
    # This is how we access arguments.
    pattern = args["Pattern"]
    strum   = args["Strum"]
    volumeN = args["Volume"]
    volumeM = args["VolumeMuted"]
    volumeE = args["VolumeEmph"]
    volumeP = args["VolumePick"]
    
    # This is the logic for the plugin.
    all_normal = ""
    all_muted = ""
    
    for bar_pattern in pattern.split(";"):
        if "." in bar_pattern:
            bar_pattern = bar_pattern.lower().split(".")
        else:
            # you can avoid commas when not using ue, ux, de, dx
            bar_pattern = bar_pattern.lower()

        strums_normal = []
        strums_muted = []
        
        step = float(pu.getSysVar("TIME"))/len(bar_pattern)
        for i, c in enumerate(bar_pattern):
            t = 1+step*i
        
            if c == "u":
                strums_normal.append("{:0.4} -{} {}".format(t, strum, volumeN))
            elif c == "ue":
                strums_normal.append("{:0.4} -{} {}".format(t, strum, volumeE))
            elif c == "um":
                strums_normal.append("{:0.4} 0 0".format(t))
                strums_muted.append("{:0.4} -{} {}".format(t, strum, volumeM))
                
            elif c == "d":
                strums_normal.append("{:0.4} +{} {}".format(t, strum, volumeN))
            elif c == "de":
                strums_normal.append("{:0.4} +{} {}".format(t, strum, volumeE))
            elif c == "dm":
                strums_normal.append("{:0.4} 0 0".format(t))
                strums_muted.append("{:0.4} +{} {}".format(t, strum, volumeM))
                
            elif c == "x":
                strums_normal.append("{:0.4} 0 0".format(t))
                strums_muted.append("{:0.4} 0 {}".format(t, volumeM))
                
            elif c == "0":
                strums_normal.append("{:0.4} 0 0".format(t))
                
            elif c.lstrip("0").isdigit():
                for s in c:
                    strums_normal.append("{:0.4} 0 {}:{}".format(t, s, volumeP))

            elif c == "-":
                pass
                
            else:
                #printUsage()
                pu.error("{}: unrecognized command in strum pattern: '{}'.".format(pu.getName(), c))    
     
        bar_normal = ("{" + "; ".join(strums_normal) + ";}") if len(strums_normal) > 0 else "z"
        bar_muted  = ("{" + "; ".join(strums_muted)  + ";}") if len(strums_muted)  > 0 else "z"
        
        all_normal += bar_normal + " "
        all_muted  += bar_muted + " "
        

    # If you don't send all the commands together the result is commands 
    # are reversed since each is pushed as the very next command to be executed.
    # So we save all the commands (with addCommand) and send them at the end
    # (with sendCommands).
    
    pu.addCommand("{} Sequence {}".format(trackname, all_normal))
    pu.addCommand("{}-Muted SeqClear".format(trackname))
    pu.addCommand("{}-Muted Copy {}".format(trackname, trackname))
    pu.addCommand("{}-Muted Voice MutedGuitar".format(trackname))
    pu.addCommand("{}-Muted Sequence {}".format(trackname, all_muted))
    pu.sendCommands()


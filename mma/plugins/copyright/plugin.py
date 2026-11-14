# We import the plugin utilities
from MMA import pluginUtils as pu

import datetime

# Minimum MMA required version.
pu.setMinMMAVersion(16, 0)

# A short plugin description.
pu.setDescription("Adds a copyright notice to the MIDI.")

author = "Johan Vromans"
# A short author line.
pu.setAuthor("Written by {}".format(author))

# We add the arguments for the command, each with name, default value and a
# small description. A default value of None requires specifying the argument.
pu.addArgument("Author", author, "The name of the copyright holder")
pu.addArgument("Year", '{}'.format(datetime.date.today().year),
               "The (first) year the copyright is valid")

# We add a small doc. %NAME% is replaced by plugin name.
pu.setPluginDoc("""
This plugin adds a copyright notice to the MIDI output using MMA command MidiCopyright.

The copyright notice consists of the copyright symbol, followed by the year and author (the copyright holder). Both `year' and `author' are arguments to this plugin. 

As suggested by the MIDI specs, `(C)' is used as copyright symbol.

This plugin has been written by Johan Vromans <jvromans@squirrel.nl>
Version 1.0.
""")

# ###################################
# # Entry points                    #
# ###################################

# This prints help when MMA is called with -I switch.
def printUsage():
    pu.printUsage()

# This is not a track plugin, so we define run(line).
def run(line):

    # We parse the arguments. Errors are thrown if something is wrong,
    # printing the correct usage on screen. Default are used if needed.
    # parseCommandLine also takes an optional boolean argument to allow
    # using of arguments not declared with pu.addArgument, default is False.
    args = pu.parseCommandLine(line)

    # This is how we access arguments.
    author = args["Author"]
    year   = args["Year"]

    # MIDI specs say we should use (C).
    pu.addCommand("MidiCopyright (C) {} {}".format(year, author))
    pu.sendCommands()

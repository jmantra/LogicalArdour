# Demo for using the data plugin

# We import the plugin utilities
from MMA import pluginUtils as pu
import MMA.gbl as gbl

def dataRun(ln):
    """ The actual plugin code. Note that it is called 
        via a standard mma data line with the plugin name
        inserted into that. The plugin converts that part
        of the line to something else ... in this case "Gm".
        However, there is nothing to stop your code from examining
        the line and changing anything in it.
    """
    
    return ['Gm'] + ln

# Entry for usage (mma -Iaddgm)

def printUsage():    
    print("Usage for the mma addgm plugin. ")

# Hello world MMA plugin

# This import will access the global variables in MMA.
# You can BUT SHOULD NOT change things. 

import MMA.gbl as gbl

# Things outside of functions are done just one when the
# module is loaded.

# print("Welcome to the hello world MMA plugin. This message should only appear one time.")

# Here is the entry point function. It must be called run().
# It will receive a list of paramaters as a list of items.

def run(l):
    print("Hello. This is the run() function in the MMA plugin.")
    print("We are at line %s in the MMA file %s." % (gbl.lineno, gbl.infile))

    if l:
        print("Args passed are:")
        for i in l:
            print(i)

# Alternative entry point for track functions.

def trackRun(name, l):
    print("This is the track variant.")
    print("Used as a %s command." % name)

    self = gbl.tnames[name]

    print("This is the plugin '%s' located at '%s'." % (plugInName['name'], plugInName['dir']))
    print("One can access methods and variables belonging to the track.")
    print("For example, this is the state for octave list: %s" % self.octave)
    print("Which means our current octave for the track %s is %s" % \
          (self.name, self.octave[0]/12))
    
    print("\nFor our last trick, we will return some setting strings to input.")

    ret = []
    ret.append( "print If you have used the -e command line option")
    ret.append( "print you will see that we have changed the octave")
    ret.append( "print and voicing of the track.")
    
    ret.append("%s Octave 6" % name)
    ret.append("%s Voice JazzGuitar" % name)

    # All return values have to be lists of words. Not a string per line!

    ret = [l.split() for l in ret]

    # The next line does the input stream push. Note that we are using
    # the current line number of the file for each line.

    gbl.inpath.push(ret, [gbl.lineno] * len(ret))

def dataRun(ln):
    return ['Gm'] + ln
        
# Entry for usage (mma -Ihello)

def printUsage():    
    print("Usage for the mma hello plugin. ")
    print("Not much to say ... I'm just an example.")

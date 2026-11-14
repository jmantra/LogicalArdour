# regplug.py

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

# Plugin registration. 
# plugin() is called by the PLUGIN command. It searchs and loads
# the required plugin code and adds them to the command tables in parse.py.

import os
import sys
import importlib
import hashlib
import json
import MMA.debug

from MMA.paths import plugPaths
from MMA.common import *
import MMA.parse
from MMA.alloc import trkClasses
import MMA.appdirs   # not mine, but it works!

# In python3 raw_input() has been renamed input()
if sys.version_info[0] == 3:
    raw_input = input

# Set the name of the entry point module. Each plugin must
# have this module (with a .py ending) in its directory.
# Filename is case-insensitive
entry = "plugin"

# This is prepended to the module name to make it unique
# as a command name. The module "foo.py" becomes the command
# "@foo"
prefix = "@"

# these are for the macro funcs and for debug.
plugList = []      # all loaded plugins
simplePlugs = []   # simple funcs registered
trackPlugs = []    # track funcs registered
dataPlugs = []     # data plugs registered

# A list of entry points for the command line help
# function. Each plugin should have a function printUsage().
# If this function is found, we add it. The -I <plugin>
# command line switch will call/display it.
plugHelp = {}

# Security permission file of accepted plugins.
# The path/file is set in getPermission() function if needed.
permFile = None

# This can be set to TRUE from the cmd line with -II
# If set the security file is ignored.
secOverRide=False

# For security we disable various load paths. These can
# disabled via the Plugin Disable=... command. They can
# not be enabled!
tryLocal = True     # from the same dir as the current file
tryDot = True       # from the users current dir
tryPlugDir = True   # from the plugin directory
plugsOff = False    # disable plug loading completely

def findPlugin(targ):
    """ Search for the plugin. 

        p - the plugin name (eg. hello)

        We search, in order, the following paths for the file hello/plugin.py
    
           - the users current directory
           - the directory in which the current file being processed lives
           - the plugin directories.

           The search is case-insensitive.

        Returns - complete path to the directory containing "hello/plugin.py",
                  and the module name (hello.plugin).
    """

    plugEntry = "%s.%s" % (entry, 'py')
    
    def matchName(d):
        """ Find a directory entry in 'd' matching the plugin name """

        if os.access(d, os.R_OK):  # skip non-exist dirs and ones we can't access
            if [b.upper() for b in os.listdir(d)].count(targ) > 1:
                warning("Plugin: there are duplicate entries of '%s' in '%s'. This "
                   "is most likly due to the same name with different cases. You "
                   "should check and delete/rename one!" % (targ, d))

            for a in os.listdir(d):
                if a.lower() == targ.lower():
                    for b in os.listdir(os.path.join(d, a)):
                        if b.lower() == plugEntry.lower():
                            # Create a module name based on the case of the files found
                            mName = "%s.%s" % (a, b[0:-3])
                            return os.path.join(a, b), mName

        return None, None

    # 1. Current dir. If found convert to complete path
    if tryDot:
        for dir in ('.', 'plugins'):
            mdir, modName = matchName(dir)
            if mdir:
                return os.path.realpath(dir), mdir, modName

    # 2. Check for the plugin in the same directory as the current
    #    file being processed ... the current file could be a library file.
    if tryLocal:
        if gbl.inpath:
            n = gbl.inpath.fname
            path = os.path.dirname(gbl.inpath.fname)
            # if path is None then we're in '.' and we've done that in (1)
            if path:
                mdir, modName = matchName(path)
                if mdir:
                    return os.path.realpath(path), mdir, modName

    # 3. The plugin directory (mmapath/plugins)
    if tryPlugDir:
        for p in MMA.paths.plugPaths:
            mdir, modName = matchName(p)
            if mdir:
                return p, mdir, modName

    return None, None, None

def hashfile(p):
    """ Calculate a sha-256 hash value on a file. """

    sha256 = hashlib.sha256(b'mmaIsWonderful')

    try:
        f = open(p, 'rb')
    except:
        error("Plugin: Cannot open file '%s'." % p)

    try:
        sha256.update(f.read())
    except:
        error("Plugin: Cannot calculate hash value for plugin file.")
    finally:
        f.close()

    return sha256.hexdigest()

def getPermission(path, name):
    """ Check the file for plugin permissions."""

    global permFile

    if secOverRide:
        return

    # We need somewhere to store this registery. appdirs to the rescue!
    if not permFile:
        cachePath = errorName = MMA.appdirs.user_data_dir('mma', 'Mellowood')
        
        # Can we access the directory? If not, we first try to create
        # a mma directory (we're assuming that HOME/.config, HOME/.local/config,
        # or MMA/lib already exists.
        try:
            os.makedirs(cachePath)
        except OSError:
            if not os.path.isdir(cachePath):
                cachePath = None  # couldn't create directory, that's okay

        if not cachePath:
            warning("Plugin: Can't create/access directory to store permission cache"
                    " file at '%s'. You can still run the plugin, but permissions"
                    " won't be saved." % errorName)

        # We should have a complete path to our storage file.
        if cachePath:
            permFile = os.path.join(cachePath, 'plugins.list')
        else:
            permFile = None

    sha = hashfile(path)
    permlist = {}

    # This is done for each PLUGIN call. Not a big deal, but could be optimized.
    if permFile:
        try:
            f = open(permFile, 'r')
            f.readline()    # Read/discard comment line
            permlist = json.load(f)
            f.close()
        except:
            permlist = {}  # files doesn't exist or can't be read. Ignore.

    # we have a valid permlist dictionary (or an empty one) in memory.
    # if the entries match, all's well

    if path in permlist and  permlist[path] == sha:
        return 

    prettyPrint("PLUGIN: This file is attempting to load the plugin '%s'."
                " As detailed in the documentation a plugin can run arbitrary"
                " Python code and can be dangerous to your system."
                " If you don't understand this, DO NOT"
                " accept loading this plugin!"
                " If you are sure you want to grant permission to load this plugin"
                " press the <y> key followed by <Enter> to register; <o><Enter>"
                " to permit running only once. Any other key combination"
                " will terminate this run." % name)
    a = raw_input("       Your choice: ")

    # Just return. Don't bother to update the permissions table
    if a == 'o':
        return

    # Abort
    if a != 'y':
        error("Plugin: permission refused for loading plugin.")

    # update our permissions dictionary and save it for the next run.

    if permFile:
        permlist[path] = sha
        try:
            f = open(permFile, 'w')
            f.write("### MMA plugin permissions. DO NOT EDIT ###\n")
            json.dump(permlist, f)
            f.close()
        except:
            warning("Plugin: Could not access/create file '%s'. Plugin permission has"
                    " not been saved. You probably have a"
                    " permissions problem on this system." % permFile)

def registerPlugin(p):
    """ Search for the plugin and register any found methods. """

    if p.startswith(prefix):  # user has option to use 
        p = p[1:]

    pdir, mdir, modName = findPlugin(p.upper())

    # pdir - complete path to plug container
    # mdir - path from pdir to the plug. (hello/plugin.py)
    # modName - name for module load (hello.plugin)

    if not pdir:
        error("Plugin: Cannot find a path to %s" % p)

    if modName in plugList:
        warning("Plugin '%s' attempted reload ignored." % modName)
        return

    initMod = os.path.join(pdir, os.path.split(mdir)[0],  "__init__.py")
    if not os.path.exists(initMod):
        error("Plugin needs an empty file '%s'." % initMod)

    if os.stat(initMod).st_size > 0:
        error("Plugin '__init__.py' module must be empty (security concern).")

    plugPath = os.path.join(pdir,mdir)
    plugName =  modName.split('.')[0]

    getPermission(plugPath, plugName)

    plugList.append(modName)
    # insert our plugin path to sys.path so that python's load
    # module function will find our plugs.
    sys.path.insert(0, pdir)

    # load the module. 
    if plugName in sys.modules.keys():
        error("Plugin: the name of the '%s' is already is use by the system. "
              "Most likely MMA has already imported a module by that name. "
              "Please rename the package!" % plugName)
    try:
        e = importlib.import_module(modName, package=None)
    except ImportError as err:
        error("Plugin: Error loading module '%s'. Python is reporting '%s'. "
              "Most likely there is an Import statement in the module which is not working." %
              (modName, str(err)))
        
    # restore old sys.path.
    sys.path.pop(0)

    # The module is now in memory.
    # Find and register the entry points.

    cmdName = prefix + p.upper()

    e.plugInName = {'name': plugName,
                    'dir':  pdir,
                    'path': plugPath,
                    'cmd':  cmdName   }

    try:
        MMA.parse.simpleFuncs[cmdName] = e.run
        simplePlugs.append(cmdName)
        if MMA.debug.debug:
            dPrint("Plugin: %s simple plugin RUN registered." % cmdName.title())
    except:
        pass
    
    try:
        MMA.parse.trackFuncs[cmdName] = e.trackRun
        trackPlugs.append(cmdName)
        if MMA.debug.debug:
            dPrint("Plugin: %s track plugin TrackRun registered." % cmdName.title())
    except:
        pass
    
    try:
        MMA.parse.dataFuncs[cmdName] = e.dataRun
        dataPlugs.append(cmdName)
        if MMA.debug.debug:
            dPrint("Plugin: %s data plugin DataRun registered." % cmdName.title())
    except:
        pass
    
    try:
        plugHelp[cmdName] = e.printUsage
    except:
        plugHelp[cmdName] = None

    return cmdName


def pluginHelp(p):
    """ Called from options to print help message. This is called
        ONLY from the MMA command line ... so no plugs have been
        loaded. We attempt to find the plug, then call its help.
    """

    cmd = registerPlugin(p)

    try:
        plugHelp[cmd]()
    except:
        print("No help message registered for '%s'." % cmd)


def plugin(ln):
    """ Search for, load and install requested plugin(s) """

    global plugsOff, tryLocal, tryDot, tryPlugDir

    if plugsOff:
        error("Plugin loading has been disabled.")

    if not ln:
        error("Plugin requires at least one argument (plugin name).")

    ln, optpair = opt2pair(ln, toupper=True)  # get options
    for cmd, opt in optpair:
        if cmd == 'DISABLE':
            for o in opt.split(','):
                a = o.upper()
                if a == 'ALL':
                    plugsOff = True
                elif a  == 'LOCAL':
                    tryLocal = False
                elif a == 'DOT':
                    tryDot = False
                elif a == 'PLUGDIR':
                    tryPlugDir = False
                else:
                    error("Plugin Disable: '%s' is an unknown or illegal option." % o)

            if MMA.debug.debug:
                if plugsOff:
                    dPrint("Plugin: loading disabled.")
                else:
                    if not tryLocal:
                        dPrint("Plugin: no local plug loading.")
                    if not tryDot:
                        dPrint("Plugin: no current directory plug loading.")
                    if not tryPlugDir:
                        dPrint("Plugin: no plugin directory plug loading.")
        else:
            error("Plugin: '%s' is an unknown command." % cmd)

    # Now load the plugins requested. Note, the args are all in
    # uppercase, but that doesn't matter since the find
    # function checks all possibilities.

    for p in ln:
        registerPlugin(p)



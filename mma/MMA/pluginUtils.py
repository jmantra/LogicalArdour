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
# # MMA plugin utilities            #
# #                                 #
# # written by Ignazio Di Napoli    #
# # <neclepsio@gmail.com>           #
# ###################################

import textwrap, traceback, sys, re
from collections import defaultdict

from MMA.common import error, warning
from MMA.macro import macros
import MMA.gbl as gbl

from MMA.termsize import getTerminalSize
termwidth = getTerminalSize()[0]-1

try:
    basestring
except NameError:
    basestring = str
  

# ###################################
# # Plugin configuration            #
# ###################################

class _pluginInfo (object):
    def __init__(self):
        self.NAME = None
        self.DESCRIPTION = ""
        self.SYNOPSIS = ""
        self.AUTHOR = ""
        self.TRACKTYPES = None
        self.ARGUMENTS = []
        self.DOC = ""
        self.COMMANDS = []
    
_plugins = defaultdict(_pluginInfo)

def _getCallerFileName():
    stackFileNames = [s[0] for s in traceback.extract_stack()]
    myName = stackFileNames[-1]
    for name in stackFileNames[::-1]:
        if name != myName:
            return name
    return None

    
def _getCallerModule():
    f = _getCallerFileName()
    if f is None:
        return None
        
    for module in sys.modules.values():
        if module is None or not hasattr(module, "__file__") or module.__file__ is None:
            continue
        if module.__file__.rpartition(".")[0] != f.rpartition(".")[0]:
            continue
        return module
    
    return None
    
    
def _P():
    f = _getCallerFileName()
    
    # plugInName is not available at module initialization, but is called
    # afterwards. So, we assign it when called later.
    if _plugins[f].NAME is None:
        module = _getCallerModule()
        if module is not None and hasattr(module, "plugInName"):
            _plugins[f].NAME = "@" + module.plugInName['name']

    return _plugins[f]


# A short description.
def setDescription(descr):
    _P().DESCRIPTION = descr

# Synopsis.
def setSynopsis(syno):
    _P().SYNOPSIS = syno

# Author.
def setAuthor(author):
    _P().AUTHOR = author

# Track types to which the plugin applies; if empty everything is accepted.
# If None, this is a non-track plugin.
def setTrackType(*types):
    _P().TRACKTYPES = types[:]

# A list of arguments for the plugin; each is specified with [name, default, doc]. 
# If no default is provided, use None to trigger an error if the user not specifies it.
def addArgument(name, value, doc):
    _P().ARGUMENTS.append((name, value, doc))

# Simple documentation. %NAME% is replaced by plugin name.
def setPluginDoc(doc):
    _P().DOC = doc.strip()
    
# Minimum MMA version required.
def setMinMMAVersion(major, minor):
    vre = re.compile("([0-9]+)\\.([0-9]+)\\.?(.*)")
    m = vre.match(gbl.version)
    if m is None:
        error("Plugin utils: version %s not recognized." % gbl.version)
    cur_major = int(m.group(1))    
    cur_minor = int(m.group(2))    
    cur_rev = m.group(3)
    
    if cur_major > major:
        return
    if cur_major == major and cur_minor >= minor:
        return
    
    error("Plugin requires MMA version {:02}.{:02} or newer.".format(major, minor))

   
# Returns plugin name
def getName():
    return _P().NAME
    
     
    
# ###################################
# # Utility functions               #
# ###################################

# If you don't send all the commands together the result is commands 
# are reversed since each is pushed as the very next command to be executed.
# So we save all the commands (with addCommand) and send them at the end
# (with sendCommands).

def addCommand(strings):
    if isinstance(strings, basestring):
        strings = [strings]
    _P().COMMANDS.extend(strings)

    
def sendCommands():
    # All values have to be lists of words. Not a string per line!
    ret = [l.split() for l in _P().COMMANDS]
    _P().COMMANDS = []
    

    # The next line does the input stream push. Note that we are using
    # the current line number of the file for each line.
    gbl.inpath.push(ret, [gbl.lineno] * len(ret))

    
def parseCommandLine(line, allowUnknown=False):
    s = " ".join(line)
    subst = [
        [" =", "="],
        ["= ", "="],
        ["  ", " "],
        [", ", ","],
        [" ,", ","],
    ]
    for s1, s2 in subst:
        while s1 in s:
            s = s.replace(s1, s2)
    
    res = {name:default for name, default, _ in _P().ARGUMENTS}
    positional = True
    for name, default, _ in _P().ARGUMENTS:
        res[name] = default
        
    for i, value in enumerate(s.split(",")):
        if value == "":
            continue
            
        if "=" in value:
            positional = False
            n, _, v = value.partition("=")
            if n not in res: 
                if not allowUnknown:
                    error("Plugin {}: unexpected argument name {}.".format(_P().NAME, n))
                else:
                    n = n.upper()
                    
        elif positional:
            if i >= len(_P().ARGUMENTS):
                error("Plugin {}: unexpected argument provided ({}).".format(_P().NAME, value))
            n, _, _ = _P().ARGUMENTS[i]
            v = value
            
        else:
            error("Plugin {}: positional argument after named argument is not allowed.".format(_P().NAME))
            
        res[n] = v
    
    for k, v in res.items():
        if v is None:
            printUsage()
            error("Plugin {}: no value for argument {}.".format(_P().NAME, k))
    
    return res
    

def _printUsage(plugin):
    width = termwidth
    
    lines = []
    lines.append((0, "Plugin {}".format(plugin.NAME)))
    if plugin.AUTHOR != "":
        lines.append((0, plugin.AUTHOR))
    lines.append((0, ""))
    if plugin.DESCRIPTION != "":
        lines.append((0, plugin.DESCRIPTION))
        lines.append((0, ""))
    lines.append((0, "SYNOPSIS"))
    if plugin.SYNOPSIS != "":
        for line in plugin.SYNOPSIS.splitlines():
            lines.append((0, line))
        lines.append((0, ""))
    else:
        t = ""
        if plugin.TRACKTYPES is not None:
            t += "Track "
        t += plugin.NAME + " "

        for name, _, _ in plugin.ARGUMENTS:
            t += name + ", " 

        lines.append(([4, 8], t.strip().rstrip(",")))
        lines.append((0, ""))

    if plugin.TRACKTYPES is not None and len(plugin.TRACKTYPES) > 0:
        if len(plugin.TRACKTYPES) == 1:
            lines.append((4, "Track type must be {}.".format(plugin.TRACKTYPES[0])))
        else:
            lines.append((4, "Track type must be one of {}.".format(", ".join(plugin.TRACKTYPES[:-1]) + " or " + plugin.TRACKTYPES[-1])))
        lines.append((0, ""))

    if len(plugin.ARGUMENTS) > 0:
        lines.append((0, "ARGUMENTS"))
        lines.append((0, ""))

        for name, default, doc in plugin.ARGUMENTS:
            defvalue = (" (default: "+default+")" if default is not None else "")
            lines.append((4, name + defvalue))
            lines.append((8, doc))
            lines.append((0, ""))

        lines.append((4, "You can also use name=value syntax, like Call (see MMA documents)."))
        lines.append((0, ""))
        
    lines.append((0, "DESCRIPTION"))
    lines.append((0, ""))
    for l in plugin.DOC.replace("\r", "").replace("%NAME%", plugin.NAME).split("\n"):
        lines.append((4, l))
    
    for indent, line in lines:
        if line.strip() == "":
            print 
        else:
            if isinstance(indent, list):
                firstindent, indent = indent
            else:
                firstindent = indent
            
            llines = textwrap.wrap(line, width-indent)
            for i, lline in enumerate(llines):
                if i == 0 and firstindent != indent:
                    print(" " * firstindent + lline + (" \\" if len(llines) > 1 else ""))
                else:
                    print(" " * indent + lline)

                    
def printUsage():
    _printUsage(_P())
       
    
def checkTrackType(name):
    if _P().TRACKTYPES is None or len(_P().TRACKTYPES) == 0:
        return

    for t in _P().TRACKTYPES:
        if name.upper() == t.upper() or name.upper().startswith(t.upper() + "-"):
            return
    
    if len(_P().TRACKTYPES) == 1:
        error("Plugin {}: track type must be {}.".format(_P().NAME, _P().TRACKTYPES[0]))
    else:
        error("Plugin {}: track type must be one of {}.".format(_P().NAME, ", ".join(_P().TRACKTYPES[:-1]) + " or " + _P().TRACKTYPES[-1]))


def getTrackType(name):
    if "-" in name:
        name = name.split("-")[0]
    return name.upper()
            
error = error
warning = warning

def getVar(name):
    return macros.vars[name]
       
def setVar(name,value):
    macros.vars[name.upper()] = str(value)
       
def getSysVar(name):
    return macros.sysvar(name)
    
    

# func.py

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

Code for Defaults and recursion stack Ignazio Di Napoli.

   Define and execute simple function / subroutine calls.

"""

import copy
from . import gbl
import MMA.file
from MMA.macro import macros
from MMA.common import *
import MMA.debug

# Storage for our functions 
class Funcs:
    def __init__(self, params, body, defaults, fname, lineN):
        self.params = params
        self.body = body
        self.defaults = defaults
        self.lineN = lineN
        self.fname = fname
        
funcList = {}

########################

def defCall(l):
    """ Define a function.  """

    if len(l) < 1:
        error("DefCall: At least one argument (name) is needed.")
        
    lineN = gbl.lineno
        
    # Grab 1st arg. This is the function name
    fname = l[0].strip().upper()
    if '$' in fname:
        error("DefCall: '$' is not permitted in function name.")

    # The params are split into words. Join together just so we can
    # take it apart again. Needed to use ',' delimiters
    # read from the inside out: replace '\,' with chr(255)
    #                           join together with space delims (skip func name)
    #                           split up at ','

    p = ' '.join(l[1:]).replace('\,', chr(255)).split(',')

    # Convert the param names so they have a leading '$'. The '$'
    # is not permitted in a param name.

    params = []
    defaults = []
    for a in p:
        a = a.strip().replace(chr(255), ",")
        if not a:
            continue
        if '=' in a:
            a,d = a.split('=')
            a = a.strip()
            d = d.strip()
        else:
            d = None
        if '$' in a:
            error("DefCall: '$' is not permitted in paramater name.")
        a = '$'+a
        if a in params:
            error("DefCall: '%s' is a duplicate paramater name." % a)

        params.append(a.upper())
        defaults.append(d)
    
    body = []
    while 1:
        ln = gbl.inpath.read()
        if not ln:
            error("DefCall: Reached EOF while looking for EndDefCall.")
        cmd = ln[0].upper()
        if cmd in ("DEFCALLEND", "ENDDEFCALL"):
            if len(ln) > 1:
                error("DefCall: No arguments permitted for DefCallEnd/EndDefCall.")
            else:
                break
        if cmd == "DEFAULT":
            if len(ln) < 2:
                error("Default: Requires at least one argument.")
            a = '$'+ln[1].strip().upper()
            d = ''
            if len(ln) >= 2:
                d = ' '.join(ln[2:])
            try:
                i = params.index(a)
            except:
                error("DefCall Default: param '%s' does not exist in '%s'." % (a, fname))
            if defaults[i]:
                warning("DefCall Default: param '%s' default value '%s' was set in param list."
                        " Overriding with '%s'." % (a, defaults[i], d))
            defaults[i] = d
            continue
            
        body.append(ln)
    
    funcList[fname] = Funcs(params, body, defaults, gbl.inpath.fname, lineN)
    
    if MMA.debug.debug: 
        t = [ a[1:] for a in params]
        dPrint("DefCall: Created function '%s': %s" % (fname, ', '.join(t)))


def callFunction(l):
    """ Call a function. """

    if len(l) < 1:
        error("DefCall: At least one argument (name) is needed.")

    fname = l[0].strip().upper()
    
    if fname not in funcList:
        error("Call: '%s' has not been defined." % fname)

    # Convert any escaped '\,' into $ff ... see explanation in defCall()
    p = ' '.join(l[1:]).replace('\,', chr(255)).split(',')

    # Validate calling params
    params = funcList[fname].params

    callParams = []
    usingDefaults = False
    namedParams = {}
    for a in p:
        a = a.strip().replace(chr(255), ',')   # commas restored
        if a:   # new list of params
            if '=' in a: 
                usingDefaults = True
                a,d = a.split('=')
                a = '$'+a.strip().upper()
                d = d.strip()
                if a not in params:
                    error("Call: '%s' is not a param of '%s'." % (a, fname))
                namedParams[a] = d
            elif usingDefaults:
                error("Call: cannot use a non-named param after a named one.")
            else:
                callParams.append(a)
                
    if usingDefaults or len(params) != len(callParams):
        s = len(callParams)
        for i, p in enumerate(params[s:]):
            if p in namedParams:
                callParams.append(namedParams[p])
            else:
                d = funcList[fname].defaults[i+s]
                if d is None:
                    #error("Call: '%s' has no default for '%s'." % (fname, p))
                    d="UNDEFINED"
                callParams.append(d)

    if len(params) != len(callParams):
           error("Call: Function '%s' needs %s params, '%s' given." % \
                 (fname, len(params), len(callParams)))

    # First, push the current values on the stack.
    # To avoid pushing not existant values, NewSet is called before pushing.
    # Then, set parameters as global values.
    # At the end of the function, stack values are restored.
    # 
    # This way, the parameters become local.  


    existingParams = [name for name in params if name[1:] in macros.vars]
    pushStack = [["StackValue", name] for name in existingParams]
    sets = [["Set", name[1:], value] for name, value in zip(params, callParams)]
    body = funcList[fname].body
    popStack = [["Set", name[1:], "$_StackValue"] for name in existingParams[::-1]]
    unset = [["UnSet", name[1:]] for name in params if name[1:] not in macros.vars]

    fullbody = pushStack + sets + body + popStack + unset
  
    # we use the source line for each, but:
    # - there is no stack for error displaying; error just display current line in input
    # - there is no saving of original file name 
     
    #lineNs = [funcList[fname].lineN] * (len(newSets) + len(pushStack) + len(sets))
    #lineNs += range(funcList[fname].lineN+1, funcList[fname].lineN+1+len(funcList[fname].body))
    #lineNs += [lineNs[-1]+1] * len(popStack)
    ##print zip(lineNs, fullbody)
    #lineNsS = ["{} ({}:{})".format(gbl.lineno, funcList[fname].fname, l) for l in lineNs]
    #gbl.inpath.push(fullbody, lineNsS) 

    # push the converted body lines into the input stream
    gbl.inpath.push(fullbody, [gbl.lineno] * len(fullbody)) 

    #print "=" * 80
    #print fname
    #print zip(params, callParams)
    #print body
    #print "=" * 80

    if MMA.debug.debug:
        dPrint ("Call: function '%s' expanded." % fname)



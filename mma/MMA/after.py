# after.py

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

After storage, setting and command insertion.

"""
import tempfile
import os

from . import gbl
from MMA.common import *
import MMA.debug

class AfterData:
    def __init__(self):
        self.bar = None        # calculated to a tickoffset
        self.cmd = None        # what to do
        self.repeat = None     # number of times to do this
        self.count = None      # number of bars to wait before doing
        self.lineno = -1       # done in init. Used to set line in pushback
        self.id = None         # a name used by the remove function
        self.finished = False  # flag. If true this event is done
        
afterData = []          # stack of after events
afterDataFinished = 0   # counter of dead events

def create(ln):
    """ Set an After event. """

    global afterData, afterDataFinished 

    dat = AfterData()
    selected = []

    ln, opts = opt2pair(ln, toupper=False, notoptstop=True)
    for cmd, opt in opts:
        cmd = cmd.upper()
        if cmd == 'BAR':
            if opt.upper() == 'EOF':
                dat.bar = 'EOF'
            else:
                opt = stoi(opt)
                if opt < 1:
                    error("After: Destination bar must be positive, not '%s'." % opt)
                    dat.bar = opt
            selected.append('Bar')
                
        elif cmd == 'REPEAT':
            opt = stoi(opt)
            if opt < 1:
                error("After: Repeat value must be positive, not '%s'." % opt)
            dat.repeat = opt
            dat.bar = opt + gbl.barNum 
            selected.append('Repeat')

        elif cmd == 'COUNT':
            opt = stoi(opt)
            if opt < 1:
                error("After: Count must be positive, not '%s'." % opt)
            dat.count = opt
            dat.bar = opt + gbl.barNum 
            selected.append('Count')

        elif cmd == 'ID':         # set a string id for this event. 
            dat.id = opt.upper()  # duplicates are fine

        elif cmd == 'REMOVE':  # delete all saved items with id==opt.
            t = False
            for a in afterData:
                if not a.finished and a.id == opt.upper():
                    a.finished = True
                    afterDataFinished += 1
                    t = True

            if len(opts) > 1 or ln:
                warning("After: Remove is ignoring other options/cmds in line.")
            if not t:
                warning("After: No events with ID=%s found to delete." % opt)
            return   # ignore any other commands

        else:
            error("After: Unknown option '%s'." % cmd)


    if not ln:
        error("After: No command given. It's needed.")

    if len(selected) == 0:
        error("After: need one of 'Count', 'Bar', or 'Repeat'. "
              "Options must be listed before the command!")

    if len(selected) > 1:
        error("After: Options conflict; can't combine %s." % ' & '.join(selected))

    dat.cmd  = ln
    dat.lineno = gbl.lineno

    if dat.bar == 'EOF':
         gbl.inpath.pushEOFline(dat.cmd)
    else:
        afterData.append(dat)  # our stack (actually a list of events)

    if MMA.debug.debug:
        dPrint("After: Added event '%s' at bar %s." % (' '.join(dat.cmd), dat.bar))

        
def check(recurse=False):
    """ Before reading any input, we check to see if any AFTER events have been
        created and if we need to process them now. Called from parse loop.
    """

    global afterData, afterDataFinished
    if not needed():   # do a fast stack scan, and (maybe) clean the stack
        return
    
    # Gather all the AFTER events for this point
    # in the MMA file for pushback
    
    stuff = []  # MMA commands
    elns = []   # and line numbers
    
    for dat in afterData:
        if not dat.finished and dat.bar == gbl.barNum:
            stuff.append(dat.cmd)
            elns.append(dat.lineno)
            
            # while going though the list of AFTER events
            # mark any ones that need to be repeated for
            # a future point
            if dat.repeat:
                dat.bar = gbl.barNum + dat.repeat
            else:
                dat.finished = True
                afterDataFinished =+ 1

    if stuff:
        if recurse:
            # note: we can't use tempfile.TemporaryFile 'cause
            # parse.parseFile() needs a filename. Don't think of
            # using stdin (1) since we might cobber existing reader.
            _, name = tempfile.mkstemp(prefix="MMA_", suffix=".mma")
            try:
                fd = open(name, 'w')
            except:
                error("Trigger: Could not open temporary scratch file "
                      "for recursion in repeat (*) section.")
            for a in stuff:
                fd.write( "%s\n" % ' '.join(a))
            fd.close()
            MMA.parse.parseFile(name)
            try:
                os.remove(name)
            except:
                pass

        else:
            # Push our AFTER command to input.
            gbl.inpath.push(stuff, elns)



def needed():
    """ Check to see if it's time to handle an After. There can be
        several different Afters on the same bar, this returns on
        the first positive. Only called from the parse loop if we
        are recursing (a * repeat).

        Returns True/False
    """

    global afterData, afterDataFinished

    # before doing the check, let's clean up our stack.
    if afterDataFinished > 40 and afterDataFinished-1 > len(afterData)/2:
        afterData = [ x for x in afterData if not x.finished ]
        afterDataFinished = 0

    # the actual check ... need to check each stacked event
    # we exit on the first needy one found
    for dat in afterData:
#        print(dat.finished, dat.bar, gbl.barNum)
        if not dat.finished and dat.bar == gbl.barNum:
            return True
        
    return False

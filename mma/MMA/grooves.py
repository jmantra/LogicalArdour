# grooves.py


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


""" Groove storage. Each entry in glist{} has a keyname
    of a saved groove.

    lastGroove and currentGroove are used by macros
"""

import MMA.midi
import MMA.notelen
import MMA.auto
import MMA.volume
import MMA.parse
import MMA.parseCL
import MMA.seqrnd
import MMA.docs
import MMA.debug

from MMA.timesig import timeSig
from . import gbl
from   MMA.common import *


glist = {}
aliaslist = {}

lastGroove = ''     # name of the last groove (used by macros)
currentGroove = ''     # name of current groove (used by macros)

COPYGROOVE = -2387      # fake groove name used by copytrack

""" groovesList[] holds a list of grooves to use when the
     groove command is used with several args. ie, when
     we use either:

         Groove 2  groove1  groove2 groove3
     or
         Groove groove1 groove2 groove3

     in both cases, the names of the grooves are stored in groovesList[]
"""

groovesList = None
groovesCount = 0


class STACKGROOVE():
    """ A little stacker for temporary grooves. """

    def __init__(self):
        self.stack = []   # set of integers used as groove names

    def push(self):
        s = self.stack
        s.append(len(s))
        grooveDefineDo(s[-1])

    def pop(self):
        s = self.stack
        if not s:
            error("Groove stacking error. Call Bob.")
        grooveDo(s.pop())

stackGroove = STACKGROOVE()   # single (only) instance


def grooveDefine(ln):
    """ Define a groove.

        Current settings are assigned to a groove name.
    """

    if not len(ln):
        error("Use: DefGroove  Name")

    slot = ln[0].upper()

    # Slot names can't contain a '/' or ':'

    if '/' in slot:
        error("The '/' is not permitted in a groove name.")

    if ':' in slot:
        error("The ':' is not permitted in a groove name.")

    if slot in aliaslist:
        error("Can't define groove name %s, already defined as an alias for %s." \
                  % (slot, aliaslist[slot]))

    if MMA.debug.gvShow and slot in glist:
        dPrint("Redefining groove %s, line %s." % (slot, gbl.lineno))

    grooveDefineDo(slot)

    if MMA.debug.debug:
        dPrint("Groove settings saved to '%s'." % slot)

    if gbl.makeGrvDefs:   # doing a database update ...
        MMA.auto.updateGrooveList(slot)

    if len(ln) > 1:
        MMA.docs.docDefine(ln)


def grooveDefineDo(slot):

    for n in gbl.tnames.values():
        if n.sticky:
            continue
        n.saveGroove(slot)

    glist[slot] = {
        'SEQSIZE':   gbl.seqSize,
        'SEQRNDWT':  MMA.seqrnd.seqRndWeight[:],
        'QPERBAR':   gbl.QperBar,
        'BARLEN':    gbl.barLen,
        'SEQRND':    MMA.seqrnd.seqRnd[:],
        'TIMESIG':   timeSig.get(),
        'SWINGMODE': MMA.swing.gsettings(),
        'VRATIO':    (MMA.volume.vTRatio, MMA.volume.vMRatio),
        'CTABS':     MMA.parseCL.chordTabs[:] }


def grooveAlias(ln):
    """ Create an alias name for an existing groove. Note: not a copy. """

    global aliaslist

    if len(ln) != 2:
        error("DefAlias needs exactly 2 args: GrooveName AliasName.")

    g = ln[0].upper()
    a = ln[1].upper()

    if not g in glist:
        error("DefAlias: Groove %s has not been defined." % ln[0])

    aliaslist[a] = g


def groove(ln):
    """ Select a previously defined groove. """

    global groovesList, groovesCount, lastGroove, currentGroove

    if not ln:
        error("Groove: needs agrument(s)")

    tmpList = []

    if ln[0].isdigit():
        wh = stoi(ln[0])
        if wh < 1:
            error("Groove selection must be > 0, not '%s'" % wh)
        ln = ln[1:]
    else:
        wh = None

    for slot in ln:
        slotOrig = slot   # we need this for search
        slot = slot.upper()

        if slot == "/":
            if len(tmpList):
                slot = tmpList[-1]
            else:
                error("A previous groove name is needed before a '/'")

        # convert alias to real groove name
        if not slot in glist and slot in aliaslist:
                slot = aliaslist[slot]
        
        if not slot in glist:
            if MMA.debug.debug:
                dPrint("Groove '%s' not defined. Trying auto-load from libraries" 
                      % slot)

            l, slot = MMA.auto.findGroove(slotOrig)    # name of the lib file with groove

            if l:
                if MMA.debug.debug:
                    dPrint("Attempting to load groove '%s' from '%s'." % (slot, l))

                reportFutureVols()
                MMA.parse.usefile([l])

                if not slot in glist:
                    error("Groove '%s' not found. Is the groove in the file '%s'? "
                          "Have libraries changed "
                          "since last 'mma -g' run?" % (slot, l))

            else:
                error("Groove '%s' could not be found in memory or library files" % slot )

        tmpList.append(slot)

    if not len(tmpList):
        error("Use: Groove [selection] Name [...]")

    ## If the first arg to list was an int() (ie: 3 groove1 groove2 grooveFoo)
    ## we select from the list. After the selection, we reset the list to be
    ## just the selected entry. This was, if there are multiple groove names
    ## without a leading int() we process the list as groove list changing
    ## with each bar.

    if wh:
        wh = (wh-1) % len(tmpList)
        tmpList = tmpList[wh:wh+1]

    slot = tmpList[0]
    grooveDo(slot)

    groovesCount = 0
    if len(tmpList) == 1:
        groovesList = None
    else:
        groovesList = tmpList

    lastGroove = currentGroove
    currentGroove = slot
    if lastGroove == '':
        lastGroove = slot

    if MMA.debug.debug:
        dPrint("Groove settings restored from '%s'." % slot)


def grooveDo(slot):
    """ This is separate from groove() which parses the command line,
        does a lib search, etc. This just copies data from an existing
        in-memory groove.
    """

    reportFutureVols()

    oldSeqSize = gbl.seqSize

    g = glist[slot]

    gbl.seqSize = g['SEQSIZE']
    MMA.seqrnd.seqRndWeight = g['SEQRNDWT']
    gbl.QperBar = g['QPERBAR']
    gbl.barLen  = g['BARLEN']
    MMA.seqrnd.seqRnd = g['SEQRND']
    timeSig.create(*g['TIMESIG'])  # passing tuple as 2 args.
    MMA.swing.grestore(g['SWINGMODE'])
    MMA.volume.vTRatio, MMA.volume.vMRatio = g['VRATIO']
    MMA.parseCL.chordTabs = g['CTABS']

    for n in gbl.tnames.values():
        if n.sticky:
            continue
        n.restoreGroove(slot)

    ## This is important! Tracks NOT overwritten by saved grooves may
    ## have the wrong sequence length. I don't see any easy way to hit
    ## just the unchanged/unrestored tracks so we do them all.
    ## Only done if a change in seqsize ... doesn't take long to be safe.

    if oldSeqSize != gbl.seqSize:
        for a in gbl.tnames.values():
            a.setSeqSize()

    MMA.seqrnd.seqRndWeight = seqBump(MMA.seqrnd.seqRndWeight)

    gbl.seqCount = 0


def reportFutureVols():
    """ Print warning for pending track cresendos.

        We need a seperate func here since the groove() may
        parse a new file, which will clear out data before
        getting to grooveDo().

        Note that the test is for more that one trailing future volume.
        This is deliberate ... a construct like:

           Chord Cresc ff 1
           ..somechord
           Groove NEW

        will leave a future volume on the stack.
    """

    volerrs = []
    for n in gbl.tnames.values():
        if n.vtype in ("SOLO", "ARIA"):  # not saved in grooves
            continue
        if len(n.futureVols) > 1:
            volerrs.append(n.name)
        n.futureVols = []     # don't want leftover future vols a track level!

    if volerrs:
        volerrs.sort()
        warning("Pending (de)Cresc in %s." % ', '.join(volerrs))


def grooveClear(ln):
    """ Delete all previously loaded grooves from memory. """

    global groovesList, groovesCount, glist, lastGroove, currentGroove, aliaslist

    if ln:
        error("GrooveClear does not have any arguments.")

    groovesList = {}
    aliaslist = {}
    groovesCount = 0
    tmplist = {}

    # we first save all the temp grooves (for include, etc) into a glist replacement

    for a in glist:
        if isinstance(a, int):     # is groove name is an integer, not string
            tmplist[a] = glist[a]  # yes, stacked groove, save

    # now just point glist to the copy. Normally created grooves are gone.

    glist = tmplist

    lastGroove = ''
    currentGroove = ''

    if MMA.debug.debug:
        dPrint("All grooves deleted.")


def nextGroove():
    """ Handle groove lists. Called from parse().

        If there is more than 1 entry in the groove list,
        advance (circle). We don't have to qualify grooves
        since they were verified when this list was created.
        groovesList is None if there is only one groove (or none).
    """

    global lastGroove, currentGroove, groovesCount

    if groovesList:
        groovesCount += 1
        if groovesCount > len(groovesList)-1:
            groovesCount = 0
        slot = groovesList[groovesCount]

        if slot != currentGroove:
            grooveDo(slot)

            lastGroove = currentGroove
            currentGroove = slot

            if MMA.debug.debug:
                dPrint("Groove (list) setting restored from '%s'." % slot)


def trackGroove(name, ln):
    """ Select a previously defined groove for a single track. """

    if len(ln) != 1:
        error("Use: %s Groove Name" % name)

    slot = ln[0].upper()

    # convert alias to real groove name
    if not slot in glist and slot in aliaslist:
        slot = aliaslist[slot]
            

    if not slot in glist:
        error("Groove '%s' not defined" % slot)

    g = gbl.tnames[name]
    g.restoreGroove(slot)

    if g.sequence == [None] * len(g.sequence):
        warning("'%s' Track Groove has no sequence. Track name error?" % name)

    if MMA.debug.debug:
        dPrint("%s Groove settings restored from '%s'." % (name, slot))


def getAlias(al):
    """ This is used by the library doc printer to get a list aliases. """

    al = al.upper()
    l = []

    for a in aliaslist:
        if aliaslist[a] == al:
            l.append(a.title())
  
    return ', '.join(l)


def allgrooves(ln):
    """ Apply a command to all currently defined grooves. """

    if not ln:
        error("AllGrooves: requires arguments.")

    noWarn = False
    verbose = False
    skip = []
    only = []
    
    stackGroove.push()  # save the current groove into a temp slot

    # Parse off options (nowarn, skip, only)
    # We need to differentiate between AllGroove options and Groove options
    # so we force AllGroove options to be at beginning.

    ln, opt = opt2pair(ln, toupper=True, notoptstop=True)
    if opt:
        for o, v in opt:

            # Disable the warning messages ... use with caution.
            # NOTE: we don't bother checking for FALSE
            if o == 'NOWARN':
                if getTF(v) == True:
                    startNoWarn = MMA.debug.noWarn
                    MMA.debug.noWarn = 1
                    noWarn = True

            elif o == 'VERBOSE':   # report which affected
                verbose = getTF(v)

            # Restrict to listed grooves
            elif o == 'ONLY':
                if not v in glist:
                    error("AllGrooves ONLY: The groove '%s' does not exist." % v)
                only.append(v)

            # Skip over listed grooves
            elif o == 'SKIP':
                if not v in glist:
                    error("AllGrooves SKIP: The groove '%s' does not exist." % v)
                skip.append(v)

            else:
                error("AllGrooves does not have a %s option." % o)

    if skip and only:
        error("AllGrooves can not have both ONLY and SKIP options.")
        
    action = ln[0].upper()   # either a command or a trackname
    if len(ln) > 1:
        trAction = ln[1].upper()
    else:
        trAction = ''

    sfuncs = MMA.parse.simpleFuncs
    tfuncs = MMA.parse.trackFuncs
    seqwarning = 0

    counter = 0

    # Set warning level to off. This is done since simple things like:
    #     SomeTrack  Volume m mf mp p
    # will spew error messages because all the grooves in memory might
    # have different seqsize values.

    gbl.inAllGrooves = True

    for g in glist:   # do command for each groove in memory
        if skip and g in skip:
            continue
        if only and g not in only:
            continue

        if verbose:
            print("AllGrooves: Modifying '%s'." % g)
            
        grooveDo(g)   # activate the groove

        if action in sfuncs:        # test for non-track command and exe.
            if action in ('GROOVE', 'DEFGROOVE', 'ALLGROOVES', 'ALLTRACKS'
                          'BEATADJUST', 'GROOVECLEAR'):
                error("AllGrooves: '%s' cannot be applied like this." % action)

            sfuncs[action](ln[1:])  # do the command
            counter += 1

        else:                       # see if this is a track command
            if not trAction:
                error("AllGrooves: No command for assumed trackname %s." % action)

            name = action  # remember 'action' is ln[0]. Using 'name' just makes it clearer

            if not name in gbl.tnames:  # skip command if track doesn't exist
                continue

            if trAction in tfuncs:
                if trAction == 'SEQUENCE' and not seqwarning:
                    warning("AllGrooves: Setting SEQUENCE on all grooves is probably a bad idea.")
                    seqwarning = 1   # we only print the warning once

                tfuncs[trAction](name, ln[2:])
                counter += 1

            else:
                error ("AllGrooves: Not a command: '%s'" % ' '.join(ln))

        grooveDefineDo(g)       # store the change!!!

    stackGroove.pop()       # restore original state

    gbl.inAllGrooves = False

    if noWarn:
        MMA.debug.noWarn = startNoWarn
        
    if not counter:
        warning("No tracks affected with '%s'" % ' '.join(ln))

    else:
        if MMA.debug.debug:
            dPrint("AllGrooves: %s tracks modified." % counter)


###################################################################

def trackCopy(name, ln):
    """ Copy/Duplicate all track data to/from existing track. """

    if ln and ln[0].upper() == 'TO':    # arg flipper
        src = name

        for dest in ln[1:]:
            dest = dest.upper()  # Destination is 1st arg
            MMA.alloc.trackAlloc(dest, 1) # create dest if it doesn't exist
            trackCopyDo(dest, [src])

    elif ln and ln[0].upper() == 'FROM':   # optional 'from' keyword
        ln = ln[1:]
        if len(ln) != 1:
            error("Copy FROM %s: Exactly one arg needed (track to copy)." % name)
        trackCopyDo(name, ln)

    else:
        trackCopyDo(name, ln)
        
def trackCopyDo(name, ln):
    """ Copy/Duplicate all track data from existing track.  """

    if len(ln) != 1:
        error("Copy %s: Exactly one arg needed (track to copy)." % name)
    cp = ln[0].upper()

    self = gbl.tnames[name]

    # Split the track-to-copy into a trackname and groovename

    if '::' in cp:
        gr, cp = cp.split('::', 1)
    else:
        gr = ''

    # Find/load the needed groove.
    if gr:
        otime = gbl.QperBar
        stackGroove.push()
        groove([gr.split(':', 1)[0]])              
        if otime != gbl.QperBar:
            error("Copy %s: TIME mismatch, groove %s has time of %s, not %s." %
                  (name, gr, gbl.QperBar, otime))
        
    if not cp in gbl.tnames:
        error("Copy %s: Track '%s' is not defined." % (name, cp))

    cp = gbl.tnames[cp]   # point to the track object

    if cp.vtype != self.vtype:
        error("Copy %s: tracks must be of same type, not %s and %s."
              % (name, self.vtype, cp.vtype))

    # Push the track to copy into a buffer. Use saveGroove for this.
    # Note that solo tracks have a special function since they normally
    # do note save groove info.
    if cp.vtype == 'SOLO':
        if gr:
            error("Copy %s: Solo tracks cannot be copied from a groove, only from memory."
                  % name)
        cp.forceSaveGroove(COPYGROOVE)
    else:
        cp.saveGroove(COPYGROOVE)

    # We need this indirection. The restore function takes
    # a groove buffer name, not a buffer. So it's either rewrite
    # the function or create a scratch name which makes it happy.
    # And it's cheap to do ... no data is copied here.
    self.grooves[COPYGROOVE] = cp.grooves[COPYGROOVE]

    # If we loaded a groove, restore to the original state.
    if gr:
        stackGroove.pop()

    # Now copy the buffered data into the target track.
    if cp.vtype == 'SOLO':
        self.forceRestoreGroove(COPYGROOVE)
    else:
        self.restoreGroove(COPYGROOVE)

    if MMA.debug.debug:
        dPrint("Copy: Settings duplicated from %s to %s" % (cp.name, self.name))

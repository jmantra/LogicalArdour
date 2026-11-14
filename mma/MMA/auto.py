
# auto.py

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


import os
import sys
import pickle

import MMA.midi
import MMA.parse
import MMA.grooves
import MMA.swing

import MMA.paths

from . import gbl
from MMA.common import *

grooveDB = []        # when filled in it becomes [['dir', dict-db], ..]
mmadir = ".mmaDB"   # constant, name of the lib database file
mkGrooveList = []    # a list of grooves defined in current file


def updateGrooveList(n):
    """ Called from parse when new grooves are defined in a -g. """

    global mkGrooveList

    mkGrooveList.append(n)


def libUpdate():
    """ Update the mma library database file(s) with -g or -G option.

        This is called from the main program after the initialization
        and other option parsing. No RETURN.
    """

    global grooveDB, mkGrooveList

    processedFiles = []
    dupMessage = []
    grooveCount = 0
    fileCount = 0
    noAccess = 0

    print( "Creating MMA groove directory database(s). Standby..." )

    """ MMA.paths.libDirs contains a complete list of all the directories in
        the libPath; we create a .mmaDB file for each one.
    """

    if not MMA.paths.libDirs:
        MMA.paths.expandLib()
    for lib in MMA.paths.libDirs:

        gdDate = None
        grooveDB = [[lib, {}]]

        # load up our database with this directory's DB file, skip if -G

        if gbl.makeGrvDefs == 1:
            g = loadDB(lib)
            if g:
                grooveDB = [[lib, g]]
                gdDate = os.path.getmtime(os.path.join(lib, mmadir))

        # -G
        # If the database is really screwed up it's possible to
        # have old links not deleted. Easy way is to completely
        # delete each .mmaDB file as we progress. If we can't delete
        # it,it's probably due to a permission error. So, just dump out.

        elif gbl.makeGrvDefs == 2:
            file = os.path.join(lib, mmadir)
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    error("Unable to delete existing database file '%s'. Are you root?" \
                            % file)

        db = grooveDB[0][1]

        print("     Processing library directory '%s'." % lib)

        """ Get a list of the files in this directory. If the list
            includes a file called 'MMAIGNORE' the entire directory
            is ignored. Otherwise, each file in the
            directory ending in 'mma' is parsed for groove defs.
        """

        dirfiles = os.listdir(lib)
    
        if "MMAIGNORE" in dirfiles:
            print("Skipping: %s" % p)
            return

        for fn in sorted(dirfiles):  # sort is just to pretty up console display

            # Ignore hidden files, emacs auto-save and non-mma files

            if fn.startswith('.') or fn.startswith('#') or not fn.endswith(gbl.EXT):
                continue

            f = os.path.join(lib, fn)      # Create full path name
            processedFiles.append(f)     # a list of ALL processed (complete paths)

            if gdDate and f in db and os.path.getmtime(f) < gdDate:
                print("        Skipped: %s" % f )
                grooveCount += len(db[f])
                continue

            if f in db:
                print("       Updating: %s" % f)
            else:
                print("       Creating: %s" % f)

            mkGrooveList = []
            MMA.grooves.grooveClear([])
            gbl.mtrks = {}
            MMA.swing.mode = 0
            for c in gbl.midiAssigns.keys():
                gbl.midiAssigns[c] = []
            for a, v in enumerate(gbl.midiAvail):
                gbl.midiAvail[a] = 0
            gbl.mtrks[0] = MMA.midi.Mtrk(0)

            gbl.tnames = {}

            MMA.parse.parseFile(f)    # read current file, grab grooves

            fileCount += 1            # just so we can report to user
            grooveCount += len(mkGrooveList)
            db[f] = mkGrooveList

        # Strip out defs of deleted (not found) files. Only on -g (update mode)

        if gbl.makeGrvDefs == 1:
            for f in list(db.keys()):
                if f not in processedFiles:
                    print("       Deleting: %s" % f)
                    del db[f]

        try:
            outpath = open(os.path.join(lib, mmadir), 'wb')
        except IOError:
            print("     Skipping '%s', no write access." % lib)
            noAccess += 1
            continue

        outpath.write(b"### mmaDB ... AUTOGENERATED BINARY DATA. "
                      b"DO NOT EDIT!!!\n")
        pickle.dump(db, outpath, protocol=2)  # proto2 forces compat between py2 and py3
        outpath.close()
        
        # check the database we just saved for duplicate entries.

        dbKeys = sorted(db.keys())
        idx = 1
        for k in dbKeys[:-1]:
            for kk in dbKeys[idx:]:
                for g in db[k]:
                    if g in db[kk]:
                        dupMessage.append("   Lib %s: %s & %s\n" % \
                                              (lib, os.path.basename(k),
                                               os.path.basename(kk)))
                        break
            idx += 1

    print("\nDatabase update complete."
            "\n     Files processed: %s" 
            "\n     Total number of grooves: %s\n" % (fileCount, grooveCount ))
    
    if noAccess:
        error ("You probably need to be 'root' to properly update your libraries.")
    
    if dupMessage:
        msg = ["Warning: Duplicate groove definitions found in:\n"]
        for a in dupMessage:
            msg.append(a)
        print(' '.join(msg))
    
    sys.exit(0)


def loadDB(d):
    """ Read a database file into memory.

        We're assuming that not much goes wrong here...if we don't find
        the database we return a Null.
    """

    try:
        infile = os.path.join(d, mmadir)
        f = open(infile, "rb")
        f.readline()    # Read/discard comment line
        g = pickle.load(f)
        f.close()
    except IOError:
        g = {}
    except ValueError:
        error("Incompatible database found. Maybe a result"
              "  of using different versions of python to"
              "  create/read, disk corruption or someone"
              "  playing games with the DB2 files."
              "  Recreate database by using 'mma -G' as root.")

    # If we can't find the directory, advise user to recreate the DB
    # Note, not an error ... should it be? Note, the compile will probably
    # end soon anyway since mma won't be able to find the requested groove.

    dirs = [os.path.dirname(i) for i in g.keys()]

    for a in set(dirs):
        if not os.path.exists(a):
            warning("There appears to be an error in the database.\n"
                    "  Directory '%s' cannot be found.\n"
                    "  Please try to execute the command 'mma -G' as root." % a)

    return g


#################################################################

def searchDB(targ, skip=None):
    """ Scan the database for the desired groove name.
        Returns the directory and the target
    """
    
    # Note the way we jump out the doubly nested loop.
    # Yes, this is pythonic and fast.
    try:
        for dir, g in grooveDB:
            for filename, namelist in g.items():
                if targ in namelist:
                    raise StopIteration

    except StopIteration:
        return os.path.join(dir, filename), targ.upper()

    # we get here if target not found in the database
    return ('', targ)
    
def findGroove(targ):
    """ Try to auto-load a groove from the library.

        The groove name (targ) can be a simple name (ie. swingsus) or
        an entended name which includes a file and directory
         (ie. swing:swingsus or stdlib/swing:swingsus).
    """

    global grooveDB
    ret = (None, targ.upper())   # not found return

    # If no existing DB we load them from expanded libPath

    if not grooveDB:
        grooveDB = []
        if not MMA.paths.libDirs:
            MMA.paths.expandLib()
        for d in MMA.paths.libDirs:
            g = loadDB(d)
            if g:
                grooveDB.append([d, g])

        if not grooveDB:   # BS value so we don't keep trying to load
            grooveDB = [['', {}]]

    # Check for extended notation. This is [DIR/DIR][FILE]:GROOVE

    # Split the filename from the groove name.
    # The complete spec for a groove name is dir/subdir/file:groove

    if ':' in targ:
        dirfile, targ = targ.split(':', 1)
        dirpath = MMA.paths.findLibFile(dirfile)
        targ = targ.upper()
        if dirpath is None:
            error("The file '%s' does not exist in libraries." % dirfile)
            
        # user is by-passing the default libs ... just pass the file/groovename back
        if dirfile.startswith('.') or os.path.isabs(dirfile):
            ret = (dirfile, targ)
            
        # did the user shortcut the extended format by using DIR:groove (without a
        # filename. That's fine, search the database for the specifed dir.
        # Only problem is that if you have duplicate grooves defined in the
        # lib the first one found will be used.
        elif os.path.isdir(dirpath):
            ret = searchDB(targ, dirfile)
                            
        else:
            # Does the library file exist at all? Check all the directories
            # set up from the expanded libPath. An example search
            # might be for "stdlib/swing:swingsus". The paths will
            # be:   1. stdlib  (no stdlib/swing.mma here)
            #      ..  lib   YES... found stdlib/swing.mma here

            fpath = MMA.paths.findLibFile(dirfile)

            if not fpath:
                error("Can't locate library file: %s! Groove: %s can't be found either."
                      % (dirfile, targ))

            if fpath.endswith(gbl.EXT) and not dirfile.endswith(gbl.EXT):
                dirfile += gbl.EXT

            ret = (dirfile, targ)

    else:
        # Just lookup a normal groove load from a file. We scan
        # the database and search for the groove name (targ).

        targ = targ.upper()
        ret = searchDB(targ)

    return ret

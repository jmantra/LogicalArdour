# file.py

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

import sys
import os
from . import gbl
from   MMA.common import *
import MMA.debug

PY3 = sys.version_info[0] == 3


def fixfname(f):
    """ Convert embedded space characters in filename to real spaces and
        expand ~ for user home directory.

        Originally this was done with .decode("string-escape") but that
        doesn't work with windows path names. So, now we just replace
        any \x20 sequences with single spaces.

        
    """

    f = f.replace('\\x20', ' ')
    return os.path.expanduser(f)


def locFile(name, lib):
    """ Locate a filename.

        This checks, in order:
          lib/name + .mma
          lib/name
          name + .mma
          name
    """

    ext = gbl.EXT
    exists = os.path.exists

    name = fixfname(name)  # for ~ expansion only
    
    if lib:
        if not name.endswith(ext):
            t = os.path.join(lib, name + ext)
            if exists(t):
                return t
        t = os.path.join(lib, name)
        if exists(t):
            return t

    if not name.endswith(ext):
        t = name + ext
        if exists(t):
            return t

    if exists(name):
        return name

    return None


###########################
# File read class
###########################


class ReadFile:

    class FileData:
        """ After reading the file in bulk it is parsed and stored in this
            data structure. Blanks lines and comments are removed.
        """

        def __init__(self, lnum, data, label):
            self.lnum = lnum
            self.data = data
            self.label = label

    def __init__(self, fname):

        self.fdata = fdata = []
        self.lastline = None
        self.lineptr = None
        self.fname = None

        self.que = []     # que for pushed lines (mainly for REPEAT)
        self.qnums = []
        #self.atEOFlines = []

        dataStore = self.FileData  # shortcut to avoid '.'s

        if fname == 1:
            inpath = sys.stdin
        else:
            try:
                if PY3:
                    inpath = open(fname, 'r', encoding=gbl.encoding)
                else:
                    inpath = open(fname, 'r')
            except IOError:
                error("Unable to open '%s' for input" % fname)
 
        if MMA.debug.debug or MMA.debug.showFilenames:
            dPrint("Opening file '%s'." % fname)

        self.fname = fname

        """ Read entire file, line by line:
             - strip off blanks, comments
             - join continuation lines
             - parse out LABELS
             - create line numbers
        """

        lcount = 0
        label = ''
        labs = []     # track label defs, error if duplicate in same file
        nlabs = []    # track linenumber label defs
        inComment = False  # multiline comment flag

        while 1:
            l = inpath.readline()

            if not l:        # EOF
                if inComment:
                    error("Multiline comment (/* */) not terminated.")
                break

            l = l.strip()
            lcount += 1

            if not l:
                continue

            # join lines ending in '\' - the strip() makes this the last char

            while l[-1] == '\\':
                l = l[0:-1] + ' ' + inpath.readline().strip()
                lcount += 1

            """ input cleanup ... for now the only cleanup is to convert
                0xa0 (non-breakable space) to 0x20 (regular space).
            """

            l = l.replace('\xa0', '\x20')

            # multiline comments
            if inComment:
                if "/*" in l:
                    warning ("Block comment start '/*' found inside comment.")
                if "*/" in l:
                    _, _, l = l.partition("*/")
                    inComment = False
                else:
                    continue

            l = l.split('//', 1)[0]  # Strip off line comment

            while "/*" in l:
                if "*/" in l:
                    t1, _, t2 = l.partition("/*")
                    t3, _, t4 = t2.partition("*/")
                    l = t1 + t4
                else:
                    l = l.split("/*")[0]
                    inComment = True

            """ Splits the remaining line into tokens using whitespace delimiters.
                Note that split() will strip off trailing and leading
                spaces, so a strip() is not needed here.
            """

            l = l.split()

            if not l:
                continue

            """ Parse out label lines. There are 2 different kinds of labels:
                - LABEL XXX
                   and
                - NNN

                The first kind is treated as an exclusive. If a NNN label or previous
                XXX duplicates, an error is generated.

                The LINE NUMBER type is not exclusive. If a duplicate NNN is found, the
                last one is used.

                XXX NNN types can not duplicate each other.

                Also note that XXX lines are stripped from input as well as NNN lines
                with only a NNN.
            """

            if l[0].upper() == 'LABEL':
                if len(l) != 2:
                    gbl.lineno = lcount
                    error("Usage: LABEL <string>")
                label = l[1].upper()
                if label[0] == '$':
                    gbl.lineno = lcount
                    error("Variables are not permitted as labels")
                if label in labs:
                    gbl.lineno = lcount
                    error("Duplicate label specified in line %s" % lcount)
                elif label in nlabs:
                    gbl.lineno = lcount
                    error("Label '%s' duplicates line number label" % label)
                labs.append(label)

            elif l[0].isdigit():
                label = l[0]

                if label in labs:
                    gbl.lineno = lcount
                    error("Line number '%s' duplicates LABEL" % label)

                if not label in nlabs:
                    nlabs.append(label)
                else:
                    for i, a in enumerate(fdata):
                        if a.label == label:
                            fdata[i].label = ''

            else:
                label = None

            # Save the line, linenumber and (maybe) the label.

            fdata.append(dataStore(lcount, l, label))

        inpath.close()

        self.lineptr = 0
        self.lastline = len(fdata)

    def toEof(self):
        """ Move pointer to End of File. """

        self.lineptr = self.lastline+1
        self.que = []
        self.qnums = []

    def goto(self, l):
        """ Do a goto jump.

            This isn't perfect, but is probably the way most GOTOs work. If
            inside a repeat/if then nothing more is processed. The jump is
            immediate. Of course, you'll run into problems with missing
            repeat/repeatend if you try it. Since all repeats are stacked
            back into the que, we just delete the que. Then we look for a
            matching label in the file line array.

            Label search is linear. Not too efficient, but the lists
            will probably never be that long either.

        """

        if not l:
            error("No label specified")

        if self.que:
            self.que = []

        for i, a in enumerate(self.fdata):
            if a.label == l:
                self.lineptr = i
                return

        error("Label '%s' has not been set" % l)

    def pushEOFline(self, ln):
        self.fdata.append(self.FileData(gbl.lineno, ln, ''))
        self.lastline+=1

    def push(self, q, nums):
        """ Push a list of lines back into the input stream.

            Note: This is a list of semi-processed lines, no comments, etc.

            It's quicker to extend a list than to insert, so add to the end.
            Note: we reverse the original, extend() then reverse again, just
            in case the caller cares.

            nums is a list of linenumbers. Needed to report error lines.
        """

        if not self.que:
            self.que = ['']
            self.qnums = [gbl.lineno]

        q.reverse()
        self.que.extend(q)
        q.reverse()

        nums.reverse()
        self.qnums.extend(nums)
        nums.reverse()

    def read(self):
        """ Return a line.

            This will return either a queued line or a line from the
            file (which was stored/processed earlier).
        """

        while 1:
            if self.que:            # Return a queued line if possible.
                ln = self.que.pop(-1)

                gbl.lineno = self.qnums.pop()

                if not ln:
                    continue

                return ln

            # Return the next line in the file.
            if self.lineptr >= self.lastline:
                return None  # EOF

            ln = self.fdata[self.lineptr].data
            gbl.lineno = self.fdata[self.lineptr].lnum
            self.lineptr += 1

            return ln

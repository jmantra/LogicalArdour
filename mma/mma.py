#!/usr/bin/python3

"""
The program "MMA - Musical Midi Accompaniment" and the associated
modules distributed with it are protected by copyright.

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
import platform

# Ensure a proper version is available.
# This test forces 2.6+ or 3.x
if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    print ("\nYou need a more current version of Python to run MMA.")
    print ("We're looking for something equal or greater than version 2.6")
    print ("Current Python version is %s\n" % sys.version)
    sys.exit(0)


#   MMA uses a number of application specific modules. These should
#   be installed in a mma modules directory or in your python
#   site-packages directory). MMA searches for the modules
#   directory and pre-pends the first found to the python system list.
#
#   If you end up with mma running (ie: it finds its modules), but
#   can't find libraries you then probably have the modules installed
#   in python-site and lib, include, etc. are NOT in one of the following
#   locations (lib and include must be in the same directory).
#
#   Note: it is quite possible with this method to have the modules
#   somewhere in python-site (NOT supported by MMA's standard installs)
#   and to have MMA's libraries in a different location (ie: /usr/share/mma).


platform = platform.system()

if platform == 'Windows':
    dirlist = [ sys.path[0], "c:/mma", "c:/program files/mma", "."]
elif platform == 'Darwin':
    dirlist = [ sys.path[0], "/Users/Shared/mma", 
             "/usr/local/share/mma", "/usr/share/mma", '.' ]
else:
    dirlist = [ sys.path[0], "/usr/local/share/mma", "/usr/share/mma", '.' ]

# Add the system python install location. If you install it this way
# you should have the default libraries, etc. under MMA in the package.

dirlist.extend(sys.path[1:])

# If a home path is specified via env variable the other
# MMA known paths from above will not be checked for modules.

envpath = os.environ.get('MMA_HOME')
if envpath != None:
    if envpath == '':
        print("MMA_HOME needs a value, use MMA_HOME=path.")
        sys.exit(1)
    dirlist = [os.path.abspath(envpath)]

# Call the mainline code.
# NOTE: the variables MMAdir and platform are read (imported)
#       by gbl.py from this module.

MMAdir = None

for d in dirlist:
    moddir = os.path.join(d, 'MMA')
    if os.path.isdir(moddir):
        if not d in sys.path:
            sys.path.insert(0, d)
        MMAdir = d

        try:
            import MMA.main    # this runs the program
            sys.exit(0)        # and ends the session
            # everything below here indicates a fatal error
            
        except ImportError:
            print("Found MMA directory in '%s'. Unable to execute 'MMA.main'." % MMAdir)
            sys.exit(1)
            
# we get here failing to find a MMA directory.

print("Unable to find the modules needed for MMA. Please check your installation.")
if envpath:
    msg = envpath
else:
    msg = dirlist
print("Could not find 'MMA.main.py' in '%s'." % msg)


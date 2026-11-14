# exits.py

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

This module contains cleanup code to be called on exit of MMA.

"""

import atexit
import os
import MMA.common

files = []


def cleanup():
    """ This cleanup routine will delete registered files. Currently this
        includes:

          files ... created by groove preview and autoplay funcs
    """

    for f in files:
        try:
            os.remove(f)
        except:
            pass

    MMA.common.cleanPrintBuffer()

atexit.register(cleanup)

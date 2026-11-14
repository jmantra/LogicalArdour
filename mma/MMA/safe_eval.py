# safe_eval.py

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

# This code pretends to implement a "safe" eval(). It really
# isn't safe! There are many ways an evil coder can exploit
# the safeguards. Unfortunately, python just isn't written to
# have a really bullet proof eval(). Look at your scripts before
# running things blindly!

import re

from math import *
from random import randint
from os import environ
from MMA.common import *
import sys

safeCmds = ['ceil', 'fabs', 'floor', 'exp', 'log', 'log10', 'pow',
            'sqrt', 'acos', 'asin', 'atan', 'atan2', 'cos', 'hypot',
            'sin', 'tan', 'degrees', 'radians', 'cosh', 'sinh',
            'int', 'in', '.join', 'str', '.split', 'for', 'randint' ]


def pathjoin(*a):
    from os import path
    return path.join(*[x.strip() for x in a])

def safeEnv(var):
    """ Return the value of an env variable. 
        On my system non-existant env vars register as None and
        vars set to '' return as '' ... so we convert them all to
        ''. MMA doesn't have a NoneType.
    """

    ret = environ.get(var)
    if ret == None:
        ret == ''
    return ret

def safeEval(expr):
    toks = re.split(r'([a-zA-Z_\.]+|.)', expr)

    # We have split out the args passed to a string to evaluate.
    # This is not ideal, but we are erring on the side of dumbness,
    # to the point that ONLY numeric args to eval will be accepted.
    # The safeCmds[] are all math functions, not string. If you attempt
    # to pass a string which is not a legal function name
    # an error will be generated. So, for a silly eg,
    # something in MMA like "Print $( ceil( 1e+4))" will work ... but
    # "Print $( ceil ( 1ee+4 )) will generate a Unknown Operator due
    # to the 2 'e's, besides the fact that 1ee+4 is wrong anyway.
    
    for t in toks:
        if len(t) > 1 and t not in safeCmds:
            error("Illegal/Unknown operator '%s' in $()." % t)

    try:
        return eval(expr)
    except:
        error("Illegal operation in '%s'." % expr)


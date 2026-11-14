# rangeify.py

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

The following code is borrowed from
       https://stackoverflow.com/questions/3429510

It has been modified to account for the MMA special
values of '?' indicating un-numbered lines and the
conversion of string values to integers.

"""
from itertools import count, groupby

def rangeify(l):
    for i,v in enumerate(l):
        try:
            l[i]=int(v)
        except ValueError:
            l[i]=-987654321

    G=(list(x) for _,x in groupby(l, lambda x,c=count(): next(c)-x))
    ret = ", ".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)
    ret = ret.replace('-987654321', '?')
    return ret

#print( rangeify(['1', '2', '?', '4', '?', '?', '4','5']))

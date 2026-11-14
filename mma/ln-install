#!/usr/bin/python

import  os, sys

# Simple python script to install mma from tarball
# This should be fixed to be more versatile. Volunteers?

PY3 = sys.version_info[0] >= 3  # set if running python3

# In python3 raw_input() has been renamed input()
if PY3:
    raw_input = input

def okay(msg):
    print(msg)
    a=raw_input("   Press <ENTER> to continue (anything else will terminate): ")

    if a:
        sys.exit(1)

    return

pyMaj=2
pyMin=6

# Before we do anything, make sure we have an up-to-date python.

if not PY3:
    if sys.version_info[0] < pyMaj or sys.version_info[1] < pyMin:
        print("\nYou need a more current version of Python to run MMA and this install script.")
        print("We're looking for something equal or greater than version %s.%s or any 3.x" % \
                  (pyMaj,pyMin))
        print("Current Python version is %s.\n" % sys.version)
        sys.exit(0)


# Check to make sure user has root permissions.

print("""
This script will install mma, the standard library and the
python modules using symbolic links to the current directory.
""")

try:
    u=os.getuid()
except:
    u=1

if u:
    okay("""You do not appear to be running this script as 'root' user.
Continuing will probably cause all kinds of strange errors
and a generally unsatisfactory experience. But, we can try...
""")

rootdir = "/usr/local/share"
rootexe = "/usr/local/bin"
  
dir = rootdir + "/mma"
exe = rootexe + "/mma"

# Check to make sure install directories exist. Offer to create
# ... these might need to be created in Mac OS X

if not os.path.exists(rootdir):
    okay("""The directory %s does not exist. Create okay?""" % rootdir)
    if os.system("mkdir -p %s" % rootdir):
        print("Opps, create failed. Were you root?")
        sys.exit(1)
    
if not os.path.exists(rootexe):
    okay("""The directory %s does not exist. Create okay?""" % rootexe)
    if os.system("mkdir -p %s" % rootexe):
        print("Opps, create failed. Were you root?")
        sys.exit(1)
      
if os.path.exists(dir):
    okay("""The directory %s currently exists. Proceeding will overwrite
with a new link. YOU MAY LOSE DATA.""" % dir)

if os.path.exists(exe):
     okay("""The file %s currently exists. Proceeding will remove this
file with a new link. YOU MAY LOSE DATA.""" % exe)

okay("""Okay, I'm ready to create the links. I will create 2 links:
 - The main distribution and library at %s
 - The callable executable at %s
""" % (dir, exe) )

os.system("ln -sf `pwd` %s" % dir)
os.system("ln -sf `pwd`/mma.py %s" % exe)


print("There are some man pages in %s/docs/man that you may wish to install." % dir)


print("Everything seems to be okay. We suggest you first update the database")
print("with the command mma -G.")
print("Have Fun!")

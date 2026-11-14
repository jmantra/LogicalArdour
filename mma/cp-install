#!/usr/bin/python

import shutil, os, sys


# Simple python script to install mma from tarball
# This should be fixed to be more versatile. Volunteers?


pyMaj=2
pyMin=6

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

# Before we do anything, make sure we have an up-to-date python.

if not PY3:
    if sys.version_info[0] < pyMaj or sys.version_info[1] < pyMin:
        print("\nYou need a more current version of Python to run MMA and this install script.")
        print("We're looking for something equal or greater than version %s.%s or any 3.x" % \
                  (pyMaj,pyMin))
        print("Current Python version is %s.\n" % sys.version)
        sys.exit(0)


# Check to make sure user has root permissions.

print("This script will install mma, the standard library and the python modules.")

try:
    u=os.getuid()
except:
    u=1

if u:
    okay("""\nYou do not appear to be running this script as 'root' user.
Continuing will probably cause all kinds of strange errors
and a generally unsatisfactory experience. But, we can try...
""")

rootdir = "/usr/local/share"
rootexe = "/usr/local/bin"

dest = rootdir + "/mma"
exe = rootexe + "/mma"

print("""
We recommend that you install the package with this script
in the default locations. This script will create a
directory 'mma' in /usr/local/share. If this isn't
what you want, then stop this script and edit this
script's directory locations. But, please note that ONLY
/usr/local/share and /usr/share are supported as default
locations.

The main executable script will be installed in %s.

If you ever decide to get rid of MMA, just delete the executable
in /usr/local/mma and the directory tree in /usr/local/share/mma.

""" % rootexe)

okay("")


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
    

###########################################
######## Copy the executable.


if os.path.exists(exe):
    okay("Existing mma executable '%s' is being overwritten." % exe)
    os.remove(exe)

print("Copying mma to %s" % exe)

shutil.copy( 'mma.py', exe)

###########################################
######## Copy the library


if os.path.exists(dest):
    bu=dest.rsplit('/', 1)[0] + '/mma-old'
    if os.path.exists(bu):
        print("This script was going to move the existing MMA tree to")
        print("a backup directory called '%s'. But that already exists." % bu)
        print("So, please delete the backup (and current) directories by hand.")
        print("Yes, the script could do this, but it's probably safer for you to do it!")
        sys.exit(1)

    okay("Existing mma tree '%s' is being moved to '%s'." % (dest, bu))
    os.rename( dest, bu )

print( "Copying library to %s" % dest)
os.makedirs(dest)
shutil.copytree( "lib", dest+"/lib")


###########################################
######## Copy the includes

print("Copying includes to %s" % dest)
shutil.copytree( "includes", dest+"/includes")

###########################################
######## Copy the plugins

print("Copying plugins to %s" % dest)
shutil.copytree( "plugins", dest+"/plugins")

###########################################
######## Copy the modules

print("Copying python modules to %s" % dest)
shutil.copytree( "MMA", dest+"/MMA")

###########################################
######## Copy the html docs

print("Copying HTML documentation to %s" % dest)
shutil.copytree( "docs", dest+"/docs")

###########################################
######## Set permissions/udate database

print("\nUpdating database file. This uses mma with the -G option.")
print("If this fails, something was not installed properly")
print("and you should contact Bob and we'll figure it out.")

okay("")

os.system("%s -G" % exe)

print("Setting permissions on MMADIR database file for user update.")
os.system("chmod a+w " + dest+"/lib/stdlib/.mmaDB")

## man pages

print("There are some man pages in %s/docs/man that you may wish to install." % dest)


print("Install complete. Have fun!")

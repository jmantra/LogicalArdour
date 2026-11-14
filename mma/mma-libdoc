#!/usr/bin/env python

# Parse libraries and create html docs (works in py 2 & 3)

import os, sys, time, platform, subprocess

if len(sys.argv)>1:
    print("""mma-libdoc is a MMA maintenance program to parse library
 files and create/maintain the html library documentation.
 This program should be run as 'root' and it takes no
 command options. For more details see the file
 "README.mma-libdoc" which is distributed with MMA.""")
    sys.exit(0)

installdir = ( "c:\\mma\\", "/usr/local/share/mma", "/usr/share/mma", ".")

libpath = ''
docpath = ''

for p in installdir:
    a = os.path.join(p, 'lib', '')
    if os.path.isdir(a):
        libpath=a
        docpath = os.path.join(p, 'docs', 'html', 'lib')
        break

if not libpath:
    print("Can't find the MMA library!")
    print("Please check your installation and/or change the search path in this program.")
    sys.exit(1)

try:
    os.mkdir(docpath)
except:
    pass

index = []
links = []

MMA = "mma"   # set different path to mma if you need to

if platform == "Windows":
    sh_value = True
else:
    sh_value = False


print("Processing library files")

def  dodir(dir):
    """ Process files in directory.  """

    global index, links
    newdirs = []

    olib = os.path.join(docpath, dir)
    if not os.path.isdir(olib):
        try:
            os.mkdir(olib)
        except:
            print("Can't create directory %s" % olib)
            sys.exit(1)

    links.append("<li> <A Href=#%s> <h2> %s </h2> </a> </li>" % (dir, dir.title()))

    if dir.lower() == "stdlib":
        index.append("<P><h3>These grooves can be used from a program just by using their name.</h3>")

    index.append("<A Name =%s></a>" % dir)
    index.append("<h2> %s </h2>" % dir.title() )

    index.append("<ul>")


    for f in sorted(os.listdir(libpath + dir)):
        this = os.path.join(libpath, dir, f)

        if f.startswith('#') or f.startswith('.'):   # ignore backup and hidden
                continue

        if os.path.isdir(this):
            newdirs.append(os.path.join(dir, f))
            continue

        if this.endswith('.mma'):
            htmlfname = os.path.join(dir, f.replace('.mma' , '.html'))
            htmldate = 0
            htmlout = os.path.join(docpath, htmlfname)
            try:
                htmldate = os.path.getmtime(htmlout)
            except:
                pass

            libdate = 0
            try:
                libdate = os.path.getmtime(this)
            except:
                print("NO, NO, NO --- let Bob know about this!")
                pass   # shouldn't ever happen!

            if libdate < htmldate:
                print("Skipping: %s" % this)

            else:
                if htmldate == 0:
                    print("Creating: %s" % htmlfname)
                else:
                    print("Updating: %s" % htmlfname)
                try:
                    pid = subprocess.Popen( [MMA, "-Dxh", "-w", "-n", this],
                          shell=sh_value, stdout=subprocess.PIPE)
                    output = pid.communicate()[0]

                except:
                    print("Error forking %s. Is MMA variable correctly set?" % MMA)
                    sys.exit(1)

                try:
                    o = open(htmlout, "w")
                    output = output.decode(encoding="UTF-8")  # for py3
                    o.write(output)
                    o.close()
                except:
                    print("ERROR Creating %s" % htmlout)
                    continue
                    

                # Now make html files for each groove in the lib file.

                for a in open(htmlout):
                    if a.startswith("<!-- GROOVE"):
                        a=a.split()
                        gname = a[1].split('=', 1)[1]
                        gout = os.path.join(docpath, dir, a[2].split('=', 1)[1])
                        srcfile = a[3].split('=', 1)[1]

                        try:
                            pid = subprocess.Popen( [MMA, "-Dgh", "-w", "-n",
                               "%s/%s" % (srcfile, gname)],
                               shell=sh_value, stdout=subprocess.PIPE)
                            output = pid.communicate()[0]
                        except:
                            print("Error forking %s. Is MMA variable correctly set?")
                            sys.exit(1)

                        try:
                            o = open(gout, "w")
                            output = output.decode(encoding="UTF-8")  # for py3
                            o.write(str(output))
                            o.close()
                        except:
                            print("ERROR Creating %s" % gout)
                        continue


            index.append("<li> <A Href = %s> %s </a> </li>" % \
                     (htmlfname, os.path.join(dir, f)))

    index.append("</ul>")

    # Insert this at the END of the stdlib listing.
    if dir.lower() == "stdlib":
        index.append('<P><h3>These grooves should be callable just by using their names. If you have problems with duplicate groove names you can always force their use with a "use" directive.</h3>')

    # recurse though any other directories in the lib dir (ie. contri/more/files)
    for d in newdirs:
        dodir(d)

##############################


a = os.listdir(libpath)
dirs = []

for b in a:
    if os.path.isdir(libpath + b):
        dirs.append(b)
dirs.sort()

if dirs.count("stdlib"):
    dirs.remove("stdlib")
    dirs.insert(0, "stdlib")


for dir in dirs:
    dodir(dir)

out = open(os.path.join(docpath, 'index.html'), "w")

out.write("""<HTML>

    <!-- Autogenerated by mma-libdoc. Do not edit ... you'll lose it! -->

<Center> <h1> The MMA Library </h1> </Center>

<P>
This document is provided as a supplement to the <em>MMA Reference
Manual</em> which lists all of the commands in the program and helpful
information which can be used to create your own "style" files. If you are a
newcomer to MMA, you
should also have a look at the <em>MMA Tutorial</em> for some "getting
started" information.

<P>
The information on these HTML pages has been generated directly
from the library files in your MMA library. Each
entry uses the filename as a header and then lists the various
defined grooves. In addition, the individual groove names are
clickable and will display further, detailed information on that groove.
<P>
You should be able to use any of the grooves listed in the "STDLIB"
section in your files without
using other directives. However, if you have files in other
locations you will need to need to
explicitly load the library file(s) with a <em>Use</em> directive.

<P>
The filenames are in all lowercase. These are the actual filenames
used in the library. If you are loading files with the <em>Use</em>
directive you must use the same case (please note that
typographic case applies only to the filename---this is operating system
dependant). <em>Groove</em> commands are case-insensitive.

<P>
Following each groove description is a boxed number in the form
<B>(4)</B>. This indicates the sequence size of the groove. Next, is
a list of tracks and instrument names. This shows the first voice or
drum note defined for each track---it is quite possible that the track
uses other voices. This data is included so that you can see what
tracks are active.

<P>
The library files supplied with MMA contain embedded documentation.
The <em>-Dxh</em> and <em>-Dxl</em> MMA command line options extract the following
information from the each library file:

<UL>
<LI> The filename from the "Doc File" directive.

<LI> The file description from the "Doc Note" directive.

<LI> Any user variables documented in "DocVar" directives.

<LI> Each groove description: This is the optional text following a
  <em>DefGroove</em> directive.

    <UL>
    <LI> The sequence size. This is extracted from the current groove
  information and was set with the <em>SeqSize</em> directive. It is
  displayed in a small box after the groove description.

    <LI>  A "summary" of the voices used in the groove. Note that a
  different voice or MIDI note is possible for each bar in the
  sequence size; however, this listing only lists the selection for
  the first bar.

   </UL>
</UL>

<P>In addition, the <em>-Dgh</em> command generates sequence graphs and
detailed settings for each groove.

<P>If you find that you don't have some of the grooves listed below
in your distribution you need to run the program <em>mma-libdoc</em>
to update these docs. Not all style files are distributed in the
default MMA distribution.

<p>

<b><font size="+1">
<p>During the development of MMA the library files have improved to the
   point of being quite reasonable. They never will substitute for
   professional players, but that never was the intention.
<p>
<p>Still, some of the files need some help. Some, frankly, need
   quite a bit of help. Hopefully, you, the intelligent user, will
   make them better and share the results with the ever growing
   MMA community. Thank you! 
</b></font>

<HR Size=3pt>
<CENTER> <H2> Index </H2> </CENTER>

""")

if links:
    out.write("<ul>")
    out.write("\n".join(links))
    out.write("</ul>")
    out.write("<HR Size=3pt>")
out.write( "\n".join(index))

out.write("""
<BR>
<HR  Size=3pt>
<P> This document and the files linked were created by <em>mma-libdoc</em>.

<P>It is a part of the MMA distribution
and is protected by the same copyrights as MMA (the GNU General Public License).

<P> Created: %s""" % time.ctime() )

out.write("<HTML>")


out.close()


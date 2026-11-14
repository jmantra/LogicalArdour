#!/usr/bin/env python


# Simple groove browser for MMA .. seems to work for python 2 and 3

# modified by Anthony Fok <foka@debian.org> to move the database files
# to .cache in the usr's root directory instead of in the library tree.

import sys
PY3 = sys.version_info[0] == 3

if PY3:
    from tkinter import *
    from tkinter import messagebox as tkMessageBox
else:
    from Tkinter import *
    import tkMessageBox

import os
import subprocess
import pickle
import platform

# Point to the mma executable. Normally you'll have 'mma' in your
# path, so leave it as the default. If not, set a complete path.

MMA = 'mma'
#MMA = "c:python25\python mma.py"

# Some tk defaults for color/font
listbx_Bcolor = "white"          # listbox colors
listbx_Fcolor = "medium blue"

# Set the font and size to use. Examples:
#     "Times 12 Normal"
#     "Helvetica 12 Italic"
#     or just set it to "" to use the default system font

#gbl_font = "Georgia 16 bold"
#gbl_font = "Helvetica 12 italic"
#gbl_font = "System 16 bold"
#gbl_font = ''
gbl_font = "System 10"

# Find the groove libraries. This code is the same as that used
# in mma.py to find the root MMA directory.

platform = platform.system()

if platform == 'Windows':
    dirlist = ( sys.path[0], "c:/mma", "c:/program files/mma", ".")
    midiPlayer = ['']   # must be a list!
    sub_shell = True
else:
    dirlist = ( sys.path[0], "/usr/local/share/mma", "/usr/share/mma", '.' )
    midiPlayer = ["aplaymidi"] # Must be a list!
    sub_shell = False

for d in dirlist:
    moddir = os.path.join(d, 'MMA')
    if os.path.isdir(moddir):
        if not d in sys.path:
            sys.path.insert(0, d)
        MMAdir = d
        break

libPath = os.path.join(MMAdir, 'lib')

if not os.path.isdir(libPath):
    print("The MMA library directory was not found.")
    sys.exit(1)

if sys.platform.startswith(('linux', 'gnu', 'freebsd', 'netbsd', 'openbsd')):
    HOME = os.path.expanduser('~')
    XDG_CACHE_HOME = os.environ.get("XDG_CACHE_HOME", os.path.join(HOME, ".cache"))
    cachePath = os.path.join(XDG_CACHE_HOME, 'mma')
else:
    cachePath = libPath

if not os.path.exists(cachePath):
    os.makedirs(cachePath)

# these are the options passed to mma for playing a groove.
# they are modified by the entryboxes at the top of screen

opt_tempo = 100
opt_keysig = "C"
opt_chords = "I vi ii V7"
opt_count = 4

# The name of the database and a storage ptr. Don't change this.

class db_Entry:
    def __init__(self, fd, g):
        self.fileDesc=fd   # description of style
        self.grooveList=g  # dictionary of groove names, descriptions

dbName   = "browserDB"
db = []


#############################################################
# Utility stuff to manage database.

def error(m=''):
    """ Universal error/termination. """

    if m:
        print(m)
    sys.exit(1)

def update_groove_db(root, dir, textbox=None):
    """ Update the list of grooves. Use mma to do work.

        The resulting database is a dict. with the keys being the filenames.
        Each entry has 2 fields:
             filedesc - the header for the file
             glist    - a dict of subgrooves. The keys are the groovenames
                        and the data is the groove desc.
     """


    gdict = {}

    files = os.listdir(os.path.join(root, dir))
    for f in files:
        path = os.path.join(root,dir,f)
        if os.path.isdir(path):
            gdict.update(update_groove_db(root, os.path.join(dir, f), textbox))

        elif path.endswith('.mma'):
            fullFname = os.path.join(dir,f)
            if textbox:
                textbox.delete(0.0, END)
                textbox.insert(END,fullFname)
                textbox.update()
            else:
                print("Parsing %s" % fullFname)

            try:
                pp=subprocess.Popen([MMA, '-Dbo', path],
                    stdout=subprocess.PIPE, shell=sub_shell)
                output = pp.communicate()[0]
            except:
                msg = "Error in reading mma file. Is MMA current?\n" \
                    "Executable set to '%s'. Is that right?" % MMA
                if textbox:
                    tkMessageBox.showerror("Database Update", msg)
                else:
                    print(msg)
                sys.exit(1)
            if pp.returncode:
                msg = "Error in MMA. Is MMA current?\n" + output
                if textbox:
                    tkMessageBox.showerror("Database Update", output)
                else:
                    print(msg)
                sys.exit(1)
            
            output = output.decode(encoding="UTF-8")  # needed for py3
            output = output.strip().split("\n")

            gg={}
            for i in range(1, len(output), 2):
                gg[output[i].strip()] = output[i+1].strip()
                e=db_Entry( output[0].strip(), gg )
            gdict[fullFname] = e

    return gdict

def write_db(root, dbName, db, textbox=None):
    """ Write the data base from memory to a file. """

    path = os.path.join(root, dbName)
    msg = None
    try:
        outpath = open(path, 'wb')
    except:
        msg = "Error creating groove database file '%s'. " \
               "Do you need to be root?" % path

    if msg:
        if textbox:
            tkMessageBox.showwarning("Database Write Error", msg)
        else:
            print(msg)
        return

    pickle.dump(db, outpath, pickle.HIGHEST_PROTOCOL )
    outpath.close()

def read_db(root, dbName):
    """ Read database. Return structure/list. """

    path = os.path.join(root, dbName)

    # 1st see if there is DB. If not, just return and it'll be created

    try:
        inpath = open(path, 'rb')
    except:
        return None

    # Could be incompatible (created by 3, read by 2)

    try:
        g = pickle.load(inpath)
    except:
        g = None
    inpath.close()

    return g



###################################################
# All the tk stuff goes here

####################################################################
## These functions create various frames. Maintains consistency
## between different windows (and makes cleaner code??).

def makeLabelBox(parent, justify=CENTER, row=0, column=0, text=''):
    """ Create a label box. """

    f = Frame(parent)
    b = Label(f,justify=justify, text=text)
    b.grid()
    f.grid(row=row, column=column, sticky=E+W)
    f.grid_rowconfigure(0, weight=1)

    return b

def makeMsgBox(parent, justify=LEFT, row=0, column=0, text=''):
    """ Create a message box. """

    b = Message(parent, border=5, relief=SUNKEN, aspect=1000,
          anchor=W, justify=justify, text=text)
    b.grid(sticky=E+W, column=column, row=row)

    return b

def makeTextBox(parent, justify=LEFT, row=0, column=0, text=''):
    """ Create a text-message box. """

    f=Frame(parent)
    ys=Scrollbar(f)

    b = Text(f, border=5, relief=SUNKEN, wrap=WORD, height=2, width=50)

    b.grid(column=1,row=0, sticky=N+E+W+S)

    ys.config(orient=VERTICAL, command=b.yview)
    ys.grid(column=0,row=0, sticky=N+S)

    f.grid(row=row, column=column, sticky=E+W+N+S)
    f.grid_rowconfigure(0, weight=0)
    f.grid_columnconfigure(1, weight=1)


    return b

def makeButtonBar(parent, row=0, column=0, buttons=(())):
    """ Create a single line frame with buttons. """

    bf=Frame(parent)
    c=0
    for txt, cmd in buttons:
        Button(bf, text=txt, height=1, command=cmd).grid(column=c, row=0, pady=5)
        c+=1
    bf.grid(row=row, column=column, sticky=W)
    return bf

def makeListBox(parent, width=50, height=20, selectmode=BROWSE, row=0, column=0):
    """ Create a list box with x and y scrollbars. """

    f=Frame(parent)
    ys=Scrollbar(f)
    xs=Scrollbar(f)
    lb=Listbox(f,
               bg=listbx_Bcolor,
               fg=listbx_Fcolor,
               width=width,
               height=height,
               yscrollcommand=ys.set,
               xscrollcommand=xs.set,
               exportselection=FALSE,
               selectmode=selectmode )

    ys.config(orient=VERTICAL, command=lb.yview)
    ys.grid(column=0,row=0, sticky=N+S)

    xs.config(orient=HORIZONTAL, command=lb.xview)
    xs.grid(column=1, row=1, sticky=E+W)

    lb.grid(column=1,row=0, sticky=NSEW)

    f.grid(row=row, column=column, sticky=NSEW)
    f.grid_rowconfigure(0, weight=1)
    f.grid_columnconfigure(1, weight=1)

    return  lb

def makeEntry(parent, label="Label", text='', column=0, row=0):
    f=Frame(parent)
    l=Label(f, anchor=W, width=10, padx=10, pady=10, text=label).grid(column=0, row=0)
    e=Entry(f, text=text, width=10)
    e.grid(column=1, row=0, sticky=W)
    e.delete(0, END)
    e.insert(END, text)
    f.grid( column=column, row=row, sticky=W)

    return e


def dohelp(hw=[None]):
    """ A primitive help function. Need a volunteer to rewrite this! """

    def delwindow():
        if hw[0]:
            hw[0].destroy()
            hw[0] = None

    if hw[0]:
        return

    hw[0] = help_window = Toplevel()
    help_window.protocol("WM_DELETE_WINDOW", delwindow)

    help_window.title( "MMA Groove Browser Help")


    b=makeListBox(help_window, height=12,width=50, row=0, column=0)

    for l in ["Simple browser to view MMA grooves.",
              "",
              "Key bindings:",
              " - In File List (top frame):",
              "    <Click> - select library file",
              "    <Double Click> View library file",
              "",
              " - In groove list (bottom frame):",
              "    <Click> - display groove info in panel",
              "    <Double Click> - Have MMA play/preview selected groove."
              "",
              "",
              "The four entry boxes at the top let you set the",
              " parameters for the groove preview." ] :

        b.insert(END, l)

    help_window.grid_rowconfigure(0, weight=1)
    help_window.grid_columnconfigure(0, weight=1)


############################
# Main display screen

class Application:

    def __init__(self):
        """ Create frames:
               bf - the menu bar
               f1, f2 - the options bars
               lb - the list box with a scroll bar
               lbdesc - desc for file entries
               lgv - list box of grooves
               lgvdesc - desc for groove
        """

        self.selectedFile = ''
        self.selectedGroove = ''

        bf = makeButtonBar(root, row=0, column=0, buttons=(
             ("Quit", self.quitall ),
             ("Help", dohelp ),
             ("Re-read Grooves", self.updatedb ),
             ("Generate MIDI", self.generateMMAFile)
             ))

        self.f1 = Frame(root)
        self.f2 = Frame(root)

        self.e_tempo  = makeEntry(self.f1, label="Tempo", text=opt_tempo,
                                  row=0, column=0)
        self.e_keysig = makeEntry(self.f1, label="Key Signature", text=opt_keysig,
                                  row=0, column=1)
        self.f1.grid( column=0, row=1, sticky=W)
        self.e_chords = makeEntry(self.f2, label="Chords", text=opt_chords,
                                  row=0, column=0)
        self.e_count  = makeEntry(self.f2, label="Count", text=opt_count,
                                  row=0, column=1)
        self.f2.grid( column=0, row=2, sticky=W)

        self.lbdesc  = makeTextBox(root, row=3, column=0, text="Current file")
        self.lb=lb   = makeListBox(root, height=15, row=4, column=0)
        self.lgvdesc = makeTextBox(root, row=5, column=0, text="Groovy")
        self.lgv=lgv = makeListBox(root, height=16, row=6, column=0)


        # bindings

        lb.bind("<Button-1>",  self.selectFileClick)
        lb.bind("<Double-Button-1>", self.showFileDoubleClick)
        lb.bind("<<ListboxSelect>>",  self.selectFileSelect)
        lgv.bind("<Button-1>", self.selectGrooveClick)
        lgv.bind("<Double-Button-1>", self.playGroove)
        lgv.bind("<<ListboxSelect>>",  self.selectGrooveSelect)

        # Make the listbox frames expandable

        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(0, weight=1)

        lb.focus_force()   # make the listbox use keyboard

        self.updateFileList()

    # Play the selected groove
    def playGroove(self,w):
        opt_tempo = self.e_tempo.get()
        opt_keysig = self.e_keysig.get()
        opt_chords = self.e_chords.get()
        opt_chords = opt_chords.replace('  ', ' ')
        opt_chords = opt_chords.replace(' ', ',')
        opt_count = self.e_count.get()

        try:
            p=subprocess.Popen([MMA, '-V', 'Tempo=%s' % opt_tempo,
                'Keysig=%s' % opt_keysig, 'Chords=%s' % opt_chords,
                'Count=%s' % opt_count, self.selectedGroove],
                stderr=subprocess.PIPE, shell=sub_shell)
            output = p.communicate()[0]
        except:
            tkMessageBox.showerror("MMA Error",
                 "Error calling MMA to process the preview.\n" \
                 "Check your installation!\n" \
                 "Executable set to '%s'. Is that right?" % MMA)
            sys.exit(1)

        if p.returncode:
            if not output:
                msg = "Error ... can't find the MMA interpreter set to %s" % MMA
            else:
                msg = output
            tkMessageBox.showwarning("MMA Error", msg)
            if not output:
                sys.exit(1)

    # Update the selected groove info
    def selectGrooveRet(self, w):
        self.selectGroove(self.lgv.get(ACTIVE) )

    def selectGrooveClick(self,w):
        self.lgv.activate(self.lgv.nearest(w.y))
        self.selectGroove(self.lgv.get(self.lgv.nearest(w.y)))

    def selectGroove(self, f):
        self.selectedGroove=f
        self.lgvdesc.config(state=NORMAL)
        self.lgvdesc.delete(0.0, END)
        self.lgvdesc.insert(END,db[self.selectedFile].grooveList[self.selectedGroove])
        self.lgvdesc.config(state=DISABLED)

    # Update the selected file into
    def selectFileClick(self, w):
        self.lb.activate(self.lb.nearest(w.y))
        self.selectFile(self.lb.get(self.lb.nearest(w.y)))


    def showFileDoubleClick(self, w):
        self.selectFileClick(w)
        self.displayFile( libPath + os.sep + self.lb.get(self.lb.nearest(w.y)) )

    def selectFileSelect(self,w):
        self.selectFile(self.lb.get(w.widget.curselection()))

    def selectGrooveSelect(self,w):
        self.selectGroove(self.lgv.get(w.widget.curselection()))


    def selectFileRet(self, w):
        self.selectFile(self.lb.get(ACTIVE) )

    def selectFile(self, f):
        self.selectedFile = f
        self.lbdesc.config(state=NORMAL)
        self.lbdesc.delete(0.0, END)
        self.lbdesc.insert(END,db[f].fileDesc)
        self.lbdesc.config(state=DISABLED)
        self.updateGrooveList()

    # Display all the files in the file window, Select entry 0
    def updateFileList(self):
        f = sorted(db)
        self.selectedFile = f[0]
        self.lb.delete(0,END)
        for ff in f:
            self.lb.insert(END, ff)
        self.selectFile(f[0])
        self.updateGrooveList()
        root.update()

    # Display all the grooves for the current file, select 0
    def updateGrooveList(self):
        g = sorted(db[self.selectedFile].grooveList)
        self.selectedGroove=g[0]
        self.lgv.delete(0,END)
        for gg in g:
            self.lgv.insert(END, gg)
        self.selectGroove(self.selectedGroove)
        root.update()


    def updatedb(self):
        global db

        self.lb.delete(0,END)
        self.lbdesc.config(state=NORMAL)
        self.lbdesc.delete(0.0, END)
        self.lgv.delete(0,END)
        self.lgvdesc.config(state=NORMAL)
        self.lgvdesc.delete(0.0, END)

        db = update_groove_db(libPath, '', self.lbdesc )
        if not db:
            print("No data read")
            sys.exit(1)
        write_db(cachePath, dbName, db, self.lbdesc)
        self.updateFileList()


    def generateMMAFile(self):
        opt_tempo = self.e_tempo.get()
        opt_keysig = self.e_keysig.get()
        opt_chords = self.e_chords.get()
        opt_chords = opt_chords.replace('  ', ' ')
        opt_chords = opt_chords.replace(' ', ',')
        opt_count = self.e_count.get()

        fileName = self.extractGrooveName(self.selectedFile) + "_demo.mma"
        print("Generating " + fileName + " in dir " + os.getcwd())
        fileName = os.getcwd() + os.sep + fileName

        grooveList = sorted(db[self.selectedFile].grooveList)

        chordList = opt_chords.split(",")
        chordList = chordList[:int(opt_count)]

        fp = open(fileName, "w")
        fp.write("KeySig " +  opt_keysig + "\n")
        fp.write("Tempo " +  opt_tempo + "\n")
        fp.write("\n\n")

        barCount = 1
        for groove in grooveList:
            fp.write("Groove " + groove + "\n")
            for chord in chordList:
                fp.write(str(barCount) + " " + chord + "\n")
                barCount = barCount+1

                # Inserts silent bar
                barCount = barCount+1
                fp.write(str(barCount) + " z!\n\n")

        fp.close()

        self.generateMidiFile(fileName)


    def extractGrooveName(self, input):
            slashLoc = input.find("/")+1
            pointLoc = input.find(".")
            output = input[slashLoc:pointLoc]
            return output


    def generateMidiFile(self, fileName):
                self.launchSubprocess("MMA interpreter", MMA, fileName);


    def displayFile(self, fileName, win=[None,None]):

        w,b = win

        if not w:
           win[0] = w = Toplevel()

           win[1] = b = makeListBox(w, height=24,width=80, row=0, column=0)
           w.grid_rowconfigure(0, weight=1)
           w.grid_columnconfigure(0, weight=1)

        b.delete(0,END)
        try:
            infile=open(fileName, 'r')
        except:
            b.insert(END, "Can't access file %s. This is configuration error." % fileName)
        else:
            for l in infile:
                b.insert(END, l.rstrip().expandtabs())

        w.title( "MMA Groove Browser: %s" % fileName )

    def launchSubprocess(self, processTitle, processCommand, fileName):
            try:
                p=subprocess.Popen([processCommand, fileName],
                stderr=subprocess.PIPE, shell=sub_shell)
                output = p.communicate()[0]
            except:
                tkMessageBox.showerror(processTitle + " Error",
                 "Error calling " + processTitle + " \n" \
                 "Check your installation!\n" \
                 "Executable set to '%s'. Is that right?" % processCommand)
                sys.exit(1)

            if p.returncode:
                if not output:
                                msg = "Error ... can't find " + processTitle + " set to %s" % processCommand
                else:
                                msg = output
                tkMessageBox.showwarning(processTitle + " Error", msg)
                if not output:
                                sys.exit(1)


    def quitall(self):
        sys.exit()


# Start the tk stuff.

db = read_db(cachePath, dbName)
if not db:
    db = update_groove_db(libPath, '', None)

    if not db:
        print("No data in database")
        sys.exit(1)

    write_db(cachePath, dbName, db, None)

root = Tk()

root.title("MMA Groove Browser")
root.option_add("*Dialog.msg.wrapLength", "15i")
if gbl_font:
    root.option_add('*font', gbl_font)
app=Application()

root.mainloop()

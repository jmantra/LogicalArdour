#!/usr/bin/python
import pickle

infile = ".mmaDB"
f = open(infile, "r")
f.readline()    # Read/discard comment line
g = pickle.load(f)
f.close()

print(g)

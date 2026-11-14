#!/usr/bin/python

import os

def doit():
	for f in os.listdir('.'):
		if os.path.isdir(f):
			os.chdir(f)
			doit()
			os.chdir("..")
		else:
			if f.endswith('.mma'):
				os.system("mma %s" % f)

doit()





	


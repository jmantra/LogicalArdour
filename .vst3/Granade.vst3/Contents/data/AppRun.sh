#!/bin/bash

#cd usr/bin
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:../lib
export PATH=$PATH:$APPDIR/usr/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$APPDIR/usr/lib
"$APPDIR/usr/bin/Granade" "$@"

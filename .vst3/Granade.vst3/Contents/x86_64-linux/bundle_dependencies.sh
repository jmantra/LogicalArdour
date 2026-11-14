#!/bin/bash

# for copying vst dependencies to a bundled directory on linux

mkdir -p ../lib

# make lists of dependencies, but don't include system ones
DEPS_GRANADE=$(ldd Granade.so | grep -oE "/(.+?)\\.so\\.[0-9]+" | grep -vE "(libc|libm|libdl|libpthread|ld-linux-)")
DEPS_PLUGIN=$(ldd plugin.so | grep -oE "/(.+?)\\.so\\.[0-9]+" | grep -vE "(libc|libm|libdl|libpthread|ld-linux-)")
for DEPENDENCY in $DEPS_GRANADE
do
    ABSOLUTE_SYMLINK=$(realpath $DEPENDENCY)
    cp -P $DEPENDENCY ../lib
    cp $ABSOLUTE_SYMLINK ../lib
done

for DEPENDENCY in $DEPS_PLUGIN
do
    ABSOLUTE_SYMLINK=$(realpath $DEPENDENCY)
    cp -P $DEPENDENCY ../lib
    cp $ABSOLUTE_SYMLINK ../lib
done

patchelf --set-rpath '$ORIGIN/../lib' Granade.so
patchelf --set-rpath '$ORIGIN/../lib' plugin.so

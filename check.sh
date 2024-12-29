#!/bin/bash

# Define the file pattern
file_pattern="/usr/share/applications/Ardour-Ardour_8.10.0.desktop"

# Check if any file matches the pattern
if match=$(ls $file_pattern 2> /dev/null); then
  echo "Matching file(s):"
  echo "$match"
  desktop=$match
else
  echo "No files matching '$file_pattern' were found."
fi

echo $desktop

#!/bin/bash

# Check if Firefox is installed
if which firefox > /dev/null 2>&1; then
    echo "Firefox is installed on this system."
else
    echo "Firefox is not installed on this system."
fi

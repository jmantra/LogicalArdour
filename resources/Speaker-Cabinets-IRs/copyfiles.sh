 
#!/bin/bash

# Check if the script is executed in a directory
if [ -z "$1" ]; then
    target_dir="."
else
    target_dir="$1"
fi

# Use find to locate all files in subdirectories and copy them to the target directory
find "$target_dir" -type f -exec mv -n {} "$target_dir" \;

echo "All files have been moved to $target_dir"

#!/bin/bash




pipewire=true

if [ "$compiled" = true ]; then

  if [ "$pipewire" = true ]; then
    sudo cp pwardour.desktop /usr/share/applications/ardour.desktop
  else
    sudo cp ardour.desktop /usr/share/applications/ardour.desktop
  fi

else

  check_file_pattern() {
    local file_pattern="$1"  # Argument to the function
    # Check if any file matches the pattern
    if match=$(ls $file_pattern 2> /dev/null); then
      echo "Matching file(s):"
      echo "$match"
      desktop=$match
    else
      echo "No files matching '$file_pattern' were found."
    fi
  }

  check_file_pattern "/usr/share/applications/Ardour-Ardour_8.10.0.desktop"
 if [ -z "$desktop" ]; then
 check_file_pattern "/usr/share/applications/ardour.desktop"
else
  echo "Desktop file already exists. No action needed."
fi

  if [ "$pipewire" = true ]; then
    sudo cp pwregardour.desktop "$desktop"
  else
    sudo cp regardour.desktop "$desktop"
  fi

fi
for file in $HOME/.config/ardour8/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/[^/]+", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done
for file in $HOME/.config/ardour8/route_templates/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/[^/]+", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done
for file in $HOME/.config/MuseScore/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/[^/]+", home); print}' "$file" > tmp && mv tmp "$file"
    fi
    done










#DIR=$(find /opt -maxdepth 1 -type d -name "Ardour-*" | sort -V | tail -n 1)





















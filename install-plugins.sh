#!/bin/bash
# Copy the plugins in this repository into the user directories Ardour scans.
# LV2 goes to ~/.lv2, VST3 to ~/.vst3, and LADSPA to ~/.ladspa.
# Same-named bundles are replaced. Everything else in those directories is left alone.

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$root/plugins"

copy_tree() {
    local from="$1"
    local to="$2"
    local items=()

    if [ ! -d "$from" ]; then
        echo "Skipping $from (folder not found)"
        return
    fi

    shopt -s nullglob
    items=("$from"/*)
    shopt -u nullglob

    if [ "${#items[@]}" -eq 0 ]; then
        echo "Nothing to copy from $from"
        return
    fi

    mkdir -p "$to"
    rsync -a "${items[@]}" "$to/"
    echo "Copied ${#items[@]} item(s) to $to"
}

copy_tree "$src/lv2" "$HOME/.lv2"
copy_tree "$src/vst3" "$HOME/.vst3"
copy_tree "$src/ladspa" "$HOME/.ladspa"

echo "Rescan plugins in Ardour so the new copies are picked up."

#!/bin/bash
export XDG_CONFIG_HOME="${HOME}/.config/LogicalArdour"

ardour_major=""
if [ -f /opt/LogicalArdour/ardour-major ]; then
	ardour_major=$(tr -d '[:space:]' < /opt/LogicalArdour/ardour-major)
fi

if [ "$ardour_major" != "9" ]; then
	ardour_major=8
fi

shopt -s nullglob
official_dirs=()
for dir in /opt/Ardour-*; do
	if [ -d "$dir" ]; then
		official_dirs+=("$dir")
	fi
done
shopt -u nullglob

candidates=()
if [ ${#official_dirs[@]} -gt 0 ]; then
	newest=$(printf '%s\n' "${official_dirs[@]}" | sort -V | tail -n 1)
	official_major=$(basename "$newest" | sed -n 's/^Ardour-\([0-9][0-9]*\)\..*/\1/p')
	if [ -n "$official_major" ]; then
		candidates+=("$newest/bin/ardour${official_major}")
	fi
fi

if [ "$ardour_major" = "9" ]; then
	candidates+=(/usr/local/bin/ardour9 /usr/bin/ardour9)
else
	candidates+=(/usr/local/bin/ardour8 /usr/bin/ardour8 /usr/bin/ardour)
fi
looked_for="/opt/Ardour-*/bin/ardour*, /usr/local/bin/ardour${ardour_major}, and /usr/bin/ardour${ardour_major}"

ardour_bin=""
for candidate in "${candidates[@]}"; do
	if [ -x "$candidate" ]; then
		ardour_bin="$candidate"
		break
	fi
done

if [ -z "$ardour_bin" ]; then
	echo "LogicalArdour: could not find Ardour (looked for ${looked_for})." >&2
	exit 1
fi

is_elf() {
	local sig
	sig=$(od -An -t x1 -N 4 "$1" 2>/dev/null | tr -d ' \n')
	[ "$sig" = "7f454c46" ]
}

# Distro and official startup scripts exec the real binary. The signal
# bitset size is compiled into that ELF, not into the wrapper.
resolve_ardour_elf() {
	local path="$1"
	local candidate dir
	if is_elf "$path"; then
		printf '%s\n' "$path"
		return 0
	fi
	dir=$(dirname "$(readlink -f "$path")")
	shopt -s nullglob
	for candidate in "$dir"/ardour-* "$dir"/../lib/ardour*/ardour-*; do
		if [ -f "$candidate" ] && is_elf "$candidate"; then
			printf '%s\n' "$(readlink -f "$candidate")"
			shopt -u nullglob
			return 0
		fi
	done
	shopt -u nullglob
	return 1
}

config_major_for() {
	local text="$1"
	local major
	major=$(printf '%s\n' "$text" | sed -n 's/.*[Aa]rdour-\([0-9][0-9]*\)\..*/\1/p' | head -n 1)
	if [ -z "$major" ]; then
		major=$(printf '%s\n' "$text" | sed -n 's/.*\/ardour\([0-9][0-9]*\)\/.*/\1/p' | head -n 1)
	fi
	if [ -z "$major" ]; then
		major=$(printf '%s\n' "$text" | sed -n 's/.*\/ardour\([0-9][0-9]*\)$/\1/p' | head -n 1)
	fi
	printf '%s\n' "$major"
}

# SetSession is always character 1 and LuaTimerS character 3 when the mask
# is printed high-bit first. New signals have been inserted before that tail,
# so only the mask length changes between releases.
align_hook_masks() {
	local ui_scripts="$1"
	local bits="$2"
	python3 - "$ui_scripts" "$bits" << 'PY'
import re
import sys

path, bits = sys.argv[1], int(sys.argv[2])
hooks = {
    "Load guided menu": (1, 3),
    "auto save snapshot": (3,),
    "Create key file": (1,),
}
with open(path, encoding="utf-8") as handle:
    text = handle.read()

def replace(match):
    name = match.group(1)
    positions = hooks.get(name)
    if positions is None:
        return match.group(0)
    mask = ["0"] * bits
    for position in positions:
        if position < bits:
            mask[position] = "1"
    return 'name="%s" signals="%s"' % (name, "".join(mask))

updated = re.sub(r'name="([^"]+)" signals="[01]+"', replace, text)
if updated != text:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(updated)
PY
}

ardour_elf=""
if ardour_elf=$(resolve_ardour_elf "$ardour_bin"); then
	signal_bits=$(grep -a -o -E 'St6bitsetILm[0-9]+E' "$ardour_elf" | sed -n 's/St6bitsetILm\([0-9][0-9]*\)E/\1/p' | sort -u)
	signal_bit_count=$(printf '%s\n' "$signal_bits" | grep -c '[0-9]')
	config_major=$(config_major_for "$ardour_elf"$'\n'"$ardour_bin")
	ui_scripts="${XDG_CONFIG_HOME}/ardour${config_major}/ui_scripts"
	if [ "$signal_bit_count" -ne 1 ] || [ -z "$config_major" ]; then
		echo "LogicalArdour: could not read the Ardour signal mask size from ${ardour_elf}; leaving hook signals unchanged." >&2
	elif [ -f "$ui_scripts" ]; then
		align_hook_masks "$ui_scripts" "$signal_bits"
	fi
else
	echo "LogicalArdour: could not find the Ardour executable behind ${ardour_bin}; leaving hook signals unchanged." >&2
fi

exec "$ardour_bin" "$@"

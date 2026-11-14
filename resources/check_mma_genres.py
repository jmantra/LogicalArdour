#!/usr/bin/env python3
"""Check that every genres.json id maps to a real MMA DefGroove."""

import json
import os
import re
import sys

GROOVE_RE = re.compile(r"^([^/]+)/([^:]+):(.+)$")
DEF_RE = re.compile(r"^\s*defgroove\s+(\S+)", re.IGNORECASE)


def main() -> int:
    resources = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(resources)
    genres_path = os.path.join(resources, "genres.json")
    map_path = os.path.join(resources, "mma_genres.json")
    lib_root = os.path.join(root, "mma", "lib")

    with open(genres_path, encoding="utf-8") as handle:
        genres = json.load(handle)
    with open(map_path, encoding="utf-8") as handle:
        mapping = json.load(handle)

    genre_ids = [profile["id"] for profile in genres.get("profiles", [])]
    errors = []

    if len(genre_ids) != len(set(genre_ids)):
        errors.append("genres.json has duplicate ids")
    if len(mapping) != len(set(mapping)):
        errors.append("mma_genres.json has duplicate ids")

    missing = [genre_id for genre_id in genre_ids if genre_id not in mapping]
    extra = [genre_id for genre_id in mapping if genre_id not in set(genre_ids)]
    if missing:
        errors.append("missing from mma_genres.json: " + ", ".join(missing))
    if extra:
        errors.append("not in genres.json: " + ", ".join(extra))

    for genre_id in genre_ids:
        entry = mapping.get(genre_id)
        if not isinstance(entry, dict):
            continue
        groove = entry.get("groove", "")
        match = GROOVE_RE.match(groove)
        if not match:
            errors.append(f"{genre_id}: groove {groove!r} is not library/file:Name")
            continue
        library, filename, groove_name = match.groups()
        path = os.path.join(lib_root, library, filename + ".mma")
        if not os.path.isfile(path):
            errors.append(f"{genre_id}: missing library file {path}")
            continue
        found = set()
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                defined = DEF_RE.match(line)
                if defined:
                    found.add(defined.group(1).lower())
        if groove_name.lower() not in found:
            errors.append(
                f"{genre_id}: {groove_name!r} is not a DefGroove in {library}/{filename}.mma"
            )

    if errors:
        for error in errors:
            print(f"Error: {error}")
        return 1

    print(f"OK: {len(genre_ids)} genres resolve to a DefGroove")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Deep scan for game data in a source tree.

Reports any file under the tree root whose content contains an unbroken run of at least
MIN_RUN_BYTES bytes of the user-supplied ROM, in either byte order. It is deliberately exact
and deliberately slow: it builds the full window index once and is meant to be run on demand,
not on every fast test run.

Exit codes:
    0   the tree is clean
    1   at least one file carries ROM content, each such file is named on stdout
    2   usage or setup error: bad arguments, missing ROM, unreadable tree. Never returns 0 here,
        because a scan that cannot run must not look like a clean tree.
"""

import argparse
import sys
import zlib
from pathlib import Path

MIN_RUN_BYTES = 96
DEFAULT_ROM_NAME = "Mario Kart 64 (Europe) (Rev A).n64"
SKIP_DIRECTORIES = {"rom", "logs", "__pycache__", ".git"}
EXIT_CLEAN = 0
EXIT_FOUND = 1
EXIT_ERROR = 2


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return EXIT_ERROR


def rom_views(rom_path):
    rom = rom_path.read_bytes()
    swapped = bytearray(rom)
    swapped[0::2], swapped[1::2] = rom[1::2], rom[0::2]
    return (rom, bytes(swapped))


def window_crcs(views):
    return {
        zlib.crc32(view[offset:offset + MIN_RUN_BYTES])
        for view in views
        for offset in range(0, len(view) - MIN_RUN_BYTES + 1)
    }


def candidate_files(root):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if SKIP_DIRECTORIES & set(path.relative_to(root).parts):
            continue
        yield path


def carries_rom_content(path, views, known_crcs):
    data = path.read_bytes()
    for offset in range(0, max(len(data) - MIN_RUN_BYTES, 0) + 1):
        window = data[offset:offset + MIN_RUN_BYTES]
        if zlib.crc32(window) in known_crcs and any(window in view for view in views):
            return window
    return None


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description="Fail when a file carries ROM content.")
    parser.add_argument("root", help="tree root to scan")
    parser.add_argument("--rom", required=True, help="path to the user-supplied ROM image")
    return parser.parse_args(argv)


def main(argv):
    arguments = parse_arguments(argv)
    root = Path(arguments.root)
    rom_path = Path(arguments.rom)

    if not root.is_dir():
        return fail(f"tree root is not a directory: {root}")
    if not rom_path.is_file():
        return fail(
            f"ROM not found at {rom_path}. This scan cannot prove the tree is clean without the "
            "user-supplied image, so it fails instead of passing."
        )

    views = rom_views(rom_path)
    known_crcs = window_crcs(views)

    hits = []
    for path in candidate_files(root):
        if carries_rom_content(path, views, known_crcs) is not None:
            hits.append(path)

    for path in hits:
        print(f"ROM content: {path}")
    if hits:
        return EXIT_FOUND
    print(f"clean: no file under {root} carries a {MIN_RUN_BYTES}-byte run of the ROM")
    return EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

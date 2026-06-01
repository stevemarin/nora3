#!/usr/bin/env python

# compares the tests that have functions written for them against
# the invalid test files in the directory

import os.path
from io import TextIOWrapper
from glob import glob

intro = "path = os.path.join"


def read_through_newline(fh: TextIOWrapper) -> None:
    while fh.read(1) not in {"\n", ""}:
        continue


def maybe_read_path(fh: TextIOWrapper) -> str | None:
    for value in intro[1:]:
        ch = fh.read(1)
        assert ch != ""
        if value != ch:
            return read_through_newline(fh)

    buffer = ""
    assert fh.read(1) == "("
    while (ch := fh.read(1)) != ")":
        if ch not in {" ", '"', "\n"}:
            buffer += ch
    assert ch == ")"
    return os.path.join("tests", *buffer.split(",")[1:])


test_functions = []
files = glob("./tests/test_*.py")
for filename in files:
    with open(filename, "r") as fh:
        while (ch := fh.read(1)) != "":
            match ch:
                case "#":
                    read_through_newline(fh)
                case "p":
                    path = maybe_read_path(fh)
                    if path is not None:
                        test_functions.append(path)
                case _:
                    continue

test_files = []
for root, dirs, filenames in os.walk("tests"):
    if "invalid_" not in root:
        continue
    for filename in filenames:
        path = os.path.join(root, filename)
        test_files.append(path)

for missing in sorted(set(test_files) - set(test_functions)):
    print(missing)

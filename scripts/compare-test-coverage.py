#!/usr/bin/env python

# compares the tests that have functions written for them against
# the invalid test files in the directory

import os
import os.path
import re
from glob import glob

test_functions = []
files = glob("./tests/test_*.py")
for filename in files:
    with open(filename, "r") as fh:
        content = re.sub(r"\s+", " ", fh.read())
    
    intro = "path = os.path.join"
    while (idx := content.find(intro)) != -1:
        assert content[idx + len(intro)] == "("

        length = 0
        while content[idx + length] != ")":
            length += 1
        
        assert content[idx + length] == ")"

        parts = content[idx + len(intro) + 1: idx + length].replace("TEST_DIR", "tests").replace('"', "").replace(" ", "").split(",")
        path = os.path.join(*parts)
        test_functions.append(path)
        content = content[idx + len(intro) + length - 1:]

test_files = []
for root, dirs, filenames in os.walk("tests"):
    if "invalid_" not in root:
        continue
    for filename in filenames:
        path = os.path.join(root, filename)
        test_files.append(path)
    
for missing in sorted(set(test_files) - set(test_functions)):
    print(missing)
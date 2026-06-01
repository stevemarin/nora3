#!/usr/bin/env bash

# compares files in local test suite against those in the official test suite
# which should be cloned into the same directory as this repo

for chapter in $(seq 1 11); do
    local_tests="./tests/chapter_$(printf '%02d\n' ${chapter})/"
    original_tests="../writing-a-c-compiler-tests/tests/chapter_${chapter}/"
    diff --recursive --brief ${local_tests} ${original_tests}
done

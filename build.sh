#!/bin/bash

# Build secure images
mbed compile -m FUTURE_SEQUANA_M0_PSA -t GCC_ARM -c --profile debug -N psoc63_m0_psa

# Build PSA tests for PSoC6-PSA
mbed test --compile -m FUTURE_SEQUANA_M0_PSA -t GCC_ARM -n tests-mbed_hal-spm,tests-psa-* --profile debug -c
mbed test --compile -m FUTURE_SEQUANA_PSA -t GCC_ARM -n tests-mbed_hal-spm,tests-psa-* --profile debug -c -DNO_GREENTEA

# Or if you prefer to build all of mbed-os tests
mbed test --compile -m FUTURE_SEQUANA_M0_PSA -t GCC_ARM -c --profile debug
mbed test --compile -m FUTURE_SEQUANA_PSA -t GCC_ARM --profile debug -c -DNO_GREENTEA

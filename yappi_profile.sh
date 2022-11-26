#!/bin/bash
TIMESTAMP=$(date +"%Y_%M_%d-%H_%M_%S")
PROF_FILE=${1:-$TIMESTAMP}
yappi -b -o ./iia_profile_results/"$PROF_FILE".conf IIA2223-proj-jog-40.py

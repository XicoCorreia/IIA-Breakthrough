#!/bin/bash
TIMESTAMP=$(date +"%Y_%m_%d-%H_%M_%S")
PROF_FILE=${1:-$TIMESTAMP}
yappi -b -o ./iia_profile_results/"$PROF_FILE".prof IIA2223-proj-tudo-40.py

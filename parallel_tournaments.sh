#!/bin/bash
NUM_THREADS=${1:-$(nproc)}
eval "echo {1..$NUM_THREADS}" \
 | xargs -n 1 -P "$NUM_THREADS" \
 sh -c 'python3 IIA2223-proj-jog-40.py | grep -A 3 "VITÓRIAS"' \
 | awk '{a[$1] += $2} END{print "Velho: "a["Velho"]"\nBelarmino: " a["Belarmino"]"\nHeurácio: "a["Heurácio"]}'

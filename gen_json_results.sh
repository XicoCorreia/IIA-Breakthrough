#!/bin/bash
for i in {1..10}
do
  python3 corre_torneios.py belarmino marco heuracio "$1" ~/results_depth_"$1"_"$i".json
done
sleep 1
echo "----- DONE -----"
echo "[" && find ~/ -maxdepth 1 -type f -name "results_depth_$1*.json" | xargs sh -c 'for arg do cat "$arg"; echo ","; done' && echo "]"

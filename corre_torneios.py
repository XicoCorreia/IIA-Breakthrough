# pylint: disable=missing-module-docstring missing-function-docstring global-statement
# IIA-2223
# Autores:
#  54685 - Francisco Correia
#  55855 - Francisco Maia
#  55955 - Alexandre Fonseca
from collections import defaultdict

import contextlib
import importlib
import io
import itertools
import json
import os
import sys

from pathos.multiprocessing import ProcessingPool
from jogar import Jogador, JogadorAlfaBeta, random_player, faz_campeonato

mod = importlib.import_module("IIA2223-proj-tudo-40")
JogoBT_40 = getattr(mod, "JogoBT_40")
func_aval_belarmino = getattr(mod, "func_aval_belarmino")
func_aval_heuracio = getattr(mod, "func_aval_heuracio")
func_aval_marco = getattr(mod, "func_aval_marco")


PLAYER_FUNC_MAP = {
    "belarmino": lambda d: JogadorAlfaBeta("Belarmino", d, func_aval_belarmino),
    "heuracio": lambda d: JogadorAlfaBeta("Heurácio", d, func_aval_heuracio),
    "marco": lambda d: JogadorAlfaBeta("Marco", d, func_aval_marco),
    "randy": lambda _: Jogador("Randy", random_player),
}


def main():
    try:
        *player_names, depth, output_path = sys.argv[1:]
    except ValueError:
        player_names = depth = output_path = ""

    if not depth.isnumeric():
        player_names = [*player_names, depth]
        depth = output_path
        output_path = None

    if not player_names or not depth.isnumeric():
        print(
            "Usage: <path_to_python_binary> corre_torneios.py "
            + "<player_1> <player_2> [...] <depth> [json_output_path]"
        )
        print("Available players: 'belarmino', 'heuracio', 'marco', 'randy'.")
        print("Examples: python3 corre_torneios.py belarmino randy 1")
        print("          python3 corre_torneios.py marco heuracio 2 ~/output.json")
        sys.exit(1)

    players = [PLAYER_FUNC_MAP[name](int(depth)) for name in player_names]
    max_workers = os.cpu_count() or 1
    with ProcessingPool(max_workers=max_workers) as executor:
        results = executor.map(worker, itertools.repeat(players, max_workers))
    lines = [line for result in results for line in result.split("\n")]
    stdout_str = "\n".join(lines)
    player_points = get_player_points(lines)
    json_output = json.dumps(player_points, ensure_ascii=False, indent=4)

    print(stdout_str)
    print("--------------")
    print("Player points:")
    total = sum(player_points.values())
    for key, val in player_points.items():
        print(f"  {key}: {val}/{total}")
    print("--------------")

    if output_path:
        with open(output_path, mode="w", encoding="utf-8") as out_file:
            out_file.write(json_output)
            print("File saved to:", output_path)


def filter_line(line):
    return line and "--vencedor" not in line and "JOGADOR" not in line


def get_player_points(lines):
    ret = defaultdict(int)
    pontos_jogadores = list(map(lambda x: x.split(), filter(filter_line, lines)))
    for player, points in pontos_jogadores:
        ret[player] += int(points)
    return ret


def worker(players: "list[Jogador]"):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        jogo = JogoBT_40()
        faz_campeonato(jogo, players, 120)
        return buf.getvalue()


if __name__ == "__main__":
    main()

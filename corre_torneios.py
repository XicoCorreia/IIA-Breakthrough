# pylint: disable=missing-module-docstring missing-function-docstring global-statement
import importlib
import itertools
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
        *player_names, depth = sys.argv[1:]
    except ValueError:
        player_names = depth = 0
    if not player_names:
        print(
            "Usage: <path_to_python_binary> corre_torneios.py <player_1> <player_2> [...] <depth>"
        )
        print("Available players: 'belarmino', 'heuracio', 'marco', 'randy'.")
        print("Example: python3 corre_torneios.py belarmino randy 1")
        sys.exit(1)

    players = [PLAYER_FUNC_MAP[name](int(depth)) for name in player_names]
    max_workers = os.cpu_count() or 1
    with ProcessingPool(max_workers=max_workers) as executor:
        executor.map(worker, itertools.repeat(players, max_workers))


def worker(players: "list[Jogador]"):
    jogo = JogoBT_40()
    faz_campeonato(jogo, players, 120)


if __name__ == "__main__":
    main()

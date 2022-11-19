# pylint: disable=invalid-name missing-module-docstring missing-class-docstring missing-function-docstring
# IIA-2223
# Autores:
#  54685 - Francisco Correia
#  55855 - Francisco Maia
#  55955 - Alexandre Fonseca

from functools import reduce
from jogos import Game, GameState


class EstadoBT_40(GameState):
    def __new__(cls, to_move, utility, board):
        return super(EstadoBT_40, cls).__new__(cls, to_move, utility, board, None)

    def __str__(self):
        board_str = ["-----------------"]
        for row in range(8, 0, -1):
            board_str.append(
                f"{row}|"
                + " ".join([self.board.get((col, row), ".") for col in "abcdefgh"])
            )
        board_str.append("-+---------------")
        board_str.append(" |a b c d e f g h")
        return "\n".join(board_str)


class JogoBT_40(Game):
    def __init__(self):
        whites = {(y, x): "W" for x in range(1, 3) for y in "abcdefgh"}
        blacks = {(y, x): "B" for x in range(7, 9) for y in "abcdefgh"}
        board = {**whites, **blacks}
        to_move = 1  # to_move: 1 is Whites, 2 is Blacks
        self.initial = EstadoBT_40(to_move, 0, board)

    def actions(self, state: EstadoBT_40):
        to_move, _, board, _ = state
        player, opponent = ("W", "B") if to_move == 1 else ("B", "W")
        pieces = [key for key, val in board.items() if val == player]
        moves = set()
        for col, row in pieces:
            i = 1 if to_move == 1 else -1
            prev_col = chr(ord(col) - i)
            next_col = chr(ord(col) + i)
            next_row = row + i
            # nota: presume-se que self.terminal_test(state) == False e que pode avançar
            if (col, next_row) not in board:
                moves.add(f"{col}{row}-{col}{next_row}")

            # não há peça ou é adversário
            if "a" <= prev_col <= "h" and board.get((prev_col, next_row)) in (
                None,
                opponent,
            ):
                moves.add(f"{col}{row}-{prev_col}{next_row}")

            if "a" <= next_col <= "h" and board.get((next_col, next_row)) in (
                None,
                opponent,
            ):
                moves.add(f"{col}{row}-{next_col}{next_row}")

        return sorted(list(moves))

    def display(self, state):
        print(state)
        if not self.terminal_test(state):
            print(f'--NEXT PLAYER: {"W" if state.to_move == 1 else "B"}')

    def executa(self, state: EstadoBT_40, valid_actions: list[str]):
        """Executa várias jogadas sobre um estado dado.
        Devolve o estado final."""
        return reduce(self.result, valid_actions, state)

    def result(self, state: EstadoBT_40, move):
        to_move = 1 if state.to_move == 2 else 2
        board = state.board.copy()
        old, new = map(lambda x: (x[0], int(x[1])), move.split("-"))
        board[new] = board[old]
        del board[old]

        return EstadoBT_40(
            to_move=to_move,
            utility=self.compute_utility(board, move, to_move),
            board=board,
        )

    def terminal_test(self, state: EstadoBT_40):
        to_move, _, board, _ = state
        opponent, row = ("B", 1) if to_move == 1 else ("W", 8)
        return any(board.get((col, row)) == opponent for col in "abcdefgh")

    def utility(self, state: EstadoBT_40, player):
        # Player 1 (W): 1
        # Player 2 (B): -1
        return state.utility if player == 1 else -state.utility

    def compute_utility(self, board, move, player):
        # TODO
        return 0

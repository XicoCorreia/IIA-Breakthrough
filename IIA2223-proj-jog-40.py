# pylint: disable=invalid-name missing-module-docstring missing-class-docstring missing-function-docstring
# IIA-2223
# Autores:
#  54685 - Francisco Correia
#  55855 - Francisco Maia
#  55955 - Alexandre Fonseca

from jogos import (
    Game,
    GameState,
    random_player,
    alphabeta_cutoff_search_new,
)
from jogar import faz_campeonato, JogadorAlfaBeta, Jogador


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
        result = state
        for move in valid_actions:
            result = self.result(result, move)
        return result

    def result(self, state: EstadoBT_40, move):
        to_move = 1 if state.to_move == 2 else 2
        board = state.board.copy()
        old, new = map(lambda x: (x[0], int(x[1])), move.split("-"))
        board[new] = board[old]
        del board[old]

        return EstadoBT_40(
            to_move=to_move,
            utility=self.compute_utility(move, state.to_move),
            board=board,
        )

    def terminal_test(self, state: EstadoBT_40):
        return state.utility != 0 or len(self.actions(state)) == 0

    def utility(self, state: EstadoBT_40, player):
        # W: 1, B: -1
        return state.utility if player == 1 else -state.utility

    def compute_utility(self, move, player):
        _, (_, row) = move.split("-")
        if int(row) != 1 and int(row) != 8:
            return 0
        return 1 if player == 1 else -1


def f_aval_belarmino(estado: EstadoBT_40, jogador):
    player = "W" if jogador == 1 else "B"
    pieces = [row for (_, row), val in estado.board.items() if val == player]
    res = 0
    if jogador == 1:
        for i in pieces:
            res += i**i
    else:
        for i in pieces:
            j = 9 - i
            res += j**j
    return res


class JogadorAlfaBetaAlt(Jogador):  # faz só utility()
    def __init__(self, nome, depth=4):
        super().__init__(
            nome,
            lambda game, state: alphabeta_cutoff_search_new(
                state,
                game,
                depth,
                eval_fn=game.utility,
            ),
        )

    def display(self):
        print(self.nome + " ")


def f_aval_jogador_heuristico(estado: EstadoBT_40, jogador):
    res = 0
    columns_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    player = "W" if jogador == 1 else "B"
    pieces = [(col, row) for (col, row), val in estado.board.items() if val == player]

    if jogador == 1:
        for col, row in pieces:
            # ! Esta linha pode ser comentada e o algoritmo ainda assim ganha bastante
            res += piece_value(estado, jogador, pieces, row, col)
            # PLayerWin
            if row == 8:
                return 500000
            # OneMoveTowin
            if row == 7 and threat(estado, jogador, row, col):
                res += 10000
            # Homeground piece
            elif row == 1:
                res += 10

        # Verificar se existem colunas vazias
        for col in columns_dict:
            exists = False
            for col_piece, _ in pieces:
                if col_piece == col:
                    exists = True
                    break
            if not exists:
                res -= 20
    else:
        for col, row in pieces:
            # ! Esta linha pode ser comentada e o algoritmo ainda assim ganha bastante
            res += piece_value(estado, jogador, pieces, row, col)
            # PLayerWin
            if row == 1:
                return 500000
            # OneMoveTowin
            if row == 2 and threat(estado, jogador, row, col):
                res += 10000
            # Homeground piece
            elif row == 8:
                res += 10

        # Verificar se existem colunas vazias
        for col in columns_dict:
            exists = False
            for col_piece, _ in pieces:
                if col_piece == col:
                    exists = True
                    break
            if not exists:
                res -= 20
    return res


def piece_value(estado: EstadoBT_40, jogador, piece, row_piece, col_piece):
    res = 0
    columns_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    col_num = columns_dict[col_piece]

    # Piece Value
    res += 1300

    # * Verify horizontal connections
    # * Verify vertical connections
    horizontal_conn = False
    vertical_conn = False
    for row, col in piece:
        if row == row_piece and columns_dict[col] in (col_num - 1, col_num + 1):
            horizontal_conn = True
        elif col_piece == col and row_piece in (row - 1, row + 1):
            vertical_conn = True
    if horizontal_conn:
        res += 35
    if vertical_conn:
        res += 15

    # Peça pode ser atacada
    # Peça pode ser protegida
    # TODO

    # Peças mais avançadas valem mais
    # Add how dangerous is the piece
    if jogador == 1:
        res += 10 * row_piece
        if row_piece == 6:
            res += 10
        elif row_piece == 7:
            res += 100
    else:
        res += (9 - row_piece) * 10
        if row_piece == 3:
            res += 10
        elif row_piece == 2:
            res += 100
    return res


def threat(estado: EstadoBT_40, jogador, row_piece, col_piece):
    return False


jogo = JogoBT_40()
j1 = JogadorAlfaBeta("Belarmino", 3, f_aval_belarmino)  # atualmente depth = 1
j2 = JogadorAlfaBeta("JogadorHeuristico", 3, f_aval_jogador_heuristico)
j3 = Jogador("Random 1", random_player)
# j4 = Jogador("Random 2", random_player)
# j5 = Jogador("Random 3", random_player)
# j5 = JogadorAlfaBetaAlt("Alfabeta")
# j6 = Jogador("NÓS", query_player)
faz_campeonato(jogo, [j1, j2], 10)

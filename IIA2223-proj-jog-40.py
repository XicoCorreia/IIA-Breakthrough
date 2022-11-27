# pylint: disable=invalid-name missing-module-docstring missing-class-docstring missing-function-docstring
# IIA-2223
# Autores:
#  54685 - Francisco Correia
#  55855 - Francisco Maia
#  55955 - Alexandre Fonseca

from time import time
from jogos import (
    Game,
    random_player,
    alphabeta_cutoff_search_new,
    query_player,
)
from jogar import faz_campeonato, joga11, JogadorAlfaBeta, Jogador

WHITE = 1
BLACK = 2


class EstadoBT_40:
    def __init__(self, to_move, utility, board, whites, blacks, moves=None):
        self.to_move = to_move
        self.utility = utility
        self.board = board
        self.whites = whites
        self.blacks = blacks
        self.moves = moves

    def __str__(self):
        player_chars = [".", "W", "B"]  # 0, WHITES and BLACKS
        board_str = ["-----------------"]
        for i in range(len(self.board), 0, -1):
            board_str.append(
                f"{i}|" + " ".join(map(lambda x: player_chars[x], self.board[i - 1]))
            )
        board_str.append("-+---------------")
        board_str.append(" |a b c d e f g h")
        return "\n".join(board_str)


class JogoBT_40(Game):
    def __init__(self, n=8):
        self.n = n
        whites = set((row, col) for row in range(2) for col in range(n))
        blacks = set((row, col) for row in range(n - 2, n) for col in range(n))
        board = [[0 for _ in range(n)] for _ in range(n)]
        for x, y in whites:
            board[x][y] = WHITE
        for x, y in blacks:
            board[x][y] = BLACK
        to_move = WHITE
        self.action_dict = self.compute_action_dict(n)
        self.initial = EstadoBT_40(to_move, 0, board, whites, blacks)

    def actions(self, state: EstadoBT_40):
        if state.moves:
            return state.moves
        moves = set()
        if state.to_move == WHITE:
            pieces, pieces_opponent = state.whites, state.blacks
        else:
            pieces, pieces_opponent = state.blacks, state.whites
        for pos in pieces:
            for target, move in self.action_dict[pos][state.to_move].items():
                # can't eat opponent's piece if it is directly in front of ours
                if target[1] == pos[1] and target in pieces_opponent:
                    continue
                if target not in pieces:  # don't eat our own pieces
                    moves.add(move)
        state.moves = sorted(moves)
        return state.moves

    def display(self, state):
        print(state)
        if not self.terminal_test(state):
            print(f'--NEXT PLAYER: {"W" if state.to_move == WHITE else "B"}')

    def executa(self, state: EstadoBT_40, valid_actions: "list[str]"):
        """Executa várias jogadas sobre um estado dado.
        Devolve o estado final."""
        result = state
        for move in valid_actions:
            result = self.result(result, move)
        return result

    def result(self, state: EstadoBT_40, move):
        board = [row[:] for row in state.board]  # deepcopy
        (old_row, old_col), (new_row, new_col) = self.convert_move(move)
        board[new_row][new_col] = state.to_move
        board[old_row][old_col] = 0
        whites, blacks = state.whites.copy(), state.blacks.copy()

        if state.to_move == WHITE:
            whites.remove((old_row, old_col))
            whites.add((new_row, new_col))
            blacks.discard((new_row, new_col))
            to_move = BLACK
        else:
            blacks.remove((old_row, old_col))
            blacks.add((new_row, new_col))
            whites.discard((new_row, new_col))
            to_move = WHITE

        return EstadoBT_40(
            to_move,
            self.compute_utility(new_row, state.to_move),
            board,
            whites,
            blacks,
        )

    def terminal_test(self, state: EstadoBT_40):
        return state.utility != 0 or len(self.actions(state)) == 0

    def utility(self, state: EstadoBT_40, player):
        # W: 1, B: -1
        return state.utility if player == WHITE else -state.utility

    def compute_utility(self, row, player):
        if 0 < row < self.n - 1:
            return 0
        return 1 if player == WHITE else -1

    def compute_action_dict(self, n):
        """
        Gera um dicionário de ações que associa pares de coordenadas
        ((x1, y1), (x2, y2)) para ações no formato dado no enunciado.
        Exemplo: ((0, 0), (1, 1)) -> a1-b2
        """

        def in_board(x):
            return 0 <= x < n

        ret = {}
        a_ord = ord("a")
        for row in range(n):
            for col in range(n):
                black_moves = {}
                white_moves = {}
                for i in filter(in_board, (row - 1, row + 1)):
                    # white pieces move upwards, black pieces downwards
                    moves = white_moves if i > row else black_moves
                    for j in filter(in_board, (col - 1, col, col + 1)):
                        moves[(i, j)] = "-".join(
                            [f"{chr(col + a_ord)}{row + 1}", f"{chr(j + a_ord)}{i + 1}"]
                        )
                # use None to pad tuple so we can use to_move as index
                ret[(row, col)] = (None, white_moves, black_moves)
        return ret

    # ? Usar dict inverso para mais desempenho
    def convert_move(self, move):
        """Converte uma ação no formato do enunciado
        para uma ação representada no estado interno.
        Exemplo: "a1-b2" -> ((0, 0), (1, 1))"""
        ord_a = ord("a")
        (old_col, old_row), (new_col, new_row) = move.split("-")
        return (
            (int(old_row) - 1, ord(old_col) - ord_a),
            (int(new_row) - 1, ord(new_col) - ord_a),
        )


def f_aval_belarmino(estado: EstadoBT_40, jogador):
    res = 0
    n = len(estado.board)
    if jogador == WHITE:
        for row, _ in estado.whites:
            x = row + 1
            res += x**x
    else:
        for row, _ in estado.blacks:
            x = n - row
            res += x**x
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
    n = len(estado.board)
    home, target, offset = (0, n - 1, -1) if jogador == WHITE else (n - 1, 0, 1)

    if jogador == WHITE:
        pieces, pieces_opponent = estado.whites, estado.blacks
    else:
        pieces, pieces_opponent = estado.blacks, estado.whites

    # Verificar se existem colunas vazias
    occupied_cols = set()

    # Player win
    if target in map(lambda x: x[0], list(pieces)):
        return float("+inf")

    for row, col in pieces:
        occupied_cols.add(col)
        res += piece_value(estado, row, col)
        # One move to win
        if row == target + offset and not threat(estado, row, col):
            res += 10000
        # Homeground piece
        elif row == home:
            res += 150

    res -= (n - len(occupied_cols)) * 20
    res -= len(pieces_opponent) * 80
    return res


def f_aval_jogador_heuristico_old(estado: EstadoBT_40, jogador):
    res = 0
    n = len(estado.board)
    home, target, offset = (0, n - 1, -1) if jogador == WHITE else (n - 1, 0, 1)

    if jogador == WHITE:
        pieces, pieces_opponent = estado.whites, estado.blacks
    else:
        pieces, pieces_opponent = estado.blacks, estado.whites

    # Verificar se existem colunas vazias
    occupied_cols = set()

    # Player win
    if target in map(lambda x: x[0], list(pieces)):
        return float("+inf")

    for row, col in pieces:
        occupied_cols.add(col)
        # res += piece_value(estado, row, col)
        # One move to win
        if row == target + offset and not threat(estado, row, col):
            res += 10000
        # Homeground piece
        elif row == home:
            res += 150

    res -= (n - len(occupied_cols)) * 20
    res -= len(pieces_opponent) * 20
    return res


def piece_value(estado: EstadoBT_40, row, col):
    res = 0
    n = len(estado.board)

    protected = False
    piece_in_danger = False
    if estado.to_move == WHITE:
        pieces = estado.whites
        pieces_opponent = estado.blacks
        friend_row, opp_row = row - 1, row + 1
        second_row, third_row = n - 2, n - 3  # from winning row
        row_value = row + 1

    else:
        pieces = estado.blacks
        pieces_opponent = estado.whites
        friend_row, opp_row = row + 1, row - 1
        second_row, third_row = 1, 2  # from winning row
        row_value = n - row

    # * Verify horizontal connections
    if (row, col - 1) in pieces or (row, col + 1) in pieces:
        res += 15

    # * Verify vertical connections
    if (row - 1, col) in pieces or (row + 1, col) in pieces:
        res += 5

    # * Verify if piece is protected (can counter-attack)
    if (friend_row, col - 1) in pieces or (friend_row, col + 1) in pieces:
        res += 15
        protected = True

    # * Verify if piece can be attacked
    if (opp_row, col - 1) in pieces_opponent or (opp_row, col + 1) in pieces_opponent:
        # Peças mais avançadas e que não podem ser atacadas valem mais
        res -= 15
        piece_in_danger = True

    if not piece_in_danger:
        if row == third_row:
            res += 5
        elif row == second_row:
            res += 20

    res += row_value * 10

    return res


def threat(estado: EstadoBT_40, row, col):
    # ? explode nas rows de cima/baixo
    if estado.to_move == WHITE:
        pieces_opponent = estado.blacks
        row += 1
    else:
        pieces_opponent = estado.whites
        row -= 1
    return (row, col - 1) in pieces_opponent or (row, col + 1) in pieces_opponent


def main():
    d = 2
    jogo = JogoBT_40()
    j1 = JogadorAlfaBeta("Belarmino", d, f_aval_belarmino)  # atualmente depth = 1
    j11 = JogadorAlfaBeta("Belarmino 2", d, f_aval_belarmino)  # atualmente depth = 1
    j2 = JogadorAlfaBeta("Heurácio", d, f_aval_jogador_heuristico)
    j22 = JogadorAlfaBeta("Velho", d, f_aval_jogador_heuristico_old)
    j3 = Jogador("Random 1", random_player)
    j4 = Jogador("Random 2", random_player)
    j5 = Jogador("Random 3", random_player)
    j5 = JogadorAlfaBetaAlt("Alfabeta")
    j6 = Jogador("NÓS", query_player)
    # time_start = time()
    # a = joga11(jogo, j1, j2)
    # delta = time() - time_start
    # num_moves = len(a[1])
    # print(delta, "s")
    # print(num_moves, "moves")
    # print(delta / num_moves, "s em média")
    # jogo.jogar(j1.fun, j2.fun, verbose=False)
    faz_campeonato(jogo, [j2, j1, j22], 10)


if __name__ == "__main__":
    main()

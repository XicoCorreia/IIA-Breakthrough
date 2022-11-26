# pylint: disable=invalid-name missing-module-docstring missing-class-docstring missing-function-docstring
# IIA-2223
# Autores:
#  54685 - Francisco Correia
#  55855 - Francisco Maia
#  55955 - Alexandre Fonseca

from jogos import (
    Game,
    random_player,
    alphabeta_cutoff_search_new,
    query_player,
)
from jogar import faz_campeonato, JogadorAlfaBeta, Jogador

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
            player_pieces, opponent_pieces = state.whites, state.blacks
        else:
            player_pieces, opponent_pieces = state.blacks, state.whites
        for pos in player_pieces:
            for target, move in self.action_dict[pos][state.to_move].items():
                # can't eat opponent's piece if it is directly in front of ours
                if target[1] == pos[1] and target in opponent_pieces:
                    continue
                if target not in player_pieces:  # don't eat our own pieces
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
    if jogador == WHITE:
        for row, _ in estado.whites:
            x = row + 1
            res += x**x
    else:
        for row, _ in estado.blacks:
            x = 8 - row
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
    columns_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    player = "W" if jogador == 1 else "B"
    pieces = [(col, row) for (col, row), val in estado.board.items() if val == player]
    pieces_opponent = [
        (col, row) for (col, row), val in estado.board.items() if val != player
    ]

    if jogador == 1:
        for col, row in pieces:
            res += piece_value(estado, jogador, pieces, pieces_opponent, row, col)
            # PLayerWin
            if row == 8:
                return 500000
            # OneMoveTowin
            if row == 7 and threat(estado, jogador, pieces, pieces_opponent, row, col):
                res += 10000
            # Homeground piece
            elif row == 1:
                res += 150

        # Verificar se existem colunas vazias
        for col in columns_dict:
            exists = False
            for col_piece, _ in pieces:
                if col_piece == col:
                    exists = True
                    break
            if not exists:
                res -= 20
        res -= len(pieces_opponent) * 20
    else:
        for col, row in pieces:
            res += piece_value(estado, jogador, pieces, pieces_opponent, row, col)
            # PLayerWin
            if row == 1:
                return 500000
            # OneMoveTowin
            if row == 2 and threat(estado, jogador, pieces, pieces_opponent, row, col):
                res += 10000
            # Homeground piece
            elif row == 8:
                res += 150

        # Verificar se existem colunas vazias
        for col in columns_dict:
            exists = False
            for col_piece, _ in pieces:
                if col_piece == col:
                    exists = True
                    break
            if not exists:
                res -= 20

        res -= len(pieces_opponent) * 20
    return res


def piece_value(
    estado: EstadoBT_40, jogador, piece, pieces_opponent, row_piece, col_piece
):
    res = 0
    columns_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    col_num = columns_dict[col_piece]

    # Piece Value
    res += 1300

    # * Verify horizontal connections
    # * Verify vertical connections
    # * Verify if piece is protected
    horizontal_conn = False
    vertical_conn = False
    protected = False
    for col, row in piece:

        if row == row_piece and columns_dict[col] in (col_num - 1, col_num + 1):
            horizontal_conn = True
        elif col_piece == col and row_piece in (row - 1, row + 1):
            vertical_conn = True

        if jogador == 1:
            if (row == row_piece - 1) and columns_dict[col] in (
                col_num - 1,
                col_num + 1,
            ):
                protected = True
        else:
            if (row == row_piece + 1) and columns_dict[col] in (
                col_num - 1,
                col_num + 1,
            ):
                protected = True

    if horizontal_conn:
        res += 35
    if vertical_conn:
        res += 15
    if protected:
        res += 35

    # * Verify if piece can be attacked
    piece_in_danger = False
    for col, row in pieces_opponent:
        if jogador == 1:
            if (row == row_piece + 1) and columns_dict[col] in (
                col_num - 1,
                col_num + 1,
            ):
                piece_in_danger = True
                break
        else:
            if (row == row_piece - 1) and columns_dict[col] in (
                col_num - 1,
                col_num + 1,
            ):
                piece_in_danger = True
                break

    # Peças mais avançadas e que não podem ser atacadas valem mais
    if piece_in_danger:
        res -= 65
        if not protected:
            res -= 65
    else:
        if not protected:
            if jogador == 1:
                if row_piece == 6:
                    res += 10
                elif row_piece == 7:
                    res += 100
            else:
                if row_piece == 3:
                    res += 10
                elif row_piece == 2:
                    res += 100

    # Perigo da peça
    if jogador == 1:
        res += row_piece * 10
    else:
        res += (9 - row_piece) * 10

    return res


def threat(estado: EstadoBT_40, jogador, pieces, pieces_opponent, row_piece, col_piece):
    columns_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    col_num = columns_dict[col_piece]
    threat1 = False
    threat2 = False

    if jogador == 1:
        for col, row in pieces_opponent:
            if row == 8 and col_num == columns_dict[col] + 1:
                threat1 = True
            if row == 8 and col_num == columns_dict[col] - 1:
                threat2 = True
    else:
        for col, row in pieces_opponent:
            if row == 1 and col_num == columns_dict[col] + 1:
                threat1 = True
            if row == 1 and col_num == columns_dict[col] - 1:
                threat2 = True

    return threat2 and threat1


def main():
    jogo = JogoBT_40()
    j1 = JogadorAlfaBeta("Belarmino 1", 2, f_aval_belarmino)  # atualmente depth = 1
    j11 = JogadorAlfaBeta("Belarmino 2", 2, f_aval_belarmino)  # atualmente depth = 1
    j2 = JogadorAlfaBeta("Heurácio", 1, f_aval_jogador_heuristico)
    j3 = Jogador("Random 1", random_player)
    j4 = Jogador("Random 2", random_player)
    j5 = Jogador("Random 3", random_player)
    j5 = JogadorAlfaBetaAlt("Alfabeta")
    j6 = Jogador("NÓS", query_player)
    faz_campeonato(jogo, [j1, j11], 10)


if __name__ == "__main__":
    main()

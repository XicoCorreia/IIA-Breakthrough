# pylint: disable=invalid-name missing-module-docstring
# IIA-2223
# Autores:
#  54685 - Francisco Correia
#  55855 - Francisco Maia
#  55955 - Alexandre Fonseca

from jogar import JogadorAlfaBeta
from jogos import Game


class EstadoBT_40:
    """Uma classe que representa o estado de um jogo Breakthrough
    para o grupo 40 de IIA 22/23."""

    def __init__(self, to_move, utility, board, pieces, moves=None):
        self.to_move = to_move
        self.utility = utility
        self.board = board
        self.pieces = pieces
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

    def threat(self, pos: "tuple[int, int]"):
        """Verifica se uma peça na posição `pos` do próximo jogador (`to_move`)
        pode ser comida por uma peça do adversário.

        Devolve `True` se a peça do próximo jogador estiver vulnerável,
        `False` em caso contrário."""

        pieces_opponent = self.pieces[self.to_move % 2]
        row, col = pos
        row = (row + 1, row - 1, 1)[self.to_move - 1]
        return (row, col - 1) in pieces_opponent or (row, col + 1) in pieces_opponent


class JogoBT_40(Game):
    """Uma classe que representa um jogo de Breakthrough
    para o grupo 40 de IIA 22/23."""

    WHITE = 1
    BLACK = 2

    def __init__(self, n=8):
        self.n = n
        whites = set((row, col) for row in range(2) for col in range(n))
        blacks = set((row, col) for row in range(n - 2, n) for col in range(n))
        board = [[0 for _ in range(n)] for _ in range(n)]
        for x, y in whites:
            board[x][y] = JogoBT_40.WHITE
        for x, y in blacks:
            board[x][y] = JogoBT_40.BLACK
        to_move = JogoBT_40.WHITE
        self.action_dict = self.compute_action_dict(n)
        self.initial = EstadoBT_40(to_move, 0, board, (whites, blacks))

    def actions(self, state: EstadoBT_40):
        if state.moves:
            return state.moves
        moves = set()
        pieces, pieces_opponent = (
            state.pieces[state.to_move - 1],
            state.pieces[state.to_move % 2],
        )
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
            print(f'--NEXT PLAYER: {"W" if state.to_move == JogoBT_40.WHITE else "B"}')

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
        whites, blacks = state.pieces[0].copy(), state.pieces[1].copy()

        if state.to_move == JogoBT_40.WHITE:
            whites.remove((old_row, old_col))
            whites.add((new_row, new_col))
            blacks.discard((new_row, new_col))
            to_move = JogoBT_40.BLACK
        else:
            blacks.remove((old_row, old_col))
            blacks.add((new_row, new_col))
            whites.discard((new_row, new_col))
            to_move = JogoBT_40.WHITE

        return EstadoBT_40(
            to_move,
            self.compute_utility(new_row, state.to_move),
            board,
            (whites, blacks),
        )

    def terminal_test(self, state: EstadoBT_40):
        # Os próprios jogos em jogar.py lidam com
        # os casos em que já não há jogadas (peças).
        return state.utility != 0

    def utility(self, state: EstadoBT_40, player):
        # W: 1, B: -1
        return state.utility if player == JogoBT_40.WHITE else -state.utility

    def compute_utility(self, row, player):
        """
        Devolve a utilidade para um dado estado:
        (1: vitória, -1: derrota, 0: não terminou)

        Pressupõe-se que a função é chamada unicamente quando
        é criado um novo estado e que o valor de `row` resulta
        de uma jogada válida para o `player` em questão.
        """
        if 0 < row < self.n - 1:
            return 0
        return 1 if player == JogoBT_40.WHITE else -1

    def compute_action_dict(self, n):
        """Devolve um dicionário que associa uma posição `(x, y)`
        usada no estado interno às ações disponíveis nessa posição.

        As associações são feitas em função do jogador
        (`1` para peças brancas, `2` para peças pretas).

        As ações são devolvidas num dicionário em que as chaves são
        a posição do destino e os valores são a ação em si.

        Exemplo de ações para uma peça em `(1,1)` (visualmente, `b2`):
        ```python
        jogo = JogoBT_40()
        actions_b2 = jogo.action_dict[(1, 1)]
        jogo.action_dict[(1, 1)] == (
            None,  # padding para indexar com state.to_move sem offset
            {(2, 0): "b2-a3", (2, 1): "b2-b3", (2, 2): "b2-c3"}, # jog. 1
            {(0, 0): "b2-a1", (0, 1): "b2-b1", (0, 2): "b2-c1"}, # jog. 2
        )
        ```"""

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


# Nota: esta é a função func_aval_heuracio no ficheiro IIA2223-proj-tudo-40.py.
def func_aval_40(estado: EstadoBT_40, jogador):
    """Função de avaliação formada a partir das
    diversas funções de avaliação criadas."""
    res = func_aval_win(estado, jogador)
    if res > 0:
        return res

    res += 15 * func_aval_horizontal(estado, jogador)

    res += 5 * func_aval_vertical(estado, jogador)

    res += 15 * func_aval_protected(estado, jogador)

    res += 5 * func_aval_danger(estado, jogador)

    res -= 20 * func_aval_empty_cols(estado, jogador)

    res -= 80 * func_aval_opponent_piece_count(estado, jogador)

    res += 10000 * func_aval_one_move_to_win(estado, jogador)

    res += 150 * func_aval_home_ground(estado, jogador)

    res += 10 * func_aval_piece_value(estado, jogador)

    return res


def func_aval_win(estado: EstadoBT_40, jogador):
    """Função de avaliação que devolve um valor arbitrariamente
    elevado se o estado for vitorioso."""
    n = len(estado.board)
    pieces = estado.pieces[jogador - 1]
    target_row = (n - 1, 0)[jogador - 1]
    for row, _ in pieces:
        if target_row == row:
            return float("+inf")
    return 0


def func_aval_horizontal(estado: EstadoBT_40, jogador):
    """Função de avaliação que valoriza a existência de
    peças amigáveis adjacentes a uma peça na horizontal."""
    res = 0
    pieces = estado.pieces[jogador - 1]
    for row, col in pieces:
        if (row, col - 1) in pieces or (row, col + 1) in pieces:
            res += 1
    return res


def func_aval_vertical(estado: EstadoBT_40, jogador):
    """Função de avaliação que valoriza a existência de
    peças amigáveis adjacentes a uma peça na vertical."""
    res = 0
    pieces = estado.pieces[jogador - 1]
    for row, col in pieces:
        if (row - 1, col) in pieces or (row + 1, col) in pieces:
            res += 1
    return res


def func_aval_protected(estado: EstadoBT_40, jogador):
    """Função de avaliação que valoriza a existência de peças amigáveis
    que podem contra-atacar caso uma peça seja comida pelo adversário."""
    res = 0
    pieces = estado.pieces[jogador - 1]
    k = (-1, 1)[jogador - 1]
    for row, col in pieces:
        friend_row = row + k
        if (friend_row, col - 1) in pieces or (friend_row, col + 1) in pieces:
            res += 1
    return res


def func_aval_danger(estado: EstadoBT_40, jogador):
    """Função de avaliação que (des)valoriza a possibilidade
    de uma peça ser comida pelo adversário.
    A função valoriza ainda peças que estejam relativamente
    perto da vitória, desde que estas não estejam em perigo."""
    res = 0
    n = len(estado.board)
    k, second_row, third_row = ((1, n - 2, n - 3), (-1, 1, 2))[jogador - 1]
    pieces_opponent = estado.pieces[jogador % 2]
    for row, col in pieces_opponent:
        row = row + k
        if (row, col - 1) in pieces_opponent or (row, col + 1) in pieces_opponent:
            # Peças mais avançadas e que não podem ser atacadas valem mais
            res -= 3
            if row == third_row:  # vs. a 1a fila do adversário
                res += 1
            elif row == second_row:  # vs. a 1a fila do adversário
                res += 4
    return res


def func_aval_empty_cols(estado: EstadoBT_40, jogador):
    """Função de avaliação que (des)valoriza a existência de
    colunas vazias (isto é, não ocupadas por peças amigáveis)."""
    occupied_cols = set()
    pieces = estado.pieces[jogador - 1]
    n = len(estado.board)
    for _, col in pieces:
        occupied_cols.add(col)
    return n - len(occupied_cols)


def func_aval_opponent_piece_count(estado: EstadoBT_40, jogador):
    """Função de avaliação que (des)valoriza o número de
    peças do adversário."""
    pieces_opponent = estado.pieces[jogador % 2]
    return len(pieces_opponent)


def func_aval_one_move_to_win(estado: EstadoBT_40, jogador):
    """Função de avaliação que valoriza uma vitória iminente
    (i.e., a uma jogada de vencer)."""
    res = 0
    n = len(estado.board)
    target, k = ((n - 1, -1), (0, 1))[jogador - 1]
    pieces = estado.pieces[jogador - 1]
    for row, col in pieces:
        if row == target + k and not estado.threat((row, col)):
            res += 1
    return res


def func_aval_home_ground(estado: EstadoBT_40, jogador):
    """Função de avaliação que valoriza peças na primeira linha,
    e, por conseguinte, a defesa."""
    n = len(estado.board)
    home = 0 if jogador == JogoBT_40.WHITE else n - 1
    res = 0
    pieces = estado.pieces[jogador - 1]
    for row, _ in pieces:
        if row == home:
            res += 1
    return res


def func_aval_piece_value(estado: EstadoBT_40, jogador):
    """Função de avaliação que valoriza o número de
    peças amigáveis."""
    res = 0
    n = len(estado.board)
    pieces = estado.pieces[jogador - 1]
    if jogador == JogoBT_40.WHITE:
        for row, _ in pieces:
            res += row + 1
    else:
        for row, _ in pieces:
            res += n - row
    return res


class JogadorBT_40(JogadorAlfaBeta):
    """Classe que representa um jogador de Breakthrough
    que usa a função de avaliação do grupo 40 no
    algoritmo alfa-beta."""

    def __init__(self, nome, depth):
        super().__init__(nome, depth, func_aval_40)

    def __str__(self) -> str:
        return self.nome

# IIA-2223
# Autores:
#  54685 - Francisco Correia
#  55855 - Francisco Maia
#  55955 - Alexandre Fonseca

from jogos import Game


class JogoBT_40(Game):
    def __init__(self):
        # self.initial = EstadoBT_40()
        pass

    def actions(self, state):
        return super().actions(state)

    def result(self, state, move):
        return super().result(state, move)

    def utility(self, state, player):
        return super().utility(state, player)

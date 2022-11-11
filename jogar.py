##Versão 11 Nov 2022 15:07

        
from random import *

##################################
# Classe Jogador 

class Jogador():
    def __init__(self, nome, fun):
        self.nome = nome
        self.fun = fun
    def display(self):
        print(nome+" ")


# Classe JogadorAlfaBeta 

class JogadorAlfaBeta(Jogador):
    def __init__(self, nome, depth,fun_eval):
        self.nome = nome
        self.fun = lambda game, state: alphabeta_cutoff_search_new(state,game,depth,eval_fn=fun_eval)
    def display(self):
        print(nome+" ")


from jogos import *

##########  para ser independente dos jogos deveria devolver um método em string ou um atributo
def joga11(game, jog1, jog2):
    ### jog1 e jog2 são jogadores com funções que dado um estado do jogo devolvem a jogada que escolheram
    ### devolve uma lista de jogadas e o resultado 1 se Brancas ganha -1 se Pretas ganha
    estado=game.initial
    proxjog = jog1
    lista_jogadas=[]
    while not game.terminal_test(estado):
 #       estado.display()
        jogada = proxjog.fun(game, estado)
#        p = game.to_move(estado)
        estado=game.result(estado,jogada)
        lista_jogadas.append(jogada)
        proxjog = jog2 if proxjog == jog1 else jog1
    #p jogou e ganhou
    return ((jog1.nome,jog2.nome),lista_jogadas, game.utility(estado,1))

from func_timeout import func_timeout, FunctionTimedOut

def joga11com_timeout(game,jog1, jog2, nsec):
    ### jog1 e jog2 são jogadores com funções que dado um estado do jogo devolvem a jogada que escolheram
    ### devolve uma lista de jogadas e o resultado 1 se Brancas ganha -1 se Pretas ganha
    estado=game.initial
    proxjog = jog1
    lista_jogadas=[]
    while not game.terminal_test(estado):
        try:
            ReturnedValue = func_timeout(nsec, proxjog.fun, args=(game, estado))
        except FunctionTimedOut:
            print("pim!", proxjog.nome)
            ReturnedValue = None    
        jogada = ReturnedValue
        if jogada == None:
            return ((jog1.nome,jog2.nome),lista_jogadas, -1 if proxjog==jog1 else 1)
        else:
 #           p = game.to_move(estado)
            estado=game.result(estado,jogada)
            lista_jogadas.append(jogada)
            proxjog = jog2 if proxjog == jog1 else jog1
        #p jogou e ganhou
    return ((jog1.nome,jog2.nome),lista_jogadas, game.utility(estado,1))

def jogaNN(game, listaJog, listaAdv, nsec=1):
    ### devolve uma lista de tuplos da forma (j1, j2, (lista de jogadas, vencedor))
    lista_jogos=[]
    j=0
    for jog in listaJog:
        for adv in listaAdv:
            if jog != adv:
                j +=1
                lista_jogos.append(joga11com_timeout(game, jog,adv, nsec))
                print(j,jog.nome, adv.nome)
    return lista_jogos



# -----------------  Mostra os jogos


def mostraJogo(game, logjog, verbose = False, step_by_step=False):
    (jogs,listajog,score)=logjog
    print(jogs[0],'vs',jogs[1])
    estado=game.initial
    for jog in listajog:
        if verbose:
            game.display(estado)
        if step_by_step:
            input()
        estado=game.result(estado,jog)
        if verbose:
            print()
            print("--> ", jog)
            print()
    if verbose:
        game.display(estado)
    print('Score:',estado.score)


#### função para fazer campeonatos e construir a tabela final


######## Funções para jogar e fazer torneios
def faz_campeonato(jogo, listaJogadores, nsec=10):
    ### faz todos os jogos com timeout de nsec por jogada
    campeonato = jogaNN(jogo, listaJogadores, listaJogadores, nsec)
    ### ignora as jogadas e contabiliza quem ganhou
    resultado_jogos = [(a,b,n) for ((a,b),x,n) in campeonato]
    tabela = dict([(jog.nome, 0) for jog in listaJogadores])
    for jogo in resultado_jogos:
        if jogo[2] == 1:
            tabela[jogo[0]] += 1
        else:
            tabela[jogo[1]] += 1
    classificacao = list(tabela.items())
    classificacao.sort(key=lambda p: -p[1])
    print("JOGADOR", "VITÓRIAS")
    for jog in classificacao:
        print('{:11}'.format(jog[0]), '{:>4}'.format(jog[1]))



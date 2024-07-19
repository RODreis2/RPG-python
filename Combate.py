import random
from Personagem import personagem
from Monstros import monstros


def combate():
    monstro = random.choice(monstros)
    print(f"combate iniciado com {monstro}")
    
    def atacar_primeiro(personagem, monstro):
        return personagem[4] >= monstro[4]
    
    if atacar_primeiro(personagem, monstro):
        # Imprime os ataques do personagem
        for i, ataque in enumerate(personagem['ataques']):
            print(f" {i}, Ataque: {personagem.ataques}")
    else:
        # Imprime o ataque do monstro
        print(f"O monstro utilizou o ataque {monstro.ataque}")

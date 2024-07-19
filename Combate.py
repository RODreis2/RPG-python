import random
from Personagem import personagem, ataques, nivel, dinheiro, xp
from monstros import monstros


def combate():
    monstro = random.choice(monstros)
    print(f"combate iniciado com {monstro}")
    
    def atacar_primeiro():
        if personagem[4] > monstro[4]:
            return True
        else:
            return False
    
    if atacar_primeiro:
        for i,n in range(ataques):
            print(i,n)
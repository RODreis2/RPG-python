import random
from Personagem import character
from Monstros import monster


def combat():
    Combat_monster = random.choice(monster)
    print(f"combate iniciado com {Combat_monster}")
    
    def atacar_primeiro(character, Combat_monster):
        return character.status[4] >= Combat_monster.status[4]
    
    if atacar_primeiro(character, Combat_monster):
        # Imprime os ataques do personagem
        for i, ataque in enumerate(character['ataques']):
            print(f" {i}, Ataque: {character.ataques}")
    else:
        # Imprime o ataque do Combat_monster
        print(f"O Combat_monster utilizou o ataque {Combat_monster.attack_methods}")

combat()
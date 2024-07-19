import random

class goblin:
    goblin1 = ["goblin", 30, 5, 10, 100]
    ataque = {"faca": random.randint(4, 7)}
    dinheiro = 10

class slime:
    slime1 = ["slime", 50, 2, 5, 200]
    ataque = {"tiro de gosma": 4}
    dinheiro = 2

class esqueleto:
    esqueleto1 = ["esqueleto", 40, 10, 7, 120]
    ataque = {"corte": random.randint(7, 10)}
    dinheiro = 10

monstros = [goblin, slime, esqueleto]



import random

class Enemy:
    def __init__(self, name, health, strengh, defense, experience, money, attack_methods):
        self.name = name
        self.health = health
        self.strengh = strengh
        self.defense = defense
        self.experience = experience
        self.money = money
        self.attack_methods = attack_methods

    def attack(self):
        # Implementar um sistema padrão de ataques
        pass

class Goblin(Enemy):
    def __init__(self):
        super().__init__(
            name="goblin",
            health=30,
            strengh=5,
            defense=10,
            experience=100,
            money=10,
            attack_methods={"faca": random.randint(4, 7)}
        )

class Slime(Enemy):
    def __init__(self):
        super().__init__(
            name="slime",
            health=50,
            strengh=2,
            defense=5,
            experience=200,
            money=2,
            attack_methods={"tiro de gosma": 4}
        )

class Skeleton(Enemy):
    def __init__(self):
        super().__init__(
            name="esqueleto",
            health=40,
            strengh=10,
            defense=7,
            experience=120,
            money=10,
            attack_methods={"corte": random.randint(7, 10)}
        )

monster = [Goblin, Slime, Skeleton]



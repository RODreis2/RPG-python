class Player:
    def __init__(self, name: str, strength: int, defense: int, speed: int, stamina: int, character_class: str):
        self.name = name
        self.strength = strength
        self.defense = defense
        self.speed = speed
        self.stamina = stamina
        self.character_class = character_class

    def get_status(self):
        print("Player Status: \n")
        print(f"Name: {self.name}")
        print(f"Strength: {self.strength}")
        print(f"Defense: {self.defense}")
        print(f"Speed: {self.speed}")
        print(f"Stamina: {self.stamina}")
        print(f"Class: {self.character_class}")
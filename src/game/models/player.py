from dataclasses import dataclass


@dataclass
class Player:
    name: str
    archetype: str
    max_hp: int
    hp: int
    max_mp: int
    mp: int
    strength: int
    defense: int
    speed: int
    gold: int = 20
    xp: int = 0
    level: int = 1
    potions: int = 1

    def is_alive(self) -> bool:
        return self.hp > 0

    def heal(self, amount: int) -> int:
        previous_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - previous_hp

    def restore_mp(self, amount: int) -> int:
        previous_mp = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - previous_mp

    def spend_mp(self, cost: int) -> bool:
        if cost <= 0:
            return True
        if self.mp < cost:
            return False
        self.mp -= cost
        return True

    def gain_xp(self, amount: int) -> bool:
        self.xp += amount
        leveled_up = False
        while self.xp >= self.level * 100:
            self.xp -= self.level * 100
            self.level += 1
            self.max_hp += 8
            self.hp = self.max_hp
            self.max_mp += 2
            self.mp = self.max_mp
            self.strength += 2
            self.defense += 1
            self.speed += 1
            leveled_up = True
        return leveled_up

    def stats_block(self) -> str:
        return (
            f"Name: {self.name}\n"
            f"Class: {self.archetype}\n"
            f"Level: {self.level}\n"
            f"HP: {self.hp}/{self.max_hp}\n"
            f"MP: {self.mp}/{self.max_mp}\n"
            f"Strength: {self.strength}\n"
            f"Defense: {self.defense}\n"
            f"Speed: {self.speed}\n"
            f"Gold: {self.gold}\n"
            f"XP: {self.xp}/{self.level * 100}\n"
            f"Potions: {self.potions}"
        )

from dataclasses import dataclass


@dataclass
class Monster:
    name: str
    hp: int
    strength: int
    defense: int
    speed: int
    xp_reward: int
    gold_reward: int

    def is_alive(self) -> bool:
        return self.hp > 0

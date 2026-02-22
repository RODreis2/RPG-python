import random

from ..models import Player


def train(player: Player) -> None:
    print("\n=== Training Grounds ===")
    print("You spend time improving your technique.")

    xp_gain = random.randint(20, 40)
    hp_cost = random.randint(4, 10)
    speed_gain = 1 if random.random() < 0.3 else 0

    player.hp = max(1, player.hp - hp_cost)
    player.strength += 1
    player.defense += 1
    if speed_gain:
        player.speed += 1

    leveled_up = player.gain_xp(xp_gain)
    print(f"Training complete: +1 Strength, +1 Defense, +{xp_gain} XP, -{hp_cost} HP.")
    if speed_gain:
        print("You also improved your speed by +1.")
    if leveled_up:
        print("You leveled up during training.")

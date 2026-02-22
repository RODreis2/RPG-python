import random

from ..models import Monster, Player


def _roll_damage(attacker_strength: int, defender_defense: int, bonus: int = 0) -> int:
    variance = random.randint(-2, 3)
    raw_damage = attacker_strength + bonus + variance
    mitigation = defender_defense // 2
    return max(1, raw_damage - mitigation)


def battle(player: Player, monster: Monster, class_skills: list[dict[str, float]]) -> bool:
    print(f"\nA wild {monster.name} appears!")

    while player.is_alive() and monster.is_alive():
        print(f"\n{player.name} HP: {player.hp}/{player.max_hp} | {monster.name} HP: {monster.hp}")

        player_turn_first = player.speed >= monster.speed
        if player_turn_first:
            _player_turn(player, monster, class_skills)
            if monster.is_alive():
                _monster_turn(player, monster)
        else:
            _monster_turn(player, monster)
            if player.is_alive():
                _player_turn(player, monster, class_skills)

    if player.is_alive():
        player.gain_xp(monster.xp_reward)
        player.gold += monster.gold_reward
        print(
            f"\nYou defeated {monster.name}! +{monster.xp_reward} XP, +{monster.gold_reward} gold."
        )
        return True

    print("\nYou were defeated. Game over.")
    return False


def _player_turn(player: Player, monster: Monster, class_skills: list[dict[str, float]]) -> None:
    print("Your action:")
    print("1. Basic Attack")
    print("2. Skill Attack")
    print("3. Use Potion")

    choice = input("> ").strip()
    if choice == "2" and class_skills:
        skill = random.choice(class_skills)
        hit_roll = random.random()
        if hit_roll <= skill["accuracy"]:
            damage = _roll_damage(player.strength, monster.defense, skill["bonus_damage"])
            monster.hp -= damage
            print(f"You used {skill['name']} and dealt {damage} damage.")
        else:
            print(f"You used {skill['name']} but missed.")
    elif choice == "3":
        if player.potions <= 0:
            print("You have no potions.")
            return
        player.potions -= 1
        healed = player.heal(25)
        print(f"You used a potion and restored {healed} HP.")
    else:
        damage = _roll_damage(player.strength, monster.defense)
        monster.hp -= damage
        print(f"You dealt {damage} damage.")


def _monster_turn(player: Player, monster: Monster) -> None:
    damage = _roll_damage(monster.strength, player.defense)
    player.hp -= damage
    print(f"{monster.name} hits you for {damage} damage.")

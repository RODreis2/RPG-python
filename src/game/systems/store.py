from ..models import Player


def open_store(player: Player, potion_catalog: list[dict]) -> None:
    print("\n=== Market ===")
    for index, potion in enumerate(potion_catalog, start=1):
        print(f"{index}. {potion['name']} ({potion['price']} gold) - {potion['description']}")
    print("0. Leave market")

    raw_choice = input("Choose an option: ").strip()
    if not raw_choice.isdigit():
        print("Invalid selection.")
        return

    choice = int(raw_choice)
    if choice == 0:
        return
    if choice < 1 or choice > len(potion_catalog):
        print("Invalid selection.")
        return

    potion = potion_catalog[choice - 1]
    if player.gold < potion["price"]:
        print("Not enough gold.")
        return

    player.gold -= potion["price"]
    player.potions += potion["stock_amount"]
    print(f"You bought {potion['name']}. Potions +{potion['stock_amount']}.")

from characters.player import Player

class Warrior:
    def create_warrior(self, player_name: str):
        warrior_player = Player(player_name, 18, 16, 9, 12, "Warrior")
        return warrior_player
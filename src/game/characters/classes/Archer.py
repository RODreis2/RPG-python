from characters.player import Player

class Archer:
    def create_archer(self, player_name: str):
        archer_player = Player(player_name, 10, 12, 18, 17, "Archer")
        return archer_player
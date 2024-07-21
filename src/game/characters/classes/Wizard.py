from characters.player import Player

class Wizard:
    def create_wizard(self, player_name: str):
        wizard_player = Player(player_name, 10, 14, 9, 10, "Warrior")
        return wizard_player
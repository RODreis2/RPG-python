from characters.player import Player
from characters.classes.Wizard import Wizard
from characters.classes.Warrior import Warrior
from characters.classes.Archer import Archer
import click

class Player_Manager:
    def __init__(self):
        self.player = None

    def setup_player(self, player_name: str, player_class: str):
        new_player = None
        click.echo(f"Character class: {player_class}")
        match player_class:
            case "Guerreiro":
                new_player = Wizard().create_wizard(player_name)
            case "Mago":
                new_player = Warrior().create_warrior(player_name)
            case "Arqueiro":
                new_player = Archer().create_archer(player_name)
        self.player = new_player

player_manager = Player_Manager()
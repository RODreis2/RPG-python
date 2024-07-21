import os
import click
from time import sleep
from cli.menus.start import start
from player.player_manager import player_manager

def start_game():
    character_options = start()
    print(character_options[0])
    player_manager.setup_player(character_options[1], character_options[0])
    click.clear()
    click.echo(f"Player Created:")
    click.echo(player_manager.player.get_status())

if __name__ == "__main__":
    start_game()

from time import sleep
import click

avaiable_classes = ("Guerreiro", "Mago", "Arqueiro")

def start():
    click.clear()
    print("Olá, Aventureiro! ")

    character_class = click.prompt("Selecione sua classe", type=click.Choice(avaiable_classes), show_choices=True)
    click.clear()
    character_name = click.prompt("Digite seu nome", type=str)
    return character_class, character_name
from Personagem import character
import click

def show_menu():
    print("========== MENU ==========")
    print("1. Ir para Dungeon")
    print("2. Ir para Loja")
    print("3. Olhar Equipamentos")
    print("4.Olhar Status")
    print("5. Sair do Jogo")
    print("==========================")

def go_dungeon():
    print("Você está entrando na dungeon...")
    #Escrever geração de mapa @joca

def go_store():
    print("Você está indo para a loja...")
    #Integrar o json com a loja e exibir

def look_equipment():
    print("Aqui estão seus equipamentos")
    #exibir os equipamentos 

def look_status():
    print("Estes são os seus status")
    print(character.status)
    #melhorar isso

def Leave_game():
    print("Saindo do jogo. Até a próxima!")

def menu_principal():
        click.clear()
        show_menu()
        menu_escolha = click.prompt("Escolha uma opção: ", type=click.IntRange(1,5), show_choices=True)
        if menu_escolha == '1':
            go_dungeon()
        elif menu_escolha == '2':
            go_store()
        elif menu_escolha == '3':
            look_equipment()
        elif menu_escolha == '4':
            look_status()
        elif menu_escolha == '5':
            Leave_game()
            
    

if __name__ == "__main__":
    menu_principal()
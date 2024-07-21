from Personagem import character
import click

def mostrar_menu():
    print("========== MENU ==========")
    print("1. Ir para Dungeon")
    print("2. Ir para Loja")
    print("3. Olhar Equipamentos")
    print("4.Olhar Status")
    print("5. Sair do Jogo")
    print("==========================")

def ir_para_dungeon():
    print("Você está entrando na dungeon...")
    #Escrever geração de mapa @joca

def ir_para_loja():
    print("Você está indo para a loja...")
    #Integrar o json com a loja e exibir

def olhar_equipamentos():
    print("Aqui estão seus equipamentos")
    #exibir os equipamentos 

def olhar_status():
    print("Estes são os seus status")
    print(character.status)
    #melhorar isso

def sair_do_jogo():
    print("Saindo do jogo. Até a próxima!")

def menu_principal():
        click.clear()
        mostrar_menu()
        menu_escolha = click.prompt("Escolha uma opção: ", type=click.IntRange(1,5), show_choices=True)
        if menu_escolha == '1':
            ir_para_dungeon()
        elif menu_escolha == '2':
            ir_para_loja()
        elif menu_escolha == '3':
            olhar_equipamentos()
        elif menu_escolha == '4':
            olhar_status()
        elif menu_escolha == '5':
            sair_do_jogo()
            
    

if __name__ == "__main__":
    menu_principal()
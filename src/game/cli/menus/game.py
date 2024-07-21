from Personagem import character

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
    while True:
        mostrar_menu()
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            ir_para_dungeon()
        elif escolha == '2':
            ir_para_loja()
        elif escolha == '3':
            olhar_equipamentos()
        elif escolha == '4':
            olhar_status()
        elif escolha == '5':
            sair_do_jogo()
            break
        else:
            print("Opção inválida! Tente novamente.")
            continue

if __name__ == "__main__":
    menu_principal()
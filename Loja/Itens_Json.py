import game.py

if menu_escolha == 3:
    print("=======Loja=======")
    print("1- Poções")
    print("2- Ferramentas")
    print("3- Armaduras")
    print("==================")
    itens_loja = str(input("qual deseja observar? "))
    if itens_loja == "1":
        with open('Potions.json', 'r') as file:
            data = json.load(file)
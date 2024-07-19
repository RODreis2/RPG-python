personagem = []



print("[G]uerreiro, [A]rqueiro, [M]ago")
Escolha_classe = str(input("digite a primeira letra de sua classe sua classe: ")).upper()

def classe(nome, vida, forca, velocidade):
    global personagem
    personagem = []
    personagem.append(nome)
    personagem.append(vida)
    personagem.append(forca)
    personagem.append(velocidade)

while Escolha_classe != "G" and Escolha_classe != "A" and Escolha_classe != "M": 
    print("guerreiro, arqueiro, mago")
    Escolha_classe = str(input("Você digitou errado por favor digite a primeira letra de sua classe sua classe: ")).upper()

nome = str(input("digite o nome do seu personagem: "))

if Escolha_classe == "G":
    guerreiro = classe(nome,150, 25, 8)  

elif Escolha_classe == "A":
    arqueiro = classe(nome, 75, 15, 30)

elif Escolha_classe == "M":
    mago = classe(nome, 50, 35, 10)

print(personagem)
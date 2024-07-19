class personagem:
    global status
    global ataques
    status = []
    ataques = {}
    nivel = 1
    xp = 0
    dinheiro = 100

def classe(nome, vida, forca, velocidade, estamina):
    global status
    status = []
    status.append(nome)
    status.append(vida)
    status.append(forca)
    status.append(velocidade)
    status.append(estamina)

print("[G]uerreiro, [A]rqueiro, [M]ago")
Escolha_classe = str(input("digite a primeira letra de sua classe sua classe: ")).upper()

while Escolha_classe != "G" and Escolha_classe != "A" and Escolha_classe != "M": 
    print("guerreiro, arqueiro, mago")
    Escolha_classe = str(input("Você digitou errado por favor digite a primeira letra de sua classe sua classe: ")).upper()

nome = str(input("digite o nome do seu status: "))

if Escolha_classe == "G":
    guerreiro = classe(nome,150, 25, 8, 150)
    ataques = {"corte":10, "corte flamejante":15}  

elif Escolha_classe == "A":
    arqueiro = classe(nome, 75, 15, 30, 200)
    ataques = {"flecha simples":10, "chuva de flechas":25}  

elif Escolha_classe == "M":
    mago = classe(nome, 50, 35, 10, 300)
    ataques = {"espinhos de pedra":20, "bola de fogo":50}
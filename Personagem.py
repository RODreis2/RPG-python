class character:
    global status
    global attacks
    status = []
    attacks = {}
    level = 1
    xp = 0
    money = 100

def Player_class(name, life, strengh, speed, stamina):
    global status
    status = []
    status.append(name)
    status.append(life)
    status.append(strengh)
    status.append(speed)
    status.append(stamina)

print("[G]uerreiro, [A]rqueiro, [M]ago")
Chose_Player_class = str(input("digite a primeira letra de sua classe sua classe: ")).upper()

while Chose_Player_class != "G" and Chose_Player_class != "A" and Chose_Player_class != "M": 
    print("guerreiro, arqueiro, mago")
    Chose_Player_class = str(input("Você digitou errado por favor digite a primeira letra de sua classe sua classe: ")).upper()

name = str(input("digite o name do seu persoangem: "))

if Chose_Player_class == "G":
    guerreiro = Player_class(name,150, 25, 8, 150)
    attacks = {"corte":10, "corte flamejante":15}  

elif Chose_Player_class == "A":
    arqueiro = Player_class(name, 75, 15, 30, 200)
    attacks = {"flecha simples":10, "chuva de flechas":25}  

elif Chose_Player_class == "M":
    mago = Player_class(name, 50, 35, 10, 300)
    attacks = {"espinhos de pedra":20, "bola de fogo":50}
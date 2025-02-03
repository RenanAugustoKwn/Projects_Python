print("Seja muito bem-vindo ao quiz!!")
answer_user = input("Quer começar? (S/N): ")
if answer_user.upper() != "S":
    quit()

print("Começando...")

score = 0

def fazer_pergunta(pergunta, opcoes, resposta_correta):
    global score
    print(pergunta)
    for opcao in opcoes:
        print(opcao)
    resposta = input("Resposta: ").upper()
    if resposta == resposta_correta:
        print("Correto!")
        score += 1
    else:
        print("Incorreto!")

fazer_pergunta("Que herói usa escudo?", ["(A) Capitão América", "(B) Thor", "(C) Homem-Aranha"], "A")
fazer_pergunta("Quem é o deus do trovão?", ["(A) Loki", "(B) Thor", "(C) Odin"], "B")
fazer_pergunta("Qual é a identidade secreta do Homem-Aranha?", ["(A) Tony Stark", "(B) Bruce Wayne", "(C) Peter Parker"], "C")
fazer_pergunta("Quem criou o traje do Homem de Ferro?", ["(A) Bruce Banner", "(B) Tony Stark", "(C) Reed Richards"], "B")
fazer_pergunta("Qual é o nome do martelo do Thor?", ["(A) Stormbreaker", "(B) Mjolnir", "(C) Excalibur"], "B")
fazer_pergunta("Quem é o líder dos Vingadores?", ["(A) Capitão América", "(B) Hulk", "(C) Viúva Negra"], "A")
fazer_pergunta("Qual é o nome do vilão principal de Vingadores: Guerra Infinita?", ["(A) Loki", "(B) Thanos", "(C) Ultron"], "B")
fazer_pergunta("Qual é o nome verdadeiro do Pantera Negra?", ["(A) T'Challa", "(B) Shuri", "(C) Erik"], "A")
fazer_pergunta("Qual herói tem garras de adamantium?", ["(A) Wolverine", "(B) Deadpool", "(C) Ciclope"], "A")
fazer_pergunta("Qual o nome do pai de Thor?", ["(A) Loki", "(B) Odin", "(C) Hela"], "B")
fazer_pergunta("Quem é o amigo fiel do Capitão América?", ["(A) Tony Stark", "(B) Bucky Barnes", "(C) Nick Fury"], "B")
fazer_pergunta("Quem é o rei de Asgard após Thor?", ["(A) Loki", "(B) Valquíria", "(C) Odin"], "B")
fazer_pergunta("Qual o nome do planeta natal do Hulk?", ["(A) Sakaar", "(B) Terra", "(C) Vormir"], "A")
fazer_pergunta("Quem é a irmã de Pantera Negra?", ["(A) Okoye", "(B) Nakia", "(C) Shuri"], "C")
fazer_pergunta("Quem é o antagonista de Pantera Negra?", ["(A) Erik Killmonger", "(B) Ulysses Klaue", "(C) Baron Zemo"], "A")
fazer_pergunta("Quem criou o Ultron?", ["(A) Bruce Banner e Tony Stark", "(B) Steve Rogers", "(C) Hank Pym"], "A")
fazer_pergunta("Quem é a feiticeira mais poderosa do MCU?", ["(A) Wanda Maximoff", "(B) Agatha Harkness", "(C) Doutor Estranho"], "A")
fazer_pergunta("Qual é o nome verdadeiro do Gavião Arqueiro?", ["(A) Clint Barton", "(B) Scott Lang", "(C) Sam Wilson"], "A")
fazer_pergunta("Quem assumiu o manto do Capitão América após Steve Rogers?", ["(A) Sam Wilson", "(B) Bucky Barnes", "(C) Tony Stark"], "A")
fazer_pergunta("Onde a Joia da Alma estava escondida?", ["(A) Wakanda", "(B) Vormir", "(C) Sakaar"], "B")

print(f"Quiz finalizado! Você acertou {score} de 21 perguntas!")

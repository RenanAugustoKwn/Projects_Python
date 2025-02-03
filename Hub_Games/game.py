import pygame as py
import random
from sys import exit

py.init()

# Configurações do jogo
largura, altura = 640, 480
tamanho_celula = 20
velocidade = 10

# Cores
verde = (0, 255, 0)
vermelho = (255, 0, 0)
preto = (0, 0, 0)
branco = (255, 255, 255)

# Inicialização da tela
tela = py.display.set_mode((largura, altura))
py.display.set_caption("Hub de Jogos")

# Função para desenhar texto
def desenhar_texto(texto, tamanho, x, y):
    fonte = py.font.Font(None, tamanho)
    superficie_texto = fonte.render(texto, True, branco)
    tela.blit(superficie_texto, (x, y))

# Função para selecionar jogo
def selecionar_jogo():
    while True:
        tela.fill(preto)
        desenhar_texto("Selecione um jogo", 40, 200, 100)
        desenhar_texto("1 - Snake", 30, 250, 200)
        desenhar_texto("2 - Flappy Bird", 30, 250, 250)
        desenhar_texto("3 - Pac-Man", 30, 250, 300)
        
        py.display.update()
        
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                exit()
            elif event.type == py.KEYDOWN:
                if event.key == py.K_1:
                    jogar_snake()
                elif event.key == py.K_2:
                    jogar_flappy_bird()
                elif event.key == py.K_3:
                    jogar_pacman()

# Função para gerar nova posição aleatória
def nova_posicao():
    x = random.randrange(0, largura, tamanho_celula)
    y = random.randrange(0, altura, tamanho_celula)
    return x, y

# Função do jogo Snake
def jogar_snake():
    cobra = [(largura // 2, altura // 2)]
    direcao = (tamanho_celula, 0)
    comida = nova_posicao()
    clock = py.time.Clock()

    while True:
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                exit()
            elif event.type == py.KEYDOWN:
                if event.key == py.K_UP and direcao != (0, tamanho_celula):
                    direcao = (0, -tamanho_celula)
                elif event.key == py.K_DOWN and direcao != (0, -tamanho_celula):
                    direcao = (0, tamanho_celula)
                elif event.key == py.K_LEFT and direcao != (tamanho_celula, 0):
                    direcao = (-tamanho_celula, 0)
                elif event.key == py.K_RIGHT and direcao != (-tamanho_celula, 0):
                    direcao = (tamanho_celula, 0)

        nova_cabeca = (cobra[0][0] + direcao[0], cobra[0][1] + direcao[1])
        cobra.insert(0, nova_cabeca)
        
        if nova_cabeca == comida:
            comida = nova_posicao()
        else:
            cobra.pop()
        
        if (
            nova_cabeca[0] < 0 or nova_cabeca[0] >= largura or
            nova_cabeca[1] < 0 or nova_cabeca[1] >= altura or
            nova_cabeca in cobra[1:]
        ):
            break

        tela.fill(preto)
        for segmento in cobra:
            py.draw.rect(tela, verde, (*segmento, tamanho_celula, tamanho_celula))
        py.draw.rect(tela, vermelho, (*comida, tamanho_celula, tamanho_celula))
        
        py.display.update()
        clock.tick(velocidade)
    
    selecionar_jogo()

# Funções vazias para Flappy Bird e Pac-Man (precisam ser implementadas)
def jogar_flappy_bird():
    pass

def jogar_pacman():
    pass

# Inicia o hub de jogos
selecionar_jogo()
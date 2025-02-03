import pygame as py
import random
import os
from sys import exit

py.init()

# Configurações do jogo
largura, altura = 500, 800
tamanho_celula = 20
velocidadeSnake = 10

# Carregar Imagens
imagem_cano = py.transform.scale2x(py.image.load(os.path.join("imgs", "pipe.png")))
imagem_chao = py.transform.scale2x(py.image.load(os.path.join("imgs", "base.png")))
imagem_background = py.transform.scale2x(py.image.load(os.path.join("imgs", "bg.png")))
imagem_passaro = [
    py.transform.scale2x(py.image.load(os.path.join("imgs", "bird1.png"))),
    py.transform.scale2x(py.image.load(os.path.join("imgs", "bird2.png"))),
    py.transform.scale2x(py.image.load(os.path.join("imgs", "bird3.png"))),
]

fonte_pontos = py.font.SysFont("arial", 20)

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
            nova_cabeca[0] < 0
            or nova_cabeca[0] >= largura
            or nova_cabeca[1] < 0
            or nova_cabeca[1] >= altura
            or nova_cabeca in cobra[1:]
        ):
            break

        tela.fill(preto)
        for segmento in cobra:
            py.draw.rect(tela, verde, (*segmento, tamanho_celula, tamanho_celula))
        py.draw.rect(tela, vermelho, (*comida, tamanho_celula, tamanho_celula))

        py.display.update()
        clock.tick(velocidadeSnake)

    selecionar_jogo()


class Passaro:
    imgs = imagem_passaro

    # Anaimacao de rotacao
    rotacao_max = 25
    velocidade_rot = 20
    tempo_anim = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.imgs[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.rotacao_max:
                self.angulo = self.rotacao_max
        else:
            if self.angulo > -90:
                self.angulo -= self.velocidade_rot

    def desenhar(self, tela):
        # Criando passaro e animcao
        self.contagem_imagem += 1
        if self.contagem_imagem < self.tempo_anim:
            self.imagem = self.imgs[0]
        elif self.contagem_imagem < self.tempo_anim * 2:
            self.imagem = self.imgs[1]
        elif self.contagem_imagem < self.tempo_anim * 3:
            self.imagem = self.imgs[2]
        elif self.contagem_imagem < self.tempo_anim * 4:
            self.imagem = self.imgs[1]
        elif self.contagem_imagem >= self.tempo_anim * 4 + 1:
            self.imagem = self.imgs[0]
            self.contagem_imagem = 0

        # Passaro caindo
        if self.angulo <= -80:
            self.imagem = self.imgs[1]
            self.contagem_imagem = self.tempo_anim * 2

        # Desenhar Passaro
        imagem_rotacionada = py.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return py.mask.from_surface(self.imagem)


class Cano:
    distancia = 200
    velocidade = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.cano_topo = py.transform.flip(imagem_cano, False, True)
        self.cano_base = imagem_cano
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.cano_topo.get_height()
        self.pos_base = self.altura + self.distancia

    def mover(self):
        self.x -= self.velocidade

    def desenhar(self, tela):
        tela.blit(self.cano_topo, (self.x, self.pos_topo))
        tela.blit(self.cano_base, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = py.mask.from_surface(self.cano_topo)
        base_mask = py.mask.from_surface(self.cano_base)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    velocidade = 5
    larguraChao = imagem_chao.get_width()
    imagem = imagem_chao

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.larguraChao

    def mover(self):
        self.x1 -= self.velocidade
        self.x2 -= self.velocidade

        if self.x1 + self.larguraChao < 0:
            self.x1 = self.x2 + self.larguraChao

        if self.x2 + self.larguraChao < 0:
            self.x2 = self.x1 + self.larguraChao

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x1, self.y))
        tela.blit(self.imagem, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(imagem_background, (0, 0))

    for passaro in passaros:
        passaro.desenhar(tela)

    for cano in canos:
        cano.desenhar(tela)

    texto = fonte_pontos.render(f"Score: {pontos}", 1, (255, 255, 255))

    tela.blit(texto, (largura - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    py.display.update()


def jogar_flappy_bird():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    pontos = 0
    clock = py.time.Clock()

    rodando = True
    while rodando:
        clock.tick(30)

        for event in py.event.get():
            if event.type == py.QUIT:
                rodando = False
                py.quit()
                quit()
            if event.type == py.KEYDOWN:
                if event.key == py.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()

        for passaro in passaros:
            passaro.mover()

        chao.mover()

        add_cano = False
        remover_canos = []

        for cano in canos:
            for i, passaro in enumerate(passaros):  
                if cano.colidir(passaro):
                    passaros.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    add_cano = True

                cano.mover()

                if cano.x + cano.cano_topo.get_width() < 0:
                    remover_canos.append(cano)

        if add_cano:
            pontos += 1
            canos.append(Cano(600))

        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_width()) > chao.y or passaro.y < 0:
                passaros.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontos)


def jogar_pacman():
    pass


# Inicia o hub de jogos
selecionar_jogo()

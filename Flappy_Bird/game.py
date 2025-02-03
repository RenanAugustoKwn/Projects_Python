import pygame as py
from pygame.locals import *
from sys import exit

py.init()

largura = 640
altura = 480

tela = py.display.set_mode((largura, altura))
py.display.set_caption("Flappy_Bird")

while True:
    for event in py.event.get():
        if event.type == QUIT:
            py.quit()
            exit()

    py.display.update()

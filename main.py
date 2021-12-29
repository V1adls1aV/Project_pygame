import pygame
import os
import sys

pygame.init()
size = width, height = 1920, 1080
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 60


def load_image(name, colorkey=None):
    file_name = os.path.join('data', name)
    if not os.path.isfile(file_name):
        print('ФАЙЛА НЕТ: ' + file_name)
        sys.exit()
    image = pygame.image.load(file_name)
    if colorkey is not None:
        if colorkey == 1:
            colorkey = image.get_at((1, 1))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    screen.fill((0, 0, 0))
    pygame.display.flip()
    clock.tick(FPS)

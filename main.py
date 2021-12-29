import pygame
import os
import sys

pygame.init()
size = WIDTH, HEIGHT = 1920, 1020
tile_width, tile_height = 300, 300
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 60

tiles_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    filename = os.path.join('data', name)
    if not os.path.isfile(filename):
        print('ФАЙЛА НЕТ: ' + filename)
        sys.exit()
    image = pygame.image.load(filename)
    if colorkey is not None:
        if colorkey == 1:
            colorkey = image.get_at((1, 1))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(name):
    filename = os.path.join('data', name)
    if not os.path.isfile(filename):
        print('ФАЙЛА НЕТ: ' + filename)
        sys.exit()
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку клетками с домами ('#')
    return [['#'] * (max_width + 2)] + list(map(
        lambda x: ['#'] + list(x) + ['#'] * (max_width - len(x)) + ['#'],
        level_map)) + [['#'] * (max_width + 2)]


def generate_level(level):
    new_level = [el[:] for el in level]
    for y in range(len(level)):
        for x in range(len(level[0])):
            if level[y][x] == '#':
                new_level[y][x] = House(x, y)
            elif level[y][x] == '.':
                if level[y + 1][x] == '.' and level[y - 1][x] == '.'\
                        and level[y][x + 1] == '.' and level[y][x - 1] == '.':
                    new_level[y][x] = Road(x, y, '+')
                elif level[y + 1][x] == '.' and level[y - 1][x] == '.' and level[y][x + 1] == '.':
                    new_level[y][x] = Road(x, y, 'V')
                elif level[y + 1][x] == '.' and level[y - 1][x] == '.' and level[y][x - 1] == '.':
                    new_level[y][x] = Road(x, y, 'V', 180)
                elif level[y + 1][x] == '.' and level[y][x + 1] == '.' and level[y][x - 1] == '.':
                    new_level[y][x] = Road(x, y, 'V', 270)
                elif level[y - 1][x] == '.' and level[y][x + 1] == '.' and level[y][x - 1] == '.':
                    new_level[y][x] = Road(x, y, 'V', 90)
                elif level[y + 1][x] == '.' and level[y][x + 1] == '.':
                    new_level[y][x] = Road(x, y, 'L', 270)
                elif level[y + 1][x] == '.' and level[y][x - 1] == '.':
                    new_level[y][x] = Road(x, y, 'L', 180)
                elif level[y - 1][x] == '.' and level[y][x + 1] == '.':
                    new_level[y][x] = Road(x, y, 'L')
                elif level[y - 1][x] == '.' and level[y][x - 1] == '.':
                    new_level[y][x] = Road(x, y, 'L', 90)
                elif level[y + 1][x] == '.' or level[y - 1][x] == '.':
                    new_level[y][x] = Road(x, y, 'I')
                elif level[y][x + 1] == '.' or level[y][x - 1] == '.':
                    new_level[y][x] = Road(x, y, 'I', 90)
    return new_level


class Road(pygame.sprite.Sprite):
    def __init__(self, x, y, mode, rotation=0):
        super().__init__(tiles_group)
        self.mode = mode
        self.rotation = rotation
        self.image = self.generate_road_image()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * tile_width, y * tile_height

    def generate_road_image(self):
        if self.mode == '+':
            return pygame.transform.rotate(load_image('crossroad.png'), self.rotation)
        elif self.mode == 'V':
            return pygame.transform.rotate(load_image('fork.png'), self.rotation)
        elif self.mode == 'L':
            return pygame.transform.rotate(load_image('corner.png'), self.rotation)
        elif self.mode == 'I':
            return pygame.transform.rotate(load_image('line.png'), self.rotation)


class House(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group)
        self.image = load_image('house.png')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * tile_width, y * tile_height


city = generate_level(load_level('map.txt'))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

import pygame
import os
import sys
from math import sin, cos, pi
from random import randint

pygame.init()
size = WIDTH, HEIGHT = 1920, 1020
tile_width, tile_height = 300, 300
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 60

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
empty_group = pygame.sprite.Group()
police_group = pygame.sprite.Group()
covers = []


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    filename = os.path.join('data', name)
    if not os.path.isfile(filename):
        print('ФАЙЛА НЕТ: ' + filename)
        sys.exit()
    image = pygame.image.load(filename)
    if color_key is not None:
        if color_key == 1:
            color_key = image.get_at((1, 1))
        image.set_colorkey(color_key)
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
    f = True
    gamer = None
    finish_tile = None
    modification_tile = None
    len_x = len(level[0])
    len_y = len(level)
    for y in range(len_y):
        for x in range(len_x):
            if level[y][x] == '#':
                new_level[y][x] = Empty(x, y)

            elif level[y][x] == '.':
                new_level[y][x] = Road(x, y, *create_road_direction(level, x, y))
                if f:
                    gamer = Player(x, y)
                    f = False

            elif level[y][x] == ',':
                new_level[y][x] = Road(x, y, 'P')
                if f:
                    gamer = Player(x, y)
                    f = False

            elif level[y][x] == '@':
                finish_tile = new_level[y][x] = Finish(x, y, *create_road_direction(level, x, y))

            elif level[y][x] == 'X':
                new_level[y][x] = Police(x, y, *create_road_direction(level, x, y))

            elif level[y][x] == '$':
                modification_tile = new_level[y][x] = Modification(x, y, *create_road_direction(level, x, y))

    return new_level, gamer, finish_tile, modification_tile


def create_road_direction(level, x, y):
    if compare_road_type(level[y + 1][x]) and compare_road_type(level[y - 1][x]) \
            and compare_road_type(level[y][x + 1]) and compare_road_type(level[y][x - 1]):
        return '+'
    elif compare_road_type(level[y + 1][x]) and compare_road_type(level[y - 1][x]) \
            and compare_road_type(level[y][x + 1]):
        return 'V'
    elif compare_road_type(level[y - 1][x]) and compare_road_type(level[y][x + 1]) \
            and compare_road_type(level[y][x - 1]):
        return 'V', 90
    elif compare_road_type(level[y + 1][x]) and compare_road_type(level[y - 1][x]) \
            and compare_road_type(level[y][x - 1]):
        return 'V', 180
    elif compare_road_type(level[y + 1][x]) and compare_road_type(level[y][x + 1]) \
            and compare_road_type(level[y][x - 1]):
        return 'V', 270
    elif compare_road_type(level[y + 1][x]) and compare_road_type(level[y][x + 1]):
        return 'L', 270
    elif compare_road_type(level[y + 1][x]) and compare_road_type(level[y][x - 1]):
        return 'L', 180
    elif compare_road_type(level[y - 1][x]) and compare_road_type(level[y][x - 1]):
        return 'L', 90
    elif compare_road_type(level[y - 1][x]) and compare_road_type(level[y][x + 1]):
        return 'L'
    elif compare_road_type(level[y][x + 1]) or compare_road_type(level[y][x - 1]):
        return 'I', 90
    elif compare_road_type(level[y + 1][x]) or compare_road_type(level[y - 1][x]):
        return 'I'
    return 'P'


def compare_road_type(t):
    if t == '.' or t == 'X' or t == '@' or t == '$':
        return True
    return False


def start_screen():
    menu = Menu()
    menu.add_option(0, 'Lamborghini')
    menu.add_option(0, 'Ferrari')
    menu.add_option(1, 'town')
    menu.add_option(1, 'city')
    menu.add_option(1, 'mega_city')
    menu.add_option(2, 'Начать игру', None)
    menu.add_option(2, 'Выйти', terminate)

    background = load_image('start_screen.png')
    run = True
    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                terminate()

            but = pygame.key.get_pressed()
            if but[pygame.K_UP]:
                menu.change(0, -1)
            if but[pygame.K_DOWN]:
                menu.change(0, 1)
            if but[pygame.K_LEFT]:
                menu.change(-1, 0)
            if but[pygame.K_RIGHT]:
                menu.change(1, 0)
            if but[pygame.K_SPACE]:
                run = menu.choose()

        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        menu.draw(100, 100, 500, 200)
        pygame.display.flip()
        clock.tick(FPS)
    return menu


def end_screen(res):
    rotation = 0
    new_size = 1200
    font_size = 800
    victory_font = None
    h = -470
    if res is not None:
        background = load_image('win_screen.png')
        result_image = res
        victory_font = pygame.font.Font(None, 500)
    else:
        background = load_image('defeat_screen.png')
        result_image = load_image('banned.png')

    run = True
    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                terminate()

        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        if res is not None:
            font = pygame.font.Font(None, font_size)
            if font_size > 450:
                font_size -= 15
                rotation += 15
                h += 20
            screen.blit(victory_font.render('VICTORY', True, (255, 155, 0)), (192, h))
            screen.blit(pygame.transform.rotate(
                font.render(str(result_image), True, (255, 155, 0)), rotation),
                ((WIDTH - font_size) // 2, (HEIGHT - font_size) // 2))
        else:
            screen.blit(pygame.transform.scale(pygame.transform.rotate(
                result_image, rotation), (new_size, new_size)),
                ((WIDTH - new_size) // 2, (HEIGHT - new_size) // 2))
            if new_size > 850:
                new_size -= 15
                rotation += 15
        pygame.display.flip()
        clock.tick(FPS)


class Menu:
    def __init__(self):
        self.buttons = [[], [], []]
        self.now_button_0 = 0
        self.now_button_1 = 0
        self.now_button_2 = 0
        self.now_column = 0
        self.car = None
        self.location = None

    def add_option(self, column, option, *function):
        if function:
            self.buttons[column].append([option, *function])
        else:
            self.buttons[column].append(option)

    def draw(self, x, y, delta_x, delta_y):
        font = pygame.font.Font(None, 100)
        for i in range(len(self.buttons[0])):
            if self.now_button_0 == i:

                screen.blit(font.render(self.buttons[0][i], True, (255, 155, 0)),
                            (x, y + delta_y * i))
            else:
                screen.blit(font.render(self.buttons[0][i], True, (255, 255, 0)),
                            (x, y + delta_y * i))

        for i in range(len(self.buttons[1])):
            if self.now_button_1 == i:
                screen.blit(font.render(self.buttons[1][i], True, (255, 155, 0)),
                            (x + delta_x, y + delta_y * i))
            else:
                screen.blit(font.render(self.buttons[1][i], True, (255, 255, 0)),
                            (x + delta_x, y + delta_y * i))

        for i in range(len(self.buttons[2])):
            if self.now_button_2 == i:
                screen.blit(font.render(self.buttons[2][i][0], True, (255, 155, 0)),
                            (x + delta_x + delta_x, y + delta_y * i))
            else:
                screen.blit(font.render(self.buttons[2][i][0], True, (255, 255, 0)),
                            (x + delta_x + delta_x, y + delta_y * i))

    def change(self, delta_x, delta_y):
        if delta_x:
            self.now_column += delta_x
            self.now_column = max(0, min(self.now_column, 2))
        if delta_y:
            if self.now_column == 0:
                self.now_button_0 += delta_y
                self.now_button_0 = max(0, min(self.now_button_0, len(self.buttons[0]) - 1))
            elif self.now_column == 1:
                self.now_button_1 += delta_y
                self.now_button_1 = max(0, min(self.now_button_1, len(self.buttons[1]) - 1))
            elif self.now_column == 2:
                self.now_button_2 += delta_y
                self.now_button_2 = max(0, min(self.now_button_2, len(self.buttons[2]) - 1))

    def choose(self):
        if self.now_column == 2:
            if self.buttons[2][self.now_button_2][1] is not None:
                self.buttons[2][self.now_button_2][1]()
                return True
            self.car = self.buttons[0][self.now_button_0]
            self.location = self.buttons[1][self.now_button_1]
            return False
        return True

    def result(self):
        return self.car, self.location


class Empty(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(empty_group, tiles_group, all_sprites)
        self.image = load_image(f'house_{randint(1, 5)}.png')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * tile_width, y * tile_height


class Road(pygame.sprite.Sprite):
    def __init__(self, x, y, m, rotation=0):
        super().__init__(tiles_group, all_sprites)
        self.mode = m
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
        elif self.mode == 'P':
            return pygame.transform.rotate(load_image('parking.png'), 90 * randint(0, 3))


class Police(Road):
    def __init__(self, x, y, m, rotation=0):
        super().__init__(x, y, m, rotation)
        police_group.add(self)
        covers.append(self)
        self.police_image = pygame.transform.rotate(load_image('police_car.png'), 90 * randint(0, 3))
        self.mask = pygame.mask.from_surface(self.police_image)
        self.f = True

        self.frames = []
        self.now_frame = 0
        self.boom_f = False
        self.boom_image = None
        self.frames_set = load_image('boom.png')
        self.generate_frames(8, 4)

    def show(self):
        if self.f:
            screen.blit(self.police_image, (self.rect.x, self.rect.y))
        elif self.boom_f and self.now_frame < 25:
            self.change_image()

    def generate_frames(self, columns, rows):
        w, h = self.frames_set.get_size()
        for i in range(rows):
            for j in range(columns):
                self.frames.append(self.frames_set.subsurface(
                    pygame.Rect((j * w // columns, i * h // rows), self.rect.size)))

    def change_image(self):
        self.boom_image = self.frames[int(self.now_frame)]
        screen.blit(self.boom_image, (self.rect.x, self.rect.y))
        self.now_frame += 1


class Modification(Road):
    def __init__(self, x, y, m, rotation=0):
        super().__init__(x, y, m, rotation)
        covers.append(self)
        self.modification_image = load_image('modification_image.png')
        self.mask = pygame.mask.from_surface(self.modification_image)
        self.delta = 0
        self.direction = False
        self.animation = False
        self.new_size = 280
        self.rotation = 0
        self.f = True

    def check_modify(self):
        if pygame.sprite.collide_mask(self, player):
            player.modify = True
            return True
        return False

    def show(self):
        if self.animation and self.new_size:
            screen.blit(pygame.transform.scale(pygame.transform.rotate(
                self.modification_image, self.rotation),
                (self.new_size, self.new_size)),
                (self.rect.x + (300 - self.new_size) // 2,
                 self.rect.y + (self.delta + 300 - self.new_size) // 2))
            self.rotation += 10
            self.new_size -= 20
        elif self.check_modify():
            self.f = False
            self.animation = True
        elif self.f:
            screen.blit(self.modification_image, (self.rect.x, self.rect.y + self.delta))
            if self.delta <= -15:
                self.direction = False
            if self.delta >= 15:
                self.direction = True
            if self.direction:
                self.delta -= 1
            else:
                self.delta += 1


class Finish(Road):
    def __init__(self, x, y, m, rotation=0):
        super().__init__(x, y, m, rotation)
        covers.append(self)
        self.mask = pygame.mask.from_surface(self.image)
        self.finish_image = load_image('finish.png')

    def check_finish(self, gamer):
        offset = (gamer.rect.x - self.rect.x, gamer.rect.y - self.rect.y)
        if gamer.mask.count() == self.mask.overlap_area(gamer.mask, offset):
            gamer.f = True
            return gamer.get_time(), True
        if gamer.f:
            return None, True
        return None, None

    def show(self):
        screen.blit(self.finish_image, (self.rect.x, self.rect.y))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = load_image(f'{car}.png')
        self.start_image = self.image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 25 + x * tile_width, 25 + y * tile_height
        if car == 'Lamborghini':
            self.max_front_speed = 30
            self.max_rear_speed = 7
            self.acceleration = 0.4
        elif car == 'Ferrari':
            self.max_front_speed = 25
            self.max_rear_speed = 10
            self.acceleration = 0.6
        self.speed = 0
        self.rotation = 0
        self.dx = 0
        self.dy = 0
        self.f = False
        self.modify = False
        self.start_time = None

    def update_speed(self, m):
        if m == '+' and self.speed < self.max_front_speed:
            self.speed += self.acceleration
        if m == '-' and self.speed > -self.max_rear_speed:
            self.speed -= self.acceleration
        if m == '!':
            self.breaking()
        if m == '=':
            self.rolling()
        rad = self.rotation * pi / 180
        self.dx = cos(rad) * self.speed
        self.dy = sin(rad) * self.speed * -1
        if self.speed and not self.start_time:
            self.start_time = pygame.time.get_ticks()

    def update(self):
        if not self.f:
            self.f = self.check_collide()
            if not self.f:
                self.rect.x += round(self.dx)
                self.rect.y += round(self.dy)

    def check_collide(self):
        for sprite in empty_group:
            if pygame.sprite.collide_mask(self, sprite):
                return True
        for sprite in police_group:
            if pygame.sprite.collide_mask(self, sprite):
                if self.modify:
                    self.modify = False
                    sprite.f = False
                    sprite.boom_f = True
                    return False
                if sprite.f:
                    return True
        return False

    def breaking(self):
        if self.speed >= 1:
            self.speed -= 1
        elif self.speed <= -1:
            self.speed += 1
        else:
            self.speed = 0

    def rolling(self):
        if self.speed > 0:
            self.speed -= 0.125
        elif self.speed < 0:
            self.speed += 0.125

    def turning(self, t):
        if t == '+' and self.speed and not self.f:
            if abs(self.speed) < self.max_front_speed / 2:
                self.rotation += 0.2 * self.speed
            else:
                self.rotation += 0.2 * (self.max_front_speed - self.speed + 5)
        elif t == '-' and self.speed and not self.f:
            if abs(self.speed) < self.max_front_speed / 2:
                self.rotation -= 0.2 * self.speed
            else:
                self.rotation -= 0.2 * (self.max_front_speed - self.speed + 5)
        self.image = self.blit_rotate()
        self.mask = pygame.mask.from_surface(self.image)

    def blit_rotate(self):  # возвращаем изображение с повёрнутой машиной
        rotated_image = pygame.transform.rotate(self.start_image, self.rotation)
        new_rect = rotated_image.get_rect(center=self.start_image.get_rect(
            topleft=(self.rect.x, self.rect.y)).center)
        screen.blit(rotated_image, new_rect.topleft)
        return rotated_image

    def get_time(self):
        return (pygame.time.get_ticks() - self.start_time) // 10 / 100


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)

    def update_camera(self, gamer):
        # изменяем ракурс камеры
        self.update(gamer)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            self.apply(sprite)


car, location = start_screen().result()
camera = Camera()
city, player, finish, modify = generate_level(load_level(f'{location}.txt'))
camera.update_camera(player)
mode = '='
turning = '!'
game_time = None
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

        button = pygame.key.get_pressed()
        if button[pygame.K_w]:  # регулируем режим движения
            mode = '+'
        elif button[pygame.K_s]:
            mode = '-'
        elif button[pygame.K_SPACE]:
            mode = '!'
        else:
            mode = '='

        if button[pygame.K_a]:  # регулируем режим поворота
            turning = '+'
        elif button[pygame.K_d]:
            turning = '-'
        else:
            turning = '!'

    screen.fill((0, 100, 0))
    tiles_group.draw(screen)
    for cover in covers:
        cover.show()
    player.turning(turning)
    player.update_speed(mode)
    player.update()
    game_time, flag = finish.check_finish(player)
    if flag:
        running = False
    camera.update_camera(player)
    pygame.display.flip()
    clock.tick(FPS)

end_screen(game_time)

import pygame
import os
import sys
from PIL import Image
import numpy as np
from datetime import datetime

pygame.init()
size = width, height = 800, 453
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
pygame.time.set_timer(pygame.USEREVENT, 3500)


def load_image(name, colorkey=None):
    fullname = os.path.join('sprites_for_progect', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def make_darker_with_pillow(what_make):
    preview_animation_images = []
    image = np.asarray(Image.open(what_make))
    for i in range(15, 1, -1):
        pilImage = Image.fromarray(np.uint8(image // i * 2))
        myImage = pygame.image.fromstring(pilImage.tobytes(), pilImage.size, pilImage.mode)
        preview_animation_images.append(myImage)
    return preview_animation_images


class AnimatedPreview(pygame.sprite.Sprite):
    def __init__(self, preview):
        super().__init__(group_preview)
        self.frames = make_darker_with_pillow(preview)
        self.frame_number = 0
        self.image = self.frames[self.frame_number]
        self.rect = pygame.Rect(0, 0, 1700, 1000)

    def update(self):
        if self.frame_number < len(self.frames) - 1:
            self.frame_number = self.frame_number + 1
            self.image = self.frames[self.frame_number]


def show_the_text():
    font = pygame.font.Font(None, 50)
    text = font.render("Press any key to start", True, (255, 255, 255))
    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2 + 200
    screen.blit(text, (text_x, text_y))


def terminate():
    pygame.quit()
    sys.exit()


def make_and_show_preview1():
    AnimatedPreview('preview_1.png')
    while True:
        group_preview.draw(screen)
        group_preview.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.USEREVENT:
                show_the_text()
                pygame.display.flip()
                pygame.time.wait(1000)
            if event.type == pygame.KEYDOWN:
                return
        pygame.display.flip()
        clock.tick(10)


def show_text_for_input_name(text, x, y):
    intro_text = text
    font = pygame.font.Font(None, 30)
    string_rendered = font.render(intro_text, 1, pygame.Color('white'))
    screen.blit(string_rendered, (x, y))


#  функция отрисовки окна ввода никнейма пользователя для бд
def input_your_name():
    input_name = ''
    AnimatedPreview('for_input_name.png')
    fl = False
    while True:
        group_preview.draw(screen)
        group_preview.update()
        if fl:
            show_text_for_input_name('Before starting the game, enter your nickname:', 170, 250)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.USEREVENT:
                fl = True
            if event.type == pygame.KEYDOWN:
                if event.unicode == '\r':
                    return input_name, datetime.now()
                elif event.unicode == '\b' and input_name:
                    input_name = input_name[0: len(input_name) - 1]
                else:
                    input_name += event.unicode
        show_text_for_input_name(input_name, 350, 300)
        pygame.display.flip()
        clock.tick(10)


class PartofMap(pygame.sprite.Sprite):
    def __init__(self, image, x):
        super().__init__(map_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, 0
        self.mask = pygame.mask.from_surface(self.image)


class Gate(PartofMap):
    def __init__(self, image, x):
        super().__init__(image, x)
        self.frames = [load_image(f'start_enter{i}.png') for i in range(5)]
        self.cur_frame = 0

    def animation(self):
        if self.cur_frame < 5:
            self.image = self.frames[self.cur_frame]
            self.cur_frame += 1


def screen_of_death():
    pass


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(player_group)
        self.image = load_image('stop.png')
        self.rect = self.image.get_rect()
        self.rect.bottom = 300
        self.rect.x, self.fl = 90, False
        self.a = 5
        self.run_frames = [load_image(f'run{i}.png') for i in range(5)]
        self.run_frames_reverse = [pygame.transform.flip(image, True, False) for image in self.run_frames]
        self.run = 0

    def animation_move(self, move):
        if move == 'STOP':
            self.image = load_image('stop.png')
        if move == 'RIGHT':
            self.run = (self.run + 1) % len(self.run_frames)
            self.image = self.run_frames[self.run]
        if move == 'LEFT':
            self.run = (self.run + 1) % len(self.run_frames_reverse)
            self.image = self.run_frames_reverse[self.run]

    # для гравитации
    def update(self, whom_mask):
        self.a += 1
        self.fl = False
        # если хотя бы с 1 спрайтом карты есть пересечение, мы держим нашего персонажа на спрайте
        for el in whom_mask:
            if pygame.sprite.collide_mask(self, el):
                self.fl = True
        # если пересечения ни с кем нет, мы падаем вниз и больше не реагируем на страдания юзвера
        if not self.fl:
            self.rect = self.rect.move(0, self.a)


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, obj, player, motion):
        if player.fl and motion != 'STOP':
            obj.rect.x += self.dx

    def update(self, target, moving):
        if moving == 'RIGHT':
            self.dx = - abs((target.rect.x + target.rect.w // 2 - width // 2)) // 8
        elif moving == 'LEFT':
            self.dx = + abs((target.rect.x + target.rect.w // 2 - width // 2)) // 8
        target.animation_move(moving)


def start_game():
    player = Player()
    camera = Camera()
    x, p, motion = 0, [], 'STOP'
    for i in range(7):
        if i == 0:
            p.append(Gate(parts[i], x))
        else:
            p.append(PartofMap(parts[i], x))
        x += p[i].rect.width
    while 1:
        screen.fill((0, 5, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP and motion != 'UP':
                motion = 'STOP'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                motion = 'LEFT'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                motion = 'RIGHT'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                motion = 'UP'
        map_group.draw(screen)
        player_group.draw(screen)
        p[0].animation()
        camera.update(player, motion)
        for sprite in map_group:
            if pygame.sprite.collide_mask(player, p[0]):
                if motion == 'RIGHT':
                    camera.apply(sprite, player, motion)
            else:
                camera.apply(sprite, player, motion)
        player.update(p)
        pygame.display.flip()
        clock.tick(12)


group_preview = pygame.sprite.Group()
map_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
make_and_show_preview1()
a = input_your_name()
parts = {0: load_image('start_enter.png'), 1: load_image('spikes.png'),
         2: load_image('pillars.png'), 3: load_image('end_of_pillars.png'),
         4: load_image('find_a_weapon.png'), 5: load_image('for_fight.png'),
         6: load_image('end.png')}
nickname, time_of_start_playing = a[0], a[1]
start_game()
terminate()

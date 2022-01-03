import os
import sys
import pygame
import random

pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()
size = width, height = 750, 450
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
rocks_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
shot_group = pygame.sprite.Group()


def load_level(filename):
    filename = 'levels/' + filename
    with open(filename, 'r', encoding='utf-8') as mapfile:
        level_map = [line.strip() for line in mapfile.readlines()]
    max_width = max([len(x) for x in level_map])
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f'Файл с изображением "{fullname}" отсутствует')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is None:
        image = image.convert_alpha()
    else:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


tile_images = {
    'wall_1': pygame.transform.scale(load_image('wall_1.png'), (50, 50)),
    'wall_2': pygame.transform.scale(load_image('wall_2.png'), (50, 50)),
    'wall_3': pygame.transform.scale(load_image('wall_3.png'), (50, 50)),
    'wall_4': pygame.transform.scale(load_image('wall_4.png'), (50, 50)),
    'wall_5': pygame.transform.scale(load_image('wall_5.png'), (50, 50)),
    'wall_6': pygame.transform.scale(load_image('wall_6.png'), (50, 50)),
    'wall_7': pygame.transform.scale(load_image('wall_7.png'), (50, 50)),
    'wall_8': pygame.transform.scale(load_image('wall_8.png'), (50, 50)),
    'empty': pygame.transform.scale(load_image('tile_2.png'), (50, 50)),
    'empty_1': pygame.transform.scale(load_image('tile_1.png'), (50, 50)),
    'empty_2': pygame.transform.scale(load_image('tile_3.png'), (50, 50))
}
player_image = pygame.transform.scale(load_image('creature-1.png'), (40, 40))
dummy_image = load_image('dummy.png')
rock_image = pygame.transform.scale(load_image('rock.png'), (50, 50))
rock_break_image = pygame.transform.scale(load_image('rock_break.png'), (50, 50))
tile_width = tile_height = 50
player = None
dummy = None


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    pass


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if 'wall' in tile_type:
            self.add(walls_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)


class Rock(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(rocks_group, enemy_group, all_sprites)
        self.image = rock_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        self.hp = 2

    def update(self):
        if pygame.sprite.spritecollideany(self, shot_group):
            self.hp -= 1
            shot_group.update(True)
            if self.hp <= 0:
                self.kill()
            else:
                self.image = rock_break_image


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 5, tile_height * pos_y + 5)

    def update(self, x, y):
        if pygame.sprite.spritecollideany(self, walls_group) or\
                pygame.sprite.spritecollideany(self, rocks_group):
            self.rect.x -= x
            self.rect.y -= y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = dummy_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 10, tile_height * pos_y + 5)
        self.hp = 3

    def update(self):
        if pygame.sprite.spritecollideany(self, shot_group):
            self.hp -= 1
            shot_group.update(True)
            if self.hp == 0:
                self.kill()


class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, vx, vy):
        super().__init__(shot_group)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color('red'), (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vx, self.vy = vx, vy

    def update(self, damage):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, enemy_group) and damage or \
                pygame.sprite.spritecollideany(self, walls_group):
            self.kill()


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = width // 2 - target.rect.x - target.rect.w // 2
        self.dy = height // 2 - target.rect.y - target.rect.h // 2


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile(random.choice(('empty', 'empty_1', 'empty_2')), x, y)
            elif level[y][x] == '#':
                if (x, y) == (0, 0):
                    Tile('wall_1', x, y)
                elif len(level[y]) - 1 > x > 0 and y == 0:
                    Tile('wall_2', x, y)
                elif (x, y) == (len(level[y]) - 1, 0):
                    Tile('wall_3', x, y)
                elif x == 0 and len(level) - 1 > y > 0:
                    Tile('wall_4', x, y)
                elif x == len(level[y]) - 1 and len(level) - 1 > y > 0:
                    Tile('wall_5', x, y)
                elif (x, y) == (0, len(level) - 1):
                    Tile('wall_6', x, y)
                elif len(level[y]) - 1 > x > 0 and y == len(level) - 1:
                    Tile('wall_7', x, y)
                elif (x, y) == (len(level[y]) - 1, len(level) - 1):
                    Tile('wall_8', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '&':
                Tile('empty', x, y)
                Enemy(x, y)
            elif level[y][x] == '?':
                Tile('empty', x, y)
                Rock(x, y)
    return new_player, x, y


if __name__ == '__main__':
    pygame.display.set_caption('Dungeon Quest: demo')
    clock = pygame.time.Clock()
    start_screen()
    player, level_x, level_y = generate_level(load_level('demo.txt'))
    x, y = 0, 0
    v = 1
    running = True
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    x -= v
                elif event.key == pygame.K_w:
                    y -= v
                elif event.key == pygame.K_d:
                    x += v
                elif event.key == pygame.K_s:
                    y += v
                moving = True
                if event.key == pygame.K_LEFT:
                    shot = Shot(player.rect.x - 14, player.rect.y + 14, 7, -2, 0)
                elif event.key == pygame.K_RIGHT:
                    shot = Shot(player.rect.x + 40, player.rect.y + 14, 7, 2, 0)
                elif event.key == pygame.K_UP:
                    shot = Shot(player.rect.x + 14, player.rect.y - 14, 7, 0, -2)
                elif event.key == pygame.K_DOWN:
                    shot = Shot(player.rect.x + 14, player.rect.y + 40, 7, 0, 2)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    x += v
                elif event.key == pygame.K_w:
                    y += v
                elif event.key == pygame.K_d:
                    x -= v
                elif event.key == pygame.K_s:
                    y -= v
        player.rect.x += x
        player.rect.y += y
        player.update(x, y)
        enemy_group.update()
        shot_group.update(False)
        rocks_group.update()
        tiles_group.draw(screen)
        enemy_group.draw(screen)
        player_group.draw(screen)
        shot_group.draw(screen)
        rocks_group.draw(screen)
        clock.tick(200)
        pygame.display.flip()
    pygame.quit()

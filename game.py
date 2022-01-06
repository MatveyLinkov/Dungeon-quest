import os
import sys
import pygame
import random

pygame.init()
#  pygame.joystick.init()
#  js = pygame.joystick.Joystick(0)
#  js.init()
size = width, height = 750, 500
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
inventory_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
rocks_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
shot_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
melee_group = pygame.sprite.Group()
current_weapon = 'silver_sword'


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


cell_image = pygame.transform.scale(load_image('inventory_cell.png'), (50, 50))
choose_cell = pygame.transform.scale(load_image('inventory_cell1.png'), (50, 50))
cells = [False, False, False, False, False, False, False, False, False, False,
         False, False, False, False, True]
weapons = {
    'silver_sword': pygame.transform.scale(load_image('silver_sword.png'), (30, 30)),
    'diamond_sword': pygame.transform.scale(load_image('diamond_sword.png'), (30, 30)),
    'default_blaster': pygame.transform.scale(load_image('default_blaster.png'), (30, 30))
}
all_weapons = ['diamond_sword', 'silver_sword', 'default_blaster']
swords = ['diamond_sword', 'silver_sword']
guns = ['default_blaster']
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
#  closed_chest_image = pygame.transform.scale(load_image('closed_chest.png'), (50, 50))
#  opened_chest_image = pygame.transform.scale(load_image('opened_chest.png'), (50, 50))
chest_image = pygame.transform.scale(load_image('chest.png'), (50, 50))
tile_width = tile_height = 50
player = None
dummy = None


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    pass


class Inventory(pygame.sprite.Sprite):
    def __init__(self, pos_x, choose=False, weapon=None):
        super().__init__(inventory_group, all_sprites)
        if choose:
            self.image = choose_cell
            Inventory(cells.index(True))
            cells[cells.index(True)], cells[pos_x] = False, True
        else:
            self.image = cell_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos_x * tile_width, 0)


class WeaponInventory(pygame.sprite.Sprite):
    def __init__(self, pos_x, weapon):
        super().__init__(weapon_group, all_sprites)
        self.image = weapon
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(10 + pos_x * tile_width, 10)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if 'wall' in tile_type:
            self.add(walls_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y + 50)


class Rock(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(rocks_group, all_sprites)
        self.image = rock_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y + 50)
        self.hp = 10

    def update(self, weapon='silver_sword'):
        if pygame.sprite.spritecollideany(self, shot_group):
            if weapon == 'default_blaster':
                self.hp -= 1
            shot_group.update(True)
            if self.hp <= 0:
                self.kill()
            if self.hp <= 5:
                self.image = rock_break_image
        elif pygame.sprite.spritecollideany(self, melee_group):
            if weapon == 'silver_sword':
                self.hp -= 1
            if weapon == 'diamond_sword':
                self.hp -= 3
            if self.hp <= 0:
                self.kill()
            if self.hp <= 5:
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
        self.rect = self.rect.move(tile_width * pos_x + 10, tile_height * pos_y + 55)
        self.hp = 3

    def update(self, weapon='silver_sword'):
        if pygame.sprite.spritecollideany(self, shot_group):
            if weapon == 'default_blaster':
                self.hp -= 1
            shot_group.update(True)
            if self.hp <= 0:
                self.kill()
        elif pygame.sprite.spritecollideany(self, melee_group):
            if weapon == 'silver_sword':
                self.hp -= 1
            if weapon == 'diamond_sword':
                self.hp -= 3
            if self.hp <= 0:
                self.kill()


class Chest(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(chest_group, all_sprites)
        self.image = chest_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y + 55)

    def update(self, button):
        if pygame.sprite.spritecollideany(self, player_group):
            if button == 'e':
                getting_weapon()
                self.kill()
            if button is None:
                pass


def getting_weapon():
    global current_weapon
    current_weapon = random.choice(all_weapons)



class Melee(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon, way):
        super().__init__(melee_group)
        self.image = weapons[weapon]
        if way == 'up':
            self.image = pygame.transform.rotate(self.image, 45)
        elif way == 'down':
            self.image = pygame.transform.rotate(self.image, -135)
        elif way == 'left':
            self.image = pygame.transform.rotate(self.image, 135)
        elif way == 'right':
            self.image = pygame.transform.rotate(self.image, -45)
        self.weapon = weapon
        self.way = way
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - 15, y - 10

    def update(self):
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
                pygame.sprite.spritecollideany(self, walls_group) or \
                pygame.sprite.spritecollideany(self, rocks_group) and damage:
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
    Inventory(0, True)
    WeaponInventory(0, weapons['silver_sword'])
    for i in range(1, 15):
        Inventory(i)
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
            elif level[y][x] == '*':
                Tile('empty', x, y)
                Rock(x, y)
            elif level[y][x] == '?':
                Tile('empty', x, y)
                Chest(x, y)
    return new_player, x, y


if __name__ == '__main__':
    pygame.display.set_caption('Dungeon Quest: demo')
    clock = pygame.time.Clock()
    start_screen()
    player, level_x, level_y = generate_level(load_level('demo.txt'))
    x, y = 0, 0
    v = 1
    button = None
    running = True
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 0 <= event.pos[1] <= 50 and event.pos[0] // 50 != cells.index(True):
                    Inventory(event.pos[0] // 50, True)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    x -= v
                elif event.key == pygame.K_w:
                    y -= v
                elif event.key == pygame.K_d:
                    x += v
                elif event.key == pygame.K_s:
                    y += v
                if event.key == pygame.K_LEFT:
                    if current_weapon in guns:
                        shot = Shot(player.rect.x - 14, player.rect.y + 14, 7, -2, 0)
                    elif current_weapon in swords:
                        melee = Melee(player.rect.x - 14, player.rect.y + 14, current_weapon,
                                      'left')
                elif event.key == pygame.K_RIGHT:
                    if current_weapon in guns:
                        shot = Shot(player.rect.x + 40, player.rect.y + 14, 7, 2, 0)
                    elif current_weapon in swords:
                        melee = Melee(player.rect.x + 40, player.rect.y + 14, current_weapon,
                                      'right')
                elif event.key == pygame.K_UP:
                    if current_weapon in guns:
                        shot = Shot(player.rect.x + 14, player.rect.y - 14, 7, 0, -2)
                    elif current_weapon in swords:
                        melee = Melee(player.rect.x + 14, player.rect.y - 14, current_weapon, 'up')
                elif event.key == pygame.K_DOWN:
                    if current_weapon in guns:
                        shot = Shot(player.rect.x + 14, player.rect.y + 40, 7, 0, 2)
                    elif current_weapon in swords:
                        melee = Melee(player.rect.x + 14, player.rect.y + 40, current_weapon,
                                      'down')
                if event.key == pygame.K_e:
                    button = 'e'
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
        chest_group.update(button)
        button = None
        rocks_group.update(current_weapon)
        enemy_group.update(current_weapon)
        shot_group.update(False)
        melee_group.update()
        inventory_group.draw(screen)
        weapon_group.draw(screen)
        tiles_group.draw(screen)
        chest_group.draw(screen)
        enemy_group.draw(screen)
        player_group.draw(screen)
        shot_group.draw(screen)
        rocks_group.draw(screen)
        melee_group.draw(screen)
        clock.tick(200)
        pygame.display.flip()
    pygame.quit()

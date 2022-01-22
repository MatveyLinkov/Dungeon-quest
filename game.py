import os
import random
import sys

import pygame
import pytmx

map_number = input('Введите номер карты (1, 2, 3): ')
pygame.init()
size = width, height = 1280, 720
FPS = 60
MAPS_DIR = 'levels'
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
barriers_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
animated_sprites_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
shot_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
skulls_group = pygame.sprite.Group()
destroyer_group = pygame.sprite.Group()
scripts_group = pygame.sprite.Group()
rooms_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
key_group = pygame.sprite.Group()
hatch_group = pygame.sprite.Group()
ladder_group = pygame.sprite.Group()
melee_group = pygame.sprite.Group()
health_group = pygame.sprite.Group()


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


player_sheet = pygame.transform.scale(load_image('knight_sheet.png'), (552, 150))
skull_sheet = load_image('skull_sheet.png')
goblin_sheet = load_image('goblin_spritesheet.png')
bomber_sheet = pygame.transform.scale(load_image('bomber_spritesheet.png'), (288, 48))
opened_chest = load_image('chest_open_anim_3.png')
closed_chest = load_image('chest_open_anim_1.png')
key_image = load_image('key.png')
arrow_image = pygame.transform.scale(load_image('arrow.png'), (48, 48))
hit_effect_sheet = pygame.transform.scale(load_image('hit_effect.png'), (96, 32))
explosion_sheet = pygame.transform.scale(load_image('explosion_sheet.png'), (336, 48))
enemy_dead_sheet = load_image('enemy_afterdead.png')
walls = []
doors = [37, 38, 39, 40, 47, 48, 49, 50, 57, 58, 59, 60, 67, 68]
barriers = [44, 45, 53, 54]
animated_sprites = {75: 'flag_sheet.png',
                    91: 'torch_sheet.png', 94: 'candle_sheet.png'}
weapons_image = {'wooden_bow': pygame.transform.scale(load_image('wooden_bow.png'), (48, 48)),
                 'iron_sword':
                     pygame.transform.scale(load_image('slash_effect_anim.png'), (259, 86))}
weapons = ['wooden_bow', 'iron_sword']
bows = ['wooden_bow']
swords = ['iron_sword']
inventory = {1: 'wooden_bow', 2: None, 3: None}
current_weapon = inventory[1]
ts = tile_width = tile_height = 48
chest = 84
key = 89
player = None


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    pass


def getting_weapon():
    global current_weapon, inventory
    new_weapon = random.choice(weapons[1:])
    inventory[2] = new_weapon


def choose_weapon(button):
    global current_weapon
    if button == 1:
        current_weapon = inventory[1]
    elif button == 2:
        if len(inventory) >= 2:
            current_weapon = inventory[2]
        else:
            pass


def pickup_key():
    pass


class Dungeon:
    def __init__(self, filename):
        super().__init__()
        self.map = pytmx.load_pygame(f'{MAPS_DIR}/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        for obj in self.map.objects:
            if obj.type == 'player':
                self.player_x, self.player_y = obj.x // ts, obj.y // ts
            elif obj.name == 'Skull':
                Skull(4, 1, obj.x // ts, obj.y // ts, )
            elif obj.name == 'Goblin':
                Goblin(6, 2, obj.x // ts, obj.y // ts, )
            elif obj.name == 'Bomber':
                Bomber(6, 1, obj.x // ts, obj.y // ts, )
            elif obj.type == 'script':
                Script(obj.x, obj.y, obj.width, obj.height)
            elif obj.type == 'room':
                Room(obj.x, obj.y, obj.width, obj.height)

    def render(self):
        for i in range(4):
            for y in range(self.height):
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, i)
                    if image:
                        if i == 1 and self.get_tile_id((x, y), i) not in walls:
                            walls.append(self.get_tile_id((x, y), i))
                        if self.get_tile_id((x, y), i) in doors:
                            Door(x, y, image)
                        elif i == 3:
                            Barrier(x, y, image)
                        elif self.get_tile_id((x, y), i) in animated_sprites:
                            AnimatedSprite(self.get_tile_id((x, y), i), 4, 1, x, y)
                        elif self.get_tile_id((x, y), i) - 100 in animated_sprites:
                            AnimatedSprite(self.get_tile_id((x, y), i) - 100, 4, 1, x, y)
                        elif self.get_tile_id((x, y), i) - 100 == chest or \
                                self.get_tile_id((x, y), i) == chest:
                            Chest(x, y)
                        elif self.get_tile_id((x, y), i) == key or \
                                self.get_tile_id((x, y), i) - 100 == key:
                            Key(x, y)
                        elif self.get_tile_id((x, y), i) == 81 or \
                                self.get_tile_id((x, y), i) - 100 == 81:
                            Hatch(x, y, image)
                        elif self.get_tile_id((x, y), i) == 82 or \
                                self.get_tile_id((x, y), i) - 100 == 82:
                            Ladder(x, y, image)
                        else:
                            Tile(self.get_tile_id((x, y), i), x, y, image)

        return self.player_x, self.player_y

    def get_tile_id(self, position, layer):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, layer)]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_id, pos_x, pos_y, image):
        super().__init__(tiles_group, all_sprites)
        if tile_id in walls:
            self.add(walls_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)


class Barrier(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(barriers_group, all_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        if pygame.sprite.spritecollideany(self, destroyer_group):
            if [(destroyer.update(True), Particle(7, 1, self.rect.x, self.rect.y,
                explosion_sheet, destroyer)) for destroyer in destroyer_group
                    if pygame.sprite.collide_mask(self, destroyer)]:
                self.kill()


class Key(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(key_group, all_sprites)
        self.image = key_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            inventory[3] = 'key'
            self.kill()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, id, columns, rows, pos_x, pos_y):
        super().__init__(animated_sprites_group, all_sprites)
        self.frames = []
        self.crop_sheet(load_image(animated_sprites[id]), columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(8)]

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Particle(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y, image, enemy=None):
        super().__init__(particle_group, all_sprites)
        self.frames = []
        self.sheet = image
        self.enemy = enemy
        self.crop_sheet(image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos_x, pos_y)

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(8)]

    def update(self, enemy=None):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.cur_frame == len(self.frames) - 1:
            self.kill()
        if self.cur_frame == len(self.frames) // 2:
            if self.sheet == explosion_sheet:
                self.enemy.update(True)


class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(doors_group, walls_group, all_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self, close):
        if not close:
            self.remove(walls_group)
        else:
            self.add(walls_group)


class Room(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__(rooms_group, all_sprites)
        self.image = pygame.Surface((width, height))
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        self.fight = False

    def update(self):
        global doors_close
        if pygame.sprite.spritecollideany(self, player_group):
            if not pygame.sprite.spritecollideany(self, enemy_group):
                doors_close = False
            if not self.fight and doors_close:
                [enemy.update(True) for enemy in enemy_group if
                 pygame.sprite.collide_mask(self, enemy)]
                self.fight = True
                for script in scripts_group:
                    if pygame.sprite.collide_mask(self, script):
                        script.update(self.fight)


class Hatch(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(hatch_group, all_sprites)
        self.image = image
        self.count = 0
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self, button, key_available):
        if button == 'e' and key_available is True:
            if pygame.sprite.spritecollideany(self, player_group):
                self.count += 1
                if self.count == 1:
                    pass
        else:
            pass


class Ladder(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(ladder_group, all_sprites)
        self.image = image
        self.count = 0
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self, button):
        if button == 'e':
            if pygame.sprite.spritecollideany(self, player_group):
                self.count += 1
                if self.count == 1:
                    pass
        else:
            pass


class Melee(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon, angle):
        super().__init__(melee_group)
        self.frames = []
        self.crop_sheet(weapons_image[weapon], 3, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.angle = angle
        self.weapon = weapon
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - 15, y - 10
        if angle == 270:
            self.rect = self.rect.move(-6, 9)
        elif angle == 180:
            self.rect = self.rect.move(-18, -6)
        elif angle == 90:
            self.rect = self.rect.move(-6, -30)
        elif angle == 0:
            self.rect = self.rect.move(12, -6)

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(6)]

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.rotate(self.image, self.angle)
        if self.cur_frame == len(self.frames) - 1:
            self.kill()


class Script(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__(scripts_group, all_sprites)
        self.image = pygame.Surface((240, 240))
        self.rect = pygame.Rect(pos_x, pos_y, width, height)

    def update(self, fight=False):
        global doors_close
        if pygame.sprite.spritecollideany(self, player_group) or fight:
            doors_close = True
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.half_frames = 24
        self.crop_sheet(player_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 12, tile_height * pos_y + 12)
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = False
        self.visible = True
        self.time = 0

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(3)]

    def update(self, x, y, flip):
        if moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.half_frames:])
            self.image = self.frames[self.half_frames:][self.cur_frame]
        else:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[:self.half_frames])
            self.image = self.frames[:self.half_frames][self.cur_frame]
        if flip:
            self.image = pygame.transform.flip(self.image, True, False)
        if pygame.sprite.spritecollideany(self, walls_group) or\
                pygame.sprite.spritecollideany(self, barriers_group):
            self.rect.x -= x
            self.rect.y -= y
        if pygame.sprite.spritecollideany(self, enemy_group):
            return True


class Chest(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(chest_group, all_sprites)
        self.image = closed_chest
        self.count = 0
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y + 55)

    def update(self, button):
        if pygame.sprite.spritecollideany(self, player_group):
            if button == 'e':
                self.image = opened_chest
                self.count += 1
                if self.count == 1:
                    getting_weapon()
            if button is None:
                pass


class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, angle):
        super().__init__(shot_group, all_sprites)
        self.image = arrow_image
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.vx, self.vy = vx, vy
        if angle == 270:
            self.particle_x, self.particle_y = 0, 3
        elif angle == 180:
            self.particle_x, self.particle_y = 6, 0
        elif angle == 90:
            self.particle_x, self.particle_y = 12, 3
        elif angle == 0:
            self.particle_x, self.particle_y = 6, 12

    def update(self, damage):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, walls_group) or\
                pygame.sprite.spritecollideany(self, barriers_group) or\
                (pygame.sprite.spritecollideany(self, enemy_group) and damage):
            Particle(3, 1, self.rect.x + self.particle_x, self.rect.y + self.particle_y,
                     hit_effect_sheet)
            self.kill()


class Skull(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(enemy_group, skulls_group, all_sprites)
        self.frames = []
        self.crop_sheet(skull_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 12, tile_height * pos_y + 12)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 8
        self.damage = 0
        self.melee_strike = True
        self.speed = 7
        self.moving = False
        self.move_x, self.move_y = 0, 0
        self.flip = False
        self.close = False

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(8)]

    def update(self, close=False):
        if close:
            self.close = close
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if len([self.rect.x + j for j in range(self.rect.width + 1)
                if self.rect.x + j in
                [player.rect.x + i for i in range(player.rect.width + 1)]]) >= 1\
                and not self.moving and self.close:
            if self.rect.y < player.rect.y:
                self.move_y = self.speed
            else:
                self.move_y = -self.speed
            self.moving = True
        elif len([self.rect.y + j for j in range(self.rect.height + 1)
                  if self.rect.y + j in
                  [player.rect.y + i for i in range(player.rect.height + 1)]]) >= 1 \
                and not self.moving and self.close:
            if self.rect.x < player.rect.x:
                self.move_x = self.speed
                self.flip = False
            else:
                self.move_x = -self.speed
                self.flip = True
            self.moving = True
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        if not (pygame.sprite.spritecollideany(self, walls_group) or
                pygame.sprite.spritecollideany(self, barriers_group)):
            if self.moving:
                self.rect.x += self.move_x
                self.rect.y += self.move_y
        else:
            self.rect.x -= self.move_x
            self.rect.y -= self.move_y
            self.move_x, self.move_y = 0, 0
            self.moving = False
        if pygame.sprite.spritecollideany(self, shot_group):
            if current_weapon == 'wooden_bow':
                self.damage = 1
                shot_group.update(True)
        if pygame.sprite.spritecollideany(self, melee_group) and self.melee_strike:
            if current_weapon == 'iron_sword':
                self.damage = 4
        self.hp -= self.damage
        self.damage = 0
        if self.hp <= 0:
            Particle(4, 1, self.rect.x, self.rect.y,
                     pygame.transform.scale(enemy_dead_sheet, (288, 72)))
            self.kill()
        self.melee_strike = False
        if len(melee_group) == 0:
            self.melee_strike = True


class Goblin(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(enemy_group, destroyer_group, all_sprites)
        self.frames = []
        self.half_frames = 36
        self.crop_sheet(goblin_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        self.hp = 5
        self.damage = 0
        self.melee_strike = True
        self.speed = random.randint(3, 4)
        self.moving = False
        self.move_x, self.move_y = 0, 0
        self.flip = False
        self.close = False

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(6)]

    def update(self, close=False):
        self.move_x, self.move_y = 0, 0
        if close:
            self.close = not self.close
        if (self.rect.x // ts, self.rect.y // ts) != (player.rect.x // ts, player.rect.y // ts) and\
                self.close:
            self.moving = True
        if self.moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.half_frames:])
            self.image = self.frames[self.half_frames:][self.cur_frame]
        else:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[:self.half_frames])
            self.image = self.frames[:self.half_frames][self.cur_frame]
        if self.rect.x // ts < player.rect.x // ts:
            self.move_x = self.speed
            self.flip = False
        elif self.rect.x // ts > player.rect.x // ts:
            self.move_x = -self.speed
            self.flip = True
        if self.rect.y // ts < player.rect.y // ts:
            self.move_y = self.speed
        elif self.rect.y // ts > player.rect.y // ts:
            self.move_y = -self.speed
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        if not pygame.sprite.spritecollideany(self, walls_group):
            if self.moving:
                self.rect.x += self.move_x
                self.rect.y += self.move_y
        else:
            self.rect.x -= self.move_x
            self.rect.y -= self.move_y
        self.moving = False
        if pygame.sprite.spritecollideany(self, shot_group):
            if current_weapon == 'wooden_bow':
                self.damage = 1
                shot_group.update(True)
        if pygame.sprite.spritecollideany(self, melee_group):
            if current_weapon == 'iron_sword' and self.melee_strike:
                self.damage = 4
        self.hp -= self.damage
        self.damage = 0
        if self.hp <= 0:
            Particle(4, 1, self.rect.x, self.rect.y, enemy_dead_sheet)
            self.kill()
        self.melee_strike = False
        if len(melee_group) == 0:
            self.melee_strike = True


class Bomber(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(enemy_group, destroyer_group, all_sprites)
        self.frames = []
        self.crop_sheet(bomber_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        self.hp = 3
        self.damage = 0
        self.move_x, self.move_y = 0, 0
        self.flip = False
        self.close = False

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(6)]

    def update(self, close=False):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class HealthPoints(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(health_group)
        self.image = load_image('health_ui.png')
        self.rect = self.image.get_rect()


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


if __name__ == '__main__':
    pygame.display.set_caption('Dungeon Quest: alpha')

    dungeon = Dungeon(f'map0{map_number}.tmx')
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)

    player_x, player_y = dungeon.render()
    player = Player(8, 2, player_x, player_y)
    heath = HealthPoints()

    button = None
    chest_opened_count = 0

    camera = Camera()
    x, y = 0, 0
    player_v = 6
    shot_v = 16
    hp = 4
    frames = 0

    moving = False
    flip = False
    doors_close = False
    damage = False
    visible = True
    running = True
    while running:
        screen.fill(pygame.Color((37, 19, 26)))
        moving = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    x -= player_v
                elif event.key == pygame.K_w:
                    y -= player_v
                elif event.key == pygame.K_d:
                    x += player_v
                elif event.key == pygame.K_s:
                    y += player_v
                if event.key == pygame.K_LEFT:
                    if current_weapon in bows:
                        Shot(player.rect.x - 39, player.rect.y + 13, -shot_v, 0, 270)
                    elif current_weapon in swords and len(melee_group.sprites()) == 0:
                        melee = Melee(player.rect.x - 39, player.rect.y + 13, current_weapon, 180)
                elif event.key == pygame.K_RIGHT:
                    if current_weapon in bows:
                        Shot(player.rect.x + 60, player.rect.y + 13, shot_v, 0, 90)
                    elif current_weapon in swords and len(melee_group.sprites()) == 0:
                        melee = Melee(player.rect.x + 60, player.rect.y + 13, current_weapon, 0)
                elif event.key == pygame.K_UP:
                    if current_weapon in bows:
                        Shot(player.rect.x + 12, player.rect.y - 36, 0, -shot_v, 180)
                    elif current_weapon in swords and len(melee_group.sprites()) == 0:
                        melee = Melee(player.rect.x + 12, player.rect.y - 36, current_weapon, 90)
                elif event.key == pygame.K_DOWN:
                    if current_weapon in bows:
                        Shot(player.rect.x + 12, player.rect.y + 69, 0, shot_v, 0)
                    elif current_weapon in swords and len(melee_group.sprites()) == 0:
                        melee = Melee(player.rect.x + 12, player.rect.y + 69, current_weapon, 270)

                elif event.key == pygame.K_r:
                    [s.kill() for s in all_sprites]
                    dungeon = Dungeon(f'map0{map_number}.tmx')
                    player_x, player_y = dungeon.render()
                    player = Player(8, 2, player_x, player_y)
                elif event.key == pygame.K_e:
                    button = 'e'
                elif event.key == pygame.K_1:
                    choose_weapon(1)
                elif event.key == pygame.K_2:
                    choose_weapon(2)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    x += player_v
                elif event.key == pygame.K_w:
                    y += player_v
                elif event.key == pygame.K_d:
                    x -= player_v
                elif event.key == pygame.K_s:
                    y -= player_v
                elif event.key == pygame.K_e:
                    button = None
        if (x, y) != (0, 0):
            moving = True
        if x < 0:
            flip = True
        elif x > 0:
            flip = False

        player.rect.x += x
        player.rect.y += y
        player_damage = player.update(x, y, flip)
        if player_damage and not damage:
            hp -= 1
            damage = True
            visible = False
            if hp == 0:
                [s.kill() for s in all_sprites]
                dungeon = Dungeon(f'map0{map_number}.tmx')
                player_x, player_y = dungeon.render()
                player = Player(8, 2, player_x, player_y)
                hp = 4
                flip = False
                doors_close = False
                damage = False
                visible = True
        shot_group.update(False)
        melee_group.update()
        doors_group.update(doors_close)
        camera.update(player)
        scripts_group.update()
        rooms_group.update()
        animated_sprites_group.update()
        particle_group.update()
        barriers_group.update()
        enemy_group.update()
        chest_group.update(button)
        key_group.update()
        if inventory[3] is not None:
            hatch_group.update(button, True)
        else:
            hatch_group.update(button, False)
        ladder_group.update(button)
        for sprite in all_sprites:
            camera.apply(sprite)

        tiles_group.draw(screen)
        barriers_group.draw(screen)
        if doors_close:
            doors_group.draw(screen)
        ladder_group.draw(screen)
        melee_group.draw(screen)
        chest_group.draw(screen)
        hatch_group.draw(screen)
        key_group.draw(screen)
        animated_sprites_group.draw(screen)
        enemy_group.draw(screen)
        if damage:
            frames += 1
            if frames % 20 == 0:
                visible = not visible
            if frames == 100:
                frames = 0
                damage = False
        if visible:
            player_group.draw(screen)
        shot_group.draw(screen)
        particle_group.draw(screen)
        pygame.draw.rect(screen, pygame.Color((172, 50, 50)), (5, 0, 230, 48), 0)
        pygame.draw.rect(screen, pygame.Color((0, 0, 0)), (55 + 45 * hp, 0, 45 * (4 - hp), 48), 0)
        health_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()

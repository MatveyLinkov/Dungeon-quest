import os
import random
import sys

import pygame
import pytmx

map_number = input('Введите номер карты (1, 2): ')
pygame.init()
size = width, height = 1280, 720
FPS = 60
MAPS_DIR = 'levels'
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
animated_sprites_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
shot_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
scripts_group = pygame.sprite.Group()
rooms_group = pygame.sprite.Group()
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
arrow_image = pygame.transform.scale(load_image('arrow.png'), (48, 48))
hit_effect_sheet = load_image('hit_effect.png')
enemy_dead_sheet = load_image('enemy_afterdead.png')
walls = []
doors = [37, 38, 39, 40, 47, 48, 49, 50, 57, 58, 59, 60, 67, 68]
animated_sprites = {75: 'flag_sheet.png', 89: 'key_sheet.png',
                    91: 'torch_sheet.png', 94: 'candle_sheet.png'}
ts = tile_width = tile_height = 48
player = None


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
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
            elif obj.type == 'script':
                Script(obj.x, obj.y, obj.width, obj.height)
            elif obj.type == 'room':
                Room(obj.x, obj.y, obj.width, obj.height)

    def render(self):
        for i in range(3):
            for y in range(self.height):
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, i)
                    if image:
                        if i == 1 and self.get_tile_id((x, y), i) not in walls:
                            walls.append(self.get_tile_id((x, y), i))
                        if self.get_tile_id((x, y), i) in doors:
                            Door(x, y, image)
                        elif self.get_tile_id((x, y), i) in animated_sprites:
                            AnimatedSprite(self.get_tile_id((x, y), i), 4, 1, x, y)
                        elif self.get_tile_id((x, y), i) - 100 in animated_sprites:
                            AnimatedSprite(self.get_tile_id((x, y), i) - 100, 4, 1, x, y)
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
    def __init__(self, columns, rows, pos_x, pos_y, image):
        super().__init__(particle_group, all_sprites)
        self.frames = []
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
                 for i in range(6)]

    def update(self, close=False):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.cur_frame == len(self.frames) - 1:
            self.kill()


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
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect.x -= x
            self.rect.y -= y
        if pygame.sprite.spritecollideany(self, enemy_group):
            return True


class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, angle):
        super().__init__(shot_group, all_sprites)
        self.image = arrow_image
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.vx, self.vy = vx, vy

    def update(self, damage):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, walls_group) or\
                (pygame.sprite.spritecollideany(self, enemy_group) and damage):
            Particle(3, 1, self.rect.x, self.rect.y, hit_effect_sheet)
            self.kill()


class Skull(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.frames = []
        self.crop_sheet(skull_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 12, tile_height * pos_y + 12)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 8
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
        if len([self.rect.x + j for j in range(self.rect.width + 1) if self.rect.x + j in
               [player.rect.x + i for i in range(player.rect.width + 1)]]) >= 1\
                and not self.moving and self.close:
            if self.rect.y < player.rect.y:
                self.move_y = self.speed
            else:
                self.move_y = -self.speed
            self.moving = True
        elif len([self.rect.y + j for j in range(self.rect.height + 1) if self.rect.y + j in
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
        if not pygame.sprite.spritecollideany(self, walls_group):
            if self.moving:
                self.rect.x += self.move_x
                self.rect.y += self.move_y
        else:
            self.rect.x -= self.move_x
            self.rect.y -= self.move_y
            self.move_x, self.move_y = 0, 0
            self.moving = False
        if pygame.sprite.spritecollideany(self, shot_group):
            self.hp -= 1
            shot_group.update(True)
            if self.hp == 0:
                Particle(4, 1, self.rect.x, self.rect.y,
                         pygame.transform.scale(enemy_dead_sheet, (288, 72)))
                self.kill()


class Goblin(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.frames = []
        self.half_frames = 36
        self.crop_sheet(goblin_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        self.clock = pygame.time.Clock()
        self.hp = 5
        self.speed = random.randint(3, 5)
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
            self.close = close
        if self.moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.half_frames:])
            self.image = self.frames[self.half_frames:][self.cur_frame]
        else:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[:self.half_frames])
            self.image = self.frames[:self.half_frames][self.cur_frame]
        if (self.rect.x // ts, self.rect.y // ts) != (player.rect.x // ts, player.rect.y // ts) and\
                self.close:
            self.moving = True
        if self.rect.x // ts < player.rect.x // ts:
            self.move_x = self.speed
            self.flip = False
        elif self.rect.x // ts > player.rect.x // ts:
            self.move_x = -self.speed
            self.flip = True
        elif self.rect.y // ts < player.rect.y // ts:
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
            if self.move_x != 0:
                if self.rect.y // ts <= player.rect.y // ts:
                    self.move_y = self.speed
                elif self.rect.y // ts >= player.rect.y // ts:
                    self.move_y = -self.speed
                self.move_x = 0
            elif self.move_y != 0:
                if self.rect.x // ts < player.rect.x // ts:
                    self.move_x = -self.speed
                elif self.rect.x // ts > player.rect.x // ts:
                    self.move_x = self.speed
                self.move_y = 0
            self.rect.x -= self.move_x
            self.rect.y -= self.move_y
            self.moving = False
        if pygame.sprite.spritecollideany(self, shot_group):
            self.hp -= 1
            shot_group.update(True)
            if self.hp == 0:
                Particle(4, 1, self.rect.x, self.rect.y, enemy_dead_sheet)
                self.kill()


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
                    Shot(player.rect.x - 39, player.rect.y + 13, -shot_v, 0, 270)
                elif event.key == pygame.K_RIGHT:
                    Shot(player.rect.x + 60, player.rect.y + 13, shot_v, 0, 90)
                elif event.key == pygame.K_UP:
                    Shot(player.rect.x + 12, player.rect.y - 36, 0, -shot_v, 180)
                elif event.key == pygame.K_DOWN:
                    Shot(player.rect.x + 12, player.rect.y + 69, 0, shot_v, 0)
                elif event.key == pygame.K_r:
                    [s.kill() for s in all_sprites]
                    dungeon = Dungeon(f'map0{map_number}.tmx')
                    player_x, player_y = dungeon.render()
                    player = Player(8, 2, player_x, player_y)
                    hp = 4
                    flip = False
                    doors_close = False
                    damage = False
                    visible = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    x += player_v
                elif event.key == pygame.K_w:
                    y += player_v
                elif event.key == pygame.K_d:
                    x -= player_v
                elif event.key == pygame.K_s:
                    y -= player_v
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
        walls_group.update(False)
        doors_group.update(doors_close)
        camera.update(player)
        scripts_group.update()
        rooms_group.update()
        animated_sprites_group.update()
        particle_group.update()
        enemy_group.update()
        for sprite in all_sprites:
            camera.apply(sprite)

        tiles_group.draw(screen)
        if doors_close:
            doors_group.draw(screen)
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

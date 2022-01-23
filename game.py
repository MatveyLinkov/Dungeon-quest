import os
import sys
import pygame
import pytmx

pygame.init()
level = 'map' + input('Введите номер уровня (1, 2, 3): ') + '.tmx'
maps = {'map1.tmx': [23, (11, 8)], 'map2.tmx': [24, (10, 7)],
        'map3.tmx': [23, (12, 5)]}
restart = False
size = width, height = 1280, 720
FPS = 60
MAPS_DIR = 'levels'
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
slimes_group = pygame.sprite.Group()
tables_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
keys_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()


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


player_sheet = pygame.transform.scale(load_image('knight_sheet.png'), (448, 112))
slime_sheet = load_image('slime_idle_spritesheet.png')
spikes_images = ['holes.png', 'spikes.png', 'on_holes.png', 'on_spikes.png']
floor = [6, 15, 21, 22, 23, 24, 30, 31, 32, 33]
ts = tile_width = tile_height = 64
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
            if obj.name == 'Player':
                self.player_x, self.player_y = obj.x // tile_width, obj.y // tile_height
            elif obj.name == 'Slime':
                Slime(6, 1, obj.x // tile_width, obj.y // tile_height)
            elif obj.name == 'Spike':
                Spikes(obj.x // tile_width, obj.y // tile_height)

    def render(self):
        for i in range(4):
            for y in range(self.height):
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, i)
                    if image:
                        if i == 3:
                            Table(x, y, image)
                        elif self.get_tile_id((x, y), i) == 6:
                            Key(x, y, image)
                        elif self.get_tile_id((x, y), i) == 37:
                            Door(x, y, image)
                        else:
                            Tile(x, y, image)
        return self.player_x, self.player_y

    def get_tile_id(self, position, layer):
        try:
            return self.map.tiledgidmap[self.map.get_tile_gid(*position, layer)]
        except KeyError:
            pass


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(tiles_group, all_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.frames = []
        self.half_frames = 24
        self.crop_sheet(player_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 4, tile_height * pos_y + 4)
        self.mask = pygame.mask.from_surface(self.image)
        self.attempt = maps[level][0]
        self.color = 'white'

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(3)]

    def update(self, x, y, flip, back):
        damage = 0
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[:self.half_frames])
        self.image = self.frames[:self.half_frames][self.cur_frame]
        self.pos_x += x // ts
        self.pos_y += y // ts
        if moving:
            damage += 1
        if flip:
            self.image = pygame.transform.flip(self.image, True, False)
        if dungeon.get_tile_id((self.rect.x // 64, self.rect.y // 64), 0) not in floor or back:
            self.rect.x -= x
            self.rect.y -= y
            self.pos_x = self.rect.x // ts
            self.pos_y = self.rect.y // ts
            damage -= 1
        if damage == 1:
            self.color = 'white'
        if ((self.pos_x, self.pos_y) in [(s.rect.x // ts, s.rect.y // ts) for s in spikes_group] and
            damage == 1 and not pygame.sprite.spritecollideany(self, tables_group or slimes_group))\
                or (back and (self.pos_x, self.pos_y) in [(s.rect.x // ts, s.rect.y // ts)
                                                          for s in spikes_group]):
            damage += 1
            self.color = 'red'
        self.attempt -= damage
        draw(screen, self.attempt, (self.rect.x // ts, self.rect.y // ts), self.color)


class Slime(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(slimes_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.frames = []
        self.crop_sheet(slime_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 8, tile_height * pos_y + 8)

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(5)]

    def update(self, x, y, flip):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if (self.pos_x, self.pos_y) == (player.rect.x // ts, player.rect.y // ts):
            self.rect.x += x
            self.rect.y += y
            self.pos_x += x // ts
            self.pos_y += y // ts
            player_group.update(x, y, flip, True)
            if pygame.sprite.spritecollideany(self, tables_group):
                self.kill()
        tile_id = dungeon.get_tile_id((self.pos_x, self.pos_y), 0)
        if (tile_id not in floor or len([sprite for slime_sprite in slimes_group
                                         if self != slime_sprite and (self.rect.x, self.rect.y) ==
                                        (slime_sprite.rect.x, slime_sprite.rect.y)]) >= 1):
            self.kill()


class Table(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(tables_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self, x, y, flip):
        touch = 0
        if (self.rect.x // ts, self.rect.y // ts) == (player.rect.x // ts, player.rect.y // ts):
            self.rect.x += x
            self.rect.y += y
            touch += 1
            player_group.update(x, y, flip, True)
        if (dungeon.get_tile_id((self.rect.x // ts, self.rect.y // ts), 1) or (
                (self.rect.x // ts, self.rect.y // ts) in
                [(spike_sprite.rect.x // ts, spike_sprite.rect.y // ts)
                 for spike_sprite in tables_group if self != spike_sprite] and touch >= 1) or
                ((self.rect.x // ts, self.rect.y // ts) in
                 [(round(slimes_sprite.rect.x / ts), round(slimes_sprite.rect.y / ts))
                  for slimes_sprite in slimes_group])):
            self.rect.x -= x
            self.rect.y -= y


class Spikes(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(spikes_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = pygame.transform.scale(load_image(spikes_images[0]), (64, 64))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        self.image = pygame.transform.scale(load_image(spikes_images[1]), (64, 64))
        if (self.pos_x, self.pos_y) in [(s.rect.x // ts, s.rect.y // ts) for s in tables_group] or\
                pygame.sprite.spritecollideany(self, player_group):
            self.image = pygame.transform.scale(load_image(spikes_images[3]), (64, 64))


class Key(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(keys_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            self.kill()


class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(doors_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        if len(keys_group.sprites()) == 0:
            self.kill()
        if pygame.sprite.spritecollideany(self, player_group):
            player_group.update(x, y, flip, True)


def draw(screen, text, position, color):
    global restart
    if text == 0:
        text = 'X'
    elif text < 0:
        restart = True
    if position == maps[level][1]:
        text = 'WIN'
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 50)
    text = font.render(str(text), True, color)
    text_x = 10
    text_y = 10
    screen.blit(text, (text_x, text_y))


if __name__ == '__main__':
    pygame.display.set_caption('Dungeon Quest: feature')

    dungeon = Dungeon(level)
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)

    player_x, player_y = dungeon.render()
    player = Player(8, 2, player_x, player_y)
    player_v = 64

    moving = False
    flip = False
    running = True
    color = 'white'
    while running:
        screen.fill(pygame.Color((0, 0, 0)))
        if restart:
            for sprite in all_sprites:
                sprite.kill()
            dungeon = Dungeon(level)
            player_x, player_y = dungeon.render()
            player = Player(8, 2, player_x, player_y)
            restart = False
        moving = False
        x, y = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    x = -player_v
                    flip = True
                elif event.key == pygame.K_w:
                    y = -player_v
                elif event.key == pygame.K_d:
                    x = player_v
                    flip = False
                elif event.key == pygame.K_s:
                    y = player_v
                elif event.key == pygame.K_r:
                    restart = True
        if (x, y) != (0, 0):
            moving = True

        player.rect.x += x
        player.rect.y += y
        player.update(x, y, flip, False)
        slimes_group.update(x, y, flip)
        tables_group.update(x, y, flip)
        spikes_group.update()
        keys_group.update()
        doors_group.update()

        tiles_group.draw(screen)
        slimes_group.draw(screen)
        tables_group.draw(screen)
        keys_group.draw(screen)
        doors_group.draw(screen)
        player_group.draw(screen)
        spikes_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()

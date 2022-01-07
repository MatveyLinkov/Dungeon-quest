import os
import sys
import pygame
import pytmx

pygame.init()
restart = False
size = width, height = 432, 384
FPS = 120
MAPS_DIR = 'levels'
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
slimes_group = pygame.sprite.Group()
tables_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
kill = []


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


player_sheet = pygame.transform.scale(load_image('knight_sheet.png'), (368, 96))
slime_sheet = load_image('slime_idle_spritesheet.png')
floor = [6, 15, 21, 22, 23, 24, 30, 31, 32, 33]
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
            if obj.name == 'Player':
                self.player_x, self.player_y = obj.x // tile_width, obj.y // tile_height
            elif obj.type == 'slime':
                Slime(6, 1, obj.x // tile_width, obj.y // tile_height)

    def render(self):
        for i in range(2):
            for y in range(self.height):
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, i)
                    if image:
                        if self.get_tile_id((x, y), 1) == 15 and i == 1:
                            Table(x, y, image)
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
        self.half_frames = 48
        self.crop_sheet(player_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 1, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.attempt = 23

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(6)]

    def update(self, x, y, flip, back):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[:self.half_frames])
        self.image = self.frames[:self.half_frames][self.cur_frame]
        if moving:
            self.attempt -= 1
        if flip:
            self.image = pygame.transform.flip(self.image, True, False)
        if dungeon.get_tile_id((self.rect.x // 48, self.rect.y // 48), 0) not in floor or back:
            self.rect.x -= x
            self.rect.y -= y
            self.attempt += 1
        draw(screen, self.attempt, (self.rect.x // ts, self.rect.y // ts))


class Slime(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(slimes_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.frames = []
        self.crop_sheet(slime_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y - 3)

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(10)]

    def update(self, x, y, flip):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if (self.pos_x, self.pos_y) == (player.rect.x // ts, player.rect.y // ts):
            self.rect.x += x
            self.rect.y += y
            self.pos_x += x // ts
            self.pos_y += y // ts
            player_group.update(x, y, flip, True)
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
        if (dungeon.get_tile_id((self.rect.x // ts, self.rect.y // ts), 0) not in floor or
            dungeon.get_tile_id((self.rect.x // ts, self.rect.y // ts), 1) in floor[:1])\
                and touch >= 1:
            self.rect.x -= x
            self.rect.y -= y


def draw(screen, text, position):
    global restart
    if text == 0:
        text = 'X'
    elif text < 0:
        restart = True
    if position == (6, 6):
        text = 'WIN'
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 50)
    text = font.render(str(text), True, (255, 255, 255))
    text_x = 10
    text_y = 10
    screen.blit(text, (text_x, text_y))


if __name__ == '__main__':
    pygame.display.set_caption('Dungeon Quest: feature')

    dungeon = Dungeon('castletaker1.tmx')
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)

    player_x, player_y = dungeon.render()
    player = Player(8, 2, player_x, player_y)
    player_v = 48

    moving = False
    flip = False
    running = True
    while running:
        screen.fill(pygame.Color((0, 0, 0)))
        if restart:
            for sprite in all_sprites:
                sprite.kill()
            dungeon = Dungeon('castletaker1.tmx')
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

        tiles_group.draw(screen)
        slimes_group.draw(screen)
        tables_group.draw(screen)
        player_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()

import os
import sys
import pygame
import pytmx
import numpy as np

print('Нажмите F для уничтожения всех дверей')
pygame.init()
size = width, height = 1280, 720
FPS = 120
MAPS_DIR = 'levels'
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
shot_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


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
walls = []
doors = [37, 38, 39, 40, 47, 48, 49, 50, 57, 58, 59, 60, 67, 68]
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

    def render(self):
        for i in range(3):
            for y in range(self.height):
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, i)
                    if image:
                        if i == 1 and self.get_tile_id((x, y), i) not in walls:
                            walls.append(self.get_tile_id((x, y), i))
                        Tile(self.get_tile_id((x, y), i), x, y, image)
        return self.player_x, self.player_y

    def get_tile_id(self, position, layer):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, layer)]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_id, pos_x, pos_y, image):
        super().__init__(tiles_group, all_sprites)
        if tile_id in walls:
            self.add(walls_group)
            if tile_id in doors:
                self.add(doors_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        if self in doors_group:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.half_frames = 48
        self.crop_sheet(player_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x + 12, tile_height * pos_y + 12)
        self.mask = pygame.mask.from_surface(self.image)
        self.clock = pygame.time.Clock()

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(6)]

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
            if len(list(filter(lambda s: pygame.sprite.collide_mask(self, s),
                               np.array(list(walls_group))))) >= 1:
                self.rect.x -= x
                self.rect.y -= y


class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, vx, vy):
        super().__init__(shot_group, all_sprites)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color((255, 45, 190)), (radius, radius), radius)
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


if __name__ == '__main__':
    pygame.display.set_caption('Dungeon Quest: feature')

    dungeon = Dungeon('dungeon_map1.tmx')
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)

    player_x, player_y = dungeon.render()
    player = Player(8, 2, player_x, player_y)

    camera = Camera()
    x, y = 0, 0
    player_v = 3
    shot_v = 7

    moving = False
    flip = False
    running = True
    while running:
        screen.fill(pygame.Color((42, 22, 30)))
        moving = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    x -= player_v
                    flip = True
                elif event.key == pygame.K_w:
                    y -= player_v
                elif event.key == pygame.K_d:
                    x += player_v
                    flip = False
                elif event.key == pygame.K_s:
                    y += player_v
                if event.key == pygame.K_LEFT:
                    shot = Shot(player.rect.x - 20, player.rect.y + 27, 10, -shot_v, 0)
                elif event.key == pygame.K_RIGHT:
                    shot = Shot(player.rect.x + 69, player.rect.y + 27, 10, shot_v, 0)
                elif event.key == pygame.K_UP:
                    shot = Shot(player.rect.x + 27, player.rect.y - 17, 10, 0, -shot_v)
                elif event.key == pygame.K_DOWN:
                    shot = Shot(player.rect.x + 27, player.rect.y + 75, 10, 0, shot_v)
                elif event.key == pygame.K_f:
                    tiles_group.update()

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

        player.rect.x += x
        player.rect.y += y
        player.update(x, y, flip)
        shot_group.update(False)
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        tiles_group.draw(screen)
        player_group.draw(screen)
        shot_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()

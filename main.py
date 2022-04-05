import os
import random
import sys
import tkinter as tk

import pygame
import pytmx


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


def terminate():
    pygame.quit()
    sys.exit()


def getting_weapon():
    global current_weapon, inventory
    new_weapon = random.choice(weapons[1:])
    inventory[2] = new_weapon
    WeaponInInventory(weapons_image[new_weapon], 1)


def choose_weapon(button):
    global current_weapon
    if button == 1:
        current_weapon = inventory[1]
        Inventory(0, True)
    elif button == 2:
        Inventory(1, True)
        if len(inventory) >= 2:
            current_weapon = inventory[2]


def show_text(screen, text, font, position, color):  # преобразование текста
    font_color = pygame.Color(color)
    text = font.render(text, 1, font_color)  # передаём строку для экрана, затем сглаживание, цвет
    screen.blit(text, position)


def start_screen():  # начальный экран
    global transit, screen
    if transit:
        pygame.mixer.music.load('music/intro.mp3')
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(volume)
    pygame.mouse.set_visible(True)
    selection_pos = 0
    text = ['Head-Knight', 'Играть', 'Мануал', 'Настройки', 'Выход']
    if c == 1:
        fon = pygame.transform.scale(load_image('start_fon_720p.png'), (resize(1280), resize(720)))
    else:
        fon = pygame.transform.scale(load_image('start_fon.png'), (resize(1280), resize(720)))
    coord_x = [375, 554, 550, 510, 570]
    coord_y = [100, 260, 340, 420, 500]
    fonts_size = [130, 65, 65, 65, 65]
    selection_coord = [(resize(500), resize(250)), (resize(500), resize(330)),
                       (resize(500), resize(410)), (resize(500), resize(490))]
    while not start_game:
        screen.fill((0, 0, 0))
        screen.blit(fon, (0, 0))
        for elem in range(len(text)):
            font = [pygame.font.Font("fonts/American TextC.ttf", resize(fonts_size[elem])),
                    pygame.font.Font("fonts/heinrichtext.ttf", resize(fonts_size[elem])),
                    pygame.font.Font("fonts/heinrichtext.ttf", resize(fonts_size[elem])),
                    pygame.font.Font("fonts/heinrichtext.ttf", resize(fonts_size[elem])),
                    pygame.font.Font("fonts/heinrichtext.ttf", resize(fonts_size[elem]))]
            show_text(screen, text[elem], font[elem], (resize(coord_x[elem]),
                                                       resize(coord_y[elem])), 'orange')
        pygame.draw.rect(screen, '#ffd700', (selection_coord[selection_pos],
                                             (resize(300), resize(75))), resize(5))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if resize(500) <= event.pos[0] <= resize(805) and\
                            resize(250) <= event.pos[1] <= resize(580):
                        if selection_pos == 0:
                            transit = True
                            start_game.append(1)
                            return
                        elif selection_pos == 1:
                            tutorial()
                        elif selection_pos == 2:
                            settings()
                        elif selection_pos == 3:
                            terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    selection_pos += 1
                    if selection_pos == 4:
                        selection_pos = 0
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    selection_pos -= 1
                    if selection_pos == -1:
                        selection_pos = 3
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if selection_pos == 0:
                        transit = True
                        start_game.append(1)
                        return
                    elif selection_pos == 1:
                        tutorial()
                    elif selection_pos == 2:
                        settings()
                    if selection_pos == 3:
                        terminate()
                elif event.key == pygame.K_ESCAPE:
                    terminate()
            elif event.type == pygame.MOUSEMOTION:
                if resize(500) <= event.pos[0] <= resize(805):
                    if resize(250) <= event.pos[1] <= resize(330):
                        selection_pos = 0
                    if resize(330) <= event.pos[1] <= resize(410):
                        selection_pos = 1
                    if resize(410) <= event.pos[1] <= resize(490):
                        selection_pos = 2
                    if resize(490) <= event.pos[1] <= resize(580):
                        selection_pos = 3
        pygame.display.flip()
    return


def tutorial():
    global transit
    transit = False
    blurred_fon = pygame.transform.scale(load_image('blurred_fon.png'), (resize(1280), resize(720)))
    screen.blit(blurred_fon, (0, 0))
    font = pygame.font.Font("fonts/heinrichtext.ttf", resize(50))
    text = ['1. Ходьба - WASD;',
            '2. Стрельба - стрелки на клавиатуре;',
            '3. Выбор оружия - цифры на клавиатуре (1, 2);',
            '4. Взаимодейстия с объектами - E;',
            '5. Перезагрузка уровня - R;',
            '6. Выход - Esc.']
    show_text(screen, 'Назад', pygame.font.Font("fonts/heinrichtext.ttf",
                                                resize(60)), (resize(1120), resize(20)), 'orange')
    pygame.draw.rect(screen, '#ffd700', ((resize(1110), resize(10)),
                                         (resize(155), resize(70))), resize(5))
    for i in range(len(text)):
        show_text(screen, text[i], font, (resize(165), resize(90 + i * 100)), 'white')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resize(1115) <= event.pos[0] <= resize(1260) and\
                        resize(15) <= event.pos[1] <= resize(75):
                    start_screen()
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    start_screen()
                    return
        pygame.display.flip()


def settings():
    global c, screen, full_screen, volume, size, width, height, transit
    transit = False
    settings_accept = False
    selection_pos = 0
    coeff = [resolution.index(el) for el in resolution if c in resolution[resolution.index(el)]][0]
    while True:
        text = [f'Разрешение',
                'X'.join(str(el) for el in resolution[coeff][list(resolution[coeff].keys())[-1]]),
                'Полный экран',
                ['OFF', 'ON'][full_screen],
                'Громкость музыки',
                str(round(volume * 10)),
                'Применить изменения',
                'Назад']
        selection_coord = [(resize(145), resize(70)), (resize(145), resize(270)),
                           (resize(145), resize(470)), (resize(145), resize(620)),
                           (resize(985), resize(620))]
        font = pygame.font.Font("fonts/heinrichtext.ttf", resize(75))
        blurred_fon = pygame.transform.scale(load_image('blurred_fon.png'),
                                             (resize(1280), resize(720)))
        screen.blit(blurred_fon, (0, 0))
        if selection_pos < 3:
            pygame.draw.rect(screen, '#ffd700', (selection_coord[selection_pos],
                                                 (resize(1020), resize(80))), resize(5))
        elif selection_pos == 3:
            pygame.draw.rect(screen, '#ffd700', (selection_coord[selection_pos],
                                                 (resize(720), resize(80))), resize(5))
        else:
            pygame.draw.rect(screen, '#ffd700', (selection_coord[selection_pos],
                                                 (resize(190), resize(80))), resize(5))
        for i in range(6):
            if i % 2 == 0:
                show_text(screen, text[i], font, (resize(165), resize(80 + i * 100)), 'orange')
            else:
                show_text(screen, text[i], font,
                          (resize(880), resize(80 + (i - 1) * 100)), 'orange')
        for i in range(6, 8):
            show_text(screen, text[i], font, (resize(165 + (i - 6) * 830), resize(630)), 'orange')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    start_screen()
                    return
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    if selection_pos == 0:
                        coeff -= 1
                        if coeff <= 0:
                            coeff = 6
                    elif selection_pos == 1:
                        full_screen = -(full_screen - 1)
                    elif selection_pos == 2:
                        volume -= 0.1
                        if volume < 0:
                            volume = 1
                    elif selection_pos == 3:
                        selection_pos = 2
                    elif selection_pos == 4:
                        selection_pos = 3
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    if selection_pos == 0:
                        coeff += 1
                        if coeff >= len(resolution):
                            coeff = 0
                    elif selection_pos == 1:
                        full_screen = -(full_screen - 1)
                    elif selection_pos == 2:
                        volume += 0.1
                        if volume > 1:
                            volume = 0
                    elif selection_pos == 3:
                        selection_pos = 4
                    elif selection_pos == 4:
                        selection_pos = 0
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selection_pos += 1
                    if selection_pos == 5:
                        selection_pos = 0
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    selection_pos -= 1
                    if selection_pos == -1:
                        selection_pos = 4
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if selection_pos == 3:
                        settings_accept = True
                    elif selection_pos == 4:
                        start_screen()
                        return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if resize(145) <= event.pos[0] <= resize(1165) and \
                            resize(60) <= event.pos[1] <= resize(170):
                        if selection_pos == 0:
                            coeff += 1
                            if coeff >= len(resolution):
                                coeff = 0
                    if resize(145) <= event.pos[0] <= resize(1165) and \
                            resize(260) <= event.pos[1] <= resize(370):
                        full_screen = -(full_screen - 1)
                    if resize(145) <= event.pos[0] <= resize(1165) and \
                            resize(460) <= event.pos[1] <= resize(570):
                        volume += 0.1
                        if volume > 1:
                            volume = 0
                    if resize(145) <= event.pos[0] <= resize(860) and \
                            resize(620) <= event.pos[1] <= resize(700):
                        settings_accept = True
                    if resize(980) <= event.pos[0] <= resize(1170) and \
                            resize(620) <= event.pos[1] <= resize(700):
                        start_screen()
                        return
            elif event.type == pygame.MOUSEMOTION:
                if resize(145) <= event.pos[0] <= resize(1165) and\
                        resize(60) <= event.pos[1] <= resize(170):
                    selection_pos = 0
                if resize(145) <= event.pos[0] <= resize(1165) and\
                        resize(260) <= event.pos[1] <= resize(370):
                    selection_pos = 1
                if resize(145) <= event.pos[0] <= resize(1165) and\
                        resize(460) <= event.pos[1] <= resize(570):
                    selection_pos = 2
                if resize(145) <= event.pos[0] <= resize(860) and \
                        resize(620) <= event.pos[1] <= resize(700):
                    selection_pos = 3
                if resize(980) <= event.pos[0] <= resize(1170) and\
                        resize(620) <= event.pos[1] <= resize(700):
                    selection_pos = 4
            if settings_accept:
                if full_screen == 0:
                    c = list(resolution[coeff].keys())[0]
                    if resolution[coeff][list(resolution[coeff].keys())[-1]] !=\
                            (win_width, win_height):
                        c = list(resolution[coeff].keys())[-1]
                    size = width, height = resolution[coeff][c]
                    screen = pygame.display.set_mode(resolution[coeff][c])
                else:
                    c = list(resolution[coeff].keys())[-1]
                    size = width, height = resolution[coeff][c]
                    screen = pygame.display.set_mode(resolution[coeff][c], pygame.FULLSCREEN)
                settings_accept = False
                with open('settings.ini', 'w') as settings_file:
                    settings_file.write(f'ScreenSize - {list(resolution[coeff].keys())[0]}\n')
                    settings_file.write(f'MusicVolume - {volume}')
        pygame.mixer.music.set_volume(volume)
        pygame.display.flip()


def statistics():
    global count
    count += 1
    if not transit:
        if count >= 100:
            count = 0
            timer[1] += 1
            if timer[1] == 60:
                timer[1] = 0
                timer[0] += 1


def transition():
    screen.fill(pygame.Color(0, 0, 0))
    if next_level is True:
        if len(str(timer[0])) < 2:
            timer[0] = '0' + str(timer[0])
        if len(str(timer[1])) < 2:
            timer[1] = '0' + str(timer[1])
        text = [f"Уровень: {str(int(map_number) - 1)}",
                f"Время: {timer[0]}:{timer[1]}",
                f"Пройденных мини-игр: {minigame_count}"]
        font = pygame.font.Font("fonts/heinrichtext.ttf", resize(75))
        for i in range(len(text)):
            show_text(screen, text[i], font, (resize(185), resize(110 + 210 * i)), 'white')


def move_count(screen, text, position, color):
    global restart, dungeon_map, minigame_count, key_up
    if text == 0:
        text = 'X'
    elif text < 0:
        restart = True
    if position == maps[level][1] and text != -1:
        text = ''
        [s.kill() for s in all_sprites]
        minigame_count += 1
        dungeon_map = True
        key_up = False
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, resize(100))
    text = font.render(str(text), True, color)
    text_x = resize(120)
    text_y = resize(120)
    screen.blit(text, (text_x, text_y))


def resize(number):
    return round(number * c)


root = tk.Tk()
pygame.init()
data = [float(el.split(' - ')[-1].strip()) for el in open('settings.ini', 'r').readlines()]
resolution = [{0.86796875: (1111, 628), 0.91875: (1176, 664)},
              {0.94453125: (1209, 680), 1: (1280, 720)},
              {1.00390625: (1285, 726), 1.0625: (1360, 768)},
              {1.00859375: (1291, 726), 1.0671: (1366, 768)},
              {1.18125: (1512, 850), 1.25: (1600, 900)},
              {1.3046875: (1670, 937), 1.38125: (1768, 992)},
              {1.416666666666667: (1814, 1020), 1.5: (1920, 1080)}]
win_width, win_height = root.winfo_screenwidth(), root.winfo_screenheight()
s = {}
if data[0] == 0:
    size = width, height = win_width - win_width // 18, win_height - win_height // 18
else:
    s = [el for el in resolution if data[0] in el][0]
    size = width, height = [el for el in resolution if data[0] in el][0][data[0]]
    if s[list(s.keys())[-1]] != (win_width, win_height):
        size = width, height = s[list(s.keys())[-1]]
resolution = resolution[:[el[list(el.keys())[0]]
                          for el in resolution].index((win_width - win_width // 18,
                                                       win_height - win_height // 18)) + 1]
full_screen = 0
volume = data[1]
if data[0] == 0:
    c = list(resolution[[el[list(el.keys())[0]] for el in resolution].index(size)].keys())[0]
else:
    c = data[0]
    if s[list(s.keys())[-1]] != (win_width, win_height):
        c = list(s.keys())[-1]
screen = pygame.display.set_mode(size)
map_number = '1'
maps = {'castle_1.tmx': [23, (11, 8)], 'castle_2.tmx': [24, (10, 7)],
        'castle_3.tmx': [23, (12, 5)]}
level = 'castle_' + map_number + '.tmx'
FPS = 60
start_success = False
next_level = False
clock = pygame.time.Clock()
MAPS_DIR = 'levels'
final = False
transit = True
start_game = []
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
barriers_group = pygame.sprite.Group()
empty_group = pygame.sprite.Group()
bombs_group = pygame.sprite.Group()
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
life_group = pygame.sprite.Group()
slimes_group = pygame.sprite.Group()
tables_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
mini_player_group = pygame.sprite.Group()
mini_keys_group = pygame.sprite.Group()
mini_doors_group = pygame.sprite.Group()
all_cells_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()
floor = [6, 15, 21, 22, 23, 24, 30, 31, 32, 33]
completed_levels = []
destroyed_barriers = []
player_sheet = pygame.transform.scale(load_image('knight_sheet.png'), (552, 150))
skull_sheet = load_image('skull_sheet.png')
goblin_sheet = load_image('goblin_spritesheet.png')
bomber_sheet = pygame.transform.scale(load_image('bomber_spritesheet.png'), (288, 48))
health_ui = load_image('health_ui.png')
life_image = pygame.transform.scale(load_image('life.png'), (48, 36))
cell_image = pygame.transform.scale(load_image('inventory_cell.png'), (50, 50))
choose_cell = pygame.transform.scale(load_image('active_cell.png'), (50, 50))
opened_chest = load_image('chest_open_anim_3.png')
closed_chest = load_image('chest_open_anim_1.png')
key_image = load_image('key.png')
arrow_image = pygame.transform.scale(load_image('arrow.png'), (48, 48))
bomb_sheet = load_image('bomb_sheet.png')
hit_effect_sheet = pygame.transform.scale(load_image('hit_effect.png'), (96, 32))
explosion_sheet = pygame.transform.scale(load_image('explosion_sheet.png'), (336, 48))
enemy_dead_sheet = load_image('enemy_afterdead.png')
game_over = pygame.transform.scale(load_image('game_over.png'), (750, 375))
player_dead = pygame.transform.scale(load_image('knight_dead.png'), (138, 102))
animated_slimes = pygame.transform.scale(load_image('slime_animated.png'), (1728, 576))
player_win = pygame.transform.scale(load_image('player_win.png'), (1152, 162))
bag_coins = pygame.transform.scale(load_image('bag_coins.png'), (96, 96))
bags_coord = [(260, 500), (365, 425), (470, 500)]
golden_chest = pygame.transform.scale(load_image('golden_chest.png'), (96, 96))
golden_chest_coord = [(810, 500), (915, 425), (1020, 500)]
mini_player_sheet = pygame.transform.scale(load_image('knight_sheet.png'), (448, 112))
slime_sheet = load_image('slime_idle_spritesheet.png')
spikes_images = ['holes.png', 'spikes.png', 'on_holes.png', 'on_spikes.png']
walls = []
doors = [37, 38, 39, 40, 47, 48, 49, 50, 57, 58, 59, 60, 67, 68]
barriers = [44, 45, 53, 54]
animated_sprites = {75: 'flag_sheet.png',
                    91: 'torch_sheet.png', 94: 'candle_sheet.png'}
weapons_image = {'wooden_bow': load_image('wooden_bow.png'),
                 'iron_sword':
                     pygame.transform.scale(load_image('iron_sword.png'), (20, 42))}
weapons = ['wooden_bow', 'iron_sword']
bows = ['wooden_bow']
swords = ['iron_sword']
splash_effect = load_image('slash_effect_anim.png')
inventory = {1: 'wooden_bow', 2: None, 3: None}
current_weapon = inventory[1]
ts = tile_width = tile_height = 48
chest = 84
key = 89
player = None


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
            elif obj.type == 'room' and obj.name not in completed_levels:
                Room(obj.name, obj.x, obj.y, obj.width, obj.height)
            elif obj.name == 'Skull':
                Skull(4, 1, obj.x // ts, obj.y // ts, )
            elif obj.name == 'Goblin':
                Goblin(6, 2, obj.x // ts, obj.y // ts, )
            elif obj.name == 'Bomber':
                Bomber(6, 1, obj.x // ts, obj.y // ts, )
            elif obj.type == 'script':
                Script(obj.x, obj.y, obj.width, obj.height)
            elif obj.type == '???':
                Tile(0, obj.x // ts, obj.y // ts, pygame.transform.scale(load_image('secret.png'),
                                                                         (250, 225)))

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
                            if (x, y) not in destroyed_barriers:
                                Barrier(self.get_tile_id((x, y), i), x, y, image)
                        elif self.get_tile_id((x, y), i) in animated_sprites:
                            AnimatedSprite(self.get_tile_id((x, y), i), 4, 1, x, y)
                        elif self.get_tile_id((x, y), i) - 100 in animated_sprites:
                            AnimatedSprite(self.get_tile_id((x, y), i) - 100, 4, 1, x, y)
                        elif self.get_tile_id((x, y), i) - 100 == chest or \
                                self.get_tile_id((x, y), i) == chest:
                            Chest(x, y)
                        elif (self.get_tile_id((x, y), i) == key or
                              self.get_tile_id((x, y), i) - 100 == key):
                            Key(x, y)
                        elif self.get_tile_id((x, y), i) == 81 or \
                                self.get_tile_id((x, y), i) - 100 == 81:
                            Hatch(x, y, image)
                        elif self.get_tile_id((x, y), i) == 82 or \
                                self.get_tile_id((x, y), i) - 100 == 82:
                            Ladder(x, y, image)
                        else:
                            Tile(self.get_tile_id((x, y), i), x, y, image, i)

        return self.player_x, self.player_y

    def get_tile_id(self, position, layer):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, layer)]


class Castle:
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
                            MiniKey(x, y, image)
                        elif self.get_tile_id((x, y), i) == 37:
                            MiniDoor(x, y, image)
                        else:
                            Tile(self.get_tile_id((x, y), i), x, y, image)
        return self.player_x, self.player_y

    def get_tile_id(self, position, layer):
        try:
            return self.map.tiledgidmap[self.map.get_tile_gid(*position, layer)]
        except KeyError:
            pass


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_id, pos_x, pos_y, image, layer=0):
        super().__init__(tiles_group, all_sprites)
        if tile_id in walls and layer == 1:
            self.add(walls_group)
        self.image = image
        self.rect = self.image.get_rect()
        if dungeon_map:
            self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        else:
            self.rect = self.rect.move((width - 1280) / 2 + tile_width * pos_x,
                                       (height - 720) / 2 + tile_height * pos_y)


class Barrier(pygame.sprite.Sprite):
    def __init__(self, id,  pos_x, pos_y, image):
        super().__init__(barriers_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        if id == 79 or id - 100 == 79:
            self.add(empty_group)

    def update(self):
        if pygame.sprite.spritecollideany(self, destroyer_group):
            if [(destroyer.update(True), Particle(7, 1, self.rect.x, self.rect.y,
                explosion_sheet, destroyer)) for destroyer in destroyer_group
                    if pygame.sprite.collide_mask(self, destroyer)]:
                destroyed_barriers.append((self.pos_x, self.pos_y))
                self.kill()
        elif pygame.sprite.spritecollideany(self, bombs_group) and self not in empty_group:
            bombs_group.update(True)
            destroyed_barriers.append((self.pos_x, self.pos_y))
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
            WeaponInInventory(key_image, 2)
            self.kill()
        if not pygame.sprite.spritecollideany(self, rooms_group):
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
                if self.enemy:
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
    def __init__(self, name, pos_x, pos_y, width, height):
        super().__init__(rooms_group, all_sprites)
        self.name = name
        self.image = pygame.Surface((width, height))
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        self.fight = False

    def update(self):
        global doors_close
        if pygame.sprite.spritecollideany(self, player_group):
            if not pygame.sprite.spritecollideany(self, enemy_group) and not\
                    pygame.sprite.spritecollideany(self, key_group):
                doors_close = False
                self.kill()
                completed_levels.append(self.name)
            if not self.fight and doors_close:
                if [1 for enemy in filter(lambda x: pygame.sprite.collide_mask(self, x),
                                          enemy_group)]:
                    enemy_group.update(True)
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
        elif not pygame.sprite.spritecollideany(self, rooms_group):
            self.kill()


class Hatch(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(hatch_group, all_sprites)
        self.image = image
        self.count = 0
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self, button, key_available):
        global dungeon_map, change_mode
        if button == 'e' and key_available is True and not change_mode:
            if pygame.sprite.spritecollideany(self, player_group):
                self.count += 1
                [s.kill() for s in all_sprites]
                dungeon_map = False
                change_mode = True
                inventory[3] = None


class Ladder(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(ladder_group, all_sprites)
        self.image = image
        self.count = 0
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self, button):
        global next_level
        global map_number, restart, transit
        if button == 'e':
            if pygame.sprite.spritecollideany(self, player_group) and self.count == 0:
                self.count += 1
                map_number = str(int(map_number) + 1)
                restart = True
                transit = True
                next_level = True


class Player(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y, change):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.half_frames = 24
        self.crop_sheet(player_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        if not final:
            self.rect = self.rect.move(tile_width * pos_x + 36, tile_height * pos_y + 24)
            if change:
                for hatch in hatch_group:
                    self.rect.x, self.rect.y = hatch.rect.x - 12, hatch.rect.y - 12
        else:
            self.rect = self.rect.move(600, 350)
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

    def update(self, x, y, flip=False):
        if moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.half_frames:])
            self.image = self.frames[self.half_frames:][self.cur_frame]
        else:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[:self.half_frames])
            self.image = self.frames[:self.half_frames][self.cur_frame]
        self.image = pygame.transform.flip(self.image, flip, False)
        if pygame.sprite.spritecollideany(self, walls_group) or\
                pygame.sprite.spritecollideany(self, barriers_group):
            self.rect.x -= x
            self.rect.y -= y
        if pygame.sprite.spritecollideany(self, enemy_group):
            return True
        elif pygame.sprite.spritecollideany(self, bombs_group):
            bombs_group.update(True)
            return True


class Chest(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(chest_group, all_sprites)
        self.image = closed_chest
        self.count = 0
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y + 55)

    def update(self, button):
        global opened_case
        if pygame.sprite.spritecollideany(self, player_group):
            if button == 'e':
                opened_case = True
                self.count += 1
                if self.count == 1:
                    getting_weapon()
        if opened_case:
            self.image = opened_chest


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
        if pygame.sprite.spritecollideany(self, walls_group) or \
                (pygame.sprite.spritecollideany(self, barriers_group) and not
                 pygame.sprite.spritecollideany(self, empty_group)) or \
                ((pygame.sprite.spritecollideany(self, enemy_group) or
                  pygame.sprite.spritecollideany(self, bombs_group)) and damage):
            Particle(3, 1, self.rect.x + self.particle_x, self.rect.y + self.particle_y,
                     hit_effect_sheet)
            self.kill()


class Melee(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon, angle):
        super().__init__(melee_group)
        self.frames = []
        self.crop_sheet(splash_effect, 3, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.angle = angle
        self.weapon = weapon
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - 15, y - 10
        if angle == 270:
            self.rect = self.rect.move(-12, 9)
        elif angle == 180:
            self.rect = self.rect.move(-24, -12)
        elif angle == 90:
            self.rect = self.rect.move(-12, -30)
        elif angle == 0:
            self.rect = self.rect.move(12, -12)

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
        if close and pygame.sprite.spritecollideany(self, rooms_group):
            self.close = close
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.close:
            if len([self.rect.x + j for j in range(self.rect.width + 1)
                    if self.rect.x + j in
                    [player.rect.x + i for i in range(player.rect.width + 1)]]) >= 1\
                    and not self.moving:
                if self.rect.y < player.rect.y:
                    self.move_y = self.speed
                else:
                    self.move_y = -self.speed
                self.moving = True
            elif len([self.rect.y + j for j in range(self.rect.height + 1)
                      if self.rect.y + j in
                      [player.rect.y + i for i in range(player.rect.height + 1)]]) >= 1 \
                    and not self.moving:
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
            if self.hp <= 0 or not pygame.sprite.spritecollideany(self, rooms_group):
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
        self.speed = 3
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
        if close and pygame.sprite.spritecollideany(self, rooms_group):
            self.close = not self.close
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[:self.half_frames])
        self.image = self.frames[:self.half_frames][self.cur_frame]
        self.move_x, self.move_y = 0, 0
        if self.close:
            if (self.rect.x // ts, self.rect.y // ts) != (player.rect.x // ts, player.rect.y // ts):
                self.moving = True
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.half_frames:])
            self.image = self.frames[self.half_frames:][self.cur_frame]
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
        if self.hp <= 0 or not pygame.sprite.spritecollideany(self, rooms_group):
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
        self.bomb = None
        self.time = 0

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(6)]

    def update(self, close=False):
        if close and pygame.sprite.spritecollideany(self, rooms_group):
            self.close = not self.close
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.close:
            if len([self.rect.y + j for j in range(self.rect.height + 1)
                    if self.rect.y + j in
                    [player.rect.y + i for i in range(player.rect.height + 1)]]) >= 1:
                if self.rect.x < player.rect.x:
                    if not self.bomb or not self.bomb.alive():
                        self.time += 1
                        if self.time == 25:
                            self.bomb = Bomb(10, 1, self.rect.x, self.rect.y)
                            self.time = 0
            if pygame.sprite.spritecollideany(self, shot_group):
                if current_weapon == 'wooden_bow':
                    self.damage = 1
                    shot_group.update(True)
            self.hp -= self.damage
            self.damage = 0
            if self.hp <= 0 or not pygame.sprite.spritecollideany(self, rooms_group):
                Particle(4, 1, self.rect.x, self.rect.y, enemy_dead_sheet)
                self.kill()


class Bomb(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(bombs_group, all_sprites)
        self.frames = []
        self.crop_sheet(bomb_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos_x + 48, pos_y)
        self.speed = 12

    def crop_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_coord = (self.rect.w * j, self.rect.h * i)
                [self.frames.append(sheet.subsurface(pygame.Rect(frame_coord, self.rect.size)))
                 for i in range(4)]

    def update(self, damage=False):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x += self.speed
        if pygame.sprite.spritecollideany(self, walls_group) or \
            ((pygame.sprite.spritecollideany(self, barriers_group) and damage) and not
             pygame.sprite.spritecollideany(self, empty_group)) or \
                (pygame.sprite.spritecollideany(self, player_group) and damage) or\
                pygame.sprite.spritecollideany(self, shot_group) or\
                pygame.sprite.spritecollideany(self, melee_group):
            if pygame.sprite.spritecollideany(self, shot_group):
                shot_group.update(True)
            Particle(7, 1, self.rect.x, self.rect.y, explosion_sheet)
            self.kill()


class HealthPoints(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(health_group)
        self.image = health_ui
        self.rect = self.image.get_rect()


class Life(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, number):
        super().__init__(life_group)
        self.number = number
        self.image = life_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos_x, pos_y)

    def update(self, lifespan):
        if lifespan <= self.number:
            self.kill()


class Inventory(pygame.sprite.Sprite):
    def __init__(self, section, active=False):
        super().__init__(all_cells_group)
        if active:
            self.image = choose_cell
            Inventory((section + 3) % 2)
        else:
            self.image = cell_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((width - 150 + section * tile_width), 0)


class WeaponInInventory(pygame.sprite.Sprite):
    def __init__(self, weapon, section):
        super().__init__(weapon_group)
        self.image = weapon
        self.rect = self.image.get_rect()
        if section != 2:
            self.rect = self.rect.move(width - 135 + 49 * section, 5)
        else:
            self.rect = self.rect.move(width - 54, 0)


class MiniPlayer(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.frames = []
        self.half_frames = 24
        self.crop_sheet(mini_player_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((width - 1280) / 2 + tile_width * pos_x + 4,
                                   (height - 720) / 2 + tile_height * pos_y + 4)
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

    def update(self, x, y, flip, back=False):
        damage = 0
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[:self.half_frames])
        self.image = self.frames[:self.half_frames][self.cur_frame]
        self.pos_x += x // ts
        self.pos_y += y // ts
        if moving:
            damage += 1
        if flip:
            self.image = pygame.transform.flip(self.image, True, False)
        if not castle.get_tile_id(((self.rect.x - (width - 1280) / 2) // 64,
                                   (self.rect.y - (height - 720) / 2) // 64), 0) or back:
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
        move_count(screen, self.attempt, ((self.rect.x - (width - 1280) / 2) // ts,
                                          (self.rect.y - (height - 720) / 2) // ts), self.color)


class Slime(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        super().__init__(slimes_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.frames = []
        self.crop_sheet(slime_sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((width - 1280) / 2 + tile_width * pos_x + 8,
                                   (height - 720) / 2 + tile_height * pos_y + 8)

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
        if (self.pos_x, self.pos_y) == ((player.rect.x - (width - 1280) / 2) // ts,
                                        (player.rect.y - (height - 720) / 2) // ts):
            self.rect.x += x
            self.rect.y += y
            self.pos_x += x // ts
            self.pos_y += y // ts
            player_group.update(x, y, flip, True)
            if pygame.sprite.spritecollideany(self, tables_group):
                self.kill()
        tile_id = castle.get_tile_id((self.pos_x, self.pos_y), 0)
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
        self.rect = self.rect.move((width - 1280) / 2 + tile_width * pos_x,
                                   (height - 720) / 2 + tile_height * pos_y)

    def update(self, x, y, flip):
        touch = 0
        if ((self.rect.x - (width - 1280) / 2) // ts, (self.rect.y - (height - 720) / 2) // ts) ==\
                ((player.rect.x - (width - 1280) / 2) // ts,
                 (player.rect.y - (height - 720) / 2) // ts):
            self.rect.x += x
            self.rect.y += y
            touch += 1
            player_group.update(x, y, flip, True)
        if (castle.get_tile_id(((self.rect.x - (width - 1280) / 2) // ts,
                                (self.rect.y - (height - 720) / 2) // ts), 1) or (
                ((self.rect.x - (width - 1280) / 2) // ts,
                 (self.rect.y - (height - 720) / 2) // ts) in
                [((spike_sprite.rect.x - (width - 1280) / 2) // ts,
                  (spike_sprite.rect.y - (height - 720) / 2) // ts)
                 for spike_sprite in tables_group if self != spike_sprite] and touch >= 1) or
                (((self.rect.x - (width - 1280) / 2) // ts,
                  (self.rect.y - (height - 720) / 2) // ts) in
                 [(round((slimes_sprite.rect.x - (width - 1280) / 2) / ts),
                   (round(slimes_sprite.rect.y - (height - 720) / 2) / ts))
                  for slimes_sprite in slimes_group])):
            self.rect.x -= x
            self.rect.y -= y


class Spikes(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(spikes_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = pygame.transform.scale(load_image(spikes_images[0]), (64, 64))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((width - 1280) / 2 + tile_width * pos_x,
                                   (height - 720) / 2 + tile_height * pos_y)

    def update(self):
        self.image = pygame.transform.scale(load_image(spikes_images[1]), (64, 64))
        if (self.pos_x, self.pos_y) in\
                [((s.rect.x - (width - 1280) / 2) // ts,
                  (s.rect.y - (height - 720) / 2) // ts) for s in tables_group] or\
                pygame.sprite.spritecollideany(self, player_group):
            self.image = pygame.transform.scale(load_image(spikes_images[3]), (64, 64))


class MiniKey(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(mini_keys_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((width - 1280) / 2 + tile_width * pos_x,
                                   (height - 720) / 2 + tile_height * pos_y)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            self.kill()


class MiniDoor(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(mini_doors_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((width - 1280) / 2 + tile_width * pos_x,
                                   (height - 720) / 2 + tile_height * pos_y)

    def update(self):
        if len(mini_keys_group.sprites()) == 0:
            self.kill()
        if pygame.sprite.spritecollideany(self, player_group):
            player_group.update(x, y, flip, True)


class FinalScreen(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y, image, flip=False):
        super().__init__(animated_sprites_group, all_sprites)
        self.frames = []
        self.crop_sheet(image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((width - 1280) / 2 + pos_x,
                                   (height - 720) / 2 + pos_y)
        self.flip = flip

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
        self.image = pygame.transform.flip(self.image, self.flip, False)


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
    pygame.display.set_caption('Head-Knight')
    pygame.display.set_icon(load_image('icon.ico'))
    dungeon_map = True
    x, y = 0, 0
    player_v = 6
    shot_v = 16
    hp = 4
    frames = 0
    chest_opened_count = 0
    minigame_count = 0
    count = 0
    lifesaver = 3
    timer = [0, 0]
    start_screen()
    camera = Camera()
    clock = pygame.time.Clock()
    button = None
    key_up = True
    moving = False
    flip = False
    doors_close = False
    opened_case = False
    damage = False
    visible = True
    restart = False
    change_mode = False
    exit_to_menu = False
    transit_time = 0
    running = True
    while running:
        statistics()
        screen.fill(pygame.Color((37, 19, 26)))
        moving = False
        if dungeon_map:
            if len(player_group) == 0:
                if map_number != '4':
                    [s.kill() for s in all_sprites]
                    [s.kill() for s in all_cells_group]
                    transit = True
                    ts = tile_width = tile_height = 48
                    dungeon = Dungeon(f'dungeon_{map_number}.tmx')
                    pygame.mouse.set_visible(False)
                    x, y = 0, 0
                    player_x, player_y = dungeon.render()
                    player = Player(8, 2, player_x, player_y, change_mode)
                    player_v = 6
                    heath = HealthPoints()
                    for i in range(lifesaver):
                        Life(10 + 55 * i, 50, i)
                    choose_weapon(1)
                    for section in range(0, 3):
                        cell = Inventory(section)
                    cell = Inventory(0, True)
                    WeaponInInventory(weapons_image.get('wooden_bow'), 0)
                    pygame.mixer.music.load('music/dungeon.mp3')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.6 * volume)
            if restart:
                if map_number != '4':
                    [s.kill() for s in all_sprites]
                    [s.kill() for s in weapon_group]
                    [s.kill() for s in all_cells_group]
                    completed_levels.clear()
                    destroyed_barriers.clear()
                    dungeon = Dungeon(f'dungeon_{map_number}.tmx')
                    player_x, player_y = dungeon.render()
                    player = Player(8, 2, player_x, player_y, change_mode)
                    hp = 4
                    completed_levels.clear()
                    inventory = {1: 'wooden_bow', 2: None, 3: None}
                    flip = False
                    doors_close = False
                    damage = False
                    visible = True
                    change_mode = False
                    opened_case = False
                    restart = False
                    transit = True
                    for section in range(0, 3):
                        cell = Inventory(section)
                    cell = Inventory(0, True)
                    WeaponInInventory(weapons_image.get('wooden_bow'), 0)
                    if not next_level:
                        lifesaver -= 1
                else:
                    if not final:
                        final = True
                        [s.kill() for s in all_sprites]
                        FinalScreen(1, 1, 265, 0, game_over)
                        if minigame_count == 3:
                            FinalScreen(8, 1, 571, 400, player_win)
                            for i in range(3):
                                FinalScreen(1, 1, bags_coord[i][0], bags_coord[i][1], bag_coins)
                                FinalScreen(1, 1, golden_chest_coord[i][0],
                                            golden_chest_coord[i][1], golden_chest)
                            pygame.mixer.music.load('music/good_end.mp3')
                            pygame.mixer.music.set_volume(volume)
                        else:
                            FinalScreen(1, 1, 571, 400, player_dead)
                            FinalScreen(6, 4, 500, 300, animated_slimes)
                            FinalScreen(6, 4, 500, 400, animated_slimes, True)
                            pygame.mixer.music.load('music/bad_end.mp3')
                            pygame.mixer.music.set_volume(volume)
                        pygame.mixer.music.play()
                if lifesaver <= -1 or exit_to_menu:
                    [s.kill() for s in all_sprites]
                    [s.kill() for s in weapon_group]
                    transit = True
                    [sprite.kill() for sprite in all_sprites]
                    start_screen()
                    lifesaver = 3
                    map_number = '1'
                    level = 'castle_' + map_number + '.tmx'
                    minigame_count = 0
                    exit_to_menu = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    key_down = True
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
                            Melee(player.rect.x - 39, player.rect.y + 13, current_weapon, 180)
                    elif event.key == pygame.K_RIGHT:
                        if current_weapon in bows:
                            Shot(player.rect.x + 60, player.rect.y + 13, shot_v, 0, 90)
                        elif current_weapon in swords and len(melee_group.sprites()) == 0:
                            Melee(player.rect.x + 60, player.rect.y + 13, current_weapon, 0)
                    elif event.key == pygame.K_UP:
                        if current_weapon in bows:
                            Shot(player.rect.x + 12, player.rect.y - 36, 0, -shot_v, 180)
                        elif current_weapon in swords and len(melee_group.sprites()) == 0:
                            Melee(player.rect.x + 12, player.rect.y - 36, current_weapon, 90)
                    elif event.key == pygame.K_DOWN:
                        if current_weapon in bows:
                            Shot(player.rect.x + 12, player.rect.y + 69, 0, shot_v, 0)
                        elif current_weapon in swords and len(melee_group.sprites()) == 0:
                            Melee(player.rect.x + 12, player.rect.y + 69, current_weapon, 270)
                    elif event.key == pygame.K_r:
                        restart = True
                    elif event.key == pygame.K_e:
                        button = 'e'
                    elif event.key == pygame.K_1:
                        choose_weapon(1)
                    elif event.key == pygame.K_2 and inventory[2] is not None:
                        choose_weapon(2)
                    elif event.key == pygame.K_ESCAPE:
                        restart = True
                        exit_to_menu = True
                        start_game.clear()
                        if final:
                            running = False

                elif event.type == pygame.KEYUP:
                    if key_up:
                        if event.key == pygame.K_a:
                            x += player_v
                        elif event.key == pygame.K_w:
                            y += player_v
                        elif event.key == pygame.K_d:
                            x -= player_v
                        elif event.key == pygame.K_s:
                            y -= player_v
                    key_up = True
            if (x, y) != (0, 0):
                moving = True
            if x < 0:
                flip = True
            elif x > 0:
                flip = False
            if not final:
                change_mode = False
                player.rect.x += x
                player.rect.y += y
                player_damage = player.update(x, y, flip)
                if player_damage and not damage:
                    hp -= 1
                    damage = True
                    visible = False
                    if hp == 0:
                        restart = True
                shot_group.update(False)
                melee_group.update()
                doors_group.update(doors_close)
                camera.update(player)
                scripts_group.update()
                rooms_group.update()
                particle_group.update()
                barriers_group.update()
                animated_sprites_group.update()
                enemy_group.update()
                bombs_group.update()
                chest_group.update(button)
                key_group.update()
                life_group.update(lifesaver)
                if inventory[3] is not None:
                    hatch_group.update(button, True)
                else:
                    hatch_group.update(button, False)
                ladder_group.update(button)
                for sprite in all_sprites:
                    camera.apply(sprite)

                tiles_group.draw(screen)
                barriers_group.draw(screen)
                animated_sprites_group.draw(screen)
                if doors_close:
                    doors_group.draw(screen)
                ladder_group.draw(screen)
                melee_group.draw(screen)
                chest_group.draw(screen)
                hatch_group.draw(screen)
                key_group.draw(screen)
                enemy_group.draw(screen)
                bombs_group.draw(screen)
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
                pygame.draw.rect(screen, pygame.Color((0, 0, 0)), (55 + 45 * hp, 0, 45 * (4 - hp),
                                                                   48), 0)
                health_group.draw(screen)
                life_group.draw(screen)
                all_cells_group.draw(screen)
                weapon_group.draw(screen)
                button = None
        else:
            if len(player_group) == 0:
                WeaponInInventory(load_image('empty_cell.png'), 2)
                transit = True
                ts = tile_width = tile_height = 64
                castle = Castle(level)
                player_x, player_y = castle.render()
                player = MiniPlayer(8, 2, player_x, player_y)
                player_v = 64
                pygame.mixer.music.load('music/castle.mp3')
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.3 * volume)
            moving = False
            x, y = 0, 0
            if restart:
                transit = True
                [sprite.kill() for sprite in all_sprites]
                castle = Castle(level)
                player_x, player_y = castle.render()
                player = MiniPlayer(8, 2, player_x, player_y)
                restart = False
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
                    elif event.key == pygame.K_ESCAPE:
                        [s.kill() for s in all_sprites]
                        dungeon_map = True
                        key_up = False
            if (x, y) != (0, 0):
                moving = True

            player.rect.x += x
            player.rect.y += y
            player.update(x, y, flip, False)
            slimes_group.update(x, y, flip)
            tables_group.update(x, y, flip)
            spikes_group.update()
            mini_keys_group.update()
            mini_doors_group.update()

            tiles_group.draw(screen)
            slimes_group.draw(screen)
            tables_group.draw(screen)
            mini_keys_group.draw(screen)
            mini_doors_group.draw(screen)
            player_group.draw(screen)
            spikes_group.draw(screen)
        if final:
            screen.fill('black')
            animated_sprites_group.update()
            animated_sprites_group.draw(screen)
        if transit:
            transition()
            transit_time += 1
            if transit_time == 20 and next_level is False:
                transit = False
                transit_time = 0
            if transit_time == 120 and next_level is True:
                level = 'castle_' + map_number + '.tmx'
                transit = False
                transit_time = 0
                next_level = False
                timer = [0, 0]
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()

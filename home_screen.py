import pygame
import os
import sys


pygame.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):  # обработка внешних изображений
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


def blit_pil_image(screen, img, position):
    pygame_image = pygame.image.fromstring(img.tobytes(), img.size, "RGB")
    screen.blit(pygame_image, position)


def terminate():  # off game
    pygame.quit()
    sys.exit()


def show_text(text, font, position):  # преобразование текста
    font_color = pygame.Color("orange")
    text = font.render(text, 1, font_color)  # передаём строку для экрана, затем сглаживание, цвет
    screen.blit(text, position)


def start_screen():  # начальный экран
    text = ['Dungeon quest', 'play', 'exit']
    fon = pygame.transform.scale(load_image("start_fon.png"), (600, 600))
    screen.blit(fon, (0, 0))
    coord_x = [70, 243, 250]
    coord_y = [80, 430, 500]
    fonts_size = [72, 58, 58]
    for elem in range(len(text)):
        font = [pygame.font.Font("fonts/Dirtchunk.otf", fonts_size[elem]),
            pygame.font.Font("fonts/jelani.otf", fonts_size[elem]),
            pygame.font.Font("fonts/jelani.otf", fonts_size[elem])]
        show_text(text[elem], font[elem], (coord_x[elem], coord_y[elem]))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 230 <= event.pos[0] <= 370 and 450 <= event.pos[1] <= 515:
                    screen_with_levels()
                if 230 <= event.pos[0] <= 370 and 516 <= event.pos[1] <= 581:
                    terminate()
        pygame.display.flip()
        clock.tick(50)


def screen_with_levels():
    screen.fill(pygame.Color("black"))
    fon = pygame.transform.scale(load_image("fon_lvl.png"), (600, 600))
    screen.blit(fon, (0, 0))
    images = ['fon1.png', 'analog_fon.png', 'dop_fon.png', 'fon3.png', 'fon2.png']
    for name in range(len(images)):
        img = pygame.transform.scale(load_image(images[name]), (80, 80))
        screen.blit(img, (40 + 110 * name, 25))
    text_level = ['1', '2', '3', '4', '5']
    for elem in range(len(text_level)):
        font = pygame.font.Font("fonts/DS VTCorona Cyr.ttf", 56)
        show_text(text_level[elem], font, (50 + 110 * elem, 30))
    font = pygame.font.Font("fonts/jelani.otf", 58)
    show_text('back', font, (15, 520))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 3 <= event.pos[0] <= 128 and 538 <= event.pos[1] <= 597:
                    home = True
                    start_screen()
                    return home
        pygame.display.flip()
        clock.tick(50)


if __name__ == '__main__':
    pygame.display.set_caption('Dungeon quest')
    clock = pygame.time.Clock()
    start_screen()
    home = True
    to_levels = False
    help = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(100)
        pygame.display.flip()
    pygame.quit()
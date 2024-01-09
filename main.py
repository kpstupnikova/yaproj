import os
import sys

import pygame

FPS = 50
pygame.init()
size = width, height = 700, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Передвигаться с помощью стрелок"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    pygame.display.flip()

    # Ожидание нажатия клавиши или кнопки мыши
    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_key = False

    # Закрываем заставку
    screen.fill((255, 255, 255))
    pygame.display.flip()

    # Возвращаем выбранный уровень после закрытия заставки
    return choose_level()


def choose_level():
    # Отображаем меню выбора уровня
    level_menu_text = ["Выберите уровень:",
                       "1. Уровень 1",
                       "2. Уровень 2",
                       "3. Уровень 3",
                       "4. Уровень 4",
                       "5. Уровень 5"]

    font = pygame.font.Font(None, 40)
    text_coord = 50

    selected_level = None
    for line in level_menu_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()

    while selected_level is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 10 < x < 200 and 100 < y < 130:
                    selected_level = 'map.txt'
                elif 10 < x < 200 and 145 < y < 175:
                    selected_level = 'map2.txt'
                elif 10 < x < 200 and 180 < y < 210:
                    selected_level = 'map3.txt'
                elif 10 < x < 200 and 220 < y < 240:
                    selected_level = 'map4.txt'
                elif 10 < x < 200 and 250 < y < 280:
                    selected_level = 'map5.txt'

    return selected_level


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return [list(i) for i in list(map(lambda x: x.ljust(max_width, '.'), level_map))]


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'tochka': load_image('tochka.jpg'),
    'yachik': load_image('yachik.jpg')
}
yachik = load_image('yachik.jpg')
player_image = load_image('kirby.jpg')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.pos = pos_x, pos_y
        self.rect = self.image.get_rect(
            center=(tile_width * pos_x + tile_width // 2, tile_height * pos_y + tile_height // 2))

    def move(self, x, y):
        self.pos = x, y
        self.rect.center = tile_width * x + tile_width // 2, tile_height * y + tile_height // 2


# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, level_x, level_y = None, len(level[0]), len(level)
    for y in range(level_y):
        for x in range(level_x):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '№':
                Tile('yachik', x, y)
            elif level[y][x] == 'T':
                Tile('tochka', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = '.'
    return new_player, level_x, level_y


def can_move(whom, where, level):
    x, y = whom.pos
    dx, dy = 0, 0
    if where == 'up':
        dy = -1
    elif where == 'down':
        dy = 1
    elif where == 'left':
        dx = -1
    elif where == 'right':
        dx = 1

    # Проверяем, находится ли перед нами ящик
    if 0 <= x + dx < level_x and 0 <= y + dy < level_y:
        object_in_front = level[y + dy][x + dx]

        # Определить, пустое ли место или "точка" находится за ящиком
        next_pos_is_empty_or_tochka = (
                0 <= x + 2 * dx < level_x and 0 <= y + 2 * dy < level_y and
                level[y + 2 * dy][x + 2 * dx] in ['.', 'T']
        )

        # Если перед нами ящик, и позади ящика пустое место или "точка",
        # тогда двигаем ящик
        if object_in_front == '№' and next_pos_is_empty_or_tochka:
            # Переместить ящик на следующую клетку
            level[y + dy][x + dx] = '.'
            level[y + 2 * dy][x + 2 * dx] = '№'
            whom.move(x + dx, y + dy)
            # Обновляем позиции ящика на карте уровня
            update_map(level)

        # Если перед нами пустая клетка, перемещаемся туда
        elif object_in_front == '.':
            whom.move(x + dx, y + dy)

        # Если перед нами "точка", перемещаемся туда
        elif object_in_front == 'T':
            whom.move(x + dx, y + dy)


def update_map(level):
    for y in range(level_y):
        for x in range(level_x):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '№':
                Tile('yachik', x, y)
            elif level[y][x] == 'T':
                Tile('tochka', x, y)


# Запуск игры после выбора уровня
selected_level = start_screen()
map_level = load_level(selected_level)
player, level_x, level_y = generate_level(map_level)

size = width, height = level_x * tile_width, level_y * tile_height
screen = pygame.display.set_mode(size)
running = True

movements_count = 0
start_ticks = pygame.time.get_ticks()  # начальное время для таймера
while running:
    screen.fill((0, 0, 0))  # Очищаем экран
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                if event.key == pygame.K_UP:
                    can_move(player, 'up', map_level)
                    movements_count += 1
                elif event.key == pygame.K_DOWN:
                    can_move(player, 'down', map_level)
                    movements_count += 1
                elif event.key == pygame.K_LEFT:
                    can_move(player, 'left', map_level)
                    movements_count += 1
                elif event.key == pygame.K_RIGHT:
                    can_move(player, 'right', map_level)
                    movements_count += 1

    all_sprites.update()  # Обновляем все спрайты
    tiles_group.draw(screen)  # Отображаем только группу спрайтов с тайлами
    player_group.draw(screen)  # Отображаем только группу спрайтов с персонажем

    font = pygame.font.Font(None, 30)
    # Отображение таймера
    seconds = (pygame.time.get_ticks() - start_ticks) // 1000  # Преобразование миллисекунд в секунды
    timer_text = font.render(f"Время: {seconds}", True, pygame.Color('white'))
    timer_rect = timer_text.get_rect()
    timer_rect.topleft = (10, 10)
    screen.blit(timer_text, timer_rect)

    # Обновите счетчик шагов
    movements_text = font.render(f"Количество нажатий: {movements_count}", True, pygame.Color('white'))
    movements_rect = movements_text.get_rect()
    movements_rect.topleft = (10, 50)
    screen.blit(movements_text, movements_rect)
    pygame.display.flip()
    clock.tick(FPS)  # гугл лучше

pygame.quit()
sys.exit()

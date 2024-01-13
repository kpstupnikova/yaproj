import os
import random
import sys

import pygame

# Инициализация основных объектов pygame
pygame.init()
FPS = 20
size = width, height = 700, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.display.set_caption("Сокобан")

# Глобальные переменные
frame_index = 0
boxes_positions = {}
tile_width = tile_height = 50
# основной персонаж
player = None
# Инициализация групп спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
ball_group = pygame.sprite.Group()  # Группа для шариков
bg = pygame.sprite.Group()
pygame.init()
# Загрузка изображений для анимации
image1 = pygame.image.load('image1.png')
image2 = pygame.image.load('image2.png')
image3 = pygame.image.load('image3.png')
image4 = pygame.image.load('image4.png')
image5 = pygame.image.load('image5.png')

image6 = pygame.image.load('image6.png')
image7 = pygame.image.load('image7.png')
image8 = pygame.image.load('image8.png')
image9 = pygame.image.load('image9.png')
image10 = pygame.image.load('image10.png')

# Цикл обработки каждого изображения
animation_images = []
for image in [image1, image2, image3, image4, image5, image6, image7, image8, image9, image10]:
    # Применение метода удаления фона
    processed_image = image.convert_alpha()
    processed_image.set_colorkey((255, 255, 255))
    animation_images.append(processed_image)


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


tile_images = {
    'wall': load_image('box.jpg'),
    'empty': load_image('grass.jpg'),
    'tochka': load_image('tochka.jpg'),
    'yachik': load_image('yachik.jpg')
}
tochka = load_image('tochka.jpg')
yachik = load_image('yachik.jpg')


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.animation_images = animation_images
        self.image_index = 0
        self.image = self.animation_images[self.image_index]
        self.pos = pos_x, pos_y
        self.rect = self.image.get_rect(
            center=(tile_width * pos_x + tile_width // 2, tile_height * pos_y + tile_height // 2))

    def update(self, *args):
        # Обновление анимации
        self.image = self.animation_images[self.image_index]
        self.image_index = (self.image_index + 1) % len(animation_images)
        # Перемещение персонажа
        self.rect.topleft = self.pos[0] * tile_width, self.pos[1] * tile_height

    def move(self, x, y):
        self.pos = x, y
        self.rect.center = tile_width * x + tile_width // 2, tile_height * y + tile_height // 2


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius):
        super().__init__(all_sprites, bg)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("pink"),
                           (radius, radius), radius)
        x = random.randint(0, width)
        y = random.randint(0, height)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        while len(pygame.sprite.spritecollide(self, all_sprites, False)) > 1:
            x = random.randint(0, width)
            y = random.randint(0, height)
            self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vx = random.randint(0, 5)
        self.vy = random.randrange(0, 5)

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        ball_col = pygame.sprite.spritecollide(self, bg, False)
        if len(ball_col) > 1:
            for b in ball_col:
                b.vx = -b.vx
                b.vy = -b.vy


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


for i in range(4):
    ball = Ball(20)
    ball_group.add(ball)  # Добавляем созданный шар в ball_group


def terminate():
    pygame.quit()
    sys.exit()


def check_win_condition(level):
    for y in range(level_y):
        for x in range(level_x):
            # Если на месте точки нет ящика, то условие победы не выполнено
            if level[y][x] == 'T' and (x, y) not in boxes_positions:
                return False  # Условие победы не выполнено
    return True  # Все ящики на своих местах


def write_time_to_file(seconds):
    try:
        with open("times.txt", "a", encoding='utf-8') as file:
            # Записываем время, за которое игрок прошел игру, в файл с новой строки
            file.write(f"{seconds}\n")
    except IOError as e:
        print(f"Ошибка записи файла: {e}")
        sys.exit()


# функция для отображения финального экрана победы
def show_victory_screen(seconds):
    write_time_to_file(seconds)  # Записываем время прохождения в файл

    fon = pygame.transform.scale(load_image('pobeda.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 100)
    victory_text = font.render("Победа", True, pygame.Color('black'))
    text_rect = victory_text.get_rect(center=(width // 2, height // 2))
    screen.blit(victory_text, text_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Передвигаться с помощью стрелок",
                  'Задвинуть все тортики в фиолетовые квадратики']

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
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


def show_loss_screen():
    fon = pygame.transform.scale(load_image('proigrysh.jpg'), (width, height))  # Замените на ваше изображение проигрыша
    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 100)  # Устанавливаем размер шрифта
    loss_text = font.render("Проигрыш", True, pygame.Color('white'))  # Текст с черным цветом
    text_rect = loss_text.get_rect(center=(width // 2, height // 2))  # Располагаем текст по центру экрана

    screen.blit(loss_text, text_rect)  # Отображаем текст на экране

    pygame.display.flip()  # Обновляем экран, чтобы отобразить финальную заставку проигрыша

    # Ожидание выхода после проигрыша
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Выход по нажатию Escape
                    terminate()


def get_best_time():
    try:
        with open("times.txt", "r", encoding='utf-8') as file:
            times = file.readlines()
            # Преобразуем строки в числа и фильтруем пустые строки
            times = [int(time.strip()) for time in times if time.strip().isdigit()]
            if times:  # Если в списке есть элементы
                return min(times)
            else:
                return None
    except IOError as e:
        print(f"Ошибка чтения файла: {e}")
        return None


def choose_level():
    best_time = get_best_time()  # Получаем лучшее время

    # Отображаем меню выбора уровня
    level_menu_text = ['Выберите уровень',
                       "1. Уровень 1",
                       "2. Уровень 2",
                       "3. Уровень 3",
                       "4. Уровень 4",
                       "5. Уровень 5"
                       ]

    fon = pygame.transform.scale(load_image('menu.jpg'), (width, height))
    font = pygame.font.Font(None, 40)
    text_coord = 50
    screen.blit(fon, (0, 0))
    selected_level = None
    for line in level_menu_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    # Отображение лучшего времени

    best_time_text = font.render(f"Лучший результат: {best_time}", True, pygame.Color('black'))
    best_time_rect = best_time_text.get_rect()
    best_time_rect.topright = (width - 10, 10)
    screen.blit(best_time_text, best_time_rect)

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


def generate_level(level):
    Border(5, 5, width - 5, 5)
    Border(5, height - 5, width - 5, height - 5)
    Border(5, 5, 5, height - 5)
    Border(width - 5, 5, width - 5, height - 5)
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

    if 0 <= x + dx < level_x and 0 <= y + dy < level_y:
        object_in_front = level[y + dy][x + dx]
        next_pos_is_empty_or_tochka = (
                0 <= x + 2 * dx < level_x and 0 <= y + 2 * dy < level_y and level[y + 2 * dy][x + 2 * dx] in ['.',
                                                                                                              'T'])

        if object_in_front == '№' and next_pos_is_empty_or_tochka:  # если перед игроком стоит ящик
            # проверяем, можно ли двигать ящик
            if collide(x + dx, y + dy, level):
                level[y + dy][x + dx] = '.'
                level[y + 2 * dy][x + 2 * dx] = '№'
                boxes_positions[(x + 2 * dx, y + 2 * dy)] = True

            if (x + dx, y + dy) in boxes_positions:
                del boxes_positions[(x + dx, y + dy)]

            whom.move(x + dx, y + dy)
            update_map(level)

            # Проверка условий победы
            if check_win_condition(map_level):
                seconds = (pygame.time.get_ticks() - start_ticks) // 1000
                show_victory_screen(seconds)  # Передаем время функции
                running = False

        elif object_in_front == '.':
            whom.move(x + dx, y + dy)

        elif object_in_front == 'T':
            whom.move(x + dx, y + dy)


# функция проверки столкновения с ящиком
def collide(x, y, level):
    if level[y][x] == '№':  # если в указанных координатах есть ящик
        return True
    else:
        return False


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
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT \
                    or event.key == pygame.K_RIGHT:
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
    ball_group.draw(screen)  # Рисуем шарики последними, чтобы они были наверху
    ball_group.update()  # Обновляем шарики

    # Проверка столкновения шарика и персонажа
    if pygame.sprite.spritecollideany(player, ball_group):  # Проверяем столкновение персонажа с любым шаром
        show_loss_screen()  # Показываем экран проигрыша вместо простого вывода сообщения
        running = False  # Прекращаем игровой цикл

    font = pygame.font.Font(None, 30)

    # Отображение таймера
    seconds = (pygame.time.get_ticks() - start_ticks) // 1000  # Преобразование миллисекунд в секунды
    timer_text = font.render(f"Время: {seconds}", True, pygame.Color('black'))
    timer_rect = timer_text.get_rect()
    timer_rect.topleft = (10, 10)
    screen.blit(timer_text, timer_rect)

    # Обновление счетчик шагов
    movements_text = font.render(f"Количество нажатий: {movements_count}", True, pygame.Color('black'))
    movements_rect = movements_text.get_rect()
    movements_rect.topleft = (10, 50)
    screen.blit(movements_text, movements_rect)
    pygame.display.flip()
    clock.tick(FPS)

    if not running:
        break  # Если running стал False, выходим из игрового цикла

pygame.quit()
sys.exit()

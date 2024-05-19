import pygame
import psutil
import os
import subprocess
import webbrowser
import time

# Инициализация Pygame
pygame.init()

# Задаем начальные размеры окна
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Task Manager")

# Определяем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (150, 150, 150)

# Установка шрифта
font = pygame.font.SysFont(None, 24)
header_font = pygame.font.SysFont(None, 28)

# Определение цветов
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Функция для определения цвета в зависимости от загрузки CPU
def get_cpu_color(cpu_percent):
    if cpu_percent < 30:
        return GREEN  # Маленькая загрузка
    elif cpu_percent < 70:
        return YELLOW  # Средняя загрузка
    else:
        return RED  # Большая загрузка

# Получение списка процессов
processes = []
for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
    try:
        processes.append((p.info['pid'], p.info['name'], p.info['cpu_percent']))
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

# Отображение процессов с соответствующим цветом
for process in processes:
    pid, name, cpu_percent = process
    color = get_cpu_color(cpu_percent)
    # Отобразить процесс с цветом
    # draw_process(pid, name, cpu_percent, color)

# Функция для отображения текста
def draw_text(surface, text, x, y, color=BLACK, font=font):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

# Функция для получения списка процессов
def get_processes():
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_percent']):
        try:
            processes.append((p.info['pid'], p.info['name'], p.info['exe'] or 'N/A', p.info['cpu_percent'], p.info['memory_percent']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

# Основные переменные
processes = get_processes()
start_index = 0
selected_index = None
process_height = 30
menu_open = False
menu_options = ["Terminate", "Suspend", "Open File Location", "More Info"]
selected_option = 0
last_update_time = time.time()
fullscreen = False
resolutions = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
current_resolution = 0

# Основной цикл программы
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            elif event.key == pygame.K_F12:
                current_resolution = (current_resolution + 1) % len(resolutions)
                screen_width, screen_height = resolutions[current_resolution]
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            if not menu_open:
                if event.key == pygame.K_DOWN:
                    if selected_index is None:
                        selected_index = start_index
                    elif selected_index < len(processes) - 1:
                        selected_index += 1
                        if selected_index >= start_index + (screen_height // process_height) - 2:
                            start_index += 1
                elif event.key == pygame.K_UP:
                    if selected_index is None:
                        selected_index = start_index
                    elif selected_index > start_index:
                        selected_index -= 1
                        if selected_index < start_index:
                            start_index -= 1
                elif event.key == pygame.K_PAGEDOWN:
                    if start_index + (screen_height // process_height) < len(processes):
                        start_index += 1
                elif event.key == pygame.K_PAGEUP:
                    if start_index > 0:
                        start_index -= 1
            else:
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_RETURN and selected_index is not None:
                    pid, name, exe, cpu, memory = processes[selected_index]
                    if menu_options[selected_option] == "Terminate":
                        try:
                            psutil.Process(pid).terminate()
                        except psutil.NoSuchProcess:
                            pass
                    elif menu_options[selected_option] == "Suspend":
                        try:
                            psutil.Process(pid).suspend()
                        except psutil.NoSuchProcess:
                            pass
                    elif menu_options[selected_option] == "Open File Location":
                        if exe != 'N/A':
                            if os.name == 'nt':  # Windows
                                subprocess.run(['explorer', '/select,', exe])
                            elif os.name == 'posix':  # macOS, Linux
                                subprocess.run(['xdg-open', os.path.dirname(exe)])
                    elif menu_options[selected_option] == "More Info":
                        webbrowser.open(f"https://www.google.com/search?q={name}")
                    menu_open = False
                    selected_option = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not menu_open:  # ЛКМ
                x, y = event.pos
                if y > 80:
                    index = start_index + (y - 80) // process_height
                    if index < len(processes):
                        selected_index = index
                        menu_open = True
            elif event.button == 1 and menu_open:  # ЛКМ в меню
                menu_open = False
            elif event.button == 3 and not menu_open:  # ПКМ
                x, y = event.pos
                if y > 80:
                    index = start_index + (y - 80) // process_height
                    if index < len(processes):
                        selected_index = index
                        menu_open = True
            elif event.button == 4:  # Прокрутка вверх
                if start_index > 0:
                    start_index -= 1
            elif event.button == 5:  # Прокрутка вниз
                if start_index + (screen_height // process_height) < len(processes):
                    start_index += 1
        elif event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.size
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    # Обновление списка процессов каждые 2 секунды
    current_time = time.time()
    if current_time - last_update_time >= 2:
        processes = get_processes()
        last_update_time = current_time

    # Заполнение экрана белым цветом
    screen.fill(WHITE)

    # Отображение заголовка
    draw_text(screen, "Task Manager (F11 for fullscreen, F12 to change resolution, arrow keys to navigate, right-click to open menu, mouse wheel to scroll)", 20, 20)

    # Отображение заголовков столбцов
    headers = ["PID", "Name", "CPU (%)", "Memory (%)", "Path"]
    header_x_positions = [20, 100, 400, 500, 600]
    for i, header in enumerate(headers):
        draw_text(screen, header, header_x_positions[i], 50, BLACK, header_font)

    # Отображение разделительной линии под заголовками
    pygame.draw.line(screen, DARK_GRAY, (0, 75), (screen_width, 75), 2)

    # Отображение списка процессов
    y_offset = 80
    for i in range(start_index, len(processes)):
        if y_offset > screen_height - process_height:
            break
        pid, name, exe, cpu, memory = processes[i]
        process_info = [str(pid), name, f"{cpu:.1f}", f"{memory:.1f}", exe]
        color = RED if i == selected_index else BLACK
        for j, info in enumerate(process_info):
            draw_text(screen, info, header_x_positions[j], y_offset, color)
        y_offset += process_height

    # Отображение контекстного меню
    if menu_open and selected_index is not None:
        menu_x = 300
        menu_y = 100
        pygame.draw.rect(screen, GRAY, (menu_x, menu_y, 200, 180))
        for i, option in enumerate(menu_options):
            color = BLUE if i == selected_option else BLACK
            draw_text(screen, option, menu_x + 10, menu_y + 10 + i * 30, color)

    # Обновление экрана
    pygame.display.update()

# Завершение работы Pygame
pygame.quit()

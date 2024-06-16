import pygame as p
import random
import numpy as np
import threading
from pygame.locals import *
from sys import exit
import time


start_time_2 = time.time()
# Константы цветов RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 170, 0)
RED = (255, 0, 0)
cell_size = 10
#ROOLS = [[[2,3],[3]], [[2,3,4],[3]], [[2],[2,3,4]]]
ROOLS = []
system=[[-1, 0], [1, 0], [0, 1], [0, -1], [0, 0]]
option = 0
root = None
is_game_started = False
mutex = threading.Lock()


def starting_rules():
    global ROOLS
    try:
        try:
            birth = list(map(int, input("Enter birth number cells separated by space:").split()))
            alive = list(map(int, input("Enter alive number cells separated by space:").split()))
            ROOLS.append([birth, alive])
            set_display()
        except ValueError:
            print("Excepted integer number!")
            starting_rules()
    except ValueError:
        print("Excepted integer number!")
        starting_rules()

def set_display():
    global root
    root = p.display.set_mode((500, 500))
    set_size_of_cells()

def set_size_of_cells():
    global cell_size
    cell_size = 5
    print("Draw with your mouse (left button - draw, right - erase) and press S to start, for restart press R")

args = []
number_of_process = 1


def set_args():
    global args, number_of_process
    print("Options: \n1 - 1 process\n2 - 2 process\n4 - 4 process")
    arguments_4 = [[0, width//2, 0, height//2], [width//2, width, height//2, height], [width//2, width, 0 , height//2], [0, width//2, height//2, height]]
    arguments_2 = [[0, width//2, 0, height], [width//2, width, 0, height]]
    arguments_1 = [[0, width, 0, height]]
    arguments_16 = [[0, width // 4, 0, height // 4], [width // 4, width // 2, 0, height // 4], [width // 2, 3 * width // 4, 0, height // 4], [3 * width // 4, width, 0, height // 4],
                    [0, width // 4, height // 4, height // 2], [width // 4, width // 2, height // 4, height // 2], [width // 2, 3 * width // 4, height // 4, height // 2], [3 * width // 4, width, height // 4, height // 2],
                    [0, width // 4, height // 2, 3 * height // 4], [width // 4, width // 2, height // 2, 3 * height // 4], [width // 2, 3 * width // 4, height // 2, 3 * height // 4], [3 * width // 4, width, height // 2, 3 * height // 4],
                    [0, width // 4, 3 * height // 4, height], [width // 4, width // 2, 3 * height // 4, height], [width // 2, 3 * width // 4, 3 * height // 4, height], [3 * width // 4, width, 3 * height // 4, height]
                    ]
    option = int(input("Enter mode:"))
    if option == 1:
        number_of_process = 1
        args = arguments_1
    elif option == 2:
        number_of_process = 2
        args = arguments_2
    elif option == 4:
        number_of_process = 4
        args = arguments_4


starting_rules()
width = root.get_width() // cell_size
height = root.get_height() // cell_size
cells = [[random.choice([0,1]) for j in range(width)] for i in range(height)]
#cells = [[0 for j in range(height)] for i in range(width)]
#cells[width//2] = [1 for j in range(height)]
cells_next = [[0 for j in range(height)] for i in range(width)]

# Функция определения кол-ва соседей
def near(pos: list, system=[[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1], [0, 0]]):
    count = 0
    for i in system:
        if cells[(pos[0] + i[0]) % width][(pos[1] + i[1]) % height]:
            count += 1
    return count


'''def draw_field(w_x, w_x2, h_y, h_y2):
    global root, cells, cells_next, ROOLS
    for i in range(w_x, w_x2):
        for j in range(h_y, h_y2):
            p.draw.rect(root, BLACK if cells[i][j] == 1 else WHITE, [i * cell_size, j * cell_size, cell_size, cell_size])
    for i in range(w_x, w_x2):
        for j in range(h_y, h_y2):
            if cells[i][j]:
                if near([i, j], system) not in ROOLS[0][1]:
                    cells_next[i][j] = 0
                else:
                    cells_next[i][j] = 1
            elif near([i, j], system) in ROOLS[0][0]:
                cells_next[i][j] = 1
            else:
                cells_next[i][j] = 0'''


def draw_field(w_x, w_x2, h_y, h_y2):
    global root, cells, cells_next, ROOLS
    for i in range(w_x, w_x2):
        for j in range(h_y, h_y2):
            p.draw.rect(root, BLACK if cells[i][j] == 1 else WHITE, [i * cell_size, j * cell_size, cell_size, cell_size])
    for i in range(w_x, w_x2):
        for j in range(h_y, h_y2):
            if near([i, j], system) % 2 == 0:
                cells_next[i][j] = 1
            elif near([i, j], system) % 2 == 1:
                cells_next[i][j] = 0

'''def draw_field(w_x, w_x2, h_y, h_y2):
    global root, cells, cells_next, ROOLS
    opt = 0
    for i in range(w_x, w_x2):
        for j in range(h_y, h_y2):
            p.draw.rect(root, RED if cells[i][j] == 1 else BLACK, [i * cell_size, j * cell_size, cell_size, cell_size])
    for i in range(w_x, w_x2):
        for j in range(h_y, h_y2):
            cells_next[i][j] = random.choice([0, 1])'''


def run_threads(count, args):
    global cells, cells_next
    cells_next = [[0 for j in range(height)] for i in range(width)]
    threads = [
        threading.Thread(target=draw_field, args=(args[i][0], args[i][1], args[i][2], args[i][3],))
        for i in range(0, count)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    cells = cells_next

def make_number():
    global cells
    res = ""
    for i in range(height):
        for j in range(width):
            res += str(cells[j][width - 1 - i])
    f = open("num_res.txt", "a")
    f.write(str(int(res, 2)) + "\n")
    f.close()


def get_file(name):
    global cells
    f = open("list.txt", "a")
    f.write(name+"\n")
    f.close()
    f = open(name, "w")
    for i in range(height):
        for j in range(width):
            f.write(str(cells[j][width - 1 - i]))
    f.close()

def write_in_file(counter, take):
    if counter == 20:
        get_file("data/20_" + str(take) + ".txt")
    if counter == 40:
        get_file("data/40_" + str(take) + ".txt")
    if counter == 60:
        get_file("data/60_" + str(take) + ".txt")
    if counter == 80:
        get_file("data/80_" + str(take) + ".txt")
    if counter == 100:
        get_file("data/100_" + str(take) + ".txt")
    if counter == 120:
        get_file("data/120_" + str(take) + ".txt")
    if counter == 140:
        get_file("data/140_" + str(take) + ".txt")
    if counter == 160:
        get_file("data/160_" + str(take) + ".txt")
    if counter == 180:
        get_file("data/180_" + str(take) + ".txt")
    if counter == 200:
        get_file("data/200_" + str(take) + ".txt")
        end_time_2 = time.time()
        execution_time_2 = end_time_2 - start_time_2
        take += 1
        counter = 0
        cells = [[random.choice([0, 1]) for j in range(width)] for i in range(height)]
        print(f"Время выполнения программы: {execution_time_2} секунд")


#FPS = p.time.Clock()
p.event.set_allowed([p.QUIT, p.KEYDOWN, p.K_s, p.K_r])
counter = 0
take = 0
while 1:
    #FPS.tick(60)
    for i in p.event.get():
        if i.type == QUIT:
            exit()
        if i.type == p.KEYDOWN:
            if i.key == p.K_s:
                is_game_started = True
            if i.key == p.K_r:
                is_game_started = False
                starting_rules()
            if i.key == p.K_c:
                cells = [[0 for j in range(width)] for i in range(height)]
            if i.key == p.K_F1:
                word = "_B" + "".join(map(str, ROOLS[0][0])) + "_S" + "".join(map(str, ROOLS[0][1]))
                p.image.save(root, "screenshot_Murr"+word+"_"+str(take)+".jpg")
                take += 1

    #отрисовка сетки
    #for i in range(0, root.get_height()):
        #p.draw.line(root, WHITE, (0, i * cell_size), (root.get_width(), i * cell_size))
    #for j in range(0, root.get_width()):
        #p.draw.line(root, WHITE, (j * cell_size, 0), (j * cell_size, root.get_height()))
    # Обновляем экран
    p.display.update()
    #write_in_file(counter, take)
    if is_game_started:
        counter += 1
        cells_next = [[0 for j in range(height)] for i in range(width)]
        draw_field(0, width, 0, height)
        cells = cells_next
        #run_threads(number_of_process, args)
        write_in_file(counter, 0)
        make_number()
    else:
        pressed = p.mouse.get_pressed()
        pos = p.mouse.get_pos()
        if pressed[0] and 0 <= pos[0] // cell_size < width and 0 <= pos[1] // cell_size < height:
            cells[pos[0]//cell_size][pos[1]//cell_size] = 1
        if pressed[2] and 0 <= pos[0] // cell_size < width and 0 <= pos[1] // cell_size < height:
            cells[pos[0]//cell_size][pos[1]//cell_size] = 0
        for i in range(0, width):
            for j in range(0, height):
                p.draw.rect(root, BLACK if cells[i][j] == 1 else WHITE,
                            [i * cell_size, j * cell_size, cell_size, cell_size])

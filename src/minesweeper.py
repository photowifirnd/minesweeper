from graphics import Canvas
import random
import math
import time
import os

# Difficult Level
LEVELS = {
    'Easy': (8, 0.20),
    'Medium': (12, 0.22),
    'Hard': (16, 0.30)
}
# Configuraciñones de la cuadrícula
FOOTER_SIZE = 50
CELL_SIZE = 50
#Time Limits
TIME = 0.000001
#Text properties
text_sz = 30
def main():
    global GRID_SIZE, WIDTH, HEIGHT, MINES
    GRID_SIZE = 8
    CELL_SIZE = 50
    WIDTH = GRID_SIZE * CELL_SIZE
    HEIGHT = GRID_SIZE * CELL_SIZE + FOOTER_SIZE
    MINES = int(GRID_SIZE * GRID_SIZE * (20 / 100))
    canvas = Canvas(400, 400)
    grid_size, mine_ratio = pick_your_level(canvas)
    width = grid_size * CELL_SIZE
    height = grid_size * CELL_SIZE + FOOTER_SIZE
    mines = int(grid_size * grid_size * mine_ratio)
    GRID_SIZE = grid_size
    WIDTH = width
    HEIGHT = height
    MINES = mines
    aux_width = WIDTH - 40
    aux_height = GRID_SIZE * CELL_SIZE + 25
    canvas = Canvas(width, height)
    timer_display = canvas.create_text(aux_width, aux_height, text='000s', font='Courier', font_size=20, color='red', anchor='center')
    mine_display = canvas.create_text(40, aux_height, text=str(MINES), font='Courier', font_size=20, color='blue', anchor='center')

    board_field = []
    discovered = []
    flags = []
    discovered_cells = 0
    start_time = None
    timer_id = None
    count_flags = 0
    init_game(canvas, board_field, discovered, flags)
    redraw(canvas, discovered, board_field)
    
    continue_game = True
    win_game = False
    is_shift_pressed = False
    
    
    while continue_game:
        key_press = canvas.get_last_key_press()
        click = canvas.get_last_click()
        if key_press == 'Shift':
            is_shift_pressed = True
        if click is not None:
            if start_time is None:
                start_time = time.time()
            x, y = click
            row = int(y / CELL_SIZE)
            col = int(x / CELL_SIZE)
            if is_shift_pressed:
                draw_flag(canvas, flags, discovered, row, col)
                count_flags = sum(cell is not None for row in flags for cell in row)
                update_mine_display(canvas, mine_display, count_flags)
                is_shift_pressed = False
            else:
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if board_field[row][col] == 'M':
                        continue_game = False
                        win_game = False
                        break
                    elif not discovered[row][col] and flags[row][col] == None:
                        if board_field[row][col] == 0:
                            reveal_empty_cells(canvas, board_field, discovered, flags, row, col)
                        else:
                            discovered[row][col] = True
                            draw_cell(canvas, row, col, board_field, discovered)
                        discovered_cells = sum(sum_row.count(True) for sum_row in discovered)
                        if discovered_cells == GRID_SIZE * GRID_SIZE - MINES:
                            win_game = True
                            continue_game = False
        if start_time is not None:
            update_timer(canvas, start_time, timer_display)
    final_redraw(canvas, board_field, win_game)
def pick_your_level(canvas):
    canvas.create_text(WIDTH // 2, 60, text="Pick your level", font='Courier', font_size=text_sz, color='black', anchor='center')
    y=160
    buttons = {}
    for level, (size, ratio) in LEVELS.items():
        rect_id = canvas.create_rectangle(WIDTH // 2 - 100, y, WIDTH // 2 + 100, y + 40, color='lightgray', outline='black')
        text_id = canvas.create_text(WIDTH // 2, y + 20, text=level, font='Arial', font_size=18, anchor='center')
        buttons[level] = (rect_id, text_id, y, y + 40)
        y += 60
    while True:
        click = canvas.get_last_click()
        if click is not None:
            x, y = click
            for level, (_, _, top, bottom) in buttons.items():
                if WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100 and top <= y <= bottom:
                    canvas.clear()  # limpia la pantalla antes de crear el juego
                    return LEVELS[level]

def reveal_empty_cells(canvas, board_field, discovered, flags, row, col):
    stack = [(row, col)]
    while stack:
        current_row, current_col = stack.pop()
        if 0 <= current_row < GRID_SIZE and 0 <= current_col < GRID_SIZE and not discovered[current_row][current_col] and flags[current_row][current_col] == None:
            discovered[current_row][current_col] = True
            draw_cell(canvas, current_row,current_col, board_field, discovered)
            if board_field[current_row][current_col] == 0:
                for delta_row in [-1, 0, 1]:
                    for delta_col in [-1, 0, 1]:
                        if delta_row != 0 or delta_col != 0:
                            new_row = current_row + delta_row
                            new_col = current_col + delta_col
                            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE and not discovered[new_row][new_col]:
                                if board_field[new_row][new_col] != 'M':
                                    stack.append((new_row, new_col))

def count_adjacent_mines(row, col, board_field):
    """
    Cuenta cuántas minas hay en las celdas adyacentes a la posición (row, col).
    Las celdas adyacentes incluyen: arriba, abajo, izquierda, derecha y diagonales.
    """
    count = 0  # Contador de minas

    # Recorrer filas desde la anterior hasta la siguiente (row - 1, row, row + 1)
    for i in range(row - 1, row + 2):
        # Recorrer columnas desde la anterior hasta la siguiente (col - 1, col, col + 1)
        for j in range(col - 1, col + 2):
            # Verificar que no nos salimos de los límites del tablero
            if i >= 0 and i < GRID_SIZE and j >= 0 and j < GRID_SIZE:
                # Excluir la celda central (la actual)
                if i == row and j == col:
                    continue
                # Si en esa celda hay una mina, aumentamos el contador
                if board_field[i][j] == 'M':
                    count += 1
    return count

def init_game(canvas, board_field, discovered, flags):
    for i in range(GRID_SIZE):
        row = []
        row_discovered = []
        row_flags = []
        for k in range(GRID_SIZE):
            row.append(' ')
            row_discovered.append(False)
            row_flags.append(None)
        board_field.append(row)
        discovered.append(row_discovered)
        flags.append(row_flags)
    put_mines_in_board_field(board_field)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if (board_field[row][col] != 'M'):
                board_field[row][col] = count_adjacent_mines(row, col, board_field)

def reveal_all_mines(canvas, board_field):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board_field[row][col] == 'M':
                draw_mine(canvas, row, col)

def final_redraw(canvas, board_field, win_game):
    for row in range(GRID_SIZE):
        time.sleep(float(TIME))
        for col in range(GRID_SIZE):
            value = board_field[row][col]
            left_x = col * CELL_SIZE
            top_y = row * CELL_SIZE
            right_x = left_x + CELL_SIZE
            bottom_y = top_y + CELL_SIZE
            #time.sleep(float(TIME))
            canvas.create_rectangle(left_x, top_y, right_x, bottom_y, color='white', outline='black')
            if str(value) != 'M' and value > 0:
                if value == 1:
                    color = 'blue'
                elif value == 2:
                    color = 'green'
                else:
                    color = 'red'
                pos_x = col * CELL_SIZE + CELL_SIZE / 2
                pos_y = row * CELL_SIZE + CELL_SIZE / 2
                canvas.create_text(pos_x, pos_y, text=str(value), font='Arial', anchor='center', font_size=text_sz, color=color)
    reveal_all_mines(canvas, board_field)
    finish_game(canvas, win_game)
def finish_game(canvas, won):
    text="💥BOOM!!! You Lose."
    color = "red"
    if won:
        text="🏆 You Win!!"
        color='green'
    canvas.create_text(
        canvas.get_width() // 2,
        canvas.get_height() - 25,
        text=text,
        font='Courier',
        font_size=20,
        color=color,
        anchor='center'
    )

def put_mines_in_board_field(board_field):
    mines_in_board = 0
    while mines_in_board < MINES:
        row = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)
        if board_field[row][col] != 'M':
            board_field[row][col] = 'M'
            mines_in_board += 1
# Timer control: Updates the time in seconds
def update_timer(canvas, start_time, timer_display):
    elapsed_time = int(time.time() - start_time)
    canvas.change_text(timer_display, f'{elapsed_time:03d}s')
    return elapsed_time
def update_mine_display(canvas, mine_display, count_flags):
    remain = MINES - count_flags
    canvas.change_text(mine_display, f'{remain:02d}')
# Create a function to only reveal the cell that user click on. So we can improve the execution
def draw_cell(canvas, row, col, board_field, discovered):
    left_x = col * CELL_SIZE
    top_y = row * CELL_SIZE
    right_x = left_x + CELL_SIZE
    bottom_y = top_y + CELL_SIZE
    value = board_field[row][col]
    color = 'white' 
    if not discovered[row][col]:
        color = 'lightgrey'
    if MINES < int(CELL_SIZE * CELL_SIZE * (20 / 100)):
        time.sleep(float(TIME))
    canvas.create_rectangle(left_x, top_y, right_x, bottom_y, color=color, outline='black')
    if discovered[row][col] and str(value) != 'M' and value > 0:
        if value == 1:
            color = 'blue'
        elif value == 2:
            color = 'green'
        else:
            color = 'red'
        pos_x = col * CELL_SIZE + CELL_SIZE / 2
        pos_y = row * CELL_SIZE + CELL_SIZE / 2
        canvas.create_text(pos_x, pos_y, text=str(value), font='Arial', anchor='center', font_size=text_sz, color=color)
    
    #canvas.create_rectangle(left_x, top_y, right_x, bottom_y, color=color, outline='black')
def redraw(canvas, discovered, board_field):
    for row in range(GRID_SIZE):
        time.sleep(float(TIME))
        for col in range(GRID_SIZE):
            draw_cell(canvas, row, col, board_field, discovered)
def draw_flag(canvas, flags, discovered, row, col):
    #print(f"Flag on ({row}, {col}) -> discovered[{row}][{col}] -> {discovered[row][col]}")
    count_flags = sum(cell is not None for row in flags for cell in row)
    #if count_flags >= MINES:
        #return
    if not discovered[row][col]:
        if flags[row][col] is not None:
            left_x = col * CELL_SIZE
            top_y = row * CELL_SIZE
            right_x = left_x + CELL_SIZE
            bottom_y = top_y + CELL_SIZE
            canvas.delete(flags[row][col])
            canvas.create_rectangle(left_x, top_y, right_x, bottom_y, color='lightgrey', outline='black')
            flags[row][col] = None
        elif  count_flags < MINES:
            filename = 'flag.png'
            if not os.path.exists(filename):
                pos_x = col * CELL_SIZE + CELL_SIZE / 2
                pos_y = row * CELL_SIZE + CELL_SIZE / 2
                obj_id = canvas.create_text(pos_x, pos_y, text='🚩', anchor='center', font_size=text_sz)
                
            else:
                pos_x = col * CELL_SIZE
                pos_y = row * CELL_SIZE
                obj_id = canvas.create_image_with_size(pos_x, pos_y, CELL_SIZE, CELL_SIZE, filename)
            flags[row][col] = obj_id
def draw_mine(canvas, row, col):
    filename = 'mine.png'
    if not os.path.exists(filename):
        center_x = col * CELL_SIZE + CELL_SIZE / 2
        center_y = row * CELL_SIZE + CELL_SIZE / 2
        canvas.create_text(center_x, center_y, text='💣', anchor='center', font_size=text_sz)
    else:
        pos_x = col * CELL_SIZE
        pos_y = row * CELL_SIZE
        image = canvas.create_image_with_size(pos_x, pos_y,CELL_SIZE, CELL_SIZE, filename)
    time.sleep(float(TIME))

if __name__ == '__main__':
    main()
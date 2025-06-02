from graphics import Canvas
import random
import math
    
# Configuraciñones de la cuadrícula
GRID_SIZE = 5
CELL_SIZE = 50
# Amount of mines: This  be configurable
MINES = 5
def main():
    canvas = Canvas(width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
    board_field = []
    discovered = []
    discovered_cells = 0
    init_game(canvas, board_field, discovered)
    redraw(canvas, discovered, board_field)
    for row in board_field:
        print(row)
    for row in discovered:
        print(row)
    
    # Change this when mines ara implemented on graphic board. THe game must end when a mine is clicked or all blank_spaces are discovered
    continue_game = True
    win_game = False
    while continue_game:
        click = canvas.get_last_click()
        if click is not None:
            x, y = click
            row = int(y / CELL_SIZE)
            col = int(x / CELL_SIZE)
            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                if board_field[row][col] == 'M':
                    continue_game = False
                    win_game = False
                    break
                elif not discovered[row][col]:
                    if board_field[row][col] == 0:
                        reveal_empty_cells(board_field, discovered, row, col)
                    else:
                        discovered[row][col] = True
                    discovered_cells = sum(sum_row.count(True) for sum_row in discovered)
                    redraw(canvas, discovered, board_field)
                    if discovered_cells == GRID_SIZE * GRID_SIZE - MINES:
                        win_game = True
                        continue_game = False
    final_redraw(canvas, board_field, win_game)

def reveal_empty_cells(board_field, discovered, row, col):
    stack = [(row, col)]
    print(f"clicked on: {stack}")
    while stack:
        current_row, current_col = stack.pop()
        print(f"this is an explosion cell board_field{current_row, current_col}")
        if 0 <= current_row < GRID_SIZE and 0 <= current_col < GRID_SIZE and not discovered[current_row][current_col]:
            discovered[current_row][current_col] = True
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

def init_game(canvas, board_field, discovered):
    for i in range(GRID_SIZE):
        row = []
        row_discovered = []
        for k in range(GRID_SIZE):
            row.append(' ')
            row_discovered.append(False)
        board_field.append(row)
        discovered.append(row_discovered)
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
        for col in range(GRID_SIZE):
            value = board_field[row][col]
            left_x = col * CELL_SIZE
            top_y = row * CELL_SIZE
            right_x = left_x + CELL_SIZE
            bottom_y = top_y + CELL_SIZE
            canvas.create_rectangle(left_x, top_y, right_x, bottom_y, color='white', outline='black')
            if str(value) != 'M' and value > 0:
                pos_x = col * CELL_SIZE + CELL_SIZE / 2
                pos_y = row * CELL_SIZE + CELL_SIZE / 2
                canvas.create_text(pos_x, pos_y, text=str(value), font='Arial', font_size='16')
    reveal_all_mines(canvas, board_field)
    finish_game(canvas, win_game)
def finish_game(canvas, won):
    if won:
        canvas.create_text(
        canvas.get_width() // 2,
        canvas.get_height() // 2,
        text="🏆 You Win!!",
        font='Arial',
        font_size=24,
        color='green',
        anchor='center'
    )
    else:
        canvas.create_text(
        canvas.get_width() / 2,
        canvas.get_height() / 2,
        text="💥BOOM!!! You Lose.",
        font='Arial',
        font_size=24,
        color='red',
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
def redraw(canvas, discovered, board_field):
    canvas.clear()
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            left_x = col * CELL_SIZE
            top_y = row * CELL_SIZE
            right_x = left_x + CELL_SIZE
            bottom_y = top_y + CELL_SIZE
            if discovered[row][col]:
                color = 'white'
            else:
                color = 'lightgrey'
            canvas.create_rectangle(left_x, top_y, right_x, bottom_y, color=color, outline='black')
            value = board_field[row][col]
            if discovered[row][col] and str(value) != 'M' and value > 0:
                pos_x = col * CELL_SIZE + CELL_SIZE / 2
                pos_y = row * CELL_SIZE + CELL_SIZE / 2
                canvas.create_text(pos_x, pos_y, text=str(value), font='Arial', font_size='16')
def draw_mine(canvas, row, col):
    center_x = col * CELL_SIZE + CELL_SIZE / 2
    center_y = row * CELL_SIZE + CELL_SIZE / 2
    radius = CELL_SIZE * 0.2  # Puedes ajustar este valor para cambiar el tamaño

    # Dibuja un círculo negro para representar la mina
    canvas.create_oval(
        center_x - radius, center_y - radius,
        center_x + radius, center_y + radius,
        color='black'
    )
    # Dibuja líneas radiales como "púas" de la mina
    for angle in range(0, 360, 45):  # Cada 45 grados
        dx = CELL_SIZE * 0.3 * math.cos(math.radians(angle))
        dy = CELL_SIZE * 0.3 * math.sin(math.radians(angle))
        try:
            print(f"DRAW LINE from ({center_x}, {center_y}) to "
                f"({center_x + dx}, {center_y + dy})")  # Debug print
            canvas.create_line(
                center_x, center_y,
                center_x + dx, center_y + dy,
                color='black'
            )
        except Exception as e:
            print(f"Error drawing line: ({row}, {col}){e}")

if __name__ == '__main__':
    main()
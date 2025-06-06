'''
Project Description
This project is a functional implementation of the classic Minesweeper game,
developed using Python and the educational graphics.
Canvas library in the Code in Place environment. The game features mine placement, adjacent cell
calculation, recursive reveal of empty cells, flagging, and win/loss detection. Throughout the
development process, I tackled various challenges, such as optimizing the reveal algorithm,
handling edge cases in the grid, improving UI efficiency by redrawing only necessary cells,
and debugging logic related to game flow. An important part of the project was learning and applying
the Depth-First Search (DFS) algorithm to implement the recursive cell reveal logic.
Additionally, I experimented with integrating artificial intelligence using a custom call_gpt()
function to query a language model for potential moves. This helped me explore the limits
of AI interaction in logical games and understand how prompt design and model behavior influence results.
How to Play This Version of Minesweeper
🎯 Objective:
Uncover all the empty cells without clicking on any mines. If you reveal all non-mine cells, you win! If you click on a mine, you lose.
🧱 Grid:
You can choose between three different difficulty levels,
from easy, medium and hard.
Each level has between 12 and 76 randomly placed mines.
💡 Ask AI:
If you're unsure about your next move, click the "Ask AI" button at the bottom of the screen. The AI will analyze the current board and suggest a safe cell to reveal. The suggested move will be played automatically as if you clicked it.
The AI only suggests unrevealed and unflagged cells.
Use this feature wisely — it doesn't guarantee safety, but it makes the best guess based on visible information.
(Truly, AI doesn't know how to play)
👆 Controls:
🔍 Left Click:
Simply click on a cell to reveal it.
If it's a number, it shows how many mines are nearby.
If it's empty (0), it automatically reveals all adjacent empty cells and their borders.
🚩 Right-Click / Flag Mode:
Press and release Shift once since we are in a loop, then click left button on a cell to place or remove a flag. (This simulates right click of original minesweeper game)
Flags help you mark suspected mines.
You cannot reveal a flagged cell until you remove the flag.
🎉 End of Game:
If you reveal a mine: 💥 You lose.
If you reveal all non-mine cells: 🏆 You win!
When the game ends, all mines are revealed automatically.
'''
from graphics import Canvas
import random
import math
import time
import os
from ai import call_gpt

# Difficult Level
LEVELS = {
    'Easy': (8, 0.20),
    'Medium': (12, 0.22),
    'Hard': (16, 0.30)
}
# Sizes
FOOTER_SIZE = 50
CELL_SIZE = 50
#Time Limits
TIME = 0.000001
#Text properties
text_sz = 30
#############################################################################################
"""
Main entry point for the Minesweeper game. Initializes the canvas, board, and UI elements,
handles user interactions (clicks and key presses), updates the timer and mine counter,
and controls the game loop including win/loss conditions and interaction with an AI assistant.
"""
def main():
    global GRID_SIZE, WIDTH, HEIGHT, MINES
    ai_button = {}
    board_field = []
    discovered = []
    flags = []
    discovered_cells = 0
    start_time = None
    count_flags = 0
    continue_game = True
    win_game = False
    is_shift_pressed = False
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
    ai_rect = canvas.create_rectangle(
        (width // 2 - 50), height - 40,  # top-left x, y
        (width // 2 + 50), height - 10,  # bottom-right x, y
        color='lightgray', outline='black'
    )
    ai_display = canvas.create_text(
        (width // 2), height - 25,
        text="Ask AI", font='Arial', font_size=20, color='black', anchor='center'
    )
    # Guardamos las coordenadas del área clicable
    ai_button['ask_ai'] = {
        'rect_id': ai_rect,
        'text_id': ai_display,
        'top': height - 40,
        'bottom': height - 10,
        'left': width // 2 - 50,
        'right': width // 2 + 50
    }
    init_game(canvas, board_field, discovered, flags)
    draw(canvas, discovered, board_field)
    while continue_game:
        key_press = canvas.get_last_key_press()
        click = canvas.get_last_click()
        if key_press == 'Shift':
            is_shift_pressed = True
        if click is not None:
            if start_time is None:
                start_time = time.time()
            x, y = click
            ai = ai_button.get('ask_ai')
            if ai and ai['left'] <= x <= ai['right'] and ai['top'] <= y <= ai['bottom']:
                prompt = build_prompt(board_field, discovered, flags)
                print('asking AI...')
                res = call_gpt(prompt)
                print(f'Response: {res}')
                aux_x, aux_y = map(int, res.strip("() ").split(","))
                if 0 <= aux_x < GRID_SIZE and 0 <= aux_y < GRID_SIZE:
                    row = int(aux_x)
                    col = int(aux_y)
                else:
                    row = int(int(y) / CELL_SIZE)
                    col = int(int(x) / CELL_SIZE)
            else:
                row = int(int(y) / CELL_SIZE)
                col = int(int(x) / CELL_SIZE)
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
    canvas.delete(ai_rect)
    canvas.delete(ai_display)
    final_redraw(canvas, board_field, win_game)
#############################################################################################    
"""
Displays difficulty level options on the canvas and waits for the user to select one.
Args:
    canvas (Canvas): The canvas object used to draw UI elements.
Returns:
    tuple: A pair (grid_size, mine_ratio) corresponding to the selected difficulty level.
"""
def pick_your_level(canvas):
    canvas.create_text(canvas.get_width() // 2, 60, text="Pick your level", font='Courier', font_size=text_sz, color='black', anchor='center')
    y=160
    buttons = {}
    for level, (size, ratio) in LEVELS.items():
        rect_id = canvas.create_rectangle(canvas.get_width() // 2 - 100, y, canvas.get_width() // 2 + 100, y + 40, color='lightgray', outline='black')
        text_id = canvas.create_text(canvas.get_width() // 2, y + 20, text=level, font='Arial', font_size=18, anchor='center')
        buttons[level] = (rect_id, text_id, y, y + 40)
        y += 60
    while True:
        click = canvas.get_last_click()
        if click is not None:
            x, y = click
            for level, (_, _, top, bottom) in buttons.items():
                if canvas.get_width() // 2 - 100 <= x <= canvas.get_width() // 2 + 100 and top <= y <= bottom:
                    canvas.clear()  # limpia la pantalla antes de crear el juego
                    return LEVELS[level]
#############################################################################################
"""
Reveals a connected area of empty cells (value 0) starting from the given cell.
Uses a depth-first-like stack approach to uncover adjacent non-mine cells.
Args:
    canvas (Canvas): The canvas used for drawing.
    board_field (list): The 2D list representing the board values.
    discovered (list): The 2D list tracking revealed cells.
    flags (list): The 2D list of flagged cells.
    row (int): The row index of the clicked cell.
    col (int): The column index of the clicked cell.
"""
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
#############################################################################################
"""
Counts the number of mines adjacent to the cell at (row, col).
Args:
    row (int): Row index of the cell.
    col (int): Column index of the cell.
    board_field (list): The 2D list representing the game board.
Returns:
    int: The number of adjacent mines.
"""
def count_adjacent_mines(row, col, board_field):
    """
    Cuenta cuántas minas hay en las celdas adyacentes a la posición (row, col).
    Las celdas adyacentes incluyen: arriba, abajo, izquierda, derecha y diagonales.
    """
    count = 0
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
#############################################################################################
"""
Initializes the board by setting up the game field, placing mines,
and calculating numbers for each non-mine cell.
Args:
    canvas (Canvas): The canvas used for rendering.
    board_field (list): 2D list to store the minefield values.
    discovered (list): 2D list to track revealed cells.
    flags (list): 2D list to track flagged cells.
"""
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
#############################################################################################
"""
Reveals all the mines on the board (used at the end of the game).
Args:
    canvas (Canvas): The canvas used for rendering.
    board_field (list): 2D list containing the board with mines.
"""
def reveal_all_mines(canvas, board_field):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board_field[row][col] == 'M':
                draw_mine(canvas, row, col)
#############################################################################################
"""
Redraws the entire board at the end of the game and displays win or lose message.
Args:
    canvas (Canvas): The canvas object used to draw.
    board_field (list): The 2D board containing cell values.
    win_game (bool): Whether the player won or lost.
"""
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
#############################################################################################
"""
Displays the final game message depending on the result.
Args:
    canvas (Canvas): The canvas used for display.
    won (bool): Whether the player has won the game.
"""
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
#############################################################################################
"""
Randomly places a number of mines on the game board.
Args:
    board_field (list): The 2D list representing the board to be populated with mines.
"""
def put_mines_in_board_field(board_field):
    mines_in_board = 0
    while mines_in_board < MINES:
        row = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)
        if board_field[row][col] != 'M':
            board_field[row][col] = 'M'
            mines_in_board += 1
#############################################################################################
"""
Updates the on-screen timer based on elapsed game time.
Args:
    canvas (Canvas): The canvas used for rendering.
    start_time (float): The timestamp when the game started.
    timer_display (int): Canvas object ID for the timer text.
Returns:
    int: Elapsed time in seconds.
"""
def update_timer(canvas, start_time, timer_display):
    elapsed_time = int(time.time() - start_time)
    canvas.change_text(timer_display, f'{elapsed_time:03d}s')
    return elapsed_time
#############################################################################################
"""
Updates the on-screen mine counter based on current flags.
Args:
    canvas (Canvas): The canvas used for rendering.
    mine_display (int): Canvas object ID for the mine counter text.
    count_flags (int): The number of flags placed.
"""
def update_mine_display(canvas, mine_display, count_flags):
    remain = MINES - count_flags
    canvas.change_text(mine_display, f'{remain:02d}')
#############################################################################################
"""
Draws a single cell based on its discovered state and value.
Args:
    canvas (Canvas): The canvas to draw on.
    row (int): Row index of the cell.
    col (int): Column index of the cell.
    board_field (list): The 2D game board.
    discovered (list): 2D list indicating revealed cells.
"""
def draw_cell(canvas, row, col, board_field, discovered):
    left_x = col * CELL_SIZE
    top_y = row * CELL_SIZE
    right_x = left_x + CELL_SIZE
    bottom_y = top_y + CELL_SIZE
    value = board_field[row][col]
    color = 'white' 
    if not discovered[row][col]:
        color = 'lightgrey'
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
#############################################################################################
"""
Draws the entire board based on the current discovered state.
Args:
    canvas (Canvas): The canvas to draw on.
    discovered (list): 2D list of boolean values indicating revealed cells.
    board_field (list): 2D list representing the minefield.
"""
def draw(canvas, discovered, board_field):
    for row in range(GRID_SIZE):
        time.sleep(float(TIME))
        for col in range(GRID_SIZE):
            draw_cell(canvas, row, col, board_field, discovered)
#############################################################################################
"""
Toggles a flag on a hidden cell or removes it if already flagged.
Args:
    canvas (Canvas): The canvas to draw on.
    flags (list): 2D list storing flag object IDs or None.
    discovered (list): 2D list of discovered cells.
    row (int): Row index of the clicked cell.
    col (int): Column index of the clicked cell.
"""
def draw_flag(canvas, flags, discovered, row, col):
    count_flags = sum(cell is not None for row in flags for cell in row)
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
#############################################################################################
"""
Draws a mine on the board either as an emoji if image does not exist or the file image.
Args:
    canvas (Canvas): The canvas to draw on.
    row (int): Row index of the mine.
    col (int): Column index of the mine.
"""
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
#############################################################################################
"""
Builds a textual representation of the board for sending to the AI assistant.
Converts board state into a simplified format for reasoning.
I truly think that AI, with these instructions, can't play — either because it doesn't know how to play
or because the prompt is not good enough
Args:
    board_field (list): 2D list of cell values.
    discovered (list): 2D list of revealed cells.
    flags (list): 2D list of flag status.
Returns:
    str: A formatted prompt string suitable for language model input.
"""
def build_prompt(board_field, discovered, flags):
    board = []
    prompt = (
        "You are playing Minesweeper. it's mandatory you search the rules and basics of playing minesweeper Based on the current board state, suggest a single safe move "
        "as a coordinate in the format (row, col), where row and col are zero-based integers.\n\n"
        "Uncover all the empty cells without clicking on any mines. If you reveal all non-mine cells, you win! If you click on a mine, you lose.\n"
        "Each cell may be:\n"
        "- 'H' = hidden (not revealed)\n"
        "- 'F' = flagged as a mine\n"
        "- 'M' = revealed mine (should not appear in suggested moves)\n"
        "- '0'-'8' = number of adjacent mines (revealed cell)\n\n"
        "Only suggest a cell that is currently hidden ('H') and not flagged ('F').\n"
        "Return ONLY one coordinate, like this: (3, 5)\n\n"
        "Current board:\n"
    )
    for d_row in range(GRID_SIZE):
        aux = []
        for d_col in range(GRID_SIZE):
            if discovered[d_row][d_col]:
                aux.append(board_field[d_row][d_col])
            elif flags[d_row][d_col] is not None:
                aux.append('F')
            else:
                aux.append('H')
        board.append(aux)
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            aux = f'([{row}][{col}] = {board[row][col]})'
            prompt += aux
    prompt += "\nYour move just return the tupla fila, columna and remember just return tuplas with 'H':"
    return prompt
#############################################################################################
if __name__ == '__main__':
    main()
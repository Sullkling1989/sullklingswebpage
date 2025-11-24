import tkinter as tk
import random

# Game constants
CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
DELAY = 500  # Initial fall speed in ms
LEVEL_UP_SCORE = 100  # Score to advance a level
MAX_LEVEL = 5

# Tetromino shapes
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]],
}

COLORS = {
    'I': 'cyan',
    'O': 'yellow',
    'T': 'purple',
    'S': 'green',
    'Z': 'red',
    'J': 'blue',
    'L': 'orange',
}

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris")
        self.canvas = tk.Canvas(root, width=CELL_SIZE * COLUMNS, height=CELL_SIZE * ROWS, bg='black')
        self.canvas.pack()
        self.score = 0
        self.level = 1
        self.delay = DELAY
        self.game_over = False
        self.board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_piece = None
        self.current_position = [0, COLUMNS // 2 - 1]
        self.create_new_piece()
        self.root.bind("<Key>", self.key_pressed)
        self.draw_board()
        self.update_game()

    def create_new_piece(self):
        self.current_piece = random.choice(list(SHAPES.keys()))
        self.current_rotation = 0
        self.current_position = [0, COLUMNS // 2 - len(SHAPES[self.current_piece][0]) // 2]
        if self.check_collision(self.current_position):
            self.game_over = True
            self.canvas.create_text(CELL_SIZE * COLUMNS // 2, CELL_SIZE * ROWS // 2,
                                    text="GAME OVER", fill="white", font=('Helvetica', 24))

    def rotate_piece(self):
        rotated = list(zip(*SHAPES[self.current_piece][::-1]))
        old_shape = SHAPES[self.current_piece]
        SHAPES[self.current_piece] = rotated
        if self.check_collision(self.current_position):
            SHAPES[self.current_piece] = old_shape  # revert
        else:
            self.draw_board()

    def move_piece(self, dx, dy):
        new_pos = [self.current_position[0] + dy, self.current_position[1] + dx]
        if not self.check_collision(new_pos):
            self.current_position = new_pos
            self.draw_board()
        elif dy == 1:  # Collision when moving down
            self.lock_piece()
            self.clear_lines()
            self.create_new_piece()

    def check_collision(self, pos):
        shape = SHAPES[self.current_piece]
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    y = pos[0] + r
                    x = pos[1] + c
                    if x < 0 or x >= COLUMNS or y >= ROWS:
                        return True
                    if y >= 0 and self.board[y][x]:
                        return True
        return False

    def lock_piece(self):
        shape = SHAPES[self.current_piece]
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    y = self.current_position[0] + r
                    x = self.current_position[1] + c
                    if y >= 0:
                        self.board[y][x] = COLORS[self.current_piece]

    def clear_lines(self):
        lines_cleared = 0
        new_board = []
        for row in self.board:
            if 0 not in row:
                lines_cleared += 1
            else:
                new_board.append(row)
        for _ in range(lines_cleared):
            new_board.insert(0, [0 for _ in range(COLUMNS)])
        self.board = new_board
        self.score += lines_cleared * 10
        if self.score >= self.level * LEVEL_UP_SCORE and self.level < MAX_LEVEL:
            self.level += 1
            self.delay = max(100, DELAY - self.level * 50)
        self.draw_board()

    def key_pressed(self, event):
        if self.game_over and event.keysym == "Return":
            self.restart_game()
        if not self.game_over:
            if event.keysym == "Left":
                self.move_piece(-1, 0)
            elif event.keysym == "Right":
                self.move_piece(1, 0)
            elif event.keysym == "Down":
                self.move_piece(0, 1)
            elif event.keysym == "Up":
                self.rotate_piece()

    def draw_board(self):
        self.canvas.delete("all")
        # Draw fixed blocks
        for r in range(ROWS):
            for c in range(COLUMNS):
                if self.board[r][c]:
                    self.draw_cell(c, r, self.board[r][c])
        # Draw current piece
        shape = SHAPES[self.current_piece]
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    y = self.current_position[0] + r
                    x = self.current_position[1] + c
                    if y >= 0:
                        self.draw_cell(x, y, COLORS[self.current_piece])
        # Draw score and level
        self.canvas.create_text(5, 5, anchor='nw', fill="white",
                                text=f"Score: {self.score}\nLevel: {self.level}")

    def draw_cell(self, x, y, color):
        x0 = x * CELL_SIZE
        y0 = y * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

    def update_game(self):
        if not self.game_over:
            self.move_piece(0, 1)
            self.root.after(self.delay, self.update_game)

    def restart_game(self):
        self.score = 0
        self.level = 1
        self.delay = DELAY
        self.board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.game_over = False
        self.create_new_piece()
        self.update_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()

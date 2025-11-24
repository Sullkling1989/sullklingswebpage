import tkinter as tk
import random

# -----------------------------
# Game Constants
# -----------------------------
WIN_WIDTH = 750
WIN_HEIGHT = 700
PIPE_WIDTH = 80
PIPE_GAP = 200       # wider gap
BIRD_SIZE = 25
GRAVITY = 0.4
JUMP_STRENGTH = -7
PIPE_SPEED = 3
PIPE_INTERVAL = 3000  # milliseconds

# -----------------------------
class FlappyBirdGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird - Tkinter")

        self.canvas = tk.Canvas(root, width=WIN_WIDTH, height=WIN_HEIGHT, bg="skyblue")
        self.canvas.pack()

        self.running = False
        self.pipes = []

        # Bind keys
        self.root.bind("<space>", self.jump)
        self.root.bind("<Return>", self.restart_game)

        # Start for the first time
        self.setup_game()
        self.start_game()

    # -----------------------------
    def setup_game(self):
        """Resets all variables for a new game."""
        self.canvas.delete("all")

        self.score = 0
        self.score_text = self.canvas.create_text(
            10, 10, anchor="nw", text="Score: 0", 
            font=("Arial", 24), fill="white"
        )

        # Bird setup
        self.bird_y = WIN_HEIGHT // 2
        self.bird_vel = 0
        self.bird = self.canvas.create_oval(
            100, self.bird_y - BIRD_SIZE,
            100 + BIRD_SIZE, self.bird_y + BIRD_SIZE,
            fill="yellow"
        )

        self.pipes = []
        self.running = True

        # Schedule pipe spawning
        self.root.after_cancel(getattr(self, "pipe_job", None)) if hasattr(self, "pipe_job") else None
        self.pipe_job = self.root.after(PIPE_INTERVAL, self.spawn_pipe)

    # -----------------------------
    def start_game(self):
        """Begin the game loop."""
        self.running = True
        self.game_loop()

    # -----------------------------
    def restart_game(self, event=None):
        if not self.running:  # Only works after game over
            self.setup_game()
            self.start_game()

    # -----------------------------
    def jump(self, event=None):
        if self.running:
            self.bird_vel = JUMP_STRENGTH

    # -----------------------------
    def spawn_pipe(self):
        if not self.running:
            return

        gap_y = random.randint(150, WIN_HEIGHT - 150)

        top_pipe = self.canvas.create_rectangle(
            WIN_WIDTH, 0, WIN_WIDTH + PIPE_WIDTH,
            gap_y - PIPE_GAP // 2,
            fill="green"
        )

        bottom_pipe = self.canvas.create_rectangle(
            WIN_WIDTH, gap_y + PIPE_GAP // 2,
            WIN_WIDTH + PIPE_WIDTH, WIN_HEIGHT,
            fill="green"
        )

        self.pipes.append((top_pipe, bottom_pipe))

        # keep spawning pipes
        self.pipe_job = self.root.after(PIPE_INTERVAL, self.spawn_pipe)

    # -----------------------------
    def move_pipes(self):
        for top, bottom in list(self.pipes):
            self.canvas.move(top, -PIPE_SPEED, 0)
            self.canvas.move(bottom, -PIPE_SPEED, 0)

            x1, _, x2, _ = self.canvas.coords(top)

            # If pipe leaves the screen
            if x2 < 0:
                self.pipes.remove((top, bottom))
                self.canvas.delete(top)
                self.canvas.delete(bottom)

                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

    # -----------------------------
    def move_bird(self):
        self.bird_vel += GRAVITY
        self.bird_y += self.bird_vel

        self.canvas.coords(
            self.bird,
            100, self.bird_y - BIRD_SIZE,
            100 + BIRD_SIZE, self.bird_y + BIRD_SIZE
        )

    # -----------------------------
    def overlaps(self, item1, item2):
        x1, y1, x2, y2 = self.canvas.coords(item1)
        x3, y3, x4, y4 = self.canvas.coords(item2)
        return not (x2 < x3 or x1 > x4 or y2 < y3 or y1 > y4)

    # -----------------------------
    def check_collision(self):
        bx1, by1, bx2, by2 = self.canvas.coords(self.bird)

        # hit edges
        if by1 <= 0 or by2 >= WIN_HEIGHT:
            return True

        # hit pipes
        for top, bottom in self.pipes:
            if self.overlaps(self.bird, top) or self.overlaps(self.bird, bottom):
                return True

        return False

    # -----------------------------
    def game_loop(self):
        if not self.running:
            return

        self.move_bird()
        self.move_pipes()

        if self.check_collision():
            self.running = False
            self.canvas.create_text(
                WIN_WIDTH // 2, WIN_HEIGHT // 2,
                text="GAME OVER\nPress Enter to Restart",
                font=("Arial", 36), fill="red"
            )
            return

        self.root.after(16, self.game_loop)


# -----------------------------
root = tk.Tk()
game = FlappyBirdGame(root)
root.mainloop()

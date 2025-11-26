import tkinter as tk
import math
import random
import time

WIDTH, HEIGHT = 800, 700
CENTI_SPEED = 5.5
enemy_speed = 6.0
projectile_speed = 1.65
FIRE_INTERVAL = 7000
PROJECTILE_LIFETIME = 8000
LEVEL_KILL_REQUIREMENT = 50

class Projectile:
    def __init__(self, canvas, x, y, dx, dy):
        self.canvas = canvas
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.spawn_time = time.time()
        self.id = canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.canvas.coords(self.id, self.x-5, self.y-5, self.x+5, self.y+5)

    def expired(self):
        return (time.time() - self.spawn_time) * 1000 > PROJECTILE_LIFETIME or \
               self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

class Enemy:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = random.randint(50, WIDTH-50)
        self.y = random.randint(50, HEIGHT-50)
        self.last_fire = time.time()
        self.id = canvas.create_rectangle(self.x-10, self.y-10, self.x+10, self.y+10, fill="darkred")

    def update(self):
        self.x += random.uniform(-enemy_speed, enemy_speed)
        self.y += random.uniform(-enemy_speed, enemy_speed)
        self.x = max(20, min(WIDTH-20, self.x))
        self.y = max(20, min(HEIGHT-20, self.y))
        self.canvas.coords(self.id, self.x-10, self.y-10, self.x+10, self.y+10)

    def try_fire(self, player):
        now = time.time()
        if (now - self.last_fire) * 1000 > FIRE_INTERVAL:
            self.last_fire = now
            angle = math.atan2(player.y - self.y, player.x - self.x)
            dx = math.cos(angle) * projectile_speed
            dy = math.sin(angle) * projectile_speed
            return Projectile(self.canvas, self.x, self.y, dx, dy)
        return None

class Centipede:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = WIDTH//2
        self.y = HEIGHT//2
        self.length = 20
        self.lives = 12
        self.trail = []
        self.ids = []

    def update(self, mouse_x, mouse_y):
        angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
        self.x += math.cos(angle) * CENTI_SPEED
        self.y += math.sin(angle) * CENTI_SPEED

        self.trail.append((self.x, self.y))
        if len(self.trail) > self.length:
            self.trail.pop(0)

    def draw(self):
        for cid in self.ids:
            self.canvas.delete(cid)
        self.ids = []
        for tx, ty in self.trail:
            cid = self.canvas.create_oval(tx-6, ty-6, tx+6, ty+6, fill="green")
            self.ids.append(cid)

    def grow(self):
        self.length += 5

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Centipede Game - Tkinter Edition")
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()
        self.reset_game()
        self.root.bind("<Return>", self.restart)
        self.root.bind("<Motion>", self.mouse_move)
        self.mouse_x, self.mouse_y = WIDTH//2, HEIGHT//2
        self.update()
        self.root.mainloop()

    def mouse_move(self, event):
        self.mouse_x, self.mouse_y = event.x, event.y

    def reset_game(self):
        self.canvas.delete("all")
        self.player = Centipede(self.canvas)
        self.enemies = [Enemy(self.canvas) for _ in range(5)]
        self.projectiles = []
        self.kills = 0
        self.level = 1
        self.game_over = False
        self.ui = self.canvas.create_text(10, 10, anchor="nw", fill="white", font=("Arial", 16))

    def restart(self, event):
        if self.game_over:
            self.reset_game()

    def update(self):
        if not self.game_over:
            self.player.update(self.mouse_x, self.mouse_y)
            self.player.draw()

            for e in self.enemies[:]:
                e.update()
                shot = e.try_fire(self.player)
                if shot:
                    self.projectiles.append(shot)

                # Collision with entire centipede body
                for tx, ty in self.player.trail:
                    if math.hypot(tx - e.x, ty - e.y) < 20:
                        if e in self.enemies:
                            self.enemies.remove(e)
                            self.canvas.delete(e.id)
                            self.player.grow()
                            self.kills += 1

            if len(self.enemies) < 5:
                self.enemies.append(Enemy(self.canvas))

            for p in self.projectiles[:]:
                p.update()
                if p.expired():
                    self.canvas.delete(p.id)
                    self.projectiles.remove(p)
                    continue

                # Collision with entire centipede body
                for tx, ty in self.player.trail:
                    if math.hypot(tx - p.x, ty - p.y) < 10:
                        self.canvas.delete(p.id)
                        if p in self.projectiles:
                            self.projectiles.remove(p)
                        self.player.lives -= 1
                        if self.player.lives <= 0:
                            self.game_over = True
                        break

            if self.kills >= LEVEL_KILL_REQUIREMENT:
                self.level += 1
                self.kills = 0
                self.player.length += 20
                if self.level > 5:
                    self.game_over = True

            # Update UI with length/score
            self.canvas.itemconfig(self.ui, text=f"Lives: {self.player.lives}  Level: {self.level}  Length/Kills: {self.player.length}/{self.kills}")

        else:
            self.canvas.create_text(WIDTH//2, HEIGHT//2, fill="white", font=("Arial", 24),
                                    text="GAME OVER - Press ENTER to Restart")

        self.root.after(16, self.update)

Game()

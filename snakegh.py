"""
SnakeGH - A Classic Arcade Game
Lab 2 - Python (Level 200)
Name: Patrick Ankomah | Index No: 2526403267
"""
import random
import tkinter as tk
import winsound
import pygame

CELL = 24                # size of one square in pixels
COLS = 25                # squares across
ROWS = 20                # squares down
WIDTH = CELL * COLS      # 600 pixels
HEIGHT = CELL * ROWS     # 480 pixels
START_SPEED = 150        # milliseconds between moves (smaller = faster)
HIGH_SCORE_FILE = "snake_highscore.txt"\

DIRECTIONS = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1,
0)}
OPPOSITE = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}

KEYS = {"up": "Up", "w": "Up", "down": "Down", "s": "Down",
"left": "Left", "a": "Left", "right": "Right", "d": "Right"}

pygame.mixer.init()           #initialize pygame mixer
pygame.mixer.music.load("background-sound.mp3")     #loads the background sound for the game




# ---------------- Logic functions (no GUI code here) ----------------
def next_head(head, direction):
    """Return the square the head moves into."""
    dx, dy = DIRECTIONS[direction]
    x, y = head
    return x + dx, y + dy

def hits_wall(cell):
    """True if the square is outside the board."""
    x, y = cell
    return x < 0 or x >= COLS or y < 0 or y >= ROWS

def hits_self(head, snake):
    """True if the head runs into the body (the tail moves away, so skip
     it)."""
    return head in snake[:-1]

def random_food(snake):
    """Pick a random empty square for the food."""
    free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in
    snake]
    return random.choice(free)

def level_for(score):
    """Level goes up every 5 points."""
    return score // 5 + 1

def speed_for(level):
    """Each level is 15 ms faster, but never faster than 60 ms."""
    return max(60, START_SPEED - (level - 1) * 15)

def load_high_score():
    """Read the saved high score, or 0 if there is none yet."""
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    """Write the new high score to the file."""
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))

# ---------------- Game state ----------------
snake = []
direction = "Right"
next_direction = "Right"
food = (0, 0)
score = 0
level = 1
high_score = load_high_score()
running = False
paused = False
loop_id = None
no_walls_enabled = False
golden_food: tuple | None = None
golden_timer = None


# ---------------- GUI event handlers ----------------
def draw_grid():
    """Draw faint grid lines once, at the start."""
    for x in range(0, WIDTH, CELL):
        canvas.create_line(x, 0, x, HEIGHT, fill="#161b22")   #darker, and subtle grid lines
    for y in range(0, HEIGHT, CELL):
        canvas.create_line(0, y, WIDTH, y, fill="#1e1e1e")

def update_labels():
    score_label.config(text=f"Score: {score}     Level: {level}     Best:{high_score}")

def draw():
        """Clear the old snake and food, then draw them in their new places."""
        canvas.delete("piece", "message")

        fx, fy = food
        canvas.create_oval(fx * CELL + 4, fy * CELL + 4, fx * CELL + CELL - 4, fy * CELL + CELL - 4,
                           fill="#e53935", outline="", tags="piece")

        if golden_food:
            gx, gy = golden_food
            canvas.create_oval(gx * CELL + 4, gy * CELL + 4, gx * CELL + CELL - 4, gy * CELL + CELL - 4,
                               fill="#ffd600", outline="", tags="piece")

        for index, (x, y) in enumerate(snake):
            pad = 2
            colour = "#66bb6a" if index == 0 else "#00b0ff"
            canvas.create_oval(x * CELL + pad, y * CELL + pad, x * CELL + CELL -pad, y * CELL + CELL - pad,
                                    fill=colour, outline="", tags="piece")
        update_labels()

def show_message(title, subtitle):
    """Write a big message in the middle of the board."""
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 20, text=title, fill="white",font=("Segoe UI", 28, "bold"), tags="message")

    canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20, text=subtitle, fill="#bbbbbb",font=("Segoe UI", 12), tags="message")

def start_game(_event=None):
     global snake, direction, next_direction, food, score, level, running,paused, loop_id
     if loop_id is not None:
         root.after_cancel(loop_id)
     snake = [(5, 10), (4, 10), (3, 10)]
     direction = "Right"
     next_direction = "Right"
     food = random_food(snake)
     score = 0
     level = 1
     running = True
     paused = False
     draw()
     loop_id = root.after(speed_for(level), game_loop)
     spawn_golden_food()

def game_loop():
    """One tick: move, eat, draw, then schedule the next tick."""
    global direction, golden_food, food, score, level, loop_id
    direction = next_direction
    head = next_head(snake[0], direction)

    # Check if the snake eats golden food
    if head == golden_food:
         pygame.mixer.Sound("eat_insect_sound.mp3").play()
         score += 3           # Add 3 points to the score
         level = level_for(score)  # Update the game level
         golden_food = None   # Remove the golden food after eating

    if no_walls_enabled:
        wrapped_x = head[0] % COLS
        wrapped_y = head[1] % ROWS
        head = (wrapped_x, wrapped_y)
        if hits_self(head, snake):
             game_over()
             return
    else:
        if hits_wall(head) or hits_self(head, snake):
            game_over()
            return
    snake.insert(0, head)

    if head == food:
        score += 1
        level = level_for(score)
        food = random_food(snake)
        #play a smooth system chime
        pygame.mixer.Sound("eat_insect_sound.mp3").play()
    else:
        snake.pop()

    draw()
    loop_id = root.after(speed_for(level), game_loop)


def on_key(event):
    """Change direction, but never straight back into the body."""
    global next_direction
    new_direction = KEYS.get(event.keysym.lower())
    if new_direction is None or not running or paused:
        return
    if new_direction != OPPOSITE[direction]:
        next_direction = new_direction

def on_space(_event=None):
    if not running:
        start_game()
        winsound.Beep(200, 300)   # plays a short beep sound
        pygame.mixer.music.play(-1)  # plays the music on an infinite loop

def toggle_pause(_event=None):
    global paused, loop_id
    if not running:
        return
    paused = not paused
    if paused:
        root.after_cancel(loop_id)
        show_message("PAUSED", "Press P to continue")
        pygame.mixer.music.pause()
    else:
        canvas.delete("message")
        loop_id = root.after(speed_for(level), game_loop)
        pygame.mixer.music.unpause()

def game_over():
    global running, high_score
    running = False
    #play a low descending game over buzz
    pygame.mixer.Sound("game-over.mp3").play()
    if score > high_score:
        high_score = score
        save_high_score(high_score)
        show_message("NEW HIGH SCORE!", f"You scored {score}. Press Space to play again")
    else:
        show_message("GAME OVER", f"You scored {score}. Press Space to play again")
    update_labels()
    pygame.mixer.music.stop()

def toggle_no_walls(_event=None):
    global no_walls_enabled
    no_walls_enabled = not no_walls_enabled
    print(f"No walls mode: {no_walls_enabled}")

def spawn_golden_food():
    global golden_food, golden_timer

    if not running:
        return

    # Choose a random position not occupied by the snake
    golden_food = random.choice([
        (x, y) for x in range(COLS)
        for y in range(ROWS) if (x, y) not in snake
    ])

    # Remove golden food after 5 seconds
    golden_timer = root.after(5000, remove_golden_food)

    # Spawn new golden food every 10 seconds
    root.after(10000, spawn_golden_food)

def remove_golden_food():
    global golden_food

    # Make golden food disappear
    golden_food = None

# ---------------- Build the window ----------------

root = tk.Tk()
root.title("SnakeGH - Classic Arcade Game")
root.resizable(False, False)
root.configure(bg="#0d1b2a")

tk.Label(root, text="SnakeGH", font=("Segoe UI", 22, "bold"),
         fg="#66bb6a", bg="#0d1b2a").pack(pady=(10, 0))

score_label = tk.Label(root, text="Score: 0     Level: 1     Best: 0", font=
("Consolas", 13, "bold"), fg="white", bg="#0d1b2a")
score_label.pack(pady=(0, 8))

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#0d1117",
highlightthickness=0)
canvas.pack(padx=15)

tk.Label(root, text="Arrows / W A S D = move     P = pause     Space =start",fg="#90a4ae", bg="#0d1b2a").pack(pady=8)

root.bind("<Key>", on_key)
root.bind("<space>", on_space)
root.bind("p", toggle_pause)
root.bind("P", toggle_pause)
root.bind("n", toggle_no_walls)

draw_grid()

update_labels()
show_message("SnakeGH", "Press Space to start")
root.mainloop()
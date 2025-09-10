# breakout.py
import turtle
import time
import random

# --------- Screen setup ----------
WIDTH, HEIGHT = 800, 600
screen = turtle.Screen()
screen.title("Breakout - Turtle Edition")
screen.bgcolor("black")
screen.setup(WIDTH, HEIGHT)
screen.tracer(0)  # we'll manage updates manually

# --------- Score & Lives display ----------
score = 0
lives = 3

pen = turtle.Turtle()
pen.hideturtle()
pen.penup()
pen.color("white")
pen.goto(0, HEIGHT//2 - 40)
pen.write(f"Score: {score}    Lives: {lives}", align="center", font=("Courier", 18, "normal"))

def update_hud():
    pen.clear()
    pen.goto(0, HEIGHT//2 - 40)
    pen.write(f"Score: {score}    Lives: {lives}", align="center", font=("Courier", 18, "normal"))

# --------- Paddle ----------
paddle = turtle.Turtle()
paddle.shape("square")
paddle.color("white")
paddle.shapesize(stretch_wid=1, stretch_len=6)  # make it rectangular
paddle.penup()
paddle.goto(0, -HEIGHT//2 + 50)

PADDLE_SPEED = 40

def paddle_left():
    x = paddle.xcor() - PADDLE_SPEED
    left_bound = -WIDTH//2 + 50
    if x < left_bound:
        x = left_bound
    paddle.setx(x)

def paddle_right():
    x = paddle.xcor() + PADDLE_SPEED
    right_bound = WIDTH//2 - 50
    if x > right_bound:
        x = right_bound
    paddle.setx(x)

screen.listen()
screen.onkeypress(paddle_left, "Left")
screen.onkeypress(paddle_right, "Right")
screen.onkeypress(paddle_left, "a")
screen.onkeypress(paddle_right, "d")

# --------- Ball ----------
ball = turtle.Turtle()
ball.shape("circle")
ball.color("red")
ball.penup()
ball.goto(0, -100)
ball.dx = 3 * random.choice([1, -1])
ball.dy = 3

BALL_ACCEL = 0.03  # small increase over time or on hit

# --------- Bricks ----------
bricks = []
brick_colors = ["#ff4d4d", "#ff944d", "#ffe44d", "#9fff4d", "#4ddaff"]  # 5 rows

BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = 60
BRICK_HEIGHT = 20
START_X = - (BRICK_COLS / 2) * (BRICK_WIDTH + 10) + BRICK_WIDTH/2 + 10
START_Y = HEIGHT//2 - 120

for row in range(BRICK_ROWS):
    y = START_Y - row * (BRICK_HEIGHT + 10)
    color = brick_colors[row % len(brick_colors)]
    for col in range(BRICK_COLS):
        x = START_X + col * (BRICK_WIDTH + 10)
        brick = turtle.Turtle()
        brick.shape("square")
        brick.shapesize(stretch_wid=BRICK_HEIGHT/20, stretch_len=BRICK_WIDTH/20)
        brick.color(color)
        brick.penup()
        brick.goto(x, y)
        bricks.append(brick)

# --------- Utility functions ----------
def reset_ball_and_paddle():
    global ball
    ball.goto(0, -100)
    ball.dx = 3 * random.choice([1, -1])
    ball.dy = 3
    paddle.goto(0, -HEIGHT//2 + 50)
    time.sleep(0.7)

def check_paddle_collision():
    # if ball is near paddle and moving downwards, bounce
    if (ball.ycor() <= paddle.ycor() + 10 and
        ball.ycor() >= paddle.ycor() - 10 and
        abs(ball.xcor() - paddle.xcor()) <= (60 + 30)):  # approximate width tolerance
        return True
    return False

def check_brick_collision():
    # returns the brick collided or None
    for brick in bricks:
        if brick.isvisible():
            # simple bounding-box collision (approx)
            if (abs(ball.xcor() - brick.xcor()) < (BRICK_WIDTH/2 + 10)) and \
               (abs(ball.ycor() - brick.ycor()) < (BRICK_HEIGHT/2 + 10)):
                return brick
    return None

# --------- Main game loop ----------
running = True
last_time = time.time()

while running:
    screen.update()
    time.sleep(0.01)  # frame pacing (~100 FPS cap-ish)

    # Move ball
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Wall collisions (left/right)
    if ball.xcor() > WIDTH//2 - 10:
        ball.setx(WIDTH//2 - 10)
        ball.dx *= -1
    if ball.xcor() < -WIDTH//2 + 10:
        ball.setx(-WIDTH//2 + 10)
        ball.dx *= -1

    # Top collision
    if ball.ycor() > HEIGHT//2 - 10:
        ball.sety(HEIGHT//2 - 10)
        ball.dy *= -1

    # Bottom collision -> lose life
    if ball.ycor() < -HEIGHT//2:
        lives -= 1
        update_hud()
        if lives <= 0:
            # Game over
            pen.goto(0, 0)
            pen.write("GAME OVER", align="center", font=("Courier", 36, "bold"))
            pen.goto(0, -40)
            pen.write(f"Final Score: {score}", align="center", font=("Courier", 24, "normal"))
            running = False
            break
        else:
            reset_ball_and_paddle()
            continue

    # Paddle collision
    if check_paddle_collision() and ball.dy < 0:
        # Bounce; modify x velocity depending on where it hits the paddle
        offset = (ball.xcor() - paddle.xcor()) / 60  # -1 .. 1 approx
        ball.dx += offset * 2  # add some horizontal change
        ball.dy *= -1
        # small speed increase to make it progressively harder
        if ball.dx > 0:
            ball.dx += BALL_ACCEL
        else:
            ball.dx -= BALL_ACCEL
        if ball.dy > 0:
            ball.dy += BALL_ACCEL
        else:
            ball.dy -= BALL_ACCEL

    # Brick collision
    brick = check_brick_collision()
    if brick:
        brick.hideturtle()
        # Reverse vertical direction (simple)
        ball.dy *= -1
        score += 10
        update_hud()

        # Increase speed slightly every hit
        if ball.dx > 0:
            ball.dx += BALL_ACCEL
        else:
            ball.dx -= BALL_ACCEL
        if ball.dy > 0:
            ball.dy += BALL_ACCEL
        else:
            ball.dy -= BALL_ACCEL

        # Check win condition
        remaining = [b for b in bricks if b.isvisible()]
        if not remaining:
            pen.goto(0, 0)
            pen.write("YOU WIN!", align="center", font=("Courier", 36, "bold"))
            pen.goto(0, -40)
            pen.write(f"Final Score: {score}", align="center", font=("Courier", 24, "normal"))
            running = False
            break

    # tiny anti-stuck correction: ensure dx/dy don't become zero
    if abs(ball.dx) < 0.6:
        ball.dx = 0.6 if ball.dx >= 0 else -0.6
    if abs(ball.dy) < 0.6:
        ball.dy = 0.6 if ball.dy >= 0 else -0.6

# Keep window open until closed by user
screen.mainloop()
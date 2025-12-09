from flask import Flask, request, jsonify, render_template
import subprocess
import tempfile
import os
import sys

app = Flask(__name__, template_folder='.')

BASE_CODE = r"""
import turtle
import time

def start_game():
    global TILE_SIZE, START_X, START_Y
    # ---------- MAZE DATA ----------
    maze = [
        "XXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "XP                        X",
        "X XXX XXXXXXX X XXXXXXX XXX",
        "X   X X     X X X     X   X",
        "XXX X X XXX X X X XXX X X X",
        "X   X   X X     X X X   X X",
        "X XXXXXXX X XXXXX X XXXXX X",
        "X       X X     X X     X X",
        "XXXXXXX X XXXXX X XXXXX X X",
        "X     X X     X X     X   X",
        "X XXX X XXXXX X XXXXX XXXXX",
        "X X   X     X X     X     X",
        "X X XXXXXXX X XXXXX XXXXX X",
        "X X       X X     X     G X",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXX",
    ]

    ROWS = len(maze)
    COLS = len(maze[0])
    TILE_SIZE = 24

    START_X = - (COLS * TILE_SIZE) // 2
    START_Y =   (ROWS * TILE_SIZE) // 2

    # ---------- SCREEN ----------
    wn = turtle.Screen()
    wn.title("CIE & CC Maze Challenge")
    wn.bgcolor("black")
    wn.setup(width=900, height=700)
    wn.tracer(0)

    # ---------- TURTLES ----------
    class Wall(turtle.Turtle):
        def __init__(self):
            super().__init__()
            self.shape("square")
            self.color("white")
            self.penup()
            self.speed(0)
            self.shapesize(TILE_SIZE / 20 * 0.9, TILE_SIZE / 20 * 0.9)

    class Player(turtle.Turtle):
        def __init__(self):
            super().__init__()
            import os
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            gif_path = os.path.join(script_dir, "animation.gif")
            wn.addshape(gif_path)
            self.shape(gif_path)
            self.color("cyan")
            self.penup()
            self.speed(0)

    class Goal(turtle.Turtle):
        def __init__(self):
            super().__init__()
            self.shape("circle")
            self.color("red")
            self.penup()
            self.speed(0)

    # Create objects
    wall = Wall()
    player = Player()
    goal = Goal()
    error_display = turtle.Turtle()
    error_display.hideturtle()
    error_display.penup()
    error_display.speed(0)

    walls = set()  
    start = None   
    end = None     

    player_gx = None
    player_gy = None

    # ---------- BUILD MAZE ----------
    def setup_maze(level):
        nonlocal start, end, player_gx, player_gy
        for gy, row in enumerate(level):
            for gx, cell in enumerate(row):
                sx = START_X + gx * TILE_SIZE
                sy = START_Y - gy * TILE_SIZE

                if cell == "X":
                    wall.goto(sx, sy)
                    wall.stamp()
                    walls.add((gx, gy))

                elif cell == "P":
                    start = (gx, gy)
                    player_gx, player_gy = gx, gy
                    player.goto(sx, sy)

                elif cell == "G":
                    end = (gx, gy)
                    goal.goto(sx, sy)

        wn.update()

    def grid_to_screen(gx, gy):
        return START_X + gx * TILE_SIZE, START_Y - gy * TILE_SIZE

    # ---------- ERROR DISPLAY ----------
    def show_error(message):
        error_display.clear()
        error_display.goto(0, START_Y + 80)
        error_display.color("red")
        error_display.fillcolor("red")
        
        # Draw red box - larger size
        box_width = 500
        box_height = 100
        error_display.begin_fill()
        error_display.goto(-box_width/2, START_Y + 80)
        error_display.pendown()
        error_display.goto(box_width/2, START_Y + 80)
        error_display.goto(box_width/2, START_Y + 80 - box_height)
        error_display.goto(-box_width/2, START_Y + 80 - box_height)
        error_display.goto(-box_width/2, START_Y + 80)
        error_display.end_fill()
        error_display.penup()
        
        # Write error text - larger font
        error_display.goto(0, START_Y + 35)
        error_display.color("white")
        error_display.write(message, align="center", font=("Arial", 18, "bold"))
        wn.update()
        
        # Clear error after 2 seconds
        wn.ontimer(lambda: error_display.clear(), 2000)

    # ---------- FAIL ----------
    def fail(message):
        print(message)
        wn.title(message + "  Try again!")
        time.sleep(1)
        wn.bye()

    # ---------- MOVEMENT ----------
    def attempt_move(dx, dy):
        nonlocal player_gx, player_gy

        nx = player_gx + dx
        ny = player_gy + dy

        # bounds
        if not (0 <= nx < COLS and 0 <= ny < ROWS):
            fail("Out of bounds!")
            return

        # wall collision
        if (nx, ny) in walls:
            show_error("Error: Hit a wall! Try a different direction.")
            return

        # update
        error_display.clear()  # Clear any error message on successful move
        player_gx, player_gy = nx, ny
        sx, sy = grid_to_screen(nx, ny)
        player.goto(sx, sy)
        wn.update()
        time.sleep(0.08)

    # Public movement commands
    def move_up():    attempt_move(0, -1)
    def move_down():  attempt_move(0, 1)
    def move_left():  attempt_move(-1, 0)
    def move_right(): attempt_move(1, 0)  # أصلحناها لسالب خطوة كاملة

    # Setup maze
    setup_maze(maze)

    # نرجع كل شيء للمستخدم
    return player, wn, move_up, move_down, move_left, move_right, end

# ----------------- USE EXAMPLE -------------------

player, wn, move_up, move_down, move_left, move_right, end = start_game()
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/maze-image")
def maze_image():
    from flask import send_from_directory
    return send_from_directory(".", "IMG.jpg")

@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    user_code = data.get("code", "")

    try:
        # Get the base directory where app.py is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Inject the base directory path into BASE_CODE
        base_code_updated = BASE_CODE.replace(
            'script_dir = os.path.dirname(os.path.abspath(__file__))',
            f'script_dir = r"{base_dir}"'
        )

        full_code = base_code_updated + "\n# --- user code starts here ---\n" + user_code + "\n\nif player.xcor() == 24 * TILE_SIZE + START_X and player.ycor() == START_Y - 13 * TILE_SIZE: wn.title('You reached the goal! 🎉')\nelse: wn.title('Did NOT reach the goal. Try again!') " + "\n\nwn.mainloop()\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            file_path = f.name
            f.write(full_code)

        python_exec = sys.executable
        subprocess.Popen([python_exec, file_path])

        return jsonify({"status": "ok", "message": "Your maze program is running. Check the turtle window."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

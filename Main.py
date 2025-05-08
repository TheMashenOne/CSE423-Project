from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
start_time = time.time()  # Starting time of the application
last_frame_time = start_time  # Time of the last frame
delta_time = 0.0  # Time elapsed since last frame
animation_time = 0.0  # Accumulated time for animations
coin_positions = []  # List of (x, z) tuples for coin positions
NUM_COINS = 50
# Camera-related variables - positioned to view the full expanded maze
camera_pos = (0, 4100, 4100)  # Higher and further back for full maze view
camera_look_at = (0, 0, 0)  # Point camera is looking at
camera_angle = 0  # Track camera angle for rotation
fovY = 60  # Field of view
GRID_LENGTH = 2400  # Doubled the floor size
rand_var = 423
action_mode = "collect"
# Game level and maze data
current_level = 0
collected_coins = [set(), set()]  # List of sets for each level's collected coins
key_collected = False
view_mode = "overhead"
player_pos = [0, 0]  # Will be set by find_player_start()
player_angle = 0.0  # 0 = facing north
player_health = 10  # Player starts with 50 health
player_last_hit_time = 0  # Track when player was last hit for invincibility frames
PLAYER_INVINCIBILITY_TIME = 1000  # 1 second of invincibility after being hit
game_over = False  # Track if the game is over due to player death
enemies = []  # Format: [[row, col, direction, last_move_time], ...]
# direction: 0=north, 1=east, 2=south, 3=west
ENEMY_MOVE_INTERVAL = 800  # Reduced from 1000 to make normal enemies move faster
bullets = []  # Format: [x, y, z, dx, dy, dz, creation_time, is_player_bullet]  # Added is_pet flag
player_bullets = []  # Format: [x, y, z, dx, dy, dz, creation_time]  # Separate list for player bullets
BULLET_SPEED = 5  # Normal bullet speed
BOSS_BULLET_SPEED = 3  # Slower bullets for bos
BOSS_MOVE_SPEED = 0.001  # Slower movement speed for boss
BULLET_LIFETIME = 3000  # 3 seconds
ENEMY_ROTATION_SPEED = 1.0  # Reduced from 2.0 to make rotation slower
ENEMY_FIRE_INTERVAL = 200  # milliseconds between shots
PLAYER_FIRE_INTERVAL = 100  # milliseconds between player shots
player_last_shot_time = 0  # Track when player last fired
player_immobilized = False
player_immobilize_time = 0
IMMOBILIZE_DURATION = 3000
enemy_rotations = []  # Store rotation angle for each enemy
body_radius = None  # Will be set dynamically based on wall size
gun_length = None  # Will be set dynamically based on wall size
# Direction vectors for the four guns: North, East, South, West
gun_offsets = [(0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0)]
freeze_traps_collected = 0  # Number of freeze traps the player has
selected_item = ""  # Currently selected item ("key" or "freeze_trap")
freeze_trap_positions = []  # Positions of deployed freeze traps
FREEZE_DURATION = 5000  # Duration of freeze effect in milliseconds
enemy_freeze_times = []  # When each enemy was frozen (0 = not frozen)
bullets_fired = 0  # Tracks how many bullets the player has fired
bullet_limit = 15  # Starts at 15, doubles to 30 after collecting 50 coins
cloak_collected = False  # Tracks if the cloak has been collected
cloak_active = False  # Tracks if the cloak is currently active
cloak_duration = 5000  # Duration of invisibility in milliseconds
cloak_start_time = 0  # Tracks when the cloak was activated
cheat_mode = False
original_bullet_speed = BULLET_SPEED
mouse_left_down = False
mazes = [
    # Level 1 Maze
    [
        [1] * 15,
        [1, 0, 0, 1, 0, 0, 0, 1, 8, 1, 0, 0, 0, 4, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 5, 0, 0, 0, 1, 6, 0, 0, 0, 0, 1, 0, 0, 1],  # Enemy (5)
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 5, 1],  # Enemy (5)
        [1, 0, 1, 1, 1, 1, 7, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 6, 0, 0, 0, 0, 1, 0, 0, 0, 0, 5, 1, 0, 1],  # Enemy (5)
        [1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 9, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1],  # Key (2)
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Player start (3)
        [1] * 15,
    ],
    # Level 2 Maze
    [
        [1] * 15,
        [1, 4, 0, 1, 0, 0, 0, 1, 8, 1, 0, 0, 0, 0, 1],  # Black cube (4) in top-left
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 5, 0, 0, 0, 1, 6, 0, 0, 0, 5, 1, 0, 0, 1],  # Added more enemies (2 enemies in this row)
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 0, 0, 5, 1],  # Enemy (5)
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 6, 0, 0, 0, 0, 1, 0, 0, 0, 0, 5, 1, 0, 1],  # Freeze trap (6) and added 1 more enemy
        [1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 7, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],  # Game over trap (9)
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1],  # Key (2)
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],  # Player start (3) bottom-right
        [1] * 15,
    ],
    # Level 3 (Open Arena for Boss Fight)
    [
        [1] * 15,
        [1, 2, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 1],  # Black cube (4) in top-left
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Added more enemies (2 enemies in this row)
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],  # Enemy (5)
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Freeze trap (6) and added 1 more enemy
        [1, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Game over trap (9)
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Key (2)
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 1],  # Player start (3) bottom-right
        [1] * 15,
    ]
]

# Add new variable near the top with other global variables
wall_phasing = False  # Track if wall phasing is active

# Add near the top with other global variables
game_paused = False  # Track if the game is paused

# Add near the top with other global variables
game_state = "menu"  # Can be "menu" or "playing"
menu_button_rect = (400, 350, 200, 50)  # (x, y, width, height) for the start button
instructions_button_rect = (400, 280, 200, 50)  # (x, y, width, height) for the instructions button
exit_button_rect = (400, 210, 200, 50)  # (x, y, width, height) for the exit button
show_instructions = False  # Track if instructions are being shown

MAX_PLAYER_HEALTH = 100  # Maximum health cap

# Add near the top with other global variables
fifty_coin_bonus_given = False  # Track if 50 coin bonus has been given
hundred_coin_bonus_given = False  # Track if 100 coin bonus has been given

def get_elapsed_time():
    return int((time.time() - start_time) * 1000)  # Convert to milliseconds
def update_delta_time():
    global last_frame_time, delta_time, animation_time
    current_time = time.time()
    delta_time = current_time - last_frame_time
    last_frame_time = current_time
    animation_time += delta_time  # Accumulate time for animations
    return delta_time

def find_player_start():
    maze = mazes[current_level]
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 3:
                return [row, col]
    return [0, 0]  # Fallback if not found

def generate_coin_positions():
    """Generate coin positions for the current level."""
    global coin_positions
    maze = mazes[current_level]
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(maze) * wall_size // 2
    empty_cells = []

    # Only skip coins for level 3 (index 2)
    if current_level == 2:  # Level 3 (Boss Fight) - no coins in boss level
        coin_positions = []
        return

    # Generate coins for levels 1 and 2
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            # Check for empty floor and not a special cell
            if maze[row][col] == 0:  # Empty floor
                x = col * wall_size - offset + wall_size / 2
                z = row * wall_size - offset + wall_size / 2
                empty_cells.append((x, z))

    # Use different seeds for different levels to ensure different coin patterns
    random.seed(423 + current_level)  # Different seed for each level
    coin_positions = random.sample(empty_cells, min(NUM_COINS, len(empty_cells)))
    #print(f"Generated {len(coin_positions)} coins for level {current_level + 1}")  # Debug print

def load_next_level():
    """Transition the game to the next level."""
    global current_level, player_pos, enemies, key_collected
    global freeze_traps_collected, freeze_trap_positions, bullets, player_bullets
    global cloak_collected, cloak_active, cloak_start_time, bullets_fired
    global player_health, player_last_hit_time, player_immobilized, player_immobilize_time
    global collected_coins, coin_positions

    if current_level >= len(mazes) - 1:
        print("You have reached the final level. Game completed!")
        return

    # Increment the level
    current_level += 1

    # Reset player position
    player_pos = find_player_start()

    # Reset enemies, bullets, and other level-specific variables
    enemies = []
    bullets = []
    player_bullets = []
    bullets_fired = 0

    # Reset traps deployed in the current level
    freeze_trap_positions = []  # Clear deployed traps, but keep collected traps
    key_collected = False

    # Preserve player attributes
    # Reset temporary states
    player_last_hit_time = 0
    player_immobilized = False
    player_immobilize_time = 0
    cloak_start_time = 0 if not cloak_active else cloak_start_time  # Preserve cloak state across levels

    # Initialize enemies and coins for the new level
    initialize_enemies()
    generate_coin_positions()

    # Ensure collected_coins list has enough elements for the new level
    while len(collected_coins) <= current_level:
        collected_coins.append(set())

    print(f"Level {current_level + 1} loaded!")


def player_shoot():
    """Make the player shoot a bullet in the direction they're facing, considering bullet limits."""
    global player_last_shot_time, bullets_fired, bullet_limit, game_over
    if player_immobilized:
        return
    current_time = get_elapsed_time()
    if current_time - player_last_shot_time < PLAYER_FIRE_INTERVAL:
        return  # Don't shoot if we fired too recently
    # Check if bullets fired exceed the limit
    if not cheat_mode and bullets_fired >= bullet_limit:
        game_over = True  # End the game if bullet limit is exceeded
        return
    # Increment bullets fired
    bullets_fired += 1
    player_last_shot_time = current_time
    # Calculate the bullet's starting position (in front of the player's gun)
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[current_level]) * wall_size // 2
    row, col = player_pos
    x = col * wall_size - offset + wall_size / 2
    z = row * wall_size - offset + wall_size / 2
    y = 10.0 + wall_size / 3  # Height of gun
    # FIX: Flip the angle calculation so up/down directions match the visual direction
    corrected_angle = (360 - player_angle) % 360  # Invert the angle orientation
    angle_rad = math.radians(corrected_angle)
    # Calculate direction vector with the corrected angle
    dx = math.sin(angle_rad)
    dz = -math.cos(angle_rad)
    # Start bullet a bit in front of the player
    gun_length = wall_size / 2
    x += dx * gun_length
    z += dz * gun_length
    # Add bullet to player_bullets list with corrected direction
    player_bullets.append([x, y, z, dx * BULLET_SPEED, 0, dz * BULLET_SPEED, current_time])

def draw_boundary_walls():
    """Draw tall brownish red boundary walls around the entire area"""
    wall_size = GRID_LENGTH * 2 // 15  # Based on grid length and maze size
    maze = mazes[current_level]
    maze_size = len(maze) * wall_size
    offset = maze_size // 2

    # Calculate dimensions for boundary walls
    boundary_height = 400  # Reduced height for boundary walls
    boundary_thickness = 200  # Thick walls

    # Brownish red color for boundaries
    boundary_color = (0.6, 0.2, 0.1)  # Brownish red
    darker_boundary = (0.5, 0.15, 0.05)  # Slightly darker for side faces

    # North boundary wall (negative Z)
    glBegin(GL_QUADS)
    # Top face
    glColor3f(*boundary_color)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)

    # Inner face (facing the maze)
    glColor3f(*darker_boundary)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH)

    # Top surface
    glColor3f(*boundary_color)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH)
    glEnd()

    # South boundary wall (positive Z)
    glBegin(GL_QUADS)
    # Outer face
    glColor3f(*boundary_color)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)

    # Inner face
    glColor3f(*darker_boundary)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH)

    # Top surface
    glColor3f(*boundary_color)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glEnd()

    # West boundary wall (negative X)
    glBegin(GL_QUADS)
    # Outer face
    glColor3f(*boundary_color)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, -GRID_LENGTH - boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, 0, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)

    # Inner face
    glColor3f(*darker_boundary)
    glVertex3f(-GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, boundary_height, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, boundary_height, -GRID_LENGTH)

    # Top surface
    glColor3f(*boundary_color)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glVertex3f(-GRID_LENGTH - boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(-GRID_LENGTH, boundary_height, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, boundary_height, -GRID_LENGTH)
    glEnd()

    # East boundary wall (positive X)
    glBegin(GL_QUADS)
    # Outer face
    glColor3f(*boundary_color)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, -GRID_LENGTH - boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, 0, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)

    # Inner face
    glColor3f(*darker_boundary)
    glVertex3f(GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(GRID_LENGTH, boundary_height, GRID_LENGTH)
    glVertex3f(GRID_LENGTH, boundary_height, -GRID_LENGTH)

    # Top surface
    glColor3f(*boundary_color)
    glVertex3f(GRID_LENGTH, boundary_height, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, boundary_height, GRID_LENGTH)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, GRID_LENGTH + boundary_thickness)
    glVertex3f(GRID_LENGTH + boundary_thickness, boundary_height, -GRID_LENGTH - boundary_thickness)
    glEnd()


def draw_player(x, y, z):
    global cloak_active
    wall_size = GRID_LENGTH * 2 // 15
    leg_radius = wall_size / 12
    leg_height = wall_size / 3
    torso_height = wall_size / 2
    hand_length = wall_size / 3
    torso_radius = wall_size / 6
    head_radius = wall_size / 5
    gun_radius = wall_size / 15
    gun_length = wall_size / 2

    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(player_angle, 0, 1, 0)  # Apply player rotation

    quadric = gluNewQuadric()

    if cloak_active:
        glColor3f(1, 1, 1)  # White for cloaked view
        for dx in [-torso_radius / 2, torso_radius / 2]:
            glPushMatrix()
            glTranslatef(dx, 0, 0)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quadric, leg_radius, leg_radius, leg_height, 12, 3)
            glPopMatrix()

        # Draw torso (cyan cylinder)
        glPushMatrix()
        glTranslatef(0, leg_height, 0)
        glColor3f(0.0, 1.0, 1.0)  # Cyan
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, torso_radius, torso_radius, torso_height, 16, 4)
        glPopMatrix()

        # Draw hands (skin colored cylinders) on both sides of torso - pointing forward
        glColor3f(1, 1, 1)  # White when cloaked
        for dx in [-torso_radius * 1.5, torso_radius * 1.5]:
            glPushMatrix()
            glTranslatef(dx, leg_height + torso_height * 0.8, 0)
            glRotatef(180, 0, 1, 0)  # Rotate to point arms forward
            gluCylinder(quadric, leg_radius * 0.8, leg_radius * 0.8, hand_length, 12, 3)
            glPopMatrix()

        # Draw head (white sphere when cloaked)
        glColor3f(1, 1, 1)  # White
        glPushMatrix()
        glTranslatef(0, leg_height + torso_height + head_radius, 0)
        glutSolidSphere(head_radius, 16, 16)
        glPopMatrix()

        # Draw gun (white cylinder when cloaked) attached to the center of the torso, pointing forward
        glPushMatrix()
        glColor3f(1, 1, 1)  # White
        glTranslatef(0, leg_height + torso_height * 0.7, 0)
        glRotatef(180, 0, 1, 0)
        gluCylinder(quadric, gun_radius, gun_radius, gun_length, 12, 3)
        glPopMatrix()
    else:
        # Draw legs (2 purple cylinders)
        glColor3f(0.6, 0.1, 0.9)  # Purple
        for dx in [-torso_radius / 2, torso_radius / 2]:
            glPushMatrix()
            glTranslatef(dx, 0, 0)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quadric, leg_radius, leg_radius, leg_height, 12, 3)
            glPopMatrix()

        # Draw torso (cyan cylinder)
        glPushMatrix()
        glTranslatef(0, leg_height, 0)
        glColor3f(0.0, 1.0, 1.0)  # Cyan
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, torso_radius, torso_radius, torso_height, 16, 4)
        glPopMatrix()

        # Draw hands (skin colored cylinders) on both sides of torso - pointing forward
        glColor3f(1.0, 0.87, 0.77)  # Skin tone
        for dx in [-torso_radius * 1.5, torso_radius * 1.5]:
            glPushMatrix()
            glTranslatef(dx, leg_height + torso_height * 0.8, 0)
            glRotatef(180, 0, 1, 0)  # Rotate to point arms forward
            gluCylinder(quadric, leg_radius * 0.8, leg_radius * 0.8, hand_length, 12, 3)
            glPopMatrix()

        # Draw head (black sphere)
        glColor3f(0.0, 0.0, 0.0)  # Black
        glPushMatrix()
        glTranslatef(0, leg_height + torso_height + head_radius, 0)
        glutSolidSphere(head_radius, 16, 16)
        glPopMatrix()

        # Draw gun (gray cylinder) attached to the center of the torso, pointing forward
        glPushMatrix()
        glColor3f(0.5, 0.5, 0.5)  # Gray
        glTranslatef(0, leg_height + torso_height * 0.7, 0)
        glRotatef(180, 0, 1, 0)
        gluCylinder(quadric, gun_radius, gun_radius, gun_length, 12, 3)
        glPopMatrix()

    glPopMatrix()  # Final pop to match the initial push

def draw_maze():
    wall_size = GRID_LENGTH * 2 // 15
    wall_height = wall_size // 2
    maze = mazes[current_level]
    offset = len(maze) * wall_size // 2

    # Draw base floor
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.7)
    maze_size = len(maze) * wall_size
    glVertex3f(-offset, 5.0, -offset)
    glVertex3f(maze_size - offset, 5.0, -offset)
    glVertex3f(maze_size - offset, 5.0, maze_size - offset)
    glVertex3f(-offset, 5.0, maze_size - offset)
    glEnd()

    # Draw maze cells
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            cell = maze[row][col]
            x = col * wall_size - offset
            z = row * wall_size - offset

            if cell == 0:
                # Floor tile
                glBegin(GL_QUADS)
                glColor3f(0.1, 0.6, 0.1)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()

            elif cell == 1:
                # Wall
                glBegin(GL_QUADS)
                glColor3f(0.2, 0.2, 0.8)
                glVertex3f(x, wall_height + 10.0, z)
                glVertex3f(x + wall_size, wall_height + 10.0, z)
                glVertex3f(x + wall_size, wall_height + 10.0, z + wall_size)
                glVertex3f(x, wall_height + 10.0, z + wall_size)
                glEnd()

                # Draw visible side faces
                if row > 0 and maze[row - 1][col] != 1:
                    glBegin(GL_QUADS)
                    glColor3f(0.15, 0.15, 0.7)
                    glVertex3f(x, 10.0, z)
                    glVertex3f(x + wall_size, 10.0, z)
                    glVertex3f(x + wall_size, wall_height + 10.0, z)
                    glVertex3f(x, wall_height + 10.0, z)
                    glEnd()
                if row < len(maze) - 1 and maze[row + 1][col] != 1:
                    glBegin(GL_QUADS)
                    glColor3f(0.15, 0.15, 0.7)
                    glVertex3f(x, 10.0, z + wall_size)
                    glVertex3f(x + wall_size, 10.0, z + wall_size)
                    glVertex3f(x + wall_size, wall_height + 10.0, z + wall_size)
                    glVertex3f(x, wall_height + 10.0, z + wall_size)
                    glEnd()
                if col > 0 and maze[row][col - 1] != 1:
                    glBegin(GL_QUADS)
                    glColor3f(0.15, 0.15, 0.7)
                    glVertex3f(x, 10.0, z)
                    glVertex3f(x, 10.0, z + wall_size)
                    glVertex3f(x, wall_height + 10.0, z + wall_size)
                    glVertex3f(x, wall_height + 10.0, z)
                    glEnd()
                if col < len(maze[0]) - 1 and maze[row][col + 1] != 1:
                    glBegin(GL_QUADS)
                    glColor3f(0.15, 0.15, 0.7)
                    glVertex3f(x + wall_size, 10.0, z)
                    glVertex3f(x + wall_size, 10.0, z + wall_size)
                    glVertex3f(x + wall_size, wall_height + 10.0, z + wall_size)
                    glVertex3f(x + wall_size, wall_height + 10.0, z)
                    glEnd()

            elif cell == 2:
                # Floor under key
                glBegin(GL_QUADS)
                glColor3f(0.1, 0.6, 0.1)
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()
                # Animated key position
                glPushMatrix()
                current_time = get_elapsed_time() % 1000
                height_offset = 50 + 20 * abs(current_time - 500) / 500
                glTranslatef(x + wall_size / 2, height_offset, z + wall_size / 2)
                # --- Glowing Aura (transparent sphere) ---
                glPushMatrix()
                glScalef(1.5, 1.5, 1.5)
                glColor4f(1.0, 0.9, 0.4, 0.9)  # Orange glow, low alpha
                glutSolidSphere(wall_size / 4, 16, 16)
                glPopMatrix()
                # --- Solid Key: Orange Sphere + Sideways Cylinder ---
                glColor3f(1.0, 0.5, 0.0)  # Bright orange
                glutSolidSphere(wall_size / 4, 16, 16)
                quadric = gluNewQuadric()
                glRotatef(-90, 0, 1, 0)
                gluCylinder(quadric, wall_size / 12, wall_size / 12, wall_size / 2, 12, 3)
                glPopMatrix()

            elif cell == 4:
                # Draw green floor under the black cube
                glBegin(GL_QUADS)
                glColor3f(0.1, 0.6, 0.1)  # Grass green
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()
                # Draw black cube (exit block) sitting on top of the floor
                glPushMatrix()
                glTranslatef(x + wall_size / 2, wall_height / 2 + 10.0, z + wall_size / 2)
                glColor3f(0.05, 0.05, 0.05)  # Very dark gray/black
                glutSolidCube(wall_size)
                glPopMatrix()

            elif cell == 5:
                # Floor under enemy
                glBegin(GL_QUADS)
                glColor3f(0.1, 0.6, 0.1)  # Same green as normal floor
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()
            elif cell == 7:  # Cloak collectible
                # Floor under the cloak
                glBegin(GL_QUADS)
                glColor3f(0.1, 0.6, 0.1)  # Green floor
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()

                # Draw animated white sphere for the cloak
                glPushMatrix()

                # Use time to calculate scale and height dynamically
                current_time = get_elapsed_time() % 1000  # Modulo for smooth looping
                scale_factor = 0.75 + 0.25 * math.sin(current_time * 2 * math.pi / 1000)  # Scale between 0.75 and 1.0
                height_offset = 50 + 20 * abs(current_time - 500) / 500  # Vertical oscillation

                glTranslatef(x + wall_size / 2, height_offset, z + wall_size / 2)
                glScalef(scale_factor, scale_factor, scale_factor)  # Apply the scaling effect
                glColor3f(1.0, 1.0, 1.0)  # White color
                glutSolidSphere(wall_size / 4, 16, 16)
                glPopMatrix()
            elif cell == 8:  # Immobilize trap
                # Draw green floor
                glBegin(GL_QUADS)
                glColor3f(0.1, 0.6, 0.1)  # Same green as normal floor
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()

                # Draw amber trap markings (criss-cross pattern)
                glBegin(GL_LINES)
                glColor3f(1.0, 0.7, 0.0)  # Amber color
                glVertex3f(x, 11.0, z)
                glVertex3f(x + wall_size, 11.0, z + wall_size)
                glVertex3f(x, 11.0, z + wall_size)
                glVertex3f(x + wall_size, 11.0, z)
                glEnd()

            elif cell == 9:  # Deadly trap
                # Draw green floor with red trap markings
                glBegin(GL_QUADS)
                glColor3f(0.6, 0.1, 0.1)  # Reddish floor
                glVertex3f(x, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z)
                glVertex3f(x + wall_size, 10.0, z + wall_size)
                glVertex3f(x, 10.0, z + wall_size)
                glEnd()

                # Draw skull-like pattern with lines
                glBegin(GL_LINES)
                glColor3f(0.0, 0.0, 0.0)  # Black
                # X pattern
                glVertex3f(x + wall_size * 0.3, 11.0, z + wall_size * 0.3)
                glVertex3f(x + wall_size * 0.7, 11.0, z + wall_size * 0.7)
                glVertex3f(x + wall_size * 0.3, 11.0, z + wall_size * 0.7)
                glVertex3f(x + wall_size * 0.7, 11.0, z + wall_size * 0.3)
                glEnd()

                # Circle around the X
                glPushMatrix()
                glTranslatef(x + wall_size / 2, 11.0, z + wall_size / 2)
                glColor3f(0.0, 0.0, 0.0)  # Black
                glutWireSphere(wall_size / 4, 8, 2)
                glPopMatrix()

    # --- Draw Player at player_pos ---
    row, col = player_pos
    x = col * wall_size - offset
    z = row * wall_size - offset

    # Floor under player
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.6, 0.1)
    glVertex3f(x, 10.0, z)
    glVertex3f(x + wall_size, 10.0, z)
    glVertex3f(x + wall_size, 10.0, z + wall_size)
    glVertex3f(x, 10.0, z + wall_size)
    glEnd()

    # Draw player model
    glPushMatrix()
    glTranslatef(x + wall_size / 2, 10.0, z + wall_size / 2)
    draw_player(0, 0, 0)
    glPopMatrix()


def keyboardListener(key, x, y):
    global camera_pos, camera_look_at, player_pos, player_angle, view_mode, freeze_traps_collected, selected_item, freeze_trap_positions, enemy_freeze_times, action_mode, bullet_limit, bullets_fired, cheat_mode, BULLET_SPEED, wall_phasing, game_paused, game_state
    global key_collected, cloak_collected, cloak_active, cloak_start_time, collected_coins, player_health, game_over, player_last_hit_time, enemies, bullets, player_bullets, player_immobilized, player_immobilize_time, current_level, mazes, fifty_coin_bonus_given, hundred_coin_bonus_given

    key = key.decode('utf-8') if isinstance(key, bytes) else chr(key)

    # Handle ESC key to return to menu
    if key == '\x1b':  # ESC key
        game_state = "menu"
        current_level = 0
        player_pos = find_player_start()
        player_angle = 0.0
        player_health = 10
        player_last_hit_time = 0
        player_immobilized = False
        player_immobilize_time = 0
        key_collected = False
        collected_coins = [set() for _ in range(len(mazes))]
        freeze_traps_collected = 0
        freeze_trap_positions = []
        selected_item = "key"
        enemies = []
        player_bullets = []
        bullets = []
        bullets_fired = 0
        initialize_enemies()
        generate_coin_positions()
        game_over = False
        wall_phasing = False
        cloak_active = False
        cloak_collected = 0
        show_instructions = False
        fifty_coin_bonus_given = False
        hundred_coin_bonus_given = False
        return

    # Add pause toggle with space bar
    if key == ' ':
        game_paused = not game_paused
        return

    # Don't process other keys if game is paused (except for unpausing)
    if game_paused:
        return

    if game_over and (key == 'r' or key == 'R'):
        # Reset to menu state
        game_state = "menu"
        current_level = 0

        # Reset all three mazes to their original state
        mazes = [
            # Level 1 Maze
            [
                [1] * 15,
                [1, 0, 0, 1, 0, 0, 0, 1, 8, 1, 0, 0, 0, 4, 1],
                [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
                [1, 5, 0, 0, 0, 1, 6, 0, 0, 0, 0, 1, 0, 0, 1],  # Enemy (5)
                [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 5, 1],  # Enemy (5)
                [1, 0, 1, 1, 1, 1, 7, 1, 0, 1, 1, 1, 1, 0, 1],
                [1, 6, 0, 0, 0, 0, 1, 0, 0, 0, 0, 5, 1, 0, 1],  # Enemy (5)
                [1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 0, 1, 0, 1],
                [1, 9, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
                [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1],  # Key (2)
                [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
                [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Player start (3)
                [1] * 15,
            ],
            # Level 2 Maze
            [
                [1] * 15,
                [1, 4, 0, 1, 0, 0, 0, 1, 8, 1, 0, 0, 0, 0, 1],  # Black cube (4) in top-left
                [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
                [1, 5, 0, 0, 0, 1, 6, 0, 0, 0, 5, 1, 0, 0, 1],  # Added more enemies (2 enemies in this row)
                [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 0, 0, 5, 1],  # Enemy (5)
                [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
                [1, 6, 0, 0, 0, 0, 1, 0, 0, 0, 0, 5, 1, 0, 1],  # Freeze trap (6) and added 1 more enemy
                [1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 0, 1, 0, 1],
                [1, 7, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],  # Game over trap (9)
                [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 2, 1, 0, 1],  # Key (2)
                [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],  # Player start (3) bottom-right
                [1] * 15,
            ],
            # Level 3 (Open Arena for Boss Fight)
            [
                [1] * 15,
                [1, 2, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 1],  # Black cube (4) in top-left
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Added more enemies (2 enemies in this row)
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],  # Enemy (5)
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Freeze trap (6) and added 1 more enemy
                [1, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Game over trap (9)
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Key (2)
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 1],  # Player start (3) bottom-right
                [1] * 15,
            ]
        ]

        player_pos = find_player_start()
        player_angle = 0.0
        player_health = 10  # Use the initial health value set at game start
        player_last_hit_time = 0
        player_immobilized = False
        player_immobilize_time = 0
        key_collected = False
        collected_coins = [set() for _ in range(len(mazes))]  # Initialize sets for all levels
        freeze_traps_collected = 0
        freeze_trap_positions = []
        selected_item = "key"
        enemies = []
        player_bullets = []
        bullets = []
        bullets_fired = 0
        initialize_enemies()
        generate_coin_positions()
        game_over = False
        wall_phasing = False  # Reset wall phasing
        cloak_active = False  # Reset cloak state
        cloak_collected = 0  # Reset cloak count
        show_instructions = False  # Reset instructions state
        fifty_coin_bonus_given = False
        hundred_coin_bonus_given = False
        return

    if game_over:
        return

    current_time = get_elapsed_time()
    if player_immobilized:
        if current_time - player_immobilize_time > IMMOBILIZE_DURATION:
            player_immobilized = False  # Player is free
        else:
            if key in ['+', '=', '-', '_', 'r', 'R', '1', '2', '3', '4']:
                pass
            else:
                return

    row, col = player_pos
    maze = mazes[current_level]

    # Handle cheat mode toggle
    if key == 'c' or key == 'C':
        cheat_mode = not cheat_mode
        wall_phasing = False  # Reset wall phasing when toggling cheat mode
        if cheat_mode:
            BULLET_SPEED = original_bullet_speed * 2  # Double bullet speed in cheat mode
            # Don't modify cloak state when activating cheat mode
        else:
            BULLET_SPEED = original_bullet_speed  # Reset to original speed when cheat mode is off
            # Reset cloak timer when cheat mode is turned off
            if cloak_active:
                cloak_start_time = get_elapsed_time()  # Reset to current time to start normal duration
            current_time = get_elapsed_time()
            for i in range(len(enemy_freeze_times)):
                if enemy_freeze_times[i] > 0:
                    if current_time - enemy_freeze_times[i] < FREEZE_DURATION:
                        # Keep the enemy frozen with the current elapsed time preserved
                        pass
                    else:
                        # Enemy has been frozen longer than the freeze duration, so unfreeze it
                        enemy_freeze_times[i] = 0
        print(f"Cheat mode {'activated' if cheat_mode else 'deactivated'}")
        return

    # Handle wall phasing toggle
    if key == 'v' or key == 'V':
        if cheat_mode:  # Only allow wall phasing in cheat mode
            wall_phasing = not wall_phasing
            print(f"Wall phasing {'activated' if wall_phasing else 'deactivated'}")
        return

    # --- Rotation ---
    if key == 'a' or key == 'A':  # Rotate left
        player_angle = (player_angle + 15) % 360  # Increased from 5 to 15 degrees
    elif key == 'd' or key == 'D':  # Rotate right
        player_angle = (player_angle - 15) % 360  # Increased from 5 to 15 degrees

    # --- Movement ---
    if key == 'w' or key == 'W':  # Forward in facing direction
        # Calculate next position based on facing direction
        angle_rad = math.radians(player_angle)  # Convert angle to radians
        dx = -math.sin(angle_rad)  # X-axis movement
        dz = math.cos(angle_rad)  # Z-axis movement (negative because north is -z)

        # Normalize the movement vector
        length = math.sqrt(dx * dx + dz * dz)
        if length > 0:
            dx = dx / length
            dz = dz / length

        # Calculate the potential new position with normalized movement
        next_row = row - int(round(dz * 1.25))  # Movement speed
        next_col = col + int(round(dx * 1.25))  # Movement speed

        # Check if movement is valid
        # Even in wall phasing mode, don't allow going through boundary walls
        if (0 <= next_row < len(maze) and 0 <= next_col < len(maze[0]) and
                (wall_phasing or maze[next_row][next_col] in [0, 2, 3, 4, 6, 7, 8,
                                                              9])):  # Valid moves: empty, key, exit, freeze trap
            player_pos[0], player_pos[1] = next_row, next_col

    elif key == 's' or key == 'S':  # Backward (opposite of facing direction)
        # Calculate next position based on facing direction
        angle_rad = math.radians(player_angle)
        dx = math.sin(angle_rad)  # Reverse X-axis movement
        dz = -math.cos(angle_rad)  # Reverse Z-axis movement

        # Normalize the movement vector
        length = math.sqrt(dx * dx + dz * dz)
        if length > 0:
            dx = dx / length
            dz = dz / length

        next_row = row - int(round(dz * 1.25))  # Movement speed
        next_col = col + int(round(dx * 1.25))  # Movement speed

        # Check if movement is valid
        # Even in wall phasing mode, don't allow going through boundary walls
        if (0 <= next_row < len(maze) and 0 <= next_col < len(maze[0]) and
                (wall_phasing or maze[next_row][next_col] in [0, 2, 3, 4, 6, 7, 8, 9])):
            player_pos[0], player_pos[1] = next_row, next_col

    # Only check for traps if not in cheat mode
    if not cheat_mode:
        if maze[player_pos[0]][player_pos[1]] == 8:  # Immobilize trap
            player_immobilized = True
            player_immobilize_time = current_time
        elif maze[player_pos[0]][player_pos[1]] == 9:  # Deadly trap
            game_over = True

    # --- Coin Collection ---
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[current_level]) * wall_size // 2
    player_row, player_col = player_pos
    player_x = player_col * wall_size - offset + wall_size / 2
    player_z = player_row * wall_size - offset + wall_size / 2

    for i, (coin_x, coin_z) in enumerate(coin_positions):
        dist_sq = (player_x - coin_x) ** 2 + (player_z - coin_z) ** 2
        if dist_sq < (wall_size / 2.5) ** 2 and i not in collected_coins[current_level]:
            collected_coins[current_level].add(i)
            total_collected = sum(len(coins) for coins in collected_coins)

            # Check for 50 coin bonus
            if total_collected >= 50 and not fifty_coin_bonus_given:
                bullet_limit = 30
                player_health = player_health + 5
                fifty_coin_bonus_given = True
                print("Bullet limit increased to 30 and health increased!")

            # Check for 100 coin bonus
            if total_collected >= 100 and not hundred_coin_bonus_given:
                bullet_limit = 50
                player_health = player_health + 5
                hundred_coin_bonus_given = True
                print("Bullet limit increased to 50 and health increased!")

    # --- Item Selection and Actions ---
    if key == '5':
        action_mode = "key"
        if key_collected:
            selected_item = "key"
    elif key == '6':
        action_mode = "freeze_trap"
        if freeze_traps_collected > 0:
            selected_item = "freeze_trap"
    elif key == '7':  # Select the cloak
        action_mode = "cloak"
        if cloak_collected > 0:
            selected_item = "cloak"

    # --- Item Collection and Actions ---
    if key == 'e' or key == 'E':
        if maze[row][col] == 4:  # Black cube
            if current_level == 2 and key_collected and selected_item == "key":
                print("You have completed the game! Congratulations!")
                game_over = True
            elif key_collected and selected_item == "key":
                load_next_level()
            else:
                print("You need to select and have the key to progress!")
        elif maze[row][col] == 2 and not key_collected:
            key_collected = True
            maze[row][col] = 0  # Remove key from maze
            selected_item = "key"
            action_mode = "key"
        elif maze[row][col] == 7:
            cloak_collected += 1
            maze[row][col] = 0  # Remove cloak from maze
            selected_item = "cloak"
            action_mode = "cloak"
        elif maze[row][col] == 6:
            freeze_traps_collected += 1
            maze[row][col] = 0
            selected_item = "freeze_trap"
            action_mode = "freeze_trap"
        elif action_mode == "key" and key_collected:
            if maze[row][col] == 0:
                key_collected = False
                maze[row][col] = 2
                selected_item = ""
        elif action_mode == "cloak" and cloak_collected > 0 and not cloak_active:
            # Only allow cloak activation if not standing on black cube
            if maze[row][col] != 4:
                cloak_active = True
                cloak_collected -= 1  # Use up the cloak
                cloak_start_time = get_elapsed_time()  # Start the cloak timer
                if cloak_collected == 0:
                    selected_item = "key" if key_collected else ""
        elif action_mode == "freeze_trap" and freeze_traps_collected > 0:
            if maze[row][col] == 0:
                freeze_traps_collected -= 1
                freeze_trap_positions.append([row, col])
                if freeze_traps_collected == 0:
                    selected_item = "key" if key_collected else ""

                current_time = get_elapsed_time()
                for i, enemy in enumerate(enemies):
                    enemy_row, enemy_col = enemy[0], enemy[1]
                    # Check if enemy is within 2 cells of the trap
                    if abs(enemy_row - row) + abs(enemy_col - col) <= 2:
                        enemy_freeze_times[i] = current_time
                        print(f"Enemy {i} frozen at time {current_time}")  # Debug print

    # --- Camera Zoom In/Out ---
    if key == '+' or key == '=':
        dx = camera_look_at[0] - camera_pos[0]
        dy = camera_look_at[1] - camera_pos[1]
        dz = camera_look_at[2] - camera_pos[2]
        length = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
        if length > 0:
            dx, dy, dz = dx / length * 100, dy / length * 100, dz / length * 100
            camera_pos = (camera_pos[0] + dx, camera_pos[1] + dy, camera_pos[2] + dz)

    if key == '-' or key == '_':
        dx = camera_look_at[0] - camera_pos[0]
        dy = camera_look_at[1] - camera_pos[1]
        dz = camera_look_at[2] - camera_pos[2]
        length = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
        if length > 0:
            dx, dy, dz = dx / length * 100, dy / length * 100, dz / length * 100
            camera_pos = (camera_pos[0] - dx, camera_pos[1] - dy, camera_pos[2] - dz)

    # --- Camera Presets ---
    if key == 'r' or key == 'R':
        camera_pos = (0, 4800, 4800)
        camera_look_at = (0, 0, 0)
    if key == '1':
        camera_pos = (0, 2400, 5200)
        camera_look_at = (0, 0, 0)
    if key == '2':
        camera_pos = (5200, 2400, 0)
        camera_look_at = (0, 0, 0)
    if key == '3':
        camera_pos = (3600, 3000, 3600)
        camera_look_at = (0, 0, 0)
    if key == '4':
        camera_pos = (1800, 5200, 1800)
        camera_look_at = (0, 0, 0)
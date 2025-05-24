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

def initialize_enemies():
    """Find all enemies in the maze and initialize their data"""
    global enemies, enemy_rotations, enemy_freeze_times
    enemies = []
    enemy_rotations = []
    enemy_freeze_times = []  # Initialize as empty list

    current_time = get_elapsed_time()

    maze = mazes[current_level]
    if not maze:  # Safety check
        return
        
    if current_level == 2:  # Level 3 (Boss Fight)
        # Add a single boss enemy at the center of the arena
        boss_row = len(maze) // 2
        boss_col = len(maze[0]) // 2
        boss_health = 10  # Boss health
        enemies.append([boss_row, boss_col, 0, 0, current_time, boss_health])  # Add health as the last parameter
        enemy_rotations.append(0.0)  # Initial rotation angle
        enemy_freeze_times.append(0)  # Not frozen
        return

    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 5:
                # Check if this enemy has valid movement options
                has_valid_move = False
                for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:  # Check in all 4 directions
                    nr, nc = row + dr, col + dc
                    if (0 <= nr < len(maze) and
                            0 <= nc < len(maze[0]) and
                            maze[nr][nc] == 0):
                        has_valid_move = True
                        break

                # Store the direction that leads to an open cell if possible
                if has_valid_move:
                    # Find a valid direction to start with
                    valid_directions = []
                    for d, (dr, dc) in enumerate([(-1, 0), (0, 1), (1, 0), (0, -1)]):
                        nr, nc = row + dr, col + dc
                        if (0 <= nr < len(maze) and
                                0 <= nc < len(maze[0]) and
                                maze[nr][nc] == 0):
                            valid_directions.append(d)

                    direction = random.choice(valid_directions) if valid_directions else random.randint(0, 3)
                else:
                    direction = random.randint(0, 3)

                enemies.append([row, col, direction, 0, current_time])  # Added last shot time
                enemy_rotations.append(0.0)  # Initial rotation angle
                enemy_freeze_times.append(0)  # Not frozen
                # Replace enemy marker with floor in the maze
                maze[row][col] = 0

    # Initialize enemy_freeze_times with 0 for each enemy
    enemy_freeze_times = [0] * len(enemies)


def is_player_in_line_of_sight(enemy_row, enemy_col):
    """Check if player is in direct line of sight (same row or column) with no walls in between"""
    if cloak_active:
        return False
    player_row, player_col = player_pos
    maze = mazes[current_level]

    # Convert positions to integers for range function
    enemy_row = int(enemy_row)
    enemy_col = int(enemy_col)
    player_row = int(player_row)
    player_col = int(player_col)

    # Same row
    if enemy_row == player_row:
        start_col = min(enemy_col, player_col)
        end_col = max(enemy_col, player_col)
        # Check all cells between enemy and player for walls
        for col in range(start_col + 1, end_col):
            if maze[enemy_row][col] == 1:  # Wall
                return False
        return True

    # Same column
    if enemy_col == player_col:
        start_row = min(enemy_row, player_row)
        end_row = max(enemy_row, player_row)
        # Check all cells between enemy and player for walls
        for row in range(start_row + 1, end_row):
            if maze[row][enemy_col] == 1:  # Wall
                return False
        return True

    return False


def update_enemies():
    """Move enemies and handle shooting"""
    global enemies, bullets, enemy_rotations, freeze_trap_positions, player_last_hit_time, player_health, game_over, enemy_freeze_times
    if not enemies or not enemy_rotations or not enemy_freeze_times:  # Safety check
        return
        
    current_time = get_elapsed_time()
    maze = mazes[current_level]
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(maze) * wall_size // 2

    # Initialize enemy dimensions if not set
    global body_radius, gun_length
    if body_radius is None or gun_length is None:
        body_radius = wall_size / 3  # Red sphere
        gun_length = wall_size / 2  # Grey gun cylinder

    for i, enemy in enumerate(enemies):
        if not enemy or len(enemy) < 5:  # Check if enemy data is valid
            continue
            
        row, col, direction, last_move_time, last_shot_time, *health = enemy
        is_boss = len(health) > 0  # Check if this is the boss
        health = health[0] if is_boss else None

        # Check if enemy is on a freeze trap
        if freeze_trap_positions:
            for trap_index, trap_pos in enumerate(freeze_trap_positions):
                if trap_pos[0] == row and trap_pos[1] == col:
                    if i < len(enemy_freeze_times):  # Safety check
                        enemy_freeze_times[i] = current_time
                        print(f"Enemy {i} stepped on freeze trap at time {current_time}")  # Debug print
                        # Remove the trap after it's triggered
                        freeze_trap_positions.pop(trap_index)
                        break

        # Check if the enemy is frozen
        is_frozen = False
        if i < len(enemy_freeze_times):
            if enemy_freeze_times[i] > 0:  # Enemy was previously frozen
                time_since_frozen = current_time - enemy_freeze_times[i]

                if cheat_mode:
                    is_frozen = True  # Enemies remain frozen indefinitely in cheat mode
                elif time_since_frozen < FREEZE_DURATION:
                    is_frozen = True  # Freeze duration not expired
                else:
                    # Reset freeze time when duration expires
                    enemy_freeze_times[i] = 0

        if is_frozen:
            # Enemy is frozen - rotate more slowly and don't shoot or move
            enemy_rotations[i] = (enemy_rotations[i] + ENEMY_ROTATION_SPEED * 0.2) % 360
            continue

        # Boss logic
        if is_boss:
            # Rotate the boss
            enemy_rotations[i] = (enemy_rotations[i] + ENEMY_ROTATION_SPEED) % 360
            player_row, player_col = player_pos
            boss_x, boss_z = col, row
            player_x, player_z = player_col, player_row

            # Only move toward player if not cloaked
            if not cloak_active:
                dx = player_x - boss_x
                dz = player_z - boss_z
                distance = max(1, (dx ** 2 + dz ** 2) ** 0.5)  # Avoid division by zero
                dx /= distance
                dz /= distance

                # Move the boss slightly toward the player
                move_speed = BOSS_MOVE_SPEED  # Use boss-specific movement speed
                new_row = boss_z + dz * move_speed
                new_col = boss_x + dx * move_speed

                # Check if new position has a freeze trap
                new_row_int = int(round(new_row))
                new_col_int = int(round(new_col))
                for trap_index, trap_pos in enumerate(freeze_trap_positions):
                    if trap_pos[0] == new_row_int and trap_pos[1] == new_col_int:
                        enemy_freeze_times[i] = current_time
                        print(f"Boss about to step on freeze trap at time {current_time}")  # Debug print
                        # Remove the trap after it's triggered
                        freeze_trap_positions.pop(trap_index)
                        continue

                # Update boss position
                enemies[i][0] = new_row
                enemies[i][1] = new_col

            # Only skip shooting if cloaked
            if cloak_active:
                continue

            # Boss continuously fires at player if not cloaked
            if current_time - last_shot_time > ENEMY_FIRE_INTERVAL:
                enemy_x = col * wall_size - offset + wall_size / 2
                enemy_z = row * wall_size - offset + wall_size / 2
                enemy_y = 200  # Boss height

                # Calculate direction to player
                player_row, player_col = player_pos
                player_x = player_col * wall_size - offset + wall_size / 2
                player_z = player_row * wall_size - offset + wall_size / 2
                
                # Calculate direction vector
                dx = player_x - enemy_x
                dz = player_z - enemy_z
                distance = max(1, (dx ** 2 + dz ** 2) ** 0.5)  # Avoid division by zero
                dx /= distance
                dz /= distance

                # Create bullet with direction towards player using boss bullet speed
                bullets.append([enemy_x, enemy_y, enemy_z, dx * BOSS_BULLET_SPEED, 0, dz * BOSS_BULLET_SPEED, current_time, False])
                enemies[i][4] = current_time  # Update last shot time
            continue

        # Regular enemy logic
        # Rotate the enemy
        enemy_rotations[i] = (enemy_rotations[i] + ENEMY_ROTATION_SPEED) % 360

        # Check if player is in line of sight for shooting (skip if cloaked)
        player_in_sight = not cloak_active and is_player_in_line_of_sight(row, col)
        
        if player_in_sight:
            # Calculate direction to player
            player_row, player_col = player_pos
            if row == player_row:  # Same row
                new_direction = 1 if player_col > col else 3  # East or West
            elif col == player_col:  # Same column
                new_direction = 2 if player_row > row else 0  # South or North
            else:
                # If not in direct line, move towards player's row or column
                if abs(player_row - row) > abs(player_col - col):
                    new_direction = 2 if player_row > row else 0  # Move vertically
                else:
                    new_direction = 1 if player_col > col else 3  # Move horizontally
            
            # Update enemy direction
            enemies[i][2] = new_direction

            # Only move if enough time has passed since last move
            if current_time - last_move_time >= ENEMY_MOVE_INTERVAL:
                # Try to move in the new direction
                new_row, new_col = row, col
                if new_direction == 0:  # North
                    new_row -= 1
                elif new_direction == 1:  # East
                    new_col += 1
                elif new_direction == 2:  # South
                    new_row += 1
                elif new_direction == 3:  # West
                    new_col -= 1

                # Check if new position is valid
                if (0 <= new_row < len(maze) and
                        0 <= new_col < len(maze[0]) and
                        (maze[new_row][new_col] == 0 or maze[new_row][new_col] == 3)):
                    # Valid move, update position
                    enemies[i][0] = new_row
                    enemies[i][1] = new_col
                    enemies[i][3] = current_time  # Update last move time

                    # Check for collision with player
                    if abs(new_row - player_row) < 0.5 and abs(new_col - player_col) < 0.5:
                        if not cheat_mode and current_time - player_last_hit_time > PLAYER_INVINCIBILITY_TIME:
                            player_health -= 1  # Decrease health by 1 when colliding with boss
                            player_last_hit_time = current_time
                            if player_health <= 0:
                                game_over = True
                                player_health = 0

                    # Check if enemy stepped on a freeze trap
                    if [new_row, new_col] in freeze_trap_positions:
                        enemy_freeze_times[i] = current_time

            # Shoot at player if in line of sight
            if current_time - last_shot_time > ENEMY_FIRE_INTERVAL:
                # Calculate enemy position
                enemy_x = col * wall_size - offset + wall_size / 2
                enemy_z = row * wall_size - offset + wall_size / 2
                enemy_y = 200 + 20 * math.sin(current_time * 0.003)

                # Calculate bullet direction
                if row == player_row:  # Same row
                    direction_x = 1 if player_col > col else -1
                    direction_z = 0
                    gun_idx = 1 if direction_x > 0 else 3
                elif col == player_col:  # Same column
                    direction_x = 0
                    direction_z = 1 if player_row > row else -1
                    gun_idx = 2 if direction_z > 0 else 0

                # Get the gun position
                dx, dy, dz = gun_offsets[gun_idx]
                start_x = enemy_x + dx * (body_radius + gun_length)
                start_y = enemy_y
                start_z = enemy_z + dz * (body_radius + gun_length)

                # Create bullet
                bullet_dx = direction_x * BULLET_SPEED
                bullet_dz = direction_z * BULLET_SPEED
                bullets.append([start_x, start_y, start_z, bullet_dx, 0, bullet_dz, current_time, False])
                enemies[i][4] = current_time

        else:
            # Not in line of sight or cloaked, use normal patrol movement
            if current_time - last_move_time < ENEMY_MOVE_INTERVAL:
                continue

            # Try to move in current direction
            new_row, new_col = row, col
            if direction == 0:  # North
                new_row -= 1
            elif direction == 1:  # East
                new_col += 1
            elif direction == 2:  # South
                new_row += 1
            elif direction == 3:  # West
                new_col -= 1

            # Check if new position is valid
            if (0 <= new_row < len(maze) and
                    0 <= new_col < len(maze[0]) and
                    (maze[new_row][new_col] == 0 or maze[new_row][new_col] == 3)):
                # Valid move, update position
                enemies[i][0] = new_row
                enemies[i][1] = new_col
                enemies[i][3] = current_time  # Update last move time

                # Check for collision with player
                player_row, player_col = player_pos
                if abs(new_row - player_row) < 0.5 and abs(new_col - player_col) < 0.5:
                    if not cheat_mode and current_time - player_last_hit_time > PLAYER_INVINCIBILITY_TIME:
                        player_health -= 1
                        player_last_hit_time = current_time
                        if player_health <= 0:
                            game_over = True
                            player_health = 0

                # Check if enemy stepped on a freeze trap
                if [new_row, new_col] in freeze_trap_positions:
                    enemy_freeze_times[i] = current_time
            else:
                # Blocked, try turning around
                opposite_dir = (direction + 2) % 4
                test_row, test_col = row, col

                if opposite_dir == 0:  # North
                    test_row -= 1
                elif opposite_dir == 1:  # East
                    test_col += 1
                elif opposite_dir == 2:  # South
                    test_row += 1
                elif opposite_dir == 3:  # West
                    test_col -= 1

                # Check if we can move in the opposite direction
                if (0 <= test_row < len(maze) and
                        0 <= test_col < len(maze[0]) and
                        (maze[test_row][test_col] == 0 or maze[test_row][test_col] == 3)):
                    # Can move in opposite direction
                    enemies[i][0] = test_row
                    enemies[i][1] = test_col
                    enemies[i][2] = opposite_dir
                    enemies[i][3] = current_time  # Update last move time

                    # Check if enemy stepped on a freeze trap
                    if [test_row, test_col] in freeze_trap_positions:
                        enemy_freeze_times[i] = current_time
                else:
                    # Can't backtrack, try other directions
                    for offset in [1, 3, 2]:  # Try right, left, then opposite
                        test_dir = (direction + offset) % 4
                        test_row, test_col = row, col

                        if test_dir == 0:  # North
                            test_row -= 1
                        elif test_dir == 1:  # East
                            test_col += 1
                        elif test_dir == 2:  # South
                            test_row += 1
                        elif test_dir == 3:  # West
                            test_col -= 1

                        if (0 <= test_row < len(maze) and
                                0 <= test_col < len(maze[0]) and
                                (maze[test_row][test_col] == 0 or maze[test_row][test_col] == 3)):
                            # Found another valid direction
                            enemies[i][0] = test_row
                            enemies[i][1] = test_col
                            enemies[i][2] = test_dir
                            enemies[i][3] = current_time  # Update last move time

                            # Check if enemy stepped on a freeze trap
                            if [test_row, test_col] in freeze_trap_positions:
                                enemy_freeze_times[i] = current_time
                            break

        # Update move timer
        enemies[i][3] = current_time

def update_bullets():
    """Update position of all bullets and check collisions"""
    update_player_bullets()
    update_enemy_bullets()


def update_player_bullets():
    """Update player bullets and check for enemy hits."""
    global player_bullets, enemies, enemy_rotations, enemy_freeze_times
    current_time = get_elapsed_time()
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[current_level]) * wall_size // 2

    new_bullets = []
    maze = mazes[current_level]

    for bullet in player_bullets:
        x, y, z, dx, dy, dz, creation_time = bullet

        # Update position
        x += dx
        y += dy
        z += dz

        # Convert to maze coordinates
        col = int((x + offset) / wall_size)
        row = int((z + offset) / wall_size)

        # Check if out of bounds or hit wall
        if (row < 0 or row >= len(maze) or
                col < 0 or col >= len(maze[0]) or
                maze[row][col] == 1):
            continue  # Skip this bullet

        # Check if bullet lifetime expired
        if current_time - creation_time > BULLET_LIFETIME:
            continue  # Skip this bullet

        # Check for enemy hit
        enemy_hit = False
        for i, enemy in enumerate(enemies):
            enemy_row, enemy_col = enemy[0], enemy[1]
            is_boss = len(enemy) > 5  # Check if this is the boss
            enemy_x = enemy_col * wall_size - offset + wall_size / 2
            enemy_z = enemy_row * wall_size - offset + wall_size / 2
            enemy_y = 200 if is_boss else 150  # Boss is taller

            # Calculate distance to enemy
            if ((enemy_x - x) ** 2 + (enemy_z - z) ** 2 < (wall_size / 3) ** 2 and
                    abs(y - enemy_y) < wall_size / 2):
                if is_boss:
                    enemies[i][5] -= 1  # Decrease boss health
                    if enemies[i][5] <= 0:
                        enemies.pop(i)  # Remove boss when health is zero
                        enemy_rotations.pop(i)
                        enemy_freeze_times.pop(i)
                        print("Boss defeated!")
                else:
                    enemies.pop(i)  # Regular enemy dies instantly
                    enemy_rotations.pop(i)
                    enemy_freeze_times.pop(i)
                enemy_hit = True
                break

        if enemy_hit:
            continue  # Skip this bullet

        # Bullet still active, keep it
        new_bullets.append([x, y, z, dx, dy, dz, creation_time])

    player_bullets = new_bullets


def update_enemy_bullets():
    """Update enemy bullets and check for player hits"""
    global bullets, player_health, player_last_hit_time, game_over
    current_time = get_elapsed_time()
    wall_size = GRID_LENGTH * 2 // 15
    offset = len(mazes[current_level]) * wall_size // 2

    new_bullets = []
    maze = mazes[current_level]

    for bullet in bullets:
        x, y, z, dx, dy, dz, creation_time, is_player_bullet = bullet

        # Update position
        x += dx
        y += dy
        z += dz

        # Convert to maze coordinates
        col = int((x + offset) / wall_size)
        row = int((z + offset) / wall_size)

        # Check if out of bounds or hit wall
        if (row < 0 or row >= len(maze) or
                col < 0 or col >= len(maze[0]) or
                maze[row][col] == 1):
            continue  # Skip this bullet

        # Check if bullet lifetime expired
        if current_time - creation_time > BULLET_LIFETIME:
            continue  # Skip this bullet

        # Check for player hit
        player_row, player_col = player_pos
        player_x = player_col * wall_size - offset + wall_size / 2
        player_z = player_row * wall_size - offset + wall_size / 2
        player_y = 150  # Approximate player height

        if ((player_x - x) ** 2 + (player_z - z) ** 2 < (wall_size / 3) ** 2 and
                abs(y - player_y) < wall_size / 2):
            # Player hit logic
            if not cheat_mode and current_time - player_last_hit_time > PLAYER_INVINCIBILITY_TIME:
                player_health -= 1  # Decrease health by 5 when hit
                player_last_hit_time = current_time
                if player_health <= 0:
                    game_over = True
                    player_health = 0
            continue  # Skip this bullet

        # Bullet still active, keep it
        new_bullets.append([x, y, z, dx, dy, dz, creation_time, is_player_bullet])

    bullets = new_bullets


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


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


def draw_enemies():
    """Draw all enemies at their current positions"""
    if not enemies:  # Check if enemies list is empty
        return
        
    wall_size = GRID_LENGTH * 2 // 15
    maze = mazes[current_level]
    offset = len(maze) * wall_size // 2

    for i, enemy in enumerate(enemies):
        if not enemy or len(enemy) < 3:  # Check if enemy data is valid
            continue
            
        row, col, direction = enemy[0], enemy[1], enemy[2]
        # Calculate center position of this cell
        x = col * wall_size - offset + wall_size / 2
        z = row * wall_size - offset + wall_size / 2

        # More pronounced hovering and bobbing effect
        current_time = get_elapsed_time() % 2000
        height_offset = 200 + 20 * math.sin(current_time * 0.003)

        # Get rotation angle for this enemy
        rotation_angle = enemy_rotations[i] if i < len(enemy_rotations) else 0.0

        # Draw enemy with rotation
        draw_enemy(x, height_offset, z, rotation_angle, i)

        # Draw shadow beneath enemy
        glPushMatrix()
        glTranslatef(x, 11.0, z)  # Just above floor
        glColor4f(0.0, 0.0, 0.0, 0.5)  # Semi-transparent black
        glScalef(1.0, 0.1, 1.0)  # Flatten to make a shadow
        glutSolidSphere(wall_size / 3, 12, 8)
        glPopMatrix()

def draw_enemy(x, y, z, rotation_angle, i):
    """Draw an enemy at the specified position with rotating guns"""
    global body_radius, gun_length, enemy_freeze_times
    if not enemy_freeze_times or i >= len(enemy_freeze_times):  # Safety check
        return
        
    current_time = get_elapsed_time()
    is_frozen = enemy_freeze_times[i] > 0 and (cheat_mode or current_time - enemy_freeze_times[i] < FREEZE_DURATION)
    wall_size = GRID_LENGTH * 2 // 15

    # Check if this is the boss (level 3)
    is_boss = current_level == 2 and enemies and len(enemies) > 0 and len(enemies[0]) > 5

    # Increase size for better visibility, make boss bigger
    if is_boss:
        body_radius = wall_size / 1.5  # Much larger red sphere for boss
        head_radius = wall_size / 3  # Larger black sphere for boss
        gun_radius = wall_size / 8  # Larger grey gun cylinder for boss
        gun_length = wall_size  # Longer guns for boss
    else:
        body_radius = wall_size / 3  # Normal size for regular enemies
        head_radius = wall_size / 5
        gun_radius = wall_size / 14
        gun_length = wall_size / 2

    glPushMatrix()
    glTranslatef(x, y, z)  # Apply the position

    # Apply rotation for spinning effect
    glRotatef(rotation_angle, 0, 1, 0)

    quadric = gluNewQuadric()
    if not quadric:  # Safety check for quadric
        glPopMatrix()
        return

    # Body (red sphere)
    glColor3f(0.9, 0.1, 0.1)  # Bright red
    glutSolidSphere(body_radius, 16, 16)

    # Head (black sphere) on top of body
    glPushMatrix()
    glTranslatef(0, body_radius + head_radius * 0.5, 0)
    glColor3f(0.1, 0.1, 0.1)  # Black
    glutSolidSphere(head_radius, 16, 16)
    glPopMatrix()

    # Guns (grey cylinders) attached to all four sides of body
    glColor3f(0.5, 0.5, 0.5)  # Grey

    # Gun on right side (+X)
    glPushMatrix()
    glTranslatef(body_radius * 0.5, 0, 0)
    glRotatef(90, 0, 1, 0)  # Rotate to point right (+X)
    gluCylinder(quadric, gun_radius, gun_radius, gun_length, 12, 2)
    glPopMatrix()

    # Gun on left side (-X)
    glPushMatrix()
    glTranslatef(-body_radius * 0.5, 0, 0)
    glRotatef(-90, 0, 1, 0)  # Rotate to point left (-X)
    gluCylinder(quadric, gun_radius, gun_radius, gun_length, 12, 2)
    glPopMatrix()

    # Gun on front side (+Z)
    glPushMatrix()
    glTranslatef(0, 0, body_radius * 0.5)
    glRotatef(0, 0, 1, 0)  # Rotate to point forward (+Z)
    gluCylinder(quadric, gun_radius, gun_radius, gun_length, 12, 2)
    glPopMatrix()

    # Gun on back side (-Z)
    glPushMatrix()
    glTranslatef(0, 0, -body_radius * 0.5)
    glRotatef(180, 0, 1, 0)  # Rotate to point backward (-Z)
    gluCylinder(quadric, gun_radius, gun_radius, gun_length, 12, 2)
    glPopMatrix()

    if is_frozen:
        glColor4f(0.2, 0.7, 1.0, 0.6)  # Ice blue
        glutSolidSphere(body_radius * 1.2, 12, 12)

        # Draw ice crystals on the enemy
        for j in range(4):
            angle = j * 90
            glPushMatrix()
            glRotatef(angle, 0, 1, 0)
            glTranslatef(body_radius * 0.8, 0, 0)
            glColor4f(0.5, 0.8, 1.0, 0.8)
            glutSolidCone(body_radius * 0.3, body_radius * 0.6, 6, 3)
            glPopMatrix()
    glPopMatrix()


def draw_bullets():
    """Draw all active bullets"""
    wall_size = GRID_LENGTH * 2 // 15
    bullet_size = wall_size / 15

    # Draw enemy bullets (red cubes)
    for bullet in bullets:
        x, y, z = bullet[0], bullet[1], bullet[2]
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.0, 0.0)  # Bright red for enemy bullets
        glutSolidCube(bullet_size)
        glPopMatrix()

    # Draw player bullets (blue spheres)
    for bullet in player_bullets:
        x, y, z = bullet[0], bullet[1], bullet[2]
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.0, 0.5, 1.0)  # Blue for player bullets
        glutSolidSphere(bullet_size * 0.8, 8, 8)  # Use sphere for player bullets
        glPopMatrix()

def draw_freeze_traps():
    """Draw freeze traps on the maze and deployed freeze traps"""
    global freeze_trap_positions

    wall_size = GRID_LENGTH * 2 // 15
    maze = mazes[current_level]
    offset = len(maze) * wall_size // 2

    # Draw freeze traps in the maze (as cuboids above the floor)
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 6:
                x = col * wall_size - offset + wall_size / 2
                z = row * wall_size - offset + wall_size / 2

                # Draw floor under the freeze trap
                glBegin(GL_QUADS)
                glColor3f(0.1, 0.6, 0.1)  # Green floor
                glVertex3f(x - wall_size / 2, 10.0, z - wall_size / 2)
                glVertex3f(x + wall_size / 2, 10.0, z - wall_size / 2)
                glVertex3f(x + wall_size / 2, 10.0, z + wall_size / 2)
                glVertex3f(x - wall_size / 2, 10.0, z + wall_size / 2)
                glEnd()

                # Draw animated freeze trap as a cuboid above the floor
                glPushMatrix()
                current_time = get_elapsed_time() % 800
                height_offset = 40 + 15 * abs(current_time - 400) / 400
                glTranslatef(x, height_offset, z)

                # Freeze trap - blue crystal-like cube
                glColor4f(0.2, 0.6, 1.0, 0.8)  # Light blue, slightly transparent
                glutSolidCube(wall_size / 3)  # Smaller cube

                # Glowing effect
                glPushMatrix()
                current_time = get_elapsed_time() % 1000
                pulse = 0.3 + 0.2 * abs(current_time - 500) / 500
                glScalef(1.3, 1.3, 1.3)
                glColor4f(0.2, 0.7, 1.0, pulse)  # Pulsing glow
                glutSolidOctahedron()
                glPopMatrix()

                glPopMatrix()

    # Draw deployed freeze traps
    for pos in freeze_trap_positions:
        row, col = pos
        x = col * wall_size - offset + wall_size / 2
        z = row * wall_size - offset + wall_size / 2

        # Draw freeze effect on the ground
        glPushMatrix()
        glTranslatef(x, 11, z)  # Just above floor
        glColor4f(0.2, 0.7, 1.0, 0.5)  # Semi-transparent blue
        glScalef(1.0, 0.1, 1.0)  # Flatten
        glutSolidSphere(wall_size / 2, 16, 8)  # Ice patch
        glPopMatrix()


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


def draw_coins():
    """Draw all coins that haven't been collected yet."""
    if not coin_positions:  # Safety check for empty coin positions
        return
        
    wall_size = GRID_LENGTH * 2 // 15
    current_time = get_elapsed_time() % 1000
    height_offset = 30 + 10 * abs(current_time - 500) / 500
    scale = 0.5 + 0.3 * abs(current_time - 500) / 500

    # Debug print
    print(f"Drawing coins for level {current_level + 1}. Total positions: {len(coin_positions)}, Collected: {len(collected_coins[current_level]) if current_level < len(collected_coins) else 0}")

    for i, (x, z) in enumerate(coin_positions):
        if current_level >= len(collected_coins) or i in collected_coins[current_level]:
            continue  # Skip if level not in collected_coins or coin already collected

        glPushMatrix()
        glTranslatef(x, height_offset, z)
        glScalef(scale, scale, scale)
        glColor3f(1.0, 0.0, 0.0)  # Red color
        glutSolidSphere(wall_size / 3, 16, 16)
        glPopMatrix()

def keyboardListener(key, x, y):
    global camera_pos, camera_look_at, player_pos, player_angle, view_mode, freeze_traps_collected, selected_item, freeze_trap_positions, enemy_freeze_times, action_mode, bullet_limit, bullets_fired, cheat_mode, BULLET_SPEED, wall_phasing, game_paused, game_state
    global key_collected, cloak_collected, cloak_active, cloak_start_time, collected_coins, player_health, game_over, player_last_hit_time, enemies, bullets, player_bullets, player_immobilized, player_immobilize_time, current_level, mazes, fifty_coin_bonus_given, hundred_coin_bonus_given

    key = key.decode('utf-8') if isinstance(key, bytes) else chr(key)

    # Handle ESC key to return to menu
    if key == '\x1b':  # ESC key
        game_state = "menu"
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
        selected_item = ""
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
        selected_item = ""
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
            (wall_phasing or maze[next_row][next_col] in [0, 2, 3, 4, 6, 7, 8, 9])):  # Valid moves: empty, key, exit, freeze trap
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


def specialKeyListener(key, x, y):
    global camera_pos, camera_look_at, camera_angle

    # Arrow keys control camera rotation (left/right) and elevation (up/down)
    if key == GLUT_KEY_LEFT:
        # Rotate camera left around the center point - smoothed rotation
        camera_angle -= 0.03  # Smaller angle for smoother rotation
        updateCameraPosition()

    if key == GLUT_KEY_RIGHT:
        # Rotate camera right around the center point - smoothed rotation
        camera_angle += 0.03  # Smaller angle for smoother rotation
        updateCameraPosition()

    if key == GLUT_KEY_UP:
        # Move camera position up (increase y-coordinate)
        camera_pos = (camera_pos[0], camera_pos[1] + 100, camera_pos[2])

    if key == GLUT_KEY_DOWN:
        # Move camera position down (decrease y-coordinate), with a minimum height
        new_y = max(400, camera_pos[1] - 100)  # Don't go below height of 400
        camera_pos = (camera_pos[0], new_y, camera_pos[2])


def updateCameraPosition():
    """Update camera x,z position based on current angle while maintaining height"""
    global camera_pos, camera_look_at, camera_angle

    # Calculate distance from center to camera (in xz plane)
    dx = camera_pos[0] - camera_look_at[0]
    dz = camera_pos[2] - camera_look_at[2]
    radius = math.sqrt(dx ** 2 + dz ** 2)

    # Calculate new camera position based on angle
    new_x = camera_look_at[0] + radius * math.sin(camera_angle)
    new_z = camera_look_at[2] + radius * math.cos(camera_angle)

    # Update camera position, keeping y coordinate the same
    camera_pos = (new_x, camera_pos[1], new_z)


def mouseListener(button, state, x, y):
    global view_mode, mouse_left_down, game_state, show_instructions
    
    # Convert y coordinate to OpenGL coordinate system
    y = 800 - y
    
    if game_state == "menu":
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            if show_instructions:
                # Check if back button is clicked
                bx, by = 400, 150
                bw, bh = 200, 50
                if (bx <= x <= bx + bw and by <= y <= by + bh):
                    show_instructions = False
                    return
            else:
                # Check if start button is clicked
                bx, by, bw, bh = menu_button_rect
                if (bx <= x <= bx + bw and by <= y <= by + bh):
                    game_state = "playing"
                    return
                
                # Check if instructions button is clicked
                bx, by, bw, bh = instructions_button_rect
                if (bx <= x <= bx + bw and by <= y <= by + bh):
                    show_instructions = True
                    return
                
                # Check if exit button is clicked
                bx, by, bw, bh = exit_button_rect
                if (bx <= x <= bx + bw and by <= y <= by + bh):
                    glutLeaveMainLoop()  # Exit the game
                    return
        return
    
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_left_down = True  # Start continuous shooting
            if not cheat_mode:
                player_shoot()  # Single shot for non-cheat mode
        elif state == GLUT_UP:
            mouse_left_down = False  # Stop continuous shooting

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Toggle view mode
        view_mode = "first_person" if view_mode == "overhead" else "overhead"


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if view_mode == "overhead":
        # Original overhead camera setup
        gluPerspective(fovY, 1.25, 10.0, 20000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        cx, cy, cz = camera_pos
        lx, ly, lz = camera_look_at
        gluLookAt(cx, cy, cz, lx, ly, lz, 0, 1, 0)
    else:  # First-person mode
        gluPerspective(90, 1.25, 1.0, 20000)  # Wider FOV for first person
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Calculate player's position in world coordinates
        wall_size = GRID_LENGTH * 2 // 15
        maze = mazes[current_level]
        offset = len(maze) * wall_size // 2
        player_row, player_col = player_pos

        # Player's feet position
        px = player_col * wall_size - offset + wall_size / 2
        pz = player_row * wall_size - offset + wall_size / 2
        py = 10.0  # Floor level

        # Eye position (on top of head)
        eye_height = wall_size * 2  # Approximately head height

        # Calculate look direction based on player angle
        corrected_angle = (360 - player_angle) % 360
        angle_rad = math.radians(corrected_angle)
        look_x = px + math.sin(angle_rad) * 100  # Look 100 units ahead
        look_z = pz - math.cos(angle_rad) * 100  # Negative because north is -z
        look_y = py + eye_height  # Maintain eye level while looking forward

        # Position camera at player's eye level
        gluLookAt(px, py + eye_height, pz,  # From (player's eye position)
                  look_x, look_y, look_z,  # To (point ahead based on angle)
                  0, 1, 0)  # Up vector


def idle():
    global cloak_active, cloak_start_time, cloak_duration
    global player_immobilized, player_immobilize_time, mouse_left_down, player_last_shot_time

    # Don't update game state if paused
    if game_paused:
        glutPostRedisplay()
        return

    update_delta_time()
    current_time = get_elapsed_time()

    # Handle cloak deactivation only when not in cheat mode
    if not cheat_mode and cloak_active and current_time - cloak_start_time > cloak_duration:
        cloak_active = False

    # Handle immobilization timeout
    if player_immobilized and current_time - player_immobilize_time > IMMOBILIZE_DURATION:
        player_immobilized = False

    # Continuous shooting in cheat mode
    if cheat_mode and mouse_left_down:
        if current_time - player_last_shot_time > PLAYER_FIRE_INTERVAL:
            player_shoot()

    update_enemies()  # Update enemy positions and handle shooting
    update_bullets()  # Update bullet positions
    glutPostRedisplay()

def draw_menu():
    """Draw the start menu screen"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    # Set up orthographic projection for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Draw title
    draw_text(350, 600, "3D Maze Escape: Hunter's Chase", GLUT_BITMAP_TIMES_ROMAN_24)
    
    if not show_instructions:
        # Draw start button
        x, y, w, h = menu_button_rect
        glColor3f(0.2, 0.6, 0.2)  # Green color for button
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        draw_text(x + 50, y + 15, "Start Game", GLUT_BITMAP_HELVETICA_18)
        
        # Draw instructions button
        x, y, w, h = instructions_button_rect
        glColor3f(0.2, 0.4, 0.8)  # Blue color for button
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        draw_text(x + 50, y + 15, "Instructions", GLUT_BITMAP_HELVETICA_18)
        
        # Draw exit button
        x, y, w, h = exit_button_rect
        glColor3f(0.8, 0.2, 0.2)  # Red color for button
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        draw_text(x + 70, y + 15, "Exit", GLUT_BITMAP_HELVETICA_18)
    else:
        # Draw instructions
        glColor3f(0.2, 0.4, 0.8)  # Blue background for instructions
        glBegin(GL_QUADS)
        glVertex2f(200, 100)
        glVertex2f(800, 100)
        glVertex2f(800, 700)
        glVertex2f(200, 700)
        glEnd()
        
        # Draw instructions text with adjusted spacing - starting lower
        draw_text(350, 600, "3D Maze Escape: Hunter's Chase", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(300, 550, "Controls:", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 520, "WASD - Move", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 490, "Mouse - Look around", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 460, "Left Click - Shoot", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 430, "Right Click - Toggle view", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 400, "E - Interact/Collect", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 370, "5,6,7 - Select items", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 340, "Space - Pause", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 310, "C - Toggle Cheat Mode", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 280, "V - Toggle Wall Phasing (Cheat Mode)", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 250, "ESC - Return to Menu", GLUT_BITMAP_HELVETICA_18)
        draw_text(300, 220, "R - Reset Camera View", GLUT_BITMAP_HELVETICA_18)
        
        # Draw back button
        x, y = 400, 150
        w, h = 200, 50
        glColor3f(0.2, 0.6, 0.2)  # Green color for button
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        draw_text(x + 70, y + 15, "Back", GLUT_BITMAP_HELVETICA_18)
    
    glutSwapBuffers()

def showScreen():
    global game_state
    
    if game_state == "menu":
        draw_menu()
        return
        
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

    # --- Main Floor (beneath everything) ---
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.45, 0.1)  # Darker grass green
    glVertex3f(-GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, 0, GRID_LENGTH)
    glEnd()

    # --- Game Over ---
    if game_over:
        if current_level == 2 and player_health > 0 and bullets_fired <= bullet_limit and key_collected and mazes[current_level][player_pos[0]][player_pos[1]] == 4:
            draw_text(400, 400, "YOU WIN!", GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(350, 350, "Congratulations on finishing the game!", GLUT_BITMAP_HELVETICA_18)
            draw_text(350, 300, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
        else:
            # Draw player lying down for game over
            wall_size = GRID_LENGTH * 2 // 15
            maze = mazes[current_level]
            offset = len(maze) * wall_size // 2
            row, col = player_pos
            x = col * wall_size - offset + wall_size / 2
            z = row * wall_size - offset + wall_size / 2
            
            glPushMatrix()
            glTranslatef(x, 10.0, z)
            glRotatef(90, 1, 0, 0)  # Rotate to lie down
            draw_player(0, 0, 0)
            glPopMatrix()
            
            draw_text(400, 400, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(350, 350, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
        glutSwapBuffers()
        return

    # --- Boundary Walls ---
    draw_boundary_walls()

    # --- Maze Walls, Floor, Key, Exit ---
    draw_maze()

    # --- Draw Enemies (separately after the maze) ---
    draw_enemies()
    draw_bullets()

    # --- Coins ---
    draw_coins()
    draw_freeze_traps()

    # --- UI Text ---
    # Calculate total coins safely
    total_coins = 0
    for coins in collected_coins:
        if coins is not None:  # Safety check
            total_coins += len(coins)
    
    # Calculate current level coins safely
    current_level_coins = 0
    if current_level < len(collected_coins) and collected_coins[current_level] is not None:
        current_level_coins = len(collected_coins[current_level])
    
    # Calculate total possible coins safely
    total_possible_coins = NUM_COINS * 2 if coin_positions else 0
    
    draw_text(10, 770, f"Level: {current_level + 1}")
    draw_text(10, 740, f"Health: {player_health}")
    draw_text(10, 710, f"Coins Collected: {total_coins} / {total_possible_coins}")
    draw_text(10, 680, f"Level Coins: {current_level_coins} / {len(coin_positions) if coin_positions else 0}")
    draw_text(10, 650, f"Key Collected: {'Yes' if key_collected else 'No'}")
    draw_text(10, 620, f"Freeze Traps: {freeze_traps_collected}")
    draw_text(10, 590, f"Bullets Used: {bullets_fired} / {bullet_limit}")
    
    # Show boss health only in level 3
    if current_level == 2 and enemies and len(enemies) > 0 and len(enemies[0]) > 5:  # Safety check
        boss_health = enemies[0][5]
        draw_text(10, 560, f"Boss Health: {boss_health}")
    
    if player_immobilized:
        remaining_time = (IMMOBILIZE_DURATION - (get_elapsed_time() - player_immobilize_time)) // 1000
        draw_text(400, 750, f"IMMOBILIZED! ({remaining_time}s)", GLUT_BITMAP_HELVETICA_18)
    
    # Cloak status
    if cloak_active:
        draw_text(10, 530, "Cloak Active: Yes")
        if not cheat_mode:
            remaining_time = (cloak_duration - (get_elapsed_time() - cloak_start_time)) // 1000
            draw_text(10, 500, f"Cloak Duration: {remaining_time}s")
    elif cloak_collected > 0:
        draw_text(10, 530, f"Cloak Collected: {cloak_collected}")
    else:
        draw_text(10, 530, "Cloak Collected: No")

    # Selected item and action mode
    if selected_item:
        draw_text(10, 470, f"Selected Item: {selected_item}")
    else:
        draw_text(10, 470, "No item selected")
    
    # Cheat mode status
    if cheat_mode:
        draw_text(10, 440, "CHEAT MODE ACTIVE", GLUT_BITMAP_HELVETICA_18)
        if wall_phasing:
            draw_text(10, 410, "WALL PHASING ACTIVE", GLUT_BITMAP_HELVETICA_18)

    # Add pause message to UI
    if game_paused:
        draw_text(400, 400, "GAME PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(350, 350, "Press SPACE to continue", GLUT_BITMAP_HELVETICA_18)

    glutSwapBuffers()


def main():
    global player_pos, game_state
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Maze Escape: Hunter's Chase")
    # Enhanced depth testing settings
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearDepth(1.0)

    # Initialize game state
    game_state = "menu"
    player_pos = find_player_start()
    # Set a nice background color for better contrast
    glClearColor(0.05, 0.05, 0.15, 1.0)  # Dark blue background
    initialize_enemies()
    generate_coin_positions()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
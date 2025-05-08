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
                bullets.append(
                    [enemy_x, enemy_y, enemy_z, dx * BOSS_BULLET_SPEED, 0, dz * BOSS_BULLET_SPEED, current_time, False])
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
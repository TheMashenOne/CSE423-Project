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


def draw_coins():
    """Draw all coins that haven't been collected yet."""
    if not coin_positions:  # Safety check for empty coin positions
        return

    wall_size = GRID_LENGTH * 2 // 15
    current_time = get_elapsed_time() % 1000
    height_offset = 30 + 10 * abs(current_time - 500) / 500
    scale = 0.5 + 0.3 * abs(current_time - 500) / 500

    # Debug print
    print(
        f"Drawing coins for level {current_level + 1}. Total positions: {len(coin_positions)}, Collected: {len(collected_coins[current_level]) if current_level < len(collected_coins) else 0}")

    for i, (x, z) in enumerate(coin_positions):
        if current_level >= len(collected_coins) or i in collected_coins[current_level]:
            continue  # Skip if level not in collected_coins or coin already collected

        glPushMatrix()
        glTranslatef(x, height_offset, z)
        glScalef(scale, scale, scale)
        glColor3f(1.0, 0.0, 0.0)  # Red color
        glutSolidSphere(wall_size / 3, 16, 16)
        glPopMatrix()

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
        if current_level == 2 and player_health > 0 and bullets_fired <= bullet_limit and key_collected and \
                mazes[current_level][player_pos[0]][player_pos[1]] == 4:
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

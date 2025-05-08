# CSE423-Project
3D Maze Escape: Hunter’s Chase – Tactical Survival

We are developing a 3D OpenGL-based maze survival game titled "3D Maze Escape: Hunter’s Chase". The game takes place inside a fully 3D-rendered maze environment, where the player must navigate through obstacles, collect keys, avoid enemies, and escape before the time runs out.

Core Objectives

Develop a playable 3D maze environment using OpenGL. Implement interactive gameplay elements: player movement, enemy AI, power-ups, and collectibles. Demonstrate understanding of graphics programming through lighting, collision, and camera systems. 

Key Features
1. 3D Maze Layout
Maze built using a 2D array logic
Rendered with 3D cubes and lighting. 
3 levels of maze. 

2. Player Mechanics
Third-person view and first person view
WASD-based movement with collision detection. W and S moves the player forward and backward towards the gun pointes. A and D rotates left and right. 

3. Enemies (AI)
Patrolling and chasing behaviors
Enemy detection and interaction system. They rotate and shoot when the player is in line of sight. 

4. Tactical Tools
Traps: Freeze enemies if stepped on for a few seconds. 
Stealth Cloak: Turns the player invisible for a few seconds
Gun : shoots up to a certain amount of bullet. 


5. Collectibles
Coins: For points or in-game upgrades
Keys: Required to unlock the exit and access to next levels. 


6. Progression & Objectives
Collect all keys and reach the exit
Avoid enemies or disable/kill them using tools
Use coins to upgrade guns or restore health. 
HUD shows all the progression and objectives. 

7. Environments

Trap Floors: Certain tiles collapse after stepping, causing a respawn.

Trap Rooms: Areas that temporarily lock the player in.

Camera positioning: Has 4 camera options and zoom in/zoom out.

8. Main Menu Screen

The game opens with a menu screen offering:

Start Game

Instructions

Exit


9. Win and Lose Conditions

Win: Collect all required keys and escape through the exit.

Lose: Run out of health or lose all bullets.

10. Cheat mode.
Pressing C activates it. 
While in cheat mode, if enemies are frozen, they freeze indefinitely. The Stealth cloak also remains indefinitely. Also in cheat mode, the player can consecutively shoot. Player health never decreases. Floor traps don't work. 
If we press V while in cheat mode, we can phase through the maze but not the environment. 


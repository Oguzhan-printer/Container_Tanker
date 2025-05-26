# Container Tanker 🚛💨

Welcome to **Container Tanker**! 🎮 This is a thrilling 2D tank shooter game built with Pygame, where you control a tank to eliminate moving targets with limited bullets. Navigate through levels, aim with precision, and achieve titles like "GO Developer" and "Kubernetes Architect"! 🏆

This README provides an overview of the game, explains its core functions, and includes a section for the story behind its creation. Let's dive in! 🌟

-Table of Contents-
- Game Overview
- Core Functions and Features
- Initialization and Setup
- Resource Loading
- UI Management
- Game Entities
- Animations and Effects
- Game State Management
- Main Game Loop
- Story
- How to Run
- Dependencies
- Contributing

## Game Overview 🎮

Container Tanker is a Pygame-based tank shooter where players control a tank that moves with WASD keys, aims with the mouse, and shoots bullets to hit moving targets. Each level has a set number of bullets and targets, with increasing difficulty. The game features:

- **Three levels** with unique themes (GO Developer, Docker Expert, Kubernetes Architect).
- **Dynamic UI** with buttons and a volume slider.
- **Visual effects** like starburst animations and collision particles.
- **Background video frames** for an immersive experience.
- **Sound effects** for shooting, collisions, and level completion.

The goal is to destroy all targets before running out of bullets, while avoiding collisions with targets. 🚨

## Core Functions and Features 🛠️

### Initialization and Setup ⚙️

- **Pygame Initialization**: The game starts by initializing Pygame and setting up a 1920x1080 window with a 120 FPS cap. 🎥
- **Game Settings**: Constants like `TANK_SPEED`, `BULLET_SPEED`, and `TARGET_SPEED` define movement dynamics. Colors like `WHITE`, `RED`, and `VIOLET` are used for visuals. 🌈
- **Global State (**`game`**)**: A dictionary tracks the game state (`menu`, `playing`, `end`, etc.), level, bullets, targets, and animations. 📊
- **Resources (**`res`**)**: Stores sounds, fonts, and images for reuse across the game. 🖼️
- **UI (**`ui`**)**: Manages buttons and sliders for user interaction. 🖱️
- **Level Configurations (**`level_configs`**)**: Defines bullet counts, target counts, and images for each level. 🏅

### Resource Loading 📦

- `load_resources()`: Loads sounds (`shoot.wav`, `collision.wav`, `win.wav`, `background.mp3`), fonts (`Agency FB`), and images (`go_logo.png`, `tank_body.png`, etc.). If files are missing, fallback surfaces with solid colors are used. 🎵🖼️
  - Scales images to appropriate sizes (e.g., 48x48 for logos, 16x16 for bullets).
  - Loads video frames from a directory for animated backgrounds.
  - Assigns images to `level_configs` for level-specific targets.

### UI Management 🖥️

- `create_ui()`: Creates buttons for the menu (`Start`, `Quit`), level end (`Next`, `Replay`, `Back to Menu`), game over (`Retry`, `Back to Menu`), and final level (`Restart`, `Back to Menu`). Also sets up a volume slider. 🖲️
- `draw_button()`: Renders buttons with hover effects (changes text color to `LIGHT_YELLOW` when hovered). 🖌️
- `draw_slider()` and `update_slider()`: Manages the volume slider, allowing players to adjust sound levels by dragging. 🔊

### Game Entities 🎯

- **Tank**:
  - `create_tank(x, y)`: Initializes a tank with a body, turret, position, and angle. Tracks previous positions for drawing tracks. 🛡️
  - `update_tank(tank, keys, mouse_pos)`: Updates tank movement (WASD/Arrow keys) and turret aiming (mouse position). Rotates the tank body and clamps position within screen bounds. 🚜
  - `draw_tank(tank, surface)`: Draws tank tracks, body, and rotated turret. 🖼️
  - `shoot_tank(tank)`: Creates a bullet with velocity based on the turret angle, applies recoil, and plays a shoot sound. 💥
- **Bullet**:
  - `update_bullet(bullet)`: Moves bullets and checks if they're within bounds or past their lifetime (`BULLET_LIFETIME`). 🕒
  - `draw_bullet(bullet, surface)`: Draws rotated bullet images. At the same time, during the shell explosion, a recoil animation enters and the tank recoils a little. 🔫
- **Target**:
  - `create_target(x, y, image)`: Spawns a target with a random velocity and level-specific image. 🎯
  - `update_target(target)`: Moves targets, bounces them off screen edges, and clamps their position. 🏃‍♂️

### Animations and Effects ✨

- **Starburst Animation**:
  - `create_starburst_animation(text, x, y, duration, particle_count, is_celebration)`: Creates a particle-based animation with text (e.g., "Level 1 Starting!"). Uses colorful particles for celebrations (e.g., level completion). 🌟
  - `update_starburst_animation(animation)`: Updates particle positions and fades them out over time. ⏳
  - `draw_starburst_animation(animation, surface)`: Draws the text and particles with fading alpha. 🎇
- **Collision Effect**:
  - `create_collision_effect(x, y)`: Generates orange particles at collision points. 🔥
  - `update_collision_effect(effect)`: Updates particle positions, slows them down, and fades them out. 🌫️
  - `draw_collision_effect(effect, surface)`: Draws particles with transparency. 🖌️

### Game State Management 🎲

- `reset_to_menu()`: Resets the game to the menu state, clearing bullets, targets, and effects. 🏠
- `update_background_frame()`: Cycles through video frames for the background at `VIDEO_FPS`. 🎬
- `start_level()`: Initializes a level with the configured number of targets and bullets, starting with an animation. 🚀
- `handle_events()`: Processes mouse clicks, keyboard inputs, and quit events. Supports actions like starting the game, shooting, and navigating menus. 🖱️⌨️

### Main Game Loop 🔄

- `update_game()`: Updates the game state:
  - In `menu`, handles volume slider updates.
  - In `starting`, plays the start animation and transitions to `playing`.
  - In `playing`, updates tank, bullets, targets, effects, and animations. Checks for collisions and win/lose conditions. 🕹️
  - In `end` or `game_over`, updates effects and animations while waiting for user input. 🏁
- `draw_game()`: Renders the game:
  - Draws the background (video frames or a fallback gradient).
  - In `menu`, shows the title and buttons.
  - In `starting`, `end`, or `game_over`, draws animations and buttons.
  - In `playing`, draws the tank, bullets, targets, effects, animations, and HUD (bullets left, level number). 🖼️
- `main()`: Initializes resources, UI, and the tank, then runs the game loop at 120 FPS using `asyncio` for Pyodide compatibility. 🚀

## Story 📖

**Why I Created Container Tanker**\
My reason for creating the game. "I wanted to combine my passion for programming and gaming, inspired by containerization technologies like Docker and Kubernetes."

**Game Concept**\
"The game symbolizes a developer's journey through tech stacks, with each level representing a milestone (GO Developer, Docker Expert, Kubernetes Architect). The tank represents the player navigating challenges, and targets symbolize bugs or tasks to conquer."

Feel free to expand on your inspiration, whether it's personal, technical, or creative! ✍️

## How to Run 🚀

1. **Install Dependencies**: Ensure Python and Pygame are installed (see Dependencies).

2. **Prepare Assets**: Place sound files (`shoot.wav`, `collision.wav`, `win.wav`, `background.mp3`), images (`go_logo.png`, `docker_logo.png`, etc.), and video frames in the `video_frames` directory.

3. **Run the Game**: Execute the script with Python: python Game.py

   ```bash
   python container_tanker.py
   ```

4. **Controls**:

   - **WASD/Arrow Keys**: Move and rotate the tank.
   - **Mouse**: Aim the turret and shoot (left-click).
   - **S**: Start game (in menu).
   - **Q**: Quit or return to menu.
   - **R**: Replay/restart.
   - **Space**: Proceed to the next level (in end state).

## Dependencies 📚

- **Python 3.x**

- **Pygame**: Install via pip:

  ```bash
  pip install pygame
  ```

## Contributing 🤝

Contributions are welcome! 🙌 Fork the repository, make your changes, and submit a pull request. Suggestions for new features, bug fixes, or optimizations are appreciated.

Happy tanking! 🚛💥

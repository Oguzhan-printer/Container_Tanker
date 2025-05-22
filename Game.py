import pygame
import math
import random
import asyncio
import platform
import os

# Initialize Pygame
pygame.init()

# Screen and game settings
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CONTAİNER TANKER")
FPS = 120
TANK_SPEED = 3
BULLET_SPEED = 10
TARGET_SPEED = 2
BULLET_LIFETIME = 2
VIDEO_FPS = 120

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_YELLOW = (255, 255, 224)
VIOLET = (138, 43, 226)

# Global state
game = {
    "state": "menu",
    "level": 1,
    "bullets": [],
    "targets": [],
    "collision_effects": [],
    "animations": [],
    "bullets_left": 0,
    "current_frame_index": 0,
    "last_frame_time": 0,
    "tank": None,
    "video_frames": []
}

# Resources
res = {
    "shoot_sound": None,
    "collision_sound": None,
    "win_sound": None,
    "FONT": None,
    "PENALTY_FONT": None,
    "go_logo": None,
    "docker_logo": None,
    "java_logo": None,
    "tank_body_image": None,
    "tank_turret_image": None,
    "bullet_image": None
}

# UI elements
ui = {}

# Level configurations
level_configs = [
    {"bullets": 5, "targets": 5, "image": None, "title": "GO Developer"},
    {"bullets": 10, "targets": 10, "image": None, "title": "Docker Expert"},
    {"bullets": 15, "targets": 15, "image": None, "title": "Kubernetes Architect"}
]

# Load resources
def load_resources():
    # Load sounds
    try:
        for sound_name, file_name in [("shoot_sound", "assets/shoot.wav"), ("collision_sound", "assets/collision.wav"), ("win_sound", "assets/win.wav")]:
            if os.path.exists(file_name):
                res[sound_name] = pygame.mixer.Sound(file_name)
        if os.path.exists('assets/background.mp3'):
            pygame.mixer.music.load('assets/background.mp3')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Sound loading error: {e}")
    
    # Load fonts
    res["FONT"] = pygame.font.SysFont("Agency FB", 72)
    res["PENALTY_FONT"] = pygame.font.SysFont("Agency FB", 26)
    
    # Create default images
    images = {
        "go_logo": (pygame.Surface((48, 48)), GREEN),
        "docker_logo": (pygame.Surface((48, 48)), WHITE),
        "java_logo": (pygame.Surface((48, 48)), RED),
        "tank_body_image": (pygame.Surface((40, 40)), GREEN),
        "tank_turret_image": (pygame.Surface((30, 10)), YELLOW),
        "bullet_image": (pygame.Surface((16, 16)), WHITE)
    }
    
    # Fill default images with colors
    for name, (surface, color) in images.items():
        surface.fill(color)
        res[name] = surface
    
    # Try to load actual images
    try:
        for img_name, file_name in [
            ("go_logo", "assets/go_logo.png"), 
            ("docker_logo", "assets/docker_logo.png"), 
            ("java_logo", "assets/java_logo.png"),
            ("tank_body_image", "assets/tank_body.png"),
            ("tank_turret_image", "assets/tank_turret.png"),
            ("bullet_image", "assets/bullet.png")
        ]:
            if os.path.exists(file_name):
                img = pygame.image.load(file_name)
                if img_name in ["go_logo", "docker_logo", "java_logo"]:
                    img = pygame.transform.scale(img, (48, 48))
                elif img_name == "bullet_image":
                    img = pygame.transform.scale(img, (16, 16))
                res[img_name] = img
    except pygame.error as e:
        print(f"Image loading error: {e}")
    
    # Load video frames
    video_frames_dir = 'video_frames'
    if os.path.exists(video_frames_dir):
        try:
            frame_files = sorted([f for f in os.listdir(video_frames_dir) if f.endswith('.png')])
            for frame_file in frame_files:
                frame = pygame.transform.scale(pygame.image.load(os.path.join(video_frames_dir, frame_file)), (WIDTH, HEIGHT))
                game["video_frames"].append(frame)
        except Exception as e:
            print(f"Video frame loading error: {e}")
    
    # Update level configs with loaded images
    level_configs[0]["image"] = res["go_logo"]
    level_configs[1]["image"] = res["docker_logo"]
    level_configs[2]["image"] = res["java_logo"]

# UI functions
def create_ui():
    button_width, button_height = 150, 50
    button_spacing = 20
    
    # Menu buttons
    menu_start_x = (WIDTH - (button_width * 2 + button_spacing)) // 2
    menu_y = HEIGHT // 2
    ui["start_button"] = {"text": "Start (S)", "rect": pygame.Rect(menu_start_x, menu_y, button_width, button_height)}
    ui["quit_button"] = {"text": "Quit (Q)", "rect": pygame.Rect(menu_start_x + button_width + button_spacing, menu_y, button_width, button_height)}
    ui["volume_slider"] = {"rect": pygame.Rect(WIDTH - 160, 30, 150, 14), "value": 0.5, "dragging": False, "knob_radius": 5}
    
    # Level end buttons
    end_button_width, next_button_width = 150, 220
    end_start_x = (WIDTH - (next_button_width + end_button_width * 2 + button_spacing * 2)) // 2
    button_y = HEIGHT - 150
    
    ui["next_button"] = {"text": "Next Level (Space)", "rect": pygame.Rect(end_start_x, button_y, next_button_width, button_height)}
    ui["replay_button"] = {"text": "Replay (R)", "rect": pygame.Rect(end_start_x + next_button_width + button_spacing, button_y, end_button_width, button_height)}
    ui["menu_button"] = {"text": "Back to Menu (Q)", "rect": pygame.Rect(end_start_x + next_button_width + end_button_width + button_spacing * 2, button_y, end_button_width, button_height)}
    
    # Game over buttons
    lose_start_x = (WIDTH - (end_button_width * 2 + button_spacing)) // 2
    ui["retry_button"] = {"text": "Retry Level (R)", "rect": pygame.Rect(lose_start_x, button_y, end_button_width, button_height)}
    ui["lose_menu_button"] = {"text": "Back to Menu (Q)", "rect": pygame.Rect(lose_start_x + end_button_width + button_spacing, button_y, end_button_width, button_height)}
    
    # Final level buttons
    final_start_x = (WIDTH - (end_button_width * 2 + button_spacing)) // 2
    ui["restart_button"] = {"text": "Restart Game (R)", "rect": pygame.Rect(final_start_x, button_y, end_button_width, button_height)}
    ui["final_menu_button"] = {"text": "Back to Menu (Q)", "rect": pygame.Rect(final_start_x + end_button_width + button_spacing, button_y, end_button_width, button_height)}

def draw_button(button, surface):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = button["rect"].collidepoint(mouse_pos)
    text_color = LIGHT_YELLOW if is_hovered else WHITE
    
    pygame.draw.rect(surface, GRAY, button["rect"])
    text = res["PENALTY_FONT"].render(button["text"], True, text_color)
    surface.blit(text, text.get_rect(center=button["rect"].center))

def draw_slider(slider, surface):
    pygame.draw.rect(surface, WHITE, slider["rect"], 2)
    pygame.draw.rect(surface, GRAY, slider["rect"], 1, 1)
    knob_x = slider["rect"].x + int(slider["value"] * slider["rect"].width)
    pygame.draw.circle(surface, WHITE, (knob_x, slider["rect"].centery), slider["knob_radius"])
    volume_text = res["PENALTY_FONT"].render(f"Volume: {int(slider['value'] * 100)}%", True, WHITE)
    surface.blit(volume_text, (slider["rect"].x, slider["rect"].y - 27))  

def update_slider(slider, mouse_pos, mouse_pressed):
    if mouse_pressed[0] and slider["rect"].collidepoint(mouse_pos):
        slider["dragging"] = True
    if not mouse_pressed[0]:
        slider["dragging"] = False
    if slider["dragging"]:
        slider["value"] = max(0, min(1, (mouse_pos[0] - slider["rect"].x) / slider["rect"].width))
        for sound in ["shoot_sound", "collision_sound", "win_sound"]:
            if res[sound]:
                res[sound].set_volume(slider["value"])
        pygame.mixer.music.set_volume(slider["value"])

# Game entity functions
def create_tank(x, y):
    return {
        "body_image": res["tank_body_image"],
        "turret_image": res["tank_turret_image"],
        "original_body_image": res["tank_body_image"],
        "body_rect": res["tank_body_image"].get_rect(center=(x, y)),
        "pos": pygame.math.Vector2(x, y),
        "angle": 0,
        "speed": 0,
        "rotation_speed": 0,
        "max_speed": TANK_SPEED,
        "turret_angle": 0,
        "prev_positions": []
    }

def update_tank(tank, keys, mouse_pos):
    # Speed and rotation control
    tank["speed"] = tank["max_speed"] if keys[pygame.K_w] or keys[pygame.K_UP] else (-tank["max_speed"] * 0.7 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0)
    tank["rotation_speed"] = 2 if keys[pygame.K_a] or keys[pygame.K_LEFT] else (-2 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0)
    
    # Update angle and position
    tank["angle"] = (tank["angle"] + tank["rotation_speed"]) % 360
    angle_rad = math.radians(tank["angle"])
    tank["pos"].x += math.cos(angle_rad) * tank["speed"]
    tank["pos"].y -= math.sin(angle_rad) * tank["speed"]
    tank["pos"].x = max(0, min(tank["pos"].x, WIDTH))
    tank["pos"].y = max(0, min(tank["pos"].y, HEIGHT))
    
    # Track positions and update images
    tank["prev_positions"].append((tank["pos"].x, tank["pos"].y))
    if len(tank["prev_positions"]) > 50:
        tank["prev_positions"].pop(0)
    
    tank["body_image"] = pygame.transform.rotate(tank["original_body_image"], tank["angle"])
    tank["body_rect"] = tank["body_image"].get_rect(center=tank["pos"])
    tank["turret_angle"] = math.atan2(mouse_pos[1] - tank["pos"].y, mouse_pos[0] - tank["pos"].x)

def draw_tank(tank, surface):
    # Draw tracks
    for i in range(1, len(tank["prev_positions"])):
        pygame.draw.line(surface, (100, 100, 100), tank["prev_positions"][i-1], tank["prev_positions"][i], 2)
    
    # Draw tank body and turret
    surface.blit(tank["body_image"], tank["body_rect"])
    rotated_turret = pygame.transform.rotate(tank["turret_image"], -math.degrees(tank["turret_angle"]))
    surface.blit(rotated_turret, rotated_turret.get_rect(center=tank["body_rect"].center))

def shoot_tank(tank):
    # Create bullet
    bullet = {
        "pos": pygame.math.Vector2(tank["pos"].x, tank["pos"].y),
        "vel": pygame.math.Vector2(BULLET_SPEED * math.cos(tank["turret_angle"]), BULLET_SPEED * math.sin(tank["turret_angle"])),
        "image": res["bullet_image"],
        "rect": res["bullet_image"].get_rect(center=(tank["pos"].x, tank["pos"].y)),
        "spawn_time": pygame.time.get_ticks() / 1000,
        "angle": math.degrees(tank["turret_angle"])
    }
    
    # Play sound
    if res["shoot_sound"]:
        res["shoot_sound"].play()
    
    # Apply recoil
    recoil_angle = tank["turret_angle"] + math.pi
    tank["pos"].x += math.cos(recoil_angle) * 5
    tank["pos"].y += math.sin(recoil_angle) * 5
    tank["pos"].x = max(0, min(tank["pos"].x, WIDTH))
    tank["pos"].y = max(0, min(tank["pos"].y, HEIGHT))
    tank["body_rect"].center = tank["pos"]
    
    return bullet

def update_bullet(bullet):
    bullet["pos"] += bullet["vel"]
    bullet["rect"].center = bullet["pos"]
    return (0 <= bullet["pos"].x <= WIDTH and 0 <= bullet["pos"].y <= HEIGHT and
            (pygame.time.get_ticks() / 1000 - bullet["spawn_time"]) < BULLET_LIFETIME)

def draw_bullet(bullet, surface):
    rotated_bullet = pygame.transform.rotate(bullet["image"], -bullet["angle"])
    surface.blit(rotated_bullet, rotated_bullet.get_rect(center=bullet["pos"]))

def create_target(x, y, image):
    return {
        "image": image,
        "rect": image.get_rect(center=(x, y)),
        "pos": pygame.math.Vector2(x, y),
        "vel": pygame.math.Vector2(random.uniform(-TARGET_SPEED, TARGET_SPEED), random.uniform(-TARGET_SPEED, TARGET_SPEED))
    }

def update_target(target):
    # Update position
    target["pos"] += target["vel"]
    
    # Bounce off walls
    if target["pos"].x < 0 or target["pos"].x > WIDTH:
        target["vel"].x *= -1
    if target["pos"].y < 0 or target["pos"].y > HEIGHT:
        target["vel"].y *= -1
    
    # Clamp position
    target["pos"].x = max(0, min(target["pos"].x, WIDTH))
    target["pos"].y = max(0, min(target["pos"].y, HEIGHT))
    target["rect"].center = target["pos"]

# Animation functions
def create_starburst_animation(text, x, y, duration=2.0, particle_count=60, is_celebration=False):
    particles = []
    colors = [RED, VIOLET, GREEN, YELLOW] if is_celebration else [YELLOW]
    
    for _ in range(particle_count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 300) if is_celebration else random.uniform(100, 200)
        particles.append({
            'pos': pygame.math.Vector2(x, y),
            'vel': pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
            'size': random.randint(5, 10),
            'alpha': 255,
            'color': random.choice(colors) if is_celebration else YELLOW
        })
    
    return {
        "text": text,
        "x": x,
        "y": y,
        "start_time": pygame.time.get_ticks() / 1000,
        "duration": duration,
        "particles": particles,
        "is_celebration": is_celebration
    }

def update_starburst_animation(animation):
    elapsed = pygame.time.get_ticks() / 1000 - animation["start_time"]
    if elapsed > animation["duration"]:
        return False
    
    progress = elapsed / animation["duration"]
    for particle in animation["particles"]:
        particle['pos'] += particle['vel'] * (1 / FPS)
        particle['alpha'] = int(255 * (1 - progress))
        particle['size'] = max(1, particle['size'] * (1 - progress))
    return True

def draw_starburst_animation(animation, surface):
    text = res["FONT"].render(animation["text"], True, WHITE)
    surface.blit(text, text.get_rect(center=(animation["x"], animation["y"])))
    
    for particle in animation["particles"]:
        particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*particle['color'], particle['alpha']),
                          (particle['size'], particle['size']), particle['size'])
        surface.blit(particle_surface, (particle['pos'].x - particle['size'], particle['pos'].y - particle['size']))

def create_collision_effect(x, y):
    particles = []
    for _ in range(25):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        particles.append({
            'pos': pygame.math.Vector2(x, y),
            'vel': pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
            'size': random.randint(6, 12),
            'color': (255, random.randint(0, 100), 0),
            'alpha': 255
        })
    
    return {
        "pos": pygame.math.Vector2(x, y),
        "start_time": pygame.time.get_ticks() / 1000,
        "duration": 1.5,
        "particles": particles
    }

def update_collision_effect(effect):
    elapsed = pygame.time.get_ticks() / 1000 - effect["start_time"]
    if elapsed > effect["duration"]:
        return False

    progress = elapsed / effect["duration"]
    for particle in effect["particles"]:
        particle['pos'] += particle['vel'] * (1 / 60)
        particle['vel'] *= 0.92
        particle['size'] = max(1, particle['size'] * 0.95)
        particle['alpha'] = int(255 * (1 - progress))
    return True

def draw_collision_effect(effect, surface):
    for particle in effect["particles"]:
        if particle['alpha'] > 0:
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*particle['color'], particle['alpha']),
                              (particle['size'], particle['size']), particle['size'])
            surface.blit(particle_surface, (particle['pos'].x - particle['size'], particle['pos'].y - particle['size']))

# Game state functions
def reset_to_menu():
    game["state"] = "menu"
    game["level"] = 1
    game["bullets"] = []
    game["targets"] = []
    game["collision_effects"] = []
    game["animations"] = []
    game["bullets_left"] = 0
    game["tank"] = create_tank(WIDTH // 2, HEIGHT // 2)
    game["current_frame_index"] = 0
    game["last_frame_time"] = pygame.time.get_ticks() / 1000

def update_background_frame():
    if game["video_frames"]:
        current_time = pygame.time.get_ticks() / 1000
        if current_time - game["last_frame_time"] >= 1.0 / VIDEO_FPS:
            game["current_frame_index"] = (game["current_frame_index"] + 1) % len(game["video_frames"])
            game["last_frame_time"] = current_time

def start_level():
    config = level_configs[game["level"] - 1]
    game["bullets_left"] = config["bullets"]
    game["targets"] = [create_target(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), config["image"])
                      for _ in range(config["targets"])]
    game["bullets"] = []
    game["collision_effects"] = []
    game["animations"] = [create_starburst_animation(f"Level {game['level']} Starting!", WIDTH // 2, HEIGHT // 2)]
    game["state"] = "playing"

# Game loop functions
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Menu state
            if game["state"] == "menu":
                if ui["start_button"]["rect"].collidepoint(mouse_pos):
                    game["level"] = 1
                    game["animations"] = [create_starburst_animation("Container Tanker Starting!", WIDTH // 2, HEIGHT // 2)]
                    game["state"] = "starting"
                elif ui["quit_button"]["rect"].collidepoint(mouse_pos):
                    return False
            
            # Playing state
            elif game["state"] == "playing" and game["bullets_left"] > 0:
                bullet = shoot_tank(game["tank"])
                game["bullets"].append(bullet)
                game["bullets_left"] -= 1
            
            # End state
            elif game["state"] == "end":
                if ui["replay_button"]["rect"].collidepoint(mouse_pos):
                    game["level"] = 1
                    game["animations"] = [create_starburst_animation("Container Tanker Starting!", WIDTH // 2, HEIGHT // 2)]
                    game["state"] = "starting"
                elif ui["menu_button"]["rect"].collidepoint(mouse_pos):
                    reset_to_menu()
                elif ui["next_button"]["rect"].collidepoint(mouse_pos) and game["level"] < len(level_configs):
                    game["level"] += 1
                    start_level()
                elif ui["restart_button"]["rect"].collidepoint(mouse_pos) and game["level"] == len(level_configs):
                    game["level"] = 1
                    game["animations"] = [create_starburst_animation("Container Tanker Starting!", WIDTH // 2, HEIGHT // 2)]
                    game["state"] = "starting"
                elif ui["final_menu_button"]["rect"].collidepoint(mouse_pos) and game["level"] == len(level_configs):
                    reset_to_menu()
            
            # Game over state
            elif game["state"] == "game_over":
                if ui["retry_button"]["rect"].collidepoint(mouse_pos):
                    game["level"] = 1
                    game["animations"] = [create_starburst_animation("Container Tanker Starting!", WIDTH // 2, HEIGHT // 2)]
                    game["state"] = "starting"
                elif ui["lose_menu_button"]["rect"].collidepoint(mouse_pos):
                    reset_to_menu()
        
        # Keyboard events
        if event.type == pygame.KEYDOWN:
            if game["state"] == "menu" and event.key == pygame.K_s:
                game["level"] = 1
                game["animations"] = [create_starburst_animation("Container Tanker Starting!", WIDTH // 2, HEIGHT // 2)]
                game["state"] = "starting"
            elif event.key == pygame.K_q:
                if game["state"] in ["menu", "end", "game_over"]:
                    if game["state"] == "menu":
                        return False
                    else:
                        reset_to_menu()
            elif event.key == pygame.K_r and game["state"] in ["end", "game_over"]:
                game["level"] = 1
                game["animations"] = [create_starburst_animation("Container Tanker Starting!", WIDTH // 2, HEIGHT // 2)]
                game["state"] = "starting"
            elif event.key == pygame.K_SPACE and game["state"] == "end" and game["level"] < len(level_configs):
                game["level"] += 1
                start_level()
    
    return True

def update_game():
    # Update background
    update_background_frame()
    
    # Handle common events
    if not handle_events():
        return False
    
    # Update based on game state
    if game["state"] == "menu":
        update_slider(ui["volume_slider"], pygame.mouse.get_pos(), pygame.mouse.get_pressed())
    
    elif game["state"] == "starting":
        # Update animations
        for anim in game["animations"][:]:
            if not update_starburst_animation(anim):
                game["animations"].remove(anim)
        if not game["animations"]:
            start_level()
    
    elif game["state"] == "playing":
        # Update tank
        update_tank(game["tank"], pygame.key.get_pressed(), pygame.mouse.get_pos())
        
        # Update bullets
        for bullet in game["bullets"][:]:
            if not update_bullet(bullet):
                game["bullets"].remove(bullet)
        
        # Update targets and check collisions
        for target in game["targets"][:]:
            update_target(target)
            
            # Check tank collision
            if game["tank"]["body_rect"].colliderect(target["rect"]):
                game["collision_effects"].append(create_collision_effect(game["tank"]["pos"].x, game["tank"]["pos"].y))
                if res["collision_sound"]:
                    res["collision_sound"].play()
                game["animations"] = [create_starburst_animation("Game Over! Tank Hit Target!", WIDTH // 2, HEIGHT // 2)]
                game["state"] = "game_over"
                break
            
            # Check bullet collisions
            for bullet in game["bullets"][:]:
                if target["rect"].colliderect(bullet["rect"]):
                    game["targets"].remove(target)
                    game["bullets"].remove(bullet)
                    game["collision_effects"].append(create_collision_effect(target["pos"].x, target["pos"].y))
                    if res["collision_sound"]:
                        res["collision_sound"].play()
                    break
        
        # Update effects
        for effect in game["collision_effects"][:]:
            if not update_collision_effect(effect):
                game["collision_effects"].remove(effect)
        
        # Update animations
        for anim in game["animations"][:]:
            if not update_starburst_animation(anim):
                game["animations"].remove(anim)
        
        # Check win/lose conditions
        if not game["targets"]:
            config = level_configs[game["level"] - 1]
            text = f"{config['title']} Achieved!" if config["title"] else f"Level {game['level']} Completed!"
            game["animations"] = [create_starburst_animation(text, WIDTH // 2, HEIGHT // 2, 4.0, 20, True)]
            if res["win_sound"]:
                res["win_sound"].play()
            game["state"] = "end"
        
        if game["bullets_left"] == 0 and not game["bullets"] and game["targets"]:
            game["animations"] = [create_starburst_animation("Game Over! Bullets Depleted!", WIDTH // 2, HEIGHT // 2)]
            game["state"] = "game_over"
    
    elif game["state"] in ["end", "game_over"]:
        # Update effects
        for effect in game["collision_effects"][:]:
            if not update_collision_effect(effect):
                game["collision_effects"].remove(effect)
        
        # Update animations
        for anim in game["animations"][:]:
            if not update_starburst_animation(anim):
                game["animations"].remove(anim)
    
    return True

def draw_game():
    # Draw background
    if game["video_frames"] and game["current_frame_index"] < len(game["video_frames"]):
        screen.blit(game["video_frames"][game["current_frame_index"]], (0, 0))
    else:
        # Fallback gradient background
        for y in range(HEIGHT):
            pygame.draw.line(screen, (0, 0, int(50 * (y / HEIGHT))), (0, y), (WIDTH, y))
    
    # Draw based on game state
    if game["state"] == "menu":
        # Draw title
        title = res["FONT"].render("Container Tanker", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        title = pygame.transform.rotozoom(title, math.sin(pygame.time.get_ticks() / 1000) * 5, 1.0)
        screen.blit(title, title.get_rect(center=title_rect.center))
        
        # Draw buttons
        draw_button(ui["start_button"], screen)
        draw_button(ui["quit_button"], screen)
        draw_slider(ui["volume_slider"], screen)
    
    elif game["state"] in ["starting", "end", "game_over"]:
        # Draw animations
        for anim in game["animations"]:
            draw_starburst_animation(anim, screen)
        
        # Draw collision effects
        for effect in game["collision_effects"]:
            draw_collision_effect(effect, screen)
        
        # Draw buttons for end states
        if game["state"] == "end":
            if game["level"] < len(level_configs):
                draw_button(ui["next_button"], screen)
                draw_button(ui["replay_button"], screen)
                draw_button(ui["menu_button"], screen)
            else:
                draw_button(ui["restart_button"], screen)
                draw_button(ui["final_menu_button"], screen)
        elif game["state"] == "game_over":
            draw_button(ui["retry_button"], screen)
            draw_button(ui["lose_menu_button"], screen)
    
    elif game["state"] == "playing":
        # Draw game elements
        draw_tank(game["tank"], screen)
        
        for bullet in game["bullets"]:
            draw_bullet(bullet, screen)
        
        for target in game["targets"]:
            screen.blit(target["image"], target["rect"])
        
        for effect in game["collision_effects"]:
            draw_collision_effect(effect, screen)
        
        for anim in game["animations"]:
            draw_starburst_animation(anim, screen)
        
        # Draw HUD
        bullets_text = res["PENALTY_FONT"].render(f"Bullets: {game['bullets_left']}", True, WHITE)
        level_text = res["PENALTY_FONT"].render(f"Level: {game['level']}", True, WHITE)
        screen.blit(bullets_text, (10, 10))
        screen.blit(level_text, (10, 40))
    
    pygame.display.flip()

async def main():
    # Initialize game
    load_resources()
    create_ui()
    game["tank"] = create_tank(WIDTH // 2, HEIGHT // 2)
    game["last_frame_time"] = pygame.time.get_ticks() / 1000
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        running = update_game()
        draw_game()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Game could not be started: {e}")
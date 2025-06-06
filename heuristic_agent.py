"""
Heuristic agent for Sokoban game
Automatically solves Sokoban levels using the PCG generator's solver
"""

import pygame
import sys
import os
import time
import random
import collections
import copy
from Environment import Environment
from Level import Level
import pcg_generator

# --- Global Variables ---
myEnvironment = None
myLevel = None
available_themes = ["default", "ksokoban", "soft"]
current_theme_index = 0
theme = available_themes[current_theme_index]
screen_width, screen_height = 800, 600
auto_solve_delay = 0.3  # Delay between moves in seconds

# --- Heuristic Agent Logic ---

class HeuristicAgent:
    def __init__(self):
        self.solution_path = []
        self.current_step = 0
        self.solving = False
        self.level_solved = False
        
    def reset(self):
        """Reset the agent state"""
        self.solution_path = []
        self.current_step = 0
        self.solving = False
        self.level_solved = False
    
    def find_solution(self, level_matrix):
        """Find a solution for the given level"""
        # Use the existing BFS solver from pcg_generator
        solution = pcg_generator.solve_sokoban_bfs(level_matrix)
        if solution:
            self.solution_path = solution
            self.current_step = 0
            self.solving = True
            self.level_solved = False
            print(f"Solution found with {len(solution)} steps")
            return True
        else:
            print("No solution found")
            return False
    
    def get_next_move(self):
        """Get the next move from the solution path"""
        if not self.solving or self.current_step >= len(self.solution_path):
            return None
        
        move = self.solution_path[self.current_step]
        self.current_step += 1
        return move
    
    def is_finished(self):
        """Check if the agent has finished solving the level"""
        return self.level_solved or (self.solving and self.current_step >= len(self.solution_path))

# --- Drawing and Game Logic ---

def draw_text(surface, text, position, font_size=20, color=(255, 255, 255)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def drawLevel(matrix_to_draw):
    global myEnvironment, myLevel, theme, screen_width, screen_height
    if not myEnvironment or not myLevel:
        print("Error: Environment or Level not initialized for drawing.")
        return

    # Load level images based on the current theme
    try:
        wall_img_path = os.path.join(myEnvironment.getPath(), 'themes', theme, 'images', 'wall.png')
        box_img_path = os.path.join(myEnvironment.getPath(), 'themes', theme, 'images', 'box.png')
        box_on_target_img_path = os.path.join(myEnvironment.getPath(), 'themes', theme, 'images', 'box_on_target.png')
        space_img_path = os.path.join(myEnvironment.getPath(), 'themes', theme, 'images', 'space.png')
        target_img_path = os.path.join(myEnvironment.getPath(), 'themes', theme, 'images', 'target.png')
        player_img_path = os.path.join(myEnvironment.getPath(), 'themes', theme, 'images', 'player.png')

        wall = pygame.image.load(wall_img_path).convert()
        box = pygame.image.load(box_img_path).convert()
        box_on_target = pygame.image.load(box_on_target_img_path).convert()
        space = pygame.image.load(space_img_path).convert()
        target = pygame.image.load(target_img_path).convert()
        player = pygame.image.load(player_img_path).convert()
    except pygame.error as e:
        print(f"Error loading theme images for theme '{theme}': {e}")
        myEnvironment.screen.fill((0,0,0))
        draw_text(myEnvironment.screen, f"Error: Failed to load theme '{theme}'. Check console.", (50, 50), 24)
        pygame.display.update()
        return

    level_width_tiles, level_height_tiles = myLevel.getSize()
    if level_width_tiles == 0 or level_height_tiles == 0:
        print("Error: Level size is zero.")
        myEnvironment.screen.fill((0,0,0))
        draw_text(myEnvironment.screen, "Error: Level data missing or corrupt.", (50, 50))
        pygame.display.update()
        return
        
    hud_height = 80
    drawable_height = screen_height - hud_height

    img_size_w = screen_width // level_width_tiles
    img_size_h = drawable_height // level_height_tiles
    new_image_size = min(img_size_w, img_size_h, 36) 
    if new_image_size < 10: new_image_size = 10

    if new_image_size != 36: 
        wall = pygame.transform.scale(wall, (new_image_size, new_image_size))
        box = pygame.transform.scale(box, (new_image_size, new_image_size))
        box_on_target = pygame.transform.scale(box_on_target, (new_image_size, new_image_size))
        space = pygame.transform.scale(space, (new_image_size, new_image_size))
        target = pygame.transform.scale(target, (new_image_size, new_image_size))
        player = pygame.transform.scale(player, (new_image_size, new_image_size))

    images = {'#': wall, ' ': space, '$': box, '.': target, '@': player, '*': box_on_target, '+': player}
    
    myEnvironment.screen.fill((0,0,0))

    for r, row_val in enumerate(matrix_to_draw):
        for c, char_val in enumerate(row_val):
            if char_val in images:
                myEnvironment.screen.blit(images[char_val], (c * new_image_size, r * new_image_size))
            else:
                pygame.draw.rect(myEnvironment.screen, (255,0,255), (c*new_image_size, r*new_image_size, new_image_size, new_image_size))
    
    # Draw HUD
    draw_text(myEnvironment.screen, "Sokoban - Heuristic Agent", (10, screen_height - 75), 18)
    draw_text(myEnvironment.screen, "Controls: N (New Level), T (Cycle Theme), ESC (Quit)", (10, screen_height - 55), 18)
    
    if myLevel.is_pcg and myLevel.solution_path:
        solution_info = f"Solution length: {len(myLevel.solution_path)} steps"
        draw_text(myEnvironment.screen, solution_info, (screen_width - 300, screen_height - 55), 18)

    pygame.display.update()

def movePlayer(direction):
    global myLevel
    if not myLevel:
        return False

    matrix = myLevel.getMatrix()
    myLevel.addToHistory(matrix)

    player_pos = myLevel.getPlayerPosition()
    if not player_pos:
        print("Error: Player position not found.")
        return False
    
    x, y = player_pos
    
    if direction == "L": dx, dy = -1, 0
    elif direction == "R": dx, dy = 1, 0
    elif direction == "U": dx, dy = 0, -1
    elif direction == "D": dx, dy = 0, 1
    else: return False

    next_x, next_y = x + dx, y + dy
    next_next_x, next_next_y = x + 2*dx, y + 2*dy

    if not (0 <= next_y < len(matrix) and 0 <= next_x < len(matrix[next_y])):
        myLevel.getLastMatrix() 
        return False

    current_player_char = matrix[y][x]
    destination_char = matrix[next_y][next_x]
    new_matrix = [list(row) for row in matrix]
    can_move = False

    if destination_char == ' ' or destination_char == '.':
        can_move = True
        new_matrix[next_y][next_x] = '+' if destination_char == '.' else '@'
        new_matrix[y][x] = '.' if current_player_char == '+' else ' '
    elif destination_char == '$' or destination_char == '*':
        if not (0 <= next_next_y < len(matrix) and 0 <= next_next_x < len(matrix[next_next_y])):
            myLevel.getLastMatrix()
            return False
        
        char_beyond_box = matrix[next_next_y][next_next_x]
        if char_beyond_box == ' ' or char_beyond_box == '.':
            can_move = True
            new_matrix[next_next_y][next_next_x] = '*' if char_beyond_box == '.' else '$'
            new_matrix[next_y][next_x] = '+' if destination_char == '*' else '@'
            new_matrix[y][x] = '.' if current_player_char == '+' else ' '
        else:
            myLevel.getLastMatrix()
            return False
    else:
        myLevel.getLastMatrix()
        return False

    if can_move:
        myLevel.matrix = new_matrix
        drawLevel(myLevel.getMatrix())
        return True
    return False

def initLevel():
    global myLevel
    print(f"Initializing PCG level")
    
    # Always generate a new random level - don't use simple levels
    # Set a new random seed based on current time to ensure different levels
    seed = int(time.time() * 1000) % 10000000
    random.seed(seed)
    pcg_generator.set_random_seed()
    
    print(f"Using random seed: {seed} for level generation")
    
    try:
        # Generate a new random level
        generated_matrix, solution = pcg_generator.generate_level()
        
        # Verify the level is valid and solvable
        verification = pcg_generator.solve_sokoban_bfs(generated_matrix)
        if not verification:
            print("Warning: Generated level failed verification. Trying again with new seed.")
            # Try again with a different seed
            seed = (seed + 1234) % 10000000
            random.seed(seed)
            pcg_generator.set_random_seed()
            generated_matrix, solution = pcg_generator.generate_level()
            
            # Check again
            verification = pcg_generator.solve_sokoban_bfs(generated_matrix)
            if not verification:
                print("Error: Second generation attempt failed. Using fallback.")
                # Use a fallback but ensure it's different from previous ones
                generated_matrix, solution = pcg_generator.get_fallback_level()
        
        # Create the level
        myLevel = Level(source=generated_matrix, level_specifier="pcg", is_pcg=True, solution_path=solution)
        
        if myLevel and myLevel.getMatrix():
            drawLevel(myLevel.getMatrix())
        else:
            print("Failed to initialize level.")
            myEnvironment.screen.fill((20,0,0))
            draw_text(myEnvironment.screen, "Error: Could not load level!", (50,50))
            pygame.display.update()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()
        
        return myLevel
    except Exception as e:
        print(f"Error in level initialization: {e}")
        # Emergency fallback - use a different one each time
        emergency_levels = [
            [
                ['#', '#', '#', '#', '#'],
                ['#', '@', '$', '.', '#'],
                ['#', ' ', ' ', ' ', '#'],
                ['#', '#', '#', '#', '#']
            ],
            [
                ['#', '#', '#', '#', '#', '#'],
                ['#', ' ', ' ', ' ', ' ', '#'],
                ['#', '@', '$', ' ', '.', '#'],
                ['#', ' ', ' ', ' ', ' ', '#'],
                ['#', '#', '#', '#', '#', '#']
            ],
            [
                ['#', '#', '#', '#', '#'],
                ['#', '@', ' ', ' ', '#'],
                ['#', ' ', '$', ' ', '#'],
                ['#', ' ', ' ', '.', '#'],
                ['#', '#', '#', '#', '#']
            ]
        ]
        
        # Choose a different emergency level each time
        idx = int(time.time()) % len(emergency_levels)
        emergency_level = emergency_levels[idx]
        emergency_solution = ['R', 'R']
        
        myLevel = Level(source=emergency_level, level_specifier="pcg", is_pcg=True, solution_path=emergency_solution)
        drawLevel(myLevel.getMatrix())
        return myLevel

def cycle_theme():
    global theme, current_theme_index, available_themes, myLevel
    current_theme_index = (current_theme_index + 1) % len(available_themes)
    theme = available_themes[current_theme_index]
    print(f"Theme changed to: {theme}")
    if myLevel and myLevel.getMatrix():
        drawLevel(myLevel.getMatrix())

# --- Main Game Loop ---

def main():
    global myEnvironment, screen_width, screen_height
    
    pygame.init()
    myEnvironment = Environment()
    screen_width, screen_height = myEnvironment.size
    pygame.display.set_caption("Sokoban - Heuristic Agent")
    
    # Initialize the heuristic agent
    agent = HeuristicAgent()
    
    # Initialize the first level
    level = initLevel()
    
    # Find a solution for the initial level
    agent.find_solution(level.getMatrix())
    
    running = True
    level_complete = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_n:
                    # Force a new random level
                    level = initLevel()
                    agent.reset()
                    agent.find_solution(level.getMatrix())
                    level_complete = False
                elif event.key == pygame.K_t:
                    cycle_theme()
        
        # If the level is complete, wait a moment and then load a new level
        if level_complete:
            pygame.time.wait(1000)
            # Force a new random level
            level = initLevel()
            agent.reset()
            agent.find_solution(level.getMatrix())
            level_complete = False
            continue
        
        # Get the next move from the agent
        if not agent.is_finished():
            move = agent.get_next_move()
            if move:
                movePlayer(move)
                time.sleep(auto_solve_delay)  # Add delay between moves
                
                # Check if the level is solved
                if level.isSolved():
                    print("Level solved!")
                    agent.level_solved = True
                    level_complete = True
                    
                    # Display completion message
                    myEnvironment.screen.fill((0,0,0))
                    draw_text(myEnvironment.screen, "Level Completed!", (screen_width//2 - 100, screen_height//2 - 20), 30)
                    pygame.display.update()
        else:
            # If the agent has finished but the level is not solved, try to find a new solution
            if not level.isSolved():
                print("Agent finished but level not solved. Finding new solution...")
                if agent.find_solution(level.getMatrix()):
                    continue
                else:
                    # If no solution can be found, load a new level
                    print("No solution found. Loading new level...")
                    level = initLevel()
                    agent.reset()
                    agent.find_solution(level.getMatrix())
                    level_complete = False
            else:
                level_complete = True
        
        pygame.time.wait(10)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

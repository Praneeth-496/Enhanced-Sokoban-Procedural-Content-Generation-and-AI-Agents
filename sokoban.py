"""
Enhanced Sokoban game with robust PCG and hint functionality
Main game file with improved integration of PCG generator and hint system
"""

import pygame
import sys
import os
from Environment import Environment
from Level import Level
import pcg_generator

# --- Global Variables ---
myEnvironment = None
myLevel = None
available_themes = ["default", "ksokoban", "soft"]
current_theme_index = 0
theme = available_themes[current_theme_index]
current_level_set = "original"
current_level_num = 1
hint_step_index = 0
screen_width, screen_height = 800, 600

def draw_text(surface, text, position, font_size=20, color=(255, 255, 255)):
    """Draw text on the given surface"""
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def drawLevel(matrix_to_draw):
    """Draw the current level state on screen"""
    global myEnvironment, myLevel, theme, screen_width, screen_height, hint_step_index
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
    draw_text(myEnvironment.screen, "Controls: Arrows (Move), U (Undo), R (Restart)", (10, screen_height - 75), 18)
    draw_text(myEnvironment.screen, "Actions: N (New Level), H (Hint), T (Cycle Theme)", (10, screen_height - 55), 18)
    
    current_theme_text = f"Theme: {theme.capitalize()}"
    draw_text(myEnvironment.screen, current_theme_text, (screen_width - 200, screen_height - 75), 18)

    if myLevel.is_pcg and myLevel.solution_path:
        total_hints = len(myLevel.solution_path)
        hint_progress = f"Hint: {hint_step_index}/{total_hints}"
        if hint_step_index >= total_hints and total_hints > 0:
            hint_progress = "All hints used"
        elif total_hints == 0:
            hint_progress = "No hints for this level"
        draw_text(myEnvironment.screen, hint_progress, (screen_width - 200, screen_height - 55), 18)

    pygame.display.update()

def movePlayer(direction):
    """Move the player in the specified direction"""
    global myLevel, hint_step_index, screen_width, screen_height
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
        # Simple move to empty space or goal
        can_move = True
        new_matrix[next_y][next_x] = '+' if destination_char == '.' else '@'
        new_matrix[y][x] = '.' if current_player_char == '+' else ' '
    
    elif destination_char == '$' or destination_char == '*':
        # Try to push a box
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

        if myLevel.isSolved():
            myEnvironment.screen.fill((0,0,0))
            draw_text(myEnvironment.screen, "Level Completed!", (screen_width//2 - 100, screen_height//2 - 20), 30)
            pygame.display.update()
            pygame.time.wait(2000)
            if myLevel.is_pcg:
                initLevel(is_pcg=True, new_pcg_level=True)
            else:
                global current_level_num
                current_level_num += 1
                try:
                    initLevel(current_level_set, current_level_num)
                except Exception: 
                    print(f"No more levels in set {current_level_set} or error loading. Using PCG level.")
                    initLevel(is_pcg=True, new_pcg_level=True)
        return True
    return False

def initLevel(level_source=None, level_num_specifier=None, is_pcg=False, new_pcg_level=False):
    """Initialize a new level"""
    global myLevel, current_level_set, current_level_num, hint_step_index
    hint_step_index = 0  # Reset hint index for new level

    if is_pcg:
        current_level_set = "pcg"
        print(f"Initializing PCG level")
        
        # Set a new random seed for each generation
        pcg_generator.set_random_seed()
        
        # Use enhanced PCG generator
        generated_matrix, solution = pcg_generator.generate_level()
        
        # Verify the level is valid and solvable
        if not generated_matrix or not solution:
            print("Error: Failed to generate valid level. Using fallback.")
            generated_matrix, solution = pcg_generator.get_fallback_level()
        
        # Double-check solvability
        verification = pcg_generator.solve_sokoban_bfs(generated_matrix)
        if not verification:
            print("Warning: Generated level failed verification. Using fallback.")
            generated_matrix, solution = pcg_generator.get_fallback_level()
            # Verify fallback is solvable
            verification = pcg_generator.solve_sokoban_bfs(generated_matrix)
            if not verification:
                print("Critical error: Fallback level also failed verification!")
                # Use the simplest possible fallback as last resort
                generated_matrix = [
                    ['#', '#', '#', '#', '#'],
                    ['#', '@', '$', '.', '#'],
                    ['#', ' ', ' ', ' ', '#'],
                    ['#', '#', '#', '#', '#']
                ]
                solution = ['R', 'R']
        
        myLevel = Level(source=generated_matrix, level_specifier="pcg", is_pcg=True, solution_path=solution)
    else:
        current_level_set = level_source
        current_level_num = level_num_specifier
        print(f"Initializing file level: {current_level_set} - {current_level_num}")
        myLevel = Level(source=current_level_set, level_specifier=current_level_num, is_pcg=False)

    if myLevel and myLevel.getMatrix():
        drawLevel(myLevel.getMatrix())
    else:
        print("Failed to initialize or load level.")
        myEnvironment.screen.fill((20,0,0))
        draw_text(myEnvironment.screen, "Error: Could not load level!", (50,50))
        pygame.display.update()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

def show_hint():
    """Show a hint by applying the next move from the solution path"""
    global myLevel, hint_step_index
    
    if not myLevel or not myLevel.is_pcg:
        print("Hint not available for this level.")
        drawLevel(myLevel.getMatrix())
        return

    # Check if we need to regenerate the solution
    if hint_step_index >= len(myLevel.solution_path) or hint_step_index == 0:
        # If at end of solution or just starting, regenerate from current state
        regenerate_solution_from_current_state()
    
    if myLevel.solution_path and hint_step_index < len(myLevel.solution_path):
        move = myLevel.solution_path[hint_step_index]
        print(f"Hint: Applying move {move} (Step {hint_step_index + 1}/{len(myLevel.solution_path)})")
        
        # Try to apply the move
        move_successful = movePlayer(move)
        
        if move_successful:
            hint_step_index += 1
        else:
            # If the move failed, regenerate solution from current state
            print("Hint move could not be applied. Regenerating solution from current state...")
            regenerate_solution_from_current_state()
            
        drawLevel(myLevel.getMatrix())
    else:
        # If we've reached the end of the solution path but the level isn't solved,
        # regenerate a solution from the current state
        if not myLevel.isSolved():
            print("End of current solution path reached but level not solved. Regenerating solution...")
            regenerate_solution_from_current_state()
        else:
            print(f"End of hints. All {len(myLevel.solution_path)} steps of the solution have been shown.")
        
        drawLevel(myLevel.getMatrix())

def regenerate_solution_from_current_state():
    """Regenerate a solution path from the current game state"""
    global myLevel, hint_step_index
    
    if not myLevel or not myLevel.is_pcg:
        return
    
    # Get the current matrix state
    current_matrix = myLevel.getMatrix()
    
    # Use the solver to find a new solution from the current state
    new_solution = pcg_generator.solve_sokoban_bfs(current_matrix)
    
    if new_solution:
        print(f"New solution found from current state with {len(new_solution)} steps.")
        myLevel.solution_path = new_solution
        hint_step_index = 0  # Reset hint index for the new solution
    else:
        print("Could not find a solution from the current state. The level might be unsolvable from here.")
        # If no solution found, reset the level
        myLevel.resetLevel()
        hint_step_index = 0
        drawLevel(myLevel.getMatrix())
        
        # Try to find solution for the reset level
        new_solution = pcg_generator.solve_sokoban_bfs(myLevel.getMatrix())
        if new_solution:
            myLevel.solution_path = new_solution
            print(f"Level reset. New solution found with {len(new_solution)} steps.")
        else:
            print("Warning: Could not find solution even after reset. Using fallback level.")
            # If still no solution, use a fallback level
            fallback_matrix, fallback_solution = pcg_generator.get_fallback_level()
            
            # Verify fallback is solvable
            verification = pcg_generator.solve_sokoban_bfs(fallback_matrix)
            if not verification:
                print("Critical error: Fallback level failed verification!")
                # Use the simplest possible fallback as last resort
                fallback_matrix = [
                    ['#', '#', '#', '#', '#'],
                    ['#', '@', '$', '.', '#'],
                    ['#', ' ', ' ', ' ', '#'],
                    ['#', '#', '#', '#', '#']
                ]
                fallback_solution = ['R', 'R']
            
            myLevel = Level(source=fallback_matrix, level_specifier="pcg", 
                           is_pcg=True, solution_path=fallback_solution)
            drawLevel(myLevel.getMatrix())

def cycle_theme():
    """Cycle through available themes"""
    global theme, current_theme_index, available_themes, myLevel
    current_theme_index = (current_theme_index + 1) % len(available_themes)
    theme = available_themes[current_theme_index]
    print(f"Theme changed to: {theme}")
    if myLevel and myLevel.getMatrix():
        drawLevel(myLevel.getMatrix())

# --- Main Game Setup and Loop ---
if __name__ == '__main__':
    pygame.init()
    myEnvironment = Environment()
    screen_width, screen_height = myEnvironment.size
    pygame.display.set_caption("pySokoban - PCG Enhanced")

    # Start with a PCG level for immediate testing
    initLevel(is_pcg=True, new_pcg_level=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: movePlayer("L")
                elif event.key == pygame.K_RIGHT: movePlayer("R")
                elif event.key == pygame.K_UP: movePlayer("U")
                elif event.key == pygame.K_DOWN: movePlayer("D")
                elif event.key == pygame.K_u:  # Undo
                    if myLevel.getLastMatrix():
                        drawLevel(myLevel.getMatrix())
                elif event.key == pygame.K_r:  # Restart
                    myLevel.resetLevel()
                    hint_step_index = 0
                    drawLevel(myLevel.getMatrix())
                elif event.key == pygame.K_n:  # New level
                    initLevel(is_pcg=True, new_pcg_level=True)
                elif event.key == pygame.K_h:  # Hint
                    show_hint()
                elif event.key == pygame.K_t:  # Cycle theme
                    cycle_theme()
        
        pygame.time.wait(10)
    
    pygame.quit()
    sys.exit()

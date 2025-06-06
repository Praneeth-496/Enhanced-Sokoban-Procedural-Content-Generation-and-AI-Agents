"""
Enhanced Sokoban PCG Generator with improved randomization and validation
Focuses solely on generating guaranteed solvable levels
"""

import random
import collections
import copy
import time
import os

# Define level elements
WALL = '#'
FLOOR = ' '
PLAYER = '@'
BOX = '$'
GOAL = '.'
BOX_ON_GOAL = '*'
PLAYER_ON_GOAL = '+' # Player on a goal square

# --- Guaranteed Solvable Fallback Levels ---
# Diverse, verified solvable levels as fallbacks
FALLBACK_LEVELS = [
    # Simple 5x5 level
    (
        [
            ['#','#','#','#','#'],
            ['#','@',' ',' ','#'],
            ['#',' ','$','.','#'],
            ['#',' ',' ',' ','#'],
            ['#','#','#','#','#']
        ],
        ['D', 'R'] 
    ),
    # 6x6 level with 2 boxes
    (
        [
            ['#','#','#','#','#','#'],
            ['#',' ',' ',' ',' ','#'],
            ['#','@','$',' ','.','#'],
            ['#',' ','$',' ','.','#'],
            ['#',' ',' ',' ',' ','#'],
            ['#','#','#','#','#','#']
        ],
        ['R', 'R', 'D', 'R', 'U', 'L', 'D', 'R']
    ),
    # 7x7 level with 3 boxes
    (
        [
            ['#','#','#','#','#','#','#'],
            ['#',' ',' ',' ',' ',' ','#'],
            ['#',' ','$',' ','$',' ','#'],
            ['#',' ','.','@','.','$','#'],
            ['#',' ',' ',' ',' ','.','#'],
            ['#',' ',' ',' ',' ',' ','#'],
            ['#','#','#','#','#','#','#']
        ],
        ['L', 'U', 'R', 'R', 'D', 'L', 'L', 'U', 'R', 'R', 'D', 'R']
    ),
    # More complex 7x7 level with obstacles
    (
        [
            ['#','#','#','#','#','#','#'],
            ['#',' ',' ',' ',' ',' ','#'],
            ['#',' ','#','#','#',' ','#'],
            ['#','@','$',' ','$','.','#'],
            ['#',' ','#','#','#','.','#'],
            ['#',' ',' ',' ',' ','.','#'],
            ['#','#','#','#','#','#','#']
        ],
        ['R', 'R', 'R', 'U', 'L', 'L', 'D', 'R', 'R', 'U', 'L', 'D', 'L', 'U', 'R', 'R', 'D']
    ),
    # 8x8 level with multiple rooms
    (
        [
            ['#','#','#','#','#','#','#','#'],
            ['#',' ',' ','#',' ',' ',' ','#'],
            ['#',' ','$','#','$',' ',' ','#'],
            ['#',' ',' ',' ',' ',' ',' ','#'],
            ['#','#','#',' ','#','#',' ','#'],
            ['#','.','.','.','@',' ',' ','#'],
            ['#',' ',' ',' ',' ',' ',' ','#'],
            ['#','#','#','#','#','#','#','#']
        ],
        ['U', 'U', 'U', 'L', 'L', 'D', 'R', 'U', 'L', 'D', 'D', 'R', 'U', 'U', 'R', 'R', 'R', 'D', 'L', 'U', 'L', 'D', 'L', 'U', 'R', 'D']
    )
]

# --- Helper Functions for Solver and Generator ---

def get_player_and_boxes_positions(matrix):
    """Extract player position and box positions from the level matrix"""
    player_pos = None
    box_positions = []
    for r, row in enumerate(matrix):
        for c, char in enumerate(row):
            if char == PLAYER or char == PLAYER_ON_GOAL:
                player_pos = (r, c)
            elif char == BOX or char == BOX_ON_GOAL:
                box_positions.append((r, c))
    return player_pos, box_positions

def get_goal_positions(matrix):
    """Extract goal positions from the level matrix"""
    goal_positions = []
    for r, row in enumerate(matrix):
        for c, char in enumerate(row):
            if char == GOAL or char == BOX_ON_GOAL or char == PLAYER_ON_GOAL:
                goal_positions.append((r, c))
    return goal_positions

def is_level_solved(box_positions, goal_positions):
    """Check if all boxes are on goals"""
    if not box_positions or not goal_positions: 
        return False
    
    # Convert to sets for comparison if they're not already
    box_set = set(box_positions) if not isinstance(box_positions, set) else box_positions
    goal_set = set(goal_positions) if not isinstance(goal_positions, set) else goal_positions
    
    # Check if all boxes are on goals
    return len(box_set) == len(goal_set) and box_set == goal_set

def detect_simple_deadlocks(matrix):
    """
    Detect simple deadlock squares - squares from which a box can never reach a goal
    Returns a set of coordinates representing deadlock squares
    """
    rows, cols = len(matrix), len(matrix[0])
    goal_positions = get_goal_positions(matrix)
    
    # Create a copy of the matrix without boxes for deadlock detection
    clean_matrix = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if matrix[r][c] == BOX:
                row.append(FLOOR)
            elif matrix[r][c] == BOX_ON_GOAL:
                row.append(GOAL)
            else:
                row.append(matrix[r][c])
        clean_matrix.append(row)
    
    # Mark all squares from which a box can be pushed to a goal
    reachable_squares = set()
    
    # For each goal, do a reverse BFS to find all squares from which a box can reach it
    for goal_r, goal_c in goal_positions:
        # Start with the goal square
        queue = collections.deque([(goal_r, goal_c)])
        visited = set([(goal_r, goal_c)])
        
        while queue:
            r, c = queue.popleft()
            reachable_squares.add((r, c))
            
            # Check all four directions
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                # Position of potential box
                box_r, box_c = r + dr, c + dc
                # Position of potential player to push the box
                player_r, player_c = box_r + dr, box_c + dc
                
                # Check if positions are valid
                if not (0 <= box_r < rows and 0 <= box_c < cols and 
                        0 <= player_r < rows and 0 <= player_c < cols):
                    continue
                
                # Check if the box can be pushed from this position
                if (clean_matrix[box_r][box_c] in [FLOOR, GOAL, PLAYER, PLAYER_ON_GOAL] and 
                    clean_matrix[player_r][player_c] in [FLOOR, GOAL, PLAYER, PLAYER_ON_GOAL] and
                    (box_r, box_c) not in visited):
                    
                    visited.add((box_r, box_c))
                    queue.append((box_r, box_c))
    
    # All squares that are not walls and not reachable are deadlock squares
    deadlock_squares = set()
    for r in range(rows):
        for c in range(cols):
            if (clean_matrix[r][c] in [FLOOR, GOAL, PLAYER, PLAYER_ON_GOAL, BOX, BOX_ON_GOAL] and 
                (r, c) not in reachable_squares and 
                (r, c) not in goal_positions):
                deadlock_squares.add((r, c))
    
    return deadlock_squares

def detect_freeze_deadlocks(matrix, box_positions, goal_positions):
    """
    Detect freeze deadlocks - boxes that can never be moved again
    Returns True if there's a freeze deadlock, False otherwise
    """
    rows, cols = len(matrix), len(matrix[0])
    
    # Helper function to check if a box is blocked along an axis
    def is_box_blocked(box_r, box_c, axis, checked_boxes=None):
        if checked_boxes is None:
            checked_boxes = set()
        
        # If we've already checked this box, treat it as blocked to avoid cycles
        if (box_r, box_c) in checked_boxes:
            return True
        
        # Add current box to checked boxes
        checked_boxes.add((box_r, box_c))
        
        # If box is on a goal, it's not considered blocked
        if (box_r, box_c) in goal_positions:
            return False
        
        # Check horizontal axis
        if axis == 'horizontal':
            # Check left and right
            left_blocked = False
            right_blocked = False
            
            # Check left
            if box_c == 0 or matrix[box_r][box_c-1] == WALL:
                left_blocked = True
            elif matrix[box_r][box_c-1] in [BOX, BOX_ON_GOAL]:
                # Recursive check for the box to the left, but check vertical axis
                left_blocked = is_box_blocked(box_r, box_c-1, 'vertical', checked_boxes)
            
            # Check right
            if box_c == cols-1 or matrix[box_r][box_c+1] == WALL:
                right_blocked = True
            elif matrix[box_r][box_c+1] in [BOX, BOX_ON_GOAL]:
                # Recursive check for the box to the right, but check vertical axis
                right_blocked = is_box_blocked(box_r, box_c+1, 'vertical', checked_boxes)
            
            return left_blocked and right_blocked
        
        # Check vertical axis
        else:
            # Check up and down
            up_blocked = False
            down_blocked = False
            
            # Check up
            if box_r == 0 or matrix[box_r-1][box_c] == WALL:
                up_blocked = True
            elif matrix[box_r-1][box_c] in [BOX, BOX_ON_GOAL]:
                # Recursive check for the box above, but check horizontal axis
                up_blocked = is_box_blocked(box_r-1, box_c, 'horizontal', checked_boxes)
            
            # Check down
            if box_r == rows-1 or matrix[box_r+1][box_c] == WALL:
                down_blocked = True
            elif matrix[box_r+1][box_c] in [BOX, BOX_ON_GOAL]:
                # Recursive check for the box below, but check horizontal axis
                down_blocked = is_box_blocked(box_r+1, box_c, 'horizontal', checked_boxes)
            
            return up_blocked and down_blocked
    
    # Check each box for being frozen
    for box_r, box_c in box_positions:
        # Skip boxes on goals
        if (box_r, box_c) in goal_positions:
            continue
        
        # Check if box is blocked along both axes
        horizontal_blocked = is_box_blocked(box_r, box_c, 'horizontal')
        vertical_blocked = is_box_blocked(box_r, box_c, 'vertical')
        
        if horizontal_blocked and vertical_blocked:
            # Box is frozen and not on a goal - deadlock
            return True
    
    return False

def detect_corral_deadlocks(matrix, player_pos, box_positions, goal_positions):
    """
    Detect corral deadlocks - areas the player cannot reach
    Returns True if there's a corral deadlock, False otherwise
    """
    rows, cols = len(matrix), len(matrix[0])
    
    # Find all squares reachable by the player
    reachable = set()
    queue = collections.deque([player_pos])
    reachable.add(player_pos)
    
    while queue:
        r, c = queue.popleft()
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            
            if (0 <= nr < rows and 0 <= nc < cols and 
                matrix[nr][nc] not in [WALL, BOX, BOX_ON_GOAL] and 
                (nr, nc) not in reachable):
                reachable.add((nr, nc))
                queue.append((nr, nc))
    
    # Check if any box is in a corral (not reachable by player from any side)
    for box_r, box_c in box_positions:
        # Skip boxes on goals
        if (box_r, box_c) in goal_positions:
            continue
        
        # Check if any adjacent square is reachable by the player
        box_accessible = False
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = box_r + dr, box_c + dc
            if (0 <= nr < rows and 0 <= nc < cols and (nr, nc) in reachable):
                box_accessible = True
                break
        
        if not box_accessible:
            # Box is in a corral and not on a goal - deadlock
            return True
    
    return False

def has_deadlock(matrix):
    """
    Comprehensive deadlock detection combining all types
    Returns True if any deadlock is detected, False otherwise
    """
    player_pos, box_positions = get_player_and_boxes_positions(matrix)
    goal_positions = get_goal_positions(matrix)
    
    if not player_pos or not box_positions or not goal_positions:
        return True  # Invalid level state
    
    # Check for simple deadlocks
    simple_deadlock_squares = detect_simple_deadlocks(matrix)
    for box_r, box_c in box_positions:
        if (box_r, box_c) in simple_deadlock_squares and (box_r, box_c) not in goal_positions:
            return True
    
    # Check for freeze deadlocks
    if detect_freeze_deadlocks(matrix, box_positions, goal_positions):
        return True
    
    # Check for corral deadlocks
    if detect_corral_deadlocks(matrix, player_pos, box_positions, goal_positions):
        return True
    
    return False

def is_valid_level(matrix):
    """
    Check if a level is valid and solvable
    Returns True if valid, False otherwise
    """
    player_pos, box_positions = get_player_and_boxes_positions(matrix)
    goal_positions = get_goal_positions(matrix)
    
    if not player_pos or not box_positions or not goal_positions:
        return False  # Missing essential elements
    
    if len(box_positions) != len(goal_positions):
        return False  # Mismatched number of boxes and goals
    
    # Check if any boxes start on goals (pre-solved)
    boxes_on_goals = 0
    for box_pos in box_positions:
        if box_pos in goal_positions:
            boxes_on_goals += 1
    
    # If all boxes are on goals, the level is already solved
    if boxes_on_goals == len(box_positions):
        return False
    
    # Allow at most one box to start on a goal
    if boxes_on_goals > 1:
        return False
    
    # Check for deadlocks
    if has_deadlock(matrix):
        return False
    
    return True

# --- Solvability Checker (BFS) ---

def solve_sokoban_bfs(initial_matrix, max_iterations=100000):
    """
    Solve a Sokoban level using BFS
    Returns the solution path if solvable, None otherwise
    """
    # Convert matrix to tuple format for hashability in visited set
    if isinstance(initial_matrix[0], list):
        initial_matrix_tuple = tuple(tuple(row) for row in initial_matrix)
    else:
        initial_matrix_tuple = initial_matrix
    
    # Extract initial state
    initial_player_pos, initial_box_positions = get_player_and_boxes_positions(initial_matrix_tuple)
    goal_positions = get_goal_positions(initial_matrix_tuple)
    
    if not initial_player_pos or not initial_box_positions or not goal_positions:
        return None
    
    # Check if already solved
    if is_level_solved(initial_box_positions, goal_positions):
        return []
    
    # Initialize BFS
    queue = collections.deque([(initial_matrix_tuple, [])])
    visited = set()
    visited.add((initial_player_pos, tuple(sorted(initial_box_positions))))
    
    iterations = 0
    
    while queue and iterations < max_iterations:
        iterations += 1
        current_matrix_tuple, current_path = queue.popleft()
        
        # Convert to list format for manipulation
        current_matrix = [list(row) for row in current_matrix_tuple]
        
        # Get current state
        current_player_pos, current_box_positions = get_player_and_boxes_positions(current_matrix)
        
        # Try all four directions
        for dr, dc, move_char in [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]:
            # Calculate new player position
            new_player_r, new_player_c = current_player_pos[0] + dr, current_player_pos[1] + dc
            
            # Create a copy of the current matrix for this move
            next_matrix = [row[:] for row in current_matrix]
            
            # Check if new position is valid
            if not (0 <= new_player_r < len(next_matrix) and 0 <= new_player_c < len(next_matrix[0])):
                continue
            
            # Get what's at the new position
            char_at_new_pos = next_matrix[new_player_r][new_player_c]
            
            # Initialize variables for move processing
            valid_move = False
            new_box_positions = current_box_positions.copy()
            
            # Process move based on what's at the new position
            if char_at_new_pos in [FLOOR, GOAL]:
                # Simple move to empty space or goal
                valid_move = True
                next_matrix[new_player_r][new_player_c] = PLAYER_ON_GOAL if char_at_new_pos == GOAL else PLAYER
                next_matrix[current_player_pos[0]][current_player_pos[1]] = GOAL if next_matrix[current_player_pos[0]][current_player_pos[1]] == PLAYER_ON_GOAL else FLOOR
            
            elif char_at_new_pos in [BOX, BOX_ON_GOAL]:
                # Try to push a box
                pushed_box_r, pushed_box_c = new_player_r + dr, new_player_c + dc
                
                # Check if push destination is valid
                if not (0 <= pushed_box_r < len(next_matrix) and 0 <= pushed_box_c < len(next_matrix[0])):
                    continue
                
                char_beyond_box = next_matrix[pushed_box_r][pushed_box_c]
                
                if char_beyond_box in [FLOOR, GOAL]:
                    valid_move = True
                    
                    # Update box position in the list
                    new_box_positions.remove((new_player_r, new_player_c))
                    new_box_positions.append((pushed_box_r, pushed_box_c))
                    
                    # Update matrix
                    next_matrix[pushed_box_r][pushed_box_c] = BOX_ON_GOAL if char_beyond_box == GOAL else BOX
                    next_matrix[new_player_r][new_player_c] = PLAYER_ON_GOAL if char_at_new_pos == BOX_ON_GOAL else PLAYER
                    next_matrix[current_player_pos[0]][current_player_pos[1]] = GOAL if next_matrix[current_player_pos[0]][current_player_pos[1]] == PLAYER_ON_GOAL else FLOOR
            
            if valid_move:
                # Convert matrix back to tuple for hashability
                next_matrix_tuple = tuple(tuple(row) for row in next_matrix)
                
                # Create state key for visited set
                state_key = (new_player_r, new_player_c), tuple(sorted(new_box_positions))
                
                if state_key not in visited:
                    # Check if this move solves the level
                    if is_level_solved(new_box_positions, goal_positions):
                        return current_path + [move_char]
                    
                    # Check for deadlocks in the new state
                    if has_deadlock(next_matrix):
                        continue
                    
                    # Add to visited and queue
                    visited.add(state_key)
                    queue.append((next_matrix_tuple, current_path + [move_char]))
    
    # No solution found within iteration limit
    return None

# --- Reverse Play Generation ---

def reverse_play_from_goal(matrix, num_boxes):
    """
    Generate a level by starting from the goal state and working backwards
    This guarantees the level is solvable
    Returns the generated level matrix and solution path
    """
    rows, cols = len(matrix), len(matrix[0])
    goal_positions = get_goal_positions(matrix)
    
    if not goal_positions or len(goal_positions) != num_boxes:
        return None, None
    
    # Create a clean matrix with just walls, floors, and goals
    clean_matrix = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if matrix[r][c] in [WALL, FLOOR, GOAL]:
                row.append(matrix[r][c])
            elif matrix[r][c] == PLAYER or matrix[r][c] == PLAYER_ON_GOAL:
                row.append(FLOOR)  # Remove player for now
            else:
                row.append(FLOOR)  # Remove boxes for now
        clean_matrix.append(row)
    
    # Place boxes on goals (solved state)
    for goal_r, goal_c in goal_positions:
        clean_matrix[goal_r][goal_c] = BOX_ON_GOAL
    
    # Find a valid player position (adjacent to at least one box)
    player_placed = False
    player_pos = None
    
    # Try to place player adjacent to a box
    for goal_r, goal_c in goal_positions:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_r, adj_c = goal_r + dr, goal_c + dc
            if (0 <= adj_r < rows and 0 <= adj_c < cols and 
                clean_matrix[adj_r][adj_c] == FLOOR):
                clean_matrix[adj_r][adj_c] = PLAYER
                player_placed = True
                player_pos = (adj_r, adj_c)
                break
        if player_placed:
            break
    
    # If no position adjacent to a box, find any valid position
    if not player_placed:
        for r in range(rows):
            for c in range(cols):
                if clean_matrix[r][c] == FLOOR:
                    clean_matrix[r][c] = PLAYER
                    player_placed = True
                    player_pos = (r, c)
                    break
            if player_placed:
                break
    
    if not player_placed:
        return None, None  # Couldn't place player
    
    # Perform reverse moves (pull boxes away from goals)
    solution_path = []
    current_matrix = [row[:] for row in clean_matrix]
    
    # Target number of steps - aim for a reasonable challenge
    target_steps = random.randint(15, 30)
    
    steps_taken = 0
    max_attempts = target_steps * 10  # Allow multiple attempts per desired step
    attempts = 0
    
    while steps_taken < target_steps and attempts < max_attempts:
        attempts += 1
        
        # Get current player position and box positions
        player_pos, box_positions = get_player_and_boxes_positions(current_matrix)
        if not player_pos or not box_positions:
            break
        
        # Try to pull a box (reverse of pushing)
        valid_pulls = []
        
        for box_r, box_c in box_positions:
            # Check each direction for potential pull
            for dr, dc, move_char in [(-1, 0, 'D'), (1, 0, 'U'), (0, -1, 'R'), (0, 1, 'L')]:
                # Position where player would be to pull the box
                player_r, player_c = box_r + dr, box_c + dc
                
                # Position where box would end up after pull
                new_box_r, new_box_c = box_r - dr, box_c - dc
                
                # Check if positions are valid
                if not (0 <= player_r < rows and 0 <= player_c < cols and 
                        0 <= new_box_r < rows and 0 <= new_box_c < cols):
                    continue
                
                # Check if player position is valid (must be current player position)
                if (player_r, player_c) != player_pos:
                    continue
                
                # Check if new box position is valid (must be floor or goal)
                if current_matrix[new_box_r][new_box_c] not in [FLOOR, GOAL]:
                    continue
                
                # Create a temporary matrix to check for deadlocks after the pull
                temp_matrix = [row[:] for row in current_matrix]
                
                # Update box position in temp matrix
                is_box_on_goal = temp_matrix[box_r][box_c] == BOX_ON_GOAL
                is_new_pos_goal = temp_matrix[new_box_r][new_box_c] == GOAL
                
                temp_matrix[new_box_r][new_box_c] = BOX_ON_GOAL if is_new_pos_goal else BOX
                temp_matrix[box_r][box_c] = GOAL if is_box_on_goal else FLOOR
                
                # Check if this pull would create a deadlock
                if has_deadlock(temp_matrix):
                    continue
                
                # This is a valid pull
                valid_pulls.append((box_r, box_c, new_box_r, new_box_c, move_char))
        
        if not valid_pulls:
            # Try to move player to a position where pulls might be possible
            possible_moves = []
            for dr, dc, move_char in [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]:
                new_r, new_c = player_pos[0] + dr, player_pos[1] + dc
                if (0 <= new_r < rows and 0 <= new_c < cols and 
                    current_matrix[new_r][new_c] in [FLOOR, GOAL]):
                    possible_moves.append((new_r, new_c, move_char))
            
            if possible_moves:
                new_r, new_c, move_char = random.choice(possible_moves)
                
                # Update player position
                is_current_pos_goal = current_matrix[player_pos[0]][player_pos[1]] == PLAYER_ON_GOAL
                is_new_pos_goal = current_matrix[new_r][new_c] == GOAL
                
                current_matrix[new_r][new_c] = PLAYER_ON_GOAL if is_new_pos_goal else PLAYER
                current_matrix[player_pos[0]][player_pos[1]] = GOAL if is_current_pos_goal else FLOOR
                
                # Add move to solution path (in reverse)
                opposite_moves = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}
                solution_path.append(opposite_moves[move_char])
                steps_taken += 1
            continue
        
        # Choose a random valid pull
        box_r, box_c, new_box_r, new_box_c, move_char = random.choice(valid_pulls)
        
        # Execute the pull
        is_box_on_goal = current_matrix[box_r][box_c] == BOX_ON_GOAL
        is_new_pos_goal = current_matrix[new_box_r][new_box_c] == GOAL
        
        # Update box position
        current_matrix[new_box_r][new_box_c] = BOX_ON_GOAL if is_new_pos_goal else BOX
        current_matrix[box_r][box_c] = GOAL if is_box_on_goal else FLOOR
        
        # Add move to solution path (in reverse)
        solution_path.append(move_char)
        steps_taken += 1
    
    # Check if we've made enough moves
    if steps_taken < 10:  # Require at least 10 steps for a meaningful puzzle
        return None, None
    
    # Verify the level is solvable
    solution_check = solve_sokoban_bfs(current_matrix)
    if not solution_check:
        return None, None
    
    # Verify the level is valid (not pre-solved, no deadlocks)
    if not is_valid_level(current_matrix):
        return None, None
    
    return current_matrix, solution_path

# --- Level Generation Logic ---

def create_empty_level(rows, cols):
    """Create an empty level with floor tiles"""
    return [[FLOOR for _ in range(cols)] for _ in range(rows)]

def add_outer_walls(matrix):
    """Add outer walls to the level"""
    rows, cols = len(matrix), len(matrix[0])
    
    # Add top and bottom walls
    for c in range(cols):
        matrix[0][c] = WALL
        matrix[rows-1][c] = WALL
    
    # Add left and right walls
    for r in range(rows):
        matrix[r][0] = WALL
        matrix[r][cols-1] = WALL

def generate_internal_walls(matrix, complexity=0.3):
    """Generate internal walls with variable complexity"""
    rows, cols = len(matrix), len(matrix[0])
    if rows <= 4 or cols <= 4: return
    
    # Random walk approach for wall generation
    num_walks = int((rows + cols) * complexity)
    walk_length_factor = complexity
    
    for _ in range(num_walks):
        start_r, start_c = random.randint(1, rows-2), random.randint(1, cols-2)
        current_r, current_c = start_r, start_c
        max_walk_len = int((rows + cols) * walk_length_factor)

        for _ in range(max_walk_len):
            if 1 <= current_r < rows-1 and 1 <= current_c < cols-1:
                if matrix[current_r][current_c] == FLOOR: 
                    matrix[current_r][current_c] = WALL
            else: break

            dr, dc = random.choice([(-1,0), (1,0), (0,-1), (0,1)])
            next_r, next_c = current_r + dr, current_c + dc

            if 1 <= next_r < rows-1 and 1 <= next_c < cols-1:
                current_r, current_c = next_r, next_c
            else:
                current_r, current_c = random.randint(1, rows-2), random.randint(1, cols-2)

def place_goals(matrix, num_goals):
    """Place goals in the level"""
    rows, cols = len(matrix), len(matrix[0])
    goal_positions = []
    
    # Find cells that are near walls or in corners for more interesting gameplay
    corner_or_wall_cells = []
    for r_idx in range(1, rows - 1):
        for c_idx in range(1, cols - 1):
            if matrix[r_idx][c_idx] == FLOOR:
                wall_count = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if matrix[r_idx + dr][c_idx + dc] == WALL:
                        wall_count += 1
                if wall_count >= 1:  # At least one adjacent wall
                    corner_or_wall_cells.append((r_idx, c_idx))
    
    # Place goals near walls when possible
    goals_placed = 0
    random.shuffle(corner_or_wall_cells)
    for r, c in corner_or_wall_cells:
        if goals_placed >= num_goals:
            break
        matrix[r][c] = GOAL
        goal_positions.append((r, c))
        goals_placed += 1
    
    # If we couldn't place all goals near walls, place remaining randomly
    if goals_placed < num_goals:
        possible_cells = []
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if matrix[r][c] == FLOOR:
                    possible_cells.append((r, c))
        
        random.shuffle(possible_cells)
        for r, c in possible_cells:
            if goals_placed >= num_goals:
                break
            matrix[r][c] = GOAL
            goal_positions.append((r, c))
            goals_placed += 1
    
    return goal_positions

def check_level_connectivity(matrix):
    """Check if all floor tiles are connected"""
    rows, cols = len(matrix), len(matrix[0])
    
    # Find a floor tile to start from
    start_pos = None
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] in [FLOOR, GOAL, PLAYER, PLAYER_ON_GOAL, BOX, BOX_ON_GOAL]:
                start_pos = (r, c)
                break
        if start_pos:
            break
    
    if not start_pos:
        return False
    
    # BFS to find all reachable tiles
    visited = set([start_pos])
    queue = collections.deque([start_pos])
    
    while queue:
        r, c = queue.popleft()
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and 
                matrix[nr][nc] in [FLOOR, GOAL, PLAYER, PLAYER_ON_GOAL, BOX, BOX_ON_GOAL] and 
                (nr, nc) not in visited):
                visited.add((nr, nc))
                queue.append((nr, nc))
    
    # Count all non-wall tiles
    all_non_wall = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] in [FLOOR, GOAL, PLAYER, PLAYER_ON_GOAL, BOX, BOX_ON_GOAL]:
                all_non_wall += 1
    
    # Check if all non-wall tiles are reachable
    return len(visited) == all_non_wall

# --- Seed management for consistent generation ---
def set_random_seed():
    """Set a random seed based on current time to ensure different runs"""
    seed = int(time.time() * 1000) % 10000000
    random.seed(seed)
    return seed

def generate_level():
    """
    Generate a Sokoban level
    Uses reverse-play method to guarantee solvability
    """
    # Set a new random seed for each generation attempt
    seed = set_random_seed()
    
    # Randomize level size and number of boxes
    rows = random.randint(7, 10)
    cols = random.randint(7, 10)
    num_boxes = random.randint(1, 3)  # Simplified for better success rate
    
    # Maximum attempts for generation
    max_attempts = 100
    for attempt in range(max_attempts):
        if attempt % 10 == 0:
            print(f"Generation attempt {attempt+1}/{max_attempts}...")
            # Change seed slightly for each batch of attempts
            random.seed(seed + attempt)
        
        # Create empty level
        matrix = create_empty_level(rows, cols)
        
        # Generate layout
        add_outer_walls(matrix)
        complexity = random.uniform(0.1, 0.3)  # Lower complexity for better success
        generate_internal_walls(matrix, complexity)
        
        # Check connectivity
        if not check_level_connectivity(matrix):
            continue
        
        # Place goals
        place_goals(matrix, num_boxes)
        
        # Generate level using reverse-play
        final_matrix, solution_path = reverse_play_from_goal(matrix, num_boxes)
        
        if final_matrix and solution_path:
            # Final validation
            if (check_level_connectivity(final_matrix) and 
                is_valid_level(final_matrix) and 
                solve_sokoban_bfs(final_matrix)):
                return final_matrix, solution_path
    
    # If generation failed after max attempts, use fallback
    print(f"Failed to generate a suitable level after {max_attempts} attempts. Using fallback.")
    return get_fallback_level()

# --- Fallback Level Selection ---

# Track last used fallback to avoid repetition
last_fallback_index = -1

def get_fallback_level():
    """Get a fallback level if generation fails"""
    global last_fallback_index
    
    # Reset random seed for consistent fallback behavior
    random.seed(int(time.time()))
    
    # Create a list of verified fallback levels
    verified_fallbacks = []
    
    # Test each fallback level
    for idx, (fallback_matrix, fallback_solution) in enumerate(FALLBACK_LEVELS):
        # Make a deep copy to avoid modifying the original
        test_matrix = [row[:] for row in fallback_matrix]
        
        # Verify the fallback level is solvable
        if solve_sokoban_bfs(test_matrix):
            verified_fallbacks.append(idx)
    
    # If no fallbacks are verified, use emergency fallback
    if not verified_fallbacks:
        print("CRITICAL: All fallbacks failed verification. Using emergency fallback level.")
        emergency_level = [
            ['#', '#', '#', '#', '#'],
            ['#', '@', '$', '.', '#'],
            ['#', ' ', ' ', ' ', '#'],
            ['#', '#', '#', '#', '#']
        ]
        emergency_solution = ['R', 'R']
        return emergency_level, emergency_solution
    
    # Select a fallback that hasn't been used recently
    possible_indices = [i for i in verified_fallbacks if i != last_fallback_index]
    if not possible_indices:
        chosen_fallback_index = verified_fallbacks[0]
    else:
        chosen_fallback_index = random.choice(possible_indices)
    
    last_fallback_index = chosen_fallback_index
    fallback_matrix_template, fallback_solution_template = FALLBACK_LEVELS[chosen_fallback_index]
    
    # Make a deep copy to avoid modifying the original
    fallback_matrix = [row[:] for row in fallback_matrix_template]
    fallback_solution = list(fallback_solution_template)
    
    # Double-check the fallback level is solvable
    verification = solve_sokoban_bfs(fallback_matrix)
    if not verification:
        print(f"WARNING: Fallback level {chosen_fallback_index} verification failed!")
        
        # Try another fallback if this one fails
        for idx in verified_fallbacks:
            if idx != chosen_fallback_index:
                alt_matrix, alt_solution = FALLBACK_LEVELS[idx]
                alt_matrix_copy = [row[:] for row in alt_matrix]
                if solve_sokoban_bfs(alt_matrix_copy):
                    print(f"Using alternative fallback level {idx} instead.")
                    return [row[:] for row in alt_matrix], list(alt_solution)
        
        # If all fallbacks fail, use the simplest possible level as last resort
        print("CRITICAL: All fallbacks failed verification. Using emergency fallback level.")
        emergency_level = [
            ['#', '#', '#', '#', '#'],
            ['#', '@', '$', '.', '#'],
            ['#', ' ', ' ', ' ', '#'],
            ['#', '#', '#', '#', '#']
        ]
        emergency_solution = ['R', 'R']
        return emergency_level, emergency_solution
    
    return fallback_matrix, fallback_solution

# --- Simple levels for guaranteed success ---
def get_simple_level():
    """Get a simple level that's guaranteed to work"""
    simple_levels = [
        # Very simple 5x5 level
        (
            [
                ['#','#','#','#','#'],
                ['#','@',' ',' ','#'],
                ['#',' ','$','.','#'],
                ['#',' ',' ',' ','#'],
                ['#','#','#','#','#']
            ],
            ['D', 'R', 'R'] 
        ),
        # Simple 6x6 level
        (
            [
                ['#','#','#','#','#','#'],
                ['#',' ',' ',' ',' ','#'],
                ['#','@','$',' ','.','#'],
                ['#',' ',' ',' ',' ','#'],
                ['#',' ',' ',' ',' ','#'],
                ['#','#','#','#','#','#']
            ],
            ['R', 'R', 'R']
        ),
        # Simple 7x7 level
        (
            [
                ['#','#','#','#','#','#','#'],
                ['#',' ',' ',' ',' ',' ','#'],
                ['#',' ',' ',' ',' ',' ','#'],
                ['#',' ','@','$','.','#','#'],
                ['#',' ',' ',' ',' ',' ','#'],
                ['#',' ',' ',' ',' ',' ','#'],
                ['#','#','#','#','#','#','#']
            ],
            ['R', 'R']
        )
    ]
    
    # Choose a random simple level
    idx = random.randint(0, len(simple_levels) - 1)
    level_matrix, solution = simple_levels[idx]
    
    # Verify it's solvable (it should be)
    verification = solve_sokoban_bfs(level_matrix)
    if not verification:
        # If somehow it's not solvable, use the emergency fallback
        print("WARNING: Simple level verification failed! Using emergency fallback.")
        emergency_level = [
            ['#', '#', '#', '#', '#'],
            ['#', '@', '$', '.', '#'],
            ['#', ' ', ' ', ' ', '#'],
            ['#', '#', '#', '#', '#']
        ]
        emergency_solution = ['R', 'R']
        return emergency_level, emergency_solution
    
    return [row[:] for row in level_matrix], list(solution)

if __name__ == '__main__':
    print("--- Testing Sokoban PCG Generator ---")
    for i in range(3):  # Test generation 3 times
        print(f"\nTest run {i+1}/3:")
        level_data, sol_path = generate_level()
        if level_data:
            for r_idx, r_val in enumerate(level_data):
                print("" + "".join(r_val))
            print(f"  Solution path length: {len(sol_path) if sol_path else 'None'}")
            
            # Verify the level is solvable
            verification = solve_sokoban_bfs(level_data)
            if verification:
                print(f"  Verification: Level is solvable (solution length: {len(verification)})")
            else:
                print(f"  WARNING: Level verification failed!")
            
            # Check if it's a fallback level
            is_fallback = False
            for idx, fallback in enumerate(FALLBACK_LEVELS):
                fallback_matrix = fallback[0]
                if len(level_data) == len(fallback_matrix) and all(len(row) == len(fallback_matrix[i]) for i, row in enumerate(level_data)):
                    if all(level_data[i][j] == fallback_matrix[i][j] for i in range(len(level_data)) for j in range(len(level_data[i]))):
                        print(f"  (Used fallback index: {idx})")
                        is_fallback = True
                        break
            
            if not is_fallback:
                print("  (Generated new level)")
        else:
            print("  Could not generate level.")

"""
Level class for Sokoban game
Handles level loading, state management, and solution tracking
"""

import copy
import os

class Level:
    def __init__(self, source=None, level_specifier=None, is_pcg=False, solution_path=None):
        self.matrix = []
        self.history = []
        self.is_pcg = is_pcg
        self.solution_path = solution_path if solution_path else []
        self.original_matrix = None
        
        if is_pcg and isinstance(source, list):
            # PCG level - source is the level matrix
            self.matrix = copy.deepcopy(source)
            self.original_matrix = copy.deepcopy(source)
        elif not is_pcg and isinstance(source, str):
            # File level - source is the level set name, level_specifier is the level number
            self.loadLevel(source, level_specifier)
        else:
            raise ValueError("Invalid source format for level initialization")
    
    def loadLevel(self, level_set, level_num):
        """Load a level from file"""
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Construct the path to the levels directory
            levels_dir = os.path.join(current_dir, 'levels')
            
            # Construct the path to the specific level file
            level_file = os.path.join(levels_dir, f'{level_set}_{level_num}.txt')
            
            # Read the level file
            with open(level_file, 'r') as f:
                self.matrix = [list(line.strip()) for line in f.readlines() if line.strip()]
            
            # Store the original matrix for reset
            self.original_matrix = copy.deepcopy(self.matrix)
            
        except Exception as e:
            print(f"Error loading level: {e}")
            # Create a simple default level if loading fails
            self.matrix = [
                ['#', '#', '#', '#', '#'],
                ['#', '@', ' ', '$', '#'],
                ['#', ' ', ' ', '.', '#'],
                ['#', '#', '#', '#', '#']
            ]
            self.original_matrix = copy.deepcopy(self.matrix)
    
    def getMatrix(self):
        """Return the current level matrix"""
        return self.matrix
    
    def getSize(self):
        """Return the size of the level (width, height)"""
        if not self.matrix:
            return 0, 0
        return len(self.matrix[0]), len(self.matrix)
    
    def getPlayerPosition(self):
        """Find and return the player's position (x, y)"""
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell == '@' or cell == '+':
                    return x, y
        return None
    
    def addToHistory(self, matrix):
        """Add the current state to history for undo functionality"""
        self.history.append(copy.deepcopy(matrix))
        # Limit history size to prevent memory issues
        if len(self.history) > 100:
            self.history.pop(0)
    
    def getLastMatrix(self):
        """Get the previous state from history (for undo)"""
        if self.history:
            self.matrix = self.history.pop()
            return self.matrix
        return None
    
    def resetLevel(self):
        """Reset the level to its original state"""
        self.matrix = copy.deepcopy(self.original_matrix)
        self.history = []
        return self.matrix
    
    def isSolved(self):
        """Check if the level is solved (all boxes on goals)"""
        # Count boxes and goals
        boxes = 0
        goals = 0
        boxes_on_goals = 0
        
        for row in self.matrix:
            for cell in row:
                if cell == '$':
                    boxes += 1
                elif cell == '.':
                    goals += 1
                elif cell == '*':
                    boxes_on_goals += 1
                    boxes += 1
                    goals += 1
        
        # Level is solved if all boxes are on goals
        return boxes == goals == boxes_on_goals
    
    def regenerate_solution(self):
        """Regenerate solution path from current state"""
        if not self.is_pcg:
            return False
        
        try:
            # Import here to avoid circular imports
            import pcg_generator
            
            # Get a new solution from the current state
            new_solution = pcg_generator.solve_sokoban_bfs(self.matrix)
            
            if new_solution:
                self.solution_path = new_solution
                return True
            return False
        except Exception as e:
            print(f"Error regenerating solution: {e}")
            return False

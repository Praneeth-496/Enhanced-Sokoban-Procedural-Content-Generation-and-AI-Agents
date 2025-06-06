# Enhanced Sokoban: Procedural Content Generation and AI Agents

A comprehensive implementation of the classic puzzle game Sokoban, featuring procedural level generation, intelligent hint systems, and AI solving agents.

## Project Overview

This project enhances the traditional Sokoban puzzle game with three key innovations:

1. **Procedural Content Generation (PCG)** - A hybrid system that creates diverse, solvable levels across three difficulty tiers (easy, medium, hard)
2. **Intelligent Hint Mechanism** - A dynamic guidance system that adapts to player moves and provides real-time solution paths
3. **AI Solving Agents** - Two distinct approaches to automated puzzle solving:
   - Heuristic agent based on breadth-first search
   - Monte Carlo Tree Search (MCTS) agent

## Features

### Procedural Level Generation
- Hybrid approach combining constructive and search-based methods
- Guaranteed solvability through breadth-first search verification
- Sophisticated deadlock detection (simple, freeze, and corral deadlocks)
- Difficulty scaling based on solution length and complexity
- Fallback mechanism with pre-designed levels

### Hint System
- Dynamic solution path generation
- Real-time adaptation to player moves
- Step-by-step guidance
- Visual highlighting of suggested moves

### AI Agents
- **Heuristic Agent**:
  - Breadth-first search with optimization
  - Deadlock detection for early termination
  - Memory-efficient state representation
  
- **MCTS Agent**:
  - Simulation-based planning
  - Balanced exploration and exploitation
  - Heuristic evaluation for node selection

### Game Implementation
- Character-based matrix representation
- Clean separation between game logic and presentation
- Traditional Sokoban movement mechanics
- Undo functionality and state tracking

## Technical Implementation

### Game Structure
- **Level Class**: Manages game state, history, and validation
- **Environment Class**: Handles rendering and user interface
- **PCG System**: Generates and verifies puzzle levels
- **Solver Classes**: Implements AI agents and hint generation

### Deadlock Detection
The system detects three types of deadlocks:
1. **Simple Deadlocks**: Boxes pushed into corners or against walls
2. **Freeze Deadlocks**: Boxes forming immovable patterns
3. **Corral Deadlocks**: Complex configurations where boxes block each other

### Algorithms
- Breadth-First Search (BFS) for level verification and heuristic solving
- Monte Carlo Tree Search (MCTS) for advanced AI agent
- Reverse BFS for deadlock detection

## Requirements

- Python 3.7+
- Pygame 2.0+
- NumPy
- OpenAI Gym (for additional agent testing)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/enhanced-sokoban.git
cd enhanced-sokoban

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Usage

### Playing the Game
- Arrow keys for movement
- R to reset level
- Z to undo move
- H to request a hint
- N to generate a new level
- 1-3 to select difficulty (1=Easy, 2=Medium, 3=Hard)

### Running AI Agents
```bash
# Run the heuristic agent
python run_agent.py --agent heuristic --level [level_file]

# Run the MCTS agent
python run_agent.py --agent mcts --level [level_file]

# Compare agents
python compare_agents.py --levels [level_directory]
```

## Project Structure

```
enhanced-sokoban/
├── src/
│   ├── game/
│   │   ├── level.py          # Level representation and mechanics
│   │   ├── environment.py    # Game rendering and UI
│   │   └── utils.py          # Helper functions
│   ├── pcg/
│   │   ├── generator.py      # Level generation algorithms
│   │   ├── verifier.py       # Solvability checking
│   │   └── deadlock.py       # Deadlock detection
│   ├── agents/
│   │   ├── heuristic.py      # BFS-based agent
│   │   ├── mcts.py           # MCTS agent
│   │   └── common.py         # Shared agent functionality
│   └── hint/
│       └── hint_system.py    # Dynamic hint generation
├── assets/
│   ├── themes/               # Visual themes
│   └── levels/               # Pre-designed fallback levels
├── tests/                    # Unit and integration tests
├── main.py                   # Game entry point
├── run_agent.py              # Script to run agents
└── compare_agents.py         # Agent comparison tool
```

## Authors

- Jiameng Ma (s4255445)
- Praneeth Dathu (s4174089)
- SriVagdevi Viswanadha (s4417712)
- Yesmina el Arkoubi (s2989018)
- Gaurisankar Jayadas (s4374886)
- Mulakkayala Sai Krishna Reddy (s4238206)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original Sokoban concept by Hiroyuki Imabayashi
- University of Leiden, Gaming AI course


# Enhanced Sokoban: Procedural Generation and Search Agents

A Python and Pygame project exploring procedural content generation and
search-based agents for Sokoban.

The project extends a Sokoban game with randomized puzzle generation,
solvability checks, deadlock detection, interactive hints, and automated
solution playback.

Developed as a group project for the Gaming AI course at Leiden University.

## Overview

Sokoban is a grid-based puzzle in which the player pushes boxes onto target
positions. Boxes can be pushed but cannot be pulled, making planning and
deadlock avoidance central to solving a level.

This project explores two related tasks:

- Generating varied puzzles and checking whether a solution can be found.
- Using search algorithms to produce and execute sequences of moves.

The repository includes an interactive game, a BFS-based agent, and an
agent implementation that combines a BFS-first strategy with an MCTS fallback.

## Features

### Procedural Level Generation

The generator combines randomized layouts, reverse-play construction,
and validation.

The current configuration generates candidate boards with:

- Between 7 and 10 rows and columns.
- Between 1 and 3 boxes.
- Randomized internal walls.
- Connectivity and level-validity checks.
- BFS-based solvability verification.
- Predefined fallback levels when generation attempts are exhausted.

Generation is bounded by attempt and search limits. Fallback boards may
differ from the dimensions used for randomly generated candidates.

### Search and Deadlock Detection

The shared BFS solver explores reachable puzzle states and records move
sequences.

The code includes checks for:

- Simple deadlocks.
- Freeze deadlocks.
- Corral deadlocks.

These checks support generation and search by identifying problematic
box configurations.

### Interactive Gameplay

The Pygame interface provides:

- Keyboard movement.
- Undo and restart.
- Generation of new puzzles.
- Solution-based hints.
- Theme switching.

The hint system can recompute a solution from the current state. If recovery
fails, its handling may reset or replace the puzzle.

### Automated Agents

| Agent | Implementation |
|---|---|
| BFS agent | `heuristic_agent.py` calls the shared BFS solver and plays back the returned moves. |
| BFS-first/MCTS agent | `mcts_agent.py` first attempts BFS, then uses MCTS if BFS returns no solution. |

The MCTS implementation includes tree selection, expansion, random
simulations, reward propagation, and exploration–exploitation balancing.

Despite its filename, `heuristic_agent.py` uses BFS rather than A*.
Likewise, `mcts_agent.py` is not a standalone MCTS-only baseline because
it attempts BFS first.

## Repository Files

| File | Purpose |
|---|---|
| `sokoban.py` | Interactive game and keyboard controls |
| `pcg_generator.py` | Level generation, validation, deadlock checks, and BFS solver |
| `heuristic_agent.py` | BFS-based agent and visual solution playback |
| `mcts_agent.py` | BFS-first agent with an MCTS fallback |
| `Level.py` | Level representation, state history, reset, and solution tracking |
| `Environment.py` | Pygame initialization, display, and resource paths |
| `README_RUN_INSTRUCTIONS.md` | Additional run notes; some controls describe an earlier version |
| `pySokoban_Enhanced_Final.zip` | Packaged project archive |
| `LICENSE` | GNU General Public License, version 2 |

## Requirements

- Python 3; the supplied run notes identify Python 3.11 as a tested version.
- Pygame.
- A graphical desktop environment.
- Theme image assets for rendering.

The visible Python source files use Pygame and Python's standard library.
NumPy and OpenAI Gym are not required by these files.

## Setup

Clone the repository:

```bash
git clone https://github.com/Praneeth-496/Enhanced-Sokoban-Procedural-Content-Generation-and-AI-Agents.git
cd Enhanced-Sokoban-Procedural-Content-Generation-and-AI-Agents
```

Optionally create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
source .venv/bin/activate
```

Install Pygame:

```bash
python -m pip install pygame
```

### Required Rendering Assets

The scripts expect theme images under paths such as:

```text
themes/default/images/wall.png
themes/default/images/box.png
themes/default/images/box_on_target.png
themes/default/images/space.png
themes/default/images/target.png
themes/default/images/player.png
```

The configured theme names are `default`, `ksokoban`, and `soft`.

The current repository root does not expose a `themes/` directory.
Before launching the graphical programs, obtain the required assets and
place them beside the Python files. Check the included project archive
for the packaged resources.

Installing Pygame alone does not resolve missing image files.

## Running the Programs

Once the required assets are available, run commands from the directory
containing the Python files.

### Interactive Game

```bash
python sokoban.py
```

### BFS-Based Agent

```bash
python heuristic_agent.py
```

### BFS-First Agent with MCTS Fallback

```bash
python mcts_agent.py
```

The agent scripts provide their own graphical execution loops.

## Controls

### Interactive Game

| Key | Action |
|---|---|
| Arrow keys | Move the player |
| `U` | Undo the previous move |
| `R` | Restart the current level |
| `N` | Generate a new level |
| `H` | Apply a solution-based hint |
| `T` | Cycle through themes |
| Window close button | Exit |

### Agent Windows

| Key | Action |
|---|---|
| `N` | Generate a new level |
| `T` | Cycle through themes |
| `Esc` | Exit |

The current interactive game does not implement the `1`, `2`, and `3`
difficulty-selection keys described in older documentation.

## Level Representation

Levels use a character-based matrix:

| Symbol | Meaning |
|---|---|
| `#` | Wall |
| Space | Empty floor |
| `@` | Player |
| `$` | Box |
| `.` | Goal |
| `*` | Box on a goal |
| `+` | Player on a goal |

`Level.py` manages the board state, move history, reset behavior, and
stored solution paths.

## Limitations

- BFS can become expensive as puzzle size and complexity increase.
- Search limits mean that failure to find a solution does not prove a
  puzzle is unsolvable.
- MCTS rollout and iteration limits affect the returned move sequence;
  it should not be assumed to solve every puzzle.
- The BFS-first MCTS implementation requires modification before it can
  support a controlled BFS-versus-MCTS comparison.
- Graphical execution requires theme assets not exposed in the current
  repository root.
- The repository does not currently include an automated benchmark suite
  or test directory.

## Authors

- Jiameng Ma
- Praneeth Dathu
- SriVagdevi Viswanadha
- Yesmina el Arkoubi
- Gaurisankar Jayadas
- Mulakkayala Sai Krishna Reddy

## Acknowledgments

- The original Sokoban concept by Hiroyuki Imabayashi.
- The pySokoban project on which this implementation builds.
- The Gaming AI course at Leiden University.

## License

See [LICENSE](LICENSE), which contains the GNU General Public License,
version 2.

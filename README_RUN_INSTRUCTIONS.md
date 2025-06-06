# pySokoban with Enhanced PCG - How to Run

This document provides instructions on how to run the modified pySokoban game with Procedural Content Generation (PCG) features, including recent enhancements to level generation, difficulty scaling, and the hint system.

## Prerequisites

- Python 3 (tested with Python 3.11)
- Pygame library

## Installation

1.  **Ensure Python 3 is installed.**
2.  **Install Pygame:**
    Open your terminal or command prompt and run:
    ```bash
    pip3 install pygame
    ```
    If you encounter permission issues, you might need to use:
    ```bash
    pip3 install --user pygame
    ```

## Running the Game

1.  **Navigate to the Game Directory:**
    Open your terminal or command prompt and change to the directory where you extracted the game files (e.g., `pySokoban/pySokoban-1/`).
    ```bash
    cd path/to/pySokoban/pySokoban-1/
    ```

2.  **Run the Game Script:**
    Execute the main game file using Python 3:
    ```bash
    python3 sokoban.py
    ```
    (Or `python3.11 sokoban.py` if you have a specific version linked).

## Gameplay Controls

-   **Arrow Keys (Up, Down, Left, Right):** Move the player.
-   **U Key:** Undo the last move.
-   **R Key:** Restart the current level from the beginning.
-   **Escape Key:** Quit the game.

## PCG and Feature Controls

-   **1 Key:** Generate and play a new **Easy** difficulty PCG level.
-   **2 Key:** Generate and play a new **Medium** difficulty PCG level.
-   **3 Key:** Generate and play a new **Hard** difficulty PCG level.
-   **N Key:** Generate a new PCG level of the *current* PCG difficulty. If not currently on a PCG level, it will default to generating a new Easy level.
-   **H Key:** Show a hint for the current PCG level. Pressing H will apply the next step of a known, pre-calculated solution. You can use hints repeatedly to step through the entire solution path for the generated level.
-   **T Key:** Cycle through available game themes (Default, KSokoban, Soft). The display will update immediately with the new theme.

## Notes on PCG Levels (Enhanced)

-   **Solvability:** All PCG-generated levels are guaranteed to be solvable. The system includes a solver that verifies this before presenting the level.
-   **Variety and Difficulty Progression:** The PCG algorithms for Easy, Medium, and Hard difficulties have been significantly overhauled based on Sokoban design research. This aims to produce more varied and appropriately challenging levels with a clear progression in difficulty.
    -   **Easy:** Smaller grids, fewer boxes (1-2), open spaces, shorter solutions (5-20 moves).
    -   **Medium:** Moderate grids, more boxes (3-4), some corridors/rooms, moderate solutions (15-45 moves).
    -   **Hard:** Larger grids, even more boxes (4-5), complex layouts, longer solutions (40-85+ moves).
-   **High Attempt Rate for Unique Levels:** The generator now makes a very high number of attempts (750) to create a unique level for the selected difficulty, significantly minimizing the chance of seeing a fallback level.
-   **Non-Repetitive Fallback:** In the extremely rare event that the generator cannot create a suitable random level, it will use a fallback mechanism that draws from a small pool of pre-designed simple levels, ensuring you don't get the exact same fallback level repeatedly.
-   **Hints:** Hints are based on one complete solution path found by the internal solver during level generation. Pressing 'H' will guide you step-by-step through that specific solution until the level is solved (if you follow the hints). The hint system will indicate when all steps of that pre-calculated path have been shown.

Enjoy playing the enhanced pySokoban!


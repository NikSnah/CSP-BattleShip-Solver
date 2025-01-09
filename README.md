# CSP-BattleShip-Solver

This project is a **Constraint Satisfaction Problem (CSP) solver** designed to solve Battleship puzzles efficiently. Battleship puzzles involve placing ships of varying sizes on a grid, adhering to rules about ship placements and constraints for each row and column. This solver uses **backtracking** and **constraint propagation** to solve the puzzles.

---

## Features

- **CSP Framework**: Built to handle generic constraint satisfaction problems.
- **Battleship-Specific Constraints**: Ensures correct ship placements and adheres to Battleship rules.
- **Backtracking Search**: Implements a backtracking algorithm for efficient exploration of possible solutions.
- **Constraint Propagation**: Prunes the search space by propagating constraints dynamically.

---

## File Overview

### **1. `csp.py`**
- Implements the **CSP framework**.
- Provides methods for variable assignment, domain reduction, and checking constraints.
- Can be extended to solve other CSPs beyond Battleship.

### **2. `constraints.py`**
- Defines **constraints** for Battleship puzzles, including:
  - Row and column constraints.
  - Non-overlapping rules for ships.
  - Adjacency constraints to ensure ships are not touching.
- Modular constraint implementation for flexibility.

### **3. `battle.py`**
- Battleship-specific implementation of the CSP solver.
- Includes:
  - Grid setup and initialization.
  - Ship configuration details (e.g., sizes and counts).
  - Input parsing for Battleship puzzles.
- Visualizes solutions on the grid.

### **4. `backtracking.py`**
- Implements the **backtracking search algorithm**.
- Integrates with the CSP framework to:
  - Assign variables.
  - Propagate constraints.
  - Undo changes dynamically during search.
- Optimized with heuristics like:
  - Minimum Remaining Values (MRV).
  - Least Constraining Value (LCV).

---

## How It Works

1. **Input a Battleship Puzzle**:
   - Define the puzzle grid, row and column constraints, and the number of ships.
   - Input can be provided through a file or directly in the script.

2. **CSP Initialization**:
   - Variables represent possible ship placements on the grid.
   - Domains include valid ship configurations.
   - Constraints are added to ensure a valid solution.

3. **Backtracking Search**:
   - Recursively assigns variables while ensuring consistency with constraints.
   - Uses heuristics and constraint propagation to reduce search space.

4. **Output the Solution**:
   - Displays the solved Battleship grid.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/username/csp-battleship-solver.git
   cd csp-battleship-solver
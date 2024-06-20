# Minesweeper Hint System
The project aims to develop a Minesweeper hint system using constraint
programming (**Minizinc**) to not only solve the puzzle but also calculate the probability of a grid being a mine. The system will continuously update the probability as more
hint numerals (The number that the game shows to the player to indicate how many mines
are in the 3 by 3 blocks with the numbered block as the centre) are discovered.
## Objectives
### Primary
1. **Deterministic Solver:** using Constraint Programming (CP) to play Minesweeper
    - Makes a constraint models that captures Minesweeper's rules'
    - Use use the model to solve the board with the given hints
    - Iterativey call the solver to solve the game until no grid is certain
2. **Calculate Probability:** use CP to Calculate Probability for a Grid to be a Mine
    - Design a method of using the MiniZinc model to calculate Probability
    - Evaluate the performace
### Secondary
1. **User Interface Colour Display:** Create a UI that the use different colour to
display where there is definitely no mine and where there is definitely a mine as well as display gradual difference in colour base on the probability that a mine is present in the grid
2. **Difficulty Selection:** player should be able to select difficulties at the beginning of the program
3. **Solver and Display Selection:**provide options for users to choose between running the solving the game with deterministic algorithm or display the deterministic grids on the user interface
### Future Objective
1. **Evaluation:** Do some user testing of the artefact (let some students use it and collect
feedback). Then evaluate the feedback from user testing and improve the artefact.

## Installation
In order to run the code, the user will need to use the package manager [pip](https://pip.pypa.io/en/stable/) to install Minizinc and Tkinter.
```bash
pip install minizinc
pip install tk
```


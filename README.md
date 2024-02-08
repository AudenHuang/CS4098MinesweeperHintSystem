# Minesweeper Hint System
The project aims to develop a Minesweeper hint system using constraint
programming (**Minizinc**) and probability. The system will continuously update the probability as more
hint numerals (The number that the game shows to the player to indicate how many mines
are in the 3 by 3 blocks with the numbered block as the centre) are discovered.
## Objectives
### Primary
1. **Calculate Probability:** Understanding how to identify the probability of there being a
mine for the unselect section.
2. **Implementing Constraint:** Make a constraint programming model for the
minesweeper hint system.
3. **Update Constraint:** The model’s constraint should be update as more hint numerals
are discovered.
### Secondary
1. **Displaying Mines and Safe Zone:** Create a UI that the use different colour to
display where there is definitely no mine and where there is definitely a mine
2. **Displaying Probability of Having a Mine:** Update the UI so that it display gradual
difference in colour base on the probability that there is a mine around the discovered
section
### Future Objective
1. **Evaluation:** Do some user testing of the artefact (let some students use it and collect
feedback). Then evaluate the feedback from user testing and improve the artefact.

## Installation
In order to run the code, the user will need to use the package manager [pip](https://pip.pypa.io/en/stable/) to install Minizinc.
```bash
pip install minizinc
```


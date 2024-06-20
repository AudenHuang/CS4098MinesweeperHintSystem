int: Max_Width;
int: Max_Height;
int: Width;
int: Height;

% data from python
array[1..Height,1..Width] of -5..8: grid;


% Decision variable for the output grid
array[ 1..Height,1..Width] of var -4..8: outputgrid;

% Set of valid values for unrevealed cells
set of -2..8: valid_unrevealed = {-2} union 0..8;


% Count Adjacent Mines
function var int: countMines(int: i, int: j) =
  sum([if i+di >= 1 /\ i+di <= Height /\ j+dj >= 1 /\ j+dj <= Width
       then (outputgrid[i+di, j+dj] = -2) else 0 endif 
       | di in -1..1, dj in -1..1]);
       
% Count Adjacent Unrevealed Grids     
function var int: countN3(int: i, int: j) =
  sum([if i+di >= 1 /\ i+di <= Height  /\ j+dj >= 1 /\ j+dj <= Width
       then (outputgrid[i+di, j+dj] = -3) else 0 endif 
       | di in -1..1, dj in -1..1]);
       
% Checking if the input is full board
function bool: fullboard() =
  Width = Max_Width /\ Height = Max_Height;
  
% Set all the value of none target grids in the decision variable to be the same as the input
constraint forall(i in 1..Height, j in  1..Width where grid[i, j] != -1/\ grid[i, j] != -5) (
  outputgrid[i, j] = grid[i,j]
);


% Make sure that unrevealed safe grid are set to a valid safe grid value (for checking if the target grid can be a safe zone)
constraint forall(i in 1..Height, j in  1..Width where grid[i, j] = -5) (
  outputgrid[i, j] in 0..8
);

% Make sure that unreveale blocked are assigned with a valid solution
constraint forall(i in 1..Height, j in  1..Width where grid[i, j] = -1) (
  outputgrid[i, j] in valid_unrevealed
);

%Setting minimum value (constraint 1)
constraint forall(i in 1..Height, j in  1..Width where outputgrid[i,j]>=0)(
  countMines(i, j)<= outputgrid[i, j]
);


% Constraint for fullboard (Setting maximum value)(constraint 2)
  constraint fullboard()->forall(i in 1..Height, j in  1..Width where outputgrid[i,j]>=0) (
   countMines(i, j) +countN3(i,j)>= outputgrid[i, j]
  );

% Constraints for not fullboard input (Setting maximum value)
  % None border grids(constraint 3)
  constraint not fullboard()->forall(i in 2..Height-1, j in 2..Width-1 where outputgrid[i,j]>=0)(
    countMines(i, j) +countN3(i,j)>= outputgrid[i, j]
  );

  % Constraints for the corners (constraint 4)
  constraint not fullboard()/\outputgrid[1, 1] >= 0->(countMines(1, 1) +countN3(1,1)+ 5 >=outputgrid[1, 1]);
  constraint not fullboard()/\outputgrid[Height, 1] >= 0->(countMines(Height, 1) +countN3(Height,1)+ 5 >=outputgrid[Height, 1]);
  constraint not fullboard()/\outputgrid[1, Width] >= 0->(countMines(1, Width) +countN3(1,Width)+ 5 >=outputgrid[1, Width]);
  constraint not fullboard()/\outputgrid[Height, Width] >= 0->(countMines(Height, Width) +countN3(Height,Width)+ 5 >=outputgrid[Height, Width]);

  % Constrants for non corners border case (constraint 5)
  constraint not fullboard()->forall(i in 2..Height-1, j in {1,Width} where outputgrid[i, j] >= 0) (
    countMines(i, j) +countN3(i,j)+ 3 >=outputgrid[i, j]
  );
  constraint not fullboard()->forall(i in {1,Height}, j in 2..Width-1 where outputgrid[i, j] >= 0) (
   countMines(i, j) +countN3(i,j)+ 3 >=outputgrid[i, j]
  );
solve satisfy;






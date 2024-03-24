int: Max_Width;
int: Max_Height;
int: Width;
int: Height;
% int: MineNum;

% data from python
array[1..Height,1..Width] of -5..8: grid;


% Decision variable for the output grid
array[ 1..Height,1..Width] of var -4..8: outputgrid;

% Set of valid values for unrevealed cells
set of -2..8: valid_unrevealed = {-2} union 0..8;


% Count Mines
function var int: countMines(int: i, int: j) =
  sum([if i+di >= 1 /\ i+di <= Height /\ j+dj >= 1 /\ j+dj <= Width
       then (outputgrid[i+di, j+dj] = -2) else 0 endif 
       | di in -1..1, dj in -1..1]);
       
      
function var int: countN3(int: i, int: j) =
  sum([if i+di >= 1 /\ i+di <= Height  /\ j+dj >= 1 /\ j+dj <= Width
       then (outputgrid[i+di, j+dj] = -3) else 0 endif 
       | di in -1..1, dj in -1..1]);
       
% Set the values for the decision variable
constraint forall(i in 1..Height, j in  1..Width where grid[i, j] != -1/\ grid[i, j] != -5) (
  outputgrid[i, j] = grid[i,j]
);

% Make sure that unreveale blocked are assigned with a valid solution
constraint forall(i in 1..Height, j in  1..Width where grid[i, j] = -1) (
  outputgrid[i, j] in valid_unrevealed
);

% Make sure that 100% are set to not a bomb
constraint forall(i in 1..Height, j in  1..Width where grid[i, j] = -5) (
  outputgrid[i, j] in 0..8
);

constraint forall(i in 1..Height, j in  1..Width where outputgrid[i,j]>=0) (
  countMines(i, j) <= outputgrid[i, j]
);

constraint forall(i in 2..Height-1, j in 2..Width-1 where outputgrid[i,j]>=0)(
  countMines(i, j) +countN3(i,j)>= outputgrid[i, j]
);

constraint forall(i in 1..Height, j in {1,Width} where outputgrid[i, j] >= 0/\Width=Max_Width/\Height=Max_Height) (
 countMines(i, j) +countN3(i,j)>= outputgrid[i, j]
);

constraint forall(i in {1,Height}, j in 2..Width-1 where outputgrid[i, j] >= 0/\Width=Max_Width/\Height=Max_Height) (
 countMines(i, j) +countN3(i,j)>= outputgrid[i, j]
);

% constraint (Width = Max_Width /\ Height = Max_Height) -> 
%   sum([if outputgrid[i, j] = -2 then 1 else 0 endif | i in 1..Height, j in 1..Width]) <= MineNum;

solve satisfy;





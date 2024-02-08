%takes in 3 blocks to up, down, left, right to the targetting blocks
int: Width;
int: Height;

% data from python
array[1..Width, 1..Height] of -4..8: grid;


% Decision variable for the output grid
array[1..Width, 1..Height] of var -4..8: outputgrid;

% Set of valid values for unrevealed cells
set of -2..8: valid_unrevealed = {-2} union 0..8;

% Set the values for the decision variable
constraint forall(i in 1..Width, j in 1..Height where grid[i, j] != -1) (
  outputgrid[i, j] = grid[i,j]
);

% Make sure that unreveale blocked are assigned with a valid solution
constraint forall(i in 1..Width, j in 1..Height where grid[i, j] = -1) (
  outputgrid[i, j] in valid_unrevealed
);


% Count Mines
function var int: countMines(int: i, int: j) =
  sum([if i+di >= 1 /\ i+di <= Width /\ j+dj >= 1 /\ j+dj <= Height 
       then (outputgrid[i+di, j+dj] = -2) else 0 endif 
       | di in -1..1, dj in -1..1]);

function var int: countN3(int: i, int: j) =
  sum([if i+di >= 1 /\ i+di <= Width /\ j+dj >= 1 /\ j+dj <= Height 
       then (outputgrid[i+di, j+dj] = -3) else 0 endif 
       | di in -1..1, dj in -1..1]);
       
constraint forall(i in 2..Width-1, j in 2..Height-1 where outputgrid[i,j]>=0)(
  countMines(i, j) <= outputgrid[i, j] /\ countMines(i, j) +countN3(i,j)>= outputgrid[i, j]
);

constraint forall(i in {1,Width}, j in 1..Height where outputgrid[i, j] >= 0) (
  countMines(i, j) <= outputgrid[i, j]
);

constraint forall(i in 2..Width-1, j in {1,Height} where outputgrid[i, j] >= 0) (
  countMines(i, j) <= outputgrid[i, j]
);

solve satisfy;

%For debug
output[show(outputgrid[1,1..7]),"\n"];
output[show(outputgrid[2,1..7]),"\n"];
output[show(outputgrid[3,1..7]),"\n"];
output[show(outputgrid[4,1..7]),"\n"];
output[show(outputgrid[5,1..7]),"\n"];
output[show(outputgrid[6,1..7]),"\n"];
output[show(outputgrid[7,1..7]),"\n"];





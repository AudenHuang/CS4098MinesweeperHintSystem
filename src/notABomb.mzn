%takes in 3 blocks to up, down, left, right to the targetting blocks
int: Width = 7;
int: Height = 7;

% data from python
array[1..Width, 1..Height] of -4..8: grid;


% Decision variable for the output grid
array[1..Width, 1..Height] of var -4..8: outputgrid;

% Set of valid values for unrevealed cells
set of -2..8: valid_unrevealed = {-2} union 0..8;

% Set the values for the decision variable
constraint forall(i in 1..Width, j in 1..Height where grid[i, j] != -1 /\ grid[i, j] != -3) (
  outputgrid[i, j] = grid[i,j]
);
constraint forall(i in 1..Width, j in 1..Height where grid[i, j] = -1) (
  outputgrid[i, j] in valid_unrevealed
);

% Make sure that out of bound are set to not a bomb
constraint forall(i in 1..Width, j in 1..Height where grid[i, j] = -3) (
  outputgrid[i, j] in 0..8
);

% Count Mines
function var int: countMines(int: i, int: j) =
  sum([if i+di >= 1 /\ i+di <= Width /\ j+dj >= 1 /\ j+dj <= Height 
       then (outputgrid[i+di, j+dj] = -2) else 0 endif 
       | di in -1..1, dj in -1..1]);
       
function var int: countMinus4(int: i, int: j) =
  sum([if i+di >= 1 /\ i+di <= Width /\ j+dj >= 1 /\ j+dj <= Height 
       then (outputgrid[i+di, j+dj] = -4) else 0 endif 
       | di in -1..1, dj in -1..1]);
       

constraint forall(i in 2..Width-1, j in 2..Height-1 where outputgrid[i, j] >= 0) (
  countMines(i, j) = outputgrid[i, j]
);

constraint forall(i in {1,Width}, j in 1..Height where outputgrid[i, j] >= 0) (
  countMines(i, j) <= outputgrid[i, j]
);
constraint forall(i in 2..Width-1, j in {1,Height} where outputgrid[i, j] >= 0) (
  countMines(i, j) <= outputgrid[i, j]
);

% constraint forall(i in 1..Width, j in 1..Height where outputgrid[i,j]>=0)(
%     if countMinus4(i,j) > 0 then
%       countMines(i, j) <= outputgrid[i, j]
%     else
%       countMines(i, j) == outputgrid[i, j]
%     endif
% );



solve satisfy;

%For debug
output[show(outputgrid[1,1..7]),"\n"];
output[show(outputgrid[2,1..7]),"\n"];
output[show(outputgrid[3,1..7]),"\n"];
output[show(outputgrid[4,1..7]),"\n"];
output[show(outputgrid[5,1..7]),"\n"];
output[show(outputgrid[6,1..7]),"\n"];
output[show(outputgrid[7,1..7]),"\n"];





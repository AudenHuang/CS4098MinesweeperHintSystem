import math
import os
import sys
from tkinter import *
from DifficultyDialog import *
from FieldButton import *
from MZSolver import *
from BoardSizePopup import *
import random
# import minizinc
from minizinc import Status
import numpy as np
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed

class Minesweeper:
    '''Minesweeper Class:
        The game board is a list of lists:

        [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

        such that board[i][i] is the FieldButton (object) that built to represent
        the grid i,j of the game board. (by default indexed from (0,0) to (10,10))

    '''
    
    def __init__(self, master, row_size, col_size, mines_amount):
        '''Initializes the Minesweeper game with a specified size and number of mines.

            :param master: Tkinter widget or the main window object
            :param row_size: Number of rows in the minesweeper grid
            :param col_size: Number of columns in the minesweeper grid
            :param mines_amount: Total number of mines to be placed on the grid
        '''
        self.frame = Frame(master)
        self.frame.pack(padx=20, pady=20)
        self.dataflag = False
        self.hintCertain = False
        self.win = 0

        # Default game setting is 16x16 with 40 mines.
        self.row_size = row_size
        self.col_size = col_size

        self.mines_amount = mines_amount
        self.remaining_mines = self.mines_amount
        self.flags = 0
        self.is_over = False
        self.grids = []
        self.mines = []
        self.board = []
    
        self.current_board = np.full((self.row_size, self.col_size), -1)
        self.prob = np.full((self.row_size, self.col_size), -1)
        #K. Brünnler, "Minesweeper-CSP-Solver," GitHub Repository, 2020. [Online]. Available: https://github.com/kqb/Minesweeper-CSP-Solver
        self.first_click = True
        self.first_click_grid = None        
        # Initialize images for newgame grids.
        self.img_sun_normal = PhotoImage(file = "images/img_sun_normal.gif")
        self.img_sun_normal_press = PhotoImage(file = "images/img_sun_normal_press.gif")
        self.img_sun_move = PhotoImage(file = "images/img_sun_move.gif")
        self.img_sun_win = PhotoImage(file = "images/img_sun_win.gif")
        self.img_sun_lose = PhotoImage(file = "images/img_sun_lose.gif")
        
        # Initialize images for game grids.
        self.images = {}
        self.images['blank'] = PhotoImage(file = "images/img_blank.gif")
        self.images['mine'] = PhotoImage(file = "images/img_mine.gif")
        self.images['hit_mine'] = PhotoImage(file = "images/img_hit_mine.gif")
        self.images['flag'] = PhotoImage(file = "images/img_flag.gif")
        self.images['wrong'] = PhotoImage(file = "images/img_wrong_mine.gif")
        self.images['no'] = []
        self.images['prob'] = []
        #--------------------------------- modified plus my own code -----------------
        for i in range(0, 12):
            self.images['prob'].append(PhotoImage(file = "images/img_prob_"+str(i)+".gif"))
            if i< 9:
                self.images['no'].append(PhotoImage(file = "images/img_"+str(i)+".gif"))
    

        # Read test boards if it's not empty
        if not board:
            self.init_board()

        # Initialize newgame button.
        self.newgame_button = Button(self.frame, image = self.img_sun_normal)
        self.newgame_button.grid(row = 0, column = 1, columnspan = self.col_size)
        self.newgame_button.bind("<Button-1>", lambda Button: self.newgame())

        # Initialize remaining mines labels.
        self.remain_label = Label(self.frame, text = "remainng mines: ")
        self.remain_label.grid(row = self.row_size+2, column = 1, columnspan = 4, sticky=W)
        self.remain_label2 = Label(self.frame, text = self.mines_amount)
        self.remain_label2.grid(row = self.row_size+2, column = 5, columnspan = self.row_size, sticky=W)

        self.control_frame = Frame(self.frame)
        self.control_frame.grid(row=self.row_size+7, column=self.col_size+2, padx=10, pady=10)
        
        # Initialize Hint  button.
        self.base_row = self.row_size + 3 
        self.solvecomp_button = Button(self.control_frame , text="Hint_Solve_Iterative")
        self.solvecomp_button.grid(row=0, column=0, columnspan=max(self.col_size // 3, 1), sticky=W+E)
        self.solvecomp_button.bind("<Button-1>", lambda Button: self.hint_solve())

        self.solvecurrent_button = Button(self.control_frame , text="Hint_Solve_Current")
        self.solvecurrent_button.grid(row=1, column=0, columnspan=max(self.col_size // 3, 1), sticky=W+E)
        self.solvecurrent_button.bind("<Button-1>", lambda Button: self.hint_solve_current())

        self.show_certain_button = Button(self.control_frame , text="Hint_Certain")
        self.show_certain_button.grid(row=2, column=0, columnspan=max(self.col_size // 3, 1), sticky=W+E)
        self.show_certain_button.bind("<Button-1>", lambda Button: self.hint_show_certain())

        self.showprob_button = Button(self.control_frame , text=" Show_Prob ")
        self.showprob_button.grid(row=3, column=0, columnspan=max(self.col_size // 3, 1), sticky=W+E)
        self.showprob_button.bind("<Button-1>", lambda Button: self.hint_prob())

        self.showprob_smart_button= Button(self.control_frame , text=" Show_Prob_Smart ")
        self.showprob_smart_button.grid(row=4, column=0, columnspan=max(self.col_size // 3, 1), sticky=W+E)
        self.showprob_smart_button.bind("<Button-1>", lambda Button: self.hint_prob_smart(7,7))


        #For testing different dimention of the smart prob solver
        # self.showprob_smart_test_button= Button(self.control_frame , text=" Test ")
        # self.showprob_smart_test_button.grid(row=5, column=0, columnspan=max(self.col_size // 3, 1), sticky=W+E)
        # self.showprob_smart_test_button.bind("<Button-1>", lambda Button: self.on_show_prob_smart_grid_click())


        self.open_button = Button(self.control_frame , text="All_Certain")
        self.open_button.bind("<Button-1>", lambda Button: self.open_mark_certain())

        self.hide_hints_button = Button(self.control_frame , text="Hide_Hints")
        self.hide_hints_button.bind("<Button-1>", lambda Button: self.hide_hints())

        

        # Create the scrollable text area
        self.output_text = Text(self.frame , height=10, width=50)
        self.output_text.grid(row=self.row_size+7, column=1, columnspan=self.col_size, sticky="nsew")

        # Create a Scrollbar and attach it to the text area
        scrollbar = Scrollbar(self.frame , command=self.output_text.yview)
        scrollbar.grid(row=self.row_size+7, column=self.col_size+1,sticky='nsew')
        self.output_text['yscrollcommand'] = scrollbar.set
        self.output_text.bind("<Key>", self.make_text_read_only)
        # Unmute if you want to enable the first click to be a mine
        # self.init_random_mines()

    def make_text_read_only(self, event):
        '''Prevents user from typing in the output text area, making it read-only.
        
        :param event: The event that triggers this function
        '''
        return "break"

    def newgame(self):
        '''Sets up the board for a new game, resetting all relevant game state variables.'''
        self.win = 0
        # self.game_times += 1
        # self.init_board()
        self.current_board = np.full((self.row_size, self.col_size), -1)
        self.prob = np.full((self.row_size, self.col_size), -1)
        self.first_click = True
        self.first_click_grid = None
        self.is_over = False
        self.flags = 0
        self.remaining_mines = self.mines_amount
        self.mines = []
        # Reset all grids.
        for grid in self.grids:
            grid.reset()
            grid.bind('<Button-1>', self.lclicked_wrapper(grid))
            grid.bind('<Button-2>', self.rclicked_wrapper(grid))
        self.remain_label2.config(text=self.remaining_mines)
        self.newgame_button.config(image=self.img_sun_normal)
        
        self.solvecomp_button.grid(row=self.base_row, column=0, sticky=W+E)
        self.solvecurrent_button.grid(row=self.base_row+1, column=0, sticky=W+E)
        self.show_certain_button.grid(row=self.base_row+2, column=0, sticky=W+E)
        self.showprob_button.grid(row=self.base_row+3, column=0, sticky=W+E)
        self.showprob_smart_button.grid(row=self.base_row + 4, column=0, sticky=W+E)
        self.output_text.delete('1.0', END)
        self.open_button.grid_remove()
        self.hide_hints_button.grid_remove()
        # self.showprob_smart_test_button.grid(row=self.base_row + 5, column=0, sticky=W+E)
        # Unmute if you want to enable the first click to be a mine
        # self.init_random_mines()

    #K. Brünnler, "Minesweeper-CSP-Solver," GitHub Repository, 2020. [Online]. Available: https://github.com/kqb/Minesweeper-CSP-Solver
    def init_board(self):

        '''Initialize game board with grids.
        The board is a list of lists, inner lists' elements are FieldButton object.
        [ [ ],
        [ ],
        ...]
        '''

        # Create labels for row indices
        for row in range(self.row_size):
            row_label = Label(self.frame, text=str(row))
            row_label.grid(row=row+2, column=0, padx=(10, 0))

        # Create labels for column indices
        for col in range(self.col_size):
            col_label = Label(self.frame, text=str(col))
            col_label.grid(row=1, column=col+1, pady=(0, 10))

        for row in range(self.row_size):
            lis = []
            for col in range(self.col_size):
                grid = FieldButton(col, row, self.frame, self.images)
                # first row grid for new game button
                grid.grid(row=row+2, column=col+1)
                lis.append(grid)
                self.grids.append(grid)
            self.board.append(lis)
        # Bind LMB and RMB actions to grid.
        for grid in self.grids:
            grid.bind('<Button-1>', self.lclicked_wrapper(grid))
            grid.bind('<Button-2>', self.rclicked_wrapper(grid))

    #K. Brünnler, "Minesweeper-CSP-Solver," GitHub Repository, 2020. [Online]. Available: https://github.com/kqb/Minesweeper-CSP-Solver
    def init_random_mines(self):
        '''Initialize mines randomly.
        '''
        mines = self.mines_amount
        while mines:
            # Mute if you want to enable the first xlick to be a mine
            grids = self.get_adjecent_grids(self.first_click_grid.y, self.first_click_grid.x, self.row_size,self.col_size,self.board)
            grids.append(self.first_click_grid)
            #--------------------------------------------------------
            
            #flag to check if random coordinates matches the initial click's 9 grids
            match = True    
            row = None
            col = None
            while match:
                row = random.choice(range(self.row_size))
                col = random.choice(range(self.col_size))
                match = False 
                # Mute if you want to enable the first click to be a mine
                for b in grids:
                    if (row == b.y) and (col == b.x):
                        match = True
                        break
                #--------------------------------------------------------
                        
            if self.board[row][col].place_mine():
                self.mines.append(self.board[row][col])
                self.update_surrounding_grids(row, col, 1)
                mines -= 1

        
    #K. Brünnler, "Minesweeper-CSP-Solver," GitHub Repository, 2020. [Online]. Available: https://github.com/kqb/Minesweeper-CSP-Solver
    def get_adjecent_grids(self, row, col, r_size, c_size,input):
        '''Return a list of surrounding grids of grid at row and col in board.

        :param row: int
        :param col: int
        :param r_size: int
        :param c_size: int
        :param input: a 2D array
        :return: list of grids
        '''

        SURROUNDING = ((-1, -1), (-1,  0), (-1,  1),
                       (0 , -1),           (0 ,  1),
                       (1 , -1), (1 ,  0), (1 ,  1))

        neighbours = []

        for pos in SURROUNDING:
            temp_row = row +pos[0]
            temp_col = col + pos[1]
            # if 0 <= temp_row < self.row_size and 0 <= temp_col < self.col_size:
            #     neighbours.append(self.board[temp_row][temp_col])
            if 0 <= temp_row < r_size and 0 <= temp_col < c_size:
                neighbours.append(input[temp_row][temp_col])
        return neighbours

    #K. Brünnler, "Minesweeper-CSP-Solver," GitHub Repository, 2020. [Online]. Available: https://github.com/kqb/Minesweeper-CSP-Solver
    def update_surrounding_grids(self, row, col, value):
        '''Update surrounding grids' value adding given value.

        :param row: int
        :param col: int
        '''

        cells = self.get_adjecent_grids(row, col,self.row_size,self.col_size,self.board)
        for cell in cells:
            if not cell.is_mine():
                cell.value += value

    #K. Brünnler, "Minesweeper-CSP-Solver," GitHub Repository, 2020. [Online]. Available: https://github.com/kqb/Minesweeper-CSP-Solver
    def lclicked_wrapper(self, grid):
        '''Returns a lambda function that calls `lclicked` with the specified grid. Useful for binding events.
        
        :param grid: The grid cell (FieldButton) to be passed to the `lclicked` method
        '''
        return lambda Button: self.lclicked(grid)

    #K. Brünnler, "Minesweeper-CSP-Solver," GitHub Repository, 2020. [Online]. Available: https://github.com/kqb/Minesweeper-CSP-Solver
    def rclicked_wrapper(self, grid):
        '''Returns a lambda function that calls `rclicked` with the specified grid. Useful for binding events.
        
        :param grid: The grid cell (FieldButton) to be passed to the `rclicked` method
        '''
        return lambda Button: self.rclicked(grid)

    
    def lclicked(self, grid):
        '''Handles left mouse button clicks on a grid cell, revealing the cell or triggering game over.
        :param grid: The grid cell (FieldButton) that was clicked
        '''
        # Mute if you want to enable the first click to be a mine
        if self.first_click == True:
            self.first_click_grid = grid            
            self.init_random_mines()
            self.first_click = False
        #--------------------------------------------------------
            
        
        # Do nothing if it's visible or it's flagged.
        if grid.is_show() or grid.is_flag():
            return

        # Case0: hits a number grid, show the grid.
        grid.show()
        # Case1: hits a mine, game over.
        if grid.is_mine():
            grid.show_hit_mine()
            self.newgame_button.config(image=self.img_sun_lose)
            self.gameover()
        # Case2: hits an empty grid, keep showing surrounding grids until all not empty.
        elif grid.value == 0:
            grids = [grid]
            while grids:
                temp_grid = grids.pop()
                surrounding = self.get_adjecent_grids(temp_grid.y, temp_grid.x, self.row_size, self.col_size, self.board)
                for neighbour in surrounding:
                    if not neighbour.is_show() and neighbour.value == 0:
                        grids.append(neighbour)
                    neighbour.show()

        for row in range(self.row_size):
            for col in range(self.col_size):
                grid = self.board[row][col]
                if grid.is_show():
                    self.current_board[row][col] = grid.value

        # Check whether the game wins or not.
        if self.is_win():
            self.win = 1
            self.dataflag = True
            self.gameover()

    #K. Brünnler, "Minesweeper-CSP-Solver," GitHub Repository, 2020. [Online]. Available: https://github.com/kqb/Minesweeper-CSP-Solver
    def rclicked(self, grid):
        '''Handles right mouse button clicks on a grid cell, toggling a flag on the cell.
        :param grid: The grid cell (FieldButton) that was clicked
        '''
                    
        # Do nothing if it's visible.
        if grid.is_show():
            return

        # Flag/Unflag a grid.
        if grid.is_flag():
            grid.flag()
            self.flags -= 1
            self.current_board[grid.y][grid.x] = -1
        else:
            grid.flag()
            self.flags += 1
            self.current_board[grid.y][grid.x] = -2

        # Update remaining mines label.
        self.remaining_mines = (self.mines_amount-self.flags) if self.flags<self.mines_amount else 0
        self.remain_label2.config(text=self.remaining_mines)
        

        if self.is_win():
            self.win = 1
            self.dataflag = True
            self.gameover()

    def gameover(self):
        '''Disable all grids and show all mines.
        '''
        self.is_over = True
        for grid in self.grids:
            if grid.is_mine():
                if not grid.is_flag() and not self.is_win():
                    grid.show()
            elif grid.is_flag():
                grid.show_wrong_flag()
            grid.unbind('<Button-1>')
            grid.unbind('<Button-2>')
        diffculty =""
        if(self.col_size == 30):
            diffculty = "_Expert"
        elif(self.col_size == 16):
            diffculty = "_Intermediate"
        elif(self.col_size == 10):
            diffculty = "_Easy"
        if(not self.win or self.dataflag):
            if self.win:
                self.dataflag = False
            file_path = '../../data/winrate'+diffculty+'.csv'
            self.output_data_winrate(file_path, self.win)

    def is_win(self):
        '''Return True if game wins; False otherwise. The game wins if all grids are either visible or flagged, and
        the amount of flags equals the amount of mines.

        :return: bool
        '''
        for grid in self.grids:
            if not grid.is_show() and not grid.is_mine():
                return False
        self.newgame_button.config(image=self.img_sun_win)
        self.solvecomp_button.grid_remove()
        self.solvecurrent_button.grid_remove()
        self.show_certain_button.grid_remove()
        self.showprob_button.grid_remove()
        self.showprob_smart_button.grid_remove()
        # self.showprob_smart_test_button.grid_remove()
        self.open_button.grid_remove()
        self.hide_hints_button.grid_remove()

        return True

    
    # use for faster testing
    def guess_move(self):
        '''Return an unclick grid.
        :return: grid
        '''
        grids = []
        for grid in self.grids:
            if not grid.is_show() and not grid.is_flag():
                grids.append(grid)
        # If there are shown grid,
        if (self.first_click):
            lowest_prob_grids = grids[0]
            for grid in grids:
                if self.prob[lowest_prob_grids.y][lowest_prob_grids.x] == -1:
                    lowest_prob_grids = grid
                elif self.prob[grid.y][grid.x]<self.prob[lowest_prob_grids.y][lowest_prob_grids.x]:
                    lowest_prob_grids = grid
                return lowest_prob_grids
        return random.choice(grids)

    def has_shown_neighbour(self,row,col):
        '''Checks if a given grid has any revealed neighboring grids.
        
        :param row: Row index of the grid
        :param col: Column index of the grid
        :return: True if there is at least one revealed neighbor, False otherwise
        '''
        adjecent_grids = self.get_adjecent_grids(row,col,self.row_size,self.col_size,self.board)
        for grid in adjecent_grids:
            if grid.is_show():
                return True
        return False
    
    def has_unshown_neighbour(self, row ,col):
        '''Checks if a given grid has any unrevealed neighboring grids.
        
        :param row: Row index of the grid
        :param col: Column index of the grid
        :return: True if there is at least one unrevealed neighbor, False otherwise
        '''
        adjecent_grids = self.get_adjecent_grids(row,col,self.row_size,self.col_size,self.board)
        for grid in adjecent_grids:
            if self.current_board[grid.y][grid.x]== -1:
                return True
        return False
    
    def has_shown_neighbour_input(self,mInput,r,c,row_size,col_size):
        '''Checks in a given 2D array if a specific cell has any "shown" neighboring cells based on certain criteria.
        
        :param mInput: The 2D array representing part or all of the current board state
        :param r: Row index of the cell to check
        :param c: Column index of the cell to check
        :param row_size: Number of rows in the input array
        :param col_size: Number of columns in the input array
        :return: True if there is at least one "shown" neighbor, False otherwise
        '''
        adjecent_grids  = self.get_adjecent_grids(r,c,row_size,col_size,mInput)
        for grid in adjecent_grids:
            if grid >=0:
                return True
        return False
    def unreveal_with_shown_neighbour(self, row, col):
         '''Checks if an unrevealed grid has at least one revealed neighbor.
        
        :param row: Row index of the grid
        :param col: Column index of the grid
        :return: True if the grid has at least one revealed neighbor, False otherwise
        '''
         if self.current_board[row][col]== -1 and self.has_shown_neighbour(row,col):
             return True
         return False
    
    def is_not_certain(self, row, col):
        '''Determines if a grid at a given location has an uncertain status regarding being a mine or not.
        
        :param row: Row index of the grid
        :param col: Column index of the grid
        :return: True if the status of the grid being a mine is uncertain, False if certain
        '''
        if self.prob[row][col] == 100:
            return False
        if self.prob[row][col] == 0:
            return False
        return True
    
    def createInput_partial_board(self, row, col, slice_rows=7, slice_cols=7):
        '''Creates a sliced view of the current board centered around a specific grid for solving a smaller section.
        
        :param row: Row index of the center grid
        :param col: Column index of the center grid
        :param slice_rows: Number of rows in the sliced section
        :param slice_cols: Number of columns in the sliced section
        :return: A 2D numpy array representing the sliced section of the board
        '''
        # Ensure the slice size does not exceed the board dimensions
        slice_rows = min(slice_rows, self.row_size)
        slice_cols = min(slice_cols, self.col_size)
        
        input = np.full((slice_rows, slice_cols), -4)  # Use variable dimensions
        inputprob = np.full((slice_rows, slice_cols), -4)
        # Calculate the half sizes for rows and columns, adjusting for odd/even dimensions
        half_rows = slice_rows // 2
        half_cols = slice_cols // 2
        
        start_r = max(0, row - half_rows)
        end_r = min(self.row_size, row + half_rows + (1 if slice_rows % 2 != 0 else 0))
        start_c = max(0, col - half_cols)
        end_c = min(self.col_size, col + half_cols + (1 if slice_cols % 2 != 0 else 0))
        
        # Adjust the indices for filling the input array
        input_row_start = max(0, half_rows - row)
        input_col_start = max(0, half_cols - col)
        
        inputprob[input_row_start:input_row_start + end_r - start_r, input_col_start:input_col_start + end_c - start_c] = self.prob[start_r:end_r, start_c:end_c].copy()
        input[input_row_start:input_row_start + end_r - start_r, input_col_start:input_col_start + end_c - start_c] = self.current_board[start_r:end_r, start_c:end_c].copy()

        for i in range(slice_rows):
            for j in range(slice_cols):
                if input[i][j] == -1:
                    if self.has_shown_neighbour_input(input, i, j,slice_rows,slice_cols):
                        if inputprob[i][j] == 100:
                            input[i][j] = -2
                        elif inputprob[i][j] == 0:
                            input[i][j] = -5
                    else:
                        input[i][j] = -3
        return input

    
    def createInput_full_board(self):
        '''Creates a full copy of the current board state for solving the entire board.
        
        :return: A 2D numpy array representing the full board state
        '''
        input = self.current_board.copy()
        for i in range(self.row_size):
            for j in range(self.col_size):
                if input[i][j] == -1:
                    if not self.has_shown_neighbour(i,j):
                        input[i][j] = -3
        return input
    
    def hint_solve_current(self):
        '''Solves the current board using hints, making certain moves based on the current probabilities.
        
        :return: A tuple containing the number of flags placed and the number of grids opened
        '''
        self.hintCertain = False
        self.output_text.delete('1.0', END)
        self.open_button.grid_remove()
        self.hide_hints_button.grid_remove()
        self.hint_show_certain()
        flag, open =self.open_mark_certain()
        if not self.is_win() and (flag +open == 0):
            print("no certain grids please check probability")
        else:
            print("flagged ", flag, "grids")
            print("opened ", open, "grids")
        return flag, open

    def hint_solve(self):
        """Function: iterative solve the game by using Minizinc until none of the targets grids is certain.
        """
        self.hintCertain = False
        self.output_text.delete('1.0', END)
        self.open_button.grid_remove()
        self.hide_hints_button.grid_remove()
        self.showprob_button.config(text="Show_Prob")
        self.showprob_smart_button.config(text="Show_Prob_Smart")
        flag,open = self.hint_solve_current()
        if(flag+open!=0):
            self.hint_solve()
        else:
            print("Iterative solve done")
            
    def hint_show_certain(self):
        '''Highlights certain moves based on the current board state without making the moves.
        (Deterministic Algorithm)
        '''
        self.hide_hints_button.grid_remove()
        self.showprob_button.config(text="Show_Prob")
        self.showprob_smart_button.config(text="Show_Prob_Smart")
        self.check_certain_prob()
        is_mine_tasks = {}
        not_mine_tasks = {}
        input_grid = self.createInput_full_board()
        safe = 0
        mine = 0
        with ProcessPoolExecutor() as executor:
            for row in range(self.row_size):
                for col in range(self.col_size):
                    if (input_grid[row][col]== -1):
                        if self.is_not_certain(row,col):
                            modified_input = input_grid.copy()
                            modified_input[row][col]= -2
                            future = executor.submit(MZSolver.solve_minizinc_instance,self.row_size,self.col_size, self.row_size, self.col_size, modified_input)
                            is_mine_tasks[future] = (row, col, modified_input)
            for future in as_completed(is_mine_tasks):
                row, col, grid_data = is_mine_tasks[future]
                status = future.result()
                if status == Status.UNSATISFIABLE:
                    self.prob[row][col] = 0
                    safe+=1
                    self.set_grid_colour(0, row, col)
                else:
                    grid_data[row][col] = -5
                    future = executor.submit(MZSolver.solve_minizinc_instance,self.row_size,self.col_size, self.row_size, self.col_size, grid_data)
                    not_mine_tasks[future] = (row, col)
            for future in as_completed(not_mine_tasks):
                row, col = not_mine_tasks[future]
                status = future.result()             
                if status == Status.UNSATISFIABLE:
                    self.prob[row][col] = 100
                    mine+=1
                    self.set_grid_colour(100, row, col)
                else:
                    self.prob[row][col] = -1
                    self.board[row][col].reset_display()
                    
        if(safe+mine!=0):
                    self.hintCertain = True
                    self.open_button.grid(row=self.base_row + 5, column=0, sticky=W+E)
                    self.hide_hints_button.grid(row=self.base_row + 6, column=0, sticky=W+E)

    def set_grid_colour(self, prob, row, col):
        '''Sets the display color of a grid based on the probability of it being a mine.
        
        :param prob: The probability (0-100)% of the grid being a mine
        :param row: Row index of the grid
        :param col: Column index of the grid
        '''
        grid = self.board[row][col]
        if prob ==100:
            grid.show_prob(11)
        elif prob >= 90:
            grid.show_prob(10)
        elif prob >= 80:
            grid.show_prob(9)
        elif prob >= 70:
            grid.show_prob(8)
        elif prob >= 60:
            grid.show_prob(7)
        elif prob >= 50:
            grid.show_prob(6)
        elif prob >= 40:
            grid.show_prob(5)
        elif prob >= 30:
            grid.show_prob(4)
        elif prob >= 20:
            grid.show_prob(3)
        elif prob >= 10:
            grid.show_prob(2)
        elif prob > 0:
            grid.show_prob(1) 
        elif prob == 0:
            grid.show_prob(0)

    def hide_hints(self):
        '''Hides any currently displayed hints on the board, resetting the display of grids with probabilities.'''
        b = self.createInput_full_board()
        for row in range(self.row_size):
            for col in range(self.col_size):
                if (b[row][col]== -1):
                    self.board[row][col].reset_display()
                    self.prob[row][col] = -1
        self.open_button.grid_remove()
        self.hide_hints_button.grid_remove()
        

    def can_be_x(self, r,c, input,value):
        '''Determines if setting a specific grid to a given value is consistent with the rules of Minesweeper.
        
        :param r: Row index of the grid
        :param c: Column index of the grid
        :param input: The current board state as a 2D array
        :param value: The value to test setting the grid to
        :return: The result of solving the Minesweeper constraint problem with the modified grid
        '''
        modified_input = input.copy()
        modified_input[r][c]= value
        # return MZSolver.solve_minizinc_instance("./model/constraint.mzn",self.row_size,self.col_size,self.row_size,self.col_size,self.mines_amount,modified_input)
        return MZSolver.solve_minizinc_instance(self.row_size,self.col_size,self.row_size,self.col_size,modified_input)

        
    def hint_prob(self):
        '''Calculates and displays the probability of each target grid being a mine based on the current board state.
        (probability appraoch 1)'''
        self.hintCertain = False
        self.output_text.delete('1.0', END)
        self.showprob_smart_button.config(text="Show_Prob_Smart")
        self.showprob_button.config(text="Update_Prob")
        self.hint_show_certain()
        input = self.createInput_full_board()
        # for testing
        # print(input)
        for row in range(self.row_size):
            for col in range(self.col_size):
                if (input[row][col]== -1):
                    if self.is_not_certain(row,col):
                        denominator = 1
                        for i in range(0,9):
                            if self.can_be_x(row,col,input,i)==Status.SATISFIED:
                               denominator = denominator+1.0
                        prob = (1.0/denominator)*100
                        self.prob[row][col] = prob
                        prob = round(prob, 2)
                        self.display_prob(prob, row, col)
                        file_path = '../../data/output.csv'
                        self.output_data(file_path, prob, row, col)
        self.hide_hints_button.grid(row=self.base_row + 6, column=0, sticky=W+E)          
        print('done')

    def display_prob(self, prob, row, col):
        '''Updates the UI to display the probability of a grid being a mine.
        
        :param prob: The probability (0-100) of the grid being a mine
        :param row: Row index of the grid
        :param col: Column index of the grid
        '''
        self.set_grid_colour(prob, row,col)
        # messagebox.showinfo("Probability", f"Probability of grid ({row+1}, {col+1}) being a mine: {self.prob[row][col]}%")
        message = f"Probability of grid ({row}, {col}) being a mine: {prob}%\n"
        self.output_text.insert(END, message)
        # Auto-scroll to the bottom
        self.output_text.see(END)
    
    def is_border(self,row,col):
        '''Determines if a revealed grid is on the border of the discovered area with at least one unrevealed neighbor.
        
        :param row: Row index of the grid
        :param col: Column index of the grid
        :return: True if the grid is a border grid, False otherwise
        '''
        grid = self.board[row][col]
        if grid.is_show():
            if self.has_unshown_neighbour(row,col):
                return True
        return False

    def check_certain_solve(self):
        '''Checks the board for any certain moves based on current visible grids and performs those moves.'''
        for row in range(self.row_size):
            for col in range(self.col_size):
                if self.is_border(row,col):
                    currrent_grid = self.current_board[row][col]
                    adjecent_grids = self.get_adjecent_grids(row,col,self.row_size,self.col_size,self.board)
                    unreveal_grids =[]
                    flag_count = 0
                    for grid in adjecent_grids:
                        if grid.is_flag():
                            flag_count +=1
                        elif not grid.is_show():
                            unreveal_grids.append(grid)
                    if currrent_grid == (flag_count+len(unreveal_grids)):
                        for grid in unreveal_grids:
                            self.rclicked(grid)
                    elif currrent_grid == flag_count:
                        for grid in unreveal_grids:
                            self.lclicked(grid) 

    def check_certain_prob(self):
        '''Checks the board for any grids that can be determined as certainly a mine or certainly not a mine based on probability and updates their display.'''
        for row in range(self.row_size):
            for col in range(self.col_size):
                if self.is_border(row,col):
                    currrent_grid = self.board[row][col]
                    adjecent_grids = self.get_adjecent_grids(row,col,self.row_size,self.col_size,self.board)
                    unreveal_grids =[]
                    flag_count = 0
                    for grid in adjecent_grids:
                        if grid.is_flag():
                            flag_count +=1
                        elif not grid.is_show():
                            unreveal_grids.append(grid)
                    if currrent_grid.value == (flag_count+len(unreveal_grids)):
                        for grid in unreveal_grids:
                            if(not self.prob[grid.y][grid.x] == 100):
                                self.prob[grid.y][grid.x] = 100
                                self.set_grid_colour(100, grid.y,grid.x)
                    elif currrent_grid.value == flag_count:
                        for grid in unreveal_grids:
                            if(not self.prob[grid.y][grid.x] == 0):
                                self.prob[grid.y][grid.x] = 0
                                self.set_grid_colour(0, grid.y,grid.x)  
    # Only for testing                                       
    def adjust_indices(self, row, col, row_size, col_size, fullboard):
        '''Adjusts indices for accessing a partial or full board based on specified dimensions.
        
        :param row: Original row index
        :param col: Original column index
        :param row_size: Number of rows in the board or section
        :param col_size: Number of columns in the board or section
        :param fullboard: Boolean indicating if the full board is being used
        :return: Adjusted row and column indices
        '''
        if not fullboard:
            rIndex = math.ceil(row_size / 2) - 1 if row_size % 2 != 0 else row_size / 2
            cIndex = math.ceil(col_size / 2) - 1 if col_size % 2 != 0 else col_size / 2
            return int(rIndex), int(cIndex)
        return row, col

    def hint_prob_smart(self, row_size, col_size):
        '''Calculates and displays probabilities of being a mine for each unrevealed grid using a smarter, more computational approach
        (proabability approach 2).
        
        :param row_size: Number of rows to consider in the calculation (can be less than the full board size)
        :param col_size: Number of columns to consider in the calculation (can be less than the full board size)
        '''
        self.hintCertain = False
        self.output_text.delete('1.0', END)
        self.showprob_button.config(text="Show_Prob")
        self.showprob_smart_button.config(text="Update_Prob_Smart")
        # Initialize an empty dictionary to store results
        tasks = {}
        results = {}
        self.hint_show_certain()
        with ProcessPoolExecutor() as executor:
            for row in range(self.row_size):
                for col in range(self.col_size):
                    if self.unreveal_with_shown_neighbour(row,col):
                        if self.is_not_certain(row,col):
                                input_grid = []
                                fullboard = (row_size== self.row_size and col_size == self.col_size)
                                input_grid = self.createInput_full_board() if fullboard else self.createInput_partial_board(row, col, row_size, col_size)
                                for type in ["is_mine", "not_mine"]:
                                    modified_input = input_grid.copy()
                                    rIndex, cIndex = self.adjust_indices(row, col, row_size, col_size, fullboard)
                                    modified_input[rIndex][cIndex] = -2 if type == "is_mine" else -5
                                    future = executor.submit(MZSolver.solve_minizinc_instance,self.row_size,self.col_size, row_size, col_size, modified_input, True)
                                    tasks[future] = (row, col,type)
                                    if (row, col) not in results:
                                        results[(row, col)] = {'is_mine': None, 'not_mine': None}
        

            print("Done Adding",len(tasks), "Tasks")
            for future in as_completed(tasks):
                row, col, type = tasks[future]
                num_solutions = future.result()
                # if (row, col) not in results:
                #     results[(row, col)] = {'is_mine': None, 'not_mine': None}
                results[(row, col)][type] = num_solutions
                print("one task done", num_solutions)
                # Check if both futures for the cell are completed
                if None not in results[(row, col)].values():
                    num_is_mine_sol = results[(row, col)]["is_mine"]
                    num_not_mine_sol = results[(row, col)]["not_mine"]
                    prob = (num_is_mine_sol / (num_is_mine_sol + num_not_mine_sol)) * 100 if (num_is_mine_sol + num_not_mine_sol) > 0 else 0
                    prob = round(prob, 2)
                    print(prob)
                    filename = ''
                    if (not (row_size == 7 and col_size == 7)):
                        if(row_size  ==self.row_size and col_size == self.col_size):
                            filename = '_full_board'
                        else:
                            filename = '_'+str(row_size) +'_by_'+str(col_size)
                    
                    file_path = '../../data/smart_output'+filename+'.csv'
                    self.prob[row][col] = prob
                    self.output_data(file_path, prob, row, col)
                    #Update UI
                    results[(row, col)] = prob
                    # self.display_prob( prob, row, col)
            for (row, col) in results:
                prob = results[(row, col)]
                self.display_prob( prob, row, col)
        print("smart prob done")
        self.hide_hints_button.grid(row=self.base_row + 6, column=0, sticky=W+E)

    #only for testing
    def on_show_prob_smart_grid_click(self):
        '''Handles the event when the "Test" button is clicked, allowing the user to specify the size of the board section for probability calculations approach 2.'''
        popup = BoardSizePopup(self.frame)
        popup.grab_set()
        self.frame.wait_window(popup)  # Wait for the popup to close

        choice, row_size, col_size = popup.get_values()
        if choice == "entire":
            self.hint_prob_smart(self.row_size, self.col_size)  
        else:
            try:
                # Convert row_size and col_size to integers
                row_size = int(row_size)
                col_size = int(col_size)
                # If user input a size larger than the max size set the size to the max size
                if row_size > self.row_size:
                    row_size = self.row_size
                if col_size > self.col_size:
                    col_size = self.col_size
                self.hint_prob_smart(row_size, col_size) 
            except ValueError:
                # Handle invalid input
                print("Invalid input for row size or column size")

    def output_data(self, file_path, prob, row,col):
        '''Outputs calculated probabilities and their corresponding grid statuses to a CSV file.
        
        :param file_path: Path to the CSV file
        :param prob: Probability of the grid being a mine
        :param row: Row index of the grid
        :param col: Column index of the grid
        '''
        grid = self.board[row][col]
        if grid.value == -1:
            is_mine = 1
        else:
            is_mine = 0
        if os.path.exists(file_path):
            # Append data to existing CSV file
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([prob, is_mine])
        else:
            # Create new CSV file and write headers
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Probability", "IsAMine"])
                writer.writerow([prob, is_mine])

    def output_data_winrate(self, file_path, won):
        '''Outputs game win/lose data to a CSV file for statistical analysis.
        
        :param file_path: Path to the CSV file
        :param won: Indicates whether the game was won (1) or lost (0)
        '''
        if os.path.exists(file_path):
            # Append data to existing CSV file
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([won])
        else:
            # Create new CSV file and write headers
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["won"])
                writer.writerow([won])         

    def open_mark_certain(self):
        '''Automatically flags or opens cells that are determined to be certain based on the current probabilities.'''
        flag = 0
        open = 0
        for row in range(self.row_size):
            for col in range(self.col_size):
                if self.current_board[row][col]== -1:
                    if self.prob[row][col]==100:
                        self.rclicked(self.board[row][col]) 
                        flag+=1
                    elif self.prob[row][col]==0:
                        self.lclicked(self.board[row][col]) 
                        open+=1
        self.open_button.grid_remove()
        if(self.hintCertain):
            self.hide_hints_button.grid_remove()
            self.hintCertain = False
        return flag, open

def main():     
    global root
    root = Tk()
    root.title("Minesweeper")
    
    # Show difficulty selection dialog
    dialog = DifficultyDialog(root)
    if dialog.result == "Beginner":
        row_size, col_size, mines_amount = 10, 10, 10
    elif dialog.result == "Intermediate":
        row_size, col_size, mines_amount = 16, 16, 40
    elif dialog.result == "Expert":
        row_size, col_size, mines_amount = 16, 30, 99
    else:
        root.destroy()
        sys.exit("No difficulty selected. Exiting.")

    Minesweeper(root, row_size, col_size, mines_amount)
    root.mainloop()


board = []



if __name__ == "__main__":

    main()




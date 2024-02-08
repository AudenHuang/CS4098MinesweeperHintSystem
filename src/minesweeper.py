from tkinter import *
from tkinter import messagebox
from FieldButton import *
import random
# import minizinc
from minizinc import Instance, Model, Solver, Status
import numpy as np

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
        the button in cell i,j of the game board. (by default indexed from (0,0) to (10,10))

    '''

    def __init__(self, master):

        self.frame = Frame(master)
        self.frame.pack()
        
        # Keep track of amount of games played and winned.
        self.game_times = 0
        self.win_times = 0

        # Default game setting is 10x10 with 20 mines.
        self.row_size = 16
        self.col_size = 16
        self.mines_amount = 40
        self.remaining_mines = self.mines_amount
        self.flags = 0
        self.is_over = False
        self.buttons = []
        self.mines = []
        self.board = []
    

        self.input_row_size = 7
        self.input_col_size = 7
        self.current_board = np.full((self.row_size, self.col_size), -1)
        self.prob = np.full((self.row_size, self.col_size), -1)
        
        self.first_click = True
        self.first_click_button = None        
        # Initialize images for newgame button.
        self.img_sun_normal = PhotoImage(file = "images/img_sun_normal.gif")
        self.img_sun_normal_press = PhotoImage(file = "images/img_sun_normal_press.gif")
        self.img_sun_move = PhotoImage(file = "images/img_sun_move.gif")
        self.img_sun_win = PhotoImage(file = "images/img_sun_win.gif")
        self.img_sun_lose = PhotoImage(file = "images/img_sun_lose.gif")
        # Initialize images for cell button.
        self.images = {}
        self.images['blank'] = PhotoImage(file = "images/img_blank.gif")
        self.images['mine'] = PhotoImage(file = "images/img_mine.gif")
        self.images['hit_mine'] = PhotoImage(file = "images/img_hit_mine.gif")
        self.images['flag'] = PhotoImage(file = "images/img_flag.gif")
        self.images['wrong'] = PhotoImage(file = "images/img_wrong_mine.gif")
        self.images['no'] = []
        self.images['prob'] = [PhotoImage(file = "images/img_blank.gif")]
        for i in range(0, 12):
            self.images['prob'].append(PhotoImage(file = "images/img_prob_"+str(i)+".gif"))
            if i< 9:
                self.images['no'].append(PhotoImage(file = "images/img_"+str(i)+".gif"))
    

        # Read test boards if it's not empty
        if not board:
            self.init_board()

        # Initialize newgame button.
        self.newgame_button = Button(self.frame, image = self.img_sun_normal)
        self.newgame_button.grid(row = 0, column = 0, columnspan = self.col_size)
        self.newgame_button.bind("<Button-1>", lambda Button: self.newgame())
        # Initialize remaining mines labels.
        self.remain_label = Label(self.frame, text = "remainng mines: ")
        self.remain_label.grid(row = self.row_size+1, column = 0, columnspan = 4, sticky=W)
        self.remain_label2 = Label(self.frame, text = self.mines_amount)
        self.remain_label2.grid(row = self.row_size+1, column = 4, columnspan = self.row_size, sticky=W)

        # Initialize Hint  button.
        self.solvecomp_button = Button(self.frame, text="Hint_Solve")
        self.solvecomp_button.grid(row = self.row_size+1,column = 0, columnspan = self.col_size, sticky=E)
        self.solvecomp_button.bind("<Button-1>", lambda Button: self.hint_solve())

        self.show_certain_button = Button(self.frame, text="Hint_Certain")
        self.show_certain_button.grid(row = self.row_size+1,column = 0, columnspan = self.col_size-4, sticky=E)
        self.show_certain_button.bind("<Button-1>", lambda Button: self.hint_show_certain())

        self.showprob_button = Button(self.frame, text="Show_Prob")
        self.showprob_button.grid(row = self.row_size+2,column = 0, columnspan = self.col_size, sticky=E)
        self.showprob_button.bind("<Button-1>", lambda Button: self.hint_prob())

        self.showprob_button = Button(self.frame, text="Show_Prob_Smart")
        self.showprob_button.grid(row = self.row_size+2,column = 0, columnspan = self.col_size-4, sticky=E)
        self.showprob_button.bind("<Button-1>", lambda Button: self.hint_prob_smart())

        

    def newgame(self):
        '''Initialize all attributes for new game.

        :param row_size: int
        :param col_size: int
        :param mines_amount: int
        '''
        self.game_times += 1
        # self.init_board()
        self.current_board = np.full((self.row_size, self.col_size), -1)
        self.prob = np.full((self.row_size, self.col_size), -1)
        self.first_click = True
        self.first_click_button = None
        self.is_over = False
        self.flags = 0
        self.remaining_mines = self.mines_amount
        self.mines = []
        # Reset all buttons.
        for button in self.buttons:
            button.reset()
            button.bind('<Button-1>', self.lclicked_wrapper(button))
            button.bind('<Button-2>', self.rclicked_wrapper(button))
        self.remain_label2.config(text=self.remaining_mines)
        self.newgame_button.config(image=self.img_sun_normal)

    def init_board(self):
        '''Initialize game board with buttons.
        The board is a list of lists, inner lists' elements are FieldButton object.
        [ [ ],
          [ ],
          ...]
        '''

        for row in range(self.row_size):
            lis = []
            for col in range(self.col_size):
                button = FieldButton(row, col, self.frame, self.images)
                # first row grid for new game button
                button.grid(row=row+1, column=col)
                lis.append(button)
                self.buttons.append(button)
            self.board.append(lis)
        # Bind LMB and RMB actions to button.
        for button in self.buttons:
            button.bind('<Button-1>', self.lclicked_wrapper(button))
            button.bind('<Button-2>', self.rclicked_wrapper(button))

    def init_random_mines(self):
        '''Initialize mines randomly.
        '''
        mines = self.mines_amount
        while mines:
            buttons = self.get_adjecent_grids(self.first_click_button.x, self.first_click_button.y, self.row_size,self.col_size,self.board)
            buttons.append(self.first_click_button)
            
            #flag to check if random coordinates matches the initial click's 9 grids
            match = True    
            row = None
            col = None
            while match:
                row = random.choice(range(self.row_size))
                col = random.choice(range(self.col_size))
                match = False   
                for b in buttons:
                    if (row == b.x) and (col == b.y):
                        match = True
                        break
                        
            if self.board[row][col].place_mine():
                self.mines.append(self.board[row][col])
                self.update_surrounding_buttons(row, col, 1)
                mines -= 1
            
        

    def get_adjecent_grids(self, row, col, r_size, c_size,input):
        '''Return a list of surrounding buttons of button at row and col in board.
        :param row: int
        :param col: int
        :return: list of buttons
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

    def update_surrounding_buttons(self, row, col, value):
        '''Update surrounding buttons' value adding given value.

        :param row: int
        :param col: int
        '''

        cells = self.get_adjecent_grids(row, col,self.row_size,self.col_size,self.board)
        for cell in cells:
            if not cell.is_mine():
                cell.value += value

    def lclicked_wrapper(self, button):
        return lambda Button: self.lclicked(button)

    def rclicked_wrapper(self, button):
        return lambda Button: self.rclicked(button)

    def lclicked(self, button):
        '''Left click action on given button.
        '''
        if self.first_click == True:
            self.first_click_button = button            
            self.init_random_mines()
            self.first_click = False
            # for debug
            print(self.current_board)
            print(self.prob)
        
        # Do nothing if it's visible or it's flagged.
        if button.is_show() or button.is_flag():
            return

        # Case0: hits a number button, show the button.
        button.show()
        # Case1: hits a mine, game over.
        if button.is_mine():
            button.show_hit_mine()
            self.newgame_button.config(image=self.img_sun_lose)
            self.gameover()
        # Case2: hits an empty button, keep showing surrounding buttons until all not empty.
        elif button.value == 0:
            buttons = [button]
            while buttons:
                temp_button = buttons.pop()
                surrounding = self.get_adjecent_grids(temp_button.x, temp_button.y, self.row_size, self.col_size, self.board)
                for neighbour in surrounding:
                    if not neighbour.is_show() and neighbour.value == 0:
                        buttons.append(neighbour)
                    neighbour.show()

        for row in range(self.row_size):
            for col in range(self.col_size):
                grid = self.board[row][col]
                if grid.is_show():
                    self.current_board[row][col] = grid.value

        # Check whether the game wins or not.
        if self.is_win():
            self.gameover()

    def rclicked(self, button):
        '''Right click action on given button.
        '''
                    
        # Do nothing if it's visible.
        if button.is_show():
            return

        # Flag/Unflag a button.
        if button.is_flag():
            button.flag()
            self.flags -= 1
            self.current_board[button.x][button.y] = -1
        else:
            button.flag()
            self.flags += 1
            self.current_board[button.x][button.y] = -2

        # Update remaining mines label.
        self.remaining_mines = (self.mines_amount-self.flags) if self.flags<self.mines_amount else 0
        self.remain_label2.config(text=self.remaining_mines)
        

        if self.is_win():
            self.gameover()

    def gameover(self):
        '''Disable all buttons and show all mines.
        '''
        self.is_over = True
        for button in self.buttons:
            if button.is_mine():
                if not button.is_flag() and not self.is_win():
                    button.show()
            elif button.is_flag():
                button.show_wrong_flag()
            button.unbind('<Button-1>')
            button.unbind('<Button-2>')

    def is_win(self):
        '''Return True if game wins; False otherwise. The game wins if all buttons are either visible or flagged, and
        the amount of flags equals the amount of mines.

        :return: bool
        '''
        for button in self.buttons:
            if not button.is_show() and not button.is_mine():
                return False
        self.newgame_button.config(image=self.img_sun_win)
        return True

    def guess_move(self):
        '''Return an unclick button.

        :return: button
        '''

        buttons = []
        corners = [self.board[0][0], self.board[0][self.col_size-1],self.board[self.row_size-1][0],self.board[self.row_size-1][self.col_size-1]]
        for button in self.buttons:
            if not button.is_show() and not button.is_flag():
                buttons.append(button)

        for button in corners:
            if not button.is_show() and not button.is_flag():
                return button

        return random.choice(buttons)

    def has_shown_neighbour(self,r,c):
        '''Patameter: row's and colum's number of a grid
        Function: check if any of the adjecent grids is shown
        Return: True if there is a shown neighbor and False if there isn't
        '''
        adjecent_grids = self.get_adjecent_grids(r,c,self.row_size,self.col_size,self.board)
        for grid in adjecent_grids:
            if grid.is_show():
                return True
        return False
    
    def has_shown_neighbour_input(self,mInput,r,c):
        '''Patameter: a 2d array, row's and colum's number of a grid in the given array
        Function: check if any of the adjecent grids in the 2d array is shown
        Return: True if there is a shown neighbor and False if there isn't
        '''
        adjecent_grids  = self.get_adjecent_grids(r,c,self.input_row_size,self.input_col_size,mInput)
        for grid in adjecent_grids:
            if grid >=0:
                return True
        return False
    
    def createInput(self,row,col):
        '''Patameter: row's and colum's number of a grid
        Function: create a 7 by 7 input for the Minizinc model
        Return: the created input'''
        input = np.full((self.input_row_size, self.input_col_size), -4)
        start_r = max(0, row - 3)
        end_r = min(16, row + 4)
        start_c = max(0, col - 3)
        end_c = min(16, col + 4)
        input[start_r-row+3:end_r-row+3, start_c-col+3:end_c-col+3] = self.current_board[start_r:end_r, start_c:end_c].copy()
        # isABomb
        for i in range(7):
            for j in range(7):
                if input[i][j] == -1:
                    if not self.has_shown_neighbour_input(input,i,j):
                        input[i][j] = -3
        return input

    def is_not_certain(self, row, col):
        if self.prob[row][col] == 100:
            return False
        if self.prob[row][col] == 0:
            return False
        return True
    
    def createInstance(self,path,w,h,value):
        # Load MiniZinc models
        model = Model(path)
        # Create a MiniZinc solver instance (e.g., Gecode)
        gecode = Solver.lookup("gecode")
        # Create a MiniZinc instance for the model
        instance = Instance(gecode, model)
        # Feed the input to the model
        instance["grid"] = value
        instance["Width"] = w
        instance["Height"] = h
        # Return the model instance
        return instance
    
    def createInput2(self):
        input = self.current_board.copy()
        for i in range(16):
            for j in range(16):
                if input[i][j] == -1:
                    if not self.has_shown_neighbour(i,j):
                        input[i][j] = -3
        return input
  
    def hint_solve(self):
        """Function: solve parts of the game bases on current board's information by using Minizinc.
        """
        for row in range(self.row_size):
            for col in range(self.col_size):
                # for debug
                # print(self.has_shown_neighbour(row,col))
                if self.current_board[row][col]== -1 and self.has_shown_neighbour(row,col):
                    if self.is_not_certain(row,col):
                        input = self.createInput2()
                        input[row][col]=-2
                        instance = self.createInstance("./notABomb.mzn",16,16,input)
                        if instance.solve().status== Status.UNSATISFIABLE:
                            self.lclicked(self.board[row][col]) 
                        else:
                            input[row][col]=-5
                            instance = self.createInstance("./isABomb.mzn",16,16,input)
                            if instance.solve().status== Status.UNSATISFIABLE:
                                self.rclicked(self.board[row][col])
                            else:
                                self.board[row][col].show_prob(0)
                    else:
                        if self.prob[row][col] == 0:
                            self.lclicked(self.board[row][col]) 
                        else:
                            self.rclicked(self.board[row][col]) 
            
    def hint_show_certain(self):
        for row in range(self.row_size):
            for col in range(self.col_size):
                if self.current_board[row][col]== -1 and self.has_shown_neighbour(row,col):
                    if self.is_not_certain(row,col):
                        input = self.createInput2()
                        input[row][col]=-2
                        instanceNM=self.createInstance("./notABomb.mzn",16,16,input)
                        button = self.board[row][col]
                        if instanceNM.solve().status== Status.UNSATISFIABLE:
                            button.show_prob(1)
                            self.prob[row][col] = 0
                            
                        else:
                            input[row][col]=-5
                            instanceM = self.createInstance("./isABomb.mzn",16,16,input)
                            if instanceM.solve().status== Status.UNSATISFIABLE:
                                button.show_prob(12)
                                self.prob[row][col] = 100
                            else:
                                button.show_prob(0)

                    


    def can_be_x(self, input, r,c,center):
        input[r][c]= center
        instance= self.createInstance("./canBeX.mzn",16,16,input)
        result = instance.solve()
        return result.status



    def hint_prob(self):
        for row in range(self.row_size):
            for col in range(self.col_size):
                # for debug
                # print(self.has_shown_neighbour(row,col))

                if self.current_board[row][col]== -1 and self.has_shown_neighbour(row,col):
                    if self.is_not_certain(row,col):
                        self.prob[row][col] = -1
                        button = self.board[row][col]
                        # input = self.createInput(row,col)
                        input = self.createInput2()
                        input[row][col]=-5
                        instance = self.createInstance("./isABomb.mzn",16,16,input)
                        if instance.solve().status== Status.UNSATISFIABLE:
                            self.prob[row][col] = 100
                            # need to change this in the future
                            button.show_prob(12)
                        else:
                            input[row][col]= -2 
                            instance = self.createInstance("./notABomb.mzn",16,16,input)
                            if instance.solve().status== Status.UNSATISFIABLE:
                                self.prob[row][col] = 0
                                button.show_prob(1)
                            else:
                                denominator = 1.0
                                for i in range(1,9):
                                    if self.can_be_x(input,row,col,i)==Status.SATISFIED:
                                        denominator = denominator+1.0
                                prob = (1.0/denominator)*100
                                self.prob[row][col] = prob
                            
                                if prob >= 50:
                                    button.show_prob(7)
                                elif prob >= 40:
                                    button.show_prob(6)
                                elif prob >= 30:
                                    button.show_prob(5)
                                elif prob >= 20:
                                    button.show_prob(4)
                                elif prob >= 10:
                                    button.show_prob(3)
                                elif prob > 0:
                                    button.show_prob(2)  
                        print(row+1,col+1, self.prob[row][col])              
        print('done')

        
    def hint_prob_smart(self):
        for row in range(self.row_size):
            for col in range(self.col_size):
                # for debug
                # print(self.has_shown_neighbour(row,col))
                if self.current_board[row][col]== -1 and self.has_shown_neighbour(row,col):
                    if self.is_not_certain(row,col):
                        self.prob[row][col] = -1
                        button = self.board[row][col]
                        input = self.createInput2()
                        input[row][col]=-2
                        instanceNM = self.createInstance("./notABomb.mzn",16,16,input.copy())
                        input[row][col]=-5
                        instanceM = self.createInstance("./isABomb.mzn",16,16,input)
                        if(instanceNM.solve().status==Status.UNSATISFIABLE):
                            self.prob[row][col] = 0
                            button.show_prob(1)
                        elif(instanceM.solve().status==Status.UNSATISFIABLE):
                            self.prob[row][col] = 100
                            button.show_prob(12)
                        else:
                            input = self.createInput(row,col)
                            input[3][3]=-2
                            instanceNM = self.createInstance("./notABomb.mzn",7,7,input.copy())
                            input[3][3]=-5
                            instanceM = self.createInstance("./isABomb.mzn",7,7,input)
                            nMresult = instanceNM.solve(all_solutions= True).statistics["nSolutions"]
                            print("")
                            print(nMresult)
                            nNotMresult= instanceM.solve(all_solutions= True).statistics["nSolutions"]
                            print(nNotMresult)
                            prob = nMresult/(nMresult+nNotMresult)*100
                            self.prob[row][col] = prob
                            if prob >= 90:
                                button.show_prob(11)
                            elif prob >= 80:
                                button.show_prob(10)
                            elif prob >= 70:
                                button.show_prob(9)
                            elif prob >= 60:
                                button.show_prob(8)
                            elif prob >= 50:
                                button.show_prob(7)
                            elif prob >= 40:
                                button.show_prob(6)
                            elif prob >= 30:
                                button.show_prob(5)
                            elif prob >= 20:
                                button.show_prob(4)
                            elif prob >= 10:
                                button.show_prob(3)
                            elif prob > 0:
                                button.show_prob(2) 

                    print(row+1,col+1,self.prob[row][col])
                   
        print("done")
       



def main():
    global root
    root = Tk()
    root.title("Minesweeper")
    Minesweeper(root)
    root.mainloop()


board = []



if __name__ == "__main__":

    main()




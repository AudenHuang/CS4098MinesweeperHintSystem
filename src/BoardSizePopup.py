import tkinter as tk
from tkinter import simpledialog

# Only for testing
class BoardSizePopup(tk.Toplevel):
    '''
        Initializes the popup window for selecting board size for the input.
        
        :param parent: The parent Tkinter widget (often the main application window).
        '''
    def __init__(self, parent):
        super().__init__(parent)
        
        self.var = tk.StringVar(value="entire")
        self.row_size = tk.StringVar(value="7")
        self.col_size = tk.StringVar(value="7")
        
        # Radio buttons for the user to select entire or partial board
        tk.Radiobutton(self, text="Entire Board", variable=self.var, value="entire").pack(anchor='w')
        partial_board_frame = tk.Frame(self)
        partial_board_frame.pack(fill='x', padx=5, pady=5)
        tk.Radiobutton(partial_board_frame, text="Partial Board", variable=self.var, value="partial").pack(side='left')
        
        # Entry fields for row and col sizes (only enabled if partial board is selected)
        self.row_entry = tk.Entry(partial_board_frame, textvariable=self.row_size, state='disabled')
        self.row_entry.pack(side='left')
        self.col_entry = tk.Entry(partial_board_frame, textvariable=self.col_size, state='disabled')
        self.col_entry.pack(side='left')
        
        # Update entry fields based on selection
        self.var.trace('w', self.update_entries)
        
        # OK and Cancel buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill='x', pady=5)
        tk.Button(btn_frame, text="OK", command=self.on_ok).pack(side='left')
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side='left')
         # At the end of the method, close the popup window if it exists
        if hasattr(self, 'popup') and self.popup:
            self.popup.destroy()
            self.popup = None  # Reset the popup variable

    def update_entries(self, *args):
        '''
        Enables or disables the row and column size entry fields based on the board selection.
        
        :param args: Additional arguments, not used but required by the trace callback signature.
        '''
        if self.var.get() == "partial":
            self.row_entry.config(state='normal')
            self.col_entry.config(state='normal')
        else:
            self.row_entry.config(state='disabled')
            self.col_entry.config(state='disabled')

    def on_ok(self):
        '''
        Defines actions to perform when the OK button is clicked. 
        Here, it simply closes the popup, but you can extend it to include validation or other actions.
        '''
        # Perform validation if necessary
        self.destroy()  # Close the popup
    
    def get_values(self):
        '''
        Retrieves the current values of the board selection, row size, and column size.
        
        :return: A tuple containing the board selection ('entire' or 'partial'), row size, and column size.
        '''
        return self.var.get(), self.row_size.get(), self.col_size.get()

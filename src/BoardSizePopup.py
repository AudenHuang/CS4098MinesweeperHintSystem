import tkinter as tk
from tkinter import simpledialog

class BoardSizePopup(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.grab_set()
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

    def update_entries(self, *args):
        if self.var.get() == "partial":
            self.row_entry.config(state='normal')
            self.col_entry.config(state='normal')
        else:
            self.row_entry.config(state='disabled')
            self.col_entry.config(state='disabled')

    def on_ok(self):
        # Perform validation if necessary
        self.destroy()  # Close the popup
    
    def get_values(self):
        return self.var.get(), self.row_size.get(), self.col_size.get()

from tkinter import Label, OptionMenu, StringVar, simpledialog

class DifficultyDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Select Difficulty")
        Label(master, text="Choose Difficulty:").pack()
        self.var = StringVar(master)
        self.var.set("Beginner")  # default value
        options = ["Beginner", "Intermediate", "Expert"]
        OptionMenu(master, self.var, *options).pack()

    def apply(self):
        self.result = self.var.get()
import tkinter as tk
import time

class TextWindow:

    def __init__(self):
        self.window = tk.Tk()

        # Set the window title
        self.window.title("Interact with ChatGPT3")

        # Create a text widget
        self.text = tk.Text(self.window, font=("Helvetica", 20), height=40, width=100)

    def addText(self, message: str):
        self.text.insert(tk.END, f"{message}\n")
        self.text.see(tk.END)
        self.text.pack()

        self.window.update_idletasks()
        self.window.update()

    def deleteLastLine(self):
        self.text.delete("end-2l","end-1l")
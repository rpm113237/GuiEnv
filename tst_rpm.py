import tkinter as tk
import os
os.environ["DISPLAY"] = ":0"
root = tk.Tk()
root.geometry("1400x200")
root.title("Hello From Tkinter!!!!!!!!!!!!!!")

label = tk.Label(root, text="Hello, Raspberry Pi!")
label.pack()

root.mainloop()

import tkinter as tk
from tkinter import ttk  # Combobox belongs to the themed (ttk) module

def on_select(event):
    """Function called automatically when an item is selected."""
    selected_item = combo.get()
    result_label.config(text=f"You selected: {selected_item}")

# 1. Initialize the root window
root = tk.Tk()
root.title("Tkinter Combobox Demo")
root.geometry("400x200")

# 2. Define the options for the dropdown
options = ["Python", "JavaScript", "C++", "Java", "Go"]

# 3. Create a label instruction
instruction_label = ttk.Label(root, text="Select your favorite programming language:")
instruction_label.pack(pady=10)

# 4. Create the Combobox
# 'state="readonly"' prevents the user from typing custom text into the field
combo = ttk.Combobox(root, values=options, state="readonly", width=15)
combo.pack(pady=5)

# Set the default choice (index 0 is "Python")
combo.current(0)

# 5. Bind the selection event to our function
# The <<ComboboxSelected>> event fires whenever the choice changes
combo.bind("<<ComboboxSelected>>", on_select)

# 6. Create a label to display the output result
result_label = ttk.Label(root, text="You selected: Python", font=("Helvetica", 10, "bold"))
result_label.pack(pady=20)

# 7. Start the application loop
root.mainloop()

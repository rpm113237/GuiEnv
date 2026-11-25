import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x600")

# Create a style instance
style = ttk.Style()

# Configure the frame container style
style.configure(
    "Custom.TLabelframe",
    background="#f0f0f0",
    bordercolor="#3498db",
    borderwidth=20,
    relief="ridge",
)

# Configure the title text inside the labelframe
style.configure(
    "Custom.TLabelframe.Label",
    background="#f0f0f0",
#     foreground="#2c3e50",
    foreground = 'magenta',
    font=("Helvetica", 10, "bold"),
)

# Apply the custom style to the LabelFrame
labelframe = ttk.LabelFrame(
    root, text="My Group", style="Custom.TLabelframe", padding=15
)
labelframe.pack(fill="both", expand=True, padx=20, pady=20)

tstframe=ttk.LabelFrame(labelframe, text = 'test', style = "Custom.TLabelframe", padding=2)
tstframe.pack(fill="both", expand=False, padx=20, pady=20)

label = ttk.Label(tstframe, text="Inside the styled frame")
label.pack()

root.mainloop()

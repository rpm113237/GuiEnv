import tkinter as tk
from tkinter import ttk

# 1. Initialize root window
root = tk.Tk()
root.title("Employee Database")
root.geometry("600x300")

# 2. Define Columns
# Use internal IDs for code management
columns = ("id", "name", "role", "salary")

# 3. Create Treeview Widget
# "show='headings'" hides the default hierarchical first column (tree arrow)
table = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")

# 4. Define Headings (What the user sees at the top)
table.heading("id", text="ID")
table.heading("name", text="Full Name")
table.heading("role", text="Job Title")
table.heading("salary", text="Salary")

# 5. Define Column Properties
# anchor="w" aligns text left (West), "center" aligns center
table.column("id", width=50, minwidth=50, anchor="center")
table.column("name", width=150, minwidth=100, anchor="w")
table.column("role", width=150, minwidth=100, anchor="w")
table.column("salary", width=100, minwidth=80, anchor="center")

# 6. Add Sample Data
# Use an empty string '' as the first argument because we aren't nesting items
data = [
    ("101", "Alice Smith", "Software Engineer", "$95,000"),
    ("102", "Bob Jones", "UX Designer", "$82,000"),
    ("103", "Charlie Brown", "Data Analyst", "$78,000"),
    ("104", "Diana Prince", "Product Manager", "$110,000"),
]

for row in data:
    table.insert("", tk.END, values=row)

# 7. Add a Scrollbar
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=table.yview)
table.configure(yscrollcommand=scrollbar.set)

# 8. Pack layout elements
table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 9. Start application
root.mainloop()

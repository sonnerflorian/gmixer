import tkinter as tk


root = tk.Tk()
root.title("Hello World")

label = tk.Label(root, text="Hello, World!", font=("Arial", 24))
label.pack(padx=40, pady=40)

root.mainloop()

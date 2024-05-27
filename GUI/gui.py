import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

uploaded_files = []

def read_file(filepath):
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    else:
        print("Unsupported file format.")
        return
    uploaded_files.append(filepath[60::])
    update_file_list()

def update_file_list():
    file_list.delete(0, tk.END)
    for file in uploaded_files:
        file_list.insert(tk.END, file)

def open_file_dialog():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
    if filepath:
        read_file(filepath)

def drop(event):
    filepath = event.data
    if filepath:
        filepath = filepath.strip('{}')  # Strip curly braces if present
        read_file(filepath)

root = TkinterDnD.Tk()
root.title("File Upload GUI")
root.geometry("600x600")
root.config(bg="#f0f0f0")

header = tk.Label(root, text="Upload Files", bg="#4a4a4a", fg="white", font=("Arial", 16))
header.pack(fill=tk.X, pady=10)

frame = tk.Frame(root, width=400, height=200, bg="#e0e0e0", relief=tk.RAISED, bd=2)
frame.pack(pady=20)
frame.pack_propagate(False)

drag_label = tk.Label(frame, text="Drag files here", bg="#e0e0e0", font=("Arial", 14), fg="#666")
drag_label.pack(pady=50)

upload_button = tk.Button(root, text="Upload File", command=open_file_dialog, bg="#4a4a4a", fg="white", font=("Arial", 12))
upload_button.pack(pady=10)

file_list_label = tk.Label(root, text="Uploaded Files:", bg="#f0f0f0", font=("Arial", 12))
file_list_label.pack(anchor="w", padx=20)

file_list = tk.Listbox(root, width=60, height=10)
file_list.pack(pady=10)

frame.drop_target_register(DND_FILES)
frame.dnd_bind('<<Drop>>', drop)

root.mainloop()
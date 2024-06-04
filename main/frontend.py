"""
This module provides a GUI for uploading CSV and Excel files.
"""

from DbHandler import DbHandler, clean_dataframe
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import pandas as pd

# File types
file_types = ["tsun", "cb", "pb", "other"]
uploaded_files = []
type_list = []

new_db = pd.DataFrame(columns=clean_dataframe("data\ֿNeuroTech Industry IL 2023.xlsx", 'excel').columns.tolist())
new_db.to_excel('main/new.xlsx', sheet_name='new')

def read_file(filepath):
    """
    Reads a file and updates the uploaded file list.
    """
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    else:
        messagebox.showerror("Error", "Unsupported file format.")
        return
    uploaded_files.append({"path": filepath, "type": tk.StringVar(value="other")})
    update_file_list()

def update_file_list():
    """
    Updates the displayed list of uploaded files.
    """
    for widget in file_list_frame.winfo_children():
        widget.destroy()
    for i, file_info in enumerate(uploaded_files):
        file_path = file_info["path"]
        file_type_var = file_info["type"]

        file_label = ttk.Label(file_list_frame, text=file_path.split('/')[-1])
        file_label.grid(row=i, column=0, padx=5, pady=5)

        type_menu = ttk.OptionMenu(file_list_frame, file_type_var, file_type_var.get(), *file_types)
        type_menu.grid(row=i, column=1, padx=5, pady=5)

        delete_button = ttk.Button(file_list_frame,
                                    text="Delete",
                                    command=lambda idx=i: delete_file(idx))
        delete_button.grid(row=i, column=2, padx=5, pady=5)

def delete_file(index):
    """
    Deletes a file from the uploaded file list.
    """
    del uploaded_files[index]
    del df_list[index]
    update_file_list()

def open_file_dialog():
    """
    Opens a file dialog to select a file for uploading.
    """
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"),
                                                      ("Excel files", "*.xlsx")])
    if filepath:
        read_file(filepath)

def drop(event):
    """
    Handles file drop events.
    """
    filepath = event.data
    if filepath:
        filepath = filepath.strip('{}')  # Strip curly braces if present
        read_file(filepath)

def upload_all_files():
    """
    Handles the final upload of all files.
    """
    if not uploaded_files:
        messagebox.showerror("Error", "No files to upload.")
        return
    for file_info in uploaded_files:
        type = file_info['type'].get()
        file_path = file_info['path']
        print(f"Uploading {file_path} as {type}")
        handle_dfs("data\ֿNeuroTech Industry IL 2023.xlsx", file_path, type)
    messagebox.showinfo("Success", "All files uploaded successfully!") 

def handle_dfs(main_db:str, file_path:str, type:str):
    """handels dfs"""
    for file in uploaded_files:
        tsun = DbHandler(main_db, file_path, type)
        print(tsun.type)
        tsun.handle_tsun()

root = TkinterDnD.Tk()
root.title("File Upload GUI")
root.geometry("600x600")
root.config(bg="#13b013")

style = ttk.Style()
style.configure('TLabel', background='#2e352e', font=("Arial", 12))
style.configure('TButton', font=("Arial", 12))
style.configure('TFrame', background='#017002')

header = ttk.Label(root,
                    text="Upload Files",
                    background="#8bf33b",
                    foreground="white",
                    font=("Arial", 16),
                    anchor="center"
                    )
header.pack(fill=tk.X, pady=10)

frame = ttk.Frame(root, width=400, height=200, relief=tk.RAISED, borderwidth=2)
frame.pack(pady=20)
frame.pack_propagate(False)

drag_label = ttk.Label(frame, text="Drag files here",font=("Arial", 14), anchor="center")
drag_label.pack(expand=True)

upload_button = ttk.Button(root, text="Upload File", command=open_file_dialog)
upload_button.pack(pady=10)

file_list_label = ttk.Label(root, text="Uploaded Files:", anchor="w")
file_list_label.pack(anchor="w", padx=20)

file_list_frame = ttk.Frame(root)
file_list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

final_upload_button = ttk.Button(root, text="Upload All Files", command=upload_all_files)
final_upload_button.pack(pady=20)

frame.drop_target_register(DND_FILES)
frame.dnd_bind('<<Drop>>', drop)

root.mainloop()

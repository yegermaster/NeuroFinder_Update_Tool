"""
This module provides a GUI for uploading CSV and Excel files.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from tkinterdnd2 import TkinterDnD, DND_FILES
from db_handler import DbHandler


# Constants
MAIN_DB_PATH = 'main/main_db.xlsx'
NOT_NEUROTECH_PATH = 'main/not_neurotech_db.xlsx'
FILE_TYPES = ["tsun", "cb", "pb", "other"]
loading_files = []
loaded_files = []
db_handler = DbHandler(MAIN_DB_PATH, NOT_NEUROTECH_PATH)


def read_file(filepath):
    """
    Reads a file and updates the loading file list.
    """
    if filepath.endswith('.csv'):
        pd.read_csv(filepath)
    elif filepath.endswith('.xlsx'):
        pd.read_excel(filepath)
    else:
        messagebox.showerror("Error", "Unsupported file format.")
        return
    loading_files.append({"path": filepath, "data_type": tk.StringVar(value="tsun")})
    update_loading_list()

def update_loading_list():
    """
    Updates the displayed list of loading files.
    """
    for widget in loading_list_frame.winfo_children():
        widget.destroy()

    for i, file_info in enumerate(loading_files):
        file_path = file_info["path"]
        file_type_var = file_info["data_type"]

        file_label = ttk.Label(loading_list_frame, text=file_path.split('/')[-1])
        file_label.grid(row=i, column=0, padx=5, pady=5)

        type_menu = ttk.OptionMenu(loading_list_frame,
                                file_type_var, file_type_var.get(),
                                *FILE_TYPES)
        type_menu.grid(row=i, column=1, padx=5, pady=5)

        delete_button = ttk.Button(loading_list_frame,
                                    text="Delete",
                                    command=lambda idx=i: delete_loading_file(idx))
        delete_button.grid(row=i, column=2, padx=5, pady=5)

def delete_loading_file(index):
    """
    Deletes a file from the loading file list.
    """
    del loading_files[index]
    update_loading_list()

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
    if not loading_files:
        messagebox.showerror("Error", "No files to upload.")
        return
    for file_info in loading_files:
        data_type = file_info['data_type'].get()
        file_path = file_info['path']
        print(f"Uploading {file_path} as {data_type}")
        db_handler.start_process(file_path, data_type)
        loaded_files.append(file_info)
    loading_files.clear()
    update_loading_list()
    update_loaded_list()
    messagebox.showinfo("Success", "All files uploaded successfully!")

def export_all_files():
    """Exports files to Excel."""
    if not loaded_files:
        messagebox.showerror("Error", "No files to export.")
        return
    db_handler.export('main/new1.xlsx')
    messagebox.showinfo("Success", "All files uploaded exported")

def update_loaded_list():
    """
    Updates the displayed list of loaded files.
    """
    for widget in loaded_list_frame.winfo_children():
        widget.destroy()

    for i, file_info in enumerate(loaded_files):
        file_path = file_info["path"]

        file_label = ttk.Label(loaded_list_frame, text=file_path.split('/')[-1])
        file_label.grid(row=i, column=0, padx=5, pady=5)

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

final_upload_button = ttk.Button(root, text="Upload All Files", command=upload_all_files)
final_upload_button.pack(pady=20)

export_button = ttk.Button(root, text="Export", command=export_all_files)
export_button.pack(pady=20)

drag_label = ttk.Label(frame, text="Drag files here", font=("Arial", 14), anchor="center")
drag_label.pack(expand=True)

upload_button = ttk.Button(root, text="Upload File", command=open_file_dialog)
upload_button.pack(pady=10)

# Section for files loading to load
loading_label = ttk.Label(root, text="Files ready to Load:", anchor="w")
loading_label.pack(anchor="w", padx=20)

loading_list_frame = ttk.Frame(root)
loading_list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

# Section for files already loaded
loaded_label = ttk.Label(root, text="Files Already Loaded:", anchor="w")
loaded_label.pack(anchor="w", padx=20)

loaded_list_frame = ttk.Frame(root)
loaded_list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)



frame.drop_target_register(DND_FILES)
frame.dnd_bind('<<Drop>>', drop)

root.mainloop()

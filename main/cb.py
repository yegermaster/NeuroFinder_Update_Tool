"""
frontend.py - This module provides a GUI for:
    1) Uploading CSV and Excel files for processing (File Import & Processing tab).
    2) Uploading images to ImgBB and updating a CSV (Image Upload tab).

TODO:
    - Implement an algorithm to separate neurotech companies (True) from non-neurotech companies (False).
    - Modify the Status field to represent 'Not Evaluated' where applicable.
"""

import os
import base64
import logging
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
import pandas as pd
from dotenv import load_dotenv
import requests
import threading

# --- Local imports from your backend module ---
from backend import DbHandler, escape_special_characters

# ---------------------------------------------------------------------------
# Load environment variables
load_dotenv()
MAIN_DB_PATH = os.getenv('MAIN_DB_PATH')
NOT_NEUROTECH_DB_PATH = os.getenv('NOT_NEUROTECH_DB_PATH')
NEW_COMPANIES_PATH = os.getenv('NEW_COMPANIES_PATH')
UPDATED_COMPANIES_PATH = os.getenv('UPDATED_COMPANIES_PATH')
IMGBB_UPLOAD_URL = os.getenv('IMGBB_UPLOAD_URL')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
FILE_TYPES = ["tsun", "cb", "pb", "other"]
loading_files = []
loaded_files = []
lock = threading.Lock()

# Create the DbHandler instance
db_handler = DbHandler(MAIN_DB_PATH, NOT_NEUROTECH_DB_PATH)

# ---------------------------------------------------------------------------
# Helper function to create a scrollable frame
def create_scrolled_frame(parent):
    """
    Creates a scrollable CTkFrame within a parent widget and returns
    (container, inner_frame).

    - 'container' is the frame you place with .grid(...) in the parent.
    - 'inner_frame' is where you add your row/column of labels, etc.
    """
    container = ctk.CTkFrame(parent)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)

    # Canvas for scrolling
    canvas = tk.Canvas(container, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    # Scrollbar
    scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    canvas.configure(yscrollcommand=scrollbar.set)

    # Inner frame in the canvas
    inner_frame = ctk.CTkFrame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Dynamically update scroll region
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", on_configure)

    return container, inner_frame

# ---------------------------------------------------------------------------
# Core logic for file handling
def process_file(filepath: str):
    """Processes a file and updates the loading file list."""
    try:
        if filepath.endswith('.csv'):
            pd.read_csv(filepath)  # Check if CSV file can be read
        elif filepath.endswith('.xlsx'):
            pd.read_excel(filepath)  # Check if Excel file can be read
        else:
            messagebox.showerror("Error", "Unsupported file format.")
            return
        
        # Append to our "Files ready to load"
        loading_files.append({"path": filepath, "data_type": tk.StringVar(value="tsun")})
        refresh_loading_file_list()

    except FileNotFoundError:
        logging.error("File not found: %s", filepath)
        messagebox.showerror("Error", f"File not found: {filepath}")
    except pd.errors.EmptyDataError:
        logging.error("The file is empty: %s", filepath)
        messagebox.showerror("Error", f"The file is empty: {filepath}")
    except pd.errors.ParserError:
        logging.error("Parsing error in file: %s", filepath)
        messagebox.showerror("Error", f"Parsing error in file: {filepath}")
    except PermissionError:
        logging.error("Permission denied: %s", filepath)
        messagebox.showerror("Error", f"Permission denied: {filepath}")

def refresh_loading_file_list():
    """Updates the displayed list of loading files."""
    # Clear existing widgets
    for widget in loading_files_frame.winfo_children():
        widget.destroy()

    for i, file_info in enumerate(loading_files):
        file_path = file_info["path"]
        file_type_var = file_info["data_type"]
        
        # Show a normalized filename (no directories, no extension)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        normalized_name = db_handler.normalize(base_name)

        file_label = ttk.Label(loading_files_frame, text=normalized_name)
        file_label.grid(row=i, column=0, padx=5, pady=5, sticky="w")

        type_menu = ttk.OptionMenu(loading_files_frame,
                                   file_type_var,
                                   file_type_var.get(),
                                   *FILE_TYPES)
        type_menu.grid(row=i, column=1, padx=5, pady=5)

        delete_button = ttk.Button(loading_files_frame,
                                   text="Delete",
                                   command=lambda idx=i: delete_file_from_loading_list(idx))
        delete_button.grid(row=i, column=2, padx=5, pady=5)

def delete_file_from_loading_list(index: int):
    """Deletes a file from the loading file list."""
    with lock:
        del loading_files[index]
    refresh_loading_file_list()

def open_file_dialog():
    """Opens a file dialog to select multiple files for uploading."""
    filepaths = filedialog.askopenfilenames(filetypes=[
        ("CSV files", "*.csv"),
        ("Excel files", "*.xlsx")
    ])
    if filepaths:
        for filepath in filepaths:
            process_file(filepath)

def drop(event):
    """Handles file drop events, allowing multiple files."""
    filepaths = event.data.strip("{}").split("} {")
    for filepath in filepaths:
        filepath = os.path.normpath(filepath)
        process_file(filepath)

def load_all_files():
    """Validates and uploads all files in the loading list."""
    if not loading_files:
        messagebox.showerror("Error", "No files to upload.")
        return

    valid_files = []
    with lock:
        for file_info in loading_files:
            data_type = file_info['data_type'].get()
            file_path = file_info['path']
            # Validate the file type
            if not db_handler.validate_file_type(file_path, data_type):
                messagebox.showerror(
                    "Error",
                    f"File '{os.path.basename(file_path)}' does not match the "
                    f"specified type '{data_type}'. Please try again."
                )
            else:
                valid_files.append(file_info)

    if not valid_files:
        return
    
    # If valid, process them
    for file_info in valid_files:
        data_type = file_info['data_type'].get()
        path = file_info['path']
        db_handler.start_searching_process(path, data_type)
        db_handler.start_update_process(path, data_type)
        loaded_files.append(file_info)

    loading_files.clear()
    refresh_loading_file_list()
    refresh_loaded_file_list()
    messagebox.showinfo("Success", "All valid files uploaded successfully!")

def refresh_loaded_file_list():
    """Updates the displayed list of loaded files."""
    for widget in loaded_files_frame.winfo_children():
        widget.destroy()

    for i, file_info in enumerate(loaded_files):
        file_path = file_info["path"]
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        normalized_name = db_handler.normalize(base_name)

        file_label = ttk.Label(loaded_files_frame, text=normalized_name)
        file_label.grid(row=i, column=0, padx=5, pady=5, sticky="w")

def export_loaded_files():
    """Exports the 'new companies' to an Excel file."""
    if not loaded_files:
        messagebox.showerror("Error", "No files to export.")
        return
    db_handler.export_new(NEW_COMPANIES_PATH)
    messagebox.showinfo("Success", "All files exported successfully!")

def export_updated_file():
    """Exports the updated companies to an Excel file."""
    db_handler.export_updates(UPDATED_COMPANIES_PATH)
    messagebox.showinfo("Success", "Updated companies exported successfully!")

# ---------------------------------------------------------------------------


def upload_images_and_update_csv():
    """Opens the upload image GUI process."""
    folder = folder_path.get()
    csv_file = csv_path.get()
    if folder and csv_file:
        process_image_folder(folder, csv_file)
    else:
        messagebox.showwarning("Input Error",
                               "Please select both the image folder and the CSV file.")

def process_image_folder(image_folder_path, csv_file):
    """Processes all images in a folder, uploads them to ImgBB, and updates the CSV."""
    error_logs = []
    for filename in os.listdir(image_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            local_file = os.path.join(image_folder_path, filename)
            company_name = os.path.splitext(filename)[0]

            image_url = upload_to_imgbb(local_file)
            if image_url:
                update_csv_with_url(csv_file, company_name, image_url)
            else:
                error_logs.append(f"Error uploading {local_file}")

    if error_logs:
        messagebox.showerror("Upload Errors", "\n".join(error_logs))
    else:
        messagebox.showinfo("Success", "Process completed successfully!")

def upload_to_imgbb(image_path: str) -> str:
    """Uploads an image to ImgBB and returns the URL."""
    try:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        data = {
            'key': IMGBB_API_KEY,
            'image': image_data,
            'name': os.path.basename(image_path)
        }

        response = requests.post(IMGBB_UPLOAD_URL, data=data, verify=False, timeout=10)
        response.raise_for_status()
        json_response = response.json()
        return json_response['data']['url']
    except requests.exceptions.Timeout:
        logging.error("Request timed out while uploading %s to ImgBB.", image_path)
        return None
    except requests.exceptions.RequestException as e:
        logging.error("Failed to upload %s to ImgBB: %s", image_path, e)
        return None

def update_csv_with_url(csv_file: str, company_name: str, image_url: str):
    """Updates a CSV file by adding the image URL to the corresponding company."""
    rows = []
    updated = False
    company_name = escape_special_characters(company_name)

    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            messagebox.showerror("CSV Error", f"No columns found in CSV: {csv_file}")
            return
        fieldnames = reader.fieldnames + ['ImageURL'] if 'ImageURL' not in reader.fieldnames else reader.fieldnames

        for row in reader:
            if escape_special_characters(row.get('Company_Name', '')) == company_name:
                row['ImageURL'] = image_url
                updated = True
            rows.append(row)

        if not updated:
            # If the company was not found, add a new row
            new_row = {field: "" for field in fieldnames}
            new_row['Company_Name'] = company_name
            new_row['ImageURL'] = image_url
            rows.append(new_row)

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# ---------------------------------------------------------------------------
# Main GUI with Tabview
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = TkinterDnD.Tk()
root.title("Neurotech File Manager")
root.geometry("800x600")

# Image uploading logic
folder_path = tk.StringVar()
csv_path = tk.StringVar()

tabview = ctk.CTkTabview(root, width=800, height=600)
tabview.pack(fill="both", expand=True)

# ===========================================================================
# TAB 1: File Import & Processing
# ===========================================================================
file_tab = tabview.add("File Import & Processing")

# -- Top Frame: Title + Buttons
top_frame = ctk.CTkFrame(file_tab)
top_frame.pack(fill="x", pady=5)

header = ctk.CTkLabel(top_frame, text="Upload & Process Files", 
                      font=("Arial", 16), fg_color="green", 
                      text_color="white", corner_radius=5)
header.pack(fill="x", padx=10, pady=5)

buttons_frame = ctk.CTkFrame(top_frame)
buttons_frame.pack(fill="x", padx=10, pady=5)

upload_btn = ctk.CTkButton(buttons_frame, text="Select Files", command=open_file_dialog)
upload_btn.pack(side="left", padx=5)

final_upload_button = ctk.CTkButton(buttons_frame, text="Load All Files", command=load_all_files)
final_upload_button.pack(side="left", padx=5)

export_new_companies_button = ctk.CTkButton(buttons_frame, text="Export New", command=export_loaded_files)
export_new_companies_button.pack(side="left", padx=5)

export_updates_button = ctk.CTkButton(buttons_frame, text="Export Updated", command=export_updated_file)
export_updates_button.pack(side="left", padx=5)

# -- Middle Frame for the two scrollable columns
lists_frame = ctk.CTkFrame(file_tab)
lists_frame.pack(fill="both", expand=True, padx=10, pady=5)

lists_frame.grid_columnconfigure(0, weight=1)
lists_frame.grid_columnconfigure(1, weight=1)

# Left: Files ready to load
loading_label = ctk.CTkLabel(lists_frame, text="Files ready to Load:", anchor="w")
loading_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

loading_container, loading_files_frame = create_scrolled_frame(lists_frame)
loading_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

# Right: Files already loadeda
loaded_label = ctk.CTkLabel(lists_frame, text="Files Already Loaded:", anchor="w")
loaded_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)

loaded_container, loaded_files_frame = create_scrolled_frame(lists_frame)
loaded_container.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

# Support drag-and-drop in the entire tab (or a sub-frame)
file_tab.drop_target_register(DND_FILES)
file_tab.dnd_bind('<<Drop>>', drop)

# ===========================================================================
# TAB 2: Image Upload
# ===========================================================================
img_tab = tabview.add("Image Upload")

img_header = ctk.CTkLabel(img_tab, text="Upload Images to ImgBB",
                          font=("Arial", 16), fg_color="blue", text_color="white",
                          corner_radius=5)
img_header.pack(fill="x", padx=10, pady=10)

img_button_frame = ctk.CTkFrame(img_tab)
img_button_frame.pack(fill="x", padx=10, pady=10)

folder_button = ctk.CTkButton(img_button_frame, text="Select Image Folder",
                              command=lambda: folder_path.set(filedialog.askdirectory()))
folder_button.pack(side="left", padx=5)

csv_button = ctk.CTkButton(img_button_frame, text="Select CSV File",
                           command=lambda: csv_path.set(
                               filedialog.askopenfilename(
                                   filetypes=[("CSV files", "*.csv")]
                               )
                           ))
csv_button.pack(side="left", padx=5)

upload_img_button = ctk.CTkButton(img_button_frame, text="Upload Images",
                                  command=upload_images_and_update_csv)
upload_img_button.pack(side="left", padx=5)

# Optionally, you could show the user the chosen folder/CSV path in a label
info_frame = ctk.CTkFrame(img_tab)
info_frame.pack(fill="x", padx=10, pady=5)

folder_path_label = ctk.CTkLabel(info_frame, textvariable=folder_path, anchor="w")
folder_path_label.pack(fill="x", pady=2)

csv_path_label = ctk.CTkLabel(info_frame, textvariable=csv_path, anchor="w")
csv_path_label.pack(fill="x", pady=2)

# ---------------------------------------------------------------------------
# Start GUI loop
root.mainloop()

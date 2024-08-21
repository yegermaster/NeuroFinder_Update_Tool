"""
This module provides a GUI for uploading CSV and Excel files,]
as well as for uploading images to ImgBB and updating a CSV file with image URLs.
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
from backend import DbHandler, escape_special_characters
from dotenv import load_dotenv
import requests


# Load environment variables
load_dotenv()
MAIN_DB_PATH = os.getenv('MAIN_DB_PATH')
NOT_NEUROTECH_DB_PATH = os.getenv('NOT_NEUROTECH_DB_PATH')
NEW_COMPANIES_PATH = os.getenv('NEW_COMPANIES_PATH')
IMGBB_UPLOAD_URL = os.getenv('IMGBB_UPLOAD_URL')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')
UPDATED_COMPANIES_PATH = os.getenv('UPDATED_COMPANIES_PATH')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
FILE_TYPES = ["tsun", "cb", "pb", "other"]
loading_files = []
loaded_files = []
db_handler = DbHandler(MAIN_DB_PATH, NOT_NEUROTECH_DB_PATH)

# Initialize the root window with customtkinter style
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = TkinterDnD.Tk()
root.title("File Upload GUI")
root.geometry("600x600")

folder_path = tk.StringVar()
csv_path = tk.StringVar()


def upload_to_imgbb(image_path: str) -> str:
    """Uploads an image to ImgBB and returns the URL of the uploaded image."""
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
    "Updates a CSV file by adding the image URL to the corresponding company."
    rows = []
    updated = False
    company_name = escape_special_characters(company_name)
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ['ImageURL'] if 'ImageURL' not in reader.fieldnames else reader.fieldnames
        for row in reader:
            if escape_special_characters(row['Company Name']) == company_name:
                row['ImageURL'] = image_url
                updated = True
            rows.append(row)
    if updated:
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

def process_file(filepath: str):
    """Reads a file and updates the loading file list. """
    try:
        if filepath.endswith('.csv'):
            pd.read_csv(filepath)
        elif filepath.endswith('.xlsx'):
            pd.read_excel(filepath)
        else:
            messagebox.showerror("Error", "Unsupported file format.")
            return
        loading_files.append({"path": filepath, "data_type": tk.StringVar(value="tsun")})
        refresh_loading_file_list()
    except FileNotFoundError:
        messagebox.showerror("Error", f"File not found: {filepath}")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Error", f"The file is empty: {filepath}")
    except pd.errors.ParserError:
        messagebox.showerror("Error", f"Parsing error in file: {filepath}")
    except PermissionError:
        messagebox.showerror("Error", f"Permission denied: {filepath}")

def refresh_loading_file_list():
    """Updates the displayed list of loading files."""
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
                                    command=lambda idx=i: delete_file_from_loading_list(idx))
        delete_button.grid(row=i, column=2, padx=5, pady=5)

def delete_file_from_loading_list(index: int):
    """Deletes a file from the loading file list."""
    del loading_files[index]
    refresh_loading_file_list()

def open_file_dialog():
    """Opens a file dialog to select a file for uploading."""
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"),
                                                      ("Excel files", "*.xlsx")])
    if filepath:
        process_file(filepath)

def drop(event: any):
    """Handles file drop events."""
    filepath = event.data
    if filepath:
        filepath = filepath.strip('{}')  # Strip curly braces if present
        process_file(filepath)

def load_all_files():
    """ Validates and uploads all files in the loading list."""
    if not loading_files:
        messagebox.showerror("Error", "No files to upload.")
        return

    valid_files = []
    for file_info in loading_files:
        data_type = file_info['data_type'].get()
        file_path = file_info['path']
        if not db_handler.validate_file_type(file_path, data_type):
            messagebox.showerror("Error",
                                  f"File '{file_path.split('/')[-1]}' does not match the specified type '{data_type}'. Please try again.")
        else:
            valid_files.append(file_info)

    if not valid_files:
        return

    for file_info in valid_files:
        db_handler.start_searching_process(file_info['path'], file_info['data_type'].get())
        db_handler.start_update_process(file_info['path'], file_info['data_type'].get())
        loaded_files.append(file_info)

    loading_files.clear()
    refresh_loading_file_list()
    refresh_loaded_file_list()
    messagebox.showinfo("Success", "All valid files uploaded successfully!")

def export_loaded_files():
    """Exports the loaded files to an Excel file."""
    if not loaded_files:
        messagebox.showerror("Error", "No files to export.")
        return
    db_handler.export_new(NEW_COMPANIES_PATH)
    messagebox.showinfo("Success", "All files exported successfully!")

def export_updated_file():
    """Exports an Excel file of companies that need to be updated."""
    db_handler.export_updates(UPDATED_COMPANIES_PATH)
    messagebox.showinfo("Success", "Updated companies exported successfully!")

def refresh_loaded_file_list():
    """Updates the displayed list of loaded files."""
    for widget in loaded_list_frame.winfo_children():
        widget.destroy()

    for i, file_info in enumerate(loaded_files):
        file_path = file_info["path"]

        file_label = ttk.Label(loaded_list_frame, text=file_path.split('/')[-1])
        file_label.grid(row=i, column=0, padx=5, pady=5)

def upload_images_and_update_csv():
    """Opens the upload image GUI"""
    folder = folder_path.get()
    csv_file = csv_path.get()
    if folder and csv_file:
        process_image_folder(folder, csv_file)
    else:
        messagebox.showwarning("Input Error",
                                "Please select both the image folder and the CSV file.")

def process_image_folder(image_folder_path, csv_file):
    """Processes all images in a folder,
    uploads them to ImgBB, and updates the CSV with the image URLs."""
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


# Main header
header = ctk.CTkLabel(root, text="Upload Files",
                       font=("Arial", 16),
                         fg_color="green",
                           text_color="white",
                             anchor="center")
header.pack(fill="x", pady=10)

# Img uploader
img_button = ctk.CTkButton(root,
                            text="Upload Images",
                            command=upload_images_and_update_csv)
img_button.pack(pady=10)

# Folder and CSV selection for image upload
folder_button = ctk.CTkButton(root,
                               text="Select Image Folder",
                                 command=lambda: folder_path.set(filedialog.askdirectory()))
folder_button.pack(pady=10)

csv_button = ctk.CTkButton(root,
                            text="Select CSV File",
                              command=lambda: csv_path.set(filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])))
csv_button.pack(pady=10)

# Drag and drop frame
drag_frame = ctk.CTkFrame(root, width=400, height=200, corner_radius=10)
drag_frame.pack(pady=20)
drag_frame.pack_propagate(False)

upload_button = ctk.CTkButton(drag_frame,
                               text="Upload File or Drag files here",
                                 command=open_file_dialog)
upload_button.pack(pady=10)

# Button frame
button_frame = ctk.CTkFrame(root, width=600, height=100, corner_radius=10)
button_frame.pack(pady=20)
button_frame.pack_propagate(False)

final_upload_button = ctk.CTkButton(button_frame, text="Load All Files", command=load_all_files)
final_upload_button.pack(pady=5)

export_new_companies_button = ctk.CTkButton(button_frame, text="Export New Companies", command=export_loaded_files)
export_new_companies_button.pack(pady=5)

export_updates_button = ctk.CTkButton(button_frame, text="Export Updated Companies", command=export_updated_file)
export_updates_button.pack(pady=5)


# Section for files ready to load
loading_label = ctk.CTkLabel(root, text="Files ready to Load:", anchor="w")
loading_label.pack(anchor="w", padx=20)

loading_list_frame = ctk.CTkFrame(root)
loading_list_frame.pack(pady=10, padx=20, fill="both", expand=True)

# Section for files already loaded
loaded_label = ctk.CTkLabel(root, text="Files Already Loaded:", anchor="w")
loaded_label.pack(anchor="w", padx=20)

loaded_list_frame = ctk.CTkFrame(root)
loaded_list_frame.pack(pady=10, padx=20, fill="both", expand=True)

drag_frame.drop_target_register(DND_FILES)
drag_frame.dnd_bind('<<Drop>>', drop)

root.mainloop()
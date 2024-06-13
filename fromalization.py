"""
This script formalizes the database file by going thorugh each column
and it's charchtarstic and formalzies it.

Functions:
    formalize_company_name(name): Cleans and formalizes company names.
    format_date(date): Formats dates to dd-mm-yyyy format.
    format_logo_in_visualization_folder(value): Converts values to TRUE or FALSE.

Usage:
    Simply run this script with the Excel file in the specified file path.
    The script will output a new Excel file with the formalized data.

Dependencies:
    - pandas
"""

import pandas as pd



def formalize_company_name(name:str)->str:
    """ Clean and formalize company names."""
    if pd.isna(name):
        return name
    # Remove leading/trailing spaces and proper case formatting
    name = name.strip().title()
    return name

def format_date(date:str)->str:
    """ Format the date to dd-mm-yyyy."""
    if pd.isna(date):
        return date
    try:
        return pd.to_datetime(date, format='%d.%m.%Y').strftime('%d-%m-%Y')
    except ValueError:
        try:
            return pd.to_datetime(date, format='%d.%m.%y').strftime('%d-%m-%Y')
        except ValueError:
            return date

def format_logo_in_visualization_folder(value:str)->str:
    """ Convert values in the 'Logo in Visualization folder?' column to TRUE or FALSE."""
    if pd.isna(value):
        return value
    if value.lower() == "yes":
        return "TRUE"
    else:
        return "FALSE"

def apply_formalization(file_path):
    """Applys formalization for all coulmns"""
    # Load the Excel file
    file = pd.read_excel(file_path)

    # Formalize Company_Name column
    col = "Company_Name"
    file[col] = file[col].apply(formalize_company_name)

    # Formalize Company_Name column "Logo in Visualization folder?" column
    col = "Logo in Visualization folder?"
    file[col] = file[col].apply(format_logo_in_visualization_folder)

    # Formalize Company_Name column Updating_Date column
    col = 'Updating_Date'
    file[col] = file[col].apply(format_date)

    # Save the changes to a new Excel file
    output_path = "main/formalized_main_db.xlsx"
    file.to_excel(output_path, index=False)

    file_path = "main/main_db.xlsx"
    apply_formalization(file_path)

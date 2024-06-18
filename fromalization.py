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
from main.constants import location_dict

def standardize_location(location):
    """
    Standardize location names using a predefined dictionary.
    """
    standardized_locations  = location_dict
    return standardized_locations.get(location, location)


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

def apply_formalization(file_path:str)->pd.DataFrame:
    """Applys formalization for all coulmns"""
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Formalize Company_Name column
    col = "Company_Name"
    df[col] = df[col].apply(formalize_company_name)

    # Formalize Company_Location column
    col = 'Company_Location'
    df[col] = df[col].apply(standardize_location)

    # Formalize Company_Name column "Logo in Visualization folder?" column
    col = "Logo in Visualization folder?"
    df[col] = df[col].apply(format_logo_in_visualization_folder)

    # Formalize Company_Name column Updating_Date column
    col = 'Updating_Date'
    df[col] = df[col].apply(format_date)

    return df

def export_file(file_path:str, df:pd.DataFrame):
    """Exports file to file path"""
    df.to_excel(file_path, index=False)

PATH = "main/main_db.xlsx"
formalized_file = apply_formalization(PATH)

NEW_PATH = "formalize.xlsx"
export_file(NEW_PATH, formalized_file)

"""
null_finder.py - This module provides a quick search for all null rows in the data base
"""

import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()
MAIN_DB_PATH = os.getenv('MAIN_DB_PATH')
NULL_DATA_PATH = os.getenv('NULL_DATA_PATH')

def find_nulls_for_company(input_file, output_file):
    """Finds all the null rows in the data"""
    try:
        # Read the Excel file
        df = pd.read_excel(input_file)

        # Ensure the first column is the company name
        first_column = df.columns[0]
        if first_column.lower() not in ['company name', 'company', 'companyname']:
            print("Error: The first column must be 'Company Name' or equivalent.")
            return

        # Find rows with null values
        null_data = df[df.isnull().any(axis=1)].copy()

        if null_data.empty:
            print("No null data found in the file.")
        else:
            # Add a column listing the null columns for each row
            null_data['Null Columns'] = null_data.apply(
                lambda row: [col for col in df.columns if pd.isnull(row[col])],
                axis=1
            )

            # Select only the Company Name and Null Columns
            output_df = null_data[[first_column, 'Null Columns']]

            # Rename columns for clarity (optional)
            output_df.rename(columns={first_column: 'Company Name'}, inplace=True)

            # Save to a single Excel sheet
            output_df.to_excel(output_file, index=False)

            print(f"Null data grouped by company saved to {output_file}")
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Input and output file paths
    find_nulls_for_company(MAIN_DB_PATH, NULL_DATA_PATH)
    # myseries = df.isnull().sum()
    # myseries.to_excel("main/data/null_list.xlsx")
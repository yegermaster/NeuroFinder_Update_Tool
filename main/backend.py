"""
backend.py - This module provides functions for realizing the automating tool algorithm.
"""

import re
import unicodedata
from datetime import datetime as dt
import pandas as pd


def clean_value(value):
    """Cleans the input value by stripping unwanted characters and converting to int if possible."""
    if pd.isna(value):
        return value
    cleaned_value = str(value).strip('="')
    try:
        return int(cleaned_value)
    except ValueError:
        return cleaned_value

def clean_dataframe(filepath, file_type='csv'):
    """Reads a file into a DataFrame, cleans it, and returns the cleaned DataFrame."""
    read_function = pd.read_csv if file_type == 'csv' else pd.read_excel
    df = read_function(filepath, index_col=False,
                   engine='openpyxl' if file_type == 'excel' else None)
    if 'former company names' in df.columns:
        df['former company names'] = df['former company names'].astype(str)
    for col in df.columns:
        df[col] = df[col].apply(clean_value)
    return df

def escape_special_characters(name: str) -> str:
    """Replaces special characters in a filename with underscores to ensure compatibility."""
    return re.sub(r'[^a-zA-Z0-9-_]', '_', name)

class DbHandler:
    """Handles a data files from tsun, cb, pb and others"""
    def __init__(self, main_db_path, not_neurotech_path):
        self.main_db = pd.read_excel(main_db_path)
        self.not_neurotech_db = pd.read_excel(not_neurotech_path)
        self.df = pd.DataFrame()
        self.new_companies_db = pd.DataFrame(columns=self.main_db.columns.tolist())
        self.update_companies_db = pd.DataFrame(columns=self.main_db.columns.tolist())

    def normalize(self, name: str) -> str:
        """Normalzies a given name string"""
        if not isinstance(name, str):
            return ''
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8')
        name = name.lower().strip()
        name = re.sub(r'[^a-z0-9 ]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name
    
    def normalize_column_category(self, column_data):
        """Normalizes the names in a given column of the DataFrame."""
        return column_data.apply(lambda x: self.normalize(x) if isinstance(x, str) else '')
    
    def is_company_in_database(self, company_name, db):
        """Checks if a company is already in the given database, including former names."""
        if 'Company Name' not in db.columns:
            raise ValueError("no company name")
        
        normalized_name = self.normalize(company_name)

        # Normalize 'Company_Name' column
        current_names = db['Company Name'].apply(self.normalize).tolist()

        # Initialize a set with current names
        all_names_set = set(current_names)

        # Normalize and process 'former company names' column
        if 'former company names' in db.columns:
            former_names_series = db['former company names'].dropna()
            for former_names in former_names_series:
                if isinstance(former_names, str):
                    names_list = [name.strip() for name in former_names.split(';')]
                    normalized_former_names = [self.normalize(name) for name in names_list]
                    all_names_set.update(normalized_former_names)

        return normalized_name in all_names_set

    def get_updating_date(self):
        """Adds the current date to the 'Updating_Date' column for new companies."""
        current_date = dt.now().strftime("%d-%m-%Y")

        if 'Updating_Date' not in self.new_companies_db.columns:
            self.new_companies_db['Updating_Date'] = current_date
        else:
            # Only update rows where 'Updating_Date' is NaN or empty
            self.new_companies_db['Updating_Date'] = self.new_companies_db['Updating_Date'].apply(
                lambda x: current_date if pd.isna(x) or x == '' else x
            )

    
    def export_new(self, path):
        """Exports new database to excel"""
        if not path.lower().endswith('.xlsx'):
            raise ValueError("File path must end with .xlsx")
        self.get_updating_date()
        self.new_companies_db.to_excel(path, index=False, engine='openpyxl')

    def export_updates(self, path):
        """Exports the updates database to an Excel file."""
        if not path.lower().endswith('.xlsx'):
            raise ValueError("File path must end with .xlsx")
        
        current_date = dt.now().strftime("%d-%m-%Y")
        if 'Updating_Date' not in self.update_companies_db.columns:
            self.update_companies_db['Updating_Date'] = current_date
        else:
            # Only update rows where 'Updating_Date' is NaN or empty
            self.update_companies_db['Updating_Date'] = self.update_companies_db['Updating_Date'].apply(
                lambda x: current_date if pd.isna(x) or x == '' else x
            )
        self.update_companies_db.to_excel(path, index=False, engine='openpyxl')

    def clear_new_db(self):
        """Clears new database"""
        self.new_companies_db = pd.DataFrame(columns=self.main_db.columns.tolist())

    def validate_file_type(self, file_path: str, data_type: str) -> bool:
        """Validates if the file content matches the specified data type."""
        self.df = clean_dataframe(file_path)
        required_columns = {
            'tsun': ['Finder URL'],
            'cb': ['CB Rank (Company)'],
            'pb': ['PitchBook uniqe column'],  # Update with actual columns if known
            'other': ['other format uniqe column']  # Update with actual columns if known
        }
        if data_type not in required_columns:
            return False
        return all(col in self.df.columns for col in required_columns[data_type])

    def start_searching_process(self, file_path: str, data_type: str):
        """Start the searching process of the algortheim"""
        self.df = clean_dataframe(file_path)
        if data_type == 'tsun':
            self.find_new_companies_tsun()
        elif data_type == 'cb':
            self.find_new_companies_cb()
        elif data_type == 'pb':
            self.find_new_companies_pb()
        else:
            self.find_new_companies_other()

    def start_update_process(self, file_path: str, data_type: str):
        """Start the updating process of the algortheim"""
        self.df = clean_dataframe(file_path)
        if data_type == 'tsun':
            self.update_current_companies_tsun()
        if data_type == 'cb':
            self.update_current_companies_cb()

    def find_new_companies_tsun(self):
        """Finds new companies from the Startup Nation Central data"""
        for _, row in self.df.iterrows():
            company_name = row['Name']
            description = row['Description']
            website = row['Finder URL']
            year_founded = row['Founded']
            employees = row['Employees']
            funding_stage = row['Funding Stage']
            is_in_main_db = self.is_company_in_database(company_name, self.main_db)
            is_in_not_neurotech = self.is_company_in_database(company_name, self.not_neurotech_db)
            is_in_new_db = self.is_company_in_database(company_name, self.new_companies_db)
            if not is_in_main_db and not is_in_not_neurotech and not is_in_new_db:
                new_entry = pd.Series({
                    'Company Name': company_name,
                    'Startup Nation Page': website,
                    'Company Founded Year': year_founded,
                    'Company Number of Employees': employees,
                    'Funding Status': funding_stage,
                    'Description': description
                })
                self.new_companies_db = pd.concat([self.new_companies_db, pd.DataFrame([new_entry])], ignore_index=True)

    def find_new_companies_cb(self):
        """Findes new compnies from the crunchbase"""
        for _, row in self.df.iterrows():
            company_name = row['Organization Name']
            description = row['Description']
            full_description = row['Full Description']
            website = row['Organization Name URL']
            year_founded = row['Founded Date']
            cb_rank = row['CB Rank (Company)']
            headquarters = row['Headquarters Location']

            is_in_main_db  = self.is_company_in_database(company_name, self.main_db)
            is_in_not_neurotech = self.is_company_in_database(company_name, self.not_neurotech_db)
            is_in_new_db = self.is_company_in_database(company_name, self.new_companies_db)

            if not is_in_main_db and not is_in_not_neurotech and not is_in_new_db:
                new_entry = {
                    'Company Name': company_name,
                    'CB (Crunchbase) Link': website,
                    'Company Founded Year': year_founded,
                    'Company_Location': headquarters,
                    'Description': description,
                    'Full Description': full_description,
                    'Company CB Rank': cb_rank
                }
                self.new_companies_db = pd.concat([self.new_companies_db, pd.DataFrame([new_entry])], ignore_index=True)

    def find_new_companies_pb(self):
        """Findes new compnies from pitchbook """
        print("handle_pb")

    def find_new_companies_other(self):
        """Handles other data"""
        print("handle_other")

    def normalize_employee_count(self, employee_str):
        """Normalize employee string to a format suitable for comparison."""
        if pd.isna(employee_str):
            return None

        # Remove any non-numeric characters except for "-" and ","
        employee_str = str(employee_str)
        employee_str = re.sub(r'[^0-9-]', '', employee_str)

        return employee_str.strip()

    def update_current_companies_tsun(self):
        """Updates current companies from tsun, focusing on the employees column."""
        for _, row in self.df.iterrows():
            company_name = row['Name']
            website = row['Finder URL']
            employees = self.normalize_employee_count(row['Employees'])
            funding_stage = row['Funding Stage']
            
            # Check if the company exists in the main_db
            is_in_main_db  = self.is_company_in_database(company_name, self.main_db)
            # Check if the company is already in the update_companies_db to avoid duplicate entries
            is_in_not_neurotech  = self.is_company_in_database(company_name, self.update_companies_db)
            # Check if the company is in the not neurotech database
            is_in_new_db  = self.is_company_in_database(company_name, self.not_neurotech_db)

            if is_in_main_db and not is_in_not_neurotech and not is_in_new_db:
                main_db_entry = self.main_db[self.main_db['Company Name'] == company_name]
                if not main_db_entry.empty:
                    main_db_entry = main_db_entry.iloc[0]  # Get the first row as a Series         
                    
                    # Initialize a dictionary to store the differences
                    differences = {}
                    
                    # Compare the employees column specifically
                    main_db_employees = self.normalize_employee_count(main_db_entry['Company Number of Employees'])
                    if employees and employees != main_db_employees:
                        differences['Company Number of Employees'] = employees

                    # Add other fields if needed
                    if website and website != main_db_entry['Startup Nation Page']:
                        differences['Startup Nation Page'] = website
                    if funding_stage and funding_stage != main_db_entry['Funding Status']:
                        differences['Funding Status'] = funding_stage
                    
                    # If there are any differences, add the updated data to update_companies_db
                    if differences:
                        differences['Company Name'] = company_name
                        self.update_companies_db = pd.concat([self.update_companies_db, pd.DataFrame([differences])], ignore_index=True)

    def update_current_companies_cb(self):
        """Updates current companies from Crunchbase, ensuring no duplicates after tsun updates."""
        for _, row in self.df.iterrows():
            company_name = row['Organization Name']
            website = row['Organization Name URL']
            cb_rank = row['CB Rank (Company)']
            is_in_main_db  = self.is_company_in_database(company_name, self.main_db)
            is_in_not_neurotech  = self.is_company_in_database(company_name, self.not_neurotech_db)
            if is_in_main_db and not is_in_not_neurotech:
                # Look for an existing entry in the update_companies_db
                existing_update = self.update_companies_db[self.update_companies_db['Company Name'] == company_name]

                # Initialize a dictionary to store the differences
                differences = {}
                if not existing_update.empty:
                    # Update existing entry if it exists
                    differences = existing_update.iloc[0].to_dict()
                else:
                    main_db_entry = self.main_db[self.main_db['Company Name'] == company_name]
                    if not main_db_entry.empty:
                        main_db_entry = main_db_entry.iloc[0].to_dict()
                    else:
                        # If the company is not found in main_db, skip to the next iteration
                        continue

                    # Update differences with new values if they differ
                    if website and website != main_db_entry.get('CB (Crunchbase) Link'):
                        differences['CB (Crunchbase) Link'] = website
                    if cb_rank and cb_rank != main_db_entry.get('Company CB Rank'):
                        differences['Company CB Rank'] = cb_rank

                # If there are any differences, update or add the data in update_companies_db
                if differences:
                    differences['Company Name'] = company_name
                    if not existing_update.empty:
                        # Update the existing entry in update_companies_db
                        self.update_companies_db.update(pd.DataFrame([differences]))
                    else:
                        # Add a new entry to update_companies_db
                        self.update_companies_db = pd.concat([self.update_companies_db, pd.DataFrame([differences])], ignore_index=True)

    def update_current_compnies_pb(self):
        """Updates current compnies from pb"""
        pass
    
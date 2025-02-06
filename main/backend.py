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
    cleaned_value = str(value).strip('="')  # Remove extra characters
    try:
        return int(cleaned_value)
    except ValueError:
        return cleaned_value.strip()


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
        self.main_db['Normalized_Company_Name'] = self.main_db['Company Name'].apply(self.normalize)
        self.not_neurotech_db['Normalized_Company_Name'] = self.not_neurotech_db['Company Name'].apply(self.normalize)
        self.df = pd.DataFrame()
        self.new_companies_db = pd.DataFrame(columns=self.main_db.columns.tolist())
        self.update_companies_db = pd.DataFrame(columns=self.main_db.columns.tolist())

    def normalize(self, name: str) -> str:
        if not isinstance(name, str):
            return ''
        normalized = name.casefold().strip()
        normalized = unicodedata.normalize('NFKC', normalized)
        normalized = re.sub(r'[\s\-]+', '', normalized)  # Remove spaces and dashes
        normalized = re.sub(r'[^\w]', '', normalized, flags=re.UNICODE)  # Keep only alphanumeric characters
        return normalized

    def is_company_in_database(self, company_name, db):
        """Checks if a company (normalized) exists in the given database (case-insensitive)."""
        if 'Company Name' not in db.columns:
            raise ValueError("The database does not contain a 'Company Name' column.")

        normalized_name = self.normalize(company_name)

        # If the database has not been normalized, do it once and store the set for fast lookup
        if 'Normalized_Company_Name' not in db.columns:
            db['Normalized_Company_Name'] = db['Company Name'].apply(self.normalize)

        all_names_set = set(db['Normalized_Company_Name'].dropna())

        # Add former company names to the set (normalize them as well)
        if 'former company names' in db.columns:
            for former_names in db['former company names'].dropna():
                if isinstance(former_names, str):
                    all_names_set.update(self.normalize(name.strip()) for name in former_names.split(';'))

        return normalized_name in all_names_set

    def normalize_column_category(self, column_data):
        """Normalizes the names in a given column of the DataFrame."""
        return column_data.apply(lambda x: self.normalize(x) if isinstance(x, str) else '')
    
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
        """Start the searching process of the algorithm and remove duplicates."""
        self.df = clean_dataframe(file_path)
        self.new_companies_db = pd.DataFrame(columns=self.main_db.columns.tolist())  # Reset
        
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
        """Finds new companies from the TSUN dataset and ensures unique entries."""
        tsun_companies = set(self.new_companies_db['Company Name'].apply(self.normalize).dropna())
        
        for _, row in self.df.iterrows():
            company_name = clean_value(row['Name'])  # Ensure value is cleaned
            if not isinstance(company_name, str) or company_name.strip() == "":
                continue
            
            normalized_name = self.normalize(company_name)
            is_in_main_db = self.is_company_in_database(company_name, self.main_db)
            is_in_not_neurotech = self.is_company_in_database(company_name, self.not_neurotech_db)

            if normalized_name not in tsun_companies and not is_in_main_db and not is_in_not_neurotech:
                new_entry = {
                    'Company Name': company_name,
                    'Startup Nation Page': row['Finder URL'],
                    'Company Founded Year': row['Founded'],
                    'Company Number of Employees': row['Employees'],
                    'Funding Status': row['Funding Stage'],
                    'Description': row['Description']
                }
                self.new_companies_db = pd.concat([self.new_companies_db, pd.DataFrame([new_entry])], ignore_index=True)
                tsun_companies.add(normalized_name)  # Ensure it’s not re-added

    def find_new_companies_cb(self):
        """Finds new companies from Crunchbase while ensuring no duplicates and merging with TSUN data if applicable."""
        
        if 'Company Name' in self.new_companies_db.columns:
            self.new_companies_db['Normalized_Company_Name'] = self.new_companies_db['Company Name'].apply(self.normalize)

        for _, row in self.df.iterrows():
            company_name = clean_value(row['Organization Name'])
            if not isinstance(company_name, str) or company_name.strip() == "":
                continue

            normalized_name = self.normalize(company_name)

            # Check if company already exists in `new_companies_db` (from TSUN)
            if normalized_name in set(self.new_companies_db['Normalized_Company_Name']):
                idx = self.new_companies_db[self.new_companies_db['Normalized_Company_Name'] == normalized_name].index[0]

                # Update missing CB columns while keeping existing TSUN data
                self.new_companies_db.loc[idx, 'CB (Crunchbase) Link'] = row.get('Organization Name URL', self.new_companies_db.loc[idx, 'CB (Crunchbase) Link'])
                self.new_companies_db.loc[idx, 'Company CB Rank'] = row.get('CB Rank (Company)', self.new_companies_db.loc[idx, 'Company CB Rank'])
                self.new_companies_db.loc[idx, 'Company_Location'] = row.get('Headquarters Location', self.new_companies_db.loc[idx, 'Company_Location'])
                self.new_companies_db.loc[idx, 'Full Description'] = row.get('Full Description', self.new_companies_db.loc[idx, 'Full Description'])
                self.new_companies_db.loc[idx, 'Company Founded Year'] = row.get('Founded Date', self.new_companies_db.loc[idx, 'Company Founded Year'])

            else:
                # If not in TSUN, check against `main_db` and `not_neurotech_db`
                is_in_main_db = self.is_company_in_database(company_name, self.main_db)
                is_in_not_neurotech = self.is_company_in_database(company_name, self.not_neurotech_db)

                if not is_in_main_db and not is_in_not_neurotech:
                    new_entry = {
                        'Company Name': company_name,
                        'CB (Crunchbase) Link': row.get('Organization Name URL', ''),
                        'Company Founded Year': row.get('Founded Date', ''),
                        'Company_Location': row.get('Headquarters Location', ''),
                        'Description': row.get('Description', ''),
                        'Full Description': row.get('Full Description', ''),
                        'Company CB Rank': row.get('CB Rank (Company)', '')
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

            # Check if the company exists in the main_db or update dbs using normalized comparisons.
            is_in_main_db = self.is_company_in_database(company_name, self.main_db)
            is_in_not_neurotech = self.is_company_in_database(company_name, self.not_neurotech_db)
            is_in_update_db = self.is_company_in_database(company_name, self.update_companies_db)

            if is_in_main_db and not is_in_not_neurotech and not is_in_update_db:
                norm_company_name = self.normalize(company_name)
                # Use the precomputed normalized column for lookup.
                main_db_entry = self.main_db[self.main_db['Normalized_Company_Name'] == norm_company_name]
                if not main_db_entry.empty:
                    main_db_entry = main_db_entry.iloc[0]  # Get the first matching row
                    differences = {}
                    main_db_employees = self.normalize_employee_count(main_db_entry['Company Number of Employees'])
                    if employees and employees != main_db_employees:
                        differences['Company Number of Employees'] = employees
                    if website and website != main_db_entry['Startup Nation Page']:
                        differences['Startup Nation Page'] = website
                    if funding_stage and funding_stage != main_db_entry['Funding Status']:
                        differences['Funding Status'] = funding_stage
                    if differences:
                        differences['Company Name'] = company_name
                        self.update_companies_db = pd.concat([self.update_companies_db, pd.DataFrame([differences])], ignore_index=True)

    def update_current_companies_cb(self):
        """Updates current companies from Crunchbase, ensuring no duplicates after tsun updates."""
        for _, row in self.df.iterrows():
            company_name = row['Organization Name']
            website = row['Organization Name URL']
            cb_rank = row['CB Rank (Company)']
            norm_company_name = self.normalize(company_name)
            is_in_main_db = self.is_company_in_database(company_name, self.main_db)
            is_in_not_neurotech = self.is_company_in_database(company_name, self.not_neurotech_db)
            if is_in_main_db and not is_in_not_neurotech:
                # Normalize the company names in update_companies_db on the fly.
                existing_update = self.update_companies_db[self.update_companies_db['Company Name'].apply(self.normalize) == norm_company_name]
                differences = {}
                if not existing_update.empty:
                    differences = existing_update.iloc[0].to_dict()
                else:
                    main_db_entry = self.main_db[self.main_db['Normalized_Company_Name'] == norm_company_name]
                    if not main_db_entry.empty:
                        main_db_entry = main_db_entry.iloc[0].to_dict()
                    else:
                        continue
                    if website and website != main_db_entry.get('CB (Crunchbase) Link'):
                        differences['CB (Crunchbase) Link'] = website
                    if cb_rank and cb_rank != main_db_entry.get('Company CB Rank'):
                        differences['Company CB Rank'] = cb_rank
                if differences:
                    differences['Company Name'] = company_name
                    if not existing_update.empty:
                        self.update_companies_db.update(pd.DataFrame([differences]))
                    else:
                        self.update_companies_db = pd.concat([self.update_companies_db, pd.DataFrame([differences])], ignore_index=True)

    def update_current_compnies_pb(self):
        """Updates current compnies from pb"""
        pass
    
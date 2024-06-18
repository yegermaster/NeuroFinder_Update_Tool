"""
This module provides functions for realzing the automating tool algortheim.
"""

import re
import os
import unicodedata
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
    for col in df.columns:
        df[col] = df[col].apply(clean_value)
    return df


def clean_and_save(filepath, output_dir='cleaned_data', file_type='csv'):
    """Cleans the file at filepath and saves the cleaned DataFrame."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cleaned_df = clean_dataframe(filepath, file_type)
    output_file_path = os.path.join(output_dir, f'cleaned_{os.path.basename(filepath)}')
    if file_type == 'csv':
        cleaned_df.to_csv(output_file_path, index=False)
    else:
        cleaned_df.to_excel(output_file_path, index=False)
    return cleaned_df


class DbHandler:
    """Represents a single file that has been uploaded"""
    def __init__(self, main_db_path: str, not_neuro_tech_path:str):
        self.main_db = pd.read_excel(main_db_path)
        self.not_neurotech_db = pd.read_excel(not_neuro_tech_path)
        self.df = None
        self.new_db = pd.DataFrame(columns=self.main_db.columns.tolist())


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

    def is_company_in_main_db(self, company_name):
        """Checks if a company is already in the given database."""
        normalized_name = self.normalize(company_name)
        current_names = self.normalize_column_category(self.main_db['Company_Name'])
        former_names = self.normalize_column_category(self.main_db.get('Former Company Names',
                                                                        pd.Series([])))
        return any((current_names == normalized_name) | (former_names == normalized_name))
    
    def is_company_in_new_db(self, company_name):
        """Checks if a company is already in the given database."""
        normalized_name = self.normalize(company_name)
        current_names = self.normalize_column_category(self.new_db['Company_Name'])
        return any(current_names == normalized_name)
    
    def export(self, path):
        """Exports new database to excel"""
        self.new_db.to_excel(path, index=False)
    
    def clear_new_db(self):
        """Clears new database"""
        self.new_db = pd.DataFrame(columns=self.main_db.columns.tolist())

    def validate_file_type(self, file_path: str, data_type: str) -> bool:
        """Validates if the file content matches the specified data type."""
        self.df = clean_dataframe(file_path)
        required_columns = {
            'tsun': ['Finder URL'],
            'cb': ['CB Rank (Company)'],
            'pb': ['PitchBook special column'],  # Update with actual columns if known
            'other': ['other format special column']  # Update with actual columns if known
        }
        if data_type not in required_columns:
            return False
        return all(col in self.df.columns for col in required_columns[data_type])


    def start_process(self, file_path: str, data_type: str):
        """Start the process of the algortheim"""
        self.df = clean_dataframe(file_path)
        if data_type == 'tsun':
            self.handle_tsun()
        elif data_type == 'cb':
            self.handle_cb()
        elif data_type == 'pb':
            self.handle_pb()
        else:
            self.handle_other()

    def is_company_not_neurotech(self, company_name):
        """Checks if a company is listed in the not neurotech database."""
        normalized_name = self.normalize(company_name)
        current_names = self.normalize_column_category(self.not_neurotech_db['Company_Name'])
        return any(current_names == normalized_name)

    def handle_tsun(self):
        """Handles the startup central data"""
        for _, row in self.df.iterrows():
            company_name = row['Name']
            description = row['Description']
            website = row['Finder URL']
            year_founded = row['Founded']
            employees = row['Employees']
            funding_stage = row['Funding Stage']
            condition_1 = self.is_company_in_main_db(company_name)
            condition_2 = self.is_company_not_neurotech(company_name)
            condition_3 = self.is_company_in_new_db(company_name)
            if not condition_1 and not condition_2 and not condition_3:
                new_entry = pd.Series({
                    'Company_Name': company_name,
                    'Startup Nation Page': website,
                    'Company_Founded_Year': year_founded,
                    'Company_Number_of_Employees': employees,
                    'Funding_Status': funding_stage,
                    'Description': description
                })
                self.new_db = pd.concat([self.new_db, pd.DataFrame([new_entry])], ignore_index=True)

    def handle_cb(self):
        """Handles crunchbase data"""
        for _, row in self.df.iterrows():
            company_name = row['Organization Name']
            description = row['Description']
            full_description = row['Full Description']
            website = row['Organization Name URL']
            year_founded = row['Founded Date']
            cb_rank = row['CB Rank (Company)']
            headquarters = row['Headquarters Location']
            condition_1 = self.is_company_in_main_db(company_name)
            condition_2 = self.is_company_not_neurotech(company_name)
            condition_3 = self.is_company_in_new_db(company_name)
            if not condition_1 and not condition_2 and not condition_3:
                new_entry = {
                    'Company_Name': company_name,
                    'CB (Crunchbase) Link': website,
                    'Company_Founded_Year': year_founded,
                    'Company_Location': headquarters,
                    'Description': description,
                    'Full Description': full_description,
                    'Company_CB_Rank': cb_rank
                }
                self.new_db = pd.concat([self.new_db, pd.DataFrame([new_entry])], ignore_index=True)

    def handle_pb(self):
        """Handles pitchbook data"""
        print("handle_pb")

    def handle_other(self):
        """Handles other data"""
        print("handle_other")

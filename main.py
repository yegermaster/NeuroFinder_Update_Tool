import pandas as pd
from name_regulator import NameRegulator
import csv
import constants as c
import os


def clean_value_csv(value):
    """Cleans the input value by stripping unwanted characters and converting to int if possible."""
    if pd.isna(value):
        return value
    cleaned_value = str(value).strip('="')
    try:
        return int(cleaned_value)
    except ValueError:
        return cleaned_value


def clean_dataframe_csv(file_path):
    """
    Reads the CSV file at file_path into a DataFrame, cleans it,
    and returns the cleaned DataFrame.
    """
    df = pd.read_csv(file_path, index_col=False)
    for column in df.columns:
        df[column] = df[column].apply(clean_value_csv)
    return df


def clean_value_xl(value):
    """
    Cleans the input value by stripping unwanted characters.
    If the value can be converted to int, it returns int, otherwise returns the cleaned string.
    """
    if pd.isna(value):
        return value
    cleaned_value = str(value).strip('="')
    try:
        return int(cleaned_value)
    except ValueError:
        return cleaned_value


def clean_dataframe_xl(file_path):
    """
    Reads the Excel file at file_path into a DataFrame, cleans it,
    and returns the cleaned DataFrame.
    """
    df = pd.read_excel(file_path, index_col=False, engine='openpyxl')
    for column in df.columns:
        df[column] = df[column].apply(clean_value_xl)
    return df


def clean_csv(file):
    base_dir = 'cleaned_data'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    cleaned_df = clean_dataframe_csv(file)

    cleaned_df.to_csv(f'cleaned_{file}', index=False)
    return cleaned_df


class NeuroFinder:
    def __init__(self, neurofinder_path: str):
        self.neurofinder_path = neurofinder_path
        self.neurofinder_db = clean_dataframe_xl(self.neurofinder_path)
        self.name_regulator = NameRegulator()
        self.new_db = self.create_new_db()

    def normalize_column_category(self, column_data: str) -> pd:
        return column_data.apply(lambda x: self.name_regulator.normalize(x) if isinstance(x, str) else '')

    def create_new_db(self) -> pd.DataFrame:
        columns = self.neurofinder_db.columns.tolist()
        return pd.DataFrame(columns=columns)

    def is_company_in_main_db(self, company_name: str) -> bool:
        """Returns True of company name are already in the database, otherwise returns False"""
        company_name = self.name_regulator.normalize(company_name)

        current_names = self.normalize_column_category(self.neurofinder_db['Company_Name'])
        former_names = self.normalize_column_category(self.neurofinder_db['former company names'])
        return any((current_names == company_name) | (former_names == company_name))

    def is_company_in_new_db(self, company_name: str) -> bool:
        company_name = self.name_regulator.normalize(company_name)
        current_names = self.normalize_column_category(self.new_db['Company_Name'])
        former_names = self.normalize_column_category(self.new_db['former company names'])
        return any((current_names == company_name) | (former_names == company_name))

    def handle_the_start_up_nation(self, key_words: list):
        for file in key_words:

            cleaned_df = clean_csv(f'data/{file}')

            for _, row in cleaned_df.iterrows():
                company_name = row['Name']
                description = row['Description']
                website = row['Finder URL']
                year_founded = row['Founded']
                employees = row['Employees']
                funding_stage = row['Funding Stage']

                if not self.is_company_in_main_db(company_name):
                    new_entry = {
                        'Company_Name': company_name,
                        'Startup Nation Page': website,
                        'Company_Founded_Year': year_founded,
                        'Company_Number_of_Employees': employees,
                        'Funding_Status': funding_stage,
                        'Description': description
                    }
                    self.new_db = pd.concat([self.new_db, pd.DataFrame([new_entry])], ignore_index=True)
        print('the start up nation uploaded')
        return self.new_db

    def handle_crunchbase(self, cb_file):
        cleaned_df = clean_csv(cb_file)

        for _, row in cleaned_df.iterrows():
            company_name = row['Organization Name']
            description = row['Description']
            full_description = row['Full Description']
            website = row['Organization Name URL']
            year_founded = row['Founded Date']
            cb_rank = row['CB Rank (Company)']
            headquarters = row['Headquarters Location']

            if not self.is_company_in_main_db(company_name):
                if self.is_company_in_new_db(company_name):
                    index = self.new_db[
                        self.new_db['Company_Name'] == self.name_regulator.normalize(company_name)].index
                    if len(index) > 0:
                        idx = index[0]
                        self.new_db.at[idx, 'CB (Crunchbase) Link'] = website
                        self.new_db.at[idx, 'Company_Location'] = headquarters
                        self.new_db.at[idx, 'Full Description'] = full_description
                        self.new_db.at[idx, 'Company_CB_Rank'] = cb_rank
                else:
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
        print('cb has uploaded')
        return self.new_db

    def export_new_db(self):
        self.handle_the_start_up_nation(c.key_words_files)
        self.handle_crunchbase('data/cb_info.csv')
        self.new_db = self.new_db[~self.new_db['Company_Name'].isin(c.old_companies)].reset_index(drop=True)
        self.new_db.to_excel('data/new.xlsx', sheet_name='new')

    def check_overlap(self):
        neurofinder_companies = self.neurofinder_db['Company_Name'].apply(
            lambda x: self.name_regulator.normalize(x)).unique()
        new_df = pd.read_excel('data/new.xlsx')
        new_companies = new_df['Company_Name'].apply(lambda x: self.name_regulator.normalize(x)).unique()
        common_companies = [company for company in new_companies if company in neurofinder_companies]
        if common_companies:
            print(f"Overlap found for companies: {common_companies}")
        else:
            print("No overlap found between new.xlsx and ֿNeuroTech Industry IL 2023.xlsx companies.")


if __name__ == "__main__":
    n = NeuroFinder('data/ֿNeuroTech Industry IL 2023.xlsx')
    n.export_new_db()
    n.check_overlap()

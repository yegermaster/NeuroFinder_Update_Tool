import pandas as pd
from old_code.name_regulator import NameRegulator
import csv
import old_code.constants as c
import os


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
    df = read_function(filepath, index_col=False, engine='openpyxl' if file_type == 'excel' else None)
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


class NeuroFinder:
    def __init__(self, neurofinder_path: str):
        self.neurofinder_path = neurofinder_path
        self.neurofinder_db = clean_dataframe(self.neurofinder_path, 'excel')
        self.name_regulator = NameRegulator()
        self.new_db = pd.DataFrame(columns=self.neurofinder_db.columns.tolist())

    def normalize_column_category(self, column_data):
        """Normalizes the names in a given column of the DataFrame."""
        return column_data.apply(lambda x: self.name_regulator.normalize(x) if isinstance(x, str) else '')

    def is_company_in_db(self, company_name, db):
        """Checks if a company is already in the given database."""
        normalized_name = self.name_regulator.normalize(company_name)
        current_names = self.normalize_column_category(db['Company_Name'])
        former_names = self.normalize_column_category(db.get('Former Company Names', pd.Series([])))
        return any((current_names == normalized_name) | (former_names == normalized_name))

    def add_company_to_db(self, company_info, db_name='new'):
        """Adds a new company entry to the specified database."""
        db = self.new_db if db_name == "new" else self.neurofinder_db
        db = pd.concat([db, pd.DataFrame([company_info])], ignore_index=True)
        if db_name == 'new':
            self.new_db = db
        else:
            self.neurofinder_db = db

    def process_company_files(self, files, db_name='new'):
        """Processes company files, adding new entries to the database."""
        for file_path in files:
            cleaned_df = clean_and_save(file_path, file_type='csv' if file_path.endswith('.csv') else 'excel')
            for _, row in cleaned_df.iterrows():
                company_name = row.get("Name", "")
                if company_name and not self.is_company_in_db(company_name,
                                                              self.neurofinder_db) and not self.is_company_in_db(
                        company_name, self.new_db):
                    self.add_company_to_db(row.to_dict(), db_name)

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
    neurofinder = NeuroFinder('data/ֿNeuroTech Industry IL 2023.xlsx')

    neurofinder.process_company_files(['data/startup_nation.csv', 'data/cb_info.csv'])
    neurofinder.export_new_db()
    neurofinder.check_overlap()

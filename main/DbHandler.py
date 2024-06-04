import os
import re
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


class DbHandler:
    """Represents a single file that has been uploaded"""
    def __init__(self, main_db:str, file_path:str, data_type:str):
        self.file_path = file_path
        self.data_type = data_type
        self.main_db=main_db
        self.new_db = ''

    def generate_new_file(self):
        """Sends to new compnies to the new file"""
        if self.data_type=="tsun":
            self.handle_tsun()
        elif self.data_type=="cb":
            self.handle_cb()
        elif self.data_type=="pb":
            self.handle_pb()
        elif self.data_type == "other":
            self.handle_other()
        else:
            return False
        
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
        former_names = self.normalize_column_category(self.main_db.get('Former Company Names', pd.Series([])))
        return any((current_names == normalized_name) | (former_names == normalized_name))

    def handle_tsun(self):
        """Handles the start up central data"""
        print("in handle tsun")
        cleaned_df = clean_dataframe(os.path.join('data', self.file_path))
        print(cleaned_df)
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
    
    def handle_cb(self):
        """Handles crunchbase data"""
        pass

    def handle_pb(self):
        """Handles pitchbook data"""
        pass

    def handle_other(self):
        """Handles other data"""
        pass



handler = DbHandler("main_db", "file_path", "data_type")
print(handler.file_path)
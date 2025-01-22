import os
from dotenv import load_dotenv
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
MAIN_DB_PATH = os.getenv('MAIN_DB_PATH')

def check_word_in_website(url, word="career"):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Ensure the request was successful

        # Parse the webpage content
        soup = BeautifulSoup(response.text, "html.parser")

        # Check if the word exists in the text content of the page
        return word.lower() in soup.get_text().lower()

    except requests.exceptions.RequestException:
        return False

def get_websites_from_excel(file_path):
    try:
        # Load the Excel file
        data = pd.read_excel(file_path)

        # Ensure required columns exist
        if 'Company Name' not in data.columns or 'Website' not in data.columns:
            raise ValueError("The Excel file must contain 'Company Name' and 'Website' columns.")
        
        return data
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure

def save_to_excel(data, output_file):
    try:
        data.to_excel(output_file, index=False)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving Excel file: {e}")

# Fetch data from the Excel file
data = get_websites_from_excel(MAIN_DB_PATH)

if not data.empty:
    # Filter rows where "career" is found
    results = []
    for _, row in data.iterrows():
        website = row['Website']
        if pd.notna(website) and check_word_in_website(website):
            results.append({
                'Company Name': row['Company Name'],
                'Website': website
            })
    
    # Convert results to DataFrame
    found_data = pd.DataFrame(results)

    # Output results
    print(f"Total websites with 'career' found: {len(found_data)}")
    
    if not found_data.empty:
        output_file = "main/companies_with_career.xlsx"
        save_to_excel(found_data, output_file)
    else:
        print("No websites with 'career' found.")

"""
website finder.py - This module provides a a checker for the website columns rows in the data base.
it goes over each of the websites and returns all the not working websites
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from dotenv import load_dotenv
import pandas as pd
import requests

# Load environment variables
load_dotenv()
MAIN_DB_PATH = os.getenv('MAIN_DB_PATH')
WEBSITE_STATUS_PATH = os.getenv('WEBSITE_STATUS_PATH')

def get_website_status(url):
    """
    Checks the status of a website.

    Returns:
        A tuple (status_code, is_reachable) where:
            - status_code: HTTP status code or error message.
            - is_reachable: True if the website is reachable False otherwise.
    """
    try:
        response = requests.get(url, timeout=10)
        # Treat 403 and 406 as reachable
        if response.status_code in [403, 406, 404]: # link worked when those erros appeared
            return response.status_code, True
        return response.status_code, response.status_code < 400
    except requests.exceptions.RequestException as e:
        return str(e), False

def main():
    "main function the go over the websites"
    data = pd.read_excel(MAIN_DB_PATH)

    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(get_website_status,
                                          row['Website']): row for _, row in data.iterrows() if pd.notna(row['Website'])}

        for future in as_completed(future_to_url):
            row = future_to_url[future]
            company = row['Company Name']
            print(company)
            website = row['Website']

            try:
                status_code, is_reachable = future.result()
                # Append only if not reachable and not 403/406
                if not is_reachable:
                    results.append({
                        'Company Name': company,
                        'Website': website,
                        'Status Code': status_code
                    })
            except Exception as e:
                print(f"Error processing {website}: {e}")
                results.append({
                    'Company Name': company,
                    'Website': website,
                    'Status Code': f"Error: {e}"
                })

    # Create a DataFrame for the results
    results_df = pd.DataFrame(results)

    # Save results to Excel
    results_file_path = WEBSITE_STATUS_PATH
    results_df.to_excel(results_file_path, index=False)

    # Print summary
    print(f"Total websites checked: {len(data)}")
    print(f"Total websites not reachable or errored: {len(results_df)}")
    print(f"Saved results to {results_file_path}")

if __name__ == "__main__":
    main()

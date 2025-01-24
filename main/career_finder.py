"""
career_finder.py - This module searches key words in all the websites and by the provides
an indication for the company's recruting status.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from dotenv import load_dotenv
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
MAIN_DB_PATH = os.getenv('MAIN_DB_PATH')
RECRUITMENT_STATUS_PATH = os.getenv('RECRUITMENT_STATUS_PATH')
RECRUITMENT_KEYWORDS = os.getenv('RECRUITMENT_KEYWORDS', '')
RECRUITMENT_KEYWORDS = RECRUITMENT_KEYWORDS.split(',')

def check_recruiting_keywords(url, keywords=RECRUITMENT_KEYWORDS):
    """Checks for the presence of any recruitment keywords in the website's text. """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        page_text = BeautifulSoup(response.text, "html.parser").get_text().lower()
        found = [keyword for keyword in keywords if keyword.lower() in page_text]
        return found
    except requests.exceptions.RequestException:
        return None

def main():
    """Function to run the indication check. """
    data = pd.read_excel(MAIN_DB_PATH)
    found_data = []
    error_websites = []
    not_found_websites = []

    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(check_recruiting_keywords,
                                          row['Website']): row for _, row in data.iterrows() if pd.notna(row['Website'])}
        for future in as_completed(future_to_url):
            row = future_to_url[future]
            company = row['Company Name']
            print(company)
            website = row['Website']
            try:
                result = future.result()
                if result is None:
                    error_websites.append(website)
                elif result:
                    found_data.append({
                        'Company Name': company,
                        'Website': website,
                        'Found Keywords': ', '.join(result)
                    })
                else:
                    not_found_websites.append(website)
            except Exception as e:
                print(f"Error processing {website}: {e}")
                error_websites.append(website)

    # Create DataFrames for each category
    found_df = pd.DataFrame(found_data)
    error_df = pd.DataFrame({'Website': error_websites})
    not_found_df = pd.DataFrame({'Website': not_found_websites})

    # Print summary
    print(f"Total websites checked: {len(data)}")
    print(f"Total websites with recruiting indicators: {len(found_df)}")
    print(f"Total websites not reachable (error): {len(error_df)}")
    print(f"Total websites reachable but without recruiting indicators: {len(not_found_df)}\n")

    # Optionally, print detailed counts per keyword
    keyword_counts = {}
    for keywords in found_df['Found Keywords']:
        for keyword in keywords.split(', '):
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

    print("Recruitment Keywords Found:")
    for keyword, count in keyword_counts.items():
        print(f"  {keyword}: {count}")

    # Save results to Excel with multiple sheets
    with pd.ExcelWriter(RECRUITMENT_STATUS_PATH) as writer:
        found_df.to_excel(writer, sheet_name='Found', index=False)
        error_df.to_excel(writer, sheet_name='Errors', index=False)
        not_found_df.to_excel(writer, sheet_name='Not Found', index=False)
    print("\nSaved results to main/recruitment_results.xlsx")

if __name__ == "__main__":
    main()

import csv

israel_companies = []

with open('organizations.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['location_country_code'] == 'IL':
            israel_companies.append(row)

print(f"Total Israeli companies found: {len(israel_companies)}")

import requests
import pandas as pd

# Overpass API endpoint
url = "http://overpass-api.de/api/interpreter"

# Correct area ID calculation for the relation
relation_id = 1473946
area_id = 3600000000 + relation_id

# Overpass query with area ID for Israel
query = f"""
[out:json];
area({area_id})->.searchArea;
(
  node["place"="city"](area.searchArea);
  node["place"="town"](area.searchArea);
  node["place"="village"](area.searchArea);
  node["place"="hamlet"](area.searchArea);
);
out body;
>;
out skel qt;
"""

# Send the request
response = requests.get(url, params={'data': query})
data = response.json()

# Check if data is fetched
if 'elements' in data:
    # Process the data
    locations = []
    for element in data['elements']:
        if 'tags' in element:
            name = element['tags'].get('name:en', element['tags'].get('name'))
            if name:
                locations.append({
                    'id': element['id'],
                    'lat': element['lat'],
                    'lon': element['lon'],
                    'name': name
                })

    # Print fetched locations
    print(locations)

    # Convert to DataFrame and save as CSV
    if locations:
        df = pd.DataFrame(locations)
        df.to_csv('israel_locations.csv', index=False)
    else:
        print("No locations found.")
else:
    print("No data returned from the Overpass API.")

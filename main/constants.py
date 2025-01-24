"""constants.py - consants and normalization for the model"""

import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MAIN_DB_PATH = os.getenv('MAIN_DB_PATH')

# Load your Excel sheet into a DataFrame
file_path = MAIN_DB_PATH
df = pd.read_excel(file_path)

# Your dictionary of location corrections and district mappings
location_dict = {
    "Tel Aviv": "Tel Aviv-Yafo",
    "Tel Aviv-Yafo": "Tel Aviv-Yafo",
    "Rehovot": "Rehovot",
    "Jerusalem": "Jerusalem",
    "Haifa": "Haifa",
    "Lod": "Lod",
    "Beit Yehoshua": "Beit-Yehoshua",
    "Yokne'am Illit": "Yokneam",
    "Qatsrin": "Qatsrin",
    "Kiryat Bialik": "Kiryat-Bialik",
    "Herzliya": "Herzliya",
    "Ra'anana": "Raanana",
    "Nof HaGalil": "Nof-HaGalil",
    "Or Akiva": "Or-Akiva",
    "Netanya": "Netanya",
    "Rishon LeTsiyon": "Rishon-LeTsiyon",
    "Ramat Hasharon":"Ramat-Hasharon",
    "Hod Hasharon": "Hod-Hasharon",
    "Aderet":"Aderet",
    "Yavne": "Yavne",
    "Tzur Yigal": "Tzur-Yigal",
    "Ramat Gan": "Ramat-Gan",
    "Yehud": "Yehud",
    "Even Yehuda": "Even Yehuda",
    "Petah Tikva":"Petah Tikva", 
    "Hofit":"Hofit",
    "Rosh Haayin":"Rosh Haayin",
    "Caesarea":"Caesarea",
    "Ness Ziona":"Ness Ziona",
    "Benei Zion": "Benei Zion",
    "Misgav": "Misgav",
    "Kiriat Arieh, HaMerkaz, Israel":"Petah Tikva",
    "Mata":"Mata",
    "Kiryat Ono":"Kiryat Ono",
    "Be'er Sheva":"Beer Sheva",
    "Kfar Saba":"Kfar Saba",
    "Tzur Yitzhak":"Tzur Yitzhak",
    "Shorashim":"Shorashim",
    "Kfar Yona":"Kfar Yona",
    "Savyon":"Savyon",
    "Nazareth":"Nazareth",
    "Nir`am":"Nir Am",
    "Tirat Carmel":"Tirat Carmel",
    "Lehavim":"Lehavim",
    "Shlomi":"Shlomi",
    "Kibutz Reim":"Reim",
    "Ashkelon":"Ashkelon",
    "Ramat Yishai":"Ramat Yishai",
    "Kfar Sava":"Kfar Saba",
    "Yeruham":"Yeruham",
    "Sha'ar Ha'negev":"Shaar Hanegev",
    "Binyamina":"Binyamina",
    "Zur Moshe":"Zur Moshe",
    "Modi'in-Maccabim-Re'ut":"Modin-Maccabim-Reut",
    "Hadera": "Hadera",
    "Gan Soreq":"Gan Soreq",
    "Bnei Brak":"Bnei Brak",
    "Migdal HaEmek":"Migdal HaEmek",
    "Nesher":"Nesher",
    "Be'er Ya'akov":"Be'er Ya'akov",
    "Beit Shemesh":"Beit Shemesh",
    "Modiin":"Modiin",
    "Givatayim":"Givatayim",
    "Pardes Hanna-Karkur":"Pardes Hanna-Karkur",
    "Acre":"Acre",
    "Jerusalem, Yerushalayim, Israel":"Jerusalem, Yerushalayim, Israel",
    "Or Yehuda":"Or Yehuda",
    "Shefayim":"Shefayim"
}

district_locations = {
    "Central": ["Rehovot", "Lod", "Yavne", "Petah Tikva", "Rosh Haayin",
                "Caesarea", "Ness Ziona", "Bnei Brak", "Ramat Gan", "Givatayim",
                "Herzliya", "Ra'anana", "Hod Hasharon", "Ramat Hasharon", "Modi'in-Maccabim-Re'ut",
                "Or Yehuda", "Shefayim", "Hadera", "Be'er Ya'akov", "Gan Soreq",
                "Beit Yehoshua"],

    "Haifa": ["Haifa", "Acre",  "Kiryat Bialik", "Or Akiva", "Netanya",
               "Nof HaGalil", "Migdal HaEmek", "Nesher", "Tirat Carmel", "Pardes Hanna-Karkur"],

    "Jerusalem": ["Jerusalem", "Modin-Maccabim-Reut", "Beit Shemesh", "Mata"],

    "Northern": ["Yokne'am Illit", "Nazareth", "Misgav", "Zur Moshe", "Shorashim", "Shlomi", "Qatsrin"],

    "Southern": ["Ashkelon", "Be'er Sheva", "Yeruham", "Sha'ar Ha'negev", "Nir`am", "Lehavim", "Kibutz Reim"],

    "Tel-Aviv": ["Tel Aviv", "Tel Aviv-Yafo", "Tel Aviv-Yafo"]
}

# Create the combined dictionary with the correct names and districts
combined_dict = {}
for location, correct_name in location_dict.items():
    for district, locations in district_locations.items():
        if location in locations:
            combined_dict[location] = [correct_name, district]

# Add "Correct Name" and "District" columns
df['Correct Name'] = df['Company_Location'].map(lambda x: combined_dict.get(x, [x, "Unknown"])[0])
df['District'] = df['Company_Location'].map(lambda x: combined_dict.get(x, [x, "Unknown"])[1])

# Reorder the columns to place "Correct Name" and "District" right after "Company_Location"
columns_order = list(df.columns)
correct_name_index = columns_order.index('Company_Location') + 1
columns_order.insert(correct_name_index, columns_order.pop(columns_order.index('Correct Name')))
columns_order.insert(correct_name_index + 1, columns_order.pop(columns_order.index('District')))
df = df[columns_order]

# Save the updated DataFrame back to Excel
output_file_path = 'C:/Users/Owner/לימודים/בריינסטורם/neurofinder/pythonProject/location_fixed_main_db.xlsx'
df.to_excel(output_file_path, index=False)

print("District column added and file saved successfully!")

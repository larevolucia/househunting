from datetime import datetime
import pprint 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# URL for the properties listing in Amsterdam
PARARIUS_URL = "https://www.pararius.nl/koopwoningen/amsterdam/0-500000/2-slaapkamers/50m2/sinds-3"

# Path to the Excel file
EXCEL_FILE = "C:/Users/reisl/Desktop/tmp/properties_listings.xlsx"

# Initialize the WebDriver for Firefox (ensure geckodriver is installed)
driver = webdriver.Firefox()  # or webdriver.Chrome(), etc.
driver.get(PARARIUS_URL)

# Wait until the properties are loaded
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='page__row page__row--search-list']"))
    )
except Exception as e:
    print("Error loading properties:", e)
    driver.quit()
    exit()

# Initialize the dictionary to store the listed properties
listed_properties = {}

# Find all property items on the page
property_items = driver.find_elements(By.CSS_SELECTOR, "li[class='search-list__item search-list__item--listing']")

# Iterate over each property item and extract the required details
for index, item in enumerate(property_items, start=1):
    address = item.find_element(By.CSS_SELECTOR, "a[class='listing-search-item__link listing-search-item__link--title']").text.strip()
    url_suffix = item.find_element(By.CSS_SELECTOR, "a[class='listing-search-item__link listing-search-item__link--depiction']").get_attribute("href")
    price = item.find_element(By.CSS_SELECTOR, "div[class='listing-search-item__price']").text.strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    listed_properties[index] = {
        "address": address,
        "URL": url_suffix,
        "price": price,
        "timestamp": timestamp,
    }

pprint.pprint(listed_properties)

# Close the WebDriver
driver.quit()

# Convert the listed_properties dictionary to a DataFrame
new_listings_df = pd.DataFrame.from_dict(listed_properties, orient='index')

# Load the existing listings from the Excel file
try:
    existing_listings_df = pd.read_excel(EXCEL_FILE)
except FileNotFoundError:
    existing_listings_df = pd.DataFrame(columns=["address", "postal_code", "URL", "price", "timestamp"])

# Check for new listings
new_listings = new_listings_df[~new_listings_df["URL"].isin(existing_listings_df["URL"])]

# Append new listings to the existing DataFrame
if not new_listings.empty:
    updated_listings_df = pd.concat([existing_listings_df, new_listings], ignore_index=True)
    updated_listings_df.to_excel(EXCEL_FILE, index=False)
    print(f"Added {len(new_listings)} new listings to the Excel file.")
else:
    print("No new listings found.")

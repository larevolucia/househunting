"""This script aims to scrap properties listed at 
 Pararius.nl according to specific parameters"""

from datetime import datetime
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Load environment variables
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
SERVICE_ACCOUNT_FILE = (
    GOOGLE_SHEETS_CREDENTIALS_PATH
    if GOOGLE_SHEETS_CREDENTIALS_PATH
    else "credentials.json"
)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME = "Listings"


# Authenticate and initialize the Google Sheets client
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Attempt to access the specified spreadsheet and sheet
try:
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
except gspread.SpreadsheetNotFound:
    print("Error: Spreadsheet not found. Please check the SPREADSHEET_ID.")
    exit()
except gspread.WorksheetNotFound:
    print("Error: Worksheet not found. Please check the SHEET_NAME.")
    exit()


# URL for the properties listing in Amsterdam
PARARIUS_URL = (
    "https://www.pararius.nl/koopwoningen/amsterdam/0-500000/2-slaapkamers/50m2/sinds-3"
)

# Initialize the WebDriver for Firefox (ensure geckodriver is installed)
driver = webdriver.Firefox()
driver.get(PARARIUS_URL)

# Wait until the properties are loaded
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[class='page__row page__row--search-list']")
        )
    )
except Exception as e:  # pylint: disable=broad-exception-caught
    print("Error loading properties:", e)
    driver.quit()
    exit()

# Initialize the dictionary to store the listed properties
listed_properties = {}

# Find all property items on the page
property_items = driver.find_elements(
    By.CSS_SELECTOR, "li[class='search-list__item search-list__item--listing']"
)

# Iterate over each property item and extract the required details
for index, item in enumerate(property_items, start=1):
    address = item.find_element(
        By.CSS_SELECTOR,
        "a[class='listing-search-item__link listing-search-item__link--title']",
    ).text.strip()
    url_suffix = item.find_element(
        By.CSS_SELECTOR,
        "a[class='listing-search-item__link listing-search-item__link--depiction']",
    ).get_attribute("href")
    price = item.find_element(
        By.CSS_SELECTOR, "div[class='listing-search-item__price']"
    ).text.strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    listed_properties[index] = {
        "address": address,
        "URL": url_suffix,
        "price": price,
        "timestamp": timestamp,
    }

# Convert the listed_properties dictionary to a DataFrame
new_listings_df = pd.DataFrame.from_dict(listed_properties, orient="index")

# Load the existing listings from the Google Sheet
existing_listings = sheet.get_all_records()
existing_listings_df = pd.DataFrame(existing_listings)

# Check for new listings
new_listings = new_listings_df[
    ~new_listings_df["URL"].isin(existing_listings_df["URL"])
]

# Append new listings to the existing DataFrame and update the Google Sheet
if not new_listings.empty:
    updated_listings_df = pd.concat(
        [existing_listings_df, new_listings], ignore_index=True
    )
    # Fill NaN values with an empty string
    updated_listings_df = updated_listings_df.fillna("")
    # Update the Google Sheet
    sheet.update(
        [updated_listings_df.columns.values.tolist()]
        + updated_listings_df.values.tolist()
    )
    print(f"Added {len(new_listings)} new listings to the Google Sheet.")
else:
    print("No new listings found.")

# Close the WebDriver
driver.quit()

"""Web scrapes properties listed, add to google sheet and send email"""

from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# Email configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = os.environ.get("SMTP_PORT")
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")

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
    size = item.find_element(
        By.CSS_SELECTOR,
        "li[class='illustrated-features__item illustrated-features__item--surface-area']",
    ).text.strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    listed_properties[index] = {
        "address": address,
        "URL": url_suffix,
        "size": size,
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


# Function to send an email
def send_email(subject, body):
    """sending email notification"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USERNAME
    msg["To"] = EMAIL_RECIPIENT
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_USERNAME, EMAIL_RECIPIENT, text)
    server.quit()


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

    # Prepare email content
    NEW_SUBJECT = "New Property Listings Added"
    new_body = f"Added {len(new_listings)} new listings to the Google Sheet.\n\nhttps://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit?gid=0#gid=0"  # pylint: disable=line-too-long

    # Send email notification
    send_email(NEW_SUBJECT, new_body)

    print(
        f"Added {len(new_listings)} new listings to the Google Sheet and sent an email notification."  # pylint: disable=line-too-long
    )
else:
    print("No new listings found.")

# Close the WebDriver
driver.quit()

# househunting

Web scraping script checks Pararius.nl page for new entries using selenium.
With panda, the data found is managed and inserted in google sheets.

## Requires Google Sheets API configuration

### Step 1: Go to Google Cloud Console

Open your web browser and go to Google Cloud Console.
If you’re not already signed in, sign in with your Google account.

### Step 2: Select Your Project

If you don't have a project, quickly create one by clicking on New Project and providing a Project Name.
At the top left corner, click on the project dropdown.
Select your existing project from the list. If you don’t have a project, you need to create one by clicking "New Project".

### Step 3: Open the Service Accounts Page

In the left-hand navigation menu, go to IAM & Admin > Service Accounts.

### Step 4: Create a Service Account

Click on the "Create Service Account" button at the top.
Fill in the service account details:
Service account name: Enter a name for the service account.
Service account ID: This will be automatically filled based on the name.
Service account description: Enter a description (optional).
Click "Create and Continue".

### Step 5: Grant the Service Account Access to the Project

In the "Grant this service account access to the project" section, choose a role that grants appropriate access for your needs. For example, if you are accessing Google Sheets, you might need the "Editor" role.
Click "Continue".

### Step 6: Create Key for the Service Account

In the "Grant users access to this service account" section, click "Done".
You will be redirected back to the Service Accounts page. Find the service account you just created.
Click on the three dots on the right of the service account row, and select "Manage keys".
Click "Add Key" > "Create new key".
In the pop-up, select "JSON" and then click "Create".
A JSON file containing your service account key will be downloaded to your computer. This is the file you need for authentication.

## Share Google Sheet with your Project

Go to your google sheet and click on share. Share it with the client_email of your project.

## Set up App-Specific password

### Enable Two-Factor Authentication:

Ensure that two-factor authentication (2FA) is enabled on your Google account. You can enable it by visiting the Google Account Security page and following the instructions to set up 2FA.

### Generate App-Specific Password:

Go to the Google App Passwords page. You might need to sign in and complete 2FA.
Under "Select the app and device you want to generate the app password for," select "Mail" as the app and "Other" as the device. You can name it something like "Python Script".
Click "Generate".
Google will display a 16-character app-specific password. Copy this password.

### Update Your .env File:

Use the app-specific password in your .env file instead of your main Gmail password.

## PythonAnywhere

The `main.py` document was created to be run locally. Later I created an account at PythonAnywhere to run the code hourly.

In order to do that, it is required to install dependencies directly at PythonAnywhere bash console.
Since Selenium is not fully supported I had to change the code to used pyppeteer and BeautifulSoup instead.
For that it was also needed to download and install chrome via the terminal.

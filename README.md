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

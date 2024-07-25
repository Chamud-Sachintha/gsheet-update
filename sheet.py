from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
import gspread
import time
from datetime import datetime

task_id = input("Enter Task IDs (Comma separated):-")
row_number = int(input("Enter Page Start Row Number:-"))

#get task id list
task_id_list = task_id.split(",")

# Step 1: Initialize Selenium and log in
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Open the login page
login_url = "http://13.233.229.19/login"
driver.get(login_url)

# Find and fill the username and password fields
username = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/main/div[2]/div/form/div[1]/div/span/input")  # Update with actual username field name
password = driver.find_element(By.XPATH , "/html/body/div[2]/div[1]/main/div[2]/div/form/div[2]/div/span/input")  # Update with actual password field name

username.send_keys("chamud@wondereng.com")
password.send_keys("1234567890")

# Submit the login form
password.send_keys(Keys.RETURN)

# Let the login process complete (adjust the sleep time as necessary)
time.sleep(5)

# Step 2: Navigate to the target page and scrape data
url = "http://13.233.229.19/work_packages?query_props=%7B%22c%22%3A%5B%22id%22%2C%22subject%22%2C%22type%22%2C%22status%22%2C%22author%22%2C%22updatedAt%22%5D%2C%22hi%22%3Afalse%2C%22g%22%3A%22%22%2C%22t%22%3A%22updatedAt%3Adesc%2Cid%3Aasc%22%2C%22f%22%3A%5B%7B%22n%22%3A%22status%22%2C%22o%22%3A%22o%22%2C%22v%22%3A%5B%5D%7D%2C%7B%22n%22%3A%22assigneeOrGroup%22%2C%22o%22%3A%22%3D%22%2C%22v%22%3A%5B%22me%22%5D%7D%5D%7D"
driver.get(url)

# Let the page load
time.sleep(5)

for each_task_id in task_id_list:
    row_xpath = f"//tr[@data-work-package-id='{each_task_id}']"
    row = driver.find_element(By.XPATH, row_xpath)

    columns = row.find_elements(By.TAG_NAME, "td")
    task = {
        'id': columns[1].text.strip(),
        'subject': columns[2].text.strip(),
        'type': columns[3].text.strip(),
        'status': columns[4].text.strip(),
        'author': columns[5].text.strip(),
        'updatedAt': columns[6].text.strip(),
        'project': columns[7].text.strip()
    }

    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # Add your service account key file here
    creds = Credentials.from_service_account_file("logical-acolyte-429210-u0-99dd2e91d36d.json", scopes=scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1gSiKRlgkRYINzRfKMExv5eAreiwZYn2-cffYS8KdGQ8/edit?gid=0#gid=0"
    sheet = client.open_by_url(spreadsheet_url).sheet1

    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")

    formatted_task = {
        'DATE': formatted_date,
        'REQUIREMENT': "#" + task['id'] + ": " + task['subject'],
        'EMPLOYEE NAME': 'Chamud Sachintha',
        'CR / BUG / TASK': task['type'],
        'PLATFORM (PHP / JAVA)': task['project']
    }

    # Convert the dictionary to a list in the correct order
    header_row = sheet.row_values(1)  # Assumes headers are in the first row
    row_values = [formatted_task.get(header, '') for header in header_row]

    # Insert the row at the specified index
    sheet.insert_row(row_values, row_number)
    row_number += 1

print("Tasks have been successfully mapped to the Google Sheet.")

# Close the Selenium WebDriver
driver.quit()

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Setup Chrome options to mimic a real user
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)
url = 'https://finance.yahoo.com/quote/KO/history/'

try:
    print("Opening the URL...")
    driver.get(url)
    
    # Handle consent modal (might be in an iframe)
    try:
        # Wait for the consent modal to load
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "consent-frame"))
        )
        
        # Click the "Accept All" button inside the iframe
        consent_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Go to end"]]'))
        )
        consent_button.click()
        consent_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Accept all"]]'))
        )
        consent_button.click()
        print("Consent button clicked")
        driver.switch_to.default_content()  # Return to main page
    except Exception as e:
        print("Consent handling failed - trying fallback method:", e)
        # Fallback for iframe issues
        try:
            consent_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.NAME, "agree")))
            consent_button.click()
            print("Consent button clicked via fallback")
        except Exception as e:
            print("Could not handle consent popup:", e)

    # Load data
    try:
        show_all_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Show All Historical Data"]')))
        driver.execute_script("arguments[0].scrollIntoView();", show_all_link)
        driver.execute_script("arguments[0].click();", show_all_link)
        print("Clicked 'Show All Historical Data'")
        time.sleep(3)  # Allow data to load
    except Exception as e:
        print("Error loading full data:", e)

    # Scrape table data
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//table')))
    print("Table located")
    
    table = driver.find_element(By.XPATH, '//table')
    rows = table.find_elements(By.TAG_NAME, 'tr')
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        if len(cols) == 7:
            data.append([col.text for col in cols])

    # Save data
    df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
    file_path = 'data/KO_data.csv'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

except Exception as e:
    print(f"Critical error occurred: {e}")

finally:
    driver.quit()
    print("Browser closed")
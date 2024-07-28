from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
import pandas as pd
import time
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime


options = Options()
options.add_argument("--no-sandbox")
# options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=options
)

driver.set_window_size(1920, 1080)
base_url = 'https://tradingeconomics.com/calendar'
driver.get(base_url)

# Get parameter values
with open("config.json") as f:
    base_config = json.loads(f.read())

params = [x for x in base_config.get("parameters")]

# Create empty dataframe
df = pd.DataFrame()

# Choose all countries
WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-outline-secondary btn-calendar' and @onclick='toggleMainCountrySelection();']"))).click()
time.sleep(3)

WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='btn btn-outline-secondary te-c-option-world']/a[text()='All']"))).click()
time.sleep(3)

WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='btn-group  float-end;']//a[@class='btn btn-success  te-c-option' and @onclick='saveSelectionAndGO();']"))).click()
time.sleep(3)

# Scrape data for each set of parameters
for set in params:
    category = set.get("category")

    # Choose category 
    element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='btn-group']/button[contains(@class,'btn-calendar')]/i[@class='bi bi-bar-chart-fill']")))
    driver.execute_script("arguments[0].click();", element)
    time.sleep(3)
    element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='dropdown-item']/a[@href='/calendar/" + category + "']")))
    driver.execute_script("arguments[0].click();", element)
    time.sleep(3)

    # Prepare date ranges
    start_date = datetime.strptime(set.get("start_date"), "%Y-%m-%d")
    end_date = datetime.strptime(set.get("end_date"), "%Y-%m-%d")

    start_dates_list = []
    end_dates_list = []
    current_date = start_date

    while current_date <= end_date:
        start_dates_list.append(current_date)
        current_date = current_date + relativedelta(months=1)
        end_dates_list.append(current_date - relativedelta(days=1))

    start_dates_list = [date.strftime("%Y-%m-%d") for date in start_dates_list]
    end_dates_list = [date.strftime("%Y-%m-%d") for date in end_dates_list]

    for j in range(len(start_dates_list)):      
        #Choose date
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='btn-group']/button[@class='btn btn-outline-secondary btn-calendar']/i[@class='bi bi-calendar3']"))).click()
        time.sleep(3)
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='dropdown-item te-c-option']/a[contains(text(), 'Custom')]"))).click()
        time.sleep(3)
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='startDate']"))).clear()
        time.sleep(3)
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='startDate']"))).send_keys(start_dates_list[j])
        time.sleep(3)
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='endDate']"))).clear()
        time.sleep(3)
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='endDate']"))).send_keys(end_dates_list[j])
        time.sleep(3)
        element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'input-group')]/span[@class='input-group-btn']/button[@class='btn btn-success']")))
        driver.execute_script("arguments[0].click();", element)

        # Wait until table is visible
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, '//table[contains(@id,"calendar")]')))

        # Scrape indicator names
        indicators = driver.find_elements(By.XPATH, '//table[contains(@id,"calendar")]//tbody//tr//td[3]//*[1]')
        indicators_list = [indicator.text for indicator in indicators]

        # Scrape values
        elements = driver.find_elements(By.CLASS_NAME, "calendar-item")
        elements_list = [element.text if element.text else "NA" for element in elements]

        # Scrape dates
        months = driver.find_elements(By.XPATH, '//table[contains(@id,"calendar")]//tbody//tr//td[3]//span[@class="calendar-reference"]')
        months_list = [month.text if month.text else "NA" for month in months]

        # Add data to dataframe
        data = {
            'Publication_date': [f"{start_dates_list[j]}; {end_dates_list[j]}"]*len(indicators_list),
            'Category': [category]*len(indicators_list),
            'Indicator': indicators_list,
            'Date': months_list,
            'Country': elements_list[0::5],
            'Actual': elements_list[1::5],
            'Previous': elements_list[2::5],
            'Consensus': elements_list[3::5],
            'Forecast': elements_list[4::5]
        }
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)

# Export to excel
import openpyxl
df.to_excel("df_test3.xlsx")

# Close driver and connection
driver.quit()
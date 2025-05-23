# Python 3.12.4

# Package versions:
# - pandas 2.2.2
# - selenium 4.25.0

# This file contains the script that scrapes detailed features 
# of the sampled properties using their URLs, including:

# 1. Property Tenure (Leasehold/Freehold/etc.)
# 2. Distance to nearest Station (in miles)
# 3. Distance to nearest School (in miles)
# 4. Property Size (in squared meter)
# 5. Council Tax Band (rated: A-H)

# Import packages
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service

# Import the dataset
df = pd.read_csv(r'.\datasets\[sample]B28_120_properties.csv') # The main set for Analysis
df_test = pd.read_csv(r'.\datasets\[test_sample]B28_30_properties.csv') # Test set for Linear Regression

def scrape_details(dataset):

    # Create Service Object
    edgeService = Service(r"C:\\Users\blueb\\Downloads\\edgedriver_win64\\msedgedriver.exe")

    # Create Webdriver Object
    edgeDriver = webdriver.Edge(service = edgeService)

    # Dictionary contains the addtional scrapped features
    new_feilds = {'tenure' : [],
                'dist_to_station': [],
                'dist_to_school': [],
                'size': [],
                'tax_band': []}
    page_index = 0
    for u in dataset['url']:
        page_index += 1
        edgeDriver.get(u)
        time.sleep(1)
        
        # #Reject coockies first
        # cookies_button = WebDriverWait(edgeDriver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
        # # Scroll to the button to make sure it's in view
        # cookies_button.click()  # Click the "School" button
        # print("Rejected Cookies")
        # time.sleep(2)  # Pause to allow the page to load
        
        # Find Tenure:
        try:
            # Locate the <p> tag within <dd> following the <dt> tag with text "TENURE"
            tenure_element = WebDriverWait(edgeDriver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//dt[contains(., 'TENURE')]/following-sibling::dd//p"))
            )
            tenure = tenure_element.text
            new_feilds['tenure'].append(tenure)
        except:
            new_feilds['tenure'].append(None)
        
        try:
            #find size
            size_element = edgeDriver.find_element(By.XPATH, "//p[contains(text(), 'sq ft')]")
            #print('scrapped size')
            new_feilds['size'].append(size_element.text)
        except:
            new_feilds['size'].append(None)

        #Find the nearest station
        dist_sta = edgeDriver.find_element(By.CLASS_NAME, '_1ZY603T1ryTT3dMgGkM7Lg')
        print(f'Scrapped {page_index}/{len(dataset)}\r')
        new_feilds['dist_to_station'].append(dist_sta.text)
        
        # Wait until the button is present and clickable
        school_button = WebDriverWait(edgeDriver, 10).until(EC.element_to_be_clickable((By.ID, "Schools-button")))
        # Scroll to the button to make sure it's in view
        edgeDriver.execute_script("arguments[0].scrollIntoView();", school_button)
        school_button.click()  # Click the "School" button
        #print("Cliked School")
        time.sleep(2)  # Pause to allow the page to load
        dist_sch = edgeDriver.find_element(By.CLASS_NAME, '_3c74qVLIY4CQEzQmQ80PAU')
        new_feilds['dist_to_school'].append(dist_sch.text)
        
        # Locate the element containing "Band: B"
        try:
            # Wait until the dd element containing "Band: B" is located
            band_element = WebDriverWait(edgeDriver, 1).until(
                EC.visibility_of_element_located((By.XPATH, "//dd[contains(text(), 'Band:')]"))
            )

            # Extract and print the text from the element
            new_feilds['tax_band'].append(band_element.text)

        except Exception as e:
            new_feilds['tax_band'].append(None)
        
    edgeDriver.quit()
        
    # Concate new feilds to the 
    def new_dataset(dataset):
        dataset['tenure'] = new_feilds['tenure']
        dataset['to_nearest_station'] = new_feilds['dist_to_station']
        dataset['to_nearest_school'] = new_feilds['dist_to_school']
        dataset['tax_band'] = new_feilds['tax_band']
        
    return new_dataset(dataset)
    
#Start scraping and overwrite the csv fies
df_main_sample = scrape_details(df)
df_main_sample.to_csv(r'.\datasets\[sample]B28_120_properties.csv', index=False)

df_test_sample = scrape_details(df_test)
df_test.to_csv(r'.\datasets\[test_sample]B28_30_properties.csv', index=False)
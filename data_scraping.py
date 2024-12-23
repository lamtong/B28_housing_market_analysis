# Python 3.12.4

# Package versions:
# - pandas 2.2.2
# - selenium 4.25.0

# This file perfroms scaping the properties information below on rightmove.co.uk:

# 1. Property Adress: Property Title in the webpage
# 2. Price (in £)
# 3. Type: Detached, Semi-Detached, Flat, Terraced, etc.
# 4. Number of Bedrooms
# 5. Number of Bathrooms
# 6. Real Estate Agent
# 7. URL: the URL of to the detailed webpage of each property

# Import packages
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import argparse
        
# Main code for looping through all web pages
def web_scrape(url):
    '''this function perform the scrapping the information of all properties in rightmove.co.uk

    Arguments:
        url -- the url of searched properties

    Returns:
        the dictionary contains all properties information
    '''
    
    # Dictionary containing properties' attributes
    properties_info = {'address': [], # 
                        'price': [],
                        'type': [],
                        'no_bed': [],
                        'no_bath': [],
                        'agent': [],
                        'url': []}
    
    # Create Service Object
    edgeService = Service(r"C:\\Users\blueb\\Downloads\\edgedriver_win64\\msedgedriver.exe")

    # Create Webdriver Object
    edgeDriver = webdriver.Edge(service = edgeService)

    # Create Webdriver Object
    edgeDriver = webdriver.Edge(service = edgeService)
    
    try:
        edgeDriver.get(url)
        
        # Start looping all the web pages 
        page = 1 # current page indicator
        while True:
            print('\rScrapping the current page...')
        
            # Find all div elements with the class 'property-information'
            house = edgeDriver.find_elements(By.CLASS_NAME, 'propertyCard-wrapper') # this class contains all info of a listed house

            # Collect the attributes of every property object found
            for h in house:

                # Find URL
                id_tag = h.find_elements(By.TAG_NAME, 'a')
                id_attr = [t.get_attribute('href') for t in id_tag]
                properties_info['url'].append(id_attr[0]) # append found address into the dictionary
                
                # Find adress:
                add_class = h.find_elements(By.TAG_NAME, 'address')
                title_atr = [t.get_attribute('title') for t in add_class]
                properties_info['address'].append(title_atr[0]) # append found address into the dictionary

                # Find Price:
                price = h.find_elements(By.CLASS_NAME, 'propertyCard-priceValue')

                for pr in price:
                    properties_info['price'].append(pr.text)

                # Find Types, Number of Bedrooms and Bathrooms
                infos = h.find_elements(By.CLASS_NAME, 'property-information')
                temp_info = []
                for x in infos:
                    temp_info.append(x.text)
                    temp_info = temp_info[0].split('\n')
                    #print(temp_info)

                for i in range(len(temp_info)):

                    if not temp_info[i].isdigit():
                        properties_info['type'].append(temp_info[i])

                        if (i+1) < len(temp_info) and temp_info[i+1].isdigit():
                            properties_info['no_bed'].append(temp_info[i+1])

                            if (i+2) < len(temp_info) and temp_info[i+2].isdigit():
                                properties_info['no_bath'].append(temp_info[i+2])

                            else: 
                                properties_info['no_bath'].append('not_specified')

                        else:
                            properties_info['no_bed'].append('not_specified')
                            properties_info['no_bath'].append('not_specified')
                
                # Find Agent name:
                try:
                    logo = h.find_element(By.CLASS_NAME, 'propertyCard-branchLogo')
                    agent = logo.find_elements(By.TAG_NAME, 'a')
                    alt_attributes = [img.get_attribute('title') for img in agent]
                    properties_info['agent'].append(alt_attributes[0])
                except NoSuchElementException:
                    properties_info['agent'].append('not_specified')
            
            # Assert finishing scraping the current page
            print(f"\rComplete crapping the {page} page.")
            page += 1
                      
            # Navigate to the next page
            try:
                next_button = WebDriverWait(edgeDriver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='pagination-next']"))  # Adjust the locator as needed
                )
                next_button.click()  # Click the "Next" button
                print("Cliked Next")
                time.sleep(2)  # Pause to allow the page to load
            except (NoSuchElementException, TimeoutException):
                print("No more pages to scrape.")
                break  # Break the loop if there are no more pages

    finally:
        # Clean up and close the driver
        edgeDriver.quit()   
    
    return properties_info

def main():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="A Program scrape all properties information in rightmove.co.uk")

    # Add arguments
    parser.add_argument("--url", type=str, required=True, help="The URL of the all searched properties")
    parser.add_argument("--csv", type=str, required=True, help="Name of the export csv file")

    # Parse the arguments
    args = parser.parse_args()
    
    # Call the web-scraping function to collect the properties info to the dataframe
    df = pd.DataFrame(web_scrape(args.url))
    
    # pass to the exported csv file
    df.to_csv(rf'.\datasets\{args.csv}.csv', index=False)
    print("Completed Scraping")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")

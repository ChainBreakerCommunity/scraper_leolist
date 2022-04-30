###################################
###        LEOLIST MODULE       ###
###################################

import utils
import constants
import sys
import time
import undetected_chromedriver.v2 as uc
import copy
import logging
from client import ChainBreakerScraper
import json
import recapcha

# Configure loggin file.
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')

def enterLeolist(driver):
    with driver:
        driver.get("https://www.leolist.cc/personals/female-escorts/new-brunswick")
    print("Current URL: ", driver.current_url)
    # Enter to leolist.
    close = input("Do you have chrome://welcome/ open? Y/N ")
    if close == "Y":
        chrome_window = driver.window_handles[1]
        driver.switch_to.window(chrome_window)
        driver.close()
        leolist_window = driver.window_handles[0]
        driver.switch_to.window(leolist_window)
        time.sleep(2)
    agree_button = driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div[2]/a")
    agree_button.click()

def clickPhoneButton(driver):
    button = None
    list_a = driver.find_elements_by_class_name("contacts-view-btn")
    for b in list_a:
        if b.text.startswith("click to view") or b.text.startswith("SHOW"):
            try:
                button = copy.copy(b)
                button.click()
                break
            except: 
                pass
  
def main():

    with open("./config.json") as json_file: 
        data = json.load(json_file)

    endpoint = data["endpoint"]
    user = data["username"]
    password = data["password"]
    selenium_endpoint = data["selenium_endpoint"]   
    recaptcha_api_key = data["recaptcha_api_key"]

    logging.warning("Parameters passed to scraper: " + endpoint + ", " + user + ", " + password)
    client = ChainBreakerScraper(endpoint)
    print("Trying to login now")
    res = client.login(user, password)
    if type(res) != str:
        logging.critical("Login was not successful.")
        sys.exit()
    else: 
        logging.warning("Login was successful.")

    # Crear driver.
    print("Open Chrome")
    driver = uc.Chrome()
    with driver:
        driver.get("https://www.leolist.cc/personals/female-escorts/new-brunswick")
    logging.warning("Waiting 10 seconds before continue.")
    time.sleep(10)
    #continue_ = input("Continue: Y/N")
    #agree_button = driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div[2]/a")
    logging.warning("Searching accept button...")
    try:
        agree_button = driver.find_elements_by_class_name("announcementClose")
        print(agree_button)
        agree_button[0].click()
    except: 
        logging.warning("Selenium didnt pass cloudflare test. Retry process.")
        driver.quit()
        time.sleep(10)
        return main()

    time.sleep(3)

    count_announcement = 1
    count_category = 0

    for category in constants.CATEGORIES:
        for region in constants.regions:

            # Directory list.
            url_category = constants.SITE + category + "/" + region
            print("URL CATEGORY: ", url_category)
            with driver: 
                driver.get(url_category)
            print("Loading list page...")
            time.sleep(3)

            # Page lists.
            for page in range(1, constants.MAX_PAGES_PER_CATEGORY + 1):
                logging.warning("# Page: " + str(page))
                
                if page > 1:
                    # Change pagination.
                    divs_pagination = driver.find_elements_by_class_name("pagination-link")
                    if len(divs_pagination) > 0:
                        for pagination in divs_pagination: 
                            if pagination.get_attribute("aria-label") == "Next page":
                                pagination.click()
                                print("Change pagination...")
                                time.sleep(4)
                    else: 
                        continue
                    
                # Get list url.
                menu_url = driver.current_url
                list_urls = utils.get_ads_links(driver)

                for url in list_urls:

                    if client.get_status() != 200:
                        logging.error("Endpoint is offline. Service stopped.", exc_info = True)
                        driver.quit()
                        sys.exit()

                    page_link = constants.SITE + url
                    info_ad = constants.SITE_NAME + ", category: " + constants.CATEGORIES[count_category] + ", #ad " + str(count_announcement) + ", page_link " + page_link

                    if client.does_ad_exist(utils.getId(url), constants.SITE_NAME, constants.COUNTRY):
                        logging.warning("Ad already in database. Link: " + url)
                        continue
                    else:
                        logging.warning("New Ad. " + info_ad)

                    #print("Website: ", constants.site_name)
                    #print("Region: ", region)
                    #print("Category: ", category)
                    #print("Page: ", page)
                    #print("Scrapping ad # ", str(count_ads + 1))
                    #print("Link: ", ad_link)

                    with driver:
                        driver.get(url)

                    time.sleep(4)
                    #clickPhoneButton(driver)
                    #time.sleep(5)
                    data = recapcha.solveGeetestV4(url)
                    recapcha.submitGeetestV4(driver, data)
            
                    # Add ad information.
                    time.sleep(2)
                    ad_record = utils.scrap_ad_link(client, driver, url, category, region)
                    count_announcement += 1
            
                # Return the menu.
                driver.get(menu_url)
                time.sleep(4)
         
if __name__ == "__main__":
    main()

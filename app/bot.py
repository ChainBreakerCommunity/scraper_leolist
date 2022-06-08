###################################
###        LEOLIST MODULE       ###
###################################

import utils
import constants
import sys
import time
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
import copy
import logging
from chainbreaker_api import ChainBreakerScraper
import json
import recaptcha
import numpy as np
import warnings
from pyvirtualdisplay import display
warnings.filterwarnings("ignore")

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

def getDriver():
    driver = uc.Chrome()
    return driver 

    with open("./config.json") as json_file: 
        data = json.load(json_file)
    #import os
    options = webdriver.ChromeOptions()
    #chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    #chrome_options.add_argument("--headless")
    #chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    #chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--no-sandbox')
    options.add_argument('start-maximized')
    options.add_argument('enable-automation')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    driver = webdriver.Remote(data["selenium_endpoint"], desired_capabilities = DesiredCapabilities.CHROME)
    #driver = webdriver.Chrome(executable_path="./chromedriver.exe", chrome_options=chrome_options)
    return driver

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

def open_leolist(driver):
    #with driver:
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

def main():
    with open("./config.json") as json_file: 
        data = json.load(json_file)

    endpoint = data["endpoint"]
    user = data["username"]
    password = data["password"]
    
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
    driver = uc.Chrome()#getDriver()
    open_leolist(driver)

    time.sleep(3)

    count_announcement = 1
    count_category = 0

    for category in constants.CATEGORIES:
        for region in constants.regions:

            # Directory list.
            url_category = constants.SITE + category + "/" + region
            print("URL CATEGORY: ", url_category)
            #with driver: 
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
                    try:
                        driver.get(url)
                    except: 
                        driver.close()
                        driver = driver = uc.Chrome()#getDriver()
                        open_leolist(driver)
                        time.sleep(2)
                        driver.get(url)

                    logging.warning("Ad correctly loaded.")

                    time.sleep(4)
                    #clickPhoneButton(driver)
                    #time.sleep(5)
                    template_list = np.load('templates.npy')
                    res = recaptcha.captcha_solver(driver, template_list = template_list)
                    if res == True:     
                        # Add ad information.
                        time.sleep(2)
                        ad_record = utils.scrap_ad_link(client, driver, url, category, region)
                        count_announcement += 1
                    else: 
                        logging.warning("Skipping this ad because of recaptcha error")
      

                # Return the menu.
                driver.get(menu_url)
                time.sleep(4)
         
if __name__ == "__main__":
    main()

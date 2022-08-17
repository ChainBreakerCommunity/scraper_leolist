import bot.scrape
import bot.constants
import sys
import time
import copy
import datetime
import json
import bot.recaptcha
import numpy as np

import undetected_chromedriver.v2 as uc
from selenium import webdriver
from chainbreaker_api import ChainBreakerScraper
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By

import warnings
warnings.filterwarnings("ignore")

from utils.env import get_config
config = get_config()

from logger.logger import get_logger
logger = get_logger(__name__, level = "DEBUG", stream = True)

def enterLeolist(driver):
    with driver:
        driver.get(bot.constants.BASE_URL)
    logger.info("Current URL: ", driver.current_url)
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

    list_a = driver.find_elements(By.CLASS_NAME, "contacts-view-btn")
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
    driver.get(bot.constants.BASE_URL)
    logger.warning("Waiting 10 seconds before continue.")
    time.sleep(10)
    #continue_ = input("Continue: Y/N")
    #agree_button = driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div[2]/a")
    logger.warning("Searching accept button...")
    try:
        agree_button = driver.find_element(By.CLASS_NAME, "announcementClose")
        agree_button.click()
    except Exception as e: 
        logger.exception(str(e))
        driver.quit()
        time.sleep(10)
        return execute_scraper()

def execute_scraper():

    start_time = datetime.datetime.now()

    endpoint = config["ENDPOINT"]
    user = config["USERNAME"]
    password = config["PASSWORD"]
    
    logger.warning("Parameters passed to scraper: " + endpoint + ", " + user + ", " + password)
    client = ChainBreakerScraper(endpoint)
    logger.info("Trying to login now")
    res = client.login(user, password)
    if type(res) != str:
        logger.critical("Login was not successful.")
        sys.exit()
    else: 
        logger.warning("Login was successful.")

    # Crear driver.
    logger.info("Open Chrome")
    driver = uc.Chrome()#getDriver()
    open_leolist(driver)

    time.sleep(3)

    count_announcement = 1
    count_category = 0

    for category in bot.constants.CATEGORIES:
        for region in bot.constants.regions:

            current_time = datetime.datetime.now()
            delta = current_time - current_time
            sec = delta.total_seconds()
            mins = sec / 60
            if mins >= 60:
                sys.exit()

            # Directory list.
            url_category = bot.constants.SITE + category + "/" + str(region)
            logger.info("URL CATEGORY: " + url_category)
            #with driver: 
            driver.get(url_category)
            logger.info("Loading list page...")
            time.sleep(3)

            # Page lists.
            for page in range(1, bot.constants.MAX_PAGES_PER_CATEGORY + 1):
                logger.warning("# Page: " + str(page))
                
                if page > 1:
                    # Change pagination.
                    divs_pagination = driver.find_elements(By.CLASS_NAME, "pagination-link")
                    if len(divs_pagination) > 0:
                        for pagination in divs_pagination: 
                            if pagination.get_attribute("aria-label") == "Next page":
                                pagination.click()
                                logger.info("Change pagination...")
                                time.sleep(4)
                    else: 
                        continue
                    
                # Get list url.
                menu_url = driver.current_url
                list_urls = bot.scrape.get_ads_links(driver)

                for url in list_urls:

                    if client.get_status() != 200:
                        logger.error("Endpoint is offline. Service stopped.", exc_info = True)
                        driver.quit()
                        sys.exit()

                    page_link = bot.constants.SITE + url
                    info_ad = bot.constants.SITE_NAME + ", category: " + bot.constants.CATEGORIES[count_category] + ", #ad " + str(count_announcement) + ", page_link " + page_link

                    if client.does_ad_exist(bot.scrape.getId(url), bot.constants.SITE_NAME, bot.constants.COUNTRY):
                        logger.warning("Ad already in database. Link: " + url)
                        continue
                    else:
                        logger.warning("New Ad. " + info_ad)

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

                    logger.warning("Ad correctly loaded.")

                    time.sleep(4)
                    #clickPhoneButton(driver)
                    #time.sleep(5)
                    template_list = np.load('./bot/templates.npy')
                    res = bot.recaptcha.captcha_solver(driver, template_list = template_list)
                    if res == True:     
                        # Add ad information.
                        time.sleep(2)
                        ad_record = bot.scrape.scrap_ad_link(client, driver, url, category, region)
                        count_announcement += 1
                    else: 
                        logger.warning("Skipping this ad because of recaptcha error")
      

                # Return the menu.
                driver.get(menu_url)
                time.sleep(4)
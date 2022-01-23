###################################
###        LEOLIST MODULE       ###
###################################

#from aux_functions import does_ad_exist
from utils import scrap_ad_link
import utils
from utils import get_ads_links, getImageURLS, getId
import constants
import os 
import sys
import bs4 as bs
import time
import undetected_chromedriver.v2 as uc
import copy
import logging
from client import ChainBreakerScraper
import json

# Configure loggin file.
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')

# Selenium Libraries.
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Recaptcha libraries
import speech_recognition as sr
import urllib
import pydub

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
    return solveRecaptcha(driver)

def solveRecaptcha(driver):
    try:
        WebDriverWait(driver, 10, ignored_exceptions = NoSuchElementException).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='recaptcha challenge']")))
        recaptcha_audio_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#recaptcha-audio-button")))
        recaptcha_audio_button.click()
        time.sleep(2)
        play_button = driver.find_element_by_class_name("rc-audiochallenge-play-button").find_element_by_class_name("rc-button-default")
        play_button.click()
        src = driver.find_element_by_id("audio-source").get_attribute("src")
        print("[INFO] Audio src: %s"%src)
        urllib.request.urlretrieve(src, os.path.normpath(os.getcwd()+"\\sample.mp3"))
        time.sleep(3)
        
        #load downloaded mp3 audio file as .wav
        try:
            sound = pydub.AudioSegment.from_mp3(os.path.normpath(os.getcwd()+"\\sample.mp3"))
            sound.export(os.path.normpath(os.getcwd()+"\\sample.wav"), format="wav")
            sample_audio = sr.AudioFile(os.path.normpath(os.getcwd()+"\\sample.wav"))
        except:
            print("[-] Please run program as administrator or download ffmpeg manually, http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/")
            
        #translate audio to text with google voice recognition
        r = sr.Recognizer()
        with sample_audio as source:
            audio = r.record(source)
        key = r.recognize_google(audio)
        print("[INFO] Recaptcha Passcode: %s"%key)
        
        #key in results and submit
        driver.find_element_by_id("audio-response").send_keys(key.lower())
        verify_button = driver.find_element_by_id("recaptcha-verify-button")
        verify_button.click()
        time.sleep(5)

        # check if recaptcha window dissapired.
        print("Recaptcha error message: ", driver.find_element_by_class_name("rc-audiochallenge-error-message").get_attribute("style"))
        success = (driver.find_element_by_class_name("rc-audiochallenge-error-message").get_attribute("style") == "display: none;")
        driver.switch_to.default_content()
        time.sleep(2)
        if not success: 
            print("Recaptcha error")
        return success
    except: 
        problem_recaptcha = False
        list_a = driver.find_elements_by_class_name("contacts-view-btn")
        for b in list_a:
            if b.text.startswith("click to view") or b.text.startswith("SHOW") or b.text.startswith("Loading"):
                problem_recaptcha = True
                break
        driver.switch_to.default_content()
        if not problem_recaptcha:
            print("No recaptcha.")
            return True
        else:
            print("Recaptcha couldnt be reached.")
            return False
    
def main():

    with open("./config.json") as json_file: 
        data = json.load(json_file)

    endpoint = data["endpoint"]
    user = data["username"]
    password = data["password"]
    selenium_endpoint = data["selenium_endpoint"]   

    logging.warning("Parameters passed to scraper: " + endpoint + ", " + user + ", " + password)
    client = ChainBreakerScraper(endpoint)
    res = client.login(user, password)
    if type(res) != str:
        logging.critical("Login was not successful.")
        sys.exit()
    else: 
        logging.warning("Login was successful.")

    # Crear driver.
    driver = uc.Chrome()
    with driver:
        driver.get("https://www.leolist.cc/personals/female-escorts/new-brunswick")
    time.sleep(10)
    #agree_button = driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div[2]/a")
    #agree_button = driver.find_elements_by_class_name("announcementClose")
    #print(agree_button)
    #agree_button.click()
    #time.sleep(2)

    count_announcement = 1
    count_category = 0

    for category in constants.CATEGORIES:
        for region in constants.regions:

            # Directory list.
            url_category = constants.SITE + category + "/" + region
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

                    if client.does_ad_exist(utils.get_id_from_url(url), constants.SITE_NAME, constants.COUNTRY):
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
                    success_click = clickPhoneButton(driver)

                    if success_click:
                        # Add ad information.
                        time.sleep(2)
                        ad_record = utils.scrap_ad_link(client, driver, url, category, region)
                        count_announcement += 1
                    else: 
                        print("We will skip this ad...")
            
                # Return the menu.
                driver.get(menu_url)
                time.sleep(4)
         
if __name__ == "__main__":
    main()

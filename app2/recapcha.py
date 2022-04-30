
# Selenium Libraries.
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver.v2 as uc
import time
import os
import json
import urllib
import pydub
import requests
import speech_recognition as sr
import logging
import sys

with open("./config.json") as json_file: 
    data = json.load(json_file)
API_KEY = data["recaptcha_api_key"]
GEETEST_ID = data["leolist_geetest_id"]
MAX_TRIES = 5

def solveGeetestV4(pageurl:str) -> dict:
    route = "http://2captcha.com/in.php?key={api_key}&method=geetest_v4&captcha_id={captcha_id}&&pageurl={pageurl}" \
            .format(api_key = API_KEY, captcha_id = GEETEST_ID, pageurl = pageurl)
    logging.warning("Post request: ", route)
    result = requests.post(route)
    req_id = result.text[3:]
    route = "http://2captcha.com/res.php?key={api_key}&action=get&id={req_id}" \
            .format(api_key = API_KEY, req_id = req_id)
    
    # Wait 20 seconds for 2recaptcha response.
    time.sleep(20)
    logging.warning("Get request: ", route)
    response = requests.get(route)
    tries = 0
    
    # Recaptcha is not ready, repeat request every 5 seconds until MAX_TRIES
    while response.text == "CAPCHA_NOT_READY":
        time.sleep(5)
        while tries > MAX_TRIES:
            logging.error("Recaptcha max tries exceeded.")
            sys.exit()
        tries = tries + 1
        response = requests.get(route)

    string = response.text[3:]
    data = json.loads(string)
    return data

def submitGeetestV4(driver: uc.Chrome, data: dict) -> None:
    #page_source = driver.page_source
    #os.system("echo {string} > source.html".format(string = page_source))

    #inputHidden(driver, "captcha_id", data["captcha_id"])
    inputHidden(driver, "gee_test_lot_number", data["lot_number"])
    inputHidden(driver, "gee_test_pass_token", data["pass_token"])
    inputHidden(driver, "gee_test_gen_time", data["gen_time"])
    inputHidden(driver, "gee_test_captcha_output", data["captcha_output"])
    driver.execute_script("return document.getElementById('registersubmit').click()")
    #form_submit = driver.find_element_by_id("registersubmit")
    #form_submit.click()
    #driver.switch_to_default_content()
    #@browser.execute_script("return document.getElementById('hiddinthing').value = 'foo';")

def inputHidden(driver, field, value):
    driver.execute_script("return document.getElementById('{field}').value = '{value}'".format(field = field, value = value))

def solveRecaptcha(driver):

    def googleRecaptcha(driver):
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

    def geetestRecaptcha(driver):
        with open("./config.json") as json_file: 
            data = json.load(json_file)
        recaptcha2_key = data["recaptcha2_key"]
    
        # Add these values
        API_KEY = recaptcha2_key  # Your 2captcha API KEY
        site_key = ''  # site-key, read the 2captcha docs on how to get this
        url = 'http://somewebsite.com'  # example url
        proxy = None #'127.0.0.1:6969'  # example proxy

        #proxy = {'http': 'http://' + proxy, 'https': 'https://' + proxy}

        s = requests.Session()

        # here we post site key to 2captcha to get captcha ID (and we parse it here too)
        captcha_id = s.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key, url), proxies=proxy).text.split('|')[1]
        # then we parse gresponse from 2captcha response
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id), proxies=proxy).text
        print("solving ref captcha...")
        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            time.sleep(5)
            recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id), proxies=proxy).text
        recaptcha_answer = recaptcha_answer.split('|')[1]

        # we make the payload for the post data here, use something like mitmproxy or fiddler to see what is needed
        payload = {
            'key': 'value',
            'gresponse': recaptcha_answer  # This is the response from 2captcha, which is needed for the post request to go through.
        }

        # then send the post request to the url
        response = s.post(url, payload, proxies=proxy)        
  
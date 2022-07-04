
"""
Leolist Captcha solving, web-scraping script
@author: Elsa Riachi, s5941336
@date: April 08 2022
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import cv2 as cv
import numpy as np
from scipy import ndimage, signal
import copy

from logger.logger import get_logger
logger = get_logger(__name__, level = "DEBUG", stream = True)


""" Captcha solving functions """
def normalize(x):
    return x / np.linalg.norm(x)

def find_peak(scores):
    change = np.sign(scores[1:] - scores[:-1])
    filter = [1, 1, 1, -1, -1, -1]

    corr = np.correlate(change, filter)
    peak_loc_list = np.argwhere(corr == 6).squeeze() + 3
    if peak_loc_list.size > 1:
        # start with 1 to avoid source piece
        s = scores[peak_loc_list[1:]]
        peak_idx = np.argmax(s)
        return peak_loc_list[peak_idx + 1]
    else:
        s = scores[peak_loc_list]
        peak_idx = np.argmax(s)
        return peak_loc_list

def get_edges(img):
    #img = cv.GaussianBlur(img, ksize=(5, 5), sigmaX=1, sigmaY=1)

    #  edge detection
    edges = cv.Canny(img, 150, 200)
    # cv.imshow('Edges', edges)
    # cv.waitKey(0)

    edges = cv.dilate(edges, None)
    # cv.imshow('Dilated Edges', edges)
    # cv.waitKey(0)

    return edges

def similarity(template, segment):
    dot = np.sum(segment * template)
    return dot

def crop_and_slide(img, src_loc, template):
    dot_values = []
    loc_values = []
    stride = 2
    buffer = template.shape[0]
    min_y = max(0, src_loc[0] - buffer // 2)
    max_y = min(img.shape[0], src_loc[0] + buffer // 2)
    search_area = img[min_y:max_y, :]

    for x in range(0, img.shape[1], stride):
        if x + buffer < img.shape[1]:
            segment = normalize(search_area[:, x:x + buffer])
            dot = np.sum(segment * template)
            dot_values.append(dot)
            loc_values.append(x + buffer // 2)

    peak_loc = find_peak(np.array(dot_values))
    dst_loc = loc_values[peak_loc]
    return dst_loc

def get_offset(og_img, shifted_img, template_list):
    img = cv.cvtColor(og_img, cv.COLOR_BGR2HSV)[:, :, 2]
    shifted_img = cv.cvtColor(shifted_img, cv.COLOR_BGR2HSV)[:, :, 2]

    diff = shifted_img - img
    diff = cv.GaussianBlur(diff, ksize=(7, 7), sigmaX=3, sigmaY=1)
    diff = cv.GaussianBlur(diff, ksize=(7, 7), sigmaX=3, sigmaY=1)

    edges = get_edges(diff)

    best_template, best_location = get_template_match(edges, template_list)

    # crop and slide
    edges = get_edges(og_img)
    dst_loc = crop_and_slide(edges, best_location, best_template)
    # dst_loc = fast_crop_and_slide(edges, best_location, best_template)

    # best location could be the moved puzzle piece or the source position
    if best_location[1] > 80:
        offset = dst_loc - best_location[1]
    else:
        offset = dst_loc - best_location[1] - 120

    # cv.circle(og_img, (dst_loc, best_location[0]), 6, (0, 255, 255), -1)

    return offset, dst_loc, og_img

def get_template_match(edges, template_list):

    activation_map = signal.oaconvolve(np.tile(edges[None, :], (template_list.shape[0], 1, 1)),
                                        template_list, mode='same', axes=(1, 2))

    max_sim_idx = np.unravel_index(np.argmax(activation_map), activation_map.shape)
    max_sim_template = max_sim_idx[0]
    max_location = max_sim_idx[1:]

    # what we want is correlation, so we should 'flip' the filter.
    return ndimage.rotate(template_list[max_sim_template].squeeze(), 180), max_location

def clickPhoneButton(driver):
    button = None
    list_a = driver.find_elements(By.CLASS_NAME, "contacts-view-btn")
    for b in list_a:
        if b.text.startswith("click to view") or b.text.startswith("SHOW"):
            try:
                button = copy.copy(b)
                button.click()
                return True
            except: 
                pass
    return False

def captcha_solver(driver, template_list):
    max_tries = 5

    res = clickPhoneButton(driver)
    if res == False: 
        return False
    time.sleep(1)

    start = False
    while not start:
        try:
            slider_window = driver.find_element(by=By.CLASS_NAME, value="geetest_window")
            if slider_window.size['height'] == 0:
                continue
            else:
                start = True
        except:
            continue
        start = True

    for tr in range(max_tries):
        tr += 1
        time.sleep(1.5)
        slider_window = driver.find_element(by=By.CLASS_NAME, value="geetest_window")
        slider_btn = driver.find_element(by=By.CLASS_NAME, value="geetest_btn")
        slider_window.screenshot(f"ss.png")
        img = cv.imread("ss.png")

        # move halfway to get diff
        stride = 120
        action = webdriver.ActionChains(driver)
        action.move_to_element(slider_btn)
        action.click_and_hold()
        action.move_by_offset(stride, 0)
        action.perform()

        time.sleep(0.5)
        slider_window = driver.find_element(by=By.CLASS_NAME, value="geetest_window")
        slider_window.screenshot(f"ss_{stride}.png")

        shifted_img = cv.imread(f'ss_{stride}.png')

        try:
            offset, dst_loc, og_img = get_offset(img, shifted_img, template_list)
            action.move_to_element(slider_btn)
            action.click_and_hold()
            action.move_by_offset(offset, 0)

            action.release()
            action.perform()
            time.sleep(6)

        except:
            print(f"Something went wrong, trying again for try {tr + 1}")

        try:
            # check for geetest window again, supposed to fail if captcha solved
            slider_window = driver.find_element(by=By.CLASS_NAME, value="geetest_window")
            if slider_window.size['height'] == 0:
                logger.info('Success!')
                return True
        except Exception:
            logger.info("Success!")
            return True

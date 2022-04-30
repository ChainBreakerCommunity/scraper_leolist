import constants
import time
import bs4 as bs
import re
import datetime
from dateutil.parser import parse
from client import ChainBreakerScraper
import logging
from typing import List 

def clean_string(string, no_space = False):   
    """
    Clean String.
    """
    if no_space:
        string = string.replace("  ","")
    string = string.strip()
    string = string.lower()
    string = string.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    string = string.replace("\n"," ")
    return string

def get_ads_links(driver):
    divs = driver.find_elements_by_class_name("group")
    post_links = list()
    
    for post in divs: 
        
        a_tag_post = post.find_elements_by_tag_name("a")
        
        for element in a_tag_post: 
            if a_tag_post.index(element) == 0:
                link = element.get_attribute("href")
                post_id = element.get_attribute("name").replace("ad", "")
                post_links.append(link)
                #print(post_id)
                #if not general_functions.does_ad_exist(post_id):
                #    post_links.append(link)
                
    return post_links

def getId(url):
    #print(url)
    m = re.findall(r'\d+', url)
    return m[-1]

def getTitle(soup: bs.BeautifulSoup):
    return soup.find_all("h1", {"class":"head__title", "itemprop":"name"})[0].get_text()

def getSubtitle(soup: bs.BeautifulSoup):
    return soup.find_all("span", {"class": "text"})[0].get_text()

def getCity(soup: bs.BeautifulSoup):
    info = soup.find_all("div", {"class":"info"})[0]
    city = info \
      .find_all("div", {"id":"preview-city"})[0] \
      .find_all("span", {"itemprop":"addressLocality"})[0] \
      .get_text()
    return city

def getRegion(region):
    return region

def getText(soup: bs.BeautifulSoup) -> str:
    text = soup \
      .find_all("div", {"itemprop":"description"})[0] \
      .find_all("div", {"class":"ad-description-container"})[0].get_text()
    text = clean_string(text)
    return text

def getCategory(category: str) -> str:
    return category

def getName(soup: bs.BeautifulSoup) -> str:
    name = soup.find_all("div", {"id":"preview-name"})[0].get_text()
    return name

def getAge(soup: bs.BeautifulSoup) -> str:
    age = soup.find_all("div", {"id":"preview-age"})[0].get_text()
    return age

def getEthnicity(soup: bs.BeautifulSoup) -> str:
    ethnicity = soup.find_all("div", {"id":"preview-ethnicity"})[0].get_text()
    ethnicity = clean_string(ethnicity)
    return ethnicity
#
def getAvailability(soup: bs.BeautifulSoup) -> str:
    text = soup.find_all("div", {"id":"preview-availability"})[0].get_text()
    text = clean_string(text)
    return text

def getHeight(soup: bs.BeautifulSoup) -> str:
    text = soup.find_all("div", {"id":"preview-height"})[0].get_text()
    text = clean_string(text)
    return text

def getWeight(soup: bs.BeautifulSoup) -> str:
    text = soup.find_all("div", {"id":"preview-weight"})[0].get_text()
    text = clean_string(text)
    return text

def getStats(soup: bs.BeautifulSoup) -> str:
    text = soup.find_all("div", {"id":"preview-stats"})[0].get_text()
    text = clean_string(text)
    return text

def getHair(soup: bs.BeautifulSoup) -> str:
    text = soup.find_all("div", {"id":"preview-hair"})[0].get_text()
    text = clean_string(text)
    return text

def getEye(soup: bs.BeautifulSoup) -> str:
    text = soup.find_all("div", {"id":"preview-eye"})[0].get_text()
    text = clean_string(text)
    return text
#
def getPrice(soup: bs.BeautifulSoup) -> str:
    price = soup.find_all("span", {"id":"preview-price"})[0].get_text()
    return price

def getGPS(soup: bs.BeautifulSoup):
    latitude = ""
    longitude = ""
    geo = soup.find_all("div", {"itemprop":"geo"})
    if len(geo) > 0:
        latitude = geo[0].find_all("meta", {"itemprop":"latitude"})[0]["content"]
        longitude = geo[0].find_all("meta", {"itemprop":"longitude"})[0]["content"]
    return latitude, longitude

def getPostDate(subtitle: str):
        
    if subtitle.startswith("Posted Today, "):
        split = subtitle.split(" — ")
        postedToday = split[0][len("Posted Today, "):]
        return parse(postedToday)

    elif subtitle.startswith("Posted Yesterday, "):
        split = subtitle.split(" — ")
        postedYesterday = parse(split[0][len("Posted Yesterday, "):])
        newdate = postedYesterday.replace(day = postedYesterday.day - 1)
        return newdate

    elif subtitle.startswith("Posted on "):
        split = subtitle.split(" — ")
        postedOn = split[0][len("Posted on "):]
        return parse(postedOn)

def numViews(subtitle: str) -> str:
    split = subtitle.split(" — ")
    if split[1].startswith("Viewed "):
        numViews = split[1][len("Viewed "):-1*len(" times")]
    return numViews

def getCellphone(soup: bs.BeautifulSoup) -> str:
    href = ""
    try:
        href = soup.find_all("a", {"class":"phone"})[0]["href"]
    except:
        pass
    if href == "":
        return ""
    else:
        return href.replace("tel:","")

def getEmail(soup: bs.BeautifulSoup) -> str:
    href = ""
    try:
        href = soup.find_all("a", {"itemprop":"email"})[0]["href"]
    except: 
        pass
    if href == "":
        return ""
    else:
        return href.replace("mailto:","")

def getWhatsAppContact(soup: bs.BeautifulSoup) -> str:
    href = ""
    try:
        href = soup.find_all("a", {"itemprop":"whatsapp"})[0]["href"]
    except:
        href = ""
    m = re.findall(r'\d+', href)
    return m[0]

def getDateScrap() -> datetime.datetime:
    return datetime.datetime.now()

def isVerified(soup: bs.BeautifulSoup) -> str:
    try:
        text = soup.find_all("div", {"class":"alert-verified"})[0].get_text()
        return "1"
    except:
        return "0"

def isGold(soup: bs.BeautifulSoup) -> str:
    try:
        soup.find_all("div", {"class":"gold-label"})[0].get_text()
        return "1"
    except:
        return "0"

def getReviewsLink(soup: bs.BeautifulSoup):
    try:
        link = soup.find_all("a", {"id":"lyla-button"})[0]["href"]
        if link == "https://www.lyla.ch/": 
            return (False, "")
        else: 
            return (True, link)
    except:
        return (False, "")

def getExternalWebsite(soup: bs.BeautifulSoup) -> str:
    div = soup.find_all("div", {"class":"website"})[0]
    href = div.find("a")["href"]
    href = "" if href == "#" else href
    return href

def getImageURLS(driver) -> List[str]:
    image_list = list()
    
    try:
        verified_images = driver.find_element_by_class_name("account-photos--verified")
        for image in verified_images.find_elements_by_tag_name("img"): 
            image_list.append((image.get_attribute("src"), 1))
    except: 
        pass
    
    try:
        not_verified_images = driver.find_element_by_class_name("account-photos--images")
        for image in not_verified_images.find_elements_by_tag_name("img"): 
            image_list.append((image.get_attribute("src"), 0))
    except: 
        pass
    return image_list

def hasCellphoneIcon(driver) -> int:
    address = driver.find_element_by_class_name("address")
    explore = address.find_elements_by_tag_name("i")
    for res in explore:
        if res.get_attribute("class") == "icon-phone-o mr":
            if res.value_of_css_property("display") == "block":
                return 1
    return 0

def scrap_ad_link(client: ChainBreakerScraper, driver, link:str, category:str, region:str):
    
    # Get soup object.
    soup = bs.BeautifulSoup(driver.page_source, "html")

    # Get phone or whatsapp
    phone = getCellphone(soup)
    if phone == None:
        whatsapp = getWhatsAppContact(soup)
        if whatsapp != None:
            phone = whatsapp
        else:
            print("Phone not found! We will skip this ad.")
            #return None

    author = constants.AUTHOR
    language = constants.LANGUAGE
    link = link
    id_page = getId(link)
    title = getTitle(soup)
    text = getText(soup)
    category = category
    subtitle = getSubtitle(soup)
    first_post_date = getPostDate(subtitle)
    date_scrap = getDateScrap()
    website = constants.SITE_NAME

    email = getEmail(soup)
    verified_ad = isVerified(soup)
    prepayment = ""
    promoted_ad = isGold(soup)
    external_website = getExternalWebsite(soup)
    reviews_website = getReviewsLink(soup)[1]
    country = "canada" 
    region = region
    city = getCity(soup)
    place = ""

    comments = []
    latitude, longitude = getGPS(soup)
    nationality = getEthnicity(soup)
    age = getAge(soup)

    # Upload ad in database.
    status_code = client.insert_ad(author, language, link, id_page, title, text, category, first_post_date, date_scrap, website, phone, country, region, city, place, email, verified_ad, prepayment, promoted_ad, external_website,
            reviews_website, comments, latitude, longitude, nationality, age) # Eliminar luego
    print(status_code)
    if status_code != 200: 
        print("Algo salió mal...")
    else: 
        print("Éxito!")
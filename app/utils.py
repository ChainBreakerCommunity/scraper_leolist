import constants
import time
import bs4 as bs
import re
import datetime
from dateutil.parser import parse
from client import ChainBreakerScraper

def clean_string(string, no_space = False):   
    """
    Clean String.
    """
    if no_space:
        string = string.replace("  ","")
        string = string.replace("\n"," ")
    string = string.strip()
    string = string.lower()
    string = string.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
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

def getTitle(soup):
    return soup.find_all("h1", {"class":"head__title", "itemprop":"name"})[0].get_text()

def getSubtitle(soup):
    return soup.find_all("span", {"class": "text"})[0].get_text()

def getCity(soup):
    info = soup.find_all("div", {"class":"info"})[0]
    city = info \
      .find_all("div", {"id":"preview-city"})[0] \
      .find_all("span", {"itemprop":"addressLocality"})[0] \
      .get_text()
    if city == "":
        return None
    else:
        return city

def getRegion(region):
    return region

def getText(soup):
    text = soup \
      .find_all("div", {"itemprop":"description"})[0] \
      .find_all("div", {"class":"ad-description-container"})[0].get_text()
    text = clean_string(text)
    #text = text_format.process_text_pipeline(text)
    if text == "":
        return None
    else:
        return text

def getCategory(category):
    if category == "":
        return None
    else:
        return category

def getName(soup):
    name = soup.find_all("div", {"id":"preview-name"})[0].get_text()
    if name == "":
        return None
    else:
        return name

def getAge(soup):
    age = soup.find_all("div", {"id":"preview-age"})[0].get_text()
    if age == "":
        return None
    else:
        return age

def getEthnicity(soup):
    ethnicity = soup.find_all("div", {"id":"preview-ethnicity"})[0].get_text()
    ethnicity = clean_string(ethnicity)
    if ethnicity == "":
        return None
    else:
        return ethnicity
#
def getAvailability(soup):
    text = soup.find_all("div", {"id":"preview-availability"})[0].get_text()
    text = clean_string(text)
    if text == "":
        return None
    else:
        return text

def getHeight(soup):
    text = soup.find_all("div", {"id":"preview-height"})[0].get_text()
    text = clean_string(text)
    if text == "":
        return None
    else:
        return text

def getWeight(soup):
    text = soup.find_all("div", {"id":"preview-weight"})[0].get_text()
    text = clean_string(text)
    if text == "":
        return None
    else:
        return text

def getStats(soup):
    text = soup.find_all("div", {"id":"preview-stats"})[0].get_text()
    text = clean_string(text)
    if text == "":
        return None
    else:
        return text
    return text

def getHair(soup):
    text = soup.find_all("div", {"id":"preview-hair"})[0].get_text()
    text = clean_string(text)
    if text == "":
        return None
    else:
        return text

def getEye(soup):
    text = soup.find_all("div", {"id":"preview-eye"})[0].get_text()
    text = clean_string(text)
    if text == "":
        return None
    else:
        return text
#
def getPrice(soup):
    price = soup.find_all("span", {"id":"preview-price"})[0].get_text()
    if price == "":
        return None
    else:
        return price

def getGPS(soup):
    latitude = None
    longitude = None
    geo = soup.find_all("div", {"itemprop":"geo"})
    if len(geo) > 0:
        latitude = geo[0].find_all("meta", {"itemprop":"latitude"})[0]["content"]
        longitude = geo[0].find_all("meta", {"itemprop":"longitude"})[0]["content"]
    return latitude, longitude

def getPostDate(subtitle):
        
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

def numViews(subtitle):
    split = subtitle.split(" — ")
    if split[1].startswith("Viewed "):
        numViews = split[1][len("Viewed "):-1*len(" times")]
    if numViews == "":
        return None
    else:
        return numViews

def getCellphone(soup):
    href = soup.find_all("a", {"class":"phone"})[0]["href"]
    if href == "":
        return None
    else:
        return href.replace("tel:","")

def getEmail(soup):
    href = soup.find_all("a", {"itemprop":"email"})[0]["href"]
    if href == "":
        return None
    else:
        return href.replace("mailto:","")

def getWhatsAppContact(soup):
    href = soup.find_all("a", {"itemprop":"whatsapp"})[0]["href"]
    m = re.findall(r'\d+', href)
    if m[0] == "":
        return None
    else:
        return m[0]

def getDateScrap():
    return datetime.datetime.now()

def isVerified(soup):
    try:
        text = soup.find_all("div", {"class":"alert-verified"})[0].get_text()
        return True
    except:
        return False

def isGold(soup):
    try:
        soup.find_all("div", {"class":"gold-label"})[0].get_text()
        return True
    except:
        return False

def getReviewsLink(soup):
    try:
        link = soup.find_all("a", {"id":"lyla-button"})[0]["href"]
        if link == "https://www.lyla.ch/": 
            return False, None
        else: 
            return True, link
    except:
        return None

def getExternalWebsite(soup):
    div = soup.find_all("div", {"class":"website"})[0]
    href = div.find("a")["href"]
    return href

def getImageURLS(driver):
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

def hasCellphoneIcon(driver):
    address = driver.find_element_by_class_name("address")
    explore = address.find_elements_by_tag_name("i")
    for res in explore:
        if res.get_attribute("class") == "icon-phone-o mr":
            if res.value_of_css_property("display") == "block":
                return 1
    return 0

def scrap_ad_link(client: ChainBreakerScraper, driver, link, category, region):
    
    soup = bs.BeautifulSoup(driver.page_source, "html")
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
    
    whatsapp = getWhatsAppContact(soup)
    email = getEmail(soup)

    verified_ad = isVerified(soup)
    prepayment = None
    promoted_ad = isGold(soup)
    external_website = getExternalWebsite(soup)
    reviews_website = getReviewsLink(soup)
    country = "canada" 
    region = region
    city = getCity(soup)
    place = None
    phone = getCellphone(soup)
    comments = []
    latitude, longitude = getGPS(soup)
    nationality = getEthnicity(soup)
    age = getAge(soup)

    if phone != "":
        status_code = client.insert_ad(author, language, link, id_page, title, text, category, first_post_date, date_scrap, website, phone, country, region, city, place, email, verified_ad, prepayment, promoted_ad, external_website,
                reviews_website, comments, latitude, longitude, nationality, age) # Eliminar luego
        print(status_code)
    
        if status_code != 200: 
            print("Algo salió mal...")
        else: 
            print("Éxito!")
    else: 
        print("Phone not found! We will skip this ad.")
# Sitio, urls, categorías y variables.
AUTHOR = "chainbreaker"
COUNTRY = "canada"
SITE_NAME = "leolist"
SITE = "https://www.leolist.cc/personals/"
LANGUAGE = "english"

BASE_URL = "https://www.leolist.cc/personals/female-escorts/new-brunswick"

global url_base_list
url_base_list = [
    "https://www.leolist.cc/personals/female-escorts",
    "https://www.leolist.cc/personals/female-massage",
    "https://www.leolist.cc/personals/shemale-escorts/", # transsexual escorts
    "https://www.leolist.cc/personals/dom-fetish/",
    "https://www.leolist.cc/personals/gigs-jobs",
    "https://www.leolist.cc/personals/male-escorts/"
]

CATEGORIES = [
    "female-escorts",
    "female-massage",
    "shemale-escorts",
    "dom-fetish",
    "gigs-jobs",
    "male-escorts",
]

global regions

REGIONS = [
  'calgary',
  'edmonton',
  'north-alberta',
  'metro-vancouver',
  'vancouver-island',
  'interior',
  'northern-bc',
  'manitoba',
  'new-brunswick',
  'newfoundland',
  'labrador',
  'nw_territories',
  'nova-scotia',
  'nunavut',
  'central-ontario',
  'greater-toronto',
  'hamilton-niagara',
  'northern-ontario',
  'south-eastern-ontario',
  'south-western-ontario',
  'prince-edward',
  'quebec',
  'regina',
  'saskatoon',
  'yukon',
]
import numpy as np
regions = list(np.random.permutation(REGIONS))

global MAX_PAGES_PER_CATEGORY
MAX_PAGES_PER_CATEGORY = 5 # El máximo es 40.
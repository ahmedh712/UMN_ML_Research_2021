#pip install pandas matplotlib numpy SpaCy geotext geocoder uszipcode geopy
import pandas as pd
import numpy as np
from collections import Counter
from functools import lru_cache
import math


##cleaning
"""punctuation removal"""
import re
import string

def removePunc(s):
    remove = string.punctuation
    rm = string.punctuation.replace(",", "")
    return s.translate(str.maketrans("", "", rm))

"""emoji removal"""
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
def remove_emoji(string):
    return emoji_pattern.sub(r'', string)


"""The spacy function used below uses a deprecated function and the warnings are obnoxious when there's 100,000 of them"""
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


from geotext import GeoText
def geotext_get_city(city_name):
    if city_name == None :
        return None
    cities = GeoText(city_name).cities
    if cities == []:
        return None
    return GeoText(city_name).cities[0]

"""#NER

##SpaCy
"""

import spacy
nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
def extractLocationSpaCy(string):
    #if string[0] == '' or string[1] != None:
    #    return None
    doc = nlp(string)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    return None

"""#Location query

##GeoPy
"""

from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="UGR_API")

@lru_cache(maxsize=32)
def geopy_get_address(location, usOnly = True):
    if location == None or location == "":
        return None
    ret = geolocator.geocode(location, addressdetails=True, timeout=10, language='en')
    if ret == None:
        return None
    elif usOnly:
        try:
            if ret.raw['address']['country'] == 'United States':
                return ret.raw['address']
        except:
            return None
    else:
        return ret.raw['address']
    return None
print(geopy_get_address('moscow', usOnly=False))
"""###state abbreviations func"""

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}
def state_abbrev_to_name(abbrev):
  if abbrev.upper() in states.keys():
    return states[abbrev.upper()]
  else:
    return abbrev


"""##Extract features from location columns

###merge extracted cities into one column
"""

def merge_locations(row):
  if row['geotext_cities'] != None:
    return row['geotext_cities']
  elif row['twitter_loc'] != None:
    return row['twitter_loc']
  elif row['spacy_loc'] != None:
    return row['spacy_loc']
  else:
    return None


def extract_city_state(str):
    # drop trailing space and commas
    while (str[-1] == " " or str[-1] == ','):
        str = str[:-1]
    if str != None and ',' in str:
        spl = str.split(',')
        city = spl[0].split()[-1]

        state = state_abbrev_to_name(spl[1].split()[0])
        if state != None:
            return city + ', ' + state
        else:
            return city


def extract_state_via_comma(str):
    if str == '' or len(str) == 0 or str == '\n':
        return None
    #drop trailing space and commas
    try:
        while(str[-1] == " " or str[-1] == ','):
            str = str[:-1]
        if ',' in str:
            lst = str.split(',')
            lst = lst[1:]
            for item in lst:
              words = item.split()
              if words[0].upper() in states.keys():
                return state_abbrev_to_name(words[0].upper())
    except:
        return None

isNotNull = lambda x: x == None

def merge_city_state(row):
  if row['merged_loc'] != None and row['comma_state'] != None:
    if state_abbrev_to_name(row['merged_loc']) != state_abbrev_to_name(row['comma_state']):
      return state_abbrev_to_name(row['merged_loc']) + ", " + state_abbrev_to_name(row['comma_state'])
    else:
      return state_abbrev_to_name(row['merged_loc'])
  elif row['merged_loc'] == None and row['comma_state'] != None:
    return state_abbrev_to_name(row['comma_state'])
  elif row['merged_loc'] != None and row['comma_state'] == None:
    return state_abbrev_to_name(row['merged_loc'])
  else:
    return None



"""###using GeoPy Location object, extract useful columns"""

def extract_city(gp):
  if gp != None:
    if 'city' in gp.keys():
      return gp['city']
    if 'town' in gp.keys():
      return gp['town']
    if 'hamlet' in gp.keys():
      return gp['hamlet']
    if 'village' in gp.keys():
      return gp['village']
def extract_state(gp):
  if gp != None:
    if 'state' in gp.keys():
      return gp['state']
def extract_county(gp):
  if gp != None:
    if 'county' in gp.keys():
      return gp['county']
def extract_country(gp):
  if gp != None:
    if 'country' in gp.keys():
      return gp['country']

from tqdm import tqdm
tqdm.pandas()

import os
from os.path import exists

import sys
import os
sys.path.append(os.path.abspath("/home/srivasta/hassa601/experiments/twitterNER/TwitterNER/NoisyNLP"))
from run_ner import TwitterNER
from twokenize import tokenizeRawTweetText
ner = TwitterNER()

def extractLocationTwitterNER(string):
    tokens = tokenizeRawTweetText(string)
    for ent in ner.get_entities(tokens):
        if ent[2]== "LOCATION":
            return " ".join(tokens[ent[0]:ent[1]])
    return None

#csize is very important that the highest value possible is used limited by memory, at least 2.5 million rows on a 16GB laptop is possible.
csize = 3000000 #chunksize

"""Load the data json // Must change the directory"""
data_directory = "/home/srivasta/hassa601/experiments/"
file_name = data_directory + "outputEth.csv"
outfile = '/home/srivasta/hassa601/experiments/FinalExtracted.csv'

chunks = pd.read_csv(file_name, dtype=object, chunksize = csize, engine='python')

colnames = ['UID', 'Names', 'Declared_Location','Ethnicity']
saved_colnames = ['UID', 'Names', 'Declared_Location','Ethnicity','Extracted_Location']


if (exists(outfile)):
    os.remove(outfile)

f = open(outfile, 'a')  # Open file as append mode
i = 0
pd.DataFrame(saved_colnames).transpose().to_csv(outfile, mode='a', header=False, index=False)

for df2 in chunks:
    df = df2
    print("chunk " + str(i))
    i += 1
    #remove NaNs and Nones
    df = df.replace(['nan', 'None'], '')
    df = df.fillna("")
    df = df.replace(to_replace=[None], value='')

    df['cleaned_loc'] = df['Declared_Location'].apply(removePunc)
    df['spacy_loc'] = df['cleaned_loc'].apply(extractLocationSpaCy)
    df['twitter_loc'] = df['cleaned_loc'].apply(extractLocationTwitterNER)
    df['geotext_cities'] = df['cleaned_loc'].apply(geotext_get_city)


    df['merged_loc'] = df.apply(merge_locations, axis=1)
    df['comma_state'] = df['cleaned_loc'].apply(extract_state_via_comma)
    df['final_location'] = df.apply(merge_city_state, axis=1)
    df = df.sort_values('final_location')
    df['geopy_merged'] = df['final_location'].apply(geopy_get_address, usOnly=False)

    df = df.drop(labels=['cleaned_loc', 'spacy_loc','twitter_loc','geotext_cities','merged_loc', 'comma_state'], axis=1)
    df.to_csv(outfile, mode='a', header=False, index = False)

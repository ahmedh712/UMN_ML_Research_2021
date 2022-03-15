# pip install pandas  numpy==1.19 nameparser stanza spacy emoji
# pip install ethnicolr
# python -m spacy download en_core_web_sm en_core_web_md en_core_web_lg

import pandas as pd
import ethnicolr as ec
import re
import string
import spacy

nlp_sm = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
nlp_md = spacy.load("en_core_web_md", disable=['transformer', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
nlp_lg = spacy.load("en_core_web_md", disable=['transformer', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
##cleaning
"""punctuation removal"""
removePunc = lambda x: x.translate(str.maketrans('', '', string.punctuation))

"""emoji removal"""
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)


def strip_emoji(text):
    RE_EMOJI = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
    return RE_EMOJI.sub(r'', text)


# def remove_emoji(string):
#     return emoji_pattern.sub(r'', string)
import emoji


def remove_non_letters(text):
    return re.sub(r'[0-9]+', ' ', text.encode("ascii", "ignore").decode())


# Processing
"""The spacy function used below uses a deprecated function and the warnings are obnoxious when there's 100,000 of them"""
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


# nlp = spacy.load("en_core_web_sm", disable=['transformer', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])


def extractPersonSpaCy(string):
    if string == None or string == "":
        return None
    doc = nlp_sm(string)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    doc = nlp_md(string)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    doc = nlp_lg(string)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


from nameparser import HumanName


def nameParserFN(name):
    n = HumanName(name)
    return [n.first, n.last]


def getFirstName(name):
    return None if name == None else nameParserFN(name)[0]


def getLastName(name):
    return None if name == None else nameParserFN(name)[1]


from multiprocessing import Pool, cpu_count
import os
from datetime import datetime

'''for multithreading fun since spacy is slow'''


def process_Pandas_data(func, df, csize, num_processes=None):
    ''' Apply a function separately to each column in a dataframe, in parallel.'''

    # If num_processes is not specified, default to minimum(#columns, #machine-cores)
    if num_processes == None:
        num_processes = min(df.shape[0], cpu_count())

    # 'with' context manager takes care of pool.close() and pool.join() for us
    with Pool(num_processes) as pool:
        # we need a sequence to pass pool.map; this line creates a generator (lazy iterator) of columns
        seq = [i for i in df]

        # pool.map returns results as a list
        results_list = list(pool.imap(func, seq, int(csize / num_processes)))

    # return list of processed columns, concatenated together as a new dataframe
    return results_list


# supresses majority of tensorflow warnings since GPU isn't used
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)

from os.path import exists

from tqdm import tqdm

tqdm.pandas()

if __name__ == '__main__':


    """Load the data json // Must change the directory"""
    data_directory = "/home/srivasta/shared/us_presidential_election_2020/MongoAhmed/"
    file_name = data_directory + "names_and_location.csv"
    outfile = '/home/srivasta/hassa601/experiments/outputEth.csv'
    csize = 100000  # chunksize

    chunks = pd.read_csv(file_name, chunksize=csize, dtype=object, engine='python')
    if exists(outfile):
        os.remove(outfile)

    f = open(outfile, 'a')  # Open file as append mode
    saved_colnames = ['UID', 'Names', 'Declared_Location', 'Ethnicity']
    pd.DataFrame(saved_colnames).transpose().to_csv(outfile, mode='a', header=False, index=False)

    i = 0

    for df in chunks:
        print("chunk " + str(i))
        i += 1
        # remove NaNs and Nones
        df = df.rename(columns={"Names": "name"})
        df = df.replace(['nan', 'None'], '')
        df = df.fillna("")
        df = df.replace(to_replace=[None], value='')
        print("preprocessing complete\n")
        # NER and name Parsing
        start = datetime.now()
        df['name_clean_SpaCy'] = df['name'].apply(remove_non_letters).apply(removePunc)
        df['name_clean_SpaCy'] = process_Pandas_data(extractPersonSpaCy, df['name_clean_SpaCy'], csize)
        print("NER time: " + str(datetime.now() - start))
        start = datetime.now()
        df['firstName'] = df['name_clean_SpaCy'].apply(getFirstName)
        df['lastName'] = df['name_clean_SpaCy'].apply(getLastName)
        # print(" splitting name time: " + str(datetime.now() - start))
        # Ethnicolr
        start = datetime.now()
        df = ec.pred_fl_reg_name(df, fname_col='firstName', lname_col='lastName')
        # print(" ethncolr time: " + str(datetime.now() - start))
        df = df.drop(labels=['lastName', 'firstName', 'asian', 'hispanic', 'nh_black', 'nh_white', 'name_clean_SpaCy'],axis=1)
        start = datetime.now()
        df.to_csv(outfile, mode='a', header=False, index=False)
        print(" tocsv time: " + str(datetime.now() - start))

    f.close()








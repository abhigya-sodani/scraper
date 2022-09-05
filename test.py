import nltk
from numpy import NaN, append
import pandas
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qsl, unquote_plus
from urllib3.connectionpool import log as urllibLogger
from selenium import webdriver
import re
import html2text
import ssl
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from difflib import SequenceMatcher
import pickle
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import spacy
from collections import Counter
 
from math import sqrt, pow, exp
 
def squared_sum(x):
  """ return 3 rounded square rooted value """
 
  return round(sqrt(sum([a*a for a in x])),3)
 
def euclidean_distance(x,y):
  """ return euclidean distance between two lists """
 
  return sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))

def distance_to_similarity(distance):
  return 1/exp(distance)

nlp=spacy.load("en_core_web_md")
def code_of_site(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    
    browser = webdriver.PhantomJS()
    browser.set_page_load_timeout(60)
    try:
        browser.get(url)
    except:
        return ""
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(str(browser.page_source))

def getKeywordsUrl(url):
    try:
        doc=code_of_site(url)
        final=[]
        for i in doc.split():
            if i.isalpha():
                if len(i)>2:
                    final.append(i.lower())
    except:
        return []
    
    return final


tokens=getKeywordsUrl("https://www.veryfi.com/")
tokens1=getKeywordsUrl("https://paygration.com/")
a=nlp(" ".join(tokens)).vector
b=nlp(" ".join(tokens1)).vector
print(distance_to_similarity(euclidean_distance(a,b)))
tagged = nltk.pos_tag(tokens)
important_words=[]
for i in tagged:
    if i[1][0]=='N':
        important_words.append(i[0])

result = [item for items, c in Counter(important_words).most_common()
                                      for item in [items] * c]
result=[*set(result)]
print(result)

tagged1 = nltk.pos_tag(tokens1)
important_words1=[]
for i in tagged1:
    if i[1][0]=='N':
        important_words1.append(i[0])

result1 = [item for items, c in Counter(important_words1).most_common()
                                      for item in [items] * c]
result1=[*set(result1)]
print(result1)

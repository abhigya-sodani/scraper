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
from progress.bar import Bar
from cs50 import SQL
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from difflib import SequenceMatcher
import pickle
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
db = SQL("sqlite:///main.db")
LOGGER.setLevel(logging.ERROR)
urllibLogger.setLevel(logging.ERROR)



class Url(object):
    '''A url object that can be compared with other url orbjects
    without regard to the vagaries of encoding, escaping, and ordering
    of parameters in query strings.'''

    def __init__(self, url):
        parts = urlparse(url)
        _query = frozenset(parse_qsl(parts.query))
        _path = unquote_plus(parts.path)
        parts = parts._replace(query=_query, path=_path)
        self.parts = parts

    def __eq__(self, other):
        return self.parts == other.parts

    def __hash__(self):
        return hash(self.parts)

class Cache:
    def __init__(self):
        self.cache={}

    def getCompaniesInCSV(self):
        comps = pandas.read_csv("companies_sorted.csv")
        return comps.iloc
    def updateCacheSection(self,map,key,value):
        if key in map.keys():
            pass
        else:
            map.update({key:value})

    def createCache(self):
        for i in self.getCompaniesInCSV():
            self.updateCacheSection(self.cache,i["industry"],{})
            self.updateCacheSection(self.cache[i["industry"]],i["country"],{})
            self.updateCacheSection(self.cache[i["industry"]][i["country"]],i["size range"],{})
            self.updateCacheSection(self.cache[i["industry"]][i["country"]][i["size range"]], i["name"],i["domain"])
            print(i["name"])
    
    def getCache(self):
        return self.cache
    
    def loadCache(self):
        f = open ("cache.pkl", "rb")
        self.cache= pickle.load(f)
           
    

def putCompaniesInDB():
     for i in companies.iloc:
        print(i[1])
        i=i.fillna(0)
        db.execute("""INSERT INTO companies(Name,Domain,Year_Founded,Industry,Size,Locality,Country,Linkedin,
        Current_Employees,Total_Employees) VALUES(:name, :domain, :year_founded, :industry, :size, :locality, 
        :country, :linkedin, :current_employees, :total_employees)""", name=i[1], domain=i[2], year_founded=str(int(i[3])), 
        industry=i[4], size=i[5], locality=i[6], country=i[7], linkedin=i[8], current_employees=str(i[9]), total_employees=str(i[10]))

def similarAppend(a, li):
    for i in li:
        if SequenceMatcher(None, a, i).ratio()>=0.85:
            return li
        if Url(a)==Url(i):
            return li
    li.append(a)
    return li

def getCompaniesInDB():
    companies=db.execute("SELECT * FROM companies")
    return companies

def getCompaniesInCSV():
    comps = pandas.read_csv("companies_sorted.csv")
    return comps.iloc

def getKeywordsInDB():
    kw=db.execute("SELECT * FROM keywords")
    return kw
def getLastKeywordEntry():
    kw=getKeywordsInDB()
    last_entry_name=kw[len(kw)-1]
    return last_entry_name["company"]

def putKeywordsInDB():
    comp=getCompaniesInDB()
    for i in comp:
        db.execute("INSERT INTO keywords (company,keywords) VALUES (:name,:keywords)", name=i["Name"], keywords="|".join(getKeywords(i["Name"])))

def appendKeywordsInDB(last):
    comp=getCompaniesInDB()
    last_keyword_seen=False
    for i in comp:
        if not last_keyword_seen:
            if i["Name"]==last:
                last_keyword_seen=True
        else:
            db.execute("INSERT INTO keywords (company,keywords) VALUES (:name,:keywords)", name=i["Name"], keywords="|".join(getKeywords(i["Name"])))

def search(company):
    comp=getCompaniesInDB()
    for i in comp:
        
        if i["Name"].__contains__(company):
            return i
       
def searchCSV(company):
    
     for i in getCompaniesInCSV():
        try:
            if i["name"].__contains__(company):
                print(i)
        except:
            continue
            
def getAllLinks(driver,url):
    links=[]
    for i in driver.find_elements_by_tag_name("a"):
        links.append(i.get_attribute("href"))
    """
    try:
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        your_element = WebDriverWait(driver,60,ignored_exceptions=ignored_exceptions)\
                            .until(expected_conditions.presence_of_element_located((By.TAG_NAME,"a")))
    except:
        return []
   
    while True:
        try:
            for i in driver.find_elements_by_tag_name("a"):
                links.append(i.get_attribute("href"))
            break
        except:
            pirnt
            driver.get(url)
            links=[]
     """
    return links

def filterLinksForPages(links,url):
    pages=[]
    for i in links:
        if i is None:
            continue
        if not i.__contains__(url):
            continue
        elif i.lower().__contains__(".jpg") or  i.lower().__contains__(".png") or  i.lower().__contains__(".svg") or  i.lower().__contains__(".gif"):
            continue
        else:
            pages=similarAppend(i,pages)
   
    return pages[0:10]

def filterLinksByKeywords(links,url,keyword):
    pages=[]
    for i in links:
        if i is None:
            continue
        if not i.__contains__(url):
            continue
        elif i.lower().__contains__(".jpg") or  i.lower().__contains__(".png") or  i.lower().__contains__(".svg") or  i.lower().__contains__(".gif"):
            continue
        else:
            if i.__contains__(keyword.lower()):
                pages=similarAppend(i,pages)
   
    return pages

def code_of_site(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    """
    req = Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    )
    """
    browser = webdriver.PhantomJS()
    browser.set_page_load_timeout(60)
    try:
        browser.get(url)
    except:
        return ""
    #html_page = urlopen(req)
    #soup = BeautifulSoup(html_page, "html.parser")
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

def getKeywords(company):
    try:
        doc=code_of_site("http://www."+search(company)["Domain"])
        final=[]
        for i in doc.split():
            if i.isalpha():
                if len(i)>2:
                    final.append(i.lower())
    except:
        return []
    
    return final

def filterCache(map):
    choices=[]
    for i in map.keys():
        choices.append(i)
    print("Select:")
    for i in range(0,len(choices)):
        print(str(i)+": "+str(choices[i]))
    inp=input()
    selected=choices[int(inp)]
    return map[selected]

c=Cache()
c.loadCache()
cache=c.getCache()
f=cache
while type(list(f.values())[0])==dict:
    f=filterCache(f)


word=input("word to search for?")
comps=[]
for i in f.items():
    if type(i[0])!=str or type(i[1])!=str:
        continue
    browser = webdriver.PhantomJS()
    browser.set_page_load_timeout(60)
    try:
        browser.get("http://www."+"callminer.com")
    except:
        continue
    print(getAllLinks(browser,"callminer.com"))
    ln=filterLinksByKeywords(getAllLinks(browser,"callminer.com"),"callminer.com","integrations")
    print(ln)
    for k in ln:
        if word in getKeywordsUrl(k):
            print("found match "+i[0])
            comps.append(i[0])
        else:
            print("match not found "+i[0])
print(comps)
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

    def loadFromCache(self):
        kw=db.execute("SELECT * FROM keywords")
        for i in kw:
            self.cache.update({i["company"]:i["keywords"].split("|")})
    def inCache(self,company):
        if company in self.cache.keys():
            return True
        return False
    

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
       

def getAllLinks(driver):
    links=[]
    for i in driver.find_elements_by_tag_name("a"):
        links.append(i.get_attribute("href"))
    return links

def filterLinksForPages(links,url):
    pages=[]
    for i in links:
        if not i.__contains__(url):
            continue
        elif i.lower().__contains__(".jpg") or  i.lower().__contains__(".png") or  i.lower().__contains__(".svg") or  i.lower().__contains__(".gif"):
            continue
        else:
            pages=similarAppend(i,pages)
   
    return pages[0:10]

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

def searchForKeyword(word):
    keywords=db.execute("SELECT * FROM keywords")
    comps=[]
    for i in keywords:
        if word.lower() in i["keywords"]:
            comps.append(i["company"])
    
    return comps

def filterByIndustry():
    comps=getCompaniesInDB()
    industries=[]
    for i in comps:
        if i["Industry"] not in industries:
            industries.append(i["Industry"])
    print("Select an industry you would like to select:")
    for i in range(0,len(industries)):
        print(str(i)+": "+industries[i])
    inp=input()
    selected=industries[int(inp)]
    comps_final=[]
    for i in comps:
        if i["Industry"] == selected:
            comps_final.append(i)
    return comps_final

def filterByLocality(comps):
    countries=[]
    for i in comps:
        if(i["Locality"].split(",")[0]=='0'):
            continue
        if i["Locality"].split(",")[2] not in countries:
            countries.append(i["Locality"].split(",")[2])
    print("Select an country you would like to select:")
    for i in range(0,len(countries)):
        print(str(i)+": "+countries[i])
    inp=input()
    selected=countries[int(inp)]
    comps_final=[]
    for i in comps:
        if(i["Locality"].split(",")[0]=='0'):
            continue
        if i["Locality"].split(",")[2].lower() == selected.lower():
            comps_final.append(i)
    return comps_final

def filterByLocality(comps):
    countries=[]
    for i in comps:
        if(i["Locality"].split(",")[0]=='0'):
            continue
        if i["Locality"].split(",")[2] not in countries:
            countries.append(i["Locality"].split(",")[2])
    print("Select an country you would like to select:")
    for i in range(0,len(countries)):
        print(str(i)+": "+countries[i])
    inp=input()
    selected=countries[int(inp)]
    comps_final=[]
    for i in comps:
        if(i["Locality"].split(",")[0]=='0'):
            continue
        if i["Locality"].split(",")[2].lower() == selected.lower():
            comps_final.append(i)
    return comps_final

def filterBySize(comps,lower,upper):
    comps_final=[]
    for i in comps:
        if int(i["Current_Employees"])<int(upper) and int(i["Current_Employees"])>int(lower):
            comps_final.append(i)
    return comps_final
"""
c=Cache()
c.loadFromCache()
while True:
    print("What Industry Do You Want to Search")
    comps=filterByIndustry()
    print("What Country Would You like to Search By")
    comps=filterByLocality(comps)
    print("What size of company do you want (min):")
    low=input()
    print("What size of company do you want (max):")
    hi=input()
    comp=filterBySize(comps,low,hi)
    print(len(comps))
    print("What keyword would you like to find?:")
    kw=input()
    returnList=[]
    for i in comps:
        if c.inCache(i["Name"]):
            if kw in c.cache[i["Name"]]:
                returnList.append(i["Name"])
        else:
            continue
            if kw in getKeywords(i["Name"]):
                returnList.append(i["Name"])
    print(returnList)

"""
#code_of_site("http://www.causal.app")

browser = webdriver.PhantomJS()
browser.set_page_load_timeout(60)

browser.get("http://www.causal.app/")
print(filterLinksForPages(getAllLinks(browser),"causal.app"))




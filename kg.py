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
import tqdm
import logging
import asyncio
from copy import deepcopy
import aiohttp
from selenium.webdriver.remote.remote_connection import LOGGER
from difflib import SequenceMatcher
import pickle
import urllib.parse
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from simplified_scrapy.request import req
from simplified_scrapy import Spider, SimplifiedDoc, SimplifiedMain
import collections
logging.disable(logging.DEBUG)
class WebScraper(object):
    def __init__(self,comps,keyword, tag):
        self.comps = comps
        # Global Place To Store The Data:
        self.matches= []
        self.keyword=keyword
        self.tag=tag
        self.index_dict={}
        self.html_dict={}

    def run_scraper_to_find_matches(self):
        asyncio.run(self.get_matches())
        
    def run_scraper_to_build_index(self):
        asyncio.run(self.create_index())

    def add_comps_to_scrape(self,companies):
        for i in companies:
            self.comps.append(i)

    def filterLinksByKeywords(self,links,keywords):
        pages=[]
        for i in links:
            if i["url"] is None:
                continue
            elif  i["url"].lower().__contains__(".jpg") or   i["url"].lower().__contains__(".png") or   i["url"].lower().__contains__(".svg") or   i["url"].lower().__contains__(".gif"):
                continue
            else:
                for j in keywords:
                    if  i["url"].lower().__contains__(j.lower()):
                        pages=similarAppend( i["url"],pages)
                        continue    
        return pages

    async def fetch_links(self, session, company_name, url):
        try:
            async with session.get("http://www."+url) as response:
                # 1. Extracting the Text:
                
                text = await response.text()
                # 2. Extracting the  Tag:
                links=await self.extract_links(url,text) 
                return company_name, links
        except Exception as e:
            #print(str(e))
            pass
    
    def store_links_index(self):
        with open('links_index.pkl', 'wb') as file:
       
            pickle.dump(self.index_dict, file, protocol=pickle.HIGHEST_PROTOCOL)
    
    def store_html_index(self):
        with open('html_index.pkl', 'wb') as file:
        
            pickle.dump(self.html_dict, file, protocol=pickle.HIGHEST_PROTOCOL)

    async def fetch(self, session, company_name, url):
        try:
            async with session.get(url) as response:
                # 1. Extracting the Text:
                text = await response.text()
                return text, url, company_name
        except Exception as e:
            #print(str(e))
            pass

    async def extract_links(self, base, text):
        doc = SimplifiedDoc(text)
        return doc.listA(url=base)
      
    
    async def extract_title_tag(self, text):
        try:
            soup = BeautifulSoup(text, 'html.parser')
            return soup.title
        except Exception as e:
            print(str(e))

    def load_index(self):
        with open('links_index.pkl', 'rb') as f:
            self.index_dict = pickle.load(f)
        
        with open('html_index.pkl', 'rb') as f:
            self.html_dict = pickle.load(f)        

    async def create_index(self):
        self.store_html_index()
        self.store_links_index()
        self.load_index()
        tasks = []
        tasks1 = []
        timeout_time=int(len(self.comps)*0.11823-6.86678)
        headers = {
            "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        timeout = aiohttp.ClientTimeout(total=None,sock_connect=100,sock_read=100)
        async with aiohttp.ClientSession(headers=headers,timeout=timeout) as session:
            for comp in self.comps:
                
                tasks.append(self.fetch_links(session, comp[0], comp[1]))

            links=[]
            for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
                links.append(await f)

            del tasks[:]
            del tasks
            
            for i in links:
                if i is None:
                    continue
                if i[0] not in self.index_dict.keys():
                    self.index_dict.update({i[0]:{}})
                for j in i[1]:
                    if j is None:
                        continue
                    self.index_dict[i[0]].update({j["url"]:j["title"]})
                    #tasks1.append(self.fetch(session,i[0],j["url"]))
            """
            site_texts=[]
            for f in tqdm.tqdm(asyncio.as_completed(tasks1), total=len(tasks1)):
                site_texts.append(await f)
            #site_texts = await asyncio.gather(*tasks1)
            counter_text=0
            for text in site_texts:
                counter_text+=1
                if text is not None:
                    if text[0] is None:
                        continue
                    self.html_dict.update({text[1]:text[0]})
                    continue
                else:
                    continue
            """
                    
    async def get_matches(self):
        tasks = []
        tasks1 = []
        links=[]
        site_texts=[]
        timeout_time=int(len(self.comps)*0.11823-6.86678)
        headers = {
            "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        timeout = aiohttp.ClientTimeout(total=None,sock_connect=25,sock_read=25)
        async with aiohttp.ClientSession(headers=headers,timeout=timeout) as session:
            for comp in self.comps:
                if comp[0] in self.index_dict.keys():
                    
                    stored_links=[]
                    for i in self.index_dict[comp[0]].keys():
                        stored_links.append({"url":i,"title":self.index_dict[comp[0]][i]})
                    links.append((comp[0],stored_links))
                else:
                    tasks.append(self.fetch_links(session, comp[0], comp[1]))
            
            for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
                
                links.append(await f)
                
              
            del tasks[:]
            del tasks
            #links = await asyncio.gather(*tasks)
            counter=0
            counter_none=0
            counterNew=0
            for i in links:
                counter+=1
                if i==None:
                    counter_none+=1
                    continue
                print(i[0])
                if i[0] not in self.index_dict.keys():
                    self.index_dict.update({i[0]:{}})
                    for j in i[1]:
                        if j is None:
                            continue
                        self.index_dict[i[0]].update({j["url"]:j["title"]})
                filtered_links=self.filterLinksByKeywords(i[1],self.keyword)
                for j in filtered_links:
                    if j not in self.html_dict.keys():
                        tasks1.append(self.fetch(session,i[0],j))
                    else:
                        site_texts.append((self.html_dict[j][1],j,self.html_dict[j][0]))
            print()
            print(counterNew)
            print("percent none: "+str(float(counter_none)/counter))
            for f in tqdm.tqdm(asyncio.as_completed(tasks1), total=len(tasks1)):
                site_texts.append(await f)
           
            counter_text=0
            for text in site_texts:
                counter_text+=1
                if text is not None:
                    h = html2text.HTML2Text()
                    h.ignore_links = True
                    if text[0] is None:
                        continue
                    self.html_dict.update({text[1]:(text[2],text[0])})
                    try:
                        doc=h.handle(str(text[0]))
                    except:
                        continue
                    final=[]
                    for i in doc.split():
                        if i.isalpha():
                            if len(i)>2:
                                final.append(i.lower())
                    for k in self.tag:
                        if k in final:
                            if text[2] not in self.matches:
                                output.write(str(text[2])+"\n")
                                self.matches.append(text[2])
                            continue  
                    continue
                else:
                    continue
            #print("percent of links scraped:"+str(counter_text/float(len(tasks1))))

        
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
           
def similarAppend(a, li):
    for i in li:
        if SequenceMatcher(None, a, i).ratio()>=0.85:
            return li
        if Url(a)==Url(i):
            return li
    li.append(a)
    return li

def merge_dict(d1, d2):
    """
    Modifies d1 in-place to contain values from d2.  If any value
    in d1 is a dictionary (or dict-like), *and* the corresponding
    value in d2 is also a dictionary, then merge them in-place.
    """
    for k,v2 in d2.items():
        v1 = d1.get(k) # returns None if v1 has no value for this key
        if ( isinstance(v1, collections.Mapping) and 
             isinstance(v2, collections.Mapping) ):
            merge_dict(v1, v2)
        else:
            d1[k] = v2

def filterCache(map):
    choices=[]
    for i in map.keys():
        choices.append(i)
    print("Select (seperate with commas no spaces):")
    for i in range(0,len(choices)):
        print(str(i)+": "+str(choices[i]))
    inp=input().split(",")
    selected=choices[int(inp[0])]
    for i in range(0,len(inp)):
        if i==0:
            continue
        merge_dict(map[selected],map[choices[int(inp[i])]])

    return map[selected]

c=Cache()
c.loadCache()
cache=c.getCache()
f=cache
while type(list(f.values())[0])==dict:
    f=filterCache(f)

url_tags=input("Enter filters for urls (seperated by commas with no spaces)").split(",")
words=input("words to search for? (seperated by commas with no spaces)").split(",")
words=[x.lower() for x in words]
comps=[]
index=input("Do you want to create and index(y/n)")
w=WebScraper(deepcopy(comps),url_tags,words)
w.load_index()
print(len(f.items()))
if index=="n":

    for i in f.items():
        if type(i[0])!=str or type(i[1])!=str:
            continue
        comps.append((i[0],i[1]))
        if len(comps)>2000:
            output=open("matches.txt","a")
            w.add_comps_to_scrape(deepcopy(comps))
            w.run_scraper_to_find_matches()
            comps=[]
            w.comps=deepcopy(comps)
            output.close()
        else:
            continue
        
    output=open("matches.txt","a")
    w.add_comps_to_scrape(deepcopy(comps))
    w.run_scraper_to_find_matches()
    output.close()
    w.store_html_index()
    w.store_links_index()
    print("Index Made")

elif index=='y':

    for i in f.items():
        if type(i[0])!=str or type(i[1])!=str:
            continue
        comps.append((i[0],i[1]))
        if len(comps)>2000:
            w.add_comps_to_scrape(deepcopy(comps))
            w.run_scraper_to_build_index()
            comps=[]
            w.comps=deepcopy(comps)
        else:
            continue
        

    w.add_comps_to_scrape(deepcopy(comps))
    w.run_scraper_to_build_index()
    
 
   
    

    
    

    
    
    

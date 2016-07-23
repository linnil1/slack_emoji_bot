#!/usr/bin/python
# -*- coding: utf-8  -*-

import json
import requests
from bs4 import BeautifulSoup

class BaseFunc:
    def crumbGet(self,rep,spec=None):
        soup = BeautifulSoup(rep.text,"lxml")
        if spec:
            soup = soup.find(**spec)
        #print(soup.find("h1").text.strip())
        return soup.find("input", attrs={"name": "crumb"})["value"]

    def sessionStart(self):
        tab = requests.Session()
        if hasattr(self,'cookies'):
            tab.cookies = self.cookies
        rep = tab.get(self.url, allow_redirects=True)
        rep.raise_for_status()
        return tab,rep

    def getalert(self,rep):
        return BeautifulSoup(rep.text,"lxml").find("p","alert").text.strip().split("\n")[0]

class Emoji(BaseFunc):
    def __init__(self,baseurl,cookies):
        self.url  = baseurl + "/customize/emoji"
        self.cookies = cookies

    def upload(self,filepath,filename):
        tab,rep = self.sessionStart()
        data = {
            'add': 1,
            'crumb': self.crumbGet(rep),
            'name': filename,
            'mode': 'data',
        }
        files = {'img': open(filepath+filename, 'rb')}
        rep = tab.post(self.url, data=data, files=files, allow_redirects=True)
        rep.raise_for_status()
        print(filename +">>" + self.getalert(rep))

    def list(self):
        tab,rep = self.sessionStart()
        tdarray = BeautifulSoup(rep.text,"lxml").find_all("tr",attrs={"class":"emoji_row"})
        emojilist= []
        for td in tdarray:
            tds = td.find_all("td")
            name = tds[1].text.strip()[1:-1]
            Type = tds[2].text.strip()
            auth = tds[3].text.strip()
            link = td.find("span")['data-original']
            emojilist.append({
                    "name":name,
                    "link":link,
                    "type":Type,
                    "author":auth })
        return emojilist
    
    def delete(self,name):
        tab,rep = self.sessionStart()
        spec = {"name":"tr","attrs":{"class":"emoji_row"}}
        data = {
            "crumb":self.crumbGet(rep,spec),
            "remove":name
            }
        rep = tab.post(self.url,data=data, allow_redirects=True)
        rep.raise_for_status()
        print(name +">>" + self.getalert(rep))

    def setalias(self,name,newname):
        tab,rep = self.sessionStart()
        data = {
            'add'  : 1,
            'crumb': self.crumbGet(rep),
            'name' : newname,
            'mode' : 'alias',
            'alias': name
        }
        rep = tab.post(self.url, data=data, allow_redirects=True)
        rep.raise_for_status()
        print(name +" -> "+newname+">>"+ self.getalert(rep))

class Customize(BaseFunc):
    def __init__(self,privacy):
        #get data from privacy
        team_name = privacy['team_name']
        email     = privacy['email']   
        password  = privacy['password']

        #prelogin
        self.baseurl = "https://{}.slack.com".format(team_name)
        self.url = self.baseurl+"/customize"
        se,rep = self.sessionStart()
        
        #login
        data = {
            'crumb': self.crumbGet(rep),
            'email': email,
            'password': password,
            'redir': "/customize",
            'remember': "on",
            'signin': 1
        }
        rep = se.post(self.baseurl,data=data, allow_redirects=True)
        rep.raise_for_status()

        #stdout not essentional
        soup = BeautifulSoup(rep.text,"lxml").find_all("h1")
        print("team_name = "+soup[0].text.strip())

        #function
        self.emoji = Emoji(self.baseurl,se.cookies)

#a = Customize(json.loads(open("privacy.json").read()))


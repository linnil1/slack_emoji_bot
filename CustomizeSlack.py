#!/usr/bin/python
# -*- coding: utf-8  -*-

import json
import requests
from bs4 import BeautifulSoup

class BaseFunc:
    def crumbGet(self,rep):
        soup = BeautifulSoup(rep.text,"lxml")
        #print(soup.find("h1").text.strip())
        return soup.find("input", attrs={"name": "crumb"})["value"]

    def sessionStart(self):
        tab = requests.Session()
        if hasattr(self,'cookies'):
            tab.cookies = self.cookies
        rep = tab.get(self.url, allow_redirects=True)
        rep.raise_for_status()
        return tab,rep

class Emoji(BaseFunc):
    def __init__(self,baseurl,cookies):
        self.url  = baseurl + "/customize/emoji"
        self.cookies = cookies

    def imageUpload(self,filepath,filename):
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
        print(filename + BeautifulSoup(rep.text,"lxml").find("p","alert").text.strip())

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
#a.emoji.imageUpload("word_data/","test")


#!/usr/bin/python
# -*- coding: utf-8  -*-

from slackclient import SlackClient
import os
import urllib.request
import urllib.parse
import requests
import json
import os
import os.path
from bs4 import BeautifulSoup

class Emoji:
    def __init__(self):
        #from privacy
        privacy = json.loads(open("privacy.json").read())
        team_name = privacy['team_name']
        email     = privacy['email']
        password  = privacy['password']
        self.webhookurl = privacy['webhook']

        #prelogin
        self.baseurl = "https://{}.slack.com".format(team_name)
        self.url = self.baseurl+"/customize/emoji"
        self.se = requests.Session()
        self.rep = self.se.get(self.url, allow_redirects=True)
        self.rep.raise_for_status()
        
        #login
        soup = BeautifulSoup(self.rep.text,"lxml")
        print(soup.find("h1").text.strip())
        crumb = soup.find("input", attrs={"name": "crumb"})["value"]
        data = {
            'crumb': crumb,
            'email': email,
            'password': password,
            'redir': "/customize/emoji",
            'remember': "on",
            'signin': 1
        }
        self.rep = self.se.post(self.baseurl,data=data, allow_redirects=True)
        self.rep.raise_for_status()

        #stdout not essentional
        soup = BeautifulSoup(self.rep.text,"lxml").find_all("h1")
        print("team_name = "+soup[0].text.strip())
        print(soup[1].text.strip())

    def imageUpload(self,filename):
        soup = BeautifulSoup(self.rep.text,"lxml")
        crumb = soup.find("input", attrs={"name": "crumb"})["value"]

        data = {
            'add': 1,
            'crumb': crumb,
            'name': filename,
            'mode': 'data',
        }
        files = {'img': open("word_data/"+filename, 'rb')}
        self.rep = self.se.post(self.url, data=data, files=files, allow_redirects=True)
        self.rep.raise_for_status()
        print(BeautifulSoup(self.rep.text,"lxml").find("p","alert").text.strip())

    def imageDownload(self,word):
        #download
        webword = urllib.parse.quote(word).lower()
        url = "http://xiaoxue.iis.sinica.edu.tw"
        geturl = url + "/ImageText2/ShowImage.ashx?text="+webword+"&font=%e5%8c%97%e5%b8%ab%e5%a4%a7%e8%aa%aa%e6%96%87%e5%b0%8f%e7%af%86&size=36&style=regular&color=%23000000"
        rep  = urllib.request.urlopen(geturl).read()

        #store
        webword = webword.replace("%","_")
        print(word+" -> "+webword)
        with open("word_data/"+webword,"wb") as f:
            f.write(rep)

    def slackMessage(self,data,channel):
        payload = {
            "channel": channel,
            "username": "小篆transformer",
            "text": data, 
            "icon_emoji": ":_e7_af_86:"}
        se = requests.Session()
        print(se.post(self.webhookurl,json=payload).text)

    def messageWord(self,word):
        webword = urllib.parse.quote(word).lower().replace("%","_")
        wordlen = len(open("word_data/"+webword,"rb").read())
        print("pnglen = "+str(wordlen))
        if wordlen<140:
            print(word+" not found")
            return word
        else:
            return  ":"+webword+":"

    def imageUpDown(self,qstr,channel):
        emoji_str = ""
        for word in qstr:
            file_noexist = not os.path.isfile("word_data/"+urllib.parse.quote(word).lower().replace("%","_"))
            print("file_noexist = ",file_noexist)
            if file_noexist:
                self.imageDownload(word)
            message = self.messageWord(word)
            if file_noexist and message[0]==':' and message[-1]==':':
                self.imageUpload(message[1:-1])
            emoji_str += message

        self.slackMessage(emoji_str,channel)


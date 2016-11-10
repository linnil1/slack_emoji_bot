#!/usr/bin/python
# -*- coding: utf-8  -*-

import json
import requests
from bs4 import BeautifulSoup
from slackclient import SlackClient
from imgurpython import ImgurClient
from multiprocessing import Pool

class Imgur:
    def __init__(self,client_id,client_secret):
        self.client = ImgurClient(client_id, client_secret)

    def imagesUpload(self,urls):
        """
        for url in urls:
            client.upload_from_url(url)
        """
        if not urls:
            return urls

        pool = Pool(len(urls))
        return pool.map(self.imageUpload,urls)

    def imageUpload(self,url):
        try:
            return self.client.upload_from_url(url)['link']
        except:
            return url


class BaseFunc:
    def crumbGet(self,rep,spec=None):
        soup = BeautifulSoup(rep.text,"lxml")
        if spec:
            soup = soup.find(**spec)
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
        return self.getalert(rep)

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
        return self.getalert(rep)

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
        return self.getalert(rep)

class Slackbot:
    def __init__(self,token):
        self.slack = SlackClient(token)
    def list(self):
        return self.slack.api_call("slackbot.responses.list")
    def base_add(self,triggers,responses):
        return self.slack.api_call("slackbot.responses.add",triggers=triggers,responses=responses)
    def base_delete(self,delid):
        return self.slack.api_call("slackbot.responses.delete",response=delid)
    def base_edit(self,editid,triggers,responses):
        return self.slack.api_call("slackbot.responses.edit",response=editid,triggers=triggers,responses=responses)

    #use element as arg
    def find(self,key,keyword='triggers'):
        replist = self.list()['responses']
        for rep in replist:
            if key in rep[keyword]:
                return rep
        return None #not found

    def update(self,element):
        return self.base_edit(element['id'], ",".join(element['triggers' ]),
                                            "\n".join(element['responses']))
    def delete(self,element):
        return self.base_delete(element['id'])
    
# the function is implement beacuse the server doesn't check same trigger word
# this function is for easy use
    def add(self,key,word): 
        element = self.find(key)
        if not element:
            return self.base_add(key,word)
        else:
            element['responses'].append(word)
            return self.upload(element)

class Customize(BaseFunc):
    def require():
        return [ "team_name", "email",
            {"name":"password","secret":True},
            {"name":"token","secret":True},
            {"name":"testtoken","secret":True,"default":""},
            "imgur_id",
            {"name":"imgur_secret","secret":True}]

    def __init__(self,privacy,login=True):
        # imgur
        client_id = privacy['imgur_id' ]
        client_secret = privacy['imgur_secret']
        self.imgur = Imgur(client_id,client_secret)

        # slackbot response
        testtoken = privacy['testtoken']
        self.slackbot = Slackbot(testtoken)

        self.privacy = privacy

        #emoji
        team_name = privacy['team_name']
        self.emoji = object
        if login:
            #prelogin
            password  = privacy['password' ]
            self.baseurl = "https://{}.slack.com".format(team_name)
            self.url = self.baseurl+"/customize"
            se,rep = self.sessionStart()
            
            #login
            data = {
                'crumb': self.crumbGet(rep),
                'email': privacy['email'],
                'password': privacy['password'],
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

    def getPrivacy(self,require):
        privacy = {}
        for req in require:
            if type(req) is str:
                req = {'name':req}
            if req.get("module"):
                if req['name'] == "emoji":
                    privacy["emoji"] = self.emoji
                elif req['name'] == "imgur":
                    privacy["imgur"] = self.imgur
                else:
                    print(req['name'] + " not found ")
            else:
                privacy[req['name']] = self.privacy[req['name']]
        return privacy

#a = Customize(json.loads(open("privacy.json").read()))


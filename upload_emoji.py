#!/usr/bin/python
# -*- coding: utf-8  -*-

# TODO : separate upload emoji and old_func
import os
import urllib.request
import urllib.parse
import requests
import os
import os.path
import string
from bs4 import BeautifulSoup
from multiprocessing import Process,Queue

class Emoji:
    def __init__(self,team_name,email,password):
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
        tab = requests.Session()
        tab.cookies = self.se.cookies
        rep = tab.post(self.url)
        soup = BeautifulSoup(rep.text,"lxml")
        crumb = soup.find("input", attrs={"name": "crumb"})["value"]

        data = {
            'add': 1,
            'crumb': crumb,
            'name': filename,
            'mode': 'data',
        }
        files = {'img': open("word_data/"+filename, 'rb')}
        rep = tab.post(self.url, data=data, files=files, allow_redirects=True)
        rep.raise_for_status()
        print(filename + BeautifulSoup(rep.text,"lxml").find("p","alert").text.strip())

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


    def messageWord(self,word):
        webword = urllib.parse.quote(word).lower().replace("%","_")
        wordlen = len(open("word_data/"+webword,"rb").read())
        print(word + "pnglen = "+str(wordlen))
        if wordlen<140:
            print(word+" not found")
            return word
        else:
            return  ":"+webword+":"

    def imageProcess(self,word,queue):
        if word in string.printable:
            queue.put((word,word))
            return #for secure problem
        webword = urllib.parse.quote(word).lower().replace("%","_")
        file_noexist = not os.path.isfile("word_data/"+webword)
        print(word + "file_noexist = ",file_noexist)
        if file_noexist:
            self.imageDownload(word)
        message = self.messageWord(word)
        if file_noexist and len(message)!=1 :
            self.imageUpload(webword)
        queue.put((word,message))

    def imageUpDown(self,qstr):
        #pre str
        uniquestr = []
        for word in qstr:
            if word not in uniquestr:
                uniquestr.append(word)
        
        #mutiprocess
        queue = Queue()
        process = []
        for word in uniquestr:
            process.append(Process(target=self.imageProcess,args=(word,queue)))
        for i in process:
            i.start()
        for i in process:
            i.join()

        #dictionary map
        worddict= {}
        for i in range(queue.qsize()):
            key,val = queue.get()
            worddict[key] = val
        emoji_str = ""
        for word in qstr:
            emoji_str += worddict[word]
        return emoji_str


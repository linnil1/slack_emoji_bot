#!/usr/bin/python
# -*- coding: utf-8  -*-

from CustomizeSlack import Customize
import urllib.request
import urllib.parse
import os.path
import string
import re
from multiprocessing import Process,Queue

class OLD_command:
    def __init__(self,slack,custom):
        self.dir = "word_data/"
        self.keyword = "old"
        self.slack  = slack
        self.custom = custom

    def filenameTo(self,word):
        return urllib.parse.quote(word).lower().replace("%","_")

    def imageDownload(self,word):
        print("Download "+word)
        webword = urllib.parse.quote(word).lower()
        geturl = "http://xiaoxue.iis.sinica.edu.tw" + "/ImageText2/ShowImage.ashx?text="+webword+"&font=%e5%8c%97%e5%b8%ab%e5%a4%a7%e8%aa%aa%e6%96%87%e5%b0%8f%e7%af%86&size=36&style=regular&color=%23000000"

        urllib.request.urlretrieve(geturl,self.dir+self.filenameTo(word))

    def messageWord(self,word):
        filename= self.filenameTo(word)
        wordlen = len(open(self.dir+filename,"rb").read())
        print(word + "pnglen = "+str(wordlen))
        if wordlen<140:
            print(word+" not found")
            return word
        else:
            return  ":"+filename+":"

    def imageProcess(self,word,queue):
        if word in string.printable:
            queue.put((word,word))
            return #for secure problem
        filename = self.filenameTo(word)
        file_noexist = not os.path.isfile(self.dir+filename)
        print(word + "noexist = ",file_noexist)
        if file_noexist:
            self.imageDownload(word)
        message = self.messageWord(word)
        if file_noexist and len(message)!=1 :
            print(filename +">>"+ self.custom.emoji.upload(self.dir,filename))
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


    def main(self,datadict):
        payload = {
            "channel": datadict['channel_id'],
            "username": "小篆transformer",
            "icon_emoji": ":_e7_af_86:"}
        text = datadict['text']

        if text.startswith("old "):
            if "'" in text: # NTUST feature
                payload["text"] = self.imageUpDown(u"「請勿輸入單引號，判定為攻擊！」")
                self.slack.api_call("chat.postMessage",**payload)
                
            data = re.search(r"(?<=old ).*",text).group().strip()
            payload["text"    ] = self.imageUpDown(data)
            print(payload['text'])
            print(self.slack.api_call("chat.postMessage",**payload))

        elif text.startswith("oldask "):
            data = re.search(r"(?<=oldask ).*",text).group().strip()
            if len(data)==6:
                udata = "%{}%{}%{}".format(data[0:2],data[2:4],data[4:6])
                data = urllib.parse.unquote(udata)
                payload["text"] = self.imageUpDown(data)+" = "+data+" = "+udata
                print(self.slack.api_call("chat.postMessage",**payload))
        
        elif text.startswith("oldreact "):
            data = re.search(r"(?<=oldreact ).*",text).group().strip()
            data = data.replace(":","") #remove unwanted data
            emoji_str = self.imageUpDown(data)
            emoji_str = re.findall(r":(\w+):",emoji_str)
            target = self.slack.api_call("channels.history",channel=payload['channel'],count=2)
            payload['timestamp'] = target['messages'][1]['ts']
            for emojiname in emoji_str:
                payload['name'] = emojiname 
                print(emojiname +">>")
                print(self.slack.api_call("reactions.add",**payload))

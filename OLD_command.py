#!/usr/bin/python
# -*- coding: utf-8  -*-

from CustomizeSlack import Customize
import urllib.request
import urllib.parse
import os.path
import string
import re
import json
from multiprocessing import Process,Queue

class OLD_command:
    def __init__(self,slack,custom):
        self.dir = "word_data/"
        self.keyword = "old"
        self.slack  = slack
        self.custom = custom
        self.oldhelp= json.loads(open("OLDhelp.json").read())

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
            emoji_str = self.imageUpDown(data)
            onlyemoji = re.findall(r":(\w+):",emoji_str)
            target = self.slack.api_call("channels.history",
                    channel=payload['channel'],
                    count=1,
                    latest=float(datadict['timestamp']),
                    inclusive=0)
            payload['timestamp'] = target['messages'][0]['ts']
            for emojiname in onlyemoji:
                payload['name'] = emojiname 
                print(emojiname +">>")
                print(self.slack.api_call("reactions.add",**payload))

            if emoji_str.startswith("old "):#for recursive use
                payload['username'] += "_recursive"
                payload['text'] = re.search(r"(?<=old ).*",emoji_str).group().strip()
                print(self.slack.api_call("chat.postMessage",**payload))

        elif text.startswith("oldset "):
            data = re.search(r"(?<=oldset).*",text).group().strip()
            two  = re.findall(r"\w+",data)
            if len(two) != 2:
                payload['text'] =  "args error"
                print(self.slack.api_call("chat.postMessage",**payload))
                return 
            if len(two[0])!=1 or two[0] in string.printable:
                payload['text'] =  "not 小篆emoji"
                print(self.slack.api_call("chat.postMessage",**payload))
                return 
            transdata = self.imageUpDown(two[0])
            if len(transdata) == 1 :
                payload['text'] =  "cannot transform to 小篆emoji"
                print(self.slack.api_call("chat.postMessage",**payload))
                return 

            transdata = transdata[1:-1]  ## get rid of ::

            payload['text'] = self.custom.emoji.setalias(transdata,two[1])
            print(self.slack.api_call("chat.postMessage",**payload))
        
        elif text.startswith("oldhelp"):
            payload['text'] = self.oldhelp['purpose']
            self.slack.api_call("chat.postMessage",**payload)
            
            payload['text'] = "\n".join( [self.oldhelp[func] for func in self.oldhelp['allfunc']] )
            self.slack.api_call("chat.postMessage",**payload)

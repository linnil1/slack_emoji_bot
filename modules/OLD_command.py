#!/usr/bin/python
# -*- coding: utf-8  -*-

from oldreact_util import oldreact
import oldtime_util 
import urllib.request
import urllib.parse
import os.path
import string
import re
import json
import time
from multiprocessing import Process,Queue

import oldgif_util
import math


class OLD:
    def require():
        return [{"name":"Emoji","module":True}]

    def __init__(self,slack,custom):
        self.dir = "data/word_data/"
        self.keyword = "old"
        self.slack  = slack
        self.emoji = custom['Emoji']
        self.oldreact = oldreact(self,slack)

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
            print(filename +">>"+ self.emoji.upload(self.dir,filename))
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

    def gifTime(self,text): #default 0.5s
        t = re.findall(r"^-t\s+(.*?)\s+",text)
        if len(t)>1:
            raise ValueError("Arguments Error")
        elif len(t) == 0:
            return 0.5
        try:
            giftime = float(t[0])
            assert(giftime>=0)
        except:
            raise ValueError("time number error")
        if giftime >= 10:
            raise ValueError("time number too big")
        return giftime

    def gifMake(self,data):
        text = self.imageUpDown(data)
        giftime = self.gifTime(text)
        onlyemoji = re.findall(r":(.*?):",text)
        if len(onlyemoji) < 2:
            raise ValueError("Need at least two words")
        if len(onlyemoji) > 100:
            raise ValueError("too many words")
        giftime = math.floor(giftime*1000)
        hashname = "oldgif_"+str(giftime)+"_"+str(abs(hash(str(onlyemoji))))

        if not os.path.isfile(self.dir+hashname):
            oldgif_util.gifGet(onlyemoji,giftime,self.dir,hashname)
            self.emoji.upload(self.dir,hashname)

        print("giflen = "+str(len(onlyemoji)))
        return ':'+hashname+':'

    def main(self,datadict):
        if 'future' not in datadict:
            self.oldreact.futurereactCount(datadict)
            if not (datadict['type'] == 'message' and (
            'subtype' not in datadict or datadict['subtype']=="bot_message")):
                return 

        payload = {
            "channel": datadict['channel'],
            "username": "小篆transformer",
            "thread_ts":datadict.get("thread_ts")or'',
            "icon_emoji": ":_e7_af_86:"}
        text = datadict['text']

        if text.startswith("old "):
            if "'" in text: # NTUST feature
                payload["text"] = self.imageUpDown(u"「請勿輸入單引號，判定為攻擊！」")
                self.slack.api_call("chat.postMessage",**payload)
                
            data = re.search(r"(?<=old ).*",text,re.DOTALL).group().strip()
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
            data = re.search(r"(?<=oldreact ).*",text,re.DOTALL).group().strip()
            emoji_str = self.imageUpDown(data)

            payload,futuretext = self.oldreact.main(payload,emoji_str,datadict['ts'])
            if payload == None:
                return
            
            onlyemoji = re.findall(r":(\w+):",futuretext)
            for emojiname in onlyemoji:
                payload['name'] = emojiname 
                print(self.slack.api_call("reactions.add",**payload))

            #for recursive use
            if futuretext.startswith("old "):
                payload['username'] += "_recursive"
                payload['text'] = re.search(r"(?<=old ).*",futuretext,re.DOTALL).group().strip()
                print(self.slack.api_call("chat.postMessage",**payload))


        elif text.startswith("oldset "):
            data = re.search(r"(?<=oldset).*",text,re.DOTALL).group().strip()
            two  = re.findall(r"\w+",data)
            if len(two) != 2:
                payload['text'] =  "args error"
                self.slack.api_call("chat.postMessage",**payload)
                return 
            if len(two[0])!=1 or two[0] in string.printable:
                payload['text'] =  "not 小篆emoji"
                self.slack.api_call("chat.postMessage",**payload)
                return 
            transdata = self.imageUpDown(two[0])
            if len(transdata) == 1 :
                payload['text'] =  "cannot transform to 小篆emoji"
                self.slack.api_call("chat.postMessage",**payload)
                return 

            transdata = transdata[1:-1]  ## get rid of ::

            payload['text'] = self.emoji.setalias(transdata,two[1])
            print(self.slack.api_call("chat.postMessage",**payload))
        
        elif text.startswith("oldhelp"):
            text ="""
`old [text]                ` *transfer text to 小篆emoji.*
`oldask [6characters]      ` *To ask what is the chinese word of the url-encoded string*
`oldreact (floor=-1) [text]` *give reactions of 小篆emoji to specific floor message*
`oldset [aWord] [newName]  ` *set alias for 小篆emoji*
`oldhelp                   ` *get help for the usage of this module*
`oldtime (time)            ` *show date and time by 小篆emoji*
`oldgif (-t second=0.5) [text]` *combine 小篆emojis into gif*
`oldgifreact (floor=-1) [text]` *give reactions of 小篆emoji gif to specific floor message*
""".strip()
            
            self.slack.api_call("chat.postMessage",**payload,text = text,
                    attachments=[{
                        "author_name":"linnil1",
                        "title":"OLD module document",
                        "title_link":"https://github.com/linnil1/slack_emoji_bot/blob/master/OLDhelp.md",
                        "text":"You can see more details in the document\nor see <https://github.com/linnil1/slack_emoji_bot|source>"
                        }])

        elif text.startswith("oldtime"):
            nowtime = ""
            if text == "oldtime":
                nowtime = time.strftime("%Y/%m/%d %H:%M")
            else:
                nowtime = re.search(r"(?<=oldtime ).*",text,re.DOTALL).group().strip()

            try:
                nowstr = oldtime_util.timeTostr(nowtime)
            except ValueError:
                return 
            payload["text"] = self.imageUpDown(nowstr)
            print(payload['text'])
            print(self.slack.api_call("chat.postMessage",**payload))

        elif text.startswith("oldgif "):
            data = re.search(r"(?<=oldgif ).*",text,re.DOTALL).group().strip()

            try:
                payload['text'] = self.gifMake(data)
            except ValueError as er:
                payload['text'] = self.messagePost(er.__str__())

            print(self.slack.api_call("chat.postMessage",**payload))
        
        elif text.startswith("oldgifreact "):
            data = re.search(r"(?<=oldgifreact ).*",text,re.DOTALL).group().strip()
            emoji_str = self.imageUpDown(data)

            payload,futuretext = self.oldreact.main(payload,emoji_str,datadict['ts'],"oldgifreact")
            if payload == None:
                return

            onlyemoji = re.findall(r":(.*?):",self.gifMake(futuretext))

            payload['name'] = onlyemoji[0]
            print(self.slack.api_call("reactions.add",**payload))

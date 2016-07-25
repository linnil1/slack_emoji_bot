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
    def __init__(self,slack,custom,manager):
        self.dir = "word_data/"
        self.keyword = "old"
        self.slack  = slack
        self.custom = custom
        self.oldhelp= json.loads(open("OLDhelp.json").read())
        self.futurereact = manager.dict()
        # {channel:[{count:,arr:[,]},{}]

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

    def getTimestamp(self,payload,count):
        count = -count+1 # because inclusive
        target = self.slack.api_call("channels.history",
                channel=payload['channel'],
                count=count,
                latest=float(payload['timestamp']),
                inclusive=1)
        target = target['messages'][count-1]
        fileid = ""
        if 'file' in target :
            fileid = target['file']['id']         
        return float(target['ts']),fileid

    def reactmain(self,payload,emojiarr,floors=-1):
        payload['timestamp'],payload['file'] =self.getTimestamp(payload,floors)
        for emojiname in emojiarr:
            payload['name'] = emojiname 
            print(self.slack.api_call("reactions.add",**payload))

    def getFloor(self,data):
        """ It should be separated by space and the range is [-F,F] in hex """
        strdig = re.search(r"^-?[0-9a-fA-F]\s",data)
        try:
            dig = int(strdig.group(),16)
        except(AttributeError,TypeError,ValueError): #nonetype or strange dig
            return -1

        return dig

    def futurereactCount(self,datadict):
        print(self.futurereact)
        if datadict['type'] == 'message': 
            if 'subtype' not in datadict or datadict['subtype']=="bot_message":
                ch = datadict['channel']
                if ch not in self.futurereact:
                    return 
                payload = {
                    "channel": ch,
                    "timestamp": datadict['ts']}
                if ch in self.futurereact:
                    mails = self.futurereact[ch]
                    for i in range(len(mails)):
                        mails[i]['count'] -= 1
                        if mails[i]['count'] == 0 :
                            print("future Mail")
                            self.reactmain(payload,mails[i]['arr'],0)
                    mails = [ mail for mail in mails if mail['count'] != 0 ] 
                    self.futurereact[ch] = mails

            elif datadict['subtype']=="message_deleted":
                #if deleted will cause some count error
                #but i don't want to deal it
                return 

    def futurereactAdd(self,payload,emojiarr,floors):
        ch = payload['channel'] 
        if ch not in self.futurereact:
            self.futurereact[ch] = []
        # http://stackoverflow.com/questions/9754034/can-i-create-a-shared-multiarray-or-lists-of-lists-object-in-python-for-multipro
        # I don't know why not use only append
        tmp = self.futurereact[ch]
        tmp.append({"count":floors,"arr":emojiarr})
        self.futurereact[ch] = tmp

        if emojiarr and floors>0:
            payload['name'] = "_e8_a1_8c" # ok in chinese
            print(self.slack.api_call("reactions.add",**payload))
           
    def main(self,datadict):
        self.futurereactCount(datadict)
        if not (datadict['type'] == 'message' and (
        'subtype' not in datadict or datadict['subtype']=="bot_message")):
            return 

        payload = {
            "channel": datadict['channel'],
            "username": "小篆transformer",
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
            onlyemoji = re.findall(r":(\w+):",emoji_str)
            
            floors = self.getFloor(emoji_str)
            payload['timestamp'] = datadict['ts']
            if floors > 0:
                self.futurereactAdd(payload,onlyemoji,floors)
                return 

            self.reactmain(payload,onlyemoji,floors)

            if emoji_str.startswith("old "):#for recursive use
                del payload['timestamp']
                del payload['file']
                payload['username'] += "_recursive"
                payload['text'] = re.search(r"(?<=old ).*",emoji_str,re.DOTALL).group().strip()
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

            payload['text'] = self.custom.emoji.setalias(transdata,two[1])
            print(self.slack.api_call("chat.postMessage",**payload))
        
        elif text.startswith("oldhelp"):
            allfunc =list(self.oldhelp['allfunc'])
            needfunc=[]
            userask = re.findall(r"\w+",text)

            if len(userask)>1 and userask[0] == "oldhelp":
                for user in userask[1:]:
                    if user in allfunc:
                        allfunc.remove(user)
                        needfunc.append(user)
            
            if not needfunc : #empty
                payload['text'] = self.oldhelp['purpose']
                self.slack.api_call("chat.postMessage",**payload)
                payload['text'] = "\n".join( [ self.oldhelp[func]['usage'] for func in allfunc] )
                self.slack.api_call("chat.postMessage",**payload)

            else:
                for func in needfunc:
                    payload['text'] = self.oldhelp[func]['usage']
                    payload['text'] += "\n"+self.oldhelp[func]['help']
                    self.slack.api_call("chat.postMessage",**payload)

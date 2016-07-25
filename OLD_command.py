#!/usr/bin/python
# -*- coding: utf-8  -*-

from CustomizeSlack import Customize
import urllib.request
import urllib.parse
import os.path
import string
import re
import json
import time
from multiprocessing import Process,Queue

class OLD_command:
    def __init__(self,slack,custom):
        self.dir = "word_data/"
        self.keyword = "old"
        self.slack  = slack
        self.custom = custom
        self.oldhelp= json.loads(open("OLDhelp.json").read())
        self.futurereact = {}
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

    def getFileID(self,payload,ts,count): #count <=0
        count = -count+1 # because inclusive
        target = {}
        for i in range(4):
            target =self.slack.api_call("channels.history",
                    channel=payload['channel'],
                    count=count,
                    latest=ts,
                    inclusive=1)
            if float(target['messages'][0]['ts']) >= float(ts):
                break;
            time.sleep(0.25)
        print("history :"+str(ts)+"-"+str(count))

        target = target['messages'][count-1]

        if 'comment' in target :
            payload['file_comment'] = target['comment']['id']         
        elif 'file' in target :
            payload['file'] = target['file']['id']         
        else:
            payload['timestamp'] = target['ts']


    def getFloor(self,data):
        """ It should be separated by space and the range is [-F,F] in hex """
        strdig = re.search(r"^-?[0-9a-fA-F]\s",data)
        try:
            dig = int(strdig.group(),16)
        except(AttributeError,TypeError,ValueError): #nonetype or strange dig
            raise ValueError

        print("Floor = " + str(dig))
        return dig

    def futurereactCount(self,datadict):
        print(self.futurereact)
        if datadict['type'] == 'message' :
            if 'subtype' not in datadict or datadict['subtype'] not in ["me_message","message_changed","message_deleted"]:
                ch = datadict['channel']
                if ch not in self.futurereact:
                    return 
                if ch in self.futurereact:
                    mails = self.futurereact[ch]
                    for i in range(len(mails)):
                        mails[i]['count'] -= 1
                        if mails[i]['count'] == 0 :
                            print("future Mail")
                            futuredict = dict(datadict)
                            futuredict['text'] = mails[i]['text']
                            futuredict['future'] = True
                            self.main(futuredict)
                    self.futurereact[ch] = [ mail for mail in mails if mail['count'] != 0 ] 
            elif datadict['subtype']=="message_deleted":
                #if deleted will cause some count error
                #but i don't want to deal it
                return 

    def futurereactAdd(self,payload,text,floors):
        ch = payload['channel'] 
        if ch not in self.futurereact:
            self.futurereact[ch] = []
        self.futurereact[ch].append({"count":floors,"text":text})
        # http://stackoverflow.com/questions/9754034/can-i-create-a-shared-multiarray-or-lists-of-lists-object-in-python-for-multipro
        # I don't know why not use only append

        payload['name'] = "_e8_a1_8c" # ok in chinese
        print(self.slack.api_call("reactions.add",**payload))
           
    def main(self,datadict):
        if 'future' not in datadict:
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
            
            floors = -1
            futuretext = emoji_str
            try: #if has floor option
                floors = self.getFloor(emoji_str)
                futuretext = re.search(r"( .*)",emoji_str,re.DOTALL).group().strip()
                if floors > 0:
                    self.getFileID(payload,datadict['ts'],0)
                    self.futurereactAdd(payload,"oldreact 0 "+futuretext,floors)
                    return 
            except:
                pass

            self.getFileID(payload,datadict['ts'],floors)
            
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

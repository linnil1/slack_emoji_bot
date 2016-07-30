import shlex
import json
import multiprocessing as MP

import votetime_util
from datetime import datetime as DT
import time

class VOTE:
    def __init__(self,slack,custom):
        """ needed word: 我 好中不 一二三四五六七八九十 票 行 廢"""
        self.slack= slack
        self.custom = custom
        self.threadend = MP.Value('i',False)
        self.thread = None
        self.init()
        self.emojidict = {
                "me" :"_e6_88_91",
                "yes":"_e5_a5_bd",
                "no" :"_e4_b8_8d",
                "ok" :"_e4_b8_ad",
                "AC" :"_e8_a1_8c",
                1:"_e4_b8_80",2:"_e4_ba_8c",3:"_e4_b8_89",
                4:"_e5_9b_9b",5:"_e4_ba_94",6:"_e5_85_ad",
                7:"_e4_b8_83",8:"_e5_85_ab",9:"_e4_b9_9d",
                10:"_e5_8d_81"}
        self.memberdict = {}
        for mem in self.slack.api_call("users.list")['members']:
            self.memberdict[mem['id']] = mem['name']

        self.myid = self.slack.api_call("auth.test")['user_id']

    def init(self):
        self.start   = False
        self.type    = "" # who yesno option 
        self.private = False
        self.members = MP.Manager().dict() #need shared
        self.noadd   = False
        self.onlyone = False
        self.peoplevote = {}
        self.title   = ""
        self.ts      = ""
        self.channel = ""
        self.options = []
        self.timestart = None
        self.timeend   = None
        if self.thread != None:
            self.thread.terminate()
            self.thread.join()
        self.threadend.value = False
        self.thread = None
        self.expectend = None

    def emojiAdd(self,name,**payload):
        if not payload:
            payload = self.payload
        if 'timestamp' not in payload and 'ts' in payload:
            payload['timestamp'] = payload['ts']
        return self.slack.api_call("reactions.add", name = name, **payload)
    def messagePost(self,text,fix=False,**payload):
        if not payload:
            payload = self.payload
        else:
            payload['icon_emoji'] = self.payload['icon_emoji']
            payload['username'] = self.payload['username']

        if fix == 2:
            method = "chat.delete"
            if 'timestamp' not in payload and 'ts' in payload:
                payload['timestamp'] = payload['ts']
        else:
            method = "chat.postMessage" if not fix else "chat.update"
        return self.slack.api_call(method, text = text, **payload)

    def typeSet(self,data):
        if self.type:
            raise ValueError("Type has been set")
        if data not in ['who','yesno','option']:
            raise ValueError("Type error ! It should be one of [who,yesno,option]")
        self.type = data
    
    def subtypeSet(self,data):
        if data == "noadd":
            if self.type != "option":
                raise ValueError("The type is not option")
            self.noadd = True
        
        if self.start:
            raise ValueError("Vote has been started")
        if data == "private":
            if self.private:
                raise ValueError("private has been set")
            self.private = True
        if data == "onlyone":
            if self.type == "who":
                raise ValueError("The type is who, meaningless")
            self.onlyone = True

    def endGo(self):
        while DT.now() <= self.expectend:
            time.sleep(1)
        self.threadend.value = True

    def timeSet(self,cdata,data):
        if self.thread != None:
            raise ValueError("Time has been set")

        if cdata == 'duration':
            self.expectend = votetime_util.getRel(data)
        elif cdata == 'endtime':
            self.expectend = votetime_util.getAbs(data)

        self.thread = MP.Process(target=self.endGo)
        self.thread.start()

    def titleSet(self,data):
        if self.title:
            raise ValueError("Title has been set")
        self.title = data
    
    def optionSet(self,data):
        if not self.type:
            raise ValueError("Type not set")
        elif self.type != "option":
            raise ValueError("Type not 'option'")
        if len(self.options) == 10:
            raise ValueError("Too many options")
        if self.noadd:
            raise ValueError("noadd has set, no option can be added")
        self.optionAdd( len(self.options)+1,data)

    def optionAdd(self,emoji,text):
        emoji = self.emojidict[emoji]
        self.options.append({
                "emoji":emoji,
                "text" :text,
                "users":[]})

        if self.start :
            self.voteShow("*Vote Start!!* (Add option)",emojis=[emoji] ,fix=True,needall=True)


    def optionParse(self,status,renew=False,showcount=False,showpeople=False):
        if renew:
            self.resultGet()
        text = status+"  Title : "+self.title + "\n"
        if self.onlyone:
            text+= "Select *one* option of choices\n"

        t = DT.now() if not self.timeend else self.timeend
        text += "Duration : "+votetime_util.getduration(self.timestart,t)+"\n"
        if showpeople:
            showcount = True
        peoplevote = dict(self.peoplevote)
        for u in self.options:
            for i in u['users']:
                if i in peoplevote:
                    peoplevote[i] += 1
                else:
                    peoplevote[i] = 1
                        
        if showcount:
            text+= str(len(peoplevote))+" people vote\n"
            
        for opt in self.options:
            text+= ":"+opt['emoji']+": "
            users = opt['users']
            if self.onlyone:
                users = [u for u in opt['users'] if peoplevote[u] ==1]
            users = ["@"+self.memberdict[u] for u in users]
            if showcount:
                text+= str(len(users))+" -> "
            if showpeople:
                text+= ",".join(users)+" "
            text+= opt['text']+"\n"

        spoil = []
        if self.onlyone:
            spoil = [ "@"+self.memberdict[u] for u in peoplevote if peoplevote[u]!=1]
        else:
            spoil = [ "@"+self.memberdict[u] for u in peoplevote if peoplevote[u]==0]

        if len(spoil) and showcount:
            text+= ":_e5_bb_a2:"
            text+= str(len(spoil))+" -> "
            if showpeople:
                text+= ",".join(spoil)+" "
            text+= "spoiled\n"
        return text
    
    def resultGetProcess(self,channel,ts,reactdict):
        reactions = self.slack.api_call("reactions.get",channel=channel,timestamp=ts)['message']
        if 'reactions' not in reactions:
            raise ValueError("Something Wrong")
        reactions = reactions['reactions']

        for react in reactions:
            name = react['name']
            if name in [e['emoji'] for e in self.options] and react['count']>1:
                tmparr = reactdict[name] if name in reactdict else []
                tmparr.extend(
                        [u for u in react['users'] if u!=self.myid])
                reactdict[name] = tmparr

    def resultGet(self):
        reactdict = MP.Manager().dict()
        if not self.private:
            self.resultGetProcess(self.channel,self.ts,reactdict)
        else:            
            pool = [ MP.Process(target=self.resultGetProcess,args=(self.members[mem]['channel'],self.members[mem]['ts'],reactdict)) for mem in dict(self.members) ]
            for p in pool : p.start()
            for p in pool : p.join()

            #for mem in self.members:
            #    self.resultGetProcess(self.members[mem]['channel'],self.members[mem]['ts'],reactdict)

        for index,dic in enumerate(self.options):
            name = dic['emoji']
            if name in reactdict:
                self.options[index]['users'] = sorted(reactdict[name])
            else:
                self.options[index]['users'] = []

    def voteShow(self,status="*Now Voting*",emojis=[],needall=False,fix=False,**kwargs):
        if not self.start :
            raise ValueError("Vote has not started yet")
        text = ""
        if fix !=2:#delete method
            text = self.optionParse(status,**kwargs)
            self.messagePost(text,fix,channel=self.channel,ts=self.ts)
        if not self.private:
            for e in emojis:
                self.emojiAdd(e,channel=self.channel,timestamp=self.ts)
        if needall and self.private:
            pool = [ MP.Process(target=self.membersPostProcess,args=(mem,text,emojis,fix))for mem in dict(self.members) ]
            for p in pool : p.start()
            for p in pool : p.join()
            #for mem in self.members:
            #    self.membersPostProcess(mem,text,emojis=emojis,fix=fix)

    def membersPostProcess(self,mem,text="",emojis=[],fix=0,needrecord=False):
        if needrecord and fix:
            raise ValueError("cannot fix and record together")
        if needrecord and not text.strip():
            raise ValueError("cannot record empty text")
        if fix==2 and (text or emojis ):
            raise ValueError("delete method cannot be done")

        if needrecord:
            rep = self.slack.api_call("im.open",user=mem)
            if rep['ok']:
                self.members[mem] = {"channel":rep['channel']['id']}
        message = self.messagePost(text,fix,**self.members[mem])
        if needrecord:
            tmpdict = self.members[mem]
            tmpdict['ts' ] = message['ts']
            self.members[mem] = tmpdict
        for e in emojis:
            self.emojiAdd(e,**self.members[mem])
    
    def messageRecord(self,text="",emojis=[]): # include emoji and needall=True
        if not text.strip():
            raise ValueError("cannot record empty text")

        message      = self.messagePost(text)
        self.ts      = message['ts']
        self.channel = self.payload['channel']
        if not self.private:
            for e in emojis: 
                self.emojiAdd(e,channel=self.channel,ts=self.ts)

        #for private
        if self.private:
            members = self.slack.api_call("channels.info",channel=self.channel)['channel']['members']
            pool = [ MP.Process(target=self.membersPostProcess,args=(mem,text,emojis,False,True))for mem in members ]
            for p in pool : p.start()
            for p in pool : p.join()
            #for mem in self.members:
            #    self.membersPostProcess(mem,text,emojis=emojis,needrecord=True)
    
    def voteStart(self):
        if not self.title:
            raise ValueError("What is the title of Vote")
        if self.start:
            raise ValueError("Vote has been started")
        self.start=True
        if self.type == "":
            raise ValueError("Which type of Vote ? who,yesno,option")
        elif self.type == "who":
            self.optionAdd("me","me")
        elif self.type == "yesno":
            self.optionAdd("yes","yes")
            self.optionAdd("no","no")
            self.optionAdd("ok","ok")

        self.timestart = DT.now()
        text = self.optionParse("*Vote Start!!*")
        self.messageRecord(text,[e['emoji'] for e in self.options])
    
    def voteEnd(self):
        self.timeend = DT.now()
        self.voteShow("*Result*",renew=True,showcount=True,showpeople=not self.private)
        if self.private:
            self.voteShow("*delete*",fix=2,needall=True)

        voteresult = {
                "title":self.title,
                "options":self.options,
                "type":self.type,
                 "private":self.private,
                 "onlyone":self.onlyone,
                 "noadd":self.noadd,
                "ts":self.ts,
                "channel":self.channel,
                "peoplevote":self.peoplevote,
                "timestart":self.timestart,
                "timeend":self.timeend}

        #open("voteLog","w+").write(json.dumps(voteresult))
        print("LOG:  "+str(voteresult))
        self.init()

    def peoplevoteCount(self,name,item,who):
        if not self.start:
            return 
        if who == self.myid:
            return 
        react = {'ts':item['ts'],'channel':item['channel']}
        if name in [o['emoji'] for o in self.options]:
            if self.private:
                if who in self.members and self.members[who] == react:
                    self.peoplevote[who] = 0
            else :
                if self.channel == item['channel'] and self.ts == item['ts']:
                    self.peoplevote[who] = 0

    def main(self,datadict):
        if self.threadend.value:
            voteend = {
                    'type' : "message",
                    'channel' : self.channel,
                    'text' : "vote end",
                    'ts' : self.ts }
            self.threadend.value = False
            self.main(voteEnd)

        if datadict['type'] == "reaction_added" :
            self.peoplevoteCount(datadict['reaction'],datadict['item'],datadict['user'])
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        self.payload = {
            "channel"  : datadict['channel'],
            "timestamp": datadict['ts'],
            "username" : "投票voter",
            "icon_emoji": ":_e7_a5_a8:"}
        text = datadict['text']
        
        if text.startswith("vote "):
            if datadict['channel'].startswith("D"):
                self.messagePost("Error ! Use it at channel")
                return
            try:
                datarr = shlex.split(text)
            except ValueError as er:
                self.messagePost(er.__str__())
                return 
            print(datarr)
            index = 1 
            while True:
                if index == len(datarr):
                    break;
                data = datarr[index]

                try:
                    if data == "start":
                        self.voteStart()
                    elif data == "title":
                        self.titleSet(datarr[index+1])
                        index+=1
                    elif data == "add":
                        self.optionSet(datarr[index+1])
                        index+=1
                    elif data == "type":
                        self.typeSet(datarr[index+1])
                        index+=1
                    elif data == "subtype":
                        self.subtypeSet(datarr[index+1])
                        index+=1
                    elif data == "duration" or data == 'endtime':
                        self.timeSet(data,datarr[index+1])
                        index+=1
                    elif data == "show":
                        if self.private:
                            raise ValueError("vote cannot show during the vote because type = private")
                        self.voteShow(renew=True,showcount=True)
                    elif data == "end":
                        self.voteEnd()
                        break;
                    else:
                        raise ValueError(data+" Arugments error")

                except IndexError as er:
                    self.messagePost("Arguments error")
                    return 
                except ValueError as er:
                    self.messagePost(er.__str__())
                    return 

                index+=1

            #AC react
            if self.private or not self.start:
                self.payload['timestamp'] = datadict['ts']
                self.emojiAdd(self.emojidict['AC'])
        elif text == 'vote':
            text  = "vote command -> just use messages to vote"
            text += """
```
vote start        # start the vote
vote title [title]# decide your title of vote
vote type         # vote type
          who     # Just vote "Who wants"
          yesno   # Vote for yes no or no opinion
          option  # mutiple option to choice you can use add to add
vote subtype      # vote type
          noadd   # for stop add option ( only for type=option)
          private # Private vote, you need to vote by direct message to bot
                  # This should be set before start. When start, my bot will send you message of vote
          onlyone # One people can only vote for one choice
vote duraion [time] # set the duration of vote from now
                  #format  like : 1Y1M1D3h4m5s
     endtime [time] # set the endtime of vote
                  #format  like : 2015/1/2 3:5:6,3/4 4,3/4,4,4:5
vote add [option] # add option ( only for type=option)
vote show         # show how many people each option
vote end          # end the vote

Example:          # the command can be chained
vote type option add Taipei
vote title "Where we want to go?"
vote start
vote add Tainan
```
"""
            self.messagePost(text)

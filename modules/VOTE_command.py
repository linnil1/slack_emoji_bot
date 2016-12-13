from concurrent.futures import ThreadPoolExecutor, wait
import votetime_util
from datetime import datetime as DT
import shlex
from threading import Timer

class VOTEOUTPUT:
    def __init__(self,slack,channel=""):
        self.slack = slack
        self.ts = ""
        self.channel = channel
        self.dm = False
        self.payload = {
            "username" : "投票voter",
            "icon_emoji": ":_e7_a5_a8:"}

    # this two function is for pool Ugly way
    def imopen(self,mem):
        rep = self.slack.api_call("im.open",user=mem)
        if rep['ok']:
            self.channel =  rep['channel']['id']
            self.dm = True
            return True
        else:
            return False 

    def postFirst(self,text):
        rep = self.slack.api_call("chat.postMessage",
            **self.payload,
            text = text,
            channel = self.channel)
        self.ts = rep['ts']

    def post(self,text):
        if not self.ts:
            self.postFirst(text)
            return 
        self.slack.api_call("chat.update",
            text = text,
            **self.payload,
            ts = self.ts, channel = self.channel)
    
    def emojiAdd(self,names):
        for name in names:
            self.slack.api_call("reactions.add",
                name = name,
                timestamp = self.ts, channel = self.channel)

    def update(self,text="",emojis=[]):
        if text:
            self.post(text)
        if emojis:
            self.emojiAdd(emojis)

    def delete(self):
        self.slack.api_call("chat.delete",
            ts = self.ts, channel = self.channel)

class VOTEOUTPUTS:
    UPDATE_All = 3 
    UPDATE_Main = 1 
    UPDATE_Private = 2 

    def __init__(self,slack,channel):
        self.slack  = slack
        self.channel = channel
        self.messages = [VOTEOUTPUT(slack,channel)]

    def setPrivate(self):
        members = self.slack.api_call("channels.info",
                      channel=self.channel)['channel']['members']

        messages = [ VOTEOUTPUT(self.slack) for i in members ]  
        with ThreadPoolExecutor(max_workers=16) as exe:
            pool = [ exe.submit( mes.imopen, members[i] )
                for i,mes in enumerate(messages) ]
            for i,mes in enumerate(messages):
                if pool[i].result():
                    self.messages.append(mes)

    def update(self, text="", emojis=[], method = 3):
        if   method == VOTEOUTPUTS.UPDATE_All:
            messages = self.messages
        elif method == VOTEOUTPUTS.UPDATE_Main:
            messages = [self.messages[0]]
        elif method == VOTEOUTPUTS.UPDATE_Private:
            messages = self.messages[1:]

        with ThreadPoolExecutor(max_workers=16) as exe:
            pool = [ exe.submit(mes.update, text, emojis) for mes in messages ]
            wait(pool)
    
    def delete(self):
        """ This method will not delete main message """
        with ThreadPoolExecutor(max_workers=16) as exe:
            pool = [ exe.submit( mes.delete ) for mes in self.messages[1:] ]
            wait(pool)
        self.messages = self.messages[:1]

    def checkChoice(self,rep):
        for mes in self.messages:
            if rep['channel'] == mes.channel and rep['ts'] == mes.ts:
                return True
        return False

class VOTETIME:
    def __init__(self,ttype="",string=""):
        self.type = ttype
        if ttype == "duration":
            self.time = votetime_util.getRel(string)
        elif ttype == "endtime":
            self.time = votetime_util.getAbs(string)
        else:
            self.time = DT.now()
        self.timeend = None

    def __str__(self):
        if self.type  == 'duration':
            return self.type + " : " + self.time 
        return self.type + " : " +  self.timestr()

    def timestr(self):
        if self.timeend:
            return DT.strftime(self.timeend,"%Y/%m/%d %H:%M:%S")
        else:
            return DT.strftime(self.time   ,"%Y/%m/%d %H:%M:%S")

    def start(self):
        if self.type == "duration":
            self.timeend = DT.now() + self.time
        else:
            self.timeend = self.time
        return (self.timeend - DT.now()).total_seconds()
    
    def go(self):
        return VOTETIME.getduration( self.time, DT.now()    )

    def left(self):
        return VOTETIME.getduration( DT.now() , self.timeend)

    def getduration(t1,t2):
        return votetime_util.getduration(t1,t2)


class VOTECONFIG:
    help = """ ```
vote init         # init the vote , it should be called first
vote start        # start the vote
vote cancel       # cancel the vote
vote title [title]# decide your title of vote
vote type         # vote type
          who     # Just vote "Who wants"
          yesno   # Vote for yes no or no opinion
          option  # mutiple option to choice you can use add to add
vote subtype      # vote type
          private # Private vote, you need to vote by direct message to bot
                  # This should be set before start.
vote duration[time] # set the duration of vote from now
                    #format  like : 1Y1M1D3h4m5s
     endtime [time] # set the endtime of vote
                    #format  like : 2015/1/2 3:5:6,3/4 4,3/4,4,4:5
vote add [option] # add option ( only for type=option)
vote show         # show how many people each option
vote end          # end the vote

Example:          # the command can be chained
vote init type option add Taipei
vote title "Where we want to go?"
vote start
vote add "Tainan"
``` """
    def __init__(self):
        self.start   = False
        self.title   = ""
        self.options = []

        self.type    = "" # who yesno option 
        #subtype
        self.private = False
        #self.onlyone = False
        #onlyone # One people can only choice one option

        #VOTETIME
        self.timestart = None  
        self.timeend   = None  

        #optiondata
        self.namevote = {}
        self.whovote = {}
        self.newemoji = [] # this will be called from outside
        """ needed word: 我 好中不 一二三四五六七八九十 票 行 廢"""
        self.emojidict = {
                "me" :"_e6_88_91",
                "yes":"_e5_a5_bd",
                "no" :"_e4_b8_8d",
                1:"_e4_b8_80",2:"_e4_ba_8c",3:"_e4_b8_89",
                4:"_e5_9b_9b",5:"_e4_ba_94",6:"_e5_85_ad",
                7:"_e4_b8_83",8:"_e5_85_ab",9:"_e4_b9_9d",
                10:"_e5_8d_81"}

    def __str__(self):
        return str({
            'start'    :self.start,
            'title'    :self.title,
            'options'  :self.options,
            'type'     :self.type,
            'private'  :self.private,
            'timestart':self.timestart,
            'timeend'  :self.timeend ,
            'whovote'  :self.whovote,
            'namevote' :self.namevote,
            'newemoji' :self.newemoji})

    def setTitle(self,data):
        if self.title:
            raise ValueError("Title has been set")
        self.title = data

    def setOption(self,data):
        if not self.type:
            raise ValueError("Type not set")
        elif self.type != "option":
            raise ValueError("Type not 'option'")
        if len(self.options) == 10:
            raise ValueError("Too many options")
        self.optionAdd( len(self.options)+1, data)
    
    def optionAdd(self,emoji,text):
        emoji = self.emojidict[emoji]
        self.options.append({
            "emoji":emoji,
            "text" :text })
        if emoji not in self.whovote: # beacuse someone react not option emoji 
            self.whovote[emoji] = []
        self.newemoji.append(emoji)

    def setType(self,data):
        if data not in ['who','yesno','option']:
            raise ValueError("Type error ! It should be one of [who,yesno,option]")
        if self.type and not self.start:
            self.options = []
            self.whovote = {}
            self.newemoji = []
        self.type = data

        if   self.type == "who"  :
            self.optionAdd("me","me")
        elif self.type == "yesno":
            self.optionAdd("yes","yes")
            self.optionAdd("no" ,"no" )
    
    def setSubtype(self,data):
        #if data == "onlyone":
        #    if self.type == "who":
        #        raise ValueError("The type is who, meaningless")
        #    self.onlyone = True

        if self.start:
            raise ValueError("Vote has been started")
        if data == "private":
            self.private = True

    def setTime(self,ttype,data):
        self.timeend = VOTETIME(ttype,data)

    # TODO finish the spoil
    def spoil(self,whos):
        return { 'text':"spoiled",
          'emoji':"_e5_bb_a2"}

    def emojiChoice(self,name,who,isadd=True):
        if isadd:
            if name not in self.whovote:
                self.whovote[name] = []
            self.whovote[name].append(who)
            if who not in self.namevote:
                self.namevote[who] = []
            self.namevote[who].append(name)
        else:
            self.whovote[name].remove(who)
            self.namevote[who].remove(name)

    def parseOption(self,showcount,showpeople):
        textall = ""

        for opt in self.options:
            text  = ":"+opt['emoji']+": "+opt['text']
            users = self.whovote[opt['emoji']]
            if showcount:
                text += " -> "+str(len(users))
            if showcount and showpeople and len(users):
                text += " : " + ", ".join(["<@"+u+">" for u in users])
            textall += text + "\n"

        return textall+"\n"

    def parseData(self,status,showcount=False,showpeople=False):
        # parameter foolproof
        if showpeople:
            showcount = True
        if self.private:
            showpeople = False
        if not self.start:
            showcount = showpeople = False


        # title
        text = status+"  Title : "+self.title + "\n"
        #if self.onlyone:
        #    text+= "Select *one* option of choices\n"

        # time
        if not self.timestart:
            if self.timeend:
                text += str(self.timeend)+"\n"
        else:
            if self.start == "END":
                text += "start: " + self.timestart.timestr() +"\n" 
                text += "end  : " + self.timeend  .timestr() +"\n" 
            elif self.timeend:
                text += "Time Left : "+self.timeend.left()+"\n"
            else: # start
                text += "Time : " + self.timestart.go() +"\n"
                        
        # option
        if showcount:
            text+= str(len(self.namevote))+" people vote\n"
        text += self.parseOption(showcount,showpeople)

        return text

    def voteStart(self):
        if not self.title:
            raise ValueError("What is the title of Vote")
        if self.type == "":
            raise ValueError("Which type of Vote ? who,yesno,option")
        if self.start:
            raise ValueError("Vote has been started")

        self.start = True
        self.timestart = VOTETIME("Start")
        #remember to self.timeend.start()

    def voteEnd(self):
        if not self.start :
            raise ValueError("vote doesn't started yet")
        if len(self.options) == 0:
            raise ValueError("No option set")
        if not self.timeend:
            self.timeend = VOTETIME("END")
        self.start = "END" # hack

class VOTE:
    def require():
        return []
    def __init__(self,slack,custom=None):
        self.slack= slack
        self.payload = {
            "username" : "投票voter",
            "icon_emoji": ":_e7_a5_a8:"}
        self.botid = self.slack.api_call("auth.test")['user_id']
        self.config = None
        self.output = None
        self.channel = ""
        self.timer = None
        self.init()

    def init(self): #remove all
        self.config = VOTECONFIG()
        self.channel = ""
        self.output = None
        if self.timer != None:
            self.timer.cancel()
            self.timer = None

    def begin(self,channel):
        if  self.config.start:
            raise ValueError("Vote has been started")
        self.init()
        self.channel = channel
        self.output = VOTEOUTPUTS(self.slack,channel)

    def post(self,text,channel=''):
        self.slack.api_call("chat.postMessage",
            channel = channel or self.channel,
            text = text,
            **self.payload)

    def update(self,text):
        if not self.channel:
            raise ValueError("not init")
        if self.config.private:
            self.output.update(text, method = VOTEOUTPUTS.UPDATE_Main)
            self.output.update(text, self.config.newemoji,
                                     method = VOTEOUTPUTS.UPDATE_Private)
        else:
            self.output.update(text, self.config.newemoji)
        self.config.newemoji = []

    def start(self):
        self.config.voteStart()
        if self.config.timeend :
            sec = self.config.timeend.start() 
            if sec < 0: 
                raise ValueError("Time is passed! Please reset")

        text = self.config.parseData("*Vote Start*")
        if self.config.private:
            self.output.setPrivate()
        self.update(text)
        
        if self.config.timeend :
            self.timer = Timer(sec,self.virutalEnd) 
            self.timer.start()

    def show(self):
        if not self.channel:
            raise ValueError("not init")
        if self.config.private:
            text = self.config.parseData("")
        else:
            text = self.config.parseData("*Status*",showcount=True)
        self.post(text)

    def end(self):
        self.config.voteEnd()
        if self.config.private:
            self.output.delete()
        text = self.config.parseData("*Result*",showpeople=True)
        self.output.update(text)
        self.init()
    
    def virutalEnd(self):
        voteend = {
            'type' : "message",
            'channel' : self.channel,
            'text' : "vote end"}
        self.main(voteend)

    def setTime(self,ttype,tstr):
        self.config.setTime(ttype,tstr)
        if self.config.start:
            sec = self.config.timeend.start() 
            if sec < 0: 
                raise ValueError("Time is passed! Please reset")
            if self.timer != None:
                self.timer.cancel()
            self.timer = Timer(sec,self.virutalEnd) 
            self.timer.start()


    def main(self,datadict):
        if datadict['type'] in ["reaction_added","reaction_removed"] and (
           self.config.start ):
            if self.output.checkChoice(datadict['item']) and (
                    datadict['user'] != self.botid ) :
                self.config.emojiChoice( 
                    datadict['reaction'] , datadict['user'] , 
                    isadd = datadict['type'] == "reaction_added")
        
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 
        text = datadict['text']

        if text == "votehelp":
            self.post(VOTECONFIG.help,datadict['channel'])
            return 

        if not text.startswith("vote "):
            return 
        if not datadict['channel'].startswith("C"):
            self.post("Error ! Use it at channel",datadict['channel'])
            return
        if self.channel and datadict['channel'] != self.channel:
            self.post("Error ! Use it at same channel",datadict['channel'])
            return

        try:
            datarr = shlex.split(text)
            print(datarr)
        except ValueError as er:
            self.post(er.__str__(),datadict['channel'])
            return 

        index = 1 
        while index < len(datarr):
            data = datarr[index]
            try:
                if   data == "init":
                     self.begin(datadict['channel'])
                elif data == "cancel":
                     self.init()
                elif data == "start":
                     self.start()
                elif data == "show": 
                     self.show()
                elif data == "end":
                     self.end()
                
                elif data == "title":
                     self.config.setTitle  (datarr[index+1])
                     index+=1
                elif data == "type":
                     self.config.setType   (datarr[index+1])
                     index+=1
                elif data == "subtype":
                     self.config.setSubtype(datarr[index+1])
                     index+=1
                elif data == "duration" or data == 'endtime':
                     self.setTime(data,datarr[index+1])
                     index+=1 

                elif data == "add":
                     self.config.setOption (datarr[index+1])
                     index+=1
                     if self.config.start:
                         text = self.config.parseData("*Vote start*(Option add)")
                         self.update(text)
                else:
                    raise ValueError(data+" not found")

            except IndexError as er:
                self.post("Arguments error",datadict['channel'])
                return 
            except ValueError as er:
                self.post(er.__str__(),datadict['channel'])
                return 

            index+=1
        print(self.config)

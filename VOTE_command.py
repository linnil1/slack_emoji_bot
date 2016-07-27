from slackclient import SlackClient
import shlex

class VOTE:
    def __init__(self,slack,custom):
        """ needed word: 我 好中不 一二三四五六七八九十 投 行"""
        self.slack= slack
        self.custom = custom
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
        self.start= False
        self.type = "" # who yesno option 
        self.title= ""
        self.ts= ""
        self.channel= ""
        self.options = []

    def emojiAdd(self,name,fix=False):
        if  fix:
            self.payload['timestamp'] = self.ts
        return self.slack.api_call("reactions.add",
                name = name, **self.payload)
    def messagePost(self,text,fix=False):
        if fix and not self.start:
            raise ValueError("How can you get this error")

        if not fix:
            return self.slack.api_call("chat.postMessage",
                    text = text,
                    **self.payload)
        else:
            return self.slack.api_call("chat.update",
                    ts = self.ts,
                    text = text,
                    **self.payload)

    def typeSet(self,data):
        if self.type:
            raise ValueError("Type has been set")
        if data not in ['who','yesno','option']:
            raise ValueError("Type error ! It should be one of [who,yesno,option]")
        self.type = data

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
        self.optionAdd( len(self.options)+1,data)
        if self.start :
            self.optionShow("*Vote Start!!* (Add option)",fix=True)
            self.emojiAdd(self.options[-1]['emoji'],fix=True)


    def optionAdd(self,emoji,text):
        self.options.append({
                "emoji":self.emojidict[emoji],
                "text" :text,
                "len"  :0,
                "users":[]})

    def optionShow(self,status,showcount=False,showpeople=False,needat=False,fix=False):
        text = status+"  Title : "+self.title + "\n"
        for opt in self.options:
            text+= ":"+opt['emoji']+": "
            if showcount:
                text+= str(opt['len'])+" -> "
            if showpeople:
                text+= ",".join([("@" if needat else "")+u for u in opt['users']])+" "
            text+= opt['text']+"\n"
            
        return self.messagePost(text,fix)

            

    def voteShow(self,status="*Now Voting*",showcount=True,**kwargs):
        if not self.start :
            raise ValueError("Vote has not started yet")
        reactions = self.slack.api_call("reactions.get",
                channel=self.channel,timestamp=self.ts)['message']
        if 'reactions' not in reactions:
            raise ValueError("No options react")
        reactions = reactions['reactions']

        for react in reactions:
            for index,dic in enumerate(self.options):
                if dic['emoji'] == react['name']:
                    self.options[index]['len'] = react['count']-1
                    self.options[index]['users'] = [self.memberdict[u] for u in react['users'] if u!=self.myid]
                    break;

        self.optionShow(status,showcount=showcount,**kwargs)
    
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

        message = self.optionShow("*Vote Start!!*")
        print(message)
        self.ts      = self.payload['timestamp'] =  message['ts']
        self.channel = self.payload['channel'  ]

        for emoji in self.options:
            self.emojiAdd(emoji['emoji'])
    
    def voteEnd(self):
        self.voteShow("*Result*",showcount=True,showpeople=True)
        voteresult = {
                "title":self.title,
                "options":self.options,
                "type":self.type,
                "ts":self.ts,
                "channel":self.channel}
        print(str(voteresult))


        text = ""
        if self.type == "who":
            text += ",".join(self.options['users']) + "want"
        elif self.type == "yesno":
            sortarr = sorted([opt for opt in self.options if opt['text']!="ok"],key=lambda opt:opt['len'],reverse=1)
            if sortarr[0]['len'] == sortarr[1]['len']:
                text = "Tie : "+str(sortarr[0]['len'])+" vs "+str(sortarr[1]['len'])
            else:
                text = "Win : "+sortarr[0]['text']+" "+str(sortarr[0]['len'])+" people"

        elif self.type == "option":
            sortarr = sorted([opt for opt in self.options if opt['text']!="ok"],key=lambda opt:opt['len'],reverse=1)
            if len(sortarr)==0:
                text = "No options"
            elif len(sortarr)<=1 or sortarr[0]['len'] > sortarr[1]['len']:
                text += "Most : :"+sortarr[0]['emoji']+":"+sortarr[0]['text']+'\n'
                text += str(sortarr[0]['len'])+" people -> "+",".join(sortarr[0]['users']) 
            else :
                text = "Tie : more than two are "+str(sortarr[0]['len'])+" people\n"

        self.messagePost(text)

        print(str(voteresult))
        self.init()

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 
        self.payload = {
            "channel"  : datadict['channel'],
            "timestamp": datadict['ts'],
            "username" : "投票voter",
            "icon_emoji": ":_e6_8a_95:"}
        text = datadict['text']
        
        if text.startswith("vote "):
            try:
                datarr = shlex.split(text)
            except ValueError as er:
                self.messagePost(er.__str__())
                return 
            print(datarr)
            index = 0 
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
                    elif data == "show":
                        self.voteShow()
                    elif data == "end":
                        self.voteEnd()

                except IndexError as er:
                    self.messagePost("Arguments error")
                    return 
                except ValueError as er:
                    self.messagePost(er.__str__())
                    return 

                index+=1

            #AC react
            if not self.start:
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
vote add [option] # add option ( only for type=option)
vote show         # show how many people each option
vote end          # end the vote
```
"""
            self.messagePost(text)

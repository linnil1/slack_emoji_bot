from concurrent.futures import ThreadPoolExecutor, wait, _base
from threading import Timer
import re
import random
from pprint import pprint
from functools import partial

class REGEXBOT:
    def require():
        return [{'name':"CustomResponse",'module':"True"},
                {'name':"interval",'default':'60'}]
    def __init__(self,slack,custom):
        self.slack = slack
        self.interval = int( custom['interval'] )
        self.customResponse = custom['CustomResponse']
        self.ori_response = []
        self.response = []
        self.messageCheck() # this also call timeSet
        self.member = {}
        for mem in self.slack.api_call("users.list")['members']:
            self.member[ mem['id'] ] = mem['name']

    def messageCheck(self):
        data = self.customResponse.list()['responses']
        if data != self.ori_response:
            self.ori_response = data
            self.response = []
            # find regex in trigger
            for rep in data:
                newdata = { 'responses' : rep['responses'] , 'triggers': [] }
                for tri in rep['triggers']:
                    if len(tri) and tri[0] == tri[-1] == '"': # no conside , in middle
                        try:
                            newdata['triggers'].append( re.compile(tri[1:-1]) )
                        except:
                            pass
                if newdata['triggers']:
                    self.response.append( newdata )
            pprint(self.response)

        self.timeSet()

    def timeSet(self):
        timer = Timer(self.interval,self.messageCheck)
        timer.start()

    def responseReplace(self,match,result,datadict={}):
        print(match.group(1))
        try:
            if match.group(1).strip() == "who": # it can't use parse = full
                return '<@'+datadict['user']+'|'+self.member[datadict['user']]+'>'
            if match.group(1).strip() == "all":
                return datadict['text']
            num = int( match.group(1) ) # number
            return result.group(num)
        except:
            return match.group()
    
    def triggerMatch(self,tri,rep,text):
        result = tri.search( text )
        if result:
            response = random.choice( rep['responses'])
            return result,response
        return None,""

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        # find valid string
        result,response = None,""
        #use async because some bad regex can destroy this module
        with ThreadPoolExecutor(max_workers=16) as exe: 
            pool = []
            for rep in self.response:
                for tri in rep['triggers']:
                    pool.append(exe.submit(self.triggerMatch,tri,rep,datadict['text']))
            for i in pool:
                try:
                    result,response = i.result(timeout=1)
                    if result:
                        break
                except: #timeout
                    pass

        # do with response string
        if result:
            replace = partial( self.responseReplace, 
                    result = result, datadict=datadict )
            responseok = re.sub(r"{{\s*(.*?)\s*}}",replace,response)
            self.slack.api_call("chat.postMessage",**{
                "username": "slackbot RE",
                "icon_url": "https://a.slack-edge.com/ae7f/plugins/slackbot/assets/service_512.png",
                "channel": datadict['channel'],
                "text":responseok
            } )

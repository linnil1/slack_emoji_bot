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
        self.timeSet()

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

    def responseReplace(self,match,response): # {{1}} only number
        try:
            num = int( match.group(1) )
            return response.group(num)
        except:
            return match.group()

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        # find valid string
        result = None
        response = ""
        for rep in self.response:
            if result:
                break
            for tri in rep['triggers']:
                result = tri.search( datadict['text'] )
                response = random.choice( rep['responses'])
                break

        # do with data string
        response_words = []
        if response:
            replace = partial( self.responseReplace, response = result)
            responseok = re.sub(r"{{\s*(\d+)\s*}}",replace,response)
            self.slack.api_call("chat.postMessage",**{
                "username": "slackbot RE",
                "icon_url": "https://a.slack-edge.com/ae7f/plugins/slackbot/assets/service_512.png",
                "channel": datadict['channel'],
                "text":responseok
            } )

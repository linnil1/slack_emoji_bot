import InitModule
from slackclient import SlackClient
import copy

import sys
import time


import os
import sys
import re
import importlib
sys.path.insert(0, './modules/')
sys.path.insert(0, './common/')
import password_crypt 
import copy

wantname = ["VOTE"]

class Slack_RTM:
    def __init__(self):
        imports = InitModule.moduleGet()
        privacy = password_crypt.logIn(InitModule.requireGet(imports))

        im = []
        for i in imports:
            if( i['name'] in ["",*wantname] ):
                im.append(i)
        imports = im

        self.modules = InitModule.initGet(privacy,imports)
        self.slack = SlackClient(privacy['_TOKEN']) #dirty methods

    def startRTM(self):
        if self.slack.rtm_connect():
            print("Start")
            while True:
                data = self.slack.rtm_read()
                if data and data[0]['type'] not in ['user_typing','reconnect_url','pref_change','presence_change','emoji_changed']:
                    print(data)
                self.commandSelect(data[0] if data else {"type":None})
                if not data:
                    time.sleep(1)
        else:
            print("Connect Error! Please Reconnect")

    def start(self):
        self.startRTM();

    def commandSelect(self,data):
        for mod in self.modules:
            mod.main(copy.deepcopy(data))


slack_rtm=  Slack_RTM()
slack_rtm.start()

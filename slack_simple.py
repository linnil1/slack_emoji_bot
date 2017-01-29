import InitModule
import ColorPrint
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

#wantname = ["REGEXBOT","CustomResponse"]
wantname = ["OLD","Emoji"]
#wantname=["LATEX","Imgur"]

class Slack_RTM:
    def __init__(self):
        self.colorPrint = ColorPrint.setPrint("Root")
        imports = InitModule.moduleGet()
        privacy = password_crypt.logIn(InitModule.requireGet(imports))

        imports = [ i for i in imports if i['name'] in ["",*wantname] ]

        self.modules = InitModule.initGet(privacy,imports)
        self.slack = SlackClient(privacy['_TOKEN']) #dirty methods
        self.ignoretype = ['user_typing','reconnect_url','pref_change','presence_change','emoji_changed','desktop_notification']

    def startRTM(self):
        if self.slack.rtm_connect():
            self.colorPrint("Start")
            while True:
                data = self.slack.rtm_read()
                if data and data[0]['type'] not in self.ignoretype:
                    self.colorPrint("GET",data)

                if not data:
                    time.sleep(1)
                else:
                    self.commandSelect(data[0])
        else:
            self.colorPrint("Connect Error!","Please Reconnect",color="ERR")

    def start(self):
        self.startRTM();

    def commandSelect(self,data):
        for mod in self.modules:
            mod.main(copy.deepcopy(data))

slack_rtm=  Slack_RTM()
slack_rtm.start()

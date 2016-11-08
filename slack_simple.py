wantmodule = "FBTOSLACK"
from slackclient import SlackClient
from CustomizeSlack import Customize

import sys
import os
import re
import importlib
import json
sys.path.insert(0, './modules/')

import time

class ntuosc:
    def __init__(self):
        #from privacy
        privacy = json.loads(open("../private.json").read())
        self.custom= Customize(privacy)
        self.slack = SlackClient(privacy['token'])
        self.modules = []

        modules = [ c for c in os.listdir("modules") if c.endswith("_command.py")]
        for command in modules:
            com = importlib.import_module(command[:-3])
            c = re.findall(r"(\w+)_command\.py",command)[0]
            if c == wantmodule:
                self.modules.append( getattr(com,c)(self.slack,self.custom) )

    def startRTM(self):
        if self.slack.rtm_connect():
            print("Start")
            while True:
                data = self.slack.rtm_read()
                if data and data[0]['type'] not in ['user_typing','reconnect_url','pref_change','presence_change','emoji_changed']:
                    print(data)
                self.commandSelect(data[0] if data else {"type":None})
                time.sleep(1)
        else:
            print("Connect Error! Please Reconnect")

    def start(self):
        self.startRTM();

    def commandSelect(self,data):
        for mod in self.modules:
            mod.main(data)


ntu =  ntuosc()
ntu.start()
